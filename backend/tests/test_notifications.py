import pytest

from app import create_app
from app.extensions import db
from app.models import Assignment, Category, Notification, Problem, User, Worker, WorkerSkill


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


def _seed_problem_and_assignment():
    resident = User(name="Resident", email="resident@example.com", phone="1111111111", password_hash="hash", role="resident")
    worker_user = User(name="Worker One", email="worker@example.com", phone="2222222222", password_hash="hash", role="worker")
    category = Category(name="Plumbing", description="Plumbing", is_active=True)
    db.session.add_all([resident, worker_user, category])
    db.session.flush()

    worker = Worker(user_id=worker_user.id, worker_id="WRK-1001", availability_status="AVAILABLE", maximum_capacity=3, current_active_jobs=0)
    db.session.add(worker)
    db.session.flush()
    db.session.add(WorkerSkill(worker_id=worker.id, category_id=category.id))

    problem = Problem(
        problem_id="CMP-1001",
        resident_id=resident.id,
        category_id=category.id,
        title="Pipe leak",
        description="Leak near kitchen pipe",
        priority="HIGH",
        status="ASSIGNED",
    )
    db.session.add(problem)
    db.session.flush()

    assignment = Assignment(problem_id=problem.id, worker_id=worker.id, status="ASSIGNED")
    db.session.add(assignment)
    db.session.commit()
    return resident, worker_user, worker, problem, assignment


def test_problem_assignment_creates_worker_and_resident_notifications(app_ctx):
    resident, worker_user, worker, problem, assignment = _seed_problem_and_assignment()

    from app.services.notification_service import notify_resident, notify_worker

    notify_worker(worker, "PROBLEM_ASSIGNED", "New problem assigned", f"You have been assigned a new problem {problem.problem_id}.")
    notify_resident(problem, "PROBLEM_ASSIGNED", "Problem assigned", f"Your reported problem {problem.problem_id} has been assigned to a worker.")
    db.session.commit()

    assert Notification.query.filter_by(user_id=worker_user.id, type="PROBLEM_ASSIGNED").count() >= 1
    assert Notification.query.filter_by(user_id=resident.id, type="PROBLEM_ASSIGNED").count() >= 1


def test_accept_assignment_creates_resident_notification(app_ctx):
    resident, worker_user, worker, problem, assignment = _seed_problem_and_assignment()

    from app.services.assignment_service import accept_assignment

    result = accept_assignment(assignment.id, worker_user.id)
    db.session.commit()

    assert result["assignment"]["status"] == "ACCEPTED"
    assert Notification.query.filter_by(user_id=resident.id, type="ASSIGNMENT_ACCEPTED").count() >= 1


def test_notifications_api_and_read_flow(app_ctx):
    resident = User(name="Resident", email="resident@example.com", phone="1111111111", password_hash="hash", role="resident")
    db.session.add(resident)
    db.session.flush()

    from app.services.notification_service import create_notification

    notification = create_notification(
        user_id=resident.id,
        notification_type="PROBLEM_CREATED",
        title="Problem reported",
        message="Your problem has been reported successfully.",
    )
    db.session.commit()

    from flask_jwt_extended import create_access_token

    token = create_access_token(identity=str(resident.id), additional_claims={"role": resident.role})
    client = app_ctx.test_client()

    response = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert len(data["notifications"]) >= 1

    notification_id = data["notifications"][0]["id"]
    response = client.patch(f"/api/notifications/{notification_id}/read", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["notification"]["is_read"] is True

    response = client.get("/api/notifications/unread-count", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["unread_count"] >= 0
