"""
Background worker for processing PDF jobs.
This module is executed by RQ workers.
"""

import logging
from services.processing_service import ProcessingService
from services.storage_service import StorageService
from services.job_queue import get_job_queue

logger = logging.getLogger(__name__)


def process_pdf_job(job_id, pdf_path, **kwargs):
    """Process a PDF file in the background.
    
    This function is called by RQ workers to process jobs asynchronously.
    
    Args:
        job_id: Unique job identifier
        pdf_path: Path to the PDF file
        **kwargs: Additional processing parameters
        
    Returns:
        dict: Processing results
    """
    job_queue = get_job_queue()
    storage_service = StorageService()
    processing_service = ProcessingService(storage_service=storage_service)
    
    def progress_callback(progress, message):
        """Update job progress in Redis."""
        job_queue.update_job_status(
            job_id,
            'processing',
            progress=progress,
            message=message
        )
    
    try:
        logger.info(f"Starting background processing for job {job_id}")
        
        # Update status to processing
        job_queue.update_job_status(
            job_id,
            'processing',
            progress=0,
            message='Starting processing...'
        )
        
        # Process the PDF
        result = processing_service.process_pdf(
            pdf_path=pdf_path,
            job_id=job_id,
            gpu=kwargs.get('gpu', True),
            progress_callback=progress_callback
        )
        
        if result['success']:
            # Save results to Redis
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
            
            logger.info(f"Job {job_id} completed successfully")
            return result
        else:
            # Processing failed
            job_queue.update_job_status(
                job_id,
                'failed',
                error=result.get('error', 'Unknown error')
            )
            
            logger.error(f"Job {job_id} failed: {result.get('error')}")
            return result
            
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)
        
        # Update status to failed
        job_queue.update_job_status(
            job_id,
            'failed',
            error=str(e)
        )
        
        raise

