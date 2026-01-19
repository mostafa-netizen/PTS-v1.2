"""
Configuration file for Structural Drawing Analysis Platform

This file contains all configurable parameters for both the server and main.py.
You can modify these values to customize the behavior without changing the code.
"""

import os

# ============================================================
# PDF PROCESSING CONFIGURATION
# ============================================================

# DPI for PDF to image conversion
# Default: 200 (pdf2image default)
# Higher values = better quality but slower processing and larger files
PDF_DPI = 200

# OCR batch size - number of tiles to process at once
# Default: 24
# Higher values = faster processing but more memory usage
# Lower values = slower but uses less memory
OCR_BATCH_SIZE = 24

# ============================================================
# MAIN.PY CONFIGURATION (Command Line Processing)
# ============================================================

# Input PDF file path for main.py
# You can use absolute path or relative path from project root
INPUT_PDF_PATH = '/Users/mostafaazab/Desktop/Work/Truestack AI/Rick Thompson/Plan Samples/plan.pdf'

# Alternative: Use a relative path
# INPUT_PDF_PATH = 'data/plan.pdf'

# Output directory for processed images
OUTPUT_DIR = 'data/final_output'

# Output filename pattern
# {i} will be replaced with page number
OUTPUT_FILENAME_PATTERN = 'tendons-{i}.png'

# Whether to automatically open the result image after processing
# Set to False if you don't want images to open automatically
AUTO_OPEN_RESULT = True

# ============================================================
# SERVER CONFIGURATION
# ============================================================

# Server host and port
SERVER_HOST = '0.0.0.0'  # 0.0.0.0 means accessible from any network interface
SERVER_PORT = 3000

# Upload folder for temporary PDF storage
UPLOAD_FOLDER = 'uploads'

# Output folder for processed results
OUTPUT_FOLDER = 'outputs'
SERVER_OUTPUT_FOLDER = 'outputs'  # Deprecated, use OUTPUT_FOLDER

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'pdf'}

# Maximum file size for upload (in bytes)
# Default: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# ============================================================
# PROCESSING CONFIGURATION
# ============================================================

# Tile size for OCR processing
TILE_SIZE = 1000

# Tile overlap for OCR processing
TILE_OVERLAP = 250

# ============================================================
# REDIS CONFIGURATION (for production)
# ============================================================

# Redis connection settings
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# ============================================================
# RUNPOD CONFIGURATION (GPU Processing)
# ============================================================

# RunPod API settings
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY', '')
RUNPOD_ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID', '')
FORCE_RUNPOD = os.getenv('FORCE_RUNPOD', 'false').lower() == 'true'

# ============================================================
# STORAGE CONFIGURATION
# ============================================================

# Storage backend: 'local' or 'spaces'
STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'local')

# DigitalOcean Spaces configuration
DO_SPACE_NAME = os.getenv('DO_SPACE_NAME', '')
DO_REGION = os.getenv('DO_REGION', 'nyc3')
DO_ACCESS_KEY = os.getenv('DO_ACCESS_KEY', '')
DO_SECRET_KEY = os.getenv('DO_SECRET_KEY', '')

# ============================================================
# AUTHENTICATION CONFIGURATION
# ============================================================

# Enable authentication
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'

# Flask secret key for sessions
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Session configuration
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

# ============================================================
# GPU CONFIGURATION
# ============================================================

# Enable GPU acceleration if available
# Set to False to force CPU usage
USE_GPU = True

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

# Log file path
LOG_FILE = 'server.log'

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# Enable detailed debug logging
DEBUG_MODE = True

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_output_path(page_number):
    """Generate output path for a given page number"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = OUTPUT_FILENAME_PATTERN.format(i=page_number)
    return os.path.join(OUTPUT_DIR, filename)

def validate_config():
    """Validate configuration values"""
    errors = []
    
    # Validate DPI
    if not isinstance(PDF_DPI, int) or PDF_DPI < 72 or PDF_DPI > 600:
        errors.append("PDF_DPI must be an integer between 72 and 600")
    
    # Validate batch size
    if not isinstance(OCR_BATCH_SIZE, int) or OCR_BATCH_SIZE < 1 or OCR_BATCH_SIZE > 100:
        errors.append("OCR_BATCH_SIZE must be an integer between 1 and 100")
    
    # Validate port
    if not isinstance(SERVER_PORT, int) or SERVER_PORT < 1024 or SERVER_PORT > 65535:
        errors.append("SERVER_PORT must be an integer between 1024 and 65535")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

# Validate configuration on import
validate_config()

# ============================================================
# CONFIGURATION SUMMARY
# ============================================================

def print_config():
    """Print current configuration"""
    print("=" * 60)
    print("📋 CURRENT CONFIGURATION")
    print("=" * 60)
    print(f"PDF DPI:              {PDF_DPI}")
    print(f"OCR Batch Size:       {OCR_BATCH_SIZE}")
    print(f"Input PDF:            {INPUT_PDF_PATH}")
    print(f"Output Directory:     {OUTPUT_DIR}")
    print(f"Auto-open Result:     {AUTO_OPEN_RESULT}")
    print(f"Server Host:          {SERVER_HOST}")
    print(f"Server Port:          {SERVER_PORT}")
    print(f"Use GPU:              {USE_GPU}")
    print(f"Debug Mode:           {DEBUG_MODE}")
    print("=" * 60)

if __name__ == '__main__':
    print_config()

