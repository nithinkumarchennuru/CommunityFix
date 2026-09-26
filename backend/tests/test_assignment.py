import pytest

from app import create_app
from app.extensions import db
from app.models import Assignment, Category, Problem, StatusHistory, User, Worker, WorkerSkill
from app.services.assignment_service import assign_problem, find_eligible_workers, rank_workers


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


def _build_problem_and_workers():
    resident = User(name="Resident", email="resident@example.com", phone="1111111111", password_hash="hash", role="resident")
    admin = User(name="Admin", email="admin@example.com", phone="2222222222", password_hash="hash", role="admin")
    worker_user_2 = User(name="Worker Two", email="worker2@example.com", phone="3333333333", password_hash="hash", role="worker")
    worker_user_3 = User(name="Worker Three", email="worker3@example.com", phone="4444444444", password_hash="hash", role="worker")
    category = Category(name="Plumbing", description="Plumbing issues", is_active=True)
    db.session.add_all([resident, admin, worker_user_2, worker_user_3, category])
    db.session.flush()

    worker_1 = Worker(user_id=admin.id, worker_id="WRK-1001", availability_status="AVAILABLE", maximum_capacity=5, current_active_jobs=1)
    worker_2 = Worker(user_id=worker_user_2.id, worker_id="WRK-1002", availability_status="AVAILABLE", maximum_capacity=4, current_active_jobs=3)
    worker_3 = Worker(user_id=worker_user_3.id, worker_id="WRK-1003", availability_status="BUSY", maximum_capacity=6, current_active_jobs=1)
    db.session.add_all([worker_1, worker_2, worker_3])
    db.session.flush()

    db.session.add_all([
        WorkerSkill(worker_id=worker_1.id, category_id=category.id),
        WorkerSkill(worker_id=worker_2.id, category_id=category.id),
        WorkerSkill(worker_id=worker_3.id, category_id=category.id),
    ])

    problem = Problem(
        problem_id="CMP-ASSIGN-1",
        resident_id=resident.id,
        category_id=category.id,
        title="Leaking pipe",
        description="Kitchen pipe leaking",
        priority="HIGH",
        status="NEW",
        location_text="Main Road",
        latitude=12.3456,
        longitude=98.7654,
    )
    db.session.add(problem)
    db.session.commit()

    return resident, admin, category, worker_1, worker_2, worker_3, problem


def test_find_eligible_workers_filters_skill_and_capacity(app_ctx):
    _, _, category, worker_1, worker_2, worker_3, problem = _build_problem_and_workers()
    eligible = find_eligible_workers(problem)
    assert {worker.id for worker in eligible} == {worker_1.id, worker_2.id}
    assert worker_3.id not in {worker.id for worker in eligible}


def test_rank_workers_is_deterministic_and_workload_aware(app_ctx):
    _, _, category, worker_1, worker_2, worker_3, problem = _build_problem_and_workers()
    ranked = rank_workers(problem, find_eligible_workers(problem))
    assert ranked[0]["worker"].id == worker_1.id
    assert ranked[0]["score"] <= ranked[1]["score"]
    assert ranked[0]["worker"].worker_id == "WRK-1001"


def test_assign_problem_creates_assignment_and_status_history(app_ctx):
    _, _, category, worker_1, worker_2, worker_3, problem = _build_problem_and_workers()
    result = assign_problem(problem.id)

    assert result["success"] is True
    assert result["problem_status"] == "ASSIGNED"
    assert result["assignment"]["worker_id"] == worker_1.id

    assignment = Assignment.query.filter_by(problem_id=problem.id).first()
    problem = Problem.query.get(problem.id)
    history = StatusHistory.query.filter_by(problem_id=problem.id).order_by(StatusHistory.changed_at.desc()).first()

    assert assignment is not None
    assert problem.status == "ASSIGNED"
    assert history is not None
    assert history.new_status == "ASSIGNED"


def test_no_eligible_workers_sets_pending_assignment(app_ctx):
    resident = User(name="Resident 2", email="resident2@example.com", phone="3333333333", password_hash="hash", role="resident")
    category = Category(name="Electrical", description="Electrical issues", is_active=True)
    db.session.add_all([resident, category])
    db.session.flush()

    worker = Worker(user_id=resident.id, worker_id="WRK-2001", availability_status="OFFLINE", maximum_capacity=4, current_active_jobs=0)
    db.session.add(worker)
    db.session.flush()
    db.session.add(WorkerSkill(worker_id=worker.id, category_id=category.id))

    problem = Problem(
        problem_id="CMP-ASSIGN-2",
        resident_id=resident.id,
        category_id=category.id,
        title="Broken switch",
        description="Room light switch is broken",
        priority="MEDIUM",
        status="NEW",
    )
    db.session.add(problem)
    db.session.commit()

    result = assign_problem(problem.id)

    assert result["success"] is False
    assert result["problem_status"] == "PENDING_ASSIGNMENT"
    assert Problem.query.get(problem.id).status == "PENDING_ASSIGNMENT"
    assert StatusHistory.query.filter_by(problem_id=problem.id, new_status="PENDING_ASSIGNMENT").count() >= 1
