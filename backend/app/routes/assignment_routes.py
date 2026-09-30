from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Problem, User, Worker
from app.services.assignment_service import (
    accept_assignment,
    assign_problem,
    complete_assignment,
    find_eligible_workers,
    get_worker_assignments,
    rank_workers,
    reject_assignment,
    start_assignment,
    start_travel,
)

assignment_bp = Blueprint("assignment", __name__, url_prefix="/api")


@assignment_bp.route("/assignments/eligible-workers", methods=["POST"])
@jwt_required()
def get_eligible_workers_route():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    problem_id = data.get("problem_id")
    if not problem_id:
        return jsonify({"success": False, "message": "Problem id is required"}), 400

    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        return jsonify({"success": False, "message": "Problem not found"}), 404

    eligible = find_eligible_workers(problem)
    ranked = rank_workers(problem, eligible)
    return jsonify({
        "success": True,
        "problem_id": problem.problem_id,
        "eligible_workers": [{
            "worker_id": item["worker"].worker_id,
            "name": item["worker"].user.name if item["worker"].user else None,
            "score": item["score"],
            "workload_percentage": item["workload_percentage"],
            "capacity_available": item["capacity_available"],
        } for item in ranked],
    }), 200


@assignment_bp.route("/assignments/me", methods=["GET"])
@jwt_required()
def get_my_assignments():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can access their assignments"}), 403

    worker = Worker.query.filter_by(user_id=user.id).first()
    if not worker:
        return jsonify({"success": False, "message": "Worker profile not found"}), 404

    status = request.args.get("status")
    priority = request.args.get("priority")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    result = get_worker_assignments(worker.id, status=status, priority=priority, page=page, per_page=per_page)
    return jsonify({"success": True, **result}), 200


@assignment_bp.route("/assignments/<int:assignment_id>/accept", methods=["POST"])
@jwt_required()
def accept_assignment_route(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can accept assignments"}), 403

    try:
        result = accept_assignment(assignment_id, user.id)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Assignment acceptance failed"}), 500

    return jsonify({"success": True, **result}), 200


@assignment_bp.route("/assignments/<int:assignment_id>/start-travel", methods=["POST"])
@jwt_required()
def start_travel_route(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can update assignment status"}), 403

    try:
        result = start_travel(assignment_id, user.id)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Travel start update failed"}), 500

    return jsonify({"success": True, **result}), 200


@assignment_bp.route("/assignments/<int:assignment_id>/start-work", methods=["POST"])
@jwt_required()
def start_work_route(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can start work"}), 403

    try:
        result = start_assignment(assignment_id, user.id)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Work start update failed"}), 500

    return jsonify({"success": True, **result}), 200


@assignment_bp.route("/assignments/<int:assignment_id>/complete", methods=["POST"])
@jwt_required()
def complete_assignment_route(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can complete assignments"}), 403

    try:
        result = complete_assignment(assignment_id, user.id)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Assignment completion failed"}), 500

    return jsonify({"success": True, **result}), 200


@assignment_bp.route("/assignments/<int:assignment_id>/reject", methods=["POST"])
@jwt_required()
def reject_assignment_route(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can reject assignments"}), 403

    data = request.get_json(silent=True) or {}
    rejection_reason = (data.get("rejection_reason") or "").strip() or "Worker declined the assignment"

    try:
        result = reject_assignment(assignment_id, user.id, rejection_reason=rejection_reason)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Assignment rejection failed"}), 500

    return jsonify({"success": True, **result}), 200


@assignment_bp.route("/problems/<problem_identifier>/assign", methods=["POST"])
@jwt_required()
def assign_problem_route(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    problem = Problem.query.filter_by(problem_id=problem_identifier).first()
    if not problem:
        return jsonify({"success": False, "message": "Problem not found"}), 404

    if user.role not in {"admin", "resident"}:
        return jsonify({"success": False, "message": "Access denied"}), 403

    result = assign_problem(problem.id)
    if not result.get("success"):
        db.session.commit()
        return jsonify({
            "success": False,
            "message": result.get("message", "Assignment failed"),
            "problem_status": result.get("problem_status", problem.status),
        }), 200 if result.get("problem_status") == "PENDING_ASSIGNMENT" else 400

    return jsonify({
        "success": True,
        "message": result.get("message", "Problem assigned successfully"),
        "problem_status": result.get("problem_status", problem.status),
        "assignment": result.get("assignment"),
        "worker": result.get("worker"),
    }), 200
