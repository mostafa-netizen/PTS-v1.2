"""
Upload API endpoints for PDF file uploads.
"""

import os
import uuid
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from services.storage_service import StorageService
from services.job_queue import get_job_queue
from services.processing_service import ProcessingService
import config

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

# Initialize services
storage_service = StorageService()
job_queue = get_job_queue()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload PDF file and start processing.
    
    Returns:
        JSON response with job_id and status
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(config.ALLOWED_EXTENSIONS)}'
            }), 400
        
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
        
        # Save uploaded file
        pdf_path = storage_service.save_upload(job_id, file)
        
        logger.info(f"File uploaded: {file.filename} (Job ID: {job_id})")
        
        # Check if we should use background processing or immediate processing
        use_background = hasattr(job_queue, 'queue')  # Redis queue available
        
        if use_background:
            # Initialize job in queue
            job_queue.update_job_status(
                job_id,
                'queued',
                filename=file.filename,
                progress=0,
                total_pages=0,
                current_page=0,
                file_size=file_size
            )
            
            # Enqueue processing job
            job_queue.enqueue_job(job_id, pdf_path)
            
            return jsonify({
                'job_id': job_id,
                'message': 'File uploaded successfully',
                'status': 'queued',
                'filename': file.filename
            }), 202
        else:
            # Process immediately (development mode)
            logger.info(f"Processing immediately (no Redis queue): {job_id}")
            
            processing_service = ProcessingService(storage_service=storage_service)
            
            def progress_callback(progress, message):
                job_queue.update_job_status(
                    job_id,
                    'processing',
                    progress=progress,
                    message=message
                )
            
            # Initialize job status
            job_queue.update_job_status(
                job_id,
                'processing',
                filename=file.filename,
                progress=0,
                file_size=file_size
            )
            
            # Process PDF
            result = processing_service.process_pdf(
                pdf_path=pdf_path,
                job_id=job_id,
                gpu=config.USE_GPU,
                progress_callback=progress_callback
            )
            
            if result['success']:
                # Save results
                job_queue.save_job_results(job_id, result['pages'])
                
                # Update final status
                job_queue.update_job_status(
                    job_id,
                    'completed',
                    progress=100,
                    message='Processing complete',
                    total_pages=result['total_pages'],
                    total_tendons=result['total_tendons'],
                    excel_path=result.get('excel_path')
                )
                
                return jsonify({
                    'job_id': job_id,
                    'message': 'Processing complete',
                    'status': 'completed',
                    'filename': file.filename,
                    'total_pages': result['total_pages'],
                    'total_tendons': result['total_tendons']
                }), 200
            else:
                job_queue.update_job_status(
                    job_id,
                    'failed',
                    error=result.get('error', 'Unknown error')
                )
                
                return jsonify({
                    'job_id': job_id,
                    'status': 'failed',
                    'error': result.get('error', 'Processing failed')
                }), 500
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

