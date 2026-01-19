"""
Main Flask application for Tendon Analysis Platform.
Production-ready version with modular architecture.
"""

import os
import logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['OUTPUT_FOLDER'] = config.OUTPUT_FOLDER
    
    # Enable CORS
    CORS(app)
    
    # Create necessary directories
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)
    
    # Register API blueprints
    from api import api_bp
    app.register_blueprint(api_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'gpu_enabled': config.USE_GPU
        }), 200
    
    # Serve static files (frontend)
    @app.route('/')
    def index():
        """Serve main HTML page."""
        return send_from_directory('.', 'index.html')
    
    @app.route('/outputs/<path:filename>')
    def serve_output(filename):
        """Serve output files."""
        return send_from_directory(config.OUTPUT_FOLDER, filename)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'error': f'File too large. Maximum size: {config.MAX_FILE_SIZE / (1024*1024):.0f}MB'
        }), 413
    
    logger.info("Flask application created successfully")
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Starting Tendon Analysis Platform")
    logger.info("=" * 60)
    logger.info(f"Server: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    logger.info(f"GPU Enabled: {config.USE_GPU}")
    logger.info(f"Debug Mode: {config.DEBUG_MODE}")
    logger.info("=" * 60)
    
    app.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=config.DEBUG_MODE
    )

