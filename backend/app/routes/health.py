from datetime import datetime, timezone
from flask import Blueprint, jsonify, current_app
from ..database import test_database_connection
from ..config import Config

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Primary health check endpoint.
    Reports API operational status, server timestamp, and database connectivity.
    """
    db_status = test_database_connection(Config)

    response_data = {
        "status": "healthy" if db_status["connected"] else "degraded",
        "service": "CommunityFix Backend API",
        "phase": "Phase 1 - Project Setup",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "status": "connected" if db_status["connected"] else "disconnected",
            "connected": db_status["connected"],
            "host": db_status["host"],
            "port": db_status["port"],
            "user": db_status["user"],
            "database_name": db_status["database"],
            "server_version": db_status.get("server_version"),
            "message": db_status["message"],
            "error": db_status.get("error")
        }
    }

    status_code = 200 if db_status["connected"] else 200  # Return 200 with degraded state so frontend can display details cleanly
    return jsonify(response_data), status_code


@health_bp.route("/ping", methods=["GET"])
def ping():
    """Lightweight ping endpoint for rapid frontend connectivity testing."""
    return jsonify({
        "status": "ok",
        "message": "pong",
        "service": "CommunityFix Backend",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@health_bp.route("/db/test", methods=["GET", "POST"])
def db_diagnostic():
    """Explicit database diagnostic endpoint."""
    diagnostic_result = test_database_connection(Config)
    return jsonify(diagnostic_result), (200 if diagnostic_result["connected"] else 503)
