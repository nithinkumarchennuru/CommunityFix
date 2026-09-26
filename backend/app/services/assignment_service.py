from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from flask import current_app

from app.extensions import db
from app.models import Assignment, Problem, ProblemImage, StatusHistory, Worker, WorkerSkill
from app.services.notification_service import notify_admins, notify_resident, notify_worker
from app.services.status_service import validate_assignment_transition, validate_problem_transition
from app.services.worker_service import calculate_workload

PRIORITY_WEIGHT = {
    "LOW": 3,
    "MEDIUM": 2,
    "HIGH": 1,
    "URGENT": 0,
}


def _utcnow():
    return datetime.now(timezone.utc)


def _get_problem(problem_ref: Problem | int | str) -> Problem | None:
    if isinstance(problem_ref, Problem):
        return problem_ref
    if isinstance(problem_ref, int):
        return Problem.query.filter_by(id=problem_ref).first()
    return Problem.query.filter_by(problem_id=str(problem_ref)).first()


def find_eligible_workers(problem: Problem | int | str) -> list[Worker]:
    problem_obj = _get_problem(problem)
    if problem_obj is None:
        return []
    problem = problem_obj

    if problem is None or not problem.category_id:
        return []

    workers = (
        Worker.query.join(WorkerSkill, WorkerSkill.worker_id == Worker.id)
        .filter(WorkerSkill.category_id == problem.category_id)
        .filter(Worker.availability_status == "AVAILABLE")
        .filter(Worker.maximum_capacity > 0)
        .filter(Worker.current_active_jobs < Worker.maximum_capacity)
        .distinct()
        .all()
    )

    return sorted(workers, key=lambda worker: (worker.id, worker.worker_id))


def calculate_worker_score(worker: Worker, problem: Problem) -> float:
    if worker.maximum_capacity <= 0:
        return float("inf")

    workload = calculate_workload(worker.current_active_jobs, worker.maximum_capacity)
    workload_percentage = float(workload["workload_percentage"])
    priority_bias = PRIORITY_WEIGHT.get(str(problem.priority).upper(), 2)

    # Lower workload is preferred; urgent problems also slightly bias the score downward.
    # Location is ignored unless a worker location model is introduced later, which is consistent
    # with the current schema and requirement not to invent worker GPS data.
    score = workload_percentage + (priority_bias * 0.25)
    score += worker.current_active_jobs * 0.25
    return round(score, 4)


def rank_workers(problem: Problem, workers: list[Worker]) -> list[dict[str, Any]]:
    ranked = []
    for worker in workers:
        score = calculate_worker_score(worker, problem)
        workload = calculate_workload(worker.current_active_jobs, worker.maximum_capacity)
        ranked.append({
            "worker": worker,
            "score": score,
            "workload_percentage": workload["workload_percentage"],
            "capacity_available": workload["capacity_available"],
            "reason": (
                f"workload={workload['workload_percentage']}%, "
                f"capacity_available={workload['capacity_available']}"
            ),
        })

    ranked.sort(key=lambda item: (
        item["score"],
        item["worker"].current_active_jobs,
        item["worker"].maximum_capacity,
        item["worker"].id,
    ))
    return ranked


