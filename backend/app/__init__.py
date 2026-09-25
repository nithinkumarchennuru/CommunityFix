import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from .config import config_by_name
from .database import db
from .routes.health import health_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory pattern for CommunityFix Flask backend.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    selected_config = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(selected_config)

    # Configure CORS for frontend communication
    allowed_origins = app.config.get("CORS_ORIGINS", ["http://localhost:5173", "http://127.0.0.1:5173"])
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True
    )
    logger.info(f"CORS enabled for origins: {allowed_origins}")

    # Initialize SQLAlchemy (lazy connection engine)
    db.init_app(app)

    # Register API Blueprints
    app.register_blueprint(health_bp, url_prefix="/api")

    # Root route for quick confirmation
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "project": "CommunityFix",
            "phase": "Phase 1 - Project Setup",
            "status": "Flask backend running",
            "documentation": {
                "health_endpoint": "/api/health",
                "ping_endpoint": "/api/ping",
                "db_test_endpoint": "/api/db/test"
            }
        })

    # Generic 404 handler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "The requested resource was not found on this server."}), 404

    # Generic 500 handler
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal Server Error", "message": "An unexpected server error occurred."}), 500

    return app
