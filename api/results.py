"""
Results API endpoints for downloading processed files.
"""

import os
import logging
from flask import Blueprint, jsonify, send_file, send_from_directory
from pathlib import Path

from services.job_queue import get_job_queue
from services.storage_service import StorageService
import config

logger = logging.getLogger(__name__)

results_bp = Blueprint('results', __name__)

# Initialize services
job_queue = get_job_queue()
storage_service = StorageService()


@results_bp.route('/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get processing results for a completed job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON response with results and download links
    """
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
            'excel_file': f"/api/export/{job_id}/excel",
            'pages': results
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@results_bp.route('/export/<job_id>/excel', methods=['GET'])
def download_excel(job_id):
    """Download Excel file with measurements.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Excel file download
    """
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


@results_bp.route('/download/<job_id>/<filename>', methods=['GET'])
def download_image(job_id, filename):
    """Download a processed image.
    
    Args:
        job_id: Job identifier
        filename: Image filename
        
    Returns:
        Image file download
    """
    try:
        # Construct file path
        file_path = Path(config.OUTPUT_FOLDER) / job_id / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Send file
        return send_file(
            file_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@results_bp.route('/download/<job_id>/all', methods=['GET'])
def download_all(job_id):
    """Download all processed images as a ZIP file.
    
    Args:
        job_id: Job identifier
        
    Returns:
        ZIP file download
    """
    try:
        import zipfile
        import io
        
        job_data = job_queue.get_job_status(job_id)
        
        if not job_data:
            return jsonify({'error': 'Job not found'}), 404
        
        if job_data.get('status') != 'completed':
            return jsonify({'error': 'Job not completed'}), 400
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all images
            job_dir = Path(config.OUTPUT_FOLDER) / job_id
            
            if job_dir.exists():
                for file_path in job_dir.glob('page_*.png'):
                    zip_file.write(file_path, file_path.name)
                
                # Add Excel file if exists
                excel_path = job_data.get('excel_path')
                if excel_path and os.path.exists(excel_path):
                    zip_file.write(excel_path, os.path.basename(excel_path))
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'tendon_analysis_{job_id}.zip'
        )
        
    except Exception as e:
        logger.error(f"Error creating ZIP: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

