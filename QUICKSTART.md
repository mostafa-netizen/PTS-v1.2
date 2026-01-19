# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9 or higher
- Poppler (for PDF processing)

### Step 1: Install Dependencies

```bash
# Install Poppler (macOS)
brew install poppler

# Install Poppler (Ubuntu/Debian)
sudo apt-get install poppler-utils

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Verify Setup

```bash
python3 test_setup.py
```

You should see:
```
✅ All tests passed! System is ready.
```

### Step 3: Run the Server

```bash
python3 app_new.py
```

You should see:
```
============================================================
🚀 Starting Tendon Analysis Platform
============================================================
Server: http://0.0.0.0:3000
GPU Enabled: True
Debug Mode: True
============================================================
```

### Step 4: Test the API

#### Option A: Using cURL

```bash
# Upload a PDF
curl -X POST -F "file=@your_plan.pdf" http://localhost:3000/api/upload

# Response:
# {
#   "job_id": "abc-123-def-456",
#   "status": "completed",
#   "total_pages": 3,
#   "total_tendons": 45
# }

# Get results
curl http://localhost:3000/api/results/abc-123-def-456

# Download Excel
curl -O http://localhost:3000/api/export/abc-123-def-456/excel
```

#### Option B: Using Python

```python
import requests

# Upload PDF
with open('plan.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:3000/api/upload',
        files={'file': f}
    )
    
job_data = response.json()
job_id = job_data['job_id']

# Check status
status = requests.get(f'http://localhost:3000/api/status/{job_id}').json()
print(f"Status: {status['status']}, Progress: {status['progress']}%")

# Get results
results = requests.get(f'http://localhost:3000/api/results/{job_id}').json()
print(f"Total pages: {results['total_pages']}")
print(f"Total tendons: {results['total_tendons']}")

# Download Excel
excel_response = requests.get(f'http://localhost:3000/api/export/{job_id}/excel')
with open('measurements.xlsx', 'wb') as f:
    f.write(excel_response.content)
```

#### Option C: Using Postman

1. Open Postman
2. Create a new POST request to `http://localhost:3000/api/upload`
3. Go to Body → form-data
4. Add key: `file`, type: File, value: select your PDF
5. Click Send
6. Copy the `job_id` from the response
7. Create a GET request to `http://localhost:3000/api/results/{job_id}`

## 📊 Understanding the Response

### Upload Response
```json
{
  "job_id": "abc-123-def-456",
  "message": "Processing complete",
  "status": "completed",
  "filename": "plan.pdf",
  "total_pages": 3,
  "total_tendons": 45
}
```

### Status Response
```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "progress": 100,
  "message": "Processing complete",
  "filename": "plan.pdf",
  "total_pages": 3,
  "total_tendons": 45,
  "excel_available": true
}
```

### Results Response
```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "total_pages": 3,
  "total_tendons": 45,
  "excel_file": "/api/export/abc-123-def-456/excel",
  "pages": [
    {
      "page": 1,
      "image_url": "/outputs/abc-123-def-456/page_1.png",
      "tendons": [
        {
          "callout": "TENDON BANDED (1)",
          "measurement": "~45.23'",
          "page": 1
        }
      ]
    }
  ]
}
```

## 🔧 Configuration

### Basic Configuration (config.py)

```python
# PDF Processing
PDF_DPI = 200              # Higher = better quality, slower
OCR_BATCH_SIZE = 24        # Higher = faster, more memory

# Server
SERVER_PORT = 3000
USE_GPU = True             # Set to False for CPU-only

# Storage
OUTPUT_FOLDER = './outputs'
UPLOAD_FOLDER = './uploads'
```

### Environment Variables (.env)

```bash
# Copy example file
cp .env.example .env

# Edit as needed
nano .env
```

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Poppler not found" error
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

### GPU not available
- Check: `python3 test_setup.py`
- Set `USE_GPU=False` in config.py

### Port already in use
- Change `SERVER_PORT` in config.py
- Or kill the process: `lsof -ti:3000 | xargs kill`

## 📚 Next Steps

1. ✅ **Test with your PDFs**: Upload your structural drawings
2. ✅ **Check Excel output**: Verify measurements are correct
3. ✅ **Adjust configuration**: Tune DPI and batch size for your needs
4. 📖 **Read full documentation**: See README_NEW.md
5. 🎨 **Try the frontend**: Coming in Phase 7

## 💡 Tips

- **First run is slower**: Model downloads and initialization
- **GPU recommended**: 10x faster than CPU
- **Batch processing**: Upload multiple PDFs via API
- **Excel formatting**: Auto-adjusted columns, professional styling
- **Error handling**: Check logs in `server.log`

## 🎯 Common Use Cases

### Process a single PDF
```bash
curl -X POST -F "file=@plan.pdf" http://localhost:3000/api/upload
```

### Batch process multiple PDFs
```bash
for file in *.pdf; do
    curl -X POST -F "file=@$file" http://localhost:3000/api/upload
done
```

### Download all results as ZIP
```bash
curl -O http://localhost:3000/api/download/{job_id}/all
```

## ✨ Success!

If you've made it this far, you should have:
- ✅ Server running on http://localhost:3000
- ✅ Successfully uploaded a PDF
- ✅ Downloaded Excel with measurements
- ✅ Verified results are accurate

**Need help?** Check the logs in `server.log` or see IMPLEMENTATION_SUMMARY.md for details.

