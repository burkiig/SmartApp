"""
Smart Attendance System — Flask Application Factory

Entry points:
    Development:   python app.py
    Production:    gunicorn -c gunicorn.conf.py "app:create_app()"
"""

import os
from flask import Flask, send_from_directory, jsonify

from config import Config
from extensions import init_extensions
from middleware.error_handler import register_error_handlers

# ── Blueprints ─────────────────────────────────────────────────────────────────
from routes.health import health_bp
from routes.auth import auth_bp
from routes.students import students_bp
from routes.courses import courses_bp
from routes.sessions import sessions_bp
from routes.excuses import excuses_bp
from routes.attendance import attendance_bp
from routes.dashboard import dashboard_bp


def create_app(config_class=Config):
    """
    Application factory.

    Args:
        config_class: A Config subclass (DevelopmentConfig, ProductionConfig,
                      TestingConfig).  Defaults to the base Config which reads
                      from environment variables.

    Returns:
        Configured Flask application instance.
    """
    config_class.validate_production()

    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    # ── Extensions ─────────────────────────────────────────────────────────────
    init_extensions(app)

    # ── Device binding middleware ───────────────────────────────────────────────
    from middleware.device_middleware import init_device_middleware
    init_device_middleware(app)

    # ── Blueprints ─────────────────────────────────────────────────────────────
    for bp in (
        health_bp,
        auth_bp,
        students_bp,
        courses_bp,
        sessions_bp,
        excuses_bp,
        attendance_bp,
        dashboard_bp,
    ):
        app.register_blueprint(bp)

    # ── Error handlers ─────────────────────────────────────────────────────────
    register_error_handlers(app)

    # ── Static directories ─────────────────────────────────────────────────────
    os.makedirs("static/faces", exist_ok=True)
    os.makedirs("static/attendance", exist_ok=True)

    # ── Seed default users (once) ──────────────────────────────────────────────
    with app.app_context():
        _seed_default_users()

    # ── Background scheduler ───────────────────────────────────────────────────
    from scheduler.session_scheduler import start_scheduler
    scheduler = start_scheduler(app)
    app.config["_scheduler"] = scheduler

    # ── Serve React web panel (SPA fallback) ───────────────────────────────────
    react_build = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web-panel", "build")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path):
        if not os.path.exists(react_build):
            return jsonify({
                "message": "Web panel not built. Run: cd web-panel && npm run build",
            }), 404
        if path.startswith("static/") or (path and os.path.exists(os.path.join(react_build, path))):
            return send_from_directory(react_build, path)
        return send_from_directory(react_build, "index.html")

    return app


# ── Default user seeding ───────────────────────────────────────────────────────

def _seed_default_users():
    """
    Ensure default demo users exist in the database.
    Runs once inside app context at startup.
    Safe to call multiple times (idempotent).
    """
    from database.factory import get_db
    from utils.security import hash_password
    from shared.logger import get_logger

    log = get_logger()
    defaults = [
        {"username": "admin",           "password": "admin123",  "role": "admin",       "name": "System Administrator",   "email": "admin@attendance.com"},
        {"username": "instructor1",     "password": "pass123",   "role": "instructor",  "name": "Dr. Robert Chen",        "email": "robert.chen@university.edu",  "department": "Computer Science"},
        {"username": "instructor_demo", "password": "demo123",   "role": "instructor",  "name": "Dr. Demo Instructor",    "email": "instructor@demo.com",         "department": "Computer Science"},
        {"username": "student1",        "password": "pass123",   "role": "student",     "name": "John Doe",               "email": "john.doe@student.edu",        "student_id": "2021001"},
        {"username": "student_demo",    "password": "demo123",   "role": "student",     "name": "Demo Student",           "email": "student@demo.com",            "student_id": "DEMO001"},
    ]

    try:
        db = get_db()
        for u in defaults:
            if not db.get_user(u["username"]):
                u["password"] = hash_password(u["password"])
                db.create_user(u)
                log.info(f"[Seed] Created user: {u['username']}")
    except Exception as e:
        get_logger().warning(f"[Seed] Could not seed users: {e}")


# ── Dev server entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    from shared.logger import setup_logger
    log = setup_logger("smart_attendance")

    app = create_app()
    log.info("Smart Attendance System v2.0 starting…")
    log.info(f"DB driver: {os.getenv('DB_DRIVER', 'json')}")

    app.run(
        debug=app.config.get("DEBUG", True),
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5000),
    )
