"""
Dashboard routes.
GET /api/dashboard/stats              — summary statistics
GET /api/dashboard/course-performance — per-course attendance rates
GET /api/dashboard/recent-activity    — last 10 attendance events
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from database.factory import get_db
from middleware.auth_middleware import require_role
from shared.logger import get_logger

log = get_logger()
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
@require_role("admin", "instructor")
def get_stats():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    students = db.get_students() or []
    records = db.get_attendance_records() or []

    today_records = [r for r in records if r.get("timestamp", "").startswith(today)]
    last_month_records = [r for r in records if r.get("timestamp", "") >= last_month]

    unique_dates = {r.get("timestamp", "").split("T")[0] for r in records if r.get("timestamp")}
    total_classes = len(unique_dates)
    total_students = len(students)
    present_today = len(today_records)

    avg_attendance = 0
    if total_classes > 0 and total_students > 0:
        avg_attendance = round((len(records) / (total_classes * total_students)) * 100)

    return jsonify({
        "success": True,
        "stats": {
            "total_students": total_students,
            "total_classes": total_classes,
            "avg_attendance": avg_attendance,
            "present_today": present_today,
            "absent_today": total_students - present_today,
            "last_month_records": len(last_month_records),
        },
    })


@dashboard_bp.route("/course-performance", methods=["GET"])
@jwt_required()
@require_role("admin", "instructor")
def get_course_performance():
    """
    Returns per-course attendance rates.
    TODO: Replace with real aggregation query once SQLite adapter is active.
    """
    db = get_db()
    courses = db.get_courses() or []
    performance = []
    for course in courses:
        performance.append({
            "course": course.get("code", ""),
            "name": course.get("name", ""),
            "attendance": 0,
            "students": len(course.get("enrolled_students", [])),
        })
    return jsonify({"success": True, "performance": performance})


@dashboard_bp.route("/recent-activity", methods=["GET"])
@jwt_required()
@require_role("admin", "instructor")
def get_recent_activity():
    db = get_db()
    records = db.get_attendance_records() or []
    recent = sorted(records, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
    activities = [
        {
            "type": "attendance",
            "title": f"{r.get('name', '?')} - Yoklama",
            "timestamp": r.get("timestamp"),
            "details": f"Öğrenci No: {r.get('student_id')}",
        }
        for r in recent
    ]
    return jsonify({"success": True, "activities": activities})
