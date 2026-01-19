# Structural Drawing Analysis Platform - Production Ready

A production-ready platform for analyzing structural drawings and extracting tendon measurements with Excel export capabilities.

## 🎯 Features

- ✅ **PDF Processing**: Convert and analyze structural drawings
- ✅ **OCR with DocTR**: Advanced text recognition with GPU acceleration
- ✅ **Line Detection**: Detect and measure tendon lines
- ✅ **Scale Detection**: Automatic scale extraction from drawings
- ✅ **Excel Export**: Export measurements to formatted Excel files
- ✅ **Multi-page Support**: Process entire PDF documents
- ✅ **REST API**: Complete API for integration
- ✅ **Background Processing**: Async job queue (with Redis)
- ✅ **Modular Architecture**: Clean separation of concerns

## 📁 Project Structure

```
project-latest-update/
├── api/                      # API endpoints
│   ├── __init__.py
│   ├── upload.py            # File upload endpoints
│   ├── processing.py        # Job status endpoints
│   └── results.py           # Results & download endpoints
├── services/                 # Business logic
│   ├── __init__.py
│   ├── processing_service.py # PDF processing
│   ├── storage_service.py    # File storage
│   ├── job_queue.py          # Job queue management
│   └── processing_worker.py  # Background worker
├── storage/                  # Storage backends
│   ├── __init__.py
│   ├── base.py              # Storage interface
│   └── local_storage.py     # Local filesystem
├── ocr/                      # OCR modules
│   ├── __init__.py
│   ├── doctr.py             # DocTR integration
│   ├── extractor.py         # Text extraction
│   ├── line_detector.py     # Line detection
│   └── base_extractor.py    # Base extractor
├── img_templates/            # Template images (10.png, 11.png)
├── app_new.py               # Main Flask application
├── config.py                # Configuration
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── test_setup.py            # Setup verification script
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (macOS)
brew install poppler  # For PDF processing

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install poppler-utils
```

### 2. Verify Setup

```bash
python test_setup.py
```

This will check:
- ✅ All required Python packages
- ✅ GPU availability
- ✅ Configuration
- ✅ Service imports
- ✅ API endpoints

### 3. Run the Server

```bash
# Development mode
python app_new.py

# Production mode (with Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app_new:app
```

### 4. Test the API

```bash
# Upload a PDF
curl -X POST -F "file=@plan.pdf" http://localhost:3000/api/upload

# Check status
curl http://localhost:3000/api/status/<job_id>

# Get results
curl http://localhost:3000/api/results/<job_id>

# Download Excel
curl -O http://localhost:3000/api/export/<job_id>/excel
```

## 📊 API Endpoints

### Upload
- `POST /api/upload` - Upload PDF file
  - Returns: `job_id`, `status`

### Processing
- `GET /api/status/<job_id>` - Get job status
  - Returns: `status`, `progress`, `message`
- `POST /api/cancel/<job_id>` - Cancel job

### Results
- `GET /api/results/<job_id>` - Get processing results
  - Returns: `pages`, `measurements`, `excel_file`
- `GET /api/export/<job_id>/excel` - Download Excel file
- `GET /api/download/<job_id>/<filename>` - Download image
- `GET /api/download/<job_id>/all` - Download ZIP with all files

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG_MODE=true

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Processing
PDF_DPI=200
OCR_BATCH_SIZE=24
TILE_SIZE=1000
TILE_OVERLAP=250

# Storage
STORAGE_BACKEND=local
OUTPUT_FOLDER=./outputs
UPLOAD_FOLDER=./uploads
```

### config.py

Edit `config.py` for advanced configuration:
- PDF processing settings
- OCR parameters
- GPU settings
- Server configuration

## 🔧 Development vs Production

### Development Mode (Current)
- ✅ In-memory job queue
- ✅ Immediate processing
- ✅ Local file storage
- ✅ Debug logging

### Production Mode (Optional)
- 🔄 Redis job queue
- 🔄 Background workers (RQ)
- 🔄 DigitalOcean Spaces storage
- 🔄 Authentication
- 🔄 Nginx + Gunicorn

## 📈 Excel Export Format

The exported Excel file contains:

| Column | Description |
|--------|-------------|
| Callouts | Tendon identifier (e.g., "TENDON BANDED (1)") |
| Measurements | Calculated measurement (e.g., "~45.23'") |
| page | Page number in PDF |

## 🧪 Testing

```bash
# Run setup tests
python test_setup.py

# Test with sample PDF
python main.py

# Test API
python -m pytest tests/  # (when tests are added)
```

## 📝 Next Steps

1. ✅ **Phase 1-6 Complete**: Core algorithm, services, API
2. 🔄 **Phase 7**: Frontend development (React UI)
3. 🔄 **Phase 8**: RunPod GPU integration
4. 🔄 **Phase 9**: Authentication system
5. 🔄 **Phase 10**: Deployment (DigitalOcean)

## 🐛 Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### GPU Not Available
- Check: `python test_setup.py`
- Set `USE_GPU=False` in config.py for CPU mode

### Redis Connection Error
- Development: Uses in-memory queue automatically
- Production: Install and start Redis

## 📚 Documentation

- [Configuration Guide](CONFIG_GUIDE.md)
- [API Documentation](API_DOCS.md) (to be created)
- [Deployment Guide](DEPLOYMENT.md) (to be created)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- DocTR for OCR
- OpenCV for image processing
- Flask for web framework

