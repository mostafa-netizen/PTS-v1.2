#!/usr/bin/env python3
"""
RunPod GPU API Server
Simple Flask API for OCR processing on RunPod GPU instances
"""

import os
import sys
import base64
import logging
from io import BytesIO
from flask import Flask, request, jsonify
import numpy as np
import cv2
import torch
from PIL import Image

# Add parent directory to path for imports
sys.path.insert(0, '/workspace')

# Import OCR module (adjust path as needed)
try:
    from ocr.doctr import OCR
except ImportError:
    print("Warning: OCR module not found. Make sure to upload ocr/ directory to RunPod.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global OCR instance (initialized once)
ocr_instance = None


def get_ocr():
    """Get or create OCR instance."""
    global ocr_instance
    if ocr_instance is None:
        logger.info("Initializing OCR model...")
        gpu_available = torch.cuda.is_available()
        logger.info(f"GPU available: {gpu_available}")
        ocr_instance = OCR(gpu=gpu_available)
        logger.info("OCR model initialized")
    return ocr_instance


def decode_image(image_data):
    """Decode base64 image to numpy array."""
    try:
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")
        
        return image
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    gpu_available = torch.cuda.is_available()
    return jsonify({
        'status': 'healthy',
        'gpu_available': gpu_available,
        'gpu_name': torch.cuda.get_device_name(0) if gpu_available else None
    })


@app.route('/ocr', methods=['POST'])
def process_ocr():
    """
    Process OCR on uploaded image.
    
    Expected JSON:
    {
        "image": "base64_encoded_image",
        "tile_info": {
            "tile_id": 0,
            "x_offset": 0,
            "y_offset": 0
        }
    }
    
    Returns:
    {
        "success": true,
        "results": [...],
        "tile_info": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode image
        logger.info("Decoding image...")
        image = decode_image(data['image'])
        logger.info(f"Image shape: {image.shape}")
        
        # Get OCR instance
        ocr = get_ocr()
        
        # Process OCR
        logger.info("Running OCR...")
        results = ocr.from_image([image])
        logger.info(f"OCR complete. Found {len(results[0])} text regions")
        
        # Convert results to serializable format
        ocr_results = []
        for result in results[0]:
            ocr_results.append({
                'text': result.get('text', ''),
                'confidence': float(result.get('confidence', 0.0)),
                'bbox': result.get('bbox', []),
                'geometry': result.get('geometry', {})
            })
        
        response = {
            'success': True,
            'results': ocr_results,
            'tile_info': data.get('tile_info', {}),
            'num_detections': len(ocr_results)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing OCR: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/batch_ocr', methods=['POST'])
def process_batch_ocr():
    """
    Process OCR on multiple images in batch.
    
    Expected JSON:
    {
        "images": ["base64_1", "base64_2", ...],
        "tile_infos": [{...}, {...}, ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'images' not in data:
            return jsonify({'error': 'No images provided'}), 400
        
        images_data = data['images']
        tile_infos = data.get('tile_infos', [{}] * len(images_data))
        
        # Decode all images
        logger.info(f"Decoding {len(images_data)} images...")
        images = []
        for img_data in images_data:
            images.append(decode_image(img_data))
        
        # Get OCR instance
        ocr = get_ocr()
        
        # Process batch
        logger.info(f"Running batch OCR on {len(images)} images...")
        batch_results = ocr.from_image(images)
        logger.info("Batch OCR complete")
        
        # Format results
        all_results = []
        for idx, results in enumerate(batch_results):
            ocr_results = []
            for result in results:
                ocr_results.append({
                    'text': result.get('text', ''),
                    'confidence': float(result.get('confidence', 0.0)),
                    'bbox': result.get('bbox', []),
                    'geometry': result.get('geometry', {})
                })
            
            all_results.append({
                'tile_info': tile_infos[idx] if idx < len(tile_infos) else {},
                'results': ocr_results,
                'num_detections': len(ocr_results)
            })
        
        return jsonify({
            'success': True,
            'batch_results': all_results,
            'total_images': len(images)
        })
        
    except Exception as e:
        logger.error(f"Error processing batch OCR: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("RunPod OCR API Server")
    logger.info("=" * 60)
    
    # Check GPU
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Version: {torch.version.cuda}")
    else:
        logger.warning("No GPU available - using CPU")
    
    logger.info("=" * 60)
    
    # Run server
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

