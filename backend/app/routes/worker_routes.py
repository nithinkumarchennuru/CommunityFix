from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Category, User, Worker, WorkerSkill
from app.services.worker_service import (
    VALID_AVAILABILITY_STATUSES,
    add_worker_skill,
    calculate_workload,
    create_worker,
    get_worker_by_public_id,
    get_worker_by_user_id,
    get_workers,
    remove_worker_skill,
    serialize_worker,
    update_worker_availability,
    update_worker_capacity,
)
from app.utils.decorators import roles_required

worker_bp = Blueprint("worker", __name__, url_prefix="/api")


def _get_authenticated_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


def _allowed_worker_access(user, worker):
    return user.role == "admin" or worker.user_id == user.id


@worker_bp.route("/workers", methods=["POST"])
@jwt_required()
@roles_required("admin")
def create_worker_route():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "message": "Request body is required"}), 400

    try:
        worker = create_worker(data)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Worker creation failed"}), 500

    result = {
        "success": True,
        "message": "Worker created successfully",
        "worker": {
            "worker_id": worker.worker_id,
            "name": worker.user.name,
            "email": worker.user.email,
            "role": worker.user.role,
            "availability_status": worker.availability_status,
            "maximum_capacity": worker.maximum_capacity,
            "current_active_jobs": worker.current_active_jobs,
        },
    }
    return jsonify(result), 201


@worker_bp.route("/workers", methods=["GET"])
@jwt_required()
@roles_required("admin")
def list_workers():
    filters = {}
    availability_status = request.args.get("availability_status")
    category_id = request.args.get("category_id")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    if availability_status:
        availability_status = availability_status.strip().upper()
        if availability_status not in {"AVAILABLE", "BUSY", "OFFLINE"}:
            return jsonify({"success": False, "message": "Invalid availability status"}), 400
        filters["availability_status"] = availability_status

    if category_id:
        try:
            filters["category_id"] = int(category_id)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid category id"}), 400

    result = get_workers(filters=filters, page=page, per_page=per_page)
    return jsonify({"success": True, **result}), 200


@worker_bp.route("/workers/me", methods=["GET"])
@jwt_required()
@roles_required("worker")
def my_worker_profile():
    user = _get_authenticated_user()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    worker = get_worker_by_user_id(user.id)
    if not worker:
        return jsonify({"success": False, "message": "Worker profile not found"}), 404

    return jsonify({"success": True, "worker": serialize_worker(worker)}), 200


@worker_bp.route("/workers/me/skills", methods=["GET"])
@jwt_required()
@roles_required("worker")
def my_worker_skills():
    user = _get_authenticated_user()
    worker = get_worker_by_user_id(user.id)
    if not worker:
        return jsonify({"success": False, "message": "Worker profile not found"}), 404

    skills = [
        {"id": skill.id, "category_id": skill.category_id, "name": skill.category.name}
        for skill in sorted(worker.skills, key=lambda item: item.category.name.lower())
        if skill.category is not None
    ]
    return jsonify({"success": True, "skills": skills}), 200


@worker_bp.route("/workers/me/skills", methods=["POST"])
@jwt_required()
@roles_required("worker")
def add_my_skill():
    user = _get_authenticated_user()
    worker = get_worker_by_user_id(user.id)
    if not worker:
        return jsonify({"success": False, "message": "Worker profile not found"}), 404

    data = request.get_json(silent=True) or {}
    category_id = data.get("category_id")

    try:
        skill = add_worker_skill(worker, category_id)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Skill creation failed"}), 500

    return jsonify({
        "success": True,
        "message": "Skill added successfully",
        "skill": {
            "id": skill.id,
            "category_id": skill.category_id,
            "name": skill.category.name,
        },
    }), 201


@worker_bp.route("/workers/me/skills/<int:skill_id>", methods=["DELETE"])
@jwt_required()
@roles_required("worker")
def remove_my_skill(skill_id):
    user = _get_authenticated_user()
    worker = get_worker_by_user_id(user.id)
    if not worker:
        return jsonify({"success": False, "message": "Worker profile not found"}), 404

    try:
        remove_worker_skill(worker, skill_id)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Skill removal failed"}), 500

    return jsonify({"success": True, "message": "Skill removed successfully"}), 200


@worker_bp.route("/workers/me/availability", methods=["PUT"])
@jwt_required()
@roles_required("worker")
def update_my_availability():
    user = _get_authenticated_user()
    worker = get_worker_by_user_id(user.id)
    if not worker:
        return jsonify({"success": False, "message": "Worker profile not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("availability_status")
    if not status:
        return jsonify({"success": False, "message": "Availability status is required"}), 400

    try:
        new_status = update_worker_availability(worker, status)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Availability update failed"}), 500

    return jsonify({
        "success": True,
        "message": "Availability updated successfully",
        "availability_status": new_status,
    }), 200


@worker_bp.route("/workers/me/workload", methods=["GET"])
@jwt_required()
@roles_required("worker")
def worker_workload():
    user = _get_authenticated_user()
    worker = get_worker_by_user_id(user.id)
    if not worker:
        return jsonify({"success": False, "message": "Worker profile not found"}), 404

    workload = calculate_workload(worker.current_active_jobs, worker.maximum_capacity)
    return jsonify({"success": True, "workload": workload}), 200


@worker_bp.route("/workers/<worker_identifier>", methods=["GET"])
@jwt_required()
def get_worker_by_id(worker_identifier):
    user = _get_authenticated_user()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    worker = get_worker_by_public_id(worker_identifier)
    if not worker:
        return jsonify({"success": False, "message": "Worker not found"}), 404

    if user.role == "resident":
        return jsonify({"success": False, "message": "Access denied"}), 403

    if user.role == "worker" and worker.user_id != user.id:
        return jsonify({"success": False, "message": "You can only view your own worker profile"}), 403

    data = {
        "success": True,
        "worker": {
            "worker_id": worker.worker_id,
            "name": worker.user.name,
            "availability_status": worker.availability_status,
            "maximum_capacity": worker.maximum_capacity,
            "current_active_jobs": worker.current_active_jobs,
            "workload_percentage": calculate_workload(worker.current_active_jobs, worker.maximum_capacity)["workload_percentage"],
            "skills": [{"id": skill.id, "name": skill.category.name} for skill in worker.skills if skill.category is not None],
        },
    }
    return jsonify(data), 200


@worker_bp.route("/workers/<worker_identifier>/capacity", methods=["PUT"])
@jwt_required()
@roles_required("admin")
def update_worker_capacity_route(worker_identifier):
    worker = get_worker_by_public_id(worker_identifier)
    if not worker:
        return jsonify({"success": False, "message": "Worker not found"}), 404

    data = request.get_json(silent=True) or {}
    if "maximum_capacity" not in data:
        return jsonify({"success": False, "message": "Maximum capacity is required"}), 400

    try:
        updated = update_worker_capacity(worker, data.get("maximum_capacity"))
        db.session.commit()
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Capacity update failed"}), 500

    return jsonify({
        "success": True,
        "message": "Capacity updated successfully",
        "worker": {
            "worker_id": updated.worker_id,
            "maximum_capacity": updated.maximum_capacity,
            "current_active_jobs": updated.current_active_jobs,
        },
    }), 200
