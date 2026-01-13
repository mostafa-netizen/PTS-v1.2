# Structural Drawing Analysis Platform

AI-Powered Tendon Detection and Analysis for Construction Plans

## Overview

This platform uses advanced computer vision and OCR technology to automatically analyze PDF structural drawings, detect tendons, and generate annotated visualizations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Hero Section │  │ File Upload  │  │   Results    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           │                │                  │              │
│           └────────────────┴──────────────────┘              │
│                          │                                   │
│                    Axios HTTP Client                         │
└──────────────────────────┼──────────────────────────────────┘
                           │
                    REST API (Flask)
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                    Backend (Python)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Flask API (app.py)                                  │   │
│  │  - /api/upload      - /api/status/:id                │   │
│  │  - /api/results/:id - /api/download/:id/:file        │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │  Processing Pipeline (main.py)                       │   │
│  │  1. PDF → Images (pdf2image)                         │   │
│  │  2. Image Tiling (crop_tiles)                        │   │
│  │  3. OCR Processing (DocTR + PyTorch)                 │   │
│  │  4. Tendon Extraction (test_extractor.py)            │   │
│  │  5. Line Detection (line_detector.py)                │   │
│  │  6. Result Generation (OpenCV)                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Features

- 🔍 **Advanced OCR**: State-of-the-art optical character recognition
- ⚡ **GPU Acceleration**: Fast processing with CUDA/MPS support
- 📊 **Detailed Results**: Visual annotations and data export
- 🎨 **Modern UI**: Industrial-themed responsive interface
- 📤 **Easy Upload**: Drag-and-drop PDF file upload
- 📥 **Batch Download**: Download all processed images at once

## Tech Stack

### Backend
- Python 3.x
- Flask (Web API)
- PyTorch (Deep Learning)
- DocTR (OCR)
- OpenCV (Computer Vision)
- pdf2image (PDF Processing)

### Frontend
- React 18
- Vite (Build Tool)
- Tailwind CSS (Styling)
- Axios (HTTP Client)

## Installation

### Prerequisites
- Python 3.8+
- Node.js 18+ and npm
- poppler-utils (for PDF processing)

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install poppler (for PDF to image conversion):
   - **macOS**: `brew install poppler`
   - **Ubuntu/Debian**: `sudo apt-get install poppler-utils`
   - **Windows**: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Backend Server

From the project root directory:
```bash
python app.py
```

The Flask API will start on `http://localhost:5000`

### Start Frontend Development Server

In a new terminal, from the frontend directory:
```bash
cd frontend
npm run dev
```

The React app will start on `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Click "Get Started" or scroll to the upload section
3. Drag and drop a PDF file or click "Browse Files"
4. Click "Upload & Process" to start analysis
5. Wait for processing to complete (progress shown in real-time)
6. View and download annotated results

## API Endpoints

### POST /api/upload
Upload a PDF file for processing
- **Body**: multipart/form-data with 'file' field
- **Response**: `{ job_id: string, message: string }`

### GET /api/status/:job_id
Get processing status for a job
- **Response**: `{ status: string, message: string, progress: number, ... }`

### GET /api/results/:job_id
Get results for a completed job
- **Response**: `{ job_id: string, total_pages: number, results: [...] }`

### GET /api/download/:job_id/:filename
Download a specific result image
- **Response**: PNG image file

## Project Structure

```
.
├── app.py                  # Flask backend API
├── main.py                 # Core processing logic
├── test_extractor.py       # Tendon extraction
├── ocr/                    # OCR modules
│   ├── doctr.py
│   ├── extractor.py
│   └── line_detector.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── HeroSection.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ProcessingStatus.jsx
│   │   │   └── ResultsDisplay.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── uploads/                # Uploaded PDFs (created automatically)
├── outputs/                # Processed results (created automatically)
└── requirements.txt        # Python dependencies
```

## Configuration

### GPU Acceleration
The system automatically detects and uses available GPU:
- CUDA (NVIDIA GPUs)
- MPS (Apple Silicon M1/M2/M3/M4)
- Falls back to CPU if no GPU available

### File Size Limits
- Maximum PDF size: 50MB (configurable in FileUpload.jsx)

## Troubleshooting

### Backend Issues
- **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
- **PDF conversion fails**: Install poppler-utils
- **GPU not detected**: Check PyTorch installation and GPU drivers

### Frontend Issues
- **npm command not found**: Install Node.js
- **Dependencies not installing**: Try `npm install --legacy-peer-deps`
- **API connection fails**: Ensure backend is running on port 5000

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.

# PTS-proj.
