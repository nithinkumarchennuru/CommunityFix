from __future__ import annotations

from typing import Any

VALID_PROBLEM_TRANSITIONS = {
    "NEW": {"PENDING_ASSIGNMENT", "ASSIGNED"},
    "PENDING_ASSIGNMENT": {"ASSIGNED"},
    "ASSIGNED": {"ACCEPTED", "REJECTED", "REASSIGNED", "PENDING_ASSIGNMENT"},
    "ACCEPTED": {"ON_THE_WAY", "IN_PROGRESS", "REJECTED", "PENDING_ASSIGNMENT"},
    "ON_THE_WAY": {"IN_PROGRESS", "REJECTED", "PENDING_ASSIGNMENT"},
    "IN_PROGRESS": {"RESOLVED", "REJECTED", "PENDING_ASSIGNMENT"},
    "REJECTED": {"PENDING_ASSIGNMENT", "ASSIGNED"},
    "REASSIGNED": {"ASSIGNED", "PENDING_ASSIGNMENT"},
    "RESOLVED": {"RESIDENT_CONFIRMED", "REOPENED"},
    "REOPENED": {"PENDING_ASSIGNMENT", "ASSIGNED"},
    "RESIDENT_CONFIRMED": set(),
    "CANCELLED": set(),
    "ESCALATED": {"PENDING_ASSIGNMENT", "ASSIGNED"},
}

VALID_ASSIGNMENT_TRANSITIONS = {
    "ASSIGNED": {"ACCEPTED", "REJECTED", "REASSIGNED", "CANCELLED"},
    "ACCEPTED": {"ON_THE_WAY", "IN_PROGRESS", "REJECTED", "CANCELLED"},
    "ON_THE_WAY": {"IN_PROGRESS", "REJECTED", "CANCELLED"},
    "IN_PROGRESS": {"COMPLETED", "REJECTED", "CANCELLED"},
    "COMPLETED": set(),
    "REJECTED": {"REASSIGNED", "CANCELLED"},
    "REASSIGNED": {"ASSIGNED", "REJECTED", "CANCELLED"},
    "CANCELLED": set(),
}


def can_transition(current: str | None, next_status: str) -> bool:
    if not current:
        return True
    current = str(current).upper()
    next_status = str(next_status).upper()
    return next_status in VALID_PROBLEM_TRANSITIONS.get(current, set()) or next_status in VALID_ASSIGNMENT_TRANSITIONS.get(current, set())


def validate_problem_transition(current: str | None, next_status: str) -> None:
    if not current:
        return
    current = str(current).upper()
    next_status = str(next_status).upper()

    allowed = VALID_PROBLEM_TRANSITIONS.get(current, set())
    if next_status not in allowed:
        raise ValueError(f"Invalid problem status transition from {current} to {next_status}")


def validate_assignment_transition(current: str | None, next_status: str) -> None:
    if not current:
        return
    current = str(current).upper()
    next_status = str(next_status).upper()

    allowed = VALID_ASSIGNMENT_TRANSITIONS.get(current, set())
    if next_status not in allowed:
        raise ValueError(f"Invalid assignment status transition from {current} to {next_status}")


def record_status_history(problem, old_status: str | None, new_status: str, changed_by: int | None, notes: str | None = None) -> None:
    from app.models import StatusHistory

    problem.status = new_status
    problem.updated_at = problem.updated_at
    problem.status_history.append(StatusHistory(
        problem_id=problem.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        notes=notes,
    ))
