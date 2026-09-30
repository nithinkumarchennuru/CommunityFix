from flask import Flask, jsonify
from sqlalchemy import text

from .config import Config
from .extensions import cors, db, jwt, migrate
from .routes.admin_routes import admin_bp
from .routes.assignment_routes import assignment_bp
from .routes.auth_routes import auth_bp
from .routes.health_routes import health_bp
from .routes.image_routes import image_bp
from .routes.notification_routes import notification_bp
from .routes.problem_routes import problem_bp
from .routes.worker_routes import worker_bp


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    if app.config.get("TESTING"):
        db.session.remove = lambda: None

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return {"success": False, "message": "Authentication required"}, 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return {"success": False, "message": "Invalid or expired token"}, 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return {"success": False, "message": "Invalid or expired token"}, 401

    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            app.config["DATABASE_READY"] = True
        except Exception as exc:
            app.config["DATABASE_READY"] = False
            app.logger.warning(
                "Database connection check failed; MySQL may not be configured yet. %s",
                exc,
            )

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(problem_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(assignment_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "message": "Resource not found",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "message": "Method not allowed",
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "message": "Internal server error",
        }), 500

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if not app.testing:
            db.session.remove()

    return app
