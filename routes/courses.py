"""
Course and Room routes — all data flows through DB adapter (no JSON file I/O here).
GET    /api/courses             — list courses
POST   /api/courses             — create course (admin/instructor)
DELETE /api/courses/<id>        — delete course (admin)
GET    /api/rooms               — list rooms
POST   /api/rooms               — create room (admin)
DELETE /api/rooms/<id>          — delete room (admin)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from database.factory import get_db
from middleware.auth_middleware import require_role
from shared.logger import get_logger

log = get_logger()
courses_bp = Blueprint("courses", __name__, url_prefix="/api")


# ── Courses ────────────────────────────────────────────────────────────────────

@courses_bp.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():
    db = get_db()
    courses = db.get_courses()
    return jsonify({"success": True, "courses": courses or []})


@courses_bp.route("/courses", methods=["POST"])
@jwt_required()
@require_role("admin", "instructor")
def add_course():
    data = request.get_json() or {}
    if not data.get("code") or not data.get("name"):
        return jsonify({"success": False, "message": "code ve name gerekli"}), 400

    db = get_db()
    course = db.create_course({
        "code": data["code"],
        "name": data["name"],
        "instructor": data.get("instructor"),
        "schedule": data.get("schedule"),
        "room": data.get("room"),
        "room_id": data.get("room_id"),
        "enrolled_students": data.get("enrolled_students", []),
    })
    log.info(f"[Courses] Created: {data['code']}")
    return jsonify({"success": True, "message": "Ders oluşturuldu", "course": course})


@courses_bp.route("/courses/<int:course_id>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_course(course_id):
    db = get_db()
    db.delete_course(course_id)
    log.info(f"[Courses] Deleted: {course_id}")
    return jsonify({"success": True, "message": "Ders silindi"})


# ── Rooms ──────────────────────────────────────────────────────────────────────

@courses_bp.route("/rooms", methods=["GET"])
@jwt_required()
def get_rooms():
    db = get_db()
    rooms = db.get_rooms()
    return jsonify({"success": True, "rooms": rooms or []})


@courses_bp.route("/rooms", methods=["POST"])
@jwt_required()
@require_role("admin")
def add_room():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"success": False, "message": "name gerekli"}), 400

    db = get_db()
    room = db.create_room({
        "name": data["name"],
        "capacity": data.get("capacity"),
        "type": data.get("type"),
        "equipment": data.get("equipment"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "geofence_radius": data.get("geofence_radius", 40),
        "status": "available",
    })
    log.info(f"[Rooms] Created: {data['name']}")
    return jsonify({"success": True, "message": "Sınıf oluşturuldu", "room": room})


@courses_bp.route("/rooms/<int:room_id>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_room(room_id):
    db = get_db()
    db.delete_room(room_id)
    log.info(f"[Rooms] Deleted: {room_id}")
    return jsonify({"success": True, "message": "Sınıf silindi"})
