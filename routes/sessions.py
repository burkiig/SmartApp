"""
Attendance session + class cancellation routes.
GET  /api/sessions               — list sessions
POST /api/sessions               — create session (admin/instructor)
GET  /api/sessions/active        — active sessions
GET  /api/sessions/<id>          — session detail
POST /api/sessions/<id>/close    — close session (admin/instructor)
GET  /api/classes/upcoming       — upcoming classes
POST /api/classes/cancel         — cancel class (instructor/admin)
GET  /api/cancellations          — list cancellations
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from database.factory import get_db
from middleware.auth_middleware import require_role
from shared.errors import ValidationError
from shared.logger import get_logger

log = get_logger()
sessions_bp = Blueprint("sessions", __name__, url_prefix="/api")


# ── Sessions ───────────────────────────────────────────────────────────────────

@sessions_bp.route("/sessions", methods=["GET"])
@jwt_required()
def get_sessions():
    db = get_db()
    course_id = request.args.get("course_id", type=int)
    status = request.args.get("status")
    sessions = db.get_sessions(course_id=course_id, status=status)
    return jsonify({"success": True, "sessions": sessions or []})


@sessions_bp.route("/sessions/active", methods=["GET"])
@jwt_required()
def get_active_sessions():
    db = get_db()
    sessions = db.get_sessions(status="active")
    return jsonify({"success": True, "sessions": sessions or []})


@sessions_bp.route("/sessions/<session_id>", methods=["GET"])
@jwt_required()
def get_session(session_id):
    db = get_db()
    session = db.get_session(session_id)
    if not session:
        return jsonify({"success": False, "message": "Oturum bulunamadı"}), 404
    return jsonify({"success": True, "session": session})


@sessions_bp.route("/sessions", methods=["POST"])
@jwt_required()
@require_role("admin", "instructor")
def create_session():
    data = request.get_json() or {}
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"success": False, "message": "course_id gerekli"}), 400

    db = get_db()
    session_data = {
        "course_id": course_id,
        "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "start_time": data.get("start_time", datetime.now().strftime("%H:%M")),
        "end_time": data.get("end_time"),
    }
    created = db.create_session(session_data)
    log.info(f"[Sessions] Created for course {course_id}: {created['id']}")
    return jsonify({"success": True, "session": created}), 201


@sessions_bp.route("/sessions/<session_id>/close", methods=["POST"])
@jwt_required()
@require_role("admin", "instructor")
def close_session(session_id):
    db = get_db()
    try:
        updated = db.update_session(session_id, {
            "status": "closed",
            "end_time": datetime.now().strftime("%H:%M"),
        })
        log.info(f"[Sessions] Closed: {session_id}")
        return jsonify({"success": True, "session": updated})
    except ValueError:
        return jsonify({"success": False, "message": "Oturum bulunamadı"}), 404


# ── Classes ────────────────────────────────────────────────────────────────────

@sessions_bp.route("/classes/upcoming", methods=["GET"])
@jwt_required()
def get_upcoming_classes():
    """
    Returns upcoming class sessions.
    TODO: Replace mock data with a real query against course_schedule once
          the schedule table is populated.
    """
    from datetime import timedelta
    today = datetime.now()
    upcoming = [
        {
            "id": 1,
            "course": "CS101",
            "title": "Introduction to Programming",
            "date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "09:00 - 10:30",
            "room": "Room 401",
            "status": "scheduled",
            "students_enrolled": 45,
        },
    ]
    return jsonify({"success": True, "classes": upcoming})


@sessions_bp.route("/classes/cancel", methods=["POST"])
@jwt_required()
@require_role("instructor", "admin")
def cancel_class():
    data = request.get_json() or {}
    class_id = data.get("class_id")
    reason = data.get("reason")
    instructor_id = data.get("instructor_id")

    if not all([class_id, reason, instructor_id]):
        raise ValidationError("class_id, reason ve instructor_id gerekli")

    db = get_db()
    cancellation_data = {
        "course_id": class_id,
        "instructor_id": instructor_id,
        "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "reason": reason,
    }
    created = db.create_cancellation(cancellation_data)

    # Close any active sessions for this course
    active = db.get_sessions(course_id=class_id, status="active")
    for s in active:
        db.update_session(s["id"], {"status": "cancelled"})

    # Resolve course code for push notification
    course = db.get_course(class_id)
    course_code = course.get("code", str(class_id)) if course else str(class_id)

    # Fire-and-forget push notification
    try:
        from services.push_service import notify_class_cancelled
        notify_class_cancelled(class_id, course_code, reason)
    except Exception as e:
        log.warning(f"[Sessions] Push notification failed: {e}")

    log.info(f"[Sessions] Class {class_id} cancelled by {instructor_id}")
    return jsonify({
        "success": True,
        "message": "Ders başarıyla iptal edildi",
        "cancellation": created,
    })


# ── Cancellations ──────────────────────────────────────────────────────────────

@sessions_bp.route("/cancellations", methods=["GET"])
@jwt_required()
def get_cancellations():
    db = get_db()
    course_id = request.args.get("course_id", type=int)
    cancellations = db.get_cancellations(course_id=course_id)
    return jsonify({"success": True, "cancellations": cancellations or []})
