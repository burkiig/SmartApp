"""
Time utility helpers used across the attendance engine and scheduler.
"""

from datetime import datetime
from typing import Optional


def seconds_since(iso_timestamp: str) -> Optional[float]:
    """
    Return the number of seconds elapsed since an ISO-format timestamp.
    Returns None if the timestamp is invalid or missing.
    """
    if not iso_timestamp:
        return None
    try:
        then = datetime.fromisoformat(iso_timestamp)
        return (datetime.now() - then).total_seconds()
    except ValueError:
        return None


def is_within_window(iso_timestamp: str, max_seconds: int) -> bool:
    """
    Return True if `iso_timestamp` is within `max_seconds` of now.
    Returns False if the timestamp is missing or older than the window.
    """
    elapsed = seconds_since(iso_timestamp)
    if elapsed is None:
        return False
    return elapsed <= max_seconds


def now_hhmm() -> str:
    """Return current time as 'HH:MM' string (used by scheduler)."""
    return datetime.now().strftime("%H:%M")


def today_date() -> str:
    """Return today's date as 'YYYY-MM-DD' string."""
    return datetime.now().strftime("%Y-%m-%d")


def today_weekday_name() -> str:
    """Return today's weekday name as used in course schedules, e.g. 'Monday'."""
    return datetime.now().strftime("%A")
