"""
SQLite database adapter with WAL mode for concurrent read performance.

Implements the full DatabaseAdapter interface.
Activate by setting DB_DRIVER=sqlite in your .env file.

Schema is auto-created on first run.  See _init_schema() for table definitions.

Performance notes:
    - WAL mode + synchronous=NORMAL enables concurrent reads
    - Indexes on high-frequency query columns (session_id, student_id, status, date)
    - face_encoding stored as BLOB (pickle.dumps of 128-float numpy array)
"""

import pickle
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import DatabaseAdapter


class DuplicateAttendanceError(Exception):
    """Raised when a student tries to submit attendance twice for the same session."""


class SQLiteAdapter(DatabaseAdapter):

    def __init__(self, db_path: str = "smart_attendance.db"):
        self.db_path = db_path
        self._init_schema()

    # ── Connection ─────────────────────────────────────────────────────────────

    def _connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ── Schema ─────────────────────────────────────────────────────────────────

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    username  TEXT UNIQUE NOT NULL,
                    password  TEXT NOT NULL,
                    role      TEXT CHECK(role IN ('admin','instructor','student')) NOT NULL,
                    name      TEXT,
                    email     TEXT,
                    department TEXT,
                    student_id TEXT,
                    push_token TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS students (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id     TEXT UNIQUE NOT NULL,
                    name           TEXT NOT NULL,
                    email          TEXT,
                    image          TEXT,
                    face_encoding  BLOB,
                    push_token     TEXT,
                    registered_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS rooms (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    name             TEXT NOT NULL,
                    capacity         INTEGER,
                    type             TEXT,
                    equipment        TEXT,
                    latitude         REAL,
                    longitude        REAL,
                    geofence_radius  INTEGER DEFAULT 40,
                    status           TEXT DEFAULT 'available'
                );

                CREATE TABLE IF NOT EXISTS courses (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    code        TEXT UNIQUE NOT NULL,
                    name        TEXT NOT NULL,
                    instructor  TEXT,
                    room_id     INTEGER REFERENCES rooms(id),
                    schedule    TEXT,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS course_enrollments (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id   INTEGER NOT NULL REFERENCES courses(id),
                    student_id  TEXT NOT NULL,
                    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(course_id, student_id)
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id          TEXT PRIMARY KEY,
                    course_id   INTEGER REFERENCES courses(id),
                    date        TEXT NOT NULL,
                    start_time  TEXT,
                    end_time    TEXT,
                    status      TEXT DEFAULT 'scheduled',
                    qr_code     TEXT,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS attendance (
                    id                 TEXT PRIMARY KEY,
                    session_id         TEXT REFERENCES sessions(id),
                    student_id         TEXT NOT NULL,
                    name               TEXT,
                    course_id          INTEGER,
                    timestamp          DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status             TEXT DEFAULT 'present',
                    method             TEXT DEFAULT 'qr_face',
                    face_score         REAL,
                    location_distance  REAL,
                    is_flagged         INTEGER DEFAULT 0,
                    flag_reason        TEXT,
                    verification_steps TEXT
                );

                CREATE TABLE IF NOT EXISTS attendance_steps (
                    id                TEXT PRIMARY KEY,
                    student_username  TEXT NOT NULL,
                    session_id        TEXT NOT NULL,
                    gps_verified      INTEGER DEFAULT 0,
                    gps_timestamp     DATETIME,
                    gps_distance      REAL,
                    gps_flag_reason   TEXT,
                    face_verified     INTEGER DEFAULT 0,
                    face_timestamp    DATETIME,
                    face_score        REAL,
                    face_flag_reason  TEXT,
                    expires_at        DATETIME NOT NULL,
                    UNIQUE(student_username, session_id)
                );

                CREATE TABLE IF NOT EXISTS cancellations (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id     INTEGER,
                    instructor_id TEXT,
                    date          TEXT,
                    reason        TEXT,
                    notified_at   DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS excuses (
                    id               TEXT PRIMARY KEY,
                    student_id       TEXT NOT NULL,
                    course_id        INTEGER,
                    session_date     TEXT,
                    excuse_type      TEXT DEFAULT 'other',
                    description      TEXT,
                    document_url     TEXT,
                    status           TEXT DEFAULT 'pending',
                    instructor_notes TEXT,
                    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS devices (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    username     TEXT NOT NULL,
                    device_id    TEXT NOT NULL,
                    platform     TEXT,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active    INTEGER DEFAULT 1,
                    UNIQUE(username, device_id)
                );

                -- Performance indexes
                CREATE INDEX IF NOT EXISTS idx_attendance_session
                    ON attendance(session_id);
                CREATE INDEX IF NOT EXISTS idx_attendance_student
                    ON attendance(student_id);
                CREATE INDEX IF NOT EXISTS idx_enrollment_course
                    ON course_enrollments(course_id);
                CREATE INDEX IF NOT EXISTS idx_enrollment_student
                    ON course_enrollments(student_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_status
                    ON sessions(status);
                CREATE INDEX IF NOT EXISTS idx_sessions_course_date
                    ON sessions(course_id, date);

                -- Duplicate protection: one attendance record per student per session
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_attendance
                    ON attendance(session_id, student_id);

                -- Scheduler race condition: prevent duplicate sessions per course/day/time
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_session
                    ON sessions(course_id, date, start_time);

                -- TTL index for fast expiry cleanup
                CREATE INDEX IF NOT EXISTS idx_attendance_steps_expiry
                    ON attendance_steps(expires_at);

                -- Device lookup by username
                CREATE INDEX IF NOT EXISTS idx_devices_username
                    ON devices(username);
            """)

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_dict(row) -> dict:
        return dict(row) if row else None

    @staticmethod
    def _rows_to_list(rows) -> list:
        return [dict(r) for r in rows]

    # ── Students ───────────────────────────────────────────────────────────────

    def get_students(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM students").fetchall()
            return self._rows_to_list(rows)

    def get_student(self, student_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM students WHERE student_id=?", (student_id,)
            ).fetchone()
            return self._row_to_dict(row)

    def create_student(self, data):
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO students
                   (student_id, name, email, image, face_encoding, push_token)
                   VALUES (?,?,?,?,?,?)""",
                (
                    data.get("student_id"), data.get("name"), data.get("email"),
                    data.get("image"), data.get("face_encoding"), data.get("push_token"),
                ),
            )
        return self.get_student(data["student_id"])

    def update_student(self, student_id, data):
        fields = ", ".join(f"{k}=?" for k in data)
        values = list(data.values()) + [student_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE students SET {fields} WHERE student_id=?", values)
        return self.get_student(student_id)

    def delete_student(self, student_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        return True

    # ── Users ──────────────────────────────────────────────────────────────────

    def get_users(self):
        with self._connect() as conn:
            return self._rows_to_list(conn.execute("SELECT * FROM users").fetchall())

    def get_user(self, username):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            return self._row_to_dict(row)

    def create_user(self, data):
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO users (username,password,role,name,email,department,student_id)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    data["username"], data["password"], data["role"],
                    data.get("name"), data.get("email"),
                    data.get("department"), data.get("student_id"),
                ),
            )
        return self.get_user(data["username"])

    def update_user(self, username, data):
        fields = ", ".join(f"{k}=?" for k in data)
        values = list(data.values()) + [username]
        with self._connect() as conn:
            conn.execute(f"UPDATE users SET {fields} WHERE username=?", values)
        return self.get_user(username)

    def delete_user(self, username):
        with self._connect() as conn:
            conn.execute("DELETE FROM users WHERE username=?", (username,))
        return True

    # ── Courses ────────────────────────────────────────────────────────────────

    def get_courses(self):
        import json
        with self._connect() as conn:
            rows = self._rows_to_list(conn.execute("SELECT * FROM courses").fetchall())
        for r in rows:
            if r.get("schedule") and isinstance(r["schedule"], str):
                try:
                    r["schedule"] = json.loads(r["schedule"])
                except Exception:
                    pass
        return rows

    def get_course(self, course_id):
        import json
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM courses WHERE id=?", (course_id,)).fetchone()
            r = self._row_to_dict(row)
        if r and isinstance(r.get("schedule"), str):
            try:
                r["schedule"] = json.loads(r["schedule"])
            except Exception:
                pass
        return r

    def create_course(self, data):
        import json
        schedule = data.get("schedule")
        if isinstance(schedule, dict):
            schedule = json.dumps(schedule)
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO courses (code, name, instructor, room_id, schedule) VALUES (?,?,?,?,?)",
                (data["code"], data["name"], data.get("instructor"), data.get("room_id"), schedule),
            )
            return self.get_course(cursor.lastrowid)

    def delete_course(self, course_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM courses WHERE id=?", (course_id,))
        return True

    # ── Rooms ──────────────────────────────────────────────────────────────────

    def get_rooms(self):
        with self._connect() as conn:
            return self._rows_to_list(conn.execute("SELECT * FROM rooms").fetchall())

    def get_room(self, room_id):
        with self._connect() as conn:
            return self._row_to_dict(
                conn.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone()
            )

    def create_room(self, data):
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO rooms
                   (name, capacity, type, equipment, latitude, longitude, geofence_radius, status)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    data["name"], data.get("capacity"), data.get("type"), data.get("equipment"),
                    data.get("latitude"), data.get("longitude"),
                    data.get("geofence_radius", 40), data.get("status", "available"),
                ),
            )
            return self.get_room(cursor.lastrowid)

    def delete_room(self, room_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        return True

    # ── Sessions ───────────────────────────────────────────────────────────────

    def get_sessions(self, course_id=None, status=None):
        query = "SELECT * FROM sessions WHERE 1=1"
        params = []
        if course_id is not None:
            query += " AND course_id=?"
            params.append(course_id)
        if status:
            query += " AND status=?"
            params.append(status)
        with self._connect() as conn:
            return self._rows_to_list(conn.execute(query, params).fetchall())

    def get_session(self, session_id):
        with self._connect() as conn:
            return self._row_to_dict(
                conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
            )

    def create_session(self, data):
        sid = str(uuid.uuid4())
        course_id = data.get("course_id")
        qr_code = None
        if course_id:
            course = self.get_course(course_id)
            if course:
                qr_code = f"smartattendance://course/{course.get('code', course_id)}?v=1"
        with self._connect() as conn:
            conn.execute(
                """INSERT OR IGNORE INTO sessions
                   (id, course_id, date, start_time, end_time, status, qr_code)
                   VALUES (?,?,?,?,?,?,?)""",
                (sid, course_id, data.get("date"), data.get("start_time"), data.get("end_time"), "active", qr_code),
            )
            # If a session already existed (IGNORE'd), return that one
            existing = conn.execute(
                "SELECT id FROM sessions WHERE course_id=? AND date=? AND start_time=?",
                (course_id, data.get("date"), data.get("start_time")),
            ).fetchone()
            final_id = existing["id"] if existing else sid
        return self.get_session(final_id)

    def update_session(self, session_id, data):
        fields = ", ".join(f"{k}=?" for k in data)
        values = list(data.values()) + [session_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE sessions SET {fields} WHERE id=?", values)
        return self.get_session(session_id)

    # ── Attendance Records ─────────────────────────────────────────────────────

    def get_attendance_records(self, date=None):
        import json
        query = "SELECT * FROM attendance WHERE 1=1"
        params = []
        if date:
            query += " AND timestamp LIKE ?"
            params.append(f"{date}%")
        with self._connect() as conn:
            rows = self._rows_to_list(conn.execute(query, params).fetchall())
        for r in rows:
            if r.get("verification_steps") and isinstance(r["verification_steps"], str):
                try:
                    r["verification_steps"] = json.loads(r["verification_steps"])
                except Exception:
                    pass
        return rows

    def create_attendance_record(self, data):
        import json
        rid = str(uuid.uuid4())
        vs = data.get("verification_steps")
        if isinstance(vs, dict):
            vs = json.dumps(vs)
        try:
            with self._connect() as conn:
                conn.execute(
                    """INSERT INTO attendance
                       (id, session_id, student_id, name, course_id, timestamp,
                        status, method, face_score, location_distance, is_flagged, flag_reason, verification_steps)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        rid, data.get("session_id"), data.get("student_id"), data.get("name"),
                        data.get("course_id"), data.get("timestamp", datetime.now().isoformat()),
                        data.get("status", "present"), data.get("method", "qr_face"),
                        data.get("face_score"), data.get("location_distance"),
                        1 if data.get("is_flagged") else 0, data.get("flag_reason"), vs,
                    ),
                )
        except sqlite3.IntegrityError:
            raise DuplicateAttendanceError(
                f"Student {data.get('student_id')} already marked present for session {data.get('session_id')}"
            )
        rows = self.get_attendance_records()
        return next((r for r in rows if r["id"] == rid), {"id": rid})

    def get_attendance_by_student(self, student_id):
        with self._connect() as conn:
            return self._rows_to_list(
                conn.execute("SELECT * FROM attendance WHERE student_id=?", (student_id,)).fetchall()
            )

    def update_attendance_record(self, record_id, update_data):
        fields = ", ".join(f"{k}=?" for k in update_data)
        values = list(update_data.values()) + [record_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE attendance SET {fields} WHERE id=?", values)
        with self._connect() as conn:
            return self._row_to_dict(
                conn.execute("SELECT * FROM attendance WHERE id=?", (record_id,)).fetchone()
            )

    def get_flagged_attendance(self):
        with self._connect() as conn:
            return self._rows_to_list(
                conn.execute("SELECT * FROM attendance WHERE is_flagged=1").fetchall()
            )

    # ── Attendance Steps ───────────────────────────────────────────────────────

    def get_attendance_step(self, step_id):
        with self._connect() as conn:
            return self._row_to_dict(
                conn.execute("SELECT * FROM attendance_steps WHERE id=?", (step_id,)).fetchone()
            )

    def create_attendance_step(self, data):
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO attendance_steps
                   (id, student_username, session_id, gps_verified, gps_timestamp,
                    gps_distance, face_verified, face_timestamp, face_score, expires_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    data["id"], data.get("student_username"), data.get("session_id"),
                    data.get("gps_verified", 0), data.get("gps_timestamp"),
                    data.get("gps_distance"), data.get("face_verified", 0),
                    data.get("face_timestamp"), data.get("face_score"), data.get("expires_at"),
                ),
            )
        return self.get_attendance_step(data["id"])

    def update_attendance_step(self, step_id, update_data):
        fields = ", ".join(f"{k}=?" for k in update_data)
        values = list(update_data.values()) + [step_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE attendance_steps SET {fields} WHERE id=?", values)
        return self.get_attendance_step(step_id)

    def delete_attendance_step(self, step_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM attendance_steps WHERE id=?", (step_id,))
        return True

    def delete_expired_attendance_steps(self):
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM attendance_steps WHERE expires_at < ?",
                (datetime.now().isoformat(),),
            )
            return cursor.rowcount

    # ── Cancellations ──────────────────────────────────────────────────────────

    def get_cancellations(self, course_id=None):
        query = "SELECT * FROM cancellations"
        params = []
        if course_id is not None:
            query += " WHERE course_id=?"
            params.append(course_id)
        with self._connect() as conn:
            return self._rows_to_list(conn.execute(query, params).fetchall())

    def create_cancellation(self, data):
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO cancellations (course_id, instructor_id, date, reason) VALUES (?,?,?,?)",
                (data.get("course_id"), data.get("instructor_id"), data.get("date"), data.get("reason")),
            )
            row = conn.execute("SELECT * FROM cancellations WHERE id=?", (cursor.lastrowid,)).fetchone()
            return self._row_to_dict(row)

    # ── Excuses ────────────────────────────────────────────────────────────────

    def get_excuses(self, student_id=None, course_id=None):
        query = "SELECT * FROM excuses WHERE 1=1"
        params = []
        if student_id:
            query += " AND student_id=?"
            params.append(student_id)
        if course_id is not None:
            query += " AND course_id=?"
            params.append(course_id)
        with self._connect() as conn:
            return self._rows_to_list(conn.execute(query, params).fetchall())

    def get_excuse(self, excuse_id):
        with self._connect() as conn:
            return self._row_to_dict(
                conn.execute("SELECT * FROM excuses WHERE id=?", (excuse_id,)).fetchone()
            )

    def create_excuse(self, data):
        eid = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO excuses
                   (id, student_id, course_id, session_date, excuse_type,
                    description, document_url, status, instructor_notes)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    eid, data["student_id"], data.get("course_id"), data.get("session_date"),
                    data.get("excuse_type", "other"), data.get("description", ""),
                    data.get("document_url", ""), data.get("status", "pending"),
                    data.get("instructor_notes", ""),
                ),
            )
        return self.get_excuse(eid)

    def update_excuse(self, excuse_id, update_data):
        fields = ", ".join(f"{k}=?" for k in update_data)
        values = list(update_data.values()) + [excuse_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE excuses SET {fields} WHERE id=?", values)
        return self.get_excuse(excuse_id)

    # ── Devices ────────────────────────────────────────────────────────────────

    def get_device(self, username: str, device_id: str) -> Optional[Dict]:
        with self._connect() as conn:
            return self._row_to_dict(
                conn.execute(
                    "SELECT * FROM devices WHERE username=? AND device_id=? AND is_active=1",
                    (username, device_id),
                ).fetchone()
            )

    def register_device(self, username: str, device_id: str, platform: str = None) -> Dict:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO devices (username, device_id, platform)
                   VALUES (?,?,?)
                   ON CONFLICT(username, device_id) DO UPDATE SET
                       last_seen_at=CURRENT_TIMESTAMP, is_active=1""",
                (username, device_id, platform),
            )
            row = conn.execute(
                "SELECT * FROM devices WHERE username=? AND device_id=?",
                (username, device_id),
            ).fetchone()
            return self._row_to_dict(row)

    def get_devices_for_user(self, username: str) -> List[Dict]:
        with self._connect() as conn:
            return self._rows_to_list(
                conn.execute(
                    "SELECT * FROM devices WHERE username=? AND is_active=1",
                    (username,),
                ).fetchall()
            )

    def revoke_device(self, username: str, device_id: str) -> bool:
        with self._connect() as conn:
            conn.execute(
                "UPDATE devices SET is_active=0 WHERE username=? AND device_id=?",
                (username, device_id),
            )
        return True

    # ── Health ─────────────────────────────────────────────────────────────────

    def health_check(self):
        try:
            with self._connect() as conn:
                conn.execute("SELECT 1").fetchone()
            return {"status": "ok", "driver": "sqlite", "path": self.db_path}
        except Exception as e:
            return {"status": "error", "error": str(e)}
