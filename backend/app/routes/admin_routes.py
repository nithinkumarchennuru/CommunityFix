from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Assignment, Category, Problem, StatusHistory, User, Worker
from app.services.worker_service import calculate_workload

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _serialize_admin_problem(problem):
    return {
        "id": problem.id,
        "problem_id": problem.problem_id,
        "title": problem.title,
        "description": problem.description,
        "priority": problem.priority,
        "status": problem.status,
        "category_id": problem.category_id,
        "category_name": problem.category.name if problem.category else None,
        "resident_id": problem.resident_id,
        "resident_name": problem.resident.name if problem.resident else None,
        "created_at": problem.created_at.isoformat() if problem.created_at else None,
        "updated_at": problem.updated_at.isoformat() if problem.updated_at else None,
        "resolved_at": problem.resolved_at.isoformat() if problem.resolved_at else None,
    }


def _serialize_admin_worker(worker):
    workload = calculate_workload(worker.current_active_jobs, worker.maximum_capacity)
    return {
        "id": worker.id,
        "worker_id": worker.worker_id,
        "user_id": worker.user_id,
        "name": worker.user.name if worker.user else None,
        "email": worker.user.email if worker.user else None,
        "availability_status": worker.availability_status,
        "maximum_capacity": worker.maximum_capacity,
        "current_active_jobs": worker.current_active_jobs,
        "workload_percentage": workload["workload_percentage"],
        "capacity_available": workload["capacity_available"],
    }


def _ensure_admin_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id)) if user_id is not None else None
    if not user:
        return None, (jsonify({"success": False, "message": "User not found"}), 404)
    if user.role != "admin":
        return None, (jsonify({"success": False, "message": "Forbidden: admin access required"}), 403)
    return user, None


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    admin_user, error = _ensure_admin_user()
    if error is not None:
        return error

    problem_statuses = [
        "NEW",
        "PENDING_ASSIGNMENT",
        "ASSIGNED",
        "ACCEPTED",
        "ON_THE_WAY",
        "IN_PROGRESS",
        "RESOLVED",
        "RESIDENT_CONFIRMED",
        "REOPENED",
        "ESCALATED",
        "CANCELLED",
    ]

    problem_counts = {
        status: Problem.query.filter_by(status=status).count()
        for status in problem_statuses
    }

    total_problems = Problem.query.count()
    workers = Worker.query.all()
    total_workers = len(workers)
    worker_counts = {
        "available": Worker.query.filter_by(availability_status="AVAILABLE").count(),
        "busy": Worker.query.filter_by(availability_status="BUSY").count(),
        "offline": Worker.query.filter_by(availability_status="OFFLINE").count(),
    }

    total_assignments = Assignment.query.count()
    assignment_counts = {
        "total": total_assignments,
        "active": Assignment.query.filter(Assignment.status.in_(["ASSIGNED", "ACCEPTED", "ON_THE_WAY", "IN_PROGRESS", "REASSIGNED", "REJECTED"])).count(),
        "completed": Assignment.query.filter_by(status="COMPLETED").count(),
        "rejected": Assignment.query.filter_by(status="REJECTED").count(),
        "reassigned": Assignment.query.filter_by(status="REASSIGNED").count(),
    }

    category_rows = (
        db.session.query(Category.name, func.count(Problem.id).label("problem_count"))
        .join(Problem, Problem.category_id == Category.id)
        .group_by(Category.id, Category.name)
        .order_by(func.count(Problem.id).desc(), Category.name.asc())
        .limit(10)
        .all()
    )
    category_breakdown = [
        {"category": name, "count": count}
        for name, count in category_rows
    ]

    high_workload_workers = []
    for worker in workers:
        workload = calculate_workload(worker.current_active_jobs, worker.maximum_capacity)
        if workload["workload_percentage"] >= 75:
            high_workload_workers.append({
                "worker_id": worker.worker_id,
                "name": worker.user.name if worker.user else None,
                "availability_status": worker.availability_status,
                "current_active_jobs": worker.current_active_jobs,
                "maximum_capacity": worker.maximum_capacity,
                "workload_percentage": workload["workload_percentage"],
            })
    high_workload_workers.sort(key=lambda item: item["workload_percentage"], reverse=True)

    now = datetime.now(timezone.utc)
    overdue_cutoff = now - timedelta(hours=24)
    overdue_problems = (
        Problem.query.filter(
            Problem.status.notin_(["RESOLVED", "RESIDENT_CONFIRMED", "CANCELLED"]),
            Problem.updated_at < overdue_cutoff,
        )
        .order_by(Problem.updated_at.asc())
        .limit(10)
        .all()
    )

    pending_assignment_problems = (
        Problem.query.filter(Problem.status.in_(["NEW", "PENDING_ASSIGNMENT", "REASSIGNED", "ESCALATED"]))
        .order_by(Problem.created_at.asc())
        .limit(10)
        .all()
    )

    recent_activity = (
        StatusHistory.query.order_by(StatusHistory.changed_at.desc())
        .limit(10)
        .all()
    )

    recent_status_activity = []
    for record in recent_activity:
        recent_status_activity.append({
            "problem_id": record.problem.problem_id if record.problem else None,
            "old_status": record.old_status,
            "new_status": record.new_status,
            "changed_by": record.changed_by_user.name if record.changed_by_user else None,
            "changed_at": record.changed_at.isoformat() if record.changed_at else None,
            "notes": record.notes,
        })

    resolved_records = Problem.query.filter(Problem.status == "RESOLVED").all()
    resolution_hours = []
    for problem in resolved_records:
        if problem.created_at and problem.resolved_at:
            delta = problem.resolved_at - problem.created_at
            resolution_hours.append(delta.total_seconds() / 3600)
    avg_resolution_hours = round(sum(resolution_hours) / len(resolution_hours), 2) if resolution_hours else 0

    last_7_days = []
    for offset in range(7):
        day = (now - timedelta(days=6 - offset)).date()
        count = Problem.query.filter(
            Problem.status == "RESOLVED",
            func.date(Problem.resolved_at) == day,
        ).count()
        last_7_days.append({"date": day.isoformat(), "count": count})

    dashboard_payload = {
        "problems": {
            "total": total_problems,
            "new": problem_counts.get("NEW", 0),
            "pending_assignment": problem_counts.get("PENDING_ASSIGNMENT", 0),
            "assigned": problem_counts.get("ASSIGNED", 0),
            "accepted": problem_counts.get("ACCEPTED", 0),
            "on_the_way": problem_counts.get("ON_THE_WAY", 0),
            "in_progress": problem_counts.get("IN_PROGRESS", 0),
            "resolved": problem_counts.get("RESOLVED", 0),
            "resident_confirmed": problem_counts.get("RESIDENT_CONFIRMED", 0),
            "reopened": problem_counts.get("REOPENED", 0),
            "escalated": problem_counts.get("ESCALATED", 0),
            "cancelled": problem_counts.get("CANCELLED", 0),
        },
        "workers": {
            "total": total_workers,
            "available": worker_counts["available"],
            "busy": worker_counts["busy"],
            "offline": worker_counts["offline"],
        },
        "assignments": assignment_counts,
        "categories": {
            "top_categories": category_breakdown,
        },
        "pending_assignment_problems": [
            _serialize_admin_problem(problem) for problem in pending_assignment_problems
        ],
        "overdue_problems": [
            _serialize_admin_problem(problem) for problem in overdue_problems
        ],
        "high_workload_workers": high_workload_workers,
        "recent_activity": recent_status_activity,
        "performance": {
            "average_resolution_hours": avg_resolution_hours,
            "resolution_trend_last_7_days": last_7_days,
        },
    }

    return jsonify({"success": True, "dashboard": dashboard_payload}), 200


