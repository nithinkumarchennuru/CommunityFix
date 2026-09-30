import pytest

from app import create_app
from app.extensions import db
from app.models import Assignment, Category, Problem, StatusHistory, User, Worker, WorkerSkill


@pytest.fixture
def app_ctx():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "communityfix-test-jwt-secret-key-1234567890",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()


def _seed_assignment_context():
    resident = User(name="Resident", email="resident@example.com", phone="1111111111", password_hash="hash", role="resident")
    worker_user = User(name="Worker One", email="worker@example.com", phone="2222222222", password_hash="hash", role="worker")
    backup_worker_user = User(name="Worker Two", email="worker2@example.com", phone="3333333333", password_hash="hash", role="worker")
    category = Category(name="Plumbing", description="Plumbing", is_active=True)
    db.session.add_all([resident, worker_user, backup_worker_user, category])
    db.session.flush()

    worker = Worker(user_id=worker_user.id, worker_id="WRK-1001", availability_status="AVAILABLE", maximum_capacity=3, current_active_jobs=1)
    backup_worker = Worker(user_id=backup_worker_user.id, worker_id="WRK-1002", availability_status="AVAILABLE", maximum_capacity=3, current_active_jobs=0)
    db.session.add_all([worker, backup_worker])
    db.session.flush()

    db.session.add_all([
        WorkerSkill(worker_id=worker.id, category_id=category.id),
        WorkerSkill(worker_id=backup_worker.id, category_id=category.id),
    ])

    problem = Problem(
        problem_id="CMP-LIFECYCLE-1",
        resident_id=resident.id,
        category_id=category.id,
        title="Pipe leak",
        description="Leak near kitchen pipe",
        priority="HIGH",
        status="ASSIGNED",
    )
    db.session.add(problem)
    db.session.flush()

    assignment = Assignment(problem_id=problem.id, worker_id=worker.id, status="ASSIGNED", assigned_at=db.func.now() if hasattr(db, 'func') else None)
    db.session.add(assignment)
    db.session.commit()

    return resident, worker_user, worker, backup_worker, problem, assignment


def test_worker_can_view_current_assignments(app_ctx):
    _, worker_user, worker, _, problem, assignment = _seed_assignment_context()
    from flask_jwt_extended import create_access_token

    token = create_access_token(identity=str(worker_user.id), additional_claims={"role": worker_user.role})
    client = app_ctx.test_client()

    response = client.get("/api/assignments/me", headers={"Authorization": f"Bearer {token}"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert len(data["assignments"]) >= 1
    assert data["assignments"][0]["problem_id"] == problem.problem_id


def test_worker_can_accept_assignment(app_ctx):
    _, worker_user, worker, _, problem, assignment = _seed_assignment_context()
    from flask_jwt_extended import create_access_token

    token = create_access_token(identity=str(worker_user.id), additional_claims={"role": worker_user.role})
    client = app_ctx.test_client()

    response = client.post(f"/api/assignments/{assignment.id}/accept", headers={"Authorization": f"Bearer {token}"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["assignment"]["status"] == "ACCEPTED"
    assert Problem.query.get(problem.id).status == "ACCEPTED"


def test_worker_reject_triggers_reassignment(app_ctx):
    _, worker_user, worker, backup_worker, problem, assignment = _seed_assignment_context()
    from flask_jwt_extended import create_access_token

    token = create_access_token(identity=str(worker_user.id), additional_claims={"role": worker_user.role})
    client = app_ctx.test_client()

    response = client.post(
        f"/api/assignments/{assignment.id}/reject",
        json={"rejection_reason": "Too far away"},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["assignment"]["status"] in {"REJECTED", "ASSIGNED"}
    assert Problem.query.get(problem.id).status in {"PENDING_ASSIGNMENT", "ASSIGNED"}


def test_worker_can_complete_assignment(app_ctx):
    _, worker_user, worker, _, problem, assignment = _seed_assignment_context()
    from flask_jwt_extended import create_access_token

    assignment.status = "IN_PROGRESS"
    db.session.commit()

    token = create_access_token(identity=str(worker_user.id), additional_claims={"role": worker_user.role})
    client = app_ctx.test_client()

    response = client.post(f"/api/assignments/{assignment.id}/complete", headers={"Authorization": f"Bearer {token}"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["assignment"]["status"] == "COMPLETED"
    assert Problem.query.get(problem.id).status == "RESOLVED"
