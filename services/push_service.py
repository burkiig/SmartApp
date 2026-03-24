"""
Push Notification Service — Expo Push API wrapper.

STATUS: FULLY IMPLEMENTED (uses Expo Push API, no FCM setup required).

Expo Push API is the recommended approach for React Native / Expo apps.
Internally it routes through FCM (Android) and APNs (iOS) automatically.
"""

from typing import Optional
from shared.logger import get_logger

log = get_logger()

try:
    import requests as http_requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    log.warning("[PushService] requests library not installed — push notifications disabled")


EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def _send_expo_push(tokens: list, title: str, body: str, data: dict = None) -> dict:
    """
    Send a batch push notification via the Expo Push API.

    Args:
        tokens : List of Expo push tokens, e.g. ["ExponentPushToken[xxx]"]
        title  : Notification title
        body   : Notification body
        data   : Optional dict attached as notification data payload

    Returns:
        Expo API response dict, or {"error": reason} on failure
    """
    if not REQUESTS_AVAILABLE:
        return {"error": "requests library not installed"}
    if not tokens:
        return {"sent": 0}

    messages = [
        {"to": t, "sound": "default", "title": title, "body": body, "data": data or {}}
        for t in tokens
    ]
    try:
        resp = http_requests.post(
            EXPO_PUSH_URL,
            json=messages,
            headers={
                "Accept": "application/json",
                "Accept-encoding": "gzip, deflate",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        log.info(f"[PushService] Sent {len(tokens)} notifications — HTTP {resp.status_code}")
        return resp.json()
    except Exception as e:
        log.error(f"[PushService] Expo API error: {e}")
        return {"error": str(e)}


def notify_class_cancelled(course_id, course_code: str, reason: str):
    """
    Send a class cancellation push notification to all enrolled students.

    Called by routes/sessions.py → cancel_class().
    """
    from database.factory import get_scheduler_db
    db = get_scheduler_db()

    course = db.get_course(course_id)
    if not course:
        return

    push_tokens = []
    for sid in course.get("enrolled_students", []):
        student = db.get_student(sid)
        if student and student.get("push_token"):
            push_tokens.append(student["push_token"])

    if not push_tokens:
        log.info(f"[PushService] No push tokens for {course_code}")
        return

    _send_expo_push(
        tokens=push_tokens,
        title="Ders İptal Edildi 📢",
        body=f"{course_code} dersi iptal edildi. Sebep: {reason}",
        data={"type": "class_cancelled", "course_id": str(course_id), "course_code": course_code},
    )


def notify_flagged_attendance(
    session_id: str,
    student_name: str,
    flag_reason: str,
    course_code: str,
):
    """
    Notify the course instructor when a suspicious attendance is detected.

    Called by services/attendance_engine.py after recording a flagged attendance.
    """
    from database.factory import get_scheduler_db
    db = get_scheduler_db()

    REASON_LABELS = {
        "duplicate_attendance": "Aynı oturumda çift yoklama denemesi",
        "location_bypassed": "GPS doğrulaması atlandı",
        "face_simulated": "Yüz tanıma simüle edildi",
        "location_and_face_bypass": "GPS ve yüz tanıma ikisi de atlandı",
        "timing_anomaly": "İşlem adımları arası süre aşıldı",
        "delayed_gps_submission": "GPS konumu gecikmeli gönderildi",
        "gps_accuracy_zero": "GPS doğruluğu sıfır (sahte GPS şüphesi)",
        "speed_too_high": "Cihaz hareket hızı çok yüksek",
    }
    label = REASON_LABELS.get(flag_reason, flag_reason)

    session = db.get_session(session_id)
    if not session:
        return
    course = db.get_course(session.get("course_id")) if session.get("course_id") else None
    if not course:
        return

    instructor = db.get_user(course.get("instructor", ""))
    if not instructor or not instructor.get("push_token"):
        return

    _send_expo_push(
        tokens=[instructor["push_token"]],
        title="⚠️ Şüpheli Yoklama Tespit Edildi",
        body=f"{course_code} — {student_name}: {label}",
        data={
            "type": "flagged_attendance",
            "session_id": session_id,
            "course_code": course_code,
            "flag_reason": flag_reason,
        },
    )
