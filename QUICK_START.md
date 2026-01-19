# 🚀 Quick Start Guide - Structural Drawing Analysis Platform

## ⚡ Get Started in 3 Steps

### Step 1: Start the Server
```bash
cd /Users/mostafaazab/Downloads/project-latest-update
python3 app.py
```

You should see:
```
============================================================
🚀 Starting Structural Drawing Analysis Platform
============================================================
Server: http://0.0.0.0:5001
GPU Enabled: True
============================================================
 * Running on http://127.0.0.1:5001
```

### Step 2: Open the Web Interface
Open your browser and navigate to:
```
http://localhost:5001
```

### Step 3: Upload and Process
1. **Upload PDF**: Drag & drop or click "Browse Files"
2. **Click**: "🚀 Plan and Process"
3. **Wait**: Processing takes 30-60 seconds per page
4. **Download**: Get annotated images and Excel file ⭐

---

## 📊 What You Get

### Annotated Images
- Visual representation of detected tendons
- Color-coded lines
- Callout text overlays
- Measurement annotations

### Excel Spreadsheet ⭐ NEW
- **Columns**: Callout, Measurement, Page
- **Format**: Professional .xlsx file
- **Size**: ~5-10KB
- **Compatible**: Excel, Google Sheets, LibreOffice

---

## 🎯 Example Output

### Input
- `test_drawing.pdf` (structural engineering drawing)

### Output
- `page_0.png` (annotated image)
- `measurements.xlsx` (Excel file)

### Excel Content
```
Callout                  | Measurement | Page
-------------------------|-------------|-----
TENDON BANDED (1)        | ~45.23'     | 0
TENDON BANDED (2)        | ~38.67'     | 0
TENDON BANDED (3)        | ~42.15'     | 0
...
```

---

## 🔧 Troubleshooting

### Server won't start?
```bash
# Kill existing process on port 5001
lsof -ti:5001 | xargs kill -9
python3 app.py
```

### Can't access http://localhost:5001?
- Check firewall settings
- Try http://127.0.0.1:5001
- Check terminal for errors

### Processing fails?
- Check PDF is valid
- Check file size < 100MB
- Check terminal logs for errors

### Excel file not downloading?
- Check job completed successfully
- Check browser download settings
- Try different browser

---

## 📁 File Locations

- **Uploads**: `uploads/` (auto-created)
- **Results**: `outputs/{job_id}/` (auto-created)
  - Annotated images: `page_0.png`, `page_1.png`, ...
  - Excel file: `measurements.xlsx`
- **Web Interface**: `index.html`
- **Backend**: `app.py`
- **Services**: `services/`
- **Utilities**: `utils/`

---

## 🎯 API Endpoints

### Upload PDF
```bash
POST /api/upload
```

### Check Status
```bash
GET /api/status/{job_id}
```

### Get Results
```bash
GET /api/results/{job_id}
```

### Download Image
```bash
GET /api/download/{job_id}/{filename}
```

### Download Excel ⭐ NEW
```bash
GET /api/export/{job_id}/excel
```

### Health Check
```bash
GET /health
```

---

## 📚 Documentation

- **README.md** - Full documentation
- **TESTING_GUIDE.md** - Testing procedures
- **PROJECT_COMPLETE.md** - Project summary
- **EXCEL_EXPORT_GUIDE.md** - Excel export details
- **FRONTEND_INTEGRATION.md** - Frontend integration
- **IMPLEMENTATION_PLAN.md** - Development phases

---

## 🎉 That's It!

You're ready to process structural drawings and export measurements to Excel!

**Processing Time**: 30-60 seconds per page
**Supported Format**: PDF only
**Max File Size**: 100MB
**GPU Acceleration**: Enabled

**Need help?** Check the documentation or review the logs in the terminal.

---

**Ready in 1 minute!** ⚡

