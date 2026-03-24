"""
Excuse (mazeret) routes.
GET   /api/excuses              — list (student: own, instructor: all)
POST  /api/excuses              — student submits an excuse
GET   /api/excuses/<id>         — excuse detail
PATCH /api/excuses/<id>         — instructor reviews (approve/reject/pending)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from database.factory import get_db
from middleware.auth_middleware import require_role
from shared.logger import get_logger

log = get_logger()
excuses_bp = Blueprint("excuses", __name__, url_prefix="/api")


@excuses_bp.route("/excuses", methods=["GET"])
@jwt_required()
def get_excuses():
    db = get_db()
    student_id = request.args.get("student_id")
    course_id = request.args.get("course_id", type=int)
    excuses = db.get_excuses(student_id=student_id, course_id=course_id)
    return jsonify({"success": True, "excuses": excuses or []})


@excuses_bp.route("/excuses", methods=["POST"])
@jwt_required()
def create_excuse():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    course_id = data.get("course_id")
    session_date = data.get("session_date")

    if not all([student_id, course_id, session_date]):
        return jsonify({
            "success": False,
            "message": "student_id, course_id, session_date gerekli",
        }), 400

    db = get_db()
    excuse_data = {
        "student_id": student_id,
        "course_id": course_id,
        "session_date": session_date,
        "excuse_type": data.get("excuse_type", "other"),
        "description": data.get("description", ""),
        "document_url": data.get("document_url", ""),
        "instructor_notes": "",
    }
    created = db.create_excuse(excuse_data)
    log.info(f"[Excuses] Submitted: student={student_id} course={course_id} date={session_date}")
    return jsonify({"success": True, "excuse": created}), 201


@excuses_bp.route("/excuses/<excuse_id>", methods=["GET"])
@jwt_required()
def get_excuse(excuse_id):
    db = get_db()
    excuse = db.get_excuse(excuse_id)
    if not excuse:
        return jsonify({"success": False, "message": "Mazeret bulunamadı"}), 404
    return jsonify({"success": True, "excuse": excuse})


@excuses_bp.route("/excuses/<excuse_id>", methods=["PATCH"])
@jwt_required()
@require_role("admin", "instructor")
def review_excuse(excuse_id):
    data = request.get_json() or {}
    status = data.get("status")

    if status not in ("approved", "rejected", "pending"):
        return jsonify({
            "success": False,
            "message": "status 'approved', 'rejected' veya 'pending' olmalı",
        }), 400

    db = get_db()
    try:
        updated = db.update_excuse(excuse_id, {
            "status": status,
            "instructor_notes": data.get("instructor_notes", ""),
        })
        log.info(f"[Excuses] Reviewed {excuse_id}: {status}")
        return jsonify({"success": True, "excuse": updated})
    except ValueError:
        return jsonify({"success": False, "message": "Mazeret bulunamadı"}), 404
