"""
Processing API endpoints for job status and management.
"""

import logging
from flask import Blueprint, jsonify

from services.job_queue import get_job_queue

logger = logging.getLogger(__name__)

processing_bp = Blueprint('processing', __name__)

# Initialize job queue
job_queue = get_job_queue()


@processing_bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status for a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON response with job status
    """
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
                'excel_available': bool(job_data.get('excel_path'))
            })
        
        elif job_data.get('status') == 'failed':
            response['error'] = job_data.get('error', 'Unknown error')
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@processing_bp.route('/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    """Cancel a processing job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON response with cancellation status
    """
    try:
        job_data = job_queue.get_job_status(job_id)
        
        if not job_data:
            return jsonify({'error': 'Job not found'}), 404
        
        current_status = job_data.get('status')
        
        if current_status in ['completed', 'failed']:
            return jsonify({
                'error': f'Cannot cancel job with status: {current_status}'
            }), 400
        
        # Update job status to cancelled
        job_queue.update_job_status(
            job_id,
            'cancelled',
            message='Job cancelled by user'
        )
        
        logger.info(f"Job cancelled: {job_id}")
        
        return jsonify({
            'job_id': job_id,
            'status': 'cancelled',
            'message': 'Job cancelled successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error cancelling job: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@processing_bp.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs (for admin/debugging).
    
    Returns:
        JSON response with list of jobs
    """
    try:
        # This is a simplified implementation
        # In production, you'd want to implement proper job listing from Redis
        return jsonify({
            'message': 'Job listing not implemented yet',
            'note': 'Use /api/status/<job_id> to check specific job status'
        }), 501
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

