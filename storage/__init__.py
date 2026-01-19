"""
Storage module for file management.
Supports local filesystem and cloud storage (DigitalOcean Spaces).
"""

from .base import StorageBackend
from .local_storage import LocalStorage

__all__ = ['StorageBackend', 'LocalStorage']