def create_assignment(problem: Problem, worker: Worker) -> dict[str, Any]:
    if problem is None or worker is None:
        return {"success": False, "message": "Problem and worker are required"}

    existing_assignment = Assignment.query.filter_by(problem_id=problem.id, worker_id=worker.id).first()
    if existing_assignment is not None:
        return {
            "success": True,
            "message": "Assignment already exists for this problem and worker",
            "assignment": {
                "id": existing_assignment.id,
                "problem_id": existing_assignment.problem_id,
                "worker_id": existing_assignment.worker_id,
                "assigned_at": existing_assignment.assigned_at.isoformat() if existing_assignment.assigned_at else None,
            },
        }

    assignment = Assignment(
        problem_id=problem.id,
        worker_id=worker.id,
        assigned_at=_utcnow(),
    )
    db.session.add(assignment)
    db.session.flush()

    old_status = problem.status
    problem.status = "ASSIGNED"
    worker.current_active_jobs = int(worker.current_active_jobs or 0) + 1
    db.session.add(StatusHistory(
        problem_id=problem.id,
        old_status=old_status,
        new_status="ASSIGNED",
        changed_by=problem.resident_id,
        notes=f"Assigned to worker {worker.worker_id}",
    ))
    db.session.flush()

    notify_worker(
        worker,
        "PROBLEM_ASSIGNED",
        "New problem assigned",
        f"You have been assigned a new problem {problem.problem_id}.",
        problem=problem,
        assignment=None,
    )
    notify_resident(
        problem,
        "PROBLEM_ASSIGNED",
        "Problem assigned",
        f"Your reported problem {problem.problem_id} has been assigned to a worker.",
        assignment=None,
    )

    return {
        "success": True,
        "message": "Problem assigned successfully",
        "assignment": {
            "id": assignment.id,
            "problem_id": assignment.problem_id,
            "worker_id": assignment.worker_id,
            "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None,
            "worker_name": worker.user.name if worker.user else None,
            "worker_id_public": worker.worker_id,
        },
        "problem_status": problem.status,
    }


def handle_no_available_worker(problem: Problem) -> dict[str, Any]:
    if problem is None:
        return {"success": False, "message": "Problem not found"}

    old_status = problem.status
    problem.status = "PENDING_ASSIGNMENT"
    db.session.add(StatusHistory(
        problem_id=problem.id,
        old_status=old_status,
        new_status="PENDING_ASSIGNMENT",
        changed_by=problem.resident_id,
        notes="No eligible worker available for this problem",
    ))
    notify_admins(
        "ADMIN_ALERT",
        "Unassigned problem",
        f"Problem {problem.problem_id} has no eligible workers available for assignment.",
        problem=problem,
    )
    notify_resident(
        problem,
        "PENDING_ASSIGNMENT",
        "Assignment pending",
        f"No worker is currently available for problem {problem.problem_id}. We are retrying assignment.",
    )
    db.session.flush()

    return {
        "success": False,
        "message": "No eligible worker available",
        "problem_status": "PENDING_ASSIGNMENT",
        "eligible_workers": [],
    }


def assign_problem(problem_id: int | str) -> dict[str, Any]:
    problem = _get_problem(problem_id)
    if not problem:
        return {"success": False, "message": "Problem not found"}

    if problem.status == "CANCELLED":
        return {"success": False, "message": "Cannot assign a cancelled problem", "problem_status": problem.status}

    eligible_workers = find_eligible_workers(problem)
    if not eligible_workers:
        result = handle_no_available_worker(problem)
        db.session.commit()
        return result

    ranked_workers = rank_workers(problem, eligible_workers)
    selected_worker = ranked_workers[0]["worker"]
    result = create_assignment(problem, selected_worker)

    if not result.get("success"):
        db.session.rollback()
        return result

    db.session.commit()
    return {
        **result,
        "worker": {
            "id": selected_worker.id,
            "worker_id": selected_worker.worker_id,
            "name": selected_worker.user.name if selected_worker.user else None,
            "availability_status": selected_worker.availability_status,
            "workload_percentage": calculate_workload(selected_worker.current_active_jobs, selected_worker.maximum_capacity)["workload_percentage"],
        },
        "ranked_workers": [
            {
                "worker_id": item["worker"].worker_id,
                "name": item["worker"].user.name if item["worker"].user else None,
                "score": item["score"],
                "workload_percentage": item["workload_percentage"],
                "capacity_available": item["capacity_available"],
            }
            for item in ranked_workers
        ],
    }


