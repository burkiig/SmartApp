"""
PostgreSQL database adapter
Implements DatabaseAdapter interface using PostgreSQL for storage
"""

import json
import os
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from .base import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database implementation"""

    def __init__(self, connection_url: str, min_conn: int = 1, max_conn: int = 5):
        self.connection_url = connection_url
        self._pool = pool.SimpleConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            dsn=connection_url
        )
        self._ensure_schema()

    def _get_conn(self):
        return self._pool.getconn()

    def _return_conn(self, conn):
        self._pool.putconn(conn)

    def _ensure_schema(self):
        """Create tables and indexes if they do not exist."""
        schema_path = os.path.join(os.path.dirname(__file__), 'postgres_schema.sql')
        if not os.path.exists(schema_path):
            return
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
        finally:
            self._return_conn(conn)

    @staticmethod
    def _row_to_dict(row: Optional[Dict]) -> Optional[Dict]:
        """Convert DB row to dict with serializable types (datetime -> ISO string, UUID -> str)."""
        if row is None:
            return None
        out = dict(row)
        for key, value in list(out.items()):
            if isinstance(value, datetime):
                out[key] = value.isoformat()
            elif hasattr(value, 'hex'):  # UUID
                out[key] = str(value)
        return out

    @staticmethod
    def _parse_ts(s: Any):
        """Parse timestamp from string or return datetime."""
        if s is None:
            return None
        if isinstance(s, datetime):
            return s
        if isinstance(s, str):
            try:
                return datetime.fromisoformat(s.replace('Z', '+00:00'))
            except ValueError:
                return None
        return s

    # ==================== STUDENTS ====================

    def get_students(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT student_id, name, image, push_token, registered_at, updated_at FROM students")
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT student_id, name, image, push_token, registered_at, updated_at FROM students WHERE student_id = %s",
                    (student_id,)
                )
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        student_id = student_data['student_id']
        reg = student_data.get('registered_at')
        if reg is None:
            reg = datetime.now()
        elif isinstance(reg, str):
            reg = self._parse_ts(reg)
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO students (student_id, name, image, push_token, registered_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (student_id) DO NOTHING""",
                    (
                        student_id,
                        student_data.get('name', ''),
                        student_data.get('image'),
                        student_data.get('push_token'),
                        reg,
                        None,
                    )
                )
                if cur.rowcount == 0:
                    raise ValueError(f"Student {student_id} already exists")
            conn.commit()
            return self.get_student(student_id)
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Student {student_id} already exists") from e
        finally:
            self._return_conn(conn)

    def update_student(self, student_id: str, student_data: Dict[str, Any]) -> Dict[str, Any]:
        student_data = {k: v for k, v in student_data.items() if k != 'student_id'}
        student_data['updated_at'] = datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cols = list(student_data.keys())
                vals = list(student_data.values())
                if not cols:
                    out = self.get_student(student_id)
                    if out is None:
                        raise ValueError(f"Student {student_id} not found")
                    return out
                set_clause = ', '.join(f"{c} = %s" for c in cols)
                cur.execute(
                    f"UPDATE students SET {set_clause} WHERE student_id = %s",
                    vals + [student_id]
                )
                if cur.rowcount == 0:
                    raise ValueError(f"Student {student_id} not found")
            conn.commit()
            return self.get_student(student_id)
        finally:
            self._return_conn(conn)

    def delete_student(self, student_id: str) -> bool:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
                n = cur.rowcount
            conn.commit()
            return n > 0
        finally:
            self._return_conn(conn)

    # ==================== ATTENDANCE RECORDS ====================

    def get_attendance_records(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if date:
                    cur.execute(
                        """SELECT id, student_id, name, timestamp, status, session_id, course_id,
                                  verification_steps, is_flagged, flag_reason, face_confidence, location, updated_at
                           FROM attendance_logs
                           WHERE timestamp::date = %s::date
                           ORDER BY timestamp""",
                        (date,)
                    )
                else:
                    cur.execute(
                        """SELECT id, student_id, name, timestamp, status, session_id, course_id,
                                  verification_steps, is_flagged, flag_reason, face_confidence, location, updated_at
                           FROM attendance_logs ORDER BY timestamp"""
                    )
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def create_attendance_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        rid = record_data.get('id') or str(uuid.uuid4())
        ts = record_data.get('timestamp') or datetime.now()
        if isinstance(ts, str):
            ts = self._parse_ts(ts) or datetime.now()
        is_flagged = record_data.get('is_flagged', False)
        verification_steps = record_data.get('verification_steps')
        location = record_data.get('location')
        if verification_steps is not None and not isinstance(verification_steps, str):
            verification_steps = json.dumps(verification_steps)
        if location is not None and not isinstance(location, str):
            location = json.dumps(location)
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO attendance_logs
                       (id, student_id, name, timestamp, status, session_id, course_id,
                        verification_steps, is_flagged, flag_reason, face_confidence, location)
                       VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s::jsonb)""",
                    (
                        rid,
                        record_data.get('student_id', ''),
                        record_data.get('name'),
                        ts,
                        record_data.get('status', 'present'),
                        record_data.get('session_id'),
                        record_data.get('course_id'),
                        verification_steps,
                        is_flagged,
                        record_data.get('flag_reason'),
                        record_data.get('face_confidence'),
                        location,
                    )
                )
            conn.commit()
            record_data['id'] = rid
            record_data['timestamp'] = ts.isoformat() if hasattr(ts, 'isoformat') else ts
            record_data['is_flagged'] = is_flagged
            return self._row_to_dict(record_data) if isinstance(record_data, dict) else record_data
        finally:
            self._return_conn(conn)

    def get_attendance_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, student_id, name, timestamp, status, session_id, course_id,
                              verification_steps, is_flagged, flag_reason, face_confidence, location, updated_at
                       FROM attendance_logs WHERE student_id = %s ORDER BY timestamp""",
                    (student_id,)
                )
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def update_attendance_record(self, record_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        update_data = dict(update_data)
        update_data['updated_at'] = datetime.now()
        verification_steps = update_data.get('verification_steps')
        location = update_data.get('location')
        if verification_steps is not None and not isinstance(verification_steps, str):
            update_data['verification_steps'] = json.dumps(verification_steps)
        if location is not None and not isinstance(location, str):
            update_data['location'] = json.dumps(location)
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cols = list(update_data.keys())
                set_clause = ', '.join(f"{c} = %s" for c in cols)
                vals = [update_data[c] for c in cols]
                cur.execute(
                    f"UPDATE attendance_logs SET {set_clause} WHERE id = %s::uuid",
                    vals + [record_id]
                )
                if cur.rowcount == 0:
                    raise ValueError(f"Attendance record {record_id} not found")
            conn.commit()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, student_id, name, timestamp, status, session_id, course_id, verification_steps, is_flagged, flag_reason, face_confidence, location, updated_at FROM attendance_logs WHERE id = %s::uuid",
                    (record_id,)
                )
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    def get_flagged_attendance(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, student_id, name, timestamp, status, session_id, course_id,
                              verification_steps, is_flagged, flag_reason, face_confidence, location, updated_at
                       FROM attendance_logs WHERE is_flagged = TRUE ORDER BY timestamp"""
                )
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    # ==================== USERS ====================

    def get_users(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT username, password, role, name, email, department, student_id, push_token, created_at, updated_at FROM users")
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT username, password, role, name, email, department, student_id, push_token, created_at, updated_at FROM users WHERE username = %s",
                    (username,)
                )
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        created = user_data.get('created_at') or datetime.now()
        if isinstance(created, str):
            created = self._parse_ts(created) or datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO users (username, password, role, name, email, department, student_id, push_token, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        user_data['username'],
                        user_data.get('password', ''),
                        user_data.get('role', 'student'),
                        user_data.get('name', ''),
                        user_data.get('email', ''),
                        user_data.get('department'),
                        user_data.get('student_id'),
                        user_data.get('push_token'),
                        created,
                        None,
                    )
                )
            conn.commit()
            return self.get_user(user_data['username'])
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"User {user_data.get('username')} already exists") from e
        finally:
            self._return_conn(conn)

    def update_user(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_data = {k: v for k, v in user_data.items() if k != 'username'}
        user_data['updated_at'] = datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cols = list(user_data.keys())
                set_clause = ', '.join(f"{c} = %s" for c in cols)
                vals = [user_data[c] for c in cols]
                cur.execute(f"UPDATE users SET {set_clause} WHERE username = %s", vals + [username])
                if cur.rowcount == 0:
                    raise ValueError(f"User {username} not found")
            conn.commit()
            return self.get_user(username)
        finally:
            self._return_conn(conn)

    def delete_user(self, username: str) -> bool:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE username = %s", (username,))
                n = cur.rowcount
            conn.commit()
            return n > 0
        finally:
            self._return_conn(conn)

    # ==================== COURSES ====================

    def get_courses(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, code, name, instructor, schedule, static_qr_code, enrolled_students, room, students, created_at FROM courses ORDER BY id")
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, code, name, instructor, schedule, static_qr_code, enrolled_students, room, students, created_at FROM courses WHERE id = %s",
                    (course_id,)
                )
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        schedule = course_data.get('schedule')
        enrolled = course_data.get('enrolled_students', [])
        if schedule is not None and not isinstance(schedule, str):
            schedule = json.dumps(schedule)
        if not isinstance(enrolled, str):
            enrolled = json.dumps(enrolled)
        static_qr = course_data.get('static_qr_code') or str(uuid.uuid4())
        created = course_data.get('created_at') or datetime.now()
        if isinstance(created, str):
            created = self._parse_ts(created) or datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO courses (code, name, instructor, schedule, static_qr_code, enrolled_students, room, students, created_at)
                       VALUES (%s, %s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s) RETURNING id""",
                    (
                        course_data.get('code', ''),
                        course_data.get('name', ''),
                        course_data.get('instructor', ''),
                        schedule,
                        static_qr,
                        enrolled,
                        course_data.get('room'),
                        course_data.get('students'),
                        created,
                    )
                )
                row = cur.fetchone()
                new_id = row[0]
            conn.commit()
            return self.get_course(new_id)
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Course code {course_data.get('code')} already exists") from e
        finally:
            self._return_conn(conn)

    def delete_course(self, course_id: int) -> bool:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
                n = cur.rowcount
            conn.commit()
            return n > 0
        finally:
            self._return_conn(conn)

    # ==================== ROOMS ====================

    def get_rooms(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, name, capacity, type, equipment, status, latitude, longitude, geofence_radius, created_at FROM rooms ORDER BY id")
                rows = cur.fetchall()
            return [self._row_to_dict(dict(row)) for row in rows]
        finally:
            self._return_conn(conn)

    def get_room(self, room_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, name, capacity, type, equipment, status, latitude, longitude, geofence_radius, created_at FROM rooms WHERE id = %s",
                    (room_id,)
                )
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    def create_room(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        room_data = dict(room_data)
        room_data.setdefault('latitude', None)
        room_data.setdefault('longitude', None)
        room_data.setdefault('geofence_radius', 50)
        created = room_data.get('created_at') or datetime.now()
        if isinstance(created, str):
            created = self._parse_ts(created) or datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO rooms (name, capacity, type, equipment, status, latitude, longitude, geofence_radius, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (
                        room_data.get('name', ''),
                        room_data.get('capacity', 1),
                        room_data.get('type', 'classroom'),
                        room_data.get('equipment'),
                        room_data.get('status'),
                        room_data.get('latitude'),
                        room_data.get('longitude'),
                        room_data.get('geofence_radius', 50),
                        created,
                    )
                )
                new_id = cur.fetchone()[0]
            conn.commit()
            return self.get_room(new_id)
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Room name {room_data.get('name')} already exists") from e
        finally:
            self._return_conn(conn)

    def delete_room(self, room_id: int) -> bool:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
                n = cur.rowcount
            conn.commit()
            return n > 0
        finally:
            self._return_conn(conn)

    # ==================== ATTENDANCE SESSIONS ====================

    def get_sessions(
        self,
        course_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                q = "SELECT id, course_id, date, start_time, end_time, status, qr_code, created_at, updated_at FROM attendance_sessions WHERE 1=1"
                params = []
                if course_id is not None:
                    q += " AND course_id = %s"
                    params.append(course_id)
                if status:
                    q += " AND status = %s"
                    params.append(status)
                q += " ORDER BY date, start_time"
                cur.execute(q, params or None)
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, course_id, date, start_time, end_time, status, qr_code, created_at, updated_at FROM attendance_sessions WHERE id = %s::uuid",
                    (session_id,)
                )
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        sid = session_data.get('id') or str(uuid.uuid4())
        status = session_data.get('status', 'active')
        qr_code = session_data.get('qr_code') or str(uuid.uuid4())
        created = session_data.get('created_at') or datetime.now()
        if isinstance(created, str):
            created = self._parse_ts(created) or datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO attendance_sessions (id, course_id, date, start_time, end_time, status, qr_code, created_at, updated_at)
                       VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        sid,
                        session_data.get('course_id'),
                        session_data.get('date', ''),
                        session_data.get('start_time'),
                        session_data.get('end_time'),
                        status,
                        qr_code,
                        created,
                        None,
                    )
                )
            conn.commit()
            return self.get_session(sid)
        finally:
            self._return_conn(conn)

    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        session_data = dict(session_data)
        session_data['updated_at'] = datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cols = [k for k in session_data.keys() if k != 'id']
                if not cols:
                    return self.get_session(session_id)
                set_clause = ', '.join(f"{c} = %s" for c in cols)
                vals = [session_data[c] for c in cols]
                cur.execute(f"UPDATE attendance_sessions SET {set_clause} WHERE id = %s::uuid", vals + [session_id])
                if cur.rowcount == 0:
                    raise ValueError(f"Session {session_id} not found")
            conn.commit()
            return self.get_session(session_id)
        finally:
            self._return_conn(conn)

    # ==================== CANCELLATIONS ====================

    def get_cancellations(self, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if course_id is not None:
                    cur.execute(
                        "SELECT id, course_id, instructor_id, date, reason, notified_at FROM cancellations WHERE course_id = %s ORDER BY date",
                        (course_id,)
                    )
                else:
                    cur.execute("SELECT id, course_id, instructor_id, date, reason, notified_at FROM cancellations ORDER BY date")
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def create_cancellation(self, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        cid = cancellation_data.get('id') or str(uuid.uuid4())
        notified = cancellation_data.get('notified_at') or datetime.now()
        if isinstance(notified, str):
            notified = self._parse_ts(notified) or datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO cancellations (id, course_id, instructor_id, date, reason, notified_at)
                       VALUES (%s::uuid, %s, %s, %s, %s, %s)""",
                    (
                        cid,
                        cancellation_data.get('course_id'),
                        cancellation_data.get('instructor_id', ''),
                        cancellation_data.get('date', ''),
                        cancellation_data.get('reason', ''),
                        notified,
                    )
                )
            conn.commit()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, course_id, instructor_id, date, reason, notified_at FROM cancellations WHERE id = %s::uuid", (cid,))
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    # ==================== EXCUSES ====================

    def get_excuses(
        self,
        student_id: Optional[str] = None,
        course_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                q = "SELECT id, student_id, course_id, session_date, document_url, status, instructor_notes, submitted_at, reviewed_at FROM excuses WHERE 1=1"
                params = []
                if student_id:
                    q += " AND student_id = %s"
                    params.append(student_id)
                if course_id is not None:
                    q += " AND course_id = %s"
                    params.append(course_id)
                q += " ORDER BY submitted_at"
                cur.execute(q, params or None)
                rows = cur.fetchall()
            return [self._row_to_dict(dict(r)) for r in rows]
        finally:
            self._return_conn(conn)

    def get_excuse(self, excuse_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, student_id, course_id, session_date, document_url, status, instructor_notes, submitted_at, reviewed_at FROM excuses WHERE id = %s::uuid",
                    (excuse_id,)
                )
                row = cur.fetchone()
            return self._row_to_dict(dict(row)) if row else None
        finally:
            self._return_conn(conn)

    def create_excuse(self, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        eid = excuse_data.get('id') or str(uuid.uuid4())
        status = excuse_data.get('status', 'pending')
        submitted = excuse_data.get('submitted_at') or datetime.now()
        if isinstance(submitted, str):
            submitted = self._parse_ts(submitted) or datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO excuses (id, student_id, course_id, session_date, document_url, status, instructor_notes, submitted_at, reviewed_at)
                       VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        eid,
                        excuse_data.get('student_id', ''),
                        excuse_data.get('course_id'),
                        excuse_data.get('session_date', ''),
                        excuse_data.get('document_url'),
                        status,
                        excuse_data.get('instructor_notes'),
                        submitted,
                        None,
                    )
                )
            conn.commit()
            return self.get_excuse(eid)
        finally:
            self._return_conn(conn)

    def update_excuse(self, excuse_id: str, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        excuse_data = dict(excuse_data)
        excuse_data['reviewed_at'] = datetime.now()
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cols = [k for k in excuse_data.keys() if k != 'id']
                if not cols:
                    return self.get_excuse(excuse_id)
                set_clause = ', '.join(f"{c} = %s" for c in cols)
                vals = [excuse_data[c] for c in cols]
                cur.execute(f"UPDATE excuses SET {set_clause} WHERE id = %s::uuid", vals + [excuse_id])
                if cur.rowcount == 0:
                    raise ValueError(f"Excuse {excuse_id} not found")
            conn.commit()
            return self.get_excuse(excuse_id)
        finally:
            self._return_conn(conn)

    # ==================== UTILITY ====================

    def health_check(self) -> Dict[str, Any]:
        conn = None
        try:
            conn = self._get_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return {
                'status': 'healthy',
                'type': 'postgresql',
                'connected': True
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'type': 'postgresql',
                'error': str(e),
                'connected': False
            }
        finally:
            if conn:
                self._return_conn(conn)
