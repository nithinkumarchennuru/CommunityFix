from flask import current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User


def serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
    }


def register_user(data):
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    if not name or not email or not phone or not password:
        raise ValueError("Missing required fields")

    if "@" not in email or "." not in email:
        raise ValueError("Invalid email format")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("User already exists")

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        role="resident",
    )

    return user


def authenticate_user(email, password):
    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user or not check_password_hash(user.password_hash, password):
        return None
    return user


def create_auth_token(user):
    expires_delta = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
    return create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
        expires_delta=expires_delta,
    )