def get_worker_assignments(worker_id: int, status: str | None = None, priority: str | None = None, page: int = 1, per_page: int = 10):
    query = Assignment.query.filter_by(worker_id=worker_id)
    if status:
        query = query.filter(Assignment.status == str(status).upper())

    assignments = query.order_by(Assignment.created_at.desc()).all()
    if priority:
        priority = str(priority).upper()
        assignments = [item for item in assignments if item.problem and item.problem.priority == priority]

    total = len(assignments)
    page = max(page, 1)
    per_page = max(per_page, 1)
    start = (page - 1) * per_page
    end = start + per_page
    paged = assignments[start:end]

    return {
        "assignments": [
            {
                "assignment_id": item.id,
                "problem_id": item.problem.problem_id if item.problem else None,
                "status": item.status,
                "problem_status": item.problem.status if item.problem else None,
                "title": item.problem.title if item.problem else None,
                "description": item.problem.description if item.problem else None,
                "priority": item.problem.priority if item.problem else None,
                "location_text": item.problem.location_text if item.problem else None,
                "assigned_at": item.assigned_at.isoformat() if item.assigned_at else None,
                "accepted_at": item.accepted_at.isoformat() if item.accepted_at else None,
                "started_at": item.started_at.isoformat() if item.started_at else None,
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                "rejected_at": item.rejected_at.isoformat() if item.rejected_at else None,
                "rejection_reason": item.rejection_reason,
            }
            for item in paged
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": max((total + per_page - 1) // per_page, 1) if total else 1,
        },
    }


def _get_assignment_or_error(assignment_id: int, worker_id: int | None = None) -> Assignment:
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        raise ValueError("Assignment not found")
    if worker_id is not None:
        worker_profile = Worker.query.filter_by(user_id=worker_id).first()
        effective_worker_id = worker_profile.id if worker_profile else worker_id
        if assignment.worker_id != effective_worker_id:
            raise ValueError("You do not have access to this assignment")
    return assignment


def _record_assignment_status(assignment: Assignment, new_status: str, problem: Problem | None = None, changed_by: int | None = None, notes: str | None = None):
    old_status = assignment.status
    validate_assignment_transition(old_status, new_status)
    assignment.status = new_status
    assignment.updated_at = datetime.now(timezone.utc)
    if new_status == "ACCEPTED":
        assignment.accepted_at = datetime.now(timezone.utc)
    elif new_status == "REJECTED":
        assignment.rejected_at = datetime.now(timezone.utc)
    elif new_status == "COMPLETED":
        assignment.completed_at = datetime.now(timezone.utc)
    elif new_status == "REASSIGNED":
        assignment.reassigned_at = datetime.now(timezone.utc)
    elif new_status == "IN_PROGRESS":
        assignment.started_at = assignment.started_at or datetime.now(timezone.utc)

    if problem is not None:
        validate_problem_transition(problem.status, new_status)
        old_problem_status = problem.status
        problem.status = new_status
        problem.updated_at = datetime.now(timezone.utc)
        db.session.add(StatusHistory(
            problem_id=problem.id,
            old_status=old_problem_status,
            new_status=new_status,
            changed_by=changed_by,
            notes=notes,
        ))

    db.session.add(StatusHistory(
        problem_id=assignment.problem_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        notes=notes,
    ))


def accept_assignment(assignment_id: int, worker_id: int) -> dict[str, Any]:
    assignment = _get_assignment_or_error(assignment_id, worker_id)
    problem = assignment.problem
    if not problem:
        raise ValueError("Problem not found")
    validate_assignment_transition(assignment.status, "ACCEPTED")
    validate_problem_transition(problem.status, "ACCEPTED")

    assignment.status = "ACCEPTED"
    assignment.accepted_at = datetime.now(timezone.utc)
    problem.status = "ACCEPTED"
    assignment.updated_at = datetime.now(timezone.utc)
    db.session.add(StatusHistory(
        problem_id=problem.id,
        old_status=problem.status,
        new_status="ACCEPTED",
        changed_by=worker_id,
        notes="Worker accepted the assignment",
    ))
    notify_resident(
        problem,
        "ASSIGNMENT_ACCEPTED",
        "Worker accepted your request",
        "The assigned worker has accepted your problem request.",
        assignment=assignment,
    )
    return {
        "assignment": {
            "assignment_id": assignment.id,
            "status": assignment.status,
            "accepted_at": assignment.accepted_at.isoformat() if assignment.accepted_at else None,
        },
        "problem_status": problem.status,
    }


