"""
Local filesystem storage backend.
"""

import os
import shutil
import logging
from pathlib import Path
from .base import StorageBackend

logger = logging.getLogger(__name__)


class LocalStorage(StorageBackend):
    """Local filesystem storage implementation."""
    
    def __init__(self, base_path='./outputs'):
        """Initialize local storage.
        
        Args:
            base_path: Base directory for storing files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorage initialized at {self.base_path}")
    
    def _get_full_path(self, path):
        """Get full filesystem path."""
        return self.base_path / path
    
    def save_file(self, path, data):
        """Save a file to local filesystem.
        
        Args:
            path: Relative path for the file
            data: File data (bytes, file-like object, or path to source file)
            
        Returns:
            str: Relative path to the saved file
        """
        full_path = self._get_full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, (str, Path)) and os.path.exists(data):
            # Copy from source file
            shutil.copy2(data, full_path)
        elif isinstance(data, bytes):
            # Write bytes
            full_path.write_bytes(data)
        else:
            # Write from file-like object
            with open(full_path, 'wb') as f:
                if hasattr(data, 'read'):
                    f.write(data.read())
                else:
                    f.write(data)
        
        logger.debug(f"Saved file: {path}")
        return str(path)
    
    def get_url(self, path):
        """Get URL for accessing a file.
        
        Args:
            path: Relative path to the file
            
        Returns:
            str: URL path (relative for local storage)
        """
        return f"/outputs/{path}"
    
    def delete_file(self, path):
        """Delete a file from local filesystem.
        
        Args:
            path: Relative path to the file
        """
        full_path = self._get_full_path(path)
        if full_path.exists():
            full_path.unlink()
            logger.debug(f"Deleted file: {path}")
    
    def file_exists(self, path):
        """Check if a file exists.
        
        Args:
            path: Relative path to the file
            
        Returns:
            bool: True if file exists
        """
        return self._get_full_path(path).exists()
    
    def get_full_path(self, path):
        """Get absolute filesystem path.
        
        Args:
            path: Relative path
            
        Returns:
            Path: Absolute path
        """
        return self._get_full_path(path)

