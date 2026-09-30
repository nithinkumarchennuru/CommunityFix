from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Notification, User
from app.services.notification_service import get_unread_count, get_user_notifications, mark_all_as_read, mark_as_read

notification_bp = Blueprint("notification", __name__, url_prefix="/api")


@notification_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    unread_only = request.args.get("unread", default="false").lower() == "true"
    notification_type = request.args.get("type")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    result = get_user_notifications(
        user_id=user.id,
        unread_only=unread_only,
        notification_type=notification_type,
        page=page,
        per_page=per_page,
    )
    return jsonify({"success": True, **result}), 200


@notification_bp.route("/notifications/<int:notification_id>", methods=["GET"])
@jwt_required()
def get_notification(notification_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not notification:
        return jsonify({"success": False, "message": "Notification not found"}), 404

    return jsonify({
        "success": True,
        "notification": {
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "problem_id": notification.problem.problem_id if notification.problem else None,
            "assignment_id": notification.assignment_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
        },
    }), 200


@notification_bp.route("/notifications/<int:notification_id>/read", methods=["PATCH"])
@jwt_required()
def read_notification(notification_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    notification = mark_as_read(notification_id, user.id)
    if not notification:
        return jsonify({"success": False, "message": "Notification not found"}), 404

    db.session.commit()
    return jsonify({
        "success": True,
        "notification": {
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "problem_id": notification.problem.problem_id if notification.problem else None,
            "assignment_id": notification.assignment_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
        },
    }), 200


@notification_bp.route("/notifications/read-all", methods=["PATCH"])
@jwt_required()
def read_all_notifications():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    count = mark_all_as_read(user.id)
    db.session.commit()
    return jsonify({"success": True, "updated_count": count}), 200


@notification_bp.route("/notifications/unread-count", methods=["GET"])
@jwt_required()
def unread_notification_count():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({"success": True, "unread_count": get_unread_count(user.id)}), 200
