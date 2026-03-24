"""
Student routes.
GET    /api/students           — list all students (admin/instructor)
POST   /api/register           — register student with face image (admin/instructor)
DELETE /api/students/<id>      — delete student (admin)
"""

import base64
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from database.factory import get_db
from middleware.auth_middleware import require_role
from shared.errors import ValidationError
from shared.logger import get_logger
from cache.face_cache import invalidate_face_cache

log = get_logger()
students_bp = Blueprint("students", __name__, url_prefix="/api")


@students_bp.route("/students", methods=["GET"])
@jwt_required()
@require_role("admin", "instructor")
def get_students():
    db = get_db()
    students = db.get_students()
    return jsonify({"success": True, "students": students or []})


@students_bp.route("/register", methods=["POST"])
@jwt_required()
@require_role("admin", "instructor")
def register_student():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    name = data.get("name")
    image_data = data.get("image")

    if not student_id or not name:
        raise ValidationError("student_id ve name gerekli")

    db = get_db()
    student_record = {
        "student_id": student_id,
        "name": name,
    }

    # ── Face processing (requires face_recognition library) ───────────────────
    if image_data:
        try:
            from services.face_service import process_face_image
            face_result = process_face_image(image_data, student_id)
            if face_result.get("error"):
                return jsonify({"success": False, "message": face_result["error"]}), 400
            student_record.update(face_result)
            # Invalidate face cache so new student is picked up immediately
            invalidate_face_cache()
        except ImportError:
            log.warning("[Students] face_service not available — skipping face processing")

    created = db.create_student(student_record)
    log.info(f"[Students] Registered: {student_id} ({name})")
    return jsonify({
        "success": True,
        "message": "Öğrenci başarıyla kaydedildi",
        "student": created,
    })


@students_bp.route("/students/<student_id>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_student(student_id):
    db = get_db()
    student = db.get_student(student_id)
    if not student:
        return jsonify({"success": False, "message": "Öğrenci bulunamadı"}), 404

    if student.get("image"):
        face_path = os.path.join("static", "faces", student["image"])
        if os.path.exists(face_path):
            os.remove(face_path)

    db.delete_student(student_id)
    invalidate_face_cache()
    log.info(f"[Students] Deleted: {student_id}")
    return jsonify({"success": True, "message": "Öğrenci silindi"})
