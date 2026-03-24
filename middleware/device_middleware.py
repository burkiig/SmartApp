"""
Device Binding Middleware — X-Device-ID enforcement.

Every student request MUST include an X-Device-ID header.
On first use the device is auto-registered; on subsequent requests
the header must match an active device for that user.

Usage (in create_app):
    from middleware.device_middleware import init_device_middleware
    init_device_middleware(app)

Clients (mobile app) must send:
    X-Device-ID: <unique-device-identifier>   (e.g. Expo.Constants.deviceId)
    X-Device-Platform: ios | android          (optional, for analytics)

Only 'student' role requests are enforced. Admin/instructor are exempt.
"""

from flask import request, jsonify, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from shared.logger import get_logger

log = get_logger()

EXEMPT_ENDPOINTS = {
    "health.health_check",
    "health.api_health",
    "auth.login",
    "auth.refresh_token",
}

MAX_DEVICES_PER_USER = 3


def init_device_middleware(app):
    """Register the before_request hook on the Flask app."""

    @app.before_request
    def check_device_binding():
        # Skip OPTIONS (CORS pre-flight) and exempt public endpoints
        if request.method == "OPTIONS":
            return
        if request.endpoint in EXEMPT_ENDPOINTS:
            return

        # Only enforce on authenticated student routes
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
        except Exception:
            return  # JWT errors are handled by route decorators

        if not identity or identity.get("role") != "student":
            return

        device_id = request.headers.get("X-Device-ID", "").strip()
        if not device_id:
            log.warning(f"[Device] Missing X-Device-ID for user {identity.get('username')}")
            return jsonify({
                "success": False,
                "message": "X-Device-ID header zorunludur.",
                "code": "MISSING_DEVICE_ID",
            }), 400

        username = identity.get("username")
        platform = request.headers.get("X-Device-Platform", "unknown")

        try:
            from database.factory import get_db
            db = get_db()

            existing = db.get_device(username, device_id)
            if existing:
                # Known device — update last_seen silently
                g.device_id = device_id
                return

            # New device — check cap before registering
            all_devices = db.get_devices_for_user(username)
            if len(all_devices) >= MAX_DEVICES_PER_USER:
                log.warning(
                    f"[Device] User {username} exceeded device cap "
                    f"({MAX_DEVICES_PER_USER}). Rejected device: {device_id[:8]}…"
                )
                return jsonify({
                    "success": False,
                    "message": (
                        f"Maksimum {MAX_DEVICES_PER_USER} cihaz kaydına ulaşıldı. "
                        "Eski cihazı kaldırarak yeniden deneyin."
                    ),
                    "code": "DEVICE_LIMIT_EXCEEDED",
                }), 403

            db.register_device(username, device_id, platform)
            g.device_id = device_id
            log.info(f"[Device] Registered new device for {username}: {device_id[:8]}… ({platform})")

        except Exception as e:
            log.error(f"[Device] Device check failed for {username}: {e}")
            # Fail open — don't block the request on internal DB errors