@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
def analytics():
    admin_user, error = _ensure_admin_user()
    if error is not None:
        return error

    total_problems = Problem.query.count()
    status_counts = {
        status: Problem.query.filter_by(status=status).count()
        for status in [
            "NEW",
            "PENDING_ASSIGNMENT",
            "ASSIGNED",
            "ACCEPTED",
            "ON_THE_WAY",
            "IN_PROGRESS",
            "RESOLVED",
            "RESIDENT_CONFIRMED",
            "REOPENED",
            "ESCALATED",
            "CANCELLED",
        ]
    }
    active_workers = Worker.query.filter(Worker.availability_status != "OFFLINE").count()
    problems_by_category = [
        {
            "category": item[0],
            "count": item[1],
        }
        for item in (
            db.session.query(Category.name, func.count(Problem.id))
            .join(Problem, Problem.category_id == Category.id)
            .group_by(Category.id, Category.name)
            .order_by(func.count(Problem.id).desc())
            .all()
        )
    ]

    response = {
        "success": True,
        "analytics": {
            "total_problems": total_problems,
            "status_counts": status_counts,
            "active_workers": active_workers,
            "by_category": problems_by_category,
            "assignment_summary": {
                "total": Assignment.query.count(),
                "completed": Assignment.query.filter_by(status="COMPLETED").count(),
                "rejected": Assignment.query.filter_by(status="REJECTED").count(),
            },
        },
    }
    return jsonify(response), 200


@admin_bp.route("/problems/pending-assignment", methods=["GET"])
@jwt_required()
def pending_assignment_problems():
    admin_user, error = _ensure_admin_user()
    if error is not None:
        return error

    problems = (
        Problem.query.filter(Problem.status.in_(["NEW", "PENDING_ASSIGNMENT", "REASSIGNED", "ESCALATED"]))
        .order_by(Problem.created_at.asc())
        .all()
    )
    return jsonify({
        "success": True,
        "count": len(problems),
        "problems": [_serialize_admin_problem(problem) for problem in problems],
    }), 200


@admin_bp.route("/workers/high-workload", methods=["GET"])
@jwt_required()
def high_workload_workers():
    admin_user, error = _ensure_admin_user()
    if error is not None:
        return error

    threshold = request.args.get("threshold", default=75, type=float)
    workers = []
    for worker in Worker.query.all():
        workload = calculate_workload(worker.current_active_jobs, worker.maximum_capacity)
        if workload["workload_percentage"] >= threshold:
            workers.append(_serialize_admin_worker(worker))
    workers.sort(key=lambda item: item["workload_percentage"], reverse=True)
    return jsonify({"success": True, "threshold": threshold, "workers": workers}), 200
