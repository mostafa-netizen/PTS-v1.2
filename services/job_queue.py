"""
Job queue service using Redis for background processing.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from redis import Redis
    from rq import Queue
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

import config

logger = logging.getLogger(__name__)


class InMemoryJobQueue:
    """In-memory job queue for development (when Redis is not available)."""
    
    def __init__(self):
        self.jobs = {}
        logger.warning("Using in-memory job queue (Redis not available)")
    
    def enqueue_job(self, job_id, pdf_path, **kwargs):
        """Add job to queue (immediately processes in development)."""
        self.jobs[job_id] = {
            'status': 'queued',
            'pdf_path': pdf_path,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        return job_id
    
    def get_job_status(self, job_id):
        """Get job status."""
        return self.jobs.get(job_id, {})
    
    def update_job_status(self, job_id, status, **kwargs):
        """Update job status."""
        if job_id not in self.jobs:
            self.jobs[job_id] = {}
        
        self.jobs[job_id].update({
            'status': status,
            'updated_at': datetime.now().isoformat(),
            **kwargs
        })
    
    def get_job_results(self, job_id):
        """Get job results."""
        job = self.jobs.get(job_id, {})
        return job.get('results', [])
    
    def save_job_results(self, job_id, results):
        """Save job results."""
        if job_id in self.jobs:
            self.jobs[job_id]['results'] = results


class RedisJobQueue:
    """Redis-based job queue for production."""
    
    def __init__(self):
        """Initialize Redis connection and queue."""
        try:
            self.redis_conn = Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
                decode_responses=True
            )
            
            # Test connection
            self.redis_conn.ping()
            
            self.queue = Queue('processing', connection=self.redis_conn)
            logger.info("RedisJobQueue initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def enqueue_job(self, job_id, pdf_path, **kwargs):
        """Add job to processing queue.
        
        Args:
            job_id: Unique job identifier
            pdf_path: Path to PDF file
            **kwargs: Additional job parameters
            
        Returns:
            str: RQ job ID
        """
        job = self.queue.enqueue(
            'services.processing_worker.process_pdf_job',
            job_id=job_id,
            pdf_path=pdf_path,
            job_timeout='30m',
            **kwargs
        )
        
        # Initialize job status in Redis
        self.update_job_status(
            job_id,
            'queued',
            rq_job_id=job.id,
            pdf_path=pdf_path,
            **kwargs
        )
        
        logger.info(f"Enqueued job {job_id} (RQ job: {job.id})")
        return job.id
    
    def get_job_status(self, job_id):
        """Get job status from Redis.
        
        Args:
            job_id: Job identifier
            
        Returns:
            dict: Job status data
        """
        job_data = self.redis_conn.hgetall(f'job:{job_id}')
        
        # Convert numeric fields
        if job_data:
            for key in ['progress', 'total_pages', 'current_page']:
                if key in job_data:
                    try:
                        job_data[key] = int(job_data[key])
                    except (ValueError, TypeError):
                        pass
        
        return job_data
    
    def update_job_status(self, job_id, status, **kwargs):
        """Update job status in Redis.
        
        Args:
            job_id: Job identifier
            status: Job status (queued, processing, completed, failed)
            **kwargs: Additional status fields
        """
        data = {
            'status': status,
            'updated_at': datetime.now().isoformat(),
            **kwargs
        }
        
        self.redis_conn.hset(f'job:{job_id}', mapping=data)
        
        # Set TTL for automatic cleanup (7 days)
        self.redis_conn.expire(f'job:{job_id}', 7 * 24 * 60 * 60)
    
    def get_job_results(self, job_id):
        """Get job results from Redis.
        
        Args:
            job_id: Job identifier
            
        Returns:
            list: Job results
        """
        results_json = self.redis_conn.get(f'job:{job_id}:results')
        if results_json:
            return json.loads(results_json)
        return []
    
    def save_job_results(self, job_id, results):
        """Save job results to Redis.
        
        Args:
            job_id: Job identifier
            results: Results data (will be JSON serialized)
        """
        self.redis_conn.set(
            f'job:{job_id}:results',
            json.dumps(results),
            ex=7 * 24 * 60 * 60  # 7 days TTL
        )


# Factory function to get appropriate job queue
def get_job_queue():
    """Get job queue instance (Redis if available, otherwise in-memory)."""
    if REDIS_AVAILABLE and config.REDIS_HOST:
        try:
            return RedisJobQueue()
        except Exception as e:
            logger.warning(f"Failed to create Redis queue, falling back to in-memory: {e}")
            return InMemoryJobQueue()
    else:
        return InMemoryJobQueue()

