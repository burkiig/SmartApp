"""
Attendance Engine — orchestrates the 3-step attendance verification chain.

Flow:
    Step 1 → verify_location()        GPS geofence check
    Step 2 → verify_face()            Face recognition
    Step 3 → verify_qr_and_record()   QR validation + persist attendance record

State between steps is persisted in the `attendance_steps` DB table with a TTL
(expires_at).  The step_id returned by Step 1 must be passed to Steps 2 and 3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOR THE DEVELOPER INTEGRATING FACE / GPS / QR MODULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Each verify_*() method has a clearly marked "── INTEGRATION POINT ──" section.
Replace the stubs/bypasses with real service calls.

After integrating each module, set the corresponding flag in config.py:
    FACE_RECOGNITION_AVAILABLE = True
    GEOFENCE_ACTIVE             = True
    QR_VERIFICATION_ACTIVE      = True

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from database.factory import get_db
from services.geofence_service import check_inside, detect_fake_gps, detect_location_jump
from services.push_service import notify_flagged_attendance
from shared.logger import get_logger

log = get_logger()

STEP_TIMEOUT = 120  # seconds — GPS→QR must complete within this window


class AttendanceEngine:
    """Stateless class — instantiate per request."""

    # ── Step 1: GPS / Geofence ─────────────────────────────────────────────────

    def verify_location(
        self,
        session_id: str,
        student_username: str,
        latitude,
        longitude,
        accuracy=None,
        speed=None,
        is_mocked: bool = False,
        altitude=None,
        gps_timestamp: str = None,
    ) -> dict:
        """
        Validate that the student is physically inside the classroom.

        On success, creates an `attendance_steps` record and returns step_id.
        The client MUST include step_id in subsequent Step 2 and Step 3 requests.

        Returns:
            {
                success       : bool,
                inside        : bool,
                distance_m    : float,
                geofence_radius: int,
                room_name     : str,
                step_id       : str,   # carry this to verify_face()
                is_flagged    : bool,
                flag_reason   : str | None,
            }
        """
        if not all([session_id, latitude is not None, longitude is not None]):
            return {"success": False, "message": "session_id, latitude ve longitude gerekli"}

        db = get_db()

        # ── Fetch session ──────────────────────────────────────────────────────
        session = db.get_session(session_id)
        if not session:
            return {"success": False, "message": "Oturum bulunamadı"}
        if session.get("status") != "active":
            return {"success": False, "message": "Bu oturum artık aktif değil"}

        # ── INTEGRATION POINT: GPS / Geofence ─────────────────────────────────
        # The geofence_service is FULLY IMPLEMENTED.
        # To activate: ensure rooms have latitude/longitude/geofence_radius set.
        course = db.get_course(session.get("course_id")) if session.get("course_id") else None
        room_id = None
        if course and isinstance(course.get("schedule"), dict):
            room_id = course["schedule"].get("room_id")
        room = db.get_room(room_id) if room_id else None

        if room and room.get("latitude") is not None:
            geo_result = check_inside(latitude, longitude, room)
            if not geo_result["inside"]:
                return {
                    "success": False,
                    "inside": False,
                    "message": "Sınıf dışındasınız — yoklama için sınıfta olmanız gerekiyor",
                    **geo_result,
                }
        else:
            geo_result = {
                "inside": True,
                "distance_m": 0,
                "geofence_radius": 40,
                "room_name": room.get("name", "Unknown") if room else "Unknown",
                "warning": "Room GPS not configured — geofence bypassed",
            }
            log.warning(f"[Engine] Geofence bypassed for session {session_id} (no room GPS)")
        # ── END INTEGRATION POINT ──────────────────────────────────────────────

        # Fake GPS detection — coords.mocked from client OS takes priority
        if is_mocked:
            is_flagged, flag_reason = True, "gps_mocked_by_os"
            log.warning(f"[Engine] Mocked GPS detected for {student_username} session={session_id}")
        else:
            is_flagged, flag_reason = detect_fake_gps(
                accuracy=accuracy,
                speed=speed if (speed is not None and speed >= 0) else None,
                gps_timestamp=gps_timestamp,
                server_receive_time=datetime.now(),
                altitude=altitude,
            )

        # Create attendance step record
        step_id = str(uuid.uuid4())
        expires_at = (datetime.now() + timedelta(seconds=STEP_TIMEOUT)).isoformat()
        db.create_attendance_step({
            "id": step_id,
            "student_username": student_username,
            "session_id": session_id,
            "gps_verified": 1,
            "gps_timestamp": datetime.now().isoformat(),
            "gps_distance": geo_result.get("distance_m"),
            "face_verified": 0,
            "face_timestamp": None,
            "face_score": None,
            "expires_at": expires_at,
        })

        log.info(f"[Engine] Step1 GPS OK: {student_username} session={session_id} step={step_id}")
        return {
            "success": True,
            "inside": True,
            "step_id": step_id,
            "is_flagged": is_flagged,
            "flag_reason": flag_reason,
            **geo_result,
        }

    # ── Step 2: Face Recognition ───────────────────────────────────────────────

    def verify_face(self, step_id: str, student_username: str, image_b64: str) -> dict:
        """
        Verify the student's face against the enrolled face encoding.

        Requires step_id from Step 1.  Rejects if the step has expired.

        Returns:
            {
                success       : bool,
                face_verified : bool,
                face_score    : float,   # distance — lower is better
                is_flagged    : bool,
            }

        ── INTEGRATION POINT: Face Recognition ──────────────────────────────
        When the `face_recognition` library is installed and students have
        face encodings stored, replace the bypass below with:

            from services.face_service import compare_face
            result = compare_face(image_b64)
            if not result["matched"]:
                return {"success": False, "message": "Yüz tanınamadı", "face_verified": False}
            face_score = result["distance"]
            is_flagged = result.get("is_flagged", False)

        Until then, face verification is bypassed and flagged with reason
        'face_simulated' so the instructor can see it on the dashboard.
        ─────────────────────────────────────────────────────────────────────
        """
        if not step_id or not image_b64:
            return {"success": False, "message": "step_id ve image gerekli"}

        db = get_db()
        step = db.get_attendance_step(step_id)
        if not step:
            return {"success": False, "message": "Geçersiz adım — önce GPS doğrulaması yapın"}
        if not step.get("gps_verified"):
            return {"success": False, "message": "GPS adımı tamamlanmamış"}
        if self._step_expired(step):
            db.delete_attendance_step(step_id)
            return {"success": False, "message": "İşlem süresi doldu — lütfen yeniden başlayın"}

        # ── INTEGRATION POINT ──────────────────────────────────────────────────
        try:
            from services.face_service import compare_face
            face_result = compare_face(image_b64)
            if not face_result.get("matched"):
                return {"success": False, "message": "Yüz tanınamadı", "face_verified": False}
            face_score = face_result["distance"]
            is_flagged = face_result.get("is_flagged", False)
            flag_reason = "face_borderline" if is_flagged else None
        except NotImplementedError:
            # Face service stub — bypass and flag
            log.warning(f"[Engine] Face recognition bypassed (not implemented) step={step_id}")
            face_score = None
            is_flagged = True
            flag_reason = "face_simulated"
        # ── END INTEGRATION POINT ─────────────────────────────────────────────

        db.update_attendance_step(step_id, {
            "face_verified": 1,
            "face_timestamp": datetime.now().isoformat(),
            "face_score": face_score,
            "face_flag_reason": flag_reason,
        })

        log.info(f"[Engine] Step2 Face: {student_username} step={step_id} score={face_score}")
        return {
            "success": True,
            "face_verified": True,
            "face_score": face_score,
            "is_flagged": is_flagged,
        }

    # ── Step 3: QR Scan + Record ───────────────────────────────────────────────

    def verify_qr_and_record(
        self,
        step_id: str,
        session_id: str,
        student_username: str,
        qr_code: str,
    ) -> dict:
        """
        Validate the QR code, check timing window, and persist the attendance record.

        Deletes the attendance_steps record after successful commit.

        Returns:
            {
                success            : bool,
                attendance_record  : dict,
                is_flagged         : bool,
                flag_reason        : str | None,
            }
        """
        if not all([step_id, session_id, qr_code]):
            return {"success": False, "message": "step_id, session_id ve qr_code gerekli"}

        db = get_db()
        step = db.get_attendance_step(step_id)
        if not step:
            return {"success": False, "message": "Geçersiz adım — GPS doğrulamasını yeniden yapın"}
        if not step.get("face_verified"):
            return {"success": False, "message": "Yüz doğrulama adımı tamamlanmamış"}
        if self._step_expired(step):
            db.delete_attendance_step(step_id)
            return {"success": False, "message": "İşlem süresi doldu — lütfen yeniden başlayın"}

        # Timing anomaly check
        flag_reasons = []
        if step.get("face_flag_reason"):
            flag_reasons.append(step["face_flag_reason"])
        if step.get("gps_flag_reason"):
            flag_reasons.append(step["gps_flag_reason"])

        # Flow speed check: GPS → Face → QR in < 5 seconds is humanly impossible
        gps_ts = step.get("gps_timestamp")
        face_ts = step.get("face_timestamp")
        if gps_ts and face_ts:
            try:
                flow_seconds = (
                    datetime.now() - datetime.fromisoformat(gps_ts)
                ).total_seconds()
                if flow_seconds is not None and flow_seconds < 5:
                    flag_reasons.append("too_fast_flow")
                    log.warning(
                        f"[Engine] Too-fast flow detected: {flow_seconds:.1f}s step={step_id}"
                    )
            except (ValueError, TypeError):
                pass

        is_flagged = len(flag_reasons) > 0

        # Session validation
        session = db.get_session(session_id)
        if not session:
            return {"success": False, "message": "Oturum bulunamadı"}
        if session.get("status") != "active":
            return {"success": False, "message": "Bu oturum artık aktif değil"}

        # ── INTEGRATION POINT: QR Verification ───────────────────────────────
        # The qr_service is FULLY IMPLEMENTED.
        # Activate it by ensuring course records have a `code` field.
        from services.qr_service import verify_qr_against_session
        qr_result = verify_qr_against_session(qr_code, session, student_username)
        if not qr_result["valid"]:
            log.warning(f"[Engine] QR invalid: {qr_result['reason']} step={step_id}")
            return {"success": False, "message": f"QR geçersiz: {qr_result['reason']}"}
        # ── END INTEGRATION POINT ─────────────────────────────────────────────

        # Resolve student info
        user = db.get_user(student_username)
        student_id = user.get("student_id", student_username) if user else student_username
        student = db.get_student(student_id) if student_id else None
        student_name = student.get("name", student_username) if student else student_username

        course_id = session.get("course_id")
        course = db.get_course(course_id) if course_id else None
        course_code = course.get("code", str(course_id)) if course else str(course_id)

        flag_reason = flag_reasons[0] if flag_reasons else None

        # Build and persist attendance record
        record = {
            "student_id": student_id,
            "name": student_name,
            "session_id": session_id,
            "course_id": course_id,
            "timestamp": datetime.now().isoformat(),
            "status": "present",
            "method": "qr_face",
            "face_score": step.get("face_score"),
            "location_distance": step.get("gps_distance"),
            "is_flagged": is_flagged,
            "flag_reason": flag_reason,
            "verification_steps": {
                "gps_ok": bool(step.get("gps_verified")),
                "face_ok": bool(step.get("face_verified")),
                "qr_ok": True,
            },
        }
        try:
            created = db.create_attendance_record(record)
        except Exception as dup_err:
            if "already marked" in str(dup_err).lower() or "unique" in str(dup_err).lower():
                db.delete_attendance_step(step_id)
                return {
                    "success": False,
                    "message": "Bu oturum için yoklamanız zaten kaydedilmiş.",
                    "code": "DUPLICATE_ATTENDANCE",
                }
            raise
        db.delete_attendance_step(step_id)

        log.info(
            f"[Engine] Attendance recorded: {student_id} session={session_id} "
            f"flagged={is_flagged} reason={flag_reason}"
        )

        if is_flagged:
            try:
                notify_flagged_attendance(session_id, student_name, flag_reason, course_code)
            except Exception as e:
                log.warning(f"[Engine] Flag notification failed: {e}")

        return {
            "success": True,
            "message": "Yoklama başarıyla kaydedildi",
            "attendance_record": created,
            "is_flagged": is_flagged,
            "flag_reason": flag_reason,
        }

    # ── Legacy (backward compat) ───────────────────────────────────────────────

    def mark_legacy(self, data: dict) -> dict:
        """Backward-compatible face-only attendance (pre-3-step flow)."""
        return {
            "success": False,
            "message": (
                "Bu endpoint artık kullanılmıyor. "
                "Lütfen /api/verify/location → /api/verify/face → /api/verify/qr "
                "zincirini kullanın."
            ),
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _step_expired(step: dict) -> bool:
        expires_at = step.get("expires_at")
        if not expires_at:
            return False
        try:
            return datetime.now() > datetime.fromisoformat(expires_at)
        except ValueError:
            return False
