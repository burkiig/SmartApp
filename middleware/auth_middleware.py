"""
Auth middleware — role-based access control decorator.

Usage:
    @jwt_required()
    @require_role('admin')
    def admin_only_view(): ...

    @jwt_required()
    @require_role('admin', 'instructor')
    def admin_or_instructor_view(): ...

JWT identity format (set in routes/auth.py login endpoint):
    {"username": str, "role": str}
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from shared.logger import get_logger

log = get_logger()


def require_role(*allowed_roles: str):
    """
    Decorator that enforces role-based access control.
    Must be placed AFTER @jwt_required().

    Args:
        *allowed_roles: One or more role strings, e.g. 'admin', 'instructor', 'student'
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity:
                return jsonify({"success": False, "message": "Kimlik doğrulanamadı"}), 401

            role = identity.get("role") if isinstance(identity, dict) else None
            if role not in allowed_roles:
                log.warning(
                    f"[Auth] Access denied: role='{role}' tried to access "
                    f"endpoint requiring {allowed_roles}"
                )
                return jsonify({
                    "success": False,
                    "message": f"Bu işlem için yetkiniz yok. Gerekli rol: {', '.join(allowed_roles)}",
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
