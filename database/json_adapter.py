"""
JSON file-based database adapter
Implements DatabaseAdapter interface using JSON files for storage
"""

import json
import os
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from .base import DatabaseAdapter


class JSONAdapter(DatabaseAdapter):
    """JSON file-based database implementation"""

    def __init__(self, base_dir: str = 'static'):
        self.base_dir = base_dir
        self.students_file      = os.path.join(base_dir, 'students.json')
        self.attendance_file    = os.path.join(base_dir, 'attendance', 'records.json')
        self.users_file         = os.path.join(base_dir, 'users.json')
        self.courses_file       = os.path.join(base_dir, 'courses.json')
        self.rooms_file         = os.path.join(base_dir, 'rooms.json')
        self.sessions_file      = os.path.join(base_dir, 'sessions.json')
        self.cancellations_file = os.path.join(base_dir, 'cancellations.json')
        self.excuses_file       = os.path.join(base_dir, 'excuses.json')

        os.makedirs(os.path.join(base_dir, 'attendance'), exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'excuses'), exist_ok=True)

        self._init_file(self.students_file,      {})
        self._init_file(self.attendance_file,    [])
        self._init_file(self.users_file,         {})
        self._init_file(self.courses_file,       [])
        self._init_file(self.rooms_file,         [])
        self._init_file(self.sessions_file,      [])
        self._init_file(self.cancellations_file, [])
        self._init_file(self.excuses_file,       [])

    def _init_file(self, filepath: str, default_data: Any):
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)

    def _read_json(self, filepath: str) -> Any:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if ('students' in filepath or 'users' in filepath) else []

    def _write_json(self, filepath: str, data: Any):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ==================== STUDENTS ====================

    def get_students(self) -> List[Dict[str, Any]]:
        return list(self._read_json(self.students_file).values())

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        return self._read_json(self.students_file).get(student_id)

    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        students = self._read_json(self.students_file)
        student_id = student_data['student_id']
        if 'registered_at' not in student_data:
            student_data['registered_at'] = datetime.now().isoformat()
        students[student_id] = student_data
        self._write_json(self.students_file, students)
        return student_data

    def update_student(self, student_id: str, student_data: Dict[str, Any]) -> Dict[str, Any]:
        students = self._read_json(self.students_file)
        if student_id not in students:
            raise ValueError(f"Student {student_id} not found")
        students[student_id].update(student_data)
        students[student_id]['updated_at'] = datetime.now().isoformat()
        self._write_json(self.students_file, students)
        return students[student_id]

    def delete_student(self, student_id: str) -> bool:
        students = self._read_json(self.students_file)
        if student_id in students:
            del students[student_id]
            self._write_json(self.students_file, students)
            return True
        return False

    # ==================== ATTENDANCE RECORDS ====================

    def get_attendance_records(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        records = self._read_json(self.attendance_file)
        if date:
            return [r for r in records if r.get('timestamp', '').startswith(date)]
        return records

    def create_attendance_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        records = self._read_json(self.attendance_file)
        if 'id' not in record_data:
            record_data['id'] = str(uuid.uuid4())
        if 'timestamp' not in record_data:
            record_data['timestamp'] = datetime.now().isoformat()
        if 'is_flagged' not in record_data:
            record_data['is_flagged'] = False
        records.append(record_data)
        self._write_json(self.attendance_file, records)
        return record_data

    def get_attendance_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        return [r for r in self._read_json(self.attendance_file) if r.get('student_id') == student_id]

    def update_attendance_record(self, record_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        records = self._read_json(self.attendance_file)
        for i, record in enumerate(records):
            if record.get('id') == record_id:
                records[i].update(update_data)
                records[i]['updated_at'] = datetime.now().isoformat()
                self._write_json(self.attendance_file, records)
                return records[i]
        raise ValueError(f"Attendance record {record_id} not found")

    def get_flagged_attendance(self) -> List[Dict[str, Any]]:
        return [r for r in self._read_json(self.attendance_file) if r.get('is_flagged') is True]

    # ==================== USERS ====================

    def get_users(self) -> List[Dict[str, Any]]:
        return list(self._read_json(self.users_file).values())

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        return self._read_json(self.users_file).get(username)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        users = self._read_json(self.users_file)
        user_data['created_at'] = datetime.now().isoformat()
        users[user_data['username']] = user_data
        self._write_json(self.users_file, users)
        return user_data

    def update_user(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        users = self._read_json(self.users_file)
        if username not in users:
            raise ValueError(f"User {username} not found")
        users[username].update(user_data)
        users[username]['updated_at'] = datetime.now().isoformat()
        self._write_json(self.users_file, users)
        return users[username]

    def delete_user(self, username: str) -> bool:
        users = self._read_json(self.users_file)
        if username in users:
            del users[username]
            self._write_json(self.users_file, users)
            return True
        return False

    # ==================== COURSES ====================

    def get_courses(self) -> List[Dict[str, Any]]:
        return self._read_json(self.courses_file)

    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        return next((c for c in self._read_json(self.courses_file) if c.get('id') == course_id), None)

    def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        courses = self._read_json(self.courses_file)
        course_data['id'] = max((c.get('id', 0) for c in courses), default=0) + 1
        if 'static_qr_code' not in course_data:
            course_data['static_qr_code'] = str(uuid.uuid4())
        if 'enrolled_students' not in course_data:
            course_data['enrolled_students'] = []
        course_data['created_at'] = datetime.now().isoformat()
        courses.append(course_data)
        self._write_json(self.courses_file, courses)
        return course_data

    def delete_course(self, course_id: int) -> bool:
        courses = self._read_json(self.courses_file)
        new_courses = [c for c in courses if c.get('id') != course_id]
        if len(new_courses) < len(courses):
            self._write_json(self.courses_file, new_courses)
            return True
        return False

    # ==================== ROOMS ====================

    def get_rooms(self) -> List[Dict[str, Any]]:
        return self._read_json(self.rooms_file)

    def get_room(self, room_id: int) -> Optional[Dict[str, Any]]:
        return next((r for r in self._read_json(self.rooms_file) if r.get('id') == room_id), None)

    def create_room(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        rooms = self._read_json(self.rooms_file)
        room_data['id'] = max((r.get('id', 0) for r in rooms), default=0) + 1
        room_data.setdefault('latitude', None)
        room_data.setdefault('longitude', None)
        room_data.setdefault('geofence_radius', 50)
        room_data['created_at'] = datetime.now().isoformat()
        rooms.append(room_data)
        self._write_json(self.rooms_file, rooms)
        return room_data

    def delete_room(self, room_id: int) -> bool:
        rooms = self._read_json(self.rooms_file)
        new_rooms = [r for r in rooms if r.get('id') != room_id]
        if len(new_rooms) < len(rooms):
            self._write_json(self.rooms_file, new_rooms)
            return True
        return False

    # ==================== ATTENDANCE SESSIONS ====================

    def get_sessions(
        self,
        course_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        sessions = self._read_json(self.sessions_file)
        if course_id is not None:
            sessions = [s for s in sessions if s.get('course_id') == course_id]
        if status:
            sessions = [s for s in sessions if s.get('status') == status]
        return sessions

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return next((s for s in self._read_json(self.sessions_file) if s.get('id') == session_id), None)

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        sessions = self._read_json(self.sessions_file)
        if 'id' not in session_data:
            session_data['id'] = str(uuid.uuid4())
        if 'status' not in session_data:
            session_data['status'] = 'active'
        if 'qr_code' not in session_data:
            session_data['qr_code'] = str(uuid.uuid4())
        session_data['created_at'] = datetime.now().isoformat()
        sessions.append(session_data)
        self._write_json(self.sessions_file, sessions)
        return session_data

    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        sessions = self._read_json(self.sessions_file)
        for i, session in enumerate(sessions):
            if session.get('id') == session_id:
                sessions[i].update(session_data)
                sessions[i]['updated_at'] = datetime.now().isoformat()
                self._write_json(self.sessions_file, sessions)
                return sessions[i]
        raise ValueError(f"Session {session_id} not found")

    # ==================== CANCELLATIONS ====================

    def get_cancellations(self, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        cancellations = self._read_json(self.cancellations_file)
        if course_id is not None:
            cancellations = [c for c in cancellations if c.get('course_id') == course_id]
        return cancellations

    def create_cancellation(self, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        cancellations = self._read_json(self.cancellations_file)
        if 'id' not in cancellation_data:
            cancellation_data['id'] = str(uuid.uuid4())
        cancellation_data['notified_at'] = datetime.now().isoformat()
        cancellations.append(cancellation_data)
        self._write_json(self.cancellations_file, cancellations)
        return cancellation_data

    # ==================== EXCUSES ====================

    def get_excuses(
        self,
        student_id: Optional[str] = None,
        course_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        excuses = self._read_json(self.excuses_file)
        if student_id:
            excuses = [e for e in excuses if e.get('student_id') == student_id]
        if course_id is not None:
            excuses = [e for e in excuses if e.get('course_id') == course_id]
        return excuses

    def get_excuse(self, excuse_id: str) -> Optional[Dict[str, Any]]:
        return next((e for e in self._read_json(self.excuses_file) if e.get('id') == excuse_id), None)

    def create_excuse(self, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        excuses = self._read_json(self.excuses_file)
        if 'id' not in excuse_data:
            excuse_data['id'] = str(uuid.uuid4())
        if 'status' not in excuse_data:
            excuse_data['status'] = 'pending'
        excuse_data['submitted_at'] = datetime.now().isoformat()
        excuses.append(excuse_data)
        self._write_json(self.excuses_file, excuses)
        return excuse_data

    def update_excuse(self, excuse_id: str, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        excuses = self._read_json(self.excuses_file)
        for i, excuse in enumerate(excuses):
            if excuse.get('id') == excuse_id:
                excuses[i].update(excuse_data)
                excuses[i]['reviewed_at'] = datetime.now().isoformat()
                self._write_json(self.excuses_file, excuses)
                return excuses[i]
        raise ValueError(f"Excuse {excuse_id} not found")

    # ==================== ATTENDANCE STEPS ====================

    def get_attendance_step(self, step_id: str) -> Optional[Dict[str, Any]]:
        steps = self._read_json(self._steps_file())
        return next((s for s in steps if s.get('id') == step_id), None)

    def create_attendance_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        steps = self._read_json(self._steps_file())
        steps = [s for s in steps if not (
            s.get('student_username') == step_data.get('student_username') and
            s.get('session_id') == step_data.get('session_id')
        )]
        steps.append(step_data)
        self._write_json(self._steps_file(), steps)
        return step_data

    def update_attendance_step(self, step_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        steps = self._read_json(self._steps_file())
        for i, s in enumerate(steps):
            if s.get('id') == step_id:
                steps[i].update(update_data)
                self._write_json(self._steps_file(), steps)
                return steps[i]
        raise ValueError(f"Step {step_id} not found")

    def delete_attendance_step(self, step_id: str) -> bool:
        steps = self._read_json(self._steps_file())
        new_steps = [s for s in steps if s.get('id') != step_id]
        self._write_json(self._steps_file(), new_steps)
        return True

    def delete_expired_attendance_steps(self) -> int:
        from datetime import datetime
        steps = self._read_json(self._steps_file())
        now = datetime.now().isoformat()
        valid = [s for s in steps if s.get('expires_at', '9999') >= now]
        deleted = len(steps) - len(valid)
        if deleted:
            self._write_json(self._steps_file(), valid)
        return deleted

    def _steps_file(self) -> str:
        path = os.path.join(self.base_dir, 'attendance_steps.json')
        self._init_file(path, [])
        return path

    # ==================== UTILITY ====================

    def health_check(self) -> Dict[str, Any]:
        try:
            files_ok = all(os.path.exists(f) for f in [
                self.students_file, self.attendance_file, self.users_file,
                self.courses_file, self.rooms_file,
                self.sessions_file, self.cancellations_file, self.excuses_file
            ])
            return {
                'status': 'healthy' if files_ok else 'degraded',
                'type': 'json',
                'files_accessible': files_ok,
                'base_dir': self.base_dir
            }
        except Exception as e:
            return {'status': 'unhealthy', 'type': 'json', 'error': str(e)}
