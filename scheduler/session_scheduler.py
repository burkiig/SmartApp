"""
Session Scheduler — APScheduler background job manager.

Runs two periodic jobs:
    1. open_sessions  — creates new sessions when a course's start time arrives
    2. close_sessions — closes active sessions when their end time is reached

CRITICAL: All jobs use `app.app_context()` so that flask.g and DB adapters
work correctly inside background threads.

Usage (called from create_app()):
    from scheduler.session_scheduler import start_scheduler
    scheduler = start_scheduler(app)
    app.config["_scheduler"] = scheduler   # stored for health endpoint
"""

from datetime import datetime

from shared.logger import get_logger
from utils.time_utils import now_hhmm, today_date, today_weekday_name

log = get_logger()

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    log.warning("[Scheduler] APScheduler not installed — automatic session management disabled")


def start_scheduler(app):
    """
    Create and start the APScheduler instance.

    Args:
        app: The Flask application instance created by create_app().
             Required so background jobs can use app.app_context().

    Returns:
        Running BackgroundScheduler instance, or None if APScheduler is unavailable.
    """
    if not SCHEDULER_AVAILABLE:
        return None

    scheduler = BackgroundScheduler(timezone="Europe/Istanbul")

    scheduler.add_job(
        func=lambda: _run_open_sessions(app),
        trigger=IntervalTrigger(seconds=30),
        id="open_sessions",
        name="Auto-open scheduled sessions",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.add_job(
        func=lambda: _run_close_sessions(app),
        trigger=IntervalTrigger(seconds=30),
        id="close_sessions",
        name="Auto-close expired sessions",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.add_job(
        func=lambda: _run_cleanup_steps(app),
        trigger=IntervalTrigger(minutes=5),
        id="cleanup_steps",
        name="Cleanup expired attendance steps",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    log.info("[Scheduler] APScheduler started — auto session management active")
    return scheduler


# ── Job implementations ────────────────────────────────────────────────────────

def _run_open_sessions(app):
    """Open sessions for courses whose start time matches the current minute."""
    with app.app_context():
        from database.factory import get_db
        from services.schedule_service import get_courses_starting_now

        db = get_db()
        today_name = today_weekday_name()
        today = today_date()
        current_time = now_hhmm()

        courses = get_courses_starting_now(db, today_name, current_time)
        for course in courses:
            try:
                existing = db.get_sessions(course_id=course["id"])
                if any(s.get("date") == today for s in existing):
                    continue

                schedule = course.get("schedule", {})
                created = db.create_session({
                    "course_id": course["id"],
                    "date": today,
                    "start_time": schedule.get("start_time"),
                    "end_time": schedule.get("end_time"),
                })
                log.info(
                    f"[Scheduler] Auto-opened session {created['id']} "
                    f"for course {course.get('code', '?')} at {current_time}"
                )
            except Exception as e:
                log.error(f"[Scheduler] Failed to open session for course {course.get('id')}: {e}")


def _run_close_sessions(app):
    """Close active sessions whose end time has been reached."""
    with app.app_context():
        from database.factory import get_db
        from services.schedule_service import get_sessions_to_close

        db = get_db()
        today = today_date()
        current_time = now_hhmm()

        sessions = get_sessions_to_close(db, today, current_time)
        for session in sessions:
            try:
                db.update_session(session["id"], {"status": "closed"})
                log.info(
                    f"[Scheduler] Auto-closed session {session['id']} "
                    f"(end_time={session.get('end_time')}, now={current_time})"
                )
            except Exception as e:
                log.error(f"[Scheduler] Failed to close session {session['id']}: {e}")


def _run_cleanup_steps(app):
    """Delete expired attendance_steps records (abandoned flows)."""
    with app.app_context():
        from database.factory import get_db
        db = get_db()
        try:
            deleted = db.delete_expired_attendance_steps()
            if deleted:
                log.info(f"[Scheduler] Cleaned up {deleted} expired attendance steps")
        except Exception as e:
            log.error(f"[Scheduler] Step cleanup error: {e}")
