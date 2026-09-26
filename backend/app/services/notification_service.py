from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.extensions import db
from app.models import Assignment, Notification, Problem, User, Worker


NOTIFICATION_TYPES = {
    "PROBLEM_CREATED": "PROBLEM_CREATED",
    "PROBLEM_ASSIGNED": "PROBLEM_ASSIGNED",
    "ASSIGNMENT_ACCEPTED": "ASSIGNMENT_ACCEPTED",
    "ASSIGNMENT_REJECTED": "ASSIGNMENT_REJECTED",
    "PROBLEM_REASSIGNED": "PROBLEM_REASSIGNED",
    "WORKER_ON_THE_WAY": "WORKER_ON_THE_WAY",
    "WORK_STARTED": "WORK_STARTED",
    "PROBLEM_RESOLVED": "PROBLEM_RESOLVED",
    "PROBLEM_CONFIRMED": "PROBLEM_CONFIRMED",
    "PROBLEM_REOPENED": "PROBLEM_REOPENED",
    "PROBLEM_ESCALATED": "PROBLEM_ESCALATED",
    "PROBLEM_CANCELLED": "PROBLEM_CANCELLED",
    "ASSIGNMENT_CANCELLED": "ASSIGNMENT_CANCELLED",
    "PENDING_ASSIGNMENT": "PENDING_ASSIGNMENT",
    "ADMIN_ALERT": "ADMIN_ALERT",
}


def _utcnow():
    return datetime.now(timezone.utc)


def create_notification(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    problem_id: int | None = None,
    assignment_id: int | None = None,
) -> Notification:
    if not user_id:
        raise ValueError("user_id is required")
    notification = Notification(
        user_id=user_id,
        problem_id=problem_id,
        assignment_id=assignment_id,
        type=str(notification_type).upper(),
        title=title,
        message=message,
        is_read=False,
        created_at=_utcnow(),
    )
    db.session.add(notification)
    db.session.flush()
    return notification


def notify_user(user_id: int, notification_type: str, title: str, message: str, problem: Problem | None = None, assignment: Assignment | None = None) -> Notification | None:
    if not user_id:
        return None
    if problem is None and assignment is not None:
        problem = assignment.problem
    notification = create_notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        problem_id=problem.id if problem else None,
        assignment_id=assignment.id if assignment else None,
    )
    return notification


def notify_resident(problem: Problem, notification_type: str, title: str, message: str, assignment: Assignment | None = None) -> Notification | None:
    if not problem or not problem.resident_id:
        return None
    return notify_user(
        user_id=problem.resident_id,
        notification_type=notification_type,
        title=title,
        message=message,
        problem=problem,
        assignment=assignment,
    )


def notify_worker(worker: Worker, notification_type: str, title: str, message: str, problem: Problem | None = None, assignment: Assignment | None = None) -> Notification | None:
    if not worker or not worker.user_id:
        return None
    return notify_user(
        user_id=worker.user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        problem=problem,
        assignment=assignment,
    )


def notify_admins(notification_type: str, title: str, message: str, problem: Problem | None = None, assignment: Assignment | None = None) -> list[Notification]:
    admins = User.query.filter_by(role="admin").all()
    notifications = []
    for admin in admins:
        notification = notify_user(
            user_id=admin.id,
            notification_type=notification_type,
            title=title,
            message=message,
            problem=problem,
            assignment=assignment,
        )
        if notification is not None:
            notifications.append(notification)
    return notifications


def mark_as_read(notification_id: int, user_id: int) -> Notification | None:
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        return None
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = _utcnow()
    return notification


def mark_all_as_read(user_id: int) -> int:
    return Notification.query.filter_by(user_id=user_id, is_read=False).update({
        "is_read": True,
        "read_at": _utcnow(),
    }, synchronize_session=False)


def get_user_notifications(user_id: int, unread_only: bool = False, notification_type: str | None = None, page: int = 1, per_page: int = 20) -> dict[str, Any]:
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    if notification_type:
        query = query.filter(Notification.type == str(notification_type).upper())

    notifications = query.order_by(Notification.created_at.desc()).all()
    total = len(notifications)
    page = max(page, 1)
    per_page = max(per_page, 1)
    start = (page - 1) * per_page
    end = start + per_page
    paged = notifications[start:end]

    return {
        "notifications": [{
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "message": item.message,
            "problem_id": item.problem.problem_id if item.problem else None,
            "assignment_id": item.assignment_id,
            "is_read": item.is_read,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "read_at": item.read_at.isoformat() if item.read_at else None,
        } for item in paged],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
        },
    }


def get_unread_count(user_id: int) -> int:
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()
