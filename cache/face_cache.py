"""
Face Encoding Cache — thread-safe in-memory cache for face encodings.

Loaded once at startup (or on first request), then reused for every
attendance verification without hitting disk or DB again.

Invalidated automatically when a new student is registered
(routes/students.py calls invalidate_face_cache() after enrollment).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOR THE DEVELOPER IMPLEMENTING FACE RECOGNITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

get_known_faces() returns a dict {student_id: numpy_array_128d}.
This is consumed by services/face_service.py → compare_face().

The cache is populated from DB (students.face_encoding BLOB column).
Each encoding is stored as pickle.dumps(numpy_array) and loaded with
pickle.loads(blob).

To populate the cache, students must be registered WITH a face image via
POST /api/register.  Students without face encodings are silently skipped.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pickle
import threading
from typing import Dict, Optional, Any

from shared.logger import get_logger

log = get_logger()

_cache: Optional[Dict[str, Any]] = None
_lock = threading.Lock()


def get_known_faces(force_reload: bool = False) -> Dict[str, Any]:
    """
    Return a dict mapping student_id → face encoding (numpy array).

    Loads from DB on first call, then serves from RAM.

    Args:
        force_reload: Set True to bypass cache and reload from DB.
                      Called automatically by invalidate_face_cache().

    Returns:
        {student_id: numpy_array_128d, ...}
        Empty dict if no students have face encodings or library is unavailable.
    """
    global _cache
    with _lock:
        if _cache is None or force_reload:
            _cache = _load_from_db()
    return _cache


def invalidate_face_cache():
    """
    Mark the cache as stale so it reloads on the next verify_face() call.
    Call this whenever a student is registered or deleted.
    """
    global _cache
    with _lock:
        _cache = None
    log.info("[FaceCache] Cache invalidated")


def _load_from_db() -> Dict[str, Any]:
    """
    Load all face encodings from the database.

    TODO (developer):
        This function requires the face_recognition + numpy libraries.
        Implement the body when those are installed.

        Steps:
            from database.factory import get_scheduler_db
            db = get_scheduler_db()
            students = db.get_students()
            result = {}
            for s in students:
                blob = s.get("face_encoding")
                if blob:
                    try:
                        encoding = pickle.loads(blob)  # → numpy array (128,)
                        result[s["student_id"]] = encoding
                    except Exception as e:
                        log.warning(f"[FaceCache] Bad encoding for {s['student_id']}: {e}")
            log.info(f"[FaceCache] Loaded {len(result)} face encodings")
            return result
    """
    try:
        from database.factory import get_scheduler_db
        db = get_scheduler_db()
        students = db.get_students() or []
        result = {}
        for s in students:
            blob = s.get("face_encoding")
            if not blob:
                continue
            try:
                encoding = pickle.loads(blob)
                result[s.get("student_id", s.get("id", ""))] = encoding
            except Exception as e:
                log.warning(f"[FaceCache] Could not load encoding for student {s.get('student_id')}: {e}")
        log.info(f"[FaceCache] Loaded {len(result)} face encodings from DB")
        return result
    except Exception as e:
        log.error(f"[FaceCache] Load error: {e}")
        return {}
