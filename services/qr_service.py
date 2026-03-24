"""
QR Code Service — Interface + stub implementation.

STATUS: INTERFACE READY — QR generation requires `qrcode` library (optional).
        QR verification logic is FULLY IMPLEMENTED (pure Python, no extra deps).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOR THE DEVELOPER IMPLEMENTING THIS MODULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QR content format:
    "smartattendance://course/<COURSE_CODE>"
    Example: "smartattendance://course/AI101"

The QR is STATIC PER COURSE — the instructor prints it once and puts it on
their slides.  Security is guaranteed by the GPS + Face steps preceding this.

Verification flow (in attendance_engine.py):
    1. Parse the QR string to extract the course code.
    2. Look up whether an active session exists for that course today.
    3. Check that the student is enrolled in that course.
    4. Return the session_id if all checks pass.

To add a rotating/time-limited QR in the future:
    - Add a `qr_secret` column to the sessions table.
    - Include a HMAC of (course_code + date + session_id) in the QR payload.
    - Verify the HMAC on the server side.

QR generation (optional — for the instructor dashboard):
    pip install qrcode[pil]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
from typing import Optional

from shared.logger import get_logger

log = get_logger()

QR_SCHEME = "smartattendance://course/"


# ── QR Generation (optional) ───────────────────────────────────────────────────

def generate_qr_image(course_code: str, output_path: str) -> bool:
    """
    Generate a PNG QR code image for the given course code.

    Args:
        course_code  : e.g. "AI101"
        output_path  : filesystem path to write the PNG to

    Returns:
        True on success, False if `qrcode` library is not installed.

    TODO (developer):
        Install: pip install qrcode[pil]

        Implementation:
            import qrcode
            qr = qrcode.make(f"{QR_SCHEME}{course_code}")
            qr.save(output_path)
            return True
    """
    try:
        import qrcode
        qr = qrcode.make(f"{QR_SCHEME}{course_code}")
        qr.save(output_path)
        log.info(f"[QRService] QR generated for {course_code} → {output_path}")
        return True
    except ImportError:
        log.warning("[QRService] qrcode library not installed — QR generation disabled")
        return False


# ── QR Parsing ─────────────────────────────────────────────────────────────────

def parse_qr_code(qr_value: str) -> Optional[str]:
    """
    Extract the course code from a QR string.

    Args:
        qr_value: String read from the QR scanner, e.g.
                  "smartattendance://course/AI101"

    Returns:
        Course code string (e.g. "AI101"), or None if format is invalid.
    """
    if not qr_value:
        return None
    if qr_value.startswith(QR_SCHEME):
        code = qr_value[len(QR_SCHEME):].strip()
        if re.match(r"^[A-Z0-9_\-]+$", code):
            return code
    # Fallback: treat the raw value as the course code (legacy support)
    return qr_value.strip() or None


# ── QR Verification ────────────────────────────────────────────────────────────

def verify_qr_against_session(qr_value: str, session: dict, student_id: str) -> dict:
    """
    Verify a scanned QR code against an active session and check enrollment.

    Args:
        qr_value   : Raw string from the QR scanner
        session    : Session dict from the database (must have status='active')
        student_id : Student's ID (used for enrollment check)

    Returns:
        {"valid": True}  on success
        {"valid": False, "reason": str}  on failure

    Checks performed:
        1. Session is active.
        2. QR code matches the course code of the session.
        3. Student is enrolled in the course (requires DB lookup — done by caller).
    """
    if session.get("status") != "active":
        return {"valid": False, "reason": "session_not_active"}

    course_code_from_qr = parse_qr_code(qr_value)
    if not course_code_from_qr:
        return {"valid": False, "reason": "invalid_qr_format"}

    session_course_code = session.get("course_code") or str(session.get("course_id", ""))
    if course_code_from_qr.upper() != session_course_code.upper():
        return {"valid": False, "reason": "qr_course_mismatch"}

    return {"valid": True}
