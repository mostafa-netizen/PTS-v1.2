# Testing Guide - Structural Drawing Analysis Platform

## 🎯 Overview

This guide provides comprehensive testing procedures for the Structural Drawing Analysis Platform with Excel export functionality.

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /Users/mostafaazab/Downloads/project-latest-update
python3 app.py
```

Expected output:
```
============================================================
🚀 Starting Structural Drawing Analysis Platform
============================================================
Server: http://0.0.0.0:5001
GPU Enabled: True
============================================================
 * Running on http://127.0.0.1:5001
```

### 2. Open Browser
Navigate to: `http://localhost:5001`

## 📋 Test Cases

### Test Case 1: Single Page PDF Upload

**Steps:**
1. Open `http://localhost:5001`
2. Click "Get Started" or scroll to upload section
3. Drag & drop `test_drawing.pdf` or click "Browse Files"
4. Click "🚀 Plan and Process"

**Expected Results:**
- ✅ File uploads successfully
- ✅ Progress bar appears and updates
- ✅ Status messages show: "Converting PDF...", "Processing page 1 of 1..."
- ✅ Processing completes within 30-60 seconds
- ✅ Results page displays with 4 statistics cards
- ✅ Excel download card appears (green background)
- ✅ Annotated image shows detected tendons

**Verify:**
- Total pages: 1
- Tendons detected: ~10-15 (depends on drawing)
- Excel available: Yes
- Results generated: 1

---

### Test Case 2: Excel File Download

**Prerequisites:** Complete Test Case 1

**Steps:**
1. On results page, locate green "Excel Measurements Ready" card
2. Click "Download Excel" button

**Expected Results:**
- ✅ Excel file downloads immediately
- ✅ Filename: `tendon_measurements_{job_id}.xlsx`
- ✅ File size: ~5-10 KB

**Verify Excel Content:**
1. Open downloaded Excel file
2. Check columns: Callout, Measurement, Page
3. Verify data:
   - Callouts like "TENDON BANDED (1)", "TENDON BANDED (2)"
   - Measurements like "~45.23'", "~38.67'"
   - Page numbers (all should be 0 for single page)
4. Check formatting:
   - Column widths auto-adjusted
   - Headers are bold
   - Data is readable

---

### Test Case 3: Download All Files

**Prerequisites:** Complete Test Case 1

**Steps:**
1. On results page, scroll to bottom
2. Click "Download All Results" button

**Expected Results:**
- ✅ Multiple downloads start (one per image + Excel)
- ✅ Downloads include:
  - `page_0.png` (annotated image)
  - `tendon_measurements_{job_id}.xlsx` (Excel file)
- ✅ All files download successfully

---

### Test Case 4: Individual Image Download

**Prerequisites:** Complete Test Case 1

**Steps:**
1. On results page, locate image grid
2. Click "Download" button on any image card

**Expected Results:**
- ✅ Image downloads immediately
- ✅ Filename: `page_0.png`
- ✅ Image shows annotated drawing with:
  - Detected lines (colored)
  - Callout text
  - Measurement text

---

### Test Case 5: Multi-Page PDF Upload

**Steps:**
1. Upload a multi-page PDF (if available)
2. Click "🚀 Plan and Process"

**Expected Results:**
- ✅ Progress updates for each page
- ✅ Status shows "Processing page X of Y..."
- ✅ All pages processed successfully
- ✅ Results show multiple images
- ✅ Excel contains data from all pages
- ✅ Page column in Excel shows correct page numbers (0, 1, 2, ...)

---

### Test Case 6: Error Handling - Invalid File

**Steps:**
1. Try to upload a non-PDF file (e.g., .txt, .jpg)

**Expected Results:**
- ✅ Error message: "Only PDF files are allowed"
- ✅ Upload is rejected
- ✅ No processing starts

---

### Test Case 7: Error Handling - Large File

**Steps:**
1. Try to upload a PDF larger than 100MB

**Expected Results:**
- ✅ Error message: "File too large. Maximum size: 100MB"
- ✅ Upload is rejected
- ✅ No processing starts

---

### Test Case 8: Job Status API

**Prerequisites:** Start a processing job

**Steps:**
1. Open browser console (F12)
2. Note the job_id from upload response
3. Test API endpoint:
```javascript
fetch('/api/status/{job_id}')
  .then(r => r.json())
  .then(console.log)
```

**Expected Response:**
```json
{
  "job_id": "abc-123-def",
  "status": "processing",
  "progress": 50,
  "message": "Processing page 1 of 2...",
  "filename": "test_drawing.pdf",
  "total_pages": 2,
  "current_page": 1
}
```

---

### Test Case 9: Results API

**Prerequisites:** Complete a processing job

**Steps:**
1. Test API endpoint:
```javascript
fetch('/api/results/{job_id}')
  .then(r => r.json())
  .then(console.log)
```

