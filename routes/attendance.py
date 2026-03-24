"""
Attendance routes — the core of the system.

Legacy face-only endpoint:
  POST /api/attendance            — mark attendance via face image (backward compat)

3-step attendance verification chain:
  POST /api/verify/location       — Step 1: GPS / geofence check
  POST /api/verify/face           — Step 2: face recognition
  POST /api/verify/qr             — Step 3: QR scan → creates attendance record

Record management:
  GET  /api/attendance/records    — list records (admin/instructor)
  GET  /api/attendance/flagged    — flagged records (admin/instructor)
  PATCH /api/attendance/<id>/review — manual review (admin/instructor)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database.factory import get_db
from middleware.auth_middleware import require_role
from shared.logger import get_logger

log = get_logger()
attendance_bp = Blueprint("attendance", __name__, url_prefix="/api")


# ── Legacy face-only attendance (backward compat) ──────────────────────────────

@attendance_bp.route("/attendance", methods=["POST"])
@jwt_required()
@require_role("student")
def mark_attendance():
    """
    Legacy endpoint retained for backward compatibility.
    New clients should use the 3-step /verify/ chain instead.
    """
    try:
        from services.attendance_engine import AttendanceEngine
        engine = AttendanceEngine()
        result = engine.mark_legacy(request.get_json() or {})
        return jsonify(result)
    except ImportError:
        return jsonify({"success": False, "message": "Attendance engine not available"}), 503
    except Exception as e:
        log.error(f"[Attendance] mark_attendance error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ── Step 1: Location / Geofence ────────────────────────────────────────────────

@attendance_bp.route("/verify/location", methods=["POST"])
@jwt_required()
@require_role("student")
def verify_location():
    """
    GPS geofence check — Step 1 of the attendance chain.

    Body:
        session_id  : str   (required)
        latitude    : float (required)
        longitude   : float (required)
        accuracy    : float (optional — GPS accuracy in metres; used for fake-GPS detection)
        altitude    : float (optional)
        speed       : float (optional — m/s; used for fake-GPS detection)

    Response:
        inside          : bool
        distance_m      : float
        geofence_radius : int
        room_name       : str
        step_id         : str  — carry this through Step 2 and Step 3
    """
    try:
        from services.attendance_engine import AttendanceEngine
        identity = get_jwt_identity()
        body = request.get_json(silent=True) or {}

        # coords.mocked = True means the client's OS flagged this as a simulated location
        is_mocked = bool(body.get("mocked") or body.get("coords", {}).get("mocked"))

        result = AttendanceEngine().verify_location(
            session_id=body.get("session_id"),
            student_username=identity.get("username"),
            latitude=body.get("latitude"),
            longitude=body.get("longitude"),
            accuracy=body.get("accuracy"),
            speed=body.get("speed"),
            is_mocked=is_mocked,
            altitude=body.get("altitude"),
            gps_timestamp=body.get("gps_timestamp"),
        )
        log.debug(f"[GPS Payload] user={identity.get('username')} "
                  f"lat={body.get('latitude')} lng={body.get('longitude')} "
                  f"acc={body.get('accuracy')} mocked={is_mocked} "
                  f"alt={body.get('altitude')} spd={body.get('speed')}")
        return jsonify(result)
    except Exception as e:
        log.error(f"[Attendance] verify_location error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ── Step 2: Face Recognition ───────────────────────────────────────────────────

@attendance_bp.route("/verify/face", methods=["POST"])
@jwt_required()
@require_role("student")
def verify_face():
    """
    Face recognition — Step 2 of the attendance chain.

    Body:
        step_id  : str    — from Step 1 response (required)
        image    : str    — base64-encoded JPEG/PNG (required)

    Response:
        face_verified   : bool
        face_score      : float  — distance (lower = more confident)
        is_flagged      : bool
    """
    try:
        from services.attendance_engine import AttendanceEngine
        identity = get_jwt_identity()
        result = AttendanceEngine().verify_face(
            step_id=request.json.get("step_id"),
            student_username=identity.get("username"),
            image_b64=request.json.get("image"),
        )
        return jsonify(result)
    except Exception as e:
        log.error(f"[Attendance] verify_face error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ── Step 3: QR Scan → Record attendance ───────────────────────────────────────

@attendance_bp.route("/verify/qr", methods=["POST"])
@jwt_required()
@require_role("student")
def verify_qr():
    """
    QR scan — Step 3 and final step; creates the attendance record.

    Body:
        step_id    : str  — from Step 1 response (required)
        session_id : str  — active session UUID (required)
        qr_code    : str  — value read from QR code, e.g. "smartattendance://course/AI101"

    Response:
        attendance_record : dict
        is_flagged        : bool
        flag_reason       : str | null
    """
    try:
        from services.attendance_engine import AttendanceEngine
        identity = get_jwt_identity()
        result = AttendanceEngine().verify_qr_and_record(
            step_id=request.json.get("step_id"),
            session_id=request.json.get("session_id"),
            student_username=identity.get("username"),
            qr_code=request.json.get("qr_code"),
        )
        return jsonify(result)
    except Exception as e:
        log.error(f"[Attendance] verify_qr error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ── Record management ──────────────────────────────────────────────────────────

@attendance_bp.route("/attendance/records", methods=["GET"])
@jwt_required()
@require_role("admin", "instructor")
def get_attendance_records():
    db = get_db()
    date = request.args.get("date")
    records = db.get_attendance_records(date=date) or []
    return jsonify({"success": True, "records": records})


@attendance_bp.route("/attendance/flagged", methods=["GET"])
@jwt_required()
@require_role("admin", "instructor")
def get_flagged_attendance():
    db = get_db()
    records = db.get_flagged_attendance() or []
    return jsonify({"success": True, "records": records})


@attendance_bp.route("/attendance/<record_id>/review", methods=["PATCH"])
@jwt_required()
@require_role("admin", "instructor")
def review_attendance(record_id):
    data = request.get_json() or {}
    db = get_db()
    try:
        update = {
            "is_flagged": data.get("is_flagged", False),
            "flag_reason": data.get("flag_reason"),
        }
        if data.get("status"):
            update["status"] = data["status"]
        updated = db.update_attendance_record(record_id, update)
        log.info(f"[Attendance] Record {record_id} reviewed")
        return jsonify({"success": True, "record": updated})
    except ValueError:
        return jsonify({"success": False, "message": "Yoklama kaydı bulunamadı"}), 404
