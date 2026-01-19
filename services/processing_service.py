"""
Processing service for PDF analysis and tendon extraction.
Handles OCR, line detection, and measurement calculations.
"""

import os
import logging
import sys
import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import cv2

from ocr.doctr import OCR
from test_extractor import extract_tendons
import config

logger = logging.getLogger(__name__)


# Compatibility function for Python < 3.12
def batched(iterable, n):
    """Batch data into lists of length n. The last batch may be shorter.

    This is a backport of itertools.batched from Python 3.12.
    """
    if sys.version_info >= (3, 12):
        from itertools import batched as _batched
        return _batched(iterable, n)

    # Manual implementation for older Python versions
    from itertools import islice
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, n))
        if not batch:
            return
        yield batch


def crop_tiles(image, tile_size=1000, overlap=250):
    """Crop image into overlapping tiles for OCR processing."""
    h, w = image.shape[:2]
    stride = tile_size - overlap

    tiles = []
    tile_id = 0

    for y in range(0, h, stride):
        for x in range(0, w, stride):
            tile = image[y:y + tile_size, x:x + tile_size]
            if tile.size == 0:
                continue

            tiles.append({
                "tile_id": tile_id,
                "x_offset": x,
                "y_offset": y,
                "image": tile
            })
            tile_id += 1
    return tiles


def project_tile_df_to_global(df_tile, x_offset, y_offset, tile_w, tile_h, full_w, full_h, tile_id):
    """Project tile coordinates to global image coordinates."""
    df = df_tile.copy()

    # tile → pixel
    df["x1_px"] = df["x1"] * tile_w + x_offset
    df["y1_px"] = df["y1"] * tile_h + y_offset
    df["x2_px"] = df["x2"] * tile_w + x_offset
    df["y2_px"] = df["y2"] * tile_h + y_offset

    # pixel → global normalized
    df["x1"] = df["x1_px"] / full_w
    df["y1"] = df["y1_px"] / full_h
    df["x2"] = df["x2_px"] / full_w
    df["y2"] = df["y2_px"] / full_h

    df["tile_id"] = tile_id

    return df[["value", "confidence", "x1", "y1", "x2", "y2", "tile_id"]]


