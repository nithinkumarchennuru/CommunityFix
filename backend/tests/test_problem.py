import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models import Category, Problem, StatusHistory, User


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "communityfix-test-jwt-secret-key-1234567890",
    })

    with app.app_context():
        db.create_all()
        category_1 = Category(name="Plumbing", description="Plumbing issues", is_active=True)
        category_2 = Category(name="Electrical", description="Electrical issues", is_active=True)
        category_3 = Category(name="Inactive Category", description="Not active", is_active=False)
        resident_1 = User(name="Resident One", email="resident1@example.com", phone="1111111111", password_hash="hash1", role="resident")
        resident_2 = User(name="Resident Two", email="resident2@example.com", phone="2222222222", password_hash="hash2", role="resident")
        admin = User(name="Admin User", email="admin@example.com", phone="3333333333", password_hash="hash3", role="admin")
        db.session.add_all([category_1, category_2, category_3, resident_1, resident_2, admin])
        db.session.commit()

        yield app.test_client(), resident_1, resident_2, admin, category_1, category_2

    with app.app_context():
        db.session.remove()


def test_create_problem_success(client):
    client_obj, resident, _, _, category, _ = client
    token = create_access_token(identity=str(resident.id), additional_claims={"role": resident.role})

    response = client_obj.post(
        "/api/problems",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category_id": category.id,
            "title": "Water leakage",
            "description": "Kitchen pipe leaking",
            "priority": "HIGH",
            "location_text": "Block A, Flat 203",
            "latitude": 11.0168,
            "longitude": 76.9558,
        },
    )

    data = response.get_json()
    assert response.status_code == 201
    assert data["success"] is True
    assert data["message"] == "Problem reported successfully"
    assert data["problem"]["status"] == "NEW"
    assert data["problem"]["problem_id"].startswith("CMP-")
    assert data["problem"]["category_id"] == category.id

    problem = Problem.query.filter_by(problem_id=data["problem"]["problem_id"]).first()
    assert problem is not None
    assert problem.status_history
    assert problem.status_history[0].new_status == "NEW"


def test_create_problem_requires_auth(client):
    client_obj, _, _, _, category, _ = client
    response = client_obj.post(
        "/api/problems",
        json={
            "category_id": category.id,
            "title": "Missing auth",
            "description": "No auth token",
            "priority": "MEDIUM",
            "location_text": "Test",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_create_problem_invalid_category(client):
    client_obj, resident, _, _, _, _ = client
    token = create_access_token(identity=str(resident.id), additional_claims={"role": resident.role})

    response = client_obj.post(
        "/api/problems",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category_id": 999,
            "title": "Bad category",
            "description": "Should fail",
            "priority": "HIGH",
            "location_text": "Here",
        },
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Category not found"


def test_get_my_problems_only_for_resident(client):
    client_obj, resident_1, resident_2, _, category, _ = client
    token_1 = create_access_token(identity=str(resident_1.id), additional_claims={"role": resident_1.role})
    token_2 = create_access_token(identity=str(resident_2.id), additional_claims={"role": resident_2.role})

    client_obj.post(
        "/api/problems",
        headers={"Authorization": f"Bearer {token_1}"},
        json={
            "category_id": category.id,
            "title": "Resident 1 issue",
            "description": "Visible to resident 1",
            "priority": "HIGH",
            "location_text": "R1 Place",
        },
    )
    client_obj.post(
        "/api/problems",
        headers={"Authorization": f"Bearer {token_2}"},
        json={
            "category_id": category.id,
            "title": "Resident 2 issue",
            "description": "Visible to resident 2",
            "priority": "LOW",
            "location_text": "R2 Place",
        },
    )

    response = client_obj.get(
        "/api/problems",
        headers={"Authorization": f"Bearer {token_1}"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert len(data["problems"]) == 1
    assert data["problems"][0]["title"] == "Resident 1 issue"


def test_get_single_problem_rejects_other_resident(client):
    client_obj, resident_1, resident_2, _, category, _ = client
    token_1 = create_access_token(identity=str(resident_1.id), additional_claims={"role": resident_1.role})
    token_2 = create_access_token(identity=str(resident_2.id), additional_claims={"role": resident_2.role})

    create_response = client_obj.post(
        "/api/problems",
        headers={"Authorization": f"Bearer {token_2}"},
        json={
            "category_id": category.id,
            "title": "Other resident issue",
            "description": "No access",
            "priority": "MEDIUM",
            "location_text": "Other place",
        },
    )
    problem_id = create_response.get_json()["problem"]["problem_id"]

    response = client_obj.get(
        f"/api/problems/{problem_id}",
        headers={"Authorization": f"Bearer {token_1}"},
    )

    assert response.status_code == 403
    assert response.get_json()["success"] is False


def test_update_problem_success(client):
    client_obj, resident, _, _, category, _ = client
    token = create_access_token(identity=str(resident.id), additional_claims={"role": resident.role})

    create_response = client_obj.post(
        "/api/problems",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category_id": category.id,
            "title": "Original title",
            "description": "Original description",
            "priority": "MEDIUM",
            "location_text": "Old place",
        },
    )
    problem_id = create_response.get_json()["problem"]["problem_id"]

    response = client_obj.put(
        f"/api/problems/{problem_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "HIGH",
            "location_text": "Updated place",
        },
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["problem"]["title"] == "Updated title"
    assert data["problem"]["priority"] == "HIGH"


def test_cancel_problem_creates_history(client):
    client_obj, resident, _, _, category, _ = client
    token = create_access_token(identity=str(resident.id), additional_claims={"role": resident.role})

    create_response = client_obj.post(
        "/api/problems",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category_id": category.id,
            "title": "Cancel me",
            "description": "Will cancel",
            "priority": "LOW",
            "location_text": "Cancel place",
        },
    )
    problem_id = create_response.get_json()["problem"]["problem_id"]

    response = client_obj.patch(
        f"/api/problems/{problem_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["problem"]["status"] == "CANCELLED"

    history = StatusHistory.query.filter_by(problem_id=Problem.query.filter_by(problem_id=problem_id).first().id).all()
    assert any(entry.new_status == "CANCELLED" for entry in history)


def test_categories_endpoint_returns_active_categories(client):
    client_obj, resident, _, _, _, _ = client
    token = create_access_token(identity=str(resident.id), additional_claims={"role": resident.role})

    response = client_obj.get(
        "/api/categories",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert any(category["name"] == "Plumbing" for category in data["categories"])
    assert all(category["name"] != "Inactive Category" for category in data["categories"])
