import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models import User
from app.utils.decorators import roles_required


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "communityfix-test-jwt-secret-key-1234567890",
    })

    with app.app_context():
        db.create_all()

    @app.route("/test-admin-only")
    @roles_required("admin")
    def admin_only():
        return {"success": True, "message": "admin ok"}, 200

    with app.app_context():
        yield app.test_client()

    with app.app_context():
        db.session.remove()


def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "9876543210",
            "password": "StrongPassword123",
        },
    )

    data = response.get_json()
    assert response.status_code == 201
    assert data["success"] is True
    assert data["message"] == "User registered successfully"
    assert data["user"]["email"] == "john@example.com"
    assert data["user"]["role"] == "resident"
    assert "password_hash" not in data["user"]

    user = User.query.filter_by(email="john@example.com").first()
    assert user is not None
    assert user.password_hash != "StrongPassword123"


def test_register_user_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Doe",
            "email": "bad-email",
            "phone": "9876543211",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_register_user_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Short Pass",
            "email": "short@example.com",
            "phone": "9876543212",
            "password": "short",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_register_user_rejects_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "First User",
            "email": "dup@example.com",
            "phone": "9876543213",
            "password": "StrongPassword123",
        },
    )

    response = client.post(
        "/api/auth/register",
        json={
            "name": "Second User",
            "email": "dup@example.com",
            "phone": "9876543214",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 409
    assert response.get_json()["success"] is False


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "phone": "9876543215",
            "password": "StrongPassword123",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "StrongPassword123",
        },
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "login@example.com"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "missing@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["success"] is False
    assert response.get_json()["message"] == "Invalid email or password"


def test_me_requires_valid_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.get_json()["success"] is False

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_me_returns_current_user(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Current User",
            "email": "current@example.com",
            "phone": "9876543216",
            "password": "StrongPassword123",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "current@example.com",
            "password": "StrongPassword123",
        },
    )
    token = login_response.get_json()["token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["user"]["email"] == "current@example.com"
    assert "password_hash" not in data["user"]


def test_roles_required_forbidden(client):
    user = User(
        name="Resident User",
        email="resident@example.com",
        phone="9876543217",
        password_hash="hashed-demo",
        role="resident",
    )
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": "resident"})
    response = client.get(
        "/test-admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json()["success"] is False
    assert response.get_json()["message"] == "You do not have permission to access this resource"