**Expected Response:**
```json
{
  "job_id": "abc-123-def",
  "status": "completed",
  "total_pages": 1,
  "total_tendons": 12,
  "excel_available": true,
  "excel_file": "/api/export/abc-123-def/excel",
  "results": [
    {
      "page": 0,
      "filename": "page_0.png",
      "path": "outputs/abc-123-def/page_0.png"
    }
  ]
}
```

---

### Test Case 10: Excel Export API

**Prerequisites:** Complete a processing job

**Steps:**
1. Test API endpoint directly:
```bash
curl -O http://localhost:5001/api/export/{job_id}/excel
```

**Expected Results:**
- ✅ Excel file downloads
- ✅ File is valid .xlsx format
- ✅ Opens in Excel/Google Sheets

---

## 🔍 Verification Checklist

### Frontend UI
- [ ] Landing page loads correctly
- [ ] Upload area is visible and functional
- [ ] Drag & drop works
- [ ] File browser works
- [ ] Progress bar animates smoothly
- [ ] Status messages update in real-time
- [ ] Results page displays correctly
- [ ] Statistics cards show correct data
- [ ] Excel download card is prominent
- [ ] Image grid displays properly
- [ ] All buttons are clickable
- [ ] Responsive design works on mobile

### Backend Processing
- [ ] PDF uploads successfully
- [ ] OCR detects text correctly
- [ ] Line detection works
- [ ] Measurements are calculated
- [ ] Annotated images are generated
- [ ] Excel file is created
- [ ] Job status updates correctly
- [ ] Error handling works
- [ ] Logging is comprehensive

### Excel Export
- [ ] Excel file is generated
- [ ] File format is correct (.xlsx)
- [ ] Columns are present (Callout, Measurement, Page)
- [ ] Data is accurate
- [ ] Formatting is professional
- [ ] File opens in Excel
- [ ] File opens in Google Sheets
- [ ] File size is reasonable (<1MB)

### API Endpoints
- [ ] POST /api/upload works
- [ ] GET /api/status/{job_id} works
- [ ] GET /api/results/{job_id} works
- [ ] GET /api/download/{job_id}/{filename} works
- [ ] GET /api/export/{job_id}/excel works
- [ ] GET /health works
- [ ] Error responses are proper JSON

## 🐛 Common Issues & Solutions

### Issue: Server won't start
**Solution:**
```bash
# Kill existing process on port 5001
lsof -ti:5001 | xargs kill -9
python3 app.py
```

### Issue: Excel file not found
**Solution:**
- Check `outputs/{job_id}/` folder exists
- Verify processing completed successfully
- Check logs for errors

### Issue: Images not displaying
**Solution:**
- Check browser console for errors
- Verify API endpoint returns correct paths
- Check file permissions in outputs folder

### Issue: Processing takes too long
**Solution:**
- Check GPU availability
- Reduce batch size in config
- Check system resources

## 📊 Performance Benchmarks

### Expected Processing Times
- **Single page PDF**: 30-60 seconds
- **5-page PDF**: 2-5 minutes
- **10-page PDF**: 5-10 minutes

### Expected File Sizes
- **Annotated PNG**: 500KB - 2MB per page
- **Excel file**: 5-10KB
- **Total output**: ~1-5MB per page

## ✅ Success Criteria

A successful test run should demonstrate:
1. ✅ PDF uploads without errors
2. ✅ Processing completes successfully
3. ✅ Annotated images show detected tendons
4. ✅ Excel file downloads correctly
5. ✅ Excel contains accurate measurements
6. ✅ UI is responsive and user-friendly
7. ✅ Error handling works properly
8. ✅ All API endpoints respond correctly

## 🎯 Next Steps After Testing

If all tests pass:
1. ✅ Platform is ready for production use
2. ✅ Can process real structural drawings
3. ✅ Excel export is fully functional

If tests fail:
1. Check logs in terminal
2. Review error messages
3. Verify file paths and permissions
4. Check dependencies are installed
5. Consult TROUBLESHOOTING.md

## 📝 Test Report Template

```
Test Date: ___________
Tester: ___________

Test Case 1: [ ] Pass [ ] Fail
Test Case 2: [ ] Pass [ ] Fail
Test Case 3: [ ] Pass [ ] Fail
Test Case 4: [ ] Pass [ ] Fail
Test Case 5: [ ] Pass [ ] Fail
Test Case 6: [ ] Pass [ ] Fail
Test Case 7: [ ] Pass [ ] Fail
Test Case 8: [ ] Pass [ ] Fail
Test Case 9: [ ] Pass [ ] Fail
Test Case 10: [ ] Pass [ ] Fail

Notes:
_________________________________
_________________________________
_________________________________

Overall Result: [ ] Pass [ ] Fail
```

---

**Happy Testing! 🎉**

