import io

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models import Category, Problem, ProblemImage, User, Worker
from app.services.storage_service import validate_image


@pytest.fixture
def image_app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "communityfix-test-jwt-secret-key-1234567890",
    })
    with app.app_context():
        db.create_all()
        admin = User(name="Admin User", email="admin@example.com", phone="1111111111", password_hash="hash", role="admin")
        resident = User(name="Resident User", email="resident@example.com", phone="2222222222", password_hash="hash", role="resident")
        worker_user = User(name="Worker User", email="worker@example.com", phone="3333333333", password_hash="hash", role="worker")
        category = Category(name="Plumbing", description="Plumbing", is_active=True)
        db.session.add_all([admin, resident, worker_user, category])
        db.session.flush()
        worker = Worker(user_id=worker_user.id, worker_id="WRK-1001", availability_status="AVAILABLE", maximum_capacity=2, current_active_jobs=1)
        problem = Problem(problem_id="CMP-1001", resident_id=resident.id, category_id=category.id, title="Leak", description="Pipe leak", priority="HIGH", status="RESOLVED")
        db.session.add_all([worker, problem])
        db.session.commit()
        yield app, resident, worker_user, admin, problem, worker
        db.session.remove()


def test_validate_image_accepts_supported_type():
    file = io.BytesIO(b"abc")
    file.filename = "photo.jpg"
    file.content_type = "image/jpeg"
    validated = validate_image(file, max_size_mb=5)
    assert validated is True


def test_validate_image_rejects_invalid_type():
    file = io.BytesIO(b"abc")
    file.filename = "photo.txt"
    file.content_type = "text/plain"
    with pytest.raises(ValueError):
        validate_image(file, max_size_mb=5)


def test_resident_can_upload_problem_image(image_app):
    app, resident, worker_user, admin, problem, worker = image_app
    client = app.test_client()
    with app.app_context():
        token = create_access_token(identity=str(resident.id), additional_claims={"role": resident.role})

    data = {
        "file": (io.BytesIO(b"fake-jpeg-data"), "problem.jpg")
    }

    from app.services import storage_service
    storage_service.upload_image = lambda file, folder, public_id=None: {"url": "https://example.com/problem.jpg", "storage_id": "communityfix/problems/problem-1"}

    response = client.post(
        f"/api/problems/{problem.problem_id}/images",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert ProblemImage.query.filter_by(problem_id=problem.id, image_type="PROBLEM").count() == 1


def test_completion_blocked_without_after_work_image_when_required(image_app):
    app, resident, worker_user, admin, problem, worker = image_app
    client = app.test_client()
    app.config["REQUIRE_AFTER_IMAGE_FOR_COMPLETION"] = True
    with app.app_context():
        token = create_access_token(identity=str(worker_user.id), additional_claims={"role": worker_user.role})

    from app.models import Assignment
    assignment = Assignment(problem_id=problem.id, worker_id=worker.id, status="IN_PROGRESS")
    db.session.add(assignment)
    db.session.commit()

    response = client.post(
        f"/api/assignments/{assignment.id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False
