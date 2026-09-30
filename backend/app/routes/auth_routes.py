from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import User
from app.services.auth_service import (
    authenticate_user,
    create_auth_token,
    register_user,
    serialize_user,
)
from app.utils.decorators import roles_required
from app.utils.validators import is_valid_email

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({"success": False, "message": "Request body is required"}), 400

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    if not name or not email or not phone or not password:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email format"}), 400

    if len(password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters long"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered"}), 409

    if "role" in data and data.get("role") == "admin":
        return jsonify({"success": False, "message": "Admin role registration is not allowed"}), 403

    try:
        user = register_user({
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
        })
        db.session.add(user)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Registration failed"}), 500

    return jsonify({
        "success": True,
        "message": "User registered successfully",
        "user": serialize_user(user),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    user = authenticate_user(email, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    token = create_auth_token(user)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": serialize_user(user),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def current_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": serialize_user(user),
    }), 200


@auth_bp.route("/admin-check", methods=["GET"])
@jwt_required()
@roles_required("admin")
def admin_check():
    return jsonify({"success": True, "message": "Admin access granted"}), 200
