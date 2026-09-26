from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")

            if role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": "You do not have permission to access this resource",
                }), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator
