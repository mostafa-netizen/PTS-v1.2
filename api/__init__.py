"""
API module for tendon analysis platform.
Contains Flask blueprints for all API endpoints.
"""

from flask import Blueprint

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import and register sub-blueprints
from .upload import upload_bp
from .processing import processing_bp
from .results import results_bp

api_bp.register_blueprint(upload_bp)
api_bp.register_blueprint(processing_bp)
api_bp.register_blueprint(results_bp)

__all__ = ['api_bp']

