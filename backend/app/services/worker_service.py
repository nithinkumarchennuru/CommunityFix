from __future__ import annotations

from typing import Any

from flask import current_app
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Category, User, Worker, WorkerSkill

VALID_AVAILABILITY_STATUSES = {"AVAILABLE", "BUSY", "OFFLINE"}


def calculate_workload(current_active_jobs: int, maximum_capacity: int) -> dict[str, Any]:
    if maximum_capacity is None or maximum_capacity <= 0:
        return {
            "current_active_jobs": current_active_jobs or 0,
            "maximum_capacity": 0,
            "workload_percentage": 0,
            "capacity_available": 0,
        }

    current = max(int(current_active_jobs or 0), 0)
    maximum = max(int(maximum_capacity), 0)
    percentage = round((current / maximum) * 100, 2) if maximum else 0
    capacity_available = max(maximum - current, 0)

    return {
        "current_active_jobs": current,
        "maximum_capacity": maximum,
        "workload_percentage": percentage,
        "capacity_available": capacity_available,
    }


def get_worker_by_user_id(user_id: int) -> Worker | None:
    return Worker.query.filter_by(user_id=user_id).first()


def get_worker_by_public_id(worker_id: str) -> Worker | None:
    return Worker.query.filter_by(worker_id=worker_id).first()


def serialize_worker(worker: Worker) -> dict[str, Any]:
    workload = calculate_workload(worker.current_active_jobs, worker.maximum_capacity)
    skills = [
        {"id": skill.id, "name": skill.category.name, "category_id": skill.category_id}
        for skill in sorted(worker.skills, key=lambda item: item.category.name.lower())
        if skill.category is not None
    ]

    return {
        "id": worker.id,
        "worker_id": worker.worker_id,
        "user_id": worker.user_id,
        "name": worker.user.name,
        "email": worker.user.email,
        "phone": worker.user.phone,
        "role": worker.user.role,
        "availability_status": worker.availability_status,
        "maximum_capacity": worker.maximum_capacity,
        "current_active_jobs": worker.current_active_jobs,
        "workload_percentage": workload["workload_percentage"],
        "capacity_available": workload["capacity_available"],
        "skills": skills,
        "created_at": worker.created_at.isoformat() if worker.created_at else None,
        "updated_at": worker.updated_at.isoformat() if worker.updated_at else None,
    }


def get_workers(filters: dict[str, Any] | None = None, page: int = 1, per_page: int = 10):
    filters = filters or {}
    query = Worker.query.join(User, Worker.user_id == User.id)

    if filters.get("availability_status"):
        query = query.filter(Worker.availability_status == filters["availability_status"].upper())

    if filters.get("category_id"):
        query = query.join(WorkerSkill, WorkerSkill.worker_id == Worker.id).filter(WorkerSkill.category_id == int(filters["category_id"]))

    if filters.get("name"):
        like_value = f"%{filters['name']}%"
        query = query.filter(or_(User.name.ilike(like_value), Worker.worker_id.ilike(like_value)))

    total = query.distinct().count()
    page = max(page, 1)
    per_page = max(per_page, 1)
    pages = max((total + per_page - 1) // per_page, 1) if total else 1
    offset = (page - 1) * per_page
    workers = query.order_by(Worker.created_at.desc()).distinct().offset(offset).limit(per_page).all()

    return {
        "workers": [serialize_worker(worker) for worker in workers],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
        },
    }


def create_worker(data: dict[str, Any]) -> Worker:
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    maximum_capacity = data.get("maximum_capacity")

    if not name:
        raise ValueError("Name is required")
    if not email:
        raise ValueError("Email is required")
    if "@" not in email or "." not in email:
        raise ValueError("Invalid email format")
    if not password:
        raise ValueError("Password is required")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not maximum_capacity:
        raise ValueError("Maximum capacity is required")

    try:
        cap = int(maximum_capacity)
    except (TypeError, ValueError):
        raise ValueError("Maximum capacity must be a positive integer") from None

    if cap <= 0:
        raise ValueError("Maximum capacity must be a positive integer")

    if User.query.filter_by(email=email).first():
        raise ValueError("Email already registered")

    user = User(
        name=name,
        email=email,
        phone=phone or "",
        password_hash=generate_password_hash(password),
        role="worker",
    )

    db.session.add(user)
    db.session.flush()

    worker = Worker(
        user_id=user.id,
        worker_id=generate_worker_id(),
        availability_status="OFFLINE",
        maximum_capacity=cap,
        current_active_jobs=0,
    )
    db.session.add(worker)
    db.session.flush()

    return worker


def generate_worker_id() -> str:
    existing = Worker.query.order_by(Worker.id.desc()).first()
    next_number = (existing.id if existing else 0) + 1
    return f"WRK-{next_number:04d}"


def add_worker_skill(worker: Worker, category_id: int) -> WorkerSkill:
    if not category_id:
        raise ValueError("Category is required")

    category = Category.query.filter_by(id=int(category_id), is_active=True).first()
    if not category:
        raise ValueError("Category not found")

    existing = WorkerSkill.query.filter_by(worker_id=worker.id, category_id=category.id).first()
    if existing:
        raise ValueError("Skill already assigned to this worker")

    skill = WorkerSkill(worker_id=worker.id, category_id=category.id)
    db.session.add(skill)
    db.session.flush()
    return skill


def remove_worker_skill(worker: Worker, skill_id: int) -> None:
    skill = WorkerSkill.query.filter_by(id=skill_id, worker_id=worker.id).first()
    if not skill:
        raise ValueError("Skill not found")
    db.session.delete(skill)
    db.session.flush()


def update_worker_availability(worker: Worker, availability_status: str) -> str:
    status = (availability_status or "").strip().upper()
    if status not in VALID_AVAILABILITY_STATUSES:
        raise ValueError("Availability status must be AVAILABLE, BUSY, or OFFLINE")
    worker.availability_status = status
    worker.updated_at = current_app.config.get("CURRENT_TIME") if current_app.config.get("CURRENT_TIME") else worker.updated_at
    return worker.availability_status


def update_worker_capacity(worker: Worker, maximum_capacity: int) -> Worker:
    try:
        cap = int(maximum_capacity)
    except (TypeError, ValueError):
        raise ValueError("Maximum capacity must be a positive integer") from None

    if cap <= 0:
        raise ValueError("Maximum capacity must be a positive integer")

    if cap < worker.current_active_jobs:
        raise ValueError("Maximum capacity cannot be lower than current_active_jobs")

    worker.maximum_capacity = cap
    return worker


def get_worker_profile(worker: Worker) -> dict[str, Any]:
    payload = serialize_worker(worker)
    payload.pop("id", None)
    payload.pop("role", None)
    return payload
