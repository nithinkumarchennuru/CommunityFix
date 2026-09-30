from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models import Assignment, Category, Problem, User, Worker, WorkerSkill


def _build_app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "communityfix-test-jwt-secret-key-1234567890",
    })
    with app.app_context():
        db.create_all()
        admin = User(name="Admin", email="admin@example.com", phone="1111111111", password_hash="hash", role="admin")
        resident = User(name="Resident", email="resident@example.com", phone="2222222222", password_hash="hash", role="resident")
        worker_user = User(name="Worker", email="worker@example.com", phone="3333333333", password_hash="hash", role="worker")
        category = Category(name="Plumbing", description="Plumbing", is_active=True)
        db.session.add_all([admin, resident, worker_user, category])
        db.session.flush()

        worker = Worker(user_id=worker_user.id, worker_id="WRK-1001", availability_status="AVAILABLE", maximum_capacity=2, current_active_jobs=1)
        db.session.add(worker)
        db.session.flush()
        db.session.add(WorkerSkill(worker_id=worker.id, category_id=category.id))

        problem_1 = Problem(problem_id="CMP-1001", resident_id=resident.id, category_id=category.id, title="Leak", description="Kitchen leak", priority="HIGH", status="PENDING_ASSIGNMENT")
        problem_2 = Problem(problem_id="CMP-1002", resident_id=resident.id, category_id=category.id, title="Pipe issue", description="Bathroom pipe", priority="MEDIUM", status="RESOLVED")
        db.session.add_all([problem_1, problem_2])
        db.session.flush()

        db.session.add(Assignment(problem_id=problem_1.id, worker_id=worker.id, status="ASSIGNED"))
        db.session.add(Assignment(problem_id=problem_2.id, worker_id=worker.id, status="COMPLETED"))
        db.session.commit()
        return app, admin


def test_admin_dashboard_summary_returns_counts():
    app, admin = _build_app()
    client = app.test_client()

    with app.app_context():
        token = create_access_token(identity=str(admin.id), additional_claims={"role": admin.role})

    response = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["dashboard"]["problems"]["total"] >= 2
    assert data["dashboard"]["workers"]["total"] >= 1
    assert data["dashboard"]["assignments"]["total"] >= 2
    assert "pending_assignment" in data["dashboard"]["problems"]
