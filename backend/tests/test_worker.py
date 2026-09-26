import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models import Category, User, Worker, WorkerSkill


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "communityfix-test-jwt-secret-key-1234567890",
    })

    with app.app_context():
        db.create_all()
        plumbing = Category(name="Plumbing", description="Pipe and drainage issues", is_active=True)
        electrical = Category(name="Electrical", description="Electrical faults", is_active=True)
        cleaning = Category(name="Cleaning", description="Cleaning and sanitation", is_active=True)
        inactive = Category(name="Inactive Skill", description="Should not be used", is_active=False)
        admin = User(name="Admin User", email="admin@example.com", phone="1111111111", password_hash="hash", role="admin")
        resident = User(name="Resident User", email="resident@example.com", phone="2222222222", password_hash="hash", role="resident")
        worker_user = User(name="Worker One", email="worker@example.com", phone="3333333333", password_hash="hash", role="worker")
        other_worker_user = User(name="Worker Two", email="worker2@example.com", phone="4444444444", password_hash="hash", role="worker")
        db.session.add_all([plumbing, electrical, cleaning, inactive, admin, resident, worker_user, other_worker_user])
        db.session.flush()
        worker = Worker(user_id=worker_user.id, worker_id="WRK-1001", availability_status="AVAILABLE", maximum_capacity=5, current_active_jobs=2)
        other_worker = Worker(user_id=other_worker_user.id, worker_id="WRK-1002", availability_status="OFFLINE", maximum_capacity=3, current_active_jobs=0)
        db.session.add_all([worker, other_worker])
        db.session.flush()
        db.session.add_all([
            WorkerSkill(worker_id=worker.id, category_id=plumbing.id),
            WorkerSkill(worker_id=worker.id, category_id=electrical.id),
            WorkerSkill(worker_id=other_worker.id, category_id=plumbing.id),
        ])
        db.session.commit()

        yield {
            "client": app.test_client(),
            "admin": admin,
            "resident": resident,
            "worker_user": worker_user,
            "worker": worker,
            "other_worker_user": other_worker_user,
            "other_worker": other_worker,
            "plumbing": plumbing,
            "electrical": electrical,
            "cleaning": cleaning,
            "inactive": inactive,
        }

    with app.app_context():
        db.session.remove()


def test_admin_can_create_worker(client):
    token = create_access_token(identity=str(client["admin"].id), additional_claims={"role": client["admin"].role})

    response = client["client"].post(
        "/api/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Worker",
            "email": "newworker@example.com",
            "phone": "5555555555",
            "password": "StrongPassword123",
            "maximum_capacity": 5,
        },
    )

    data = response.get_json()
    assert response.status_code == 201
    assert data["success"] is True
    assert data["worker"]["role"] == "worker"
    assert data["worker"]["availability_status"] == "OFFLINE"
    assert data["worker"]["current_active_jobs"] == 0
    assert data["worker"]["worker_id"].startswith("WRK-")


def test_resident_cannot_create_worker(client):
    token = create_access_token(identity=str(client["resident"].id), additional_claims={"role": client["resident"].role})

    response = client["client"].post(
        "/api/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Blocked Worker",
            "email": "blocked@example.com",
            "phone": "6666666666",
            "password": "StrongPassword123",
            "maximum_capacity": 4,
        },
    )

    assert response.status_code == 403
    assert response.get_json()["success"] is False


def test_worker_cannot_create_another_worker(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].post(
        "/api/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Another Worker",
            "email": "another@example.com",
            "phone": "7777777777",
            "password": "StrongPassword123",
            "maximum_capacity": 4,
        },
    )

    assert response.status_code == 403


def test_duplicate_email_rejected(client):
    token = create_access_token(identity=str(client["admin"].id), additional_claims={"role": client["admin"].role})

    response = client["client"].post(
        "/api/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Duplicate User",
            "email": "worker@example.com",
            "phone": "8888888888",
            "password": "StrongPassword123",
            "maximum_capacity": 4,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_worker_can_view_own_profile(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].get(
        "/api/workers/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["worker"]["worker_id"] == "WRK-1001"
    assert data["worker"]["availability_status"] == "AVAILABLE"


def test_resident_cannot_access_worker_profile(client):
    token = create_access_token(identity=str(client["resident"].id), additional_claims={"role": client["resident"].role})

    response = client["client"].get(
        "/api/workers/WRK-1001",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json()["success"] is False


def test_worker_can_add_skill(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].post(
        "/api/workers/me/skills",
        headers={"Authorization": f"Bearer {token}"},
        json={"category_id": client["cleaning"].id},
    )

    assert response.status_code == 201
    assert response.get_json()["success"] is True


def test_duplicate_skill_is_rejected(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].post(
        "/api/workers/me/skills",
        headers={"Authorization": f"Bearer {token}"},
        json={"category_id": client["plumbing"].id},
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_inactive_category_is_rejected(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].post(
        "/api/workers/me/skills",
        headers={"Authorization": f"Bearer {token}"},
        json={"category_id": client["inactive"].id},
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_worker_can_remove_own_skill(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})
    skill = WorkerSkill.query.filter_by(worker_id=client["worker"].id, category_id=client["plumbing"].id).first()
    response = client["client"].delete(
        f"/api/workers/me/skills/{skill.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Skill removed successfully"


def test_worker_can_update_availability(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].put(
        "/api/workers/me/availability",
        headers={"Authorization": f"Bearer {token}"},
        json={"availability_status": "BUSY"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["availability_status"] == "BUSY"


def test_invalid_availability_is_rejected(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].put(
        "/api/workers/me/availability",
        headers={"Authorization": f"Bearer {token}"},
        json={"availability_status": "UNKNOWN"},
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_workload_is_calculated(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})

    response = client["client"].get(
        "/api/workers/me/workload",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["workload"]["current_active_jobs"] == 2
    assert data["workload"]["maximum_capacity"] == 5
    assert data["workload"]["workload_percentage"] == 40.0
    assert data["workload"]["capacity_available"] == 3


def test_admin_can_update_capacity(client):
    token = create_access_token(identity=str(client["admin"].id), additional_claims={"role": client["admin"].role})

    response = client["client"].put(
        f"/api/workers/{client['worker'].worker_id}/capacity",
        headers={"Authorization": f"Bearer {token}"},
        json={"maximum_capacity": 6},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["worker"]["maximum_capacity"] == 6


def test_capacity_cannot_drop_below_current_jobs(client):
    token = create_access_token(identity=str(client["admin"].id), additional_claims={"role": client["admin"].role})

    response = client["client"].put(
        f"/api/workers/{client['worker'].worker_id}/capacity",
        headers={"Authorization": f"Bearer {token}"},
        json={"maximum_capacity": 1},
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_admin_can_list_workers_with_pagination(client):
    token = create_access_token(identity=str(client["admin"].id), additional_claims={"role": client["admin"].role})

    response = client["client"].get(
        "/api/workers?page=1&per_page=10",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "workers" in data
    assert data["pagination"]["page"] == 1
    assert len(data["workers"]) >= 2


def test_worker_cannot_remove_another_workers_skill(client):
    token = create_access_token(identity=str(client["worker_user"].id), additional_claims={"role": client["worker_user"].role})
    worker = Worker.query.filter_by(user_id=client["other_worker_user"].id).first()
    skill = WorkerSkill.query.filter_by(worker_id=worker.id).first()

    response = client["client"].delete(
        f"/api/workers/me/skills/{skill.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.get_json()["success"] is False