def box_iou(a, b):
    """Calculate Intersection over Union for two bounding boxes."""
    xa1, ya1, xa2, ya2 = a
    xb1, yb1, xb2, yb2 = b

    inter_x1 = max(xa1, xb1)
    inter_y1 = max(ya1, yb1)
    inter_x2 = min(xa2, xb2)
    inter_y2 = min(ya2, yb2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = (xa2 - xa1) * (ya2 - ya1)
    area_b = (xb2 - xb1) * (yb2 - yb1)

    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0


def deduplicate_ocr(df, iou_thresh=0.6):
    """Remove duplicate OCR detections using NMS."""
    df = df.sort_values("confidence", ascending=False).reset_index(drop=True)

    keep = []
    suppressed = set()

    for i in range(len(df)):
        if i in suppressed:
            continue

        keep.append(i)
        box_i = df.loc[i, ["x1", "y1", "x2", "y2"]].values
        text_i = df.loc[i, "value"].strip().lower()

        for j in range(i + 1, len(df)):
            if j in suppressed:
                continue

            text_j = df.loc[j, "value"].strip().lower()
            if text_i != text_j:
                continue

            box_j = df.loc[j, ["x1", "y1", "x2", "y2"]].values
            if box_iou(box_i, box_j) >= iou_thresh:
                suppressed.add(j)

    return df.loc[keep].reset_index(drop=True)


def tile_ocr(drawing, gpu, batch_size=2, progress_callback=None) -> pd.DataFrame:
    """Perform OCR on image using tiled approach.

    Args:
        drawing: Input image
        gpu: Whether to use GPU
        batch_size: Number of tiles to process in parallel
        progress_callback: Optional callback(current, total, message) for progress updates
    """
    full_h, full_w = drawing.shape[:2]
    tiles = crop_tiles(drawing, tile_size=config.TILE_SIZE, overlap=config.TILE_OVERLAP)
    docs = [tile["image"] for tile in tiles]
    total_tiles = len(tiles)

    if progress_callback:
        progress_callback(0, total_tiles, f"Starting OCR on {total_tiles} tiles...")

    ocr = OCR(gpu=gpu)
    results = []

    batch_num = 0
    batches = list(batched(docs, batch_size))
    total_batches = len(batches)

    for batch in batches:
        if len(batch) == 0:
            break

        results.extend(ocr.from_image(list(batch)))
        batch_num += 1

        # Report progress after each batch
        if progress_callback:
            tiles_processed = min(batch_num * batch_size, total_tiles)
            progress_callback(tiles_processed, total_tiles,
                            f"OCR processing: {tiles_processed}/{total_tiles} tiles")

    if progress_callback:
        progress_callback(total_tiles, total_tiles, "OCR complete, assembling results...")

    all_dfs = []
    for i in range(len(tiles)):
        df_tile = results[i]
        tile = tiles[i]

        if df_tile is None or df_tile.empty:
            continue

        df_global = project_tile_df_to_global(
            df_tile,
            tile["x_offset"],
            tile["y_offset"],
            tile["image"].shape[1],
            tile["image"].shape[0],
            full_w=full_w,
            full_h=full_h,
            tile_id=tile["tile_id"]
        )

        all_dfs.append(df_global)

    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final = deduplicate_ocr(df_final, iou_thresh=0.6)
    df_final["word_idx"] = range(len(df_final))

    return df_final


class ProcessingService:
    """Service for processing PDFs and extracting tendon measurements."""

    def __init__(self, storage_service=None):
        """Initialize processing service.

        Args:
            storage_service: Optional storage service for saving results
        """
        self.storage_service = storage_service
        logger.info("ProcessingService initialized")

    def process_pdf(self, pdf_path, job_id=None, gpu=True, progress_callback=None):
        """Process a PDF file and extract tendon measurements.

        Args:
            pdf_path: Path to PDF file
            job_id: Optional job ID for tracking
            gpu: Whether to use GPU for processing
            progress_callback: Optional callback function for progress updates
                              Signature: callback(progress_percent, message)

        Returns:
            dict: Processing results with pages, measurements, and Excel data
        """
        try:
            logger.info(f"Starting PDF processing: {pdf_path}")

            if progress_callback:
                progress_callback(0, "Starting PDF conversion...")

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=config.PDF_DPI)
            total_pages = len(images)
            logger.info(f"Converted PDF to {total_pages} images")

            if progress_callback:
                progress_callback(5, f"Converted to {total_pages} pages, starting OCR...")

            # Process each page
            all_excel_data = []
            results = []

            for page_num, image in enumerate(images):
                logger.info(f"Processing page {page_num + 1}/{total_pages}")

                # Calculate progress range for this page
                # Each page gets an equal portion of 5% to 90% progress
                page_start_progress = 5 + int((page_num / total_pages) * 85)
                page_end_progress = 5 + int(((page_num + 1) / total_pages) * 85)
                page_progress_range = page_end_progress - page_start_progress

                # Convert to numpy array
                drawing = np.asarray(image)

                if progress_callback:
                    progress_callback(page_start_progress,
                                    f"Page {page_num + 1}/{total_pages}: Preparing image...")

                # Perform OCR with progress tracking
                def ocr_progress(current, total, message):
                    """Nested callback for OCR progress"""
                    if progress_callback and total > 0:
                        # OCR takes 70% of page processing time
                        ocr_percent = (current / total) * 0.7
                        progress = page_start_progress + int(ocr_percent * page_progress_range)
                        progress_callback(progress, f"Page {page_num + 1}/{total_pages}: {message}")

                df_ocr = tile_ocr(drawing, gpu=gpu, batch_size=config.OCR_BATCH_SIZE,
                                progress_callback=ocr_progress)

                if progress_callback:
                    progress = page_start_progress + int(0.75 * page_progress_range)
                    progress_callback(progress,
                                    f"Page {page_num + 1}/{total_pages}: Detecting tendons...")

                # Extract tendons and measurements
                vis_image, excel_data = extract_tendons(df_ocr, drawing)

                if progress_callback:
                    progress = page_start_progress + int(0.85 * page_progress_range)
                    progress_callback(progress,
                                    f"Page {page_num + 1}/{total_pages}: Calculating measurements...")

                # Add page number to Excel data
                excel_data["page"] = page_num + 1
                all_excel_data.append(excel_data)

                # Save result image if storage service is available
                filename = f"page_{page_num}.png"
                image_url = None

                if self.storage_service and job_id:
                    if progress_callback:
                        progress = page_start_progress + int(0.95 * page_progress_range)
                        progress_callback(progress,
                                        f"Page {page_num + 1}/{total_pages}: Saving results...")

                    image_url = self.storage_service.save_result_image(
                        job_id, page_num, vis_image
                    )

                results.append({
                    'page': page_num + 1,
                    'filename': filename,
                    'image_url': image_url,
                    'measurements': excel_data.to_dict('records')
                })

                # Update progress - page complete
                if progress_callback:
                    progress_callback(page_end_progress,
                                    f"Completed page {page_num + 1}/{total_pages}")

            # Consolidate Excel data
            if progress_callback:
                progress_callback(92, "Generating Excel file...")

            consolidated_excel = pd.concat(all_excel_data, ignore_index=True)

            # Save Excel file if storage service is available
            excel_path = None
            if self.storage_service and job_id:
                if progress_callback:
                    progress_callback(95, "Saving Excel file...")

                excel_path = self.storage_service.save_excel(job_id, consolidated_excel)

            if progress_callback:
                progress_callback(100, f"Complete! Detected {len(consolidated_excel)} tendons")

            logger.info(f"Processing complete: {len(consolidated_excel)} tendons detected")

            return {
                'success': True,
                'total_pages': total_pages,
                'total_tendons': len(consolidated_excel),
                'pages': results,
                'excel_data': consolidated_excel.to_dict('records'),
                'excel_path': excel_path
            }

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

