"""
Health check endpoints.
GET /health                — public system probe
GET /api/health            — public API probe
GET /api/scheduler/status  — admin only
GET /api/metrics           — admin: live system statistics
"""

import os
import time
from datetime import datetime

from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required

from database.factory import get_db
from middleware.auth_middleware import require_role

_START_TIME = time.time()

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    try:
        db = get_db()
        db_health = db.health_check()
        return jsonify({
            "status": "healthy",
            "database": db_health,
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }), 500


@health_bp.route("/api/health", methods=["GET"])
def api_health():
    from flask import current_app
    scheduler = current_app.config.get("_scheduler")
    scheduler_status = (
        "active" if scheduler and getattr(scheduler, "running", False) else "inactive"
    )
    return jsonify({
        "status": "ok",
        "message": "API is running",
        "version": "2.0.0",
        "scheduler": scheduler_status,
        "timestamp": datetime.now().isoformat(),
    })


@health_bp.route("/api/scheduler/status", methods=["GET"])
@jwt_required()
@require_role("admin")
def scheduler_status():
    scheduler = current_app.config.get("_scheduler")
    if not scheduler:
        return jsonify({"success": True, "scheduler": {"running": False, "jobs": []}})

    jobs = [
        {
            "id": j.id,
            "name": j.name,
            "next_run": j.next_run_time.isoformat() if j.next_run_time else None,
        }
        for j in scheduler.get_jobs()
    ]
    return jsonify({
        "success": True,
        "scheduler": {"running": scheduler.running, "jobs": jobs},
    })


@health_bp.route("/api/metrics", methods=["GET"])
@jwt_required()
@require_role("admin")
def system_metrics():
    """
    Live system statistics for monitoring dashboards.

    Returns counts from all core tables, scheduler state, process memory
    usage (if psutil is installed), and uptime.
    """
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")

    def safe_count(fn, *args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            return len(result) if isinstance(result, list) else 0
        except Exception:
            return -1

    # ── DB stats ───────────────────────────────────────────────────────────────
    total_students  = safe_count(db.get_students)
    total_users     = safe_count(db.get_users)
    total_courses   = safe_count(db.get_courses)
    total_rooms     = safe_count(db.get_rooms)
    active_sessions = safe_count(db.get_sessions, status="active")
    today_attendance = safe_count(db.get_attendance_records, date=today)
    flagged_records  = safe_count(db.get_flagged_attendance)

    # ── Scheduler ──────────────────────────────────────────────────────────────
    scheduler = current_app.config.get("_scheduler")
    scheduler_running = bool(scheduler and getattr(scheduler, "running", False))

    # ── Process memory (optional — requires psutil) ────────────────────────────
    memory_mb = None
    try:
        import psutil
        proc = psutil.Process(os.getpid())
        memory_mb = round(proc.memory_info().rss / 1024 / 1024, 1)
    except ImportError:
        pass

    uptime_seconds = int(time.time() - _START_TIME)

    return jsonify({
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime_seconds,
        "database": {
            "students": total_students,
            "users": total_users,
            "courses": total_courses,
            "rooms": total_rooms,
            "active_sessions": active_sessions,
            "attendance_today": today_attendance,
            "flagged_records": flagged_records,
        },
        "scheduler": {
            "running": scheduler_running,
            "job_count": len(scheduler.get_jobs()) if scheduler_running else 0,
        },
        "process": {
            "pid": os.getpid(),
            "memory_mb": memory_mb,
        },
    })
