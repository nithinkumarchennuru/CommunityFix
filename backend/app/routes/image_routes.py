from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Assignment, Problem, ProblemImage, User, Worker
from app.services import storage_service
from app.services.notification_service import notify_admins, notify_resident, notify_worker
from app.services.storage_service import get_image_limit_for_type, validate_image

image_bp = Blueprint("image", __name__, url_prefix="/api")


def _get_problem_or_404(problem_identifier):
    problem = Problem.query.filter_by(problem_id=problem_identifier).first()
    if not problem:
        raise ValueError("Problem not found")
    return problem


def _get_assignment_or_404(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        raise ValueError("Assignment not found")
    return assignment


def _can_access_problem_images(user: User, problem: Problem) -> bool:
    if user.role == "admin":
        return True
    if user.role == "resident":
        return problem.resident_id == user.id
    if user.role == "worker":
        worker = Worker.query.filter_by(user_id=user.id).first()
        if not worker:
            return False
        return Assignment.query.filter_by(problem_id=problem.id, worker_id=worker.id).first() is not None
    return False


def _image_type_limit(image_type: str):
    return get_image_limit_for_type(image_type)


@image_bp.route("/problems/<problem_identifier>/images", methods=["POST"])
@jwt_required()
def upload_problem_image(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    try:
        problem = _get_problem_or_404(problem_identifier)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    if user.role != "resident":
        return jsonify({"success": False, "message": "Only residents can upload problem images"}), 403
    if problem.resident_id != user.id:
        return jsonify({"success": False, "message": "You can only upload images to your own problem"}), 403
    if problem.status == "CANCELLED":
        return jsonify({"success": False, "message": "Cancelled problem cannot receive new images"}), 400

    file = request.files.get("file")
    if file is None or file.filename in (None, ""):
        return jsonify({"success": False, "message": "Image file is required"}), 400

    try:
        validate_image(file)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    existing_count = ProblemImage.query.filter_by(problem_id=problem.id, image_type="PROBLEM").count()
    if existing_count >= _image_type_limit("PROBLEM"):
        return jsonify({"success": False, "message": "Maximum problem images reached"}), 400

    try:
        result = storage_service.upload_image(file, "communityfix/problems")
        image = ProblemImage(
            problem_id=problem.id,
            uploaded_by=user.id,
            image_url=result["url"],
            storage_id=result["storage_id"],
            image_type="PROBLEM",
        )
        db.session.add(image)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Problem image upload failed"}), 500

    notify_admins(
        "PROBLEM_IMAGE_UPLOADED",
        "Problem evidence uploaded",
        f"A resident uploaded image evidence for problem {problem.problem_id}.",
        problem=problem,
    )
    db.session.commit()

    return jsonify({
        "success": True,
        "image": {
            "id": image.id,
            "problem_id": problem.problem_id,
            "image_url": image.image_url,
            "image_type": image.image_type,
            "created_at": image.created_at.isoformat() if image.created_at else None,
        },
    }), 200


@image_bp.route("/assignments/<int:assignment_id>/before-image", methods=["POST"])
@jwt_required()
def upload_before_image(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can upload before-work images"}), 403

    try:
        assignment = _get_assignment_or_404(assignment_id)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    worker = Worker.query.filter_by(user_id=user.id).first()
    if not worker or assignment.worker_id != worker.id:
        return jsonify({"success": False, "message": "You can only upload before-work images for your own assignment"}), 403

    file = request.files.get("file")
    if file is None or file.filename in (None, ""):
        return jsonify({"success": False, "message": "Image file is required"}), 400

    try:
        validate_image(file)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    existing_count = ProblemImage.query.filter_by(problem_id=assignment.problem_id, image_type="BEFORE_WORK").count()
    if existing_count >= _image_type_limit("BEFORE_WORK"):
        return jsonify({"success": False, "message": "Maximum before-work images reached"}), 400

    try:
        result = storage_service.upload_image(file, "communityfix/before-work")
        image = ProblemImage(
            problem_id=assignment.problem_id,
            uploaded_by=user.id,
            image_url=result["url"],
            storage_id=result["storage_id"],
            image_type="BEFORE_WORK",
        )
        db.session.add(image)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Before-work image upload failed"}), 500

    if assignment.problem:
        notify_resident(
            assignment.problem,
            "BEFORE_WORK_IMAGE_UPLOADED",
            "Before-work evidence uploaded",
            "The assigned worker uploaded evidence before starting the repair.",
            assignment=assignment,
        )
        db.session.commit()

    return jsonify({
        "success": True,
        "image": {
            "id": image.id,
            "problem_id": assignment.problem_id,
            "image_url": image.image_url,
            "image_type": image.image_type,
            "created_at": image.created_at.isoformat() if image.created_at else None,
        },
    }), 200


@image_bp.route("/assignments/<int:assignment_id>/after-image", methods=["POST"])
@jwt_required()
def upload_after_image(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.role != "worker":
        return jsonify({"success": False, "message": "Only workers can upload after-work images"}), 403

    try:
        assignment = _get_assignment_or_404(assignment_id)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    worker = Worker.query.filter_by(user_id=user.id).first()
    if not worker or assignment.worker_id != worker.id:
        return jsonify({"success": False, "message": "You can only upload after-work images for your own assignment"}), 403

    file = request.files.get("file")
    if file is None or file.filename in (None, ""):
        return jsonify({"success": False, "message": "Image file is required"}), 400

    try:
        validate_image(file)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    existing_count = ProblemImage.query.filter_by(problem_id=assignment.problem_id, image_type="AFTER_WORK").count()
    if existing_count >= _image_type_limit("AFTER_WORK"):
        return jsonify({"success": False, "message": "Maximum after-work images reached"}), 400

    try:
        result = storage_service.upload_image(file, "communityfix/after-work")
        image = ProblemImage(
            problem_id=assignment.problem_id,
            uploaded_by=user.id,
            image_url=result["url"],
            storage_id=result["storage_id"],
            image_type="AFTER_WORK",
        )
        db.session.add(image)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "After-work image upload failed"}), 500

    if assignment.problem:
        notify_resident(
            assignment.problem,
            "AFTER_WORK_IMAGE_UPLOADED",
            "After-work evidence uploaded",
            "The worker uploaded final evidence for the completed repair.",
            assignment=assignment,
        )
        db.session.commit()

    return jsonify({
        "success": True,
        "image": {
            "id": image.id,
            "problem_id": assignment.problem_id,
            "image_url": image.image_url,
            "image_type": image.image_type,
            "created_at": image.created_at.isoformat() if image.created_at else None,
        },
    }), 200


@image_bp.route("/problems/<problem_identifier>/images", methods=["GET"])
@jwt_required()
def list_problem_images(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    try:
        problem = _get_problem_or_404(problem_identifier)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    image_type = request.args.get("image_type")
    if image_type and image_type.upper() not in {"PROBLEM", "BEFORE_WORK", "AFTER_WORK"}:
        return jsonify({"success": False, "message": "Invalid image type filter"}), 400

    if not _can_access_problem_images(user, problem):
        return jsonify({"success": False, "message": "You are not authorized to view these images"}), 403

    query = ProblemImage.query.filter_by(problem_id=problem.id)
    if image_type:
        query = query.filter_by(image_type=image_type.upper())

    images = query.order_by(ProblemImage.created_at.desc()).all()
    return jsonify({
        "success": True,
        "problem_id": problem.problem_id,
        "images": [{
            "id": item.id,
            "problem_id": item.problem_id,
            "uploaded_by": item.uploaded_by,
            "image_url": item.image_url,
            "image_type": item.image_type,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        } for item in images],
    }), 200


@image_bp.route("/problems/<problem_identifier>/images/<int:image_id>", methods=["DELETE"])
@jwt_required()
def delete_problem_image(problem_identifier, image_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    try:
        problem = _get_problem_or_404(problem_identifier)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    image = ProblemImage.query.filter_by(id=image_id, problem_id=problem.id).first()
    if not image:
        return jsonify({"success": False, "message": "Image not found for this problem"}), 404

    if user.role == "admin":
        pass
    elif user.role == "resident" and problem.resident_id == user.id:
        pass
    elif user.role == "worker":
        worker = Worker.query.filter_by(user_id=user.id).first()
        if not worker or image.uploaded_by != user.id:
            return jsonify({"success": False, "message": "You do not have permission to delete this image"}), 403
    else:
        return jsonify({"success": False, "message": "You do not have permission to delete this image"}), 403

    try:
        storage_service.delete_image(image.storage_id)
    except Exception:
        pass

    try:
        db.session.delete(image)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Image deletion failed"}), 500

    return jsonify({"success": True, "message": "Image deleted successfully"}), 200


@image_bp.route("/problems/<problem_identifier>/confirm", methods=["POST"])
@jwt_required()
def confirm_problem(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    try:
        problem = _get_problem_or_404(problem_identifier)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    if problem.resident_id != user.id:
        return jsonify({"success": False, "message": "Only the problem owner can confirm it"}), 403
    if problem.status != "RESOLVED":
        return jsonify({"success": False, "message": "Only resolved problems can be confirmed"}), 400

    problem.status = "RESIDENT_CONFIRMED"
    db.session.add(problem)
    db.session.commit()
    notify_resident(problem, "PROBLEM_CONFIRMED", "Problem confirmed", "You confirmed the resolution for this problem.")
    notify_admins("PROBLEM_CONFIRMED", "Problem confirmed", f"Resident confirmed problem {problem.problem_id}.", problem=problem)
    db.session.commit()

    return jsonify({"success": True, "problem_id": problem.problem_id, "status": problem.status}), 200


@image_bp.route("/problems/<problem_identifier>/reopen", methods=["POST"])
@jwt_required()
def reopen_problem(problem_identifier):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    try:
        problem = _get_problem_or_404(problem_identifier)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    if problem.resident_id != user.id:
        return jsonify({"success": False, "message": "Only the problem owner can reopen it"}), 403
    if problem.status not in {"RESOLVED", "RESIDENT_CONFIRMED"}:
        return jsonify({"success": False, "message": "Only resolved or confirmed problems can be reopened"}), 400

    data = request.get_json(silent=True) or {}
    reason = (data.get("reason") or "").strip()
    if not reason:
        return jsonify({"success": False, "message": "A reopen reason is required"}), 400

    old_status = problem.status
    problem.status = "REOPENED"
    db.session.add(problem)
    db.session.commit()
    notify_resident(problem, "PROBLEM_REOPENED", "Problem reopened", f"You reopened the problem: {reason}")
    notify_admins("PROBLEM_REOPENED", "Problem reopened", f"Resident reopened problem {problem.problem_id}: {reason}", problem=problem)
    if problem.assignments:
        assignment = problem.assignments[-1]
        if assignment.worker and assignment.worker.user:
            notify_worker(assignment.worker, "PROBLEM_REOPENED", "Problem reopened", f"Problem {problem.problem_id} was reopened: {reason}", problem=problem, assignment=assignment)
    db.session.commit()

    return jsonify({"success": True, "problem_id": problem.problem_id, "status": problem.status, "reason": reason}), 200
