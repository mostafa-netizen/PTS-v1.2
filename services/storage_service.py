"""
Storage service for managing file uploads and results.
"""

import os
import logging
import cv2
import pandas as pd
from pathlib import Path

from storage.local_storage import LocalStorage
import config

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage operations."""
    
    def __init__(self, backend=None):
        """Initialize storage service.
        
        Args:
            backend: Storage backend instance (defaults to LocalStorage)
        """
        if backend is None:
            self.backend = LocalStorage(base_path=config.OUTPUT_FOLDER)
        else:
            self.backend = backend
        
        # Create upload directory
        self.upload_dir = Path(config.UPLOAD_FOLDER)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("StorageService initialized")
    
    def save_upload(self, job_id, file):
        """Save uploaded PDF file.
        
        Args:
            job_id: Unique job identifier
            file: File object from Flask request
            
        Returns:
            str: Path to saved file
        """
        filename = f"{job_id}_{file.filename}"
        filepath = self.upload_dir / filename
        file.save(filepath)
        logger.info(f"Saved upload: {filename}")
        return str(filepath)
    
    def save_result_image(self, job_id, page_num, image_data):
        """Save processed result image.
        
        Args:
            job_id: Job identifier
            page_num: Page number
            image_data: Image as numpy array or bytes
            
        Returns:
            str: URL to access the image
        """
        filename = f"page_{page_num}.png"
        path = f"{job_id}/{filename}"
        
        # Convert numpy array to bytes if needed
        if hasattr(image_data, 'shape'):  # numpy array
            _, buffer = cv2.imencode('.png', image_data)
            data = buffer.tobytes()
        else:
            data = image_data
        
        self.backend.save_file(path, data)
        url = self.backend.get_url(path)
        
        logger.debug(f"Saved result image: {path}")
        return url
    
    def save_excel(self, job_id, dataframe):
        """Save Excel file with measurements.
        
        Args:
            job_id: Job identifier
            dataframe: Pandas DataFrame with measurement data
            
        Returns:
            str: Path to Excel file
        """
        filename = f"{job_id}_measurements.xlsx"
        path = f"{job_id}/{filename}"
        
        # Create temporary file
        temp_path = Path(config.OUTPUT_FOLDER) / job_id
        temp_path.mkdir(parents=True, exist_ok=True)
        excel_file = temp_path / filename
        
        # Save Excel with formatting
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            dataframe.to_excel(
                writer,
                sheet_name='Measurements',
                index=False
            )
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Measurements']
            for column in worksheet.columns:
                max_length = 0
                column_cells = [cell for cell in column]
                for cell in column_cells:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50
                worksheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width
        
        logger.info(f"Saved Excel file: {path}")
        return str(excel_file)
    
    def get_result_url(self, job_id, filename):
        """Get URL for accessing a result file.
        
        Args:
            job_id: Job identifier
            filename: Filename
            
        Returns:
            str: URL to access the file
        """
        path = f"{job_id}/{filename}"
        return self.backend.get_url(path)
    
    def delete_job_files(self, job_id):
        """Delete all files associated with a job.
        
        Args:
            job_id: Job identifier
        """
        # Delete from backend storage
        job_path = Path(config.OUTPUT_FOLDER) / job_id
        if job_path.exists():
            import shutil
            shutil.rmtree(job_path)
            logger.info(f"Deleted job files: {job_id}")
        
        # Delete upload file
        for upload_file in self.upload_dir.glob(f"{job_id}_*"):
            upload_file.unlink()
            logger.debug(f"Deleted upload: {upload_file.name}")

