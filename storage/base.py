"""
Base storage backend interface.
"""

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save_file(self, path, data):
        """Save a file.
        
        Args:
            path: Relative path for the file
            data: File data (bytes or file-like object)
            
        Returns:
            str: URL or path to the saved file
        """
        pass
    
    @abstractmethod
    def get_url(self, path):
        """Get URL for accessing a file.
        
        Args:
            path: Relative path to the file
            
        Returns:
            str: URL to access the file
        """
        pass
    
    @abstractmethod
    def delete_file(self, path):
        """Delete a file.
        
        Args:
            path: Relative path to the file
        """
        pass
    
    @abstractmethod
    def file_exists(self, path):
        """Check if a file exists.
        
        Args:
            path: Relative path to the file
            
        Returns:
            bool: True if file exists
        """
        pass

