import pytest
from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.models import (
    Assignment,
    Category,
    Problem,
    StatusHistory,
    User,
    Worker,
    WorkerSkill,
)


@pytest.fixture
def app_ctx():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()


def test_models_import_and_initialize(app_ctx):
    assert User is not None
    assert Worker is not None
    assert WorkerSkill is not None
    assert Category is not None
    assert Problem is not None
    assert Assignment is not None
    assert StatusHistory is not None

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    assert "user" in tables
    assert "worker" in tables
    assert "worker_skill" in tables
    assert "category" in tables
    assert "problem" in tables
    assert "assignment" in tables
    assert "status_history" in tables


def test_user_worker_relationship(app_ctx):
    user = User(name="Alice", email="alice@example.com", phone="1111111111", password_hash="hash", role="resident")
    worker = Worker(user=user, worker_id="WK-1001", availability_status="AVAILABLE", maximum_capacity=2, current_active_jobs=0)
    db.session.add_all([user, worker])
    db.session.commit()

    assert worker.user_id == user.id
    assert user.worker is not None
    assert user.worker.worker_id == "WK-1001"


def test_worker_skills_and_category_relationships(app_ctx):
    user = User(name="Bob", email="bob@example.com", phone="2222222222", password_hash="hash", role="worker")
    worker = Worker(user=user, worker_id="WK-1002", availability_status="BUSY", maximum_capacity=3, current_active_jobs=1)
    category_1 = Category(name="Plumbing", description="Fix plumbing issues")
    category_2 = Category(name="Electrical", description="Fix electrical issues")
    db.session.add_all([user, worker, category_1, category_2])
    db.session.flush()

    skill_1 = WorkerSkill(worker_id=worker.id, category_id=category_1.id)
    skill_2 = WorkerSkill(worker_id=worker.id, category_id=category_2.id)
    db.session.add_all([skill_1, skill_2])
    db.session.commit()

    assert len(worker.skills) == 2
    assert {skill.category.name for skill in worker.skills} == {"Plumbing", "Electrical"}


def test_problem_assignment_and_status_history(app_ctx):
    resident = User(name="Carol", email="carol@example.com", phone="3333333333", password_hash="hash", role="resident")
    category = Category(name="Water Leakage", description="Water leak fixes")
    problem = Problem(
        problem_id="CMP-1001",
        resident=resident,
        category=category,
        title="Pipe leak",
        description="Kitchen pipe leaking",
        priority="HIGH",
        status="NEW",
        location_text="Main Road",
        latitude=12.345,
        longitude=67.89,
    )
    db.session.add_all([resident, category, problem])
    db.session.commit()

    assignment = Assignment(problem_id=problem.id, worker_id=None)
    db.session.add(assignment)
    db.session.flush()

    history_1 = StatusHistory(problem_id=problem.id, old_status=None, new_status="NEW", changed_by=resident.id, notes="Problem created")
    history_2 = StatusHistory(problem_id=problem.id, old_status="NEW", new_status="PENDING_ASSIGNMENT", changed_by=resident.id, notes="Awaiting assignment")
    db.session.add_all([history_1, history_2])
    db.session.commit()

    assert category.problems[0].id == problem.id
    assert len(problem.assignments) >= 1
    assert len(problem.status_history) == 2


def test_unique_constraints(app_ctx):
    user_1 = User(name="Dana", email="dana@example.com", phone="4444444444", password_hash="hash", role="resident")
    user_2 = User(name="Diana", email="dana@example.com", phone="5555555555", password_hash="hash", role="resident")
    db.session.add(user_1)
    db.session.commit()

    db.session.add(user_2)
    with pytest.raises(Exception):
        db.session.commit()

    db.session.rollback()

    category_1 = Category(name="Parking", description="Parking issues")
    category_2 = Category(name="Parking", description="Duplicate name")
    db.session.add_all([category_1, category_2])
    with pytest.raises(Exception):
        db.session.commit()
