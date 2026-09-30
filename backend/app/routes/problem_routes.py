import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Category, Problem, StatusHistory, User
from app.services.notification_service import notify_resident

problem_bp = Blueprint("problem", __name__, url_prefix="/api")


def _serialize_problem(problem):
    return {
        "id": problem.id,
        "problem_id": problem.problem_id,
        "resident_id": problem.resident_id,
        "category_id": problem.category_id,
        "title": problem.title,
        "description": problem.description,
        "priority": problem.priority,
        "status": problem.status,
        "location_text": problem.location_text,
        "latitude": float(problem.latitude) if problem.latitude is not None else None,
        "longitude": float(problem.longitude) if problem.longitude is not None else None,
        "image_url": problem.image_url,
        "created_at": problem.created_at.isoformat() if problem.created_at else None,
        "updated_at": problem.updated_at.isoformat() if problem.updated_at else None,
        "resolved_at": problem.resolved_at.isoformat() if problem.resolved_at else None,
        "category_name": problem.category.name if problem.category else None,
        "resident_name": problem.resident.name if problem.resident else None,
    }


@problem_bp.route("/problems", methods=["POST"])
@jwt_required()
def create_problem():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if user.role != "resident":
        return jsonify({"success": False, "message": "Only residents can create problems"}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "message": "Request body is required"}), 400

    category_id = data.get("category_id")
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    priority = (data.get("priority") or "MEDIUM").strip().upper()
    location_text = (data.get("location_text") or "").strip() or None
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    image_url = (data.get("image_url") or "").strip() or None

    if not category_id:
        return jsonify({"success": False, "message": "Category is required"}), 400

    category = Category.query.filter_by(id=category_id, is_active=True).first()
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404

    if not title or len(title) < 5:
        return jsonify({"success": False, "message": "Title must be at least 5 characters long"}), 400

    if len(description) < 5:
        return jsonify({"success": False, "message": "Description must be at least 5 characters long"}), 400

    if priority not in {"LOW", "MEDIUM", "HIGH", "URGENT"}:
        return jsonify({"success": False, "message": "Priority must be LOW, MEDIUM, HIGH, or URGENT"}), 400

    if latitude is not None:
        try:
            latitude_float = float(latitude)
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Latitude must be a valid number"}), 400
        if latitude_float < -90 or latitude_float > 90:
            return jsonify({"success": False, "message": "Latitude must be between -90 and 90"}), 400
    else:
        latitude_float = None

    if longitude is not None:
        try:
            longitude_float = float(longitude)
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Longitude must be a valid number"}), 400
        if longitude_float < -180 or longitude_float > 180:
            return jsonify({"success": False, "message": "Longitude must be between -180 and 180"}), 400
    else:
        longitude_float = None

    problem = Problem(
        problem_id=f"CMP-{uuid.uuid4().hex[:8].upper()}",
        resident_id=user.id,
        category_id=category.id,
        title=title,
        description=description,
        priority=priority,
        status="NEW",
        location_text=location_text,
        latitude=latitude_float,
        longitude=longitude_float,
        image_url=image_url,
    )

    try:
        db.session.add(problem)
        db.session.flush()
        status_history = StatusHistory(
            problem_id=problem.id,
            old_status=None,
            new_status="NEW",
            changed_by=user.id,
            notes="Problem created by resident",
        )
        db.session.add(status_history)
        notify_resident(
            problem,
            "PROBLEM_CREATED",
            "Problem reported",
            f"Your problem {problem.problem_id} has been reported successfully.",
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Problem creation failed"}), 500

    return jsonify({
        "success": True,
        "message": "Problem reported successfully",
        "problem": _serialize_problem(problem),
    }), 201


@problem_bp.route("/problems", methods=["GET"])
@jwt_required()
def list_problems():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if user.role == "admin":
        problems = Problem.query.order_by(Problem.created_at.desc()).all()
    else:
        problems = Problem.query.filter_by(resident_id=user.id).order_by(Problem.created_at.desc()).all()

    return jsonify({
        "success": True,
        "count": len(problems),
        "problems": [_serialize_problem(problem) for problem in problems],
    }), 200


@problem_bp.route("/problems/<problem_identifier>", methods=["GET"])
@jwt_required()
def get_problem(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    problem = Problem.query.filter_by(problem_id=problem_identifier).first()
    if not problem:
        return jsonify({"success": False, "message": "Problem not found"}), 404

    if user.role != "admin" and problem.resident_id != user.id:
        return jsonify({"success": False, "message": "You are not allowed to view this problem"}), 403

    return jsonify({
        "success": True,
        "problem": _serialize_problem(problem),
    }), 200


@problem_bp.route("/problems/<problem_identifier>", methods=["PUT"])
@jwt_required()
def update_problem(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    problem = Problem.query.filter_by(problem_id=problem_identifier).first()
    if not problem:
        return jsonify({"success": False, "message": "Problem not found"}), 404

    if problem.resident_id != user.id:
        return jsonify({"success": False, "message": "You can only update your own problems"}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "message": "Request body is required"}), 400

    if "title" in data and data["title"] is not None:
        title = str(data["title"]).strip()
        if len(title) < 5:
            return jsonify({"success": False, "message": "Title must be at least 5 characters long"}), 400
        problem.title = title

    if "description" in data and data["description"] is not None:
        description = str(data["description"]).strip()
        if len(description) < 5:
            return jsonify({"success": False, "message": "Description must be at least 5 characters long"}), 400
        problem.description = description

    if "priority" in data and data["priority"] is not None:
        priority = str(data["priority"]).strip().upper()
        if priority not in {"LOW", "MEDIUM", "HIGH", "URGENT"}:
            return jsonify({"success": False, "message": "Priority must be LOW, MEDIUM, HIGH, or URGENT"}), 400
        problem.priority = priority

    if "location_text" in data:
        problem.location_text = (str(data["location_text"]) or "").strip() or None

    if "latitude" in data and data["latitude"] is not None:
        try:
            latitude = float(data["latitude"])
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Latitude must be a valid number"}), 400
        if latitude < -90 or latitude > 90:
            return jsonify({"success": False, "message": "Latitude must be between -90 and 90"}), 400
        problem.latitude = latitude

    if "longitude" in data and data["longitude"] is not None:
        try:
            longitude = float(data["longitude"])
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Longitude must be a valid number"}), 400
        if longitude < -180 or longitude > 180:
            return jsonify({"success": False, "message": "Longitude must be between -180 and 180"}), 400
        problem.longitude = longitude

    if "image_url" in data:
        problem.image_url = (str(data["image_url"]) or "").strip() or None

    if "category_id" in data and data["category_id"] is not None:
        category = Category.query.filter_by(id=data["category_id"], is_active=True).first()
        if not category:
            return jsonify({"success": False, "message": "Category not found"}), 404
        problem.category_id = category.id

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Problem update failed"}), 500

    return jsonify({
        "success": True,
        "message": "Problem updated successfully",
        "problem": _serialize_problem(problem),
    }), 200


@problem_bp.route("/problems/<problem_identifier>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_problem(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    problem = Problem.query.filter_by(problem_id=problem_identifier).first()
    if not problem:
        return jsonify({"success": False, "message": "Problem not found"}), 404

    if problem.resident_id != user.id:
        return jsonify({"success": False, "message": "You can only cancel your own problems"}), 403

    if problem.status == "CANCELLED":
        return jsonify({"success": False, "message": "Problem is already cancelled"}), 400

    old_status = problem.status
    problem.status = "CANCELLED"
    status_history = StatusHistory(
        problem_id=problem.id,
        old_status=old_status,
        new_status="CANCELLED",
        changed_by=user.id,
        notes="Problem cancelled by resident",
    )

    try:
        db.session.add(status_history)
        notify_resident(
            problem,
            "PROBLEM_CANCELLED",
            "Problem cancelled",
            "Your reported problem has been cancelled.",
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Problem cancellation failed"}), 500

    return jsonify({
        "success": True,
        "message": "Problem cancelled successfully",
        "problem": _serialize_problem(problem),
    }), 200


@problem_bp.route("/categories", methods=["GET"])
@jwt_required()
def list_categories():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    categories = Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()
    return jsonify({
        "success": True,
        "count": len(categories),
        "categories": [{
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active,
        } for category in categories],
    }), 200