def start_travel(assignment_id: int, worker_id: int) -> dict[str, Any]:
    assignment = _get_assignment_or_error(assignment_id, worker_id)
    if assignment.status != "ACCEPTED":
        raise ValueError("Assignment must be accepted before travel can begin")
    assignment.status = "ON_THE_WAY"
    assignment.updated_at = datetime.now(timezone.utc)
    if assignment.problem:
        assignment.problem.status = "ON_THE_WAY"
        notify_resident(
            assignment.problem,
            "WORKER_ON_THE_WAY",
            "Worker is on the way",
            "The assigned worker is on the way to handle your problem.",
            assignment=assignment,
        )
    return {"assignment": {"assignment_id": assignment.id, "status": assignment.status}}


def start_assignment(assignment_id: int, worker_id: int) -> dict[str, Any]:
    assignment = _get_assignment_or_error(assignment_id, worker_id)
    if assignment.status not in {"ACCEPTED", "ON_THE_WAY"}:
        raise ValueError("Assignment must be accepted before work can start")
    assignment.status = "IN_PROGRESS"
    assignment.started_at = assignment.started_at or datetime.now(timezone.utc)
    assignment.updated_at = datetime.now(timezone.utc)
    if assignment.problem:
        assignment.problem.status = "IN_PROGRESS"
        notify_resident(
            assignment.problem,
            "WORK_STARTED",
            "Work started",
            "Work has started on your reported problem.",
            assignment=assignment,
        )
    return {"assignment": {"assignment_id": assignment.id, "status": assignment.status}}


def complete_assignment(assignment_id: int, worker_id: int) -> dict[str, Any]:
    assignment = _get_assignment_or_error(assignment_id, worker_id)
    if assignment.status not in {"IN_PROGRESS", "ON_THE_WAY"}:
        raise ValueError("Assignment must be in progress before it can be completed")

    if current_app.config.get("REQUIRE_AFTER_IMAGE_FOR_COMPLETION", True):
        has_after_work_image = ProblemImage.query.filter_by(problem_id=assignment.problem_id, image_type="AFTER_WORK").first() is not None
        if not has_after_work_image:
            raise ValueError("After-work evidence is required before completing this assignment")

    assignment.status = "COMPLETED"
    assignment.completed_at = datetime.now(timezone.utc)
    assignment.updated_at = datetime.now(timezone.utc)
    if assignment.problem:
        assignment.problem.status = "RESOLVED"
        assignment.problem.resolved_at = assignment.completed_at
        notify_resident(
            assignment.problem,
            "PROBLEM_RESOLVED",
            "Problem resolved",
            "Your reported problem has been marked as resolved.",
            assignment=assignment,
        )
    return {"assignment": {"assignment_id": assignment.id, "status": assignment.status}, "problem_status": assignment.problem.status if assignment.problem else None}


def reject_assignment(assignment_id: int, worker_id: int, rejection_reason: str = "Worker declined the assignment") -> dict[str, Any]:
    assignment = _get_assignment_or_error(assignment_id, worker_id)
    if assignment.status not in {"ASSIGNED", "ACCEPTED", "ON_THE_WAY", "IN_PROGRESS"}:
        raise ValueError("This assignment cannot be rejected in its current state")

    old_status = assignment.status
    assignment.status = "REJECTED"
    assignment.rejected_at = datetime.now(timezone.utc)
    assignment.rejection_reason = rejection_reason
    assignment.updated_at = datetime.now(timezone.utc)

    if assignment.problem:
        old_problem_status = assignment.problem.status
        assignment.problem.status = "PENDING_ASSIGNMENT"
        db.session.add(StatusHistory(
            problem_id=assignment.problem.id,
            old_status=old_problem_status,
            new_status="PENDING_ASSIGNMENT",
            changed_by=worker_id,
            notes=f"Worker rejected assignment: {rejection_reason}",
        ))

    db.session.add(StatusHistory(
        problem_id=assignment.problem_id,
        old_status=old_status,
        new_status="REJECTED",
        changed_by=worker_id,
        notes=rejection_reason,
    ))

    return {
        "assignment": {
            "assignment_id": assignment.id,
            "status": assignment.status,
            "rejection_reason": rejection_reason,
            "rejected_at": assignment.rejected_at.isoformat() if assignment.rejected_at else None,
        },
        "problem_status": assignment.problem.status if assignment.problem else None,
    }
