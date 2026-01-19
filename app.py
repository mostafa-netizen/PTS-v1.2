import os
import uuid
import threading
import logging
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import new services
from services.processing_service import ProcessingService
from services.storage_service import StorageService
from services.job_queue import InMemoryJobQueue
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = config.UPLOAD_FOLDER
OUTPUT_FOLDER = config.OUTPUT_FOLDER
ALLOWED_EXTENSIONS = config.ALLOWED_EXTENSIONS

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize services
storage_service = StorageService()
processing_service = ProcessingService(storage_service=storage_service)
job_queue = InMemoryJobQueue()  # In-memory queue for the existing interface

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_pdf(job_id, filepath):
    """Background task to process PDF using new ProcessingService"""
    try:
        def progress_callback(progress, message):
            """Update job progress"""
            job_queue.update_job_status(
                job_id,
                'processing',
                progress=progress,
                message=message
            )

        logger.info(f"Starting background processing for job {job_id}")

        # Update status to processing
        job_queue.update_job_status(
            job_id,
            'processing',
            progress=0,
            message='Starting processing...'
        )

        # Process the PDF using the new service
        result = processing_service.process_pdf(
            pdf_path=filepath,
            job_id=job_id,
            gpu=config.USE_GPU,
            progress_callback=progress_callback
        )

        if result['success']:
            # Save results to job queue
            job_queue.save_job_results(job_id, result['pages'])

            # Update final status
            job_queue.update_job_status(
                job_id,
                'completed',
                progress=100,
                message='Processing complete',
                total_pages=result['total_pages'],
                total_tendons=result['total_tendons'],
                excel_path=result.get('excel_path'),
                excel_available=True
            )

            logger.info(f"Job {job_id} completed successfully: {result['total_tendons']} tendons detected")
        else:
            # Processing failed
            job_queue.update_job_status(
                job_id,
                'failed',
                error=result.get('error', 'Unknown error')
            )

            logger.error(f"Job {job_id} failed: {result.get('error')}")

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)

        # Update status to failed
        job_queue.update_job_status(
            job_id,
            'failed',
            error=str(e)
        )

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload PDF file and start processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > config.MAX_FILE_SIZE:
            return jsonify({
                'error': f'File too large. Maximum size: {config.MAX_FILE_SIZE / (1024*1024):.0f}MB'
            }), 400

        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Save uploaded file using storage service
        pdf_path = storage_service.save_upload(job_id, file)

        logger.info(f"File uploaded: {file.filename} (Job ID: {job_id})")

        # Initialize job status in queue
        job_queue.update_job_status(
            job_id,
            'queued',
            filename=file.filename,
            progress=0,
            total_pages=0,
            current_page=0,
            file_size=file_size
        )

        # Start background processing
        thread = threading.Thread(target=process_pdf, args=(job_id, pdf_path))
        thread.daemon = True
        thread.start()

        return jsonify({
            'job_id': job_id,
            'message': 'File uploaded successfully, processing started',
            'filename': file.filename
        }), 202

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status for a job"""
    try:
        job_data = job_queue.get_job_status(job_id)

        if not job_data:
            return jsonify({'error': 'Job not found'}), 404

        response = {
            'job_id': job_id,
            'status': job_data.get('status', 'unknown'),
            'progress': int(job_data.get('progress', 0)),
            'message': job_data.get('message', ''),
            'filename': job_data.get('filename', ''),
        }

        # Add additional fields based on status
        if job_data.get('status') == 'processing':
            response.update({
                'total_pages': int(job_data.get('total_pages', 0)),
                'current_page': int(job_data.get('current_page', 0))
            })

        elif job_data.get('status') == 'completed':
            response.update({
                'total_pages': int(job_data.get('total_pages', 0)),
                'total_tendons': int(job_data.get('total_tendons', 0)),
                'excel_available': bool(job_data.get('excel_available', False))
            })

        elif job_data.get('status') == 'failed':
            response['error'] = job_data.get('error', 'Unknown error')

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get results for a completed job"""
    try:
        job_data = job_queue.get_job_status(job_id)

        if not job_data:
            return jsonify({'error': 'Job not found'}), 404

        if job_data.get('status') != 'completed':
            return jsonify({
                'error': 'Job not completed',
                'status': job_data.get('status'),
                'message': 'Results are only available for completed jobs'
            }), 400

        # Get results from queue
        results = job_queue.get_job_results(job_id)

        response = {
            'job_id': job_id,
            'status': 'completed',
            'total_pages': int(job_data.get('total_pages', 0)),
            'total_tendons': int(job_data.get('total_tendons', 0)),
            'excel_available': bool(job_data.get('excel_available', False)),
            'excel_file': f"/api/export/{job_id}/excel" if job_data.get('excel_available') else None,
            'results': results
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error getting results: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<job_id>/<filename>', methods=['GET'])
def download_file(job_id, filename):
    """Download a specific result file"""
    try:
        # Construct file path
        filepath = os.path.join(OUTPUT_FOLDER, job_id, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404

        # Send file
        return send_file(
            filepath,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<job_id>/excel', methods=['GET'])
def download_excel(job_id):
    """Download Excel file with measurements"""
    try:
        job_data = job_queue.get_job_status(job_id)

        if not job_data:
            return jsonify({'error': 'Job not found'}), 404

        if job_data.get('status') != 'completed':
            return jsonify({'error': 'Job not completed'}), 400

        # Get Excel file path
        excel_path = job_data.get('excel_path')

        if not excel_path or not os.path.exists(excel_path):
            return jsonify({'error': 'Excel file not found'}), 404

        # Send file
        return send_file(
            excel_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'tendon_measurements_{job_id}.xlsx'
        )

    except Exception as e:
        logger.error(f"Error downloading Excel: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'gpu_enabled': config.USE_GPU
    }), 200

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Starting Structural Drawing Analysis Platform")
    logger.info("=" * 60)
    logger.info(f"Server: http://0.0.0.0:5001")
    logger.info(f"GPU Enabled: {config.USE_GPU}")
    logger.info("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5001)

