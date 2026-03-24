"""
Schedule Service — course schedule queries used by the session scheduler.

Responsibility:
    - Query the database to determine which courses should have a session opened
      or closed at the current time.
    - Isolated here so the scheduler job remains thin and testable.
"""

from datetime import datetime
from typing import List, Dict, Any

from shared.logger import get_logger

log = get_logger()


def get_courses_starting_now(db, today_name: str, current_hhmm: str) -> List[Dict[str, Any]]:
    """
    Return courses whose schedule indicates they start at `current_hhmm` today.

    Args:
        db           : Database adapter instance (from get_scheduler_db())
        today_name   : Day name, e.g. "Monday"
        current_hhmm : Current time as "HH:MM", e.g. "09:00"

    Returns:
        List of course dicts that should have a session opened right now.
    """
    try:
        courses = db.get_courses() or []
    except Exception as e:
        log.error(f"[ScheduleService] get_courses error: {e}")
        return []

    starting = []
    for course in courses:
        schedule = course.get("schedule")
        if not isinstance(schedule, dict):
            continue
        days = schedule.get("days", [])
        start = schedule.get("start_time")
        if today_name in days and start == current_hhmm:
            starting.append(course)

    return starting


def get_sessions_to_close(db, today_date: str, current_hhmm: str) -> List[Dict[str, Any]]:
    """
    Return active sessions whose end_time has been reached.

    Args:
        db           : Database adapter instance
        today_date   : ISO date string, e.g. "2026-03-23"
        current_hhmm : Current time as "HH:MM"

    Returns:
        List of session dicts that should be closed.
    """
    try:
        active = db.get_sessions(status="active") or []
    except Exception as e:
        log.error(f"[ScheduleService] get_sessions error: {e}")
        return []

    to_close = []
    for session in active:
        if session.get("date") != today_date:
            continue
        end_time = session.get("end_time")
        if end_time and current_hhmm >= end_time:
            to_close.append(session)

    return to_close
