"""
PostgreSQL database adapter
Implements DatabaseAdapter interface using PostgreSQL for storage
"""

import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from .base import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database implementation"""

    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.connection.autocommit = False  # We'll manage transactions manually
            print(f"Connected to PostgreSQL database: {self.database}")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise

    def _create_tables(self):
        """Create tables if they don't exist"""
        cursor = self.connection.cursor()

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                image TEXT,
                push_token VARCHAR(255),
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Users table (for authentication)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                code VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                instructor_id INTEGER,
                room_name VARCHAR(100),
                schedule JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                geofence_radius INTEGER DEFAULT 40
            )
        """)

        # Attendance sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                id VARCHAR(36) PRIMARY KEY,
                course_id INTEGER,
                room_name VARCHAR(100),
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                qr_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        # Attendance logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id VARCHAR(36) PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                name VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'present',
                session_id VARCHAR(36),
                course_id INTEGER,
                verification_steps JSONB,
                is_flagged BOOLEAN DEFAULT FALSE,
                flag_reason TEXT,
                face_confidence DECIMAL(5,4),
                location JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (session_id) REFERENCES attendance_sessions(id)
            )
        """)

        # Cancellations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cancellations (
                id VARCHAR(36) PRIMARY KEY,
                course_id INTEGER,
                reason TEXT,
                cancelled_by INTEGER,
                cancelled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        # Excuses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS excuses (
                id VARCHAR(36) PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                course_id INTEGER,
                reason TEXT,
                attachment_url TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                reviewed_by INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        self.connection.commit()
        cursor.close()

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a query with optional parameters"""
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]  # Convert to dict
            else:
                self.connection.commit()
                return cursor.rowcount
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    # ==================== STUDENTS ====================

    def get_students(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM students ORDER BY registered_at DESC"
        return self._execute_query(query, fetch=True)

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM students WHERE student_id = %s"
        result = self._execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None

    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        student_data['registered_at'] = datetime.now()
        columns = ', '.join(student_data.keys())
        placeholders = ', '.join(['%s'] * len(student_data))
        values = tuple(student_data.values())

        query = f"INSERT INTO students ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return student_data

    def update_student(self, student_id: str, student_data: Dict[str, Any]) -> Dict[str, Any]:
        student_data['updated_at'] = datetime.now()
        set_clause = ', '.join([f"{k} = %s" for k in student_data.keys()])
        values = tuple(student_data.values()) + (student_id,)

        query = f"UPDATE students SET {set_clause} WHERE student_id = %s"
        self._execute_query(query, values)
        return self.get_student(student_id)

    def delete_student(self, student_id: str) -> bool:
        query = "DELETE FROM students WHERE student_id = %s"
        return self._execute_query(query, (student_id,)) > 0

    # ==================== ATTENDANCE RECORDS ====================

    def get_attendance_records(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        if date:
            query = "SELECT * FROM attendance_logs WHERE DATE(timestamp) = %s ORDER BY timestamp DESC"
            return self._execute_query(query, (date,), fetch=True)
        else:
            query = "SELECT * FROM attendance_logs ORDER BY timestamp DESC"
            return self._execute_query(query, fetch=True)

    def create_attendance_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'id' not in record_data:
            record_data['id'] = str(uuid.uuid4())

        columns = ', '.join(record_data.keys())
        placeholders = ', '.join(['%s'] * len(record_data))
        values = tuple(record_data.values())

        query = f"INSERT INTO attendance_logs ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return record_data

    def get_attendance_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM attendance_logs WHERE student_id = %s ORDER BY timestamp DESC"
        return self._execute_query(query, (student_id,), fetch=True)

    def get_attendance_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM attendance_logs WHERE session_id = %s ORDER BY timestamp DESC"
        return self._execute_query(query, (session_id,), fetch=True)

    def update_attendance_record(self, record_id: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        set_clause = ', '.join([f"{k} = %s" for k in record_data.keys()])
        values = tuple(record_data.values()) + (record_id,)

        query = f"UPDATE attendance_logs SET {set_clause} WHERE id = %s"
        self._execute_query(query, values)
        return self.get_attendance_record(record_id)

    def get_attendance_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM attendance_logs WHERE id = %s"
        result = self._execute_query(query, (record_id,), fetch=True)
        return result[0] if result else None

    def delete_attendance_record(self, record_id: str) -> bool:
        query = "DELETE FROM attendance_logs WHERE id = %s"
        return self._execute_query(query, (record_id,)) > 0

    # ==================== USERS ====================

    def get_users(self) -> List[Dict[str, Any]]:
        query = "SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC"
        return self._execute_query(query, fetch=True)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT id, username, email, role, created_at FROM users WHERE id = %s"
        result = self._execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE username = %s"
        result = self._execute_query(query, (username,), fetch=True)
        return result[0] if result else None

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        columns = ', '.join(user_data.keys())
        placeholders = ', '.join(['%s'] * len(user_data))
        values = tuple(user_data.values())

        query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return user_data

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        set_clause = ', '.join([f"{k} = %s" for k in user_data.keys()])
        values = tuple(user_data.values()) + (user_id,)

        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        self._execute_query(query, values)
        return self.get_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        query = "DELETE FROM users WHERE id = %s"
        return self._execute_query(query, (user_id,)) > 0

    # ==================== COURSES ====================

    def get_courses(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM courses ORDER BY created_at DESC"
        return self._execute_query(query, fetch=True)

    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM courses WHERE id = %s"
        result = self._execute_query(query, (course_id,), fetch=True)
        return result[0] if result else None

    def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        columns = ', '.join(course_data.keys())
        placeholders = ', '.join(['%s'] * len(course_data))
        values = tuple(course_data.values())

        query = f"INSERT INTO courses ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return course_data

    def update_course(self, course_id: int, course_data: Dict[str, Any]) -> Dict[str, Any]:
        set_clause = ', '.join([f"{k} = %s" for k in course_data.keys()])
        values = tuple(course_data.values()) + (course_id,)

        query = f"UPDATE courses SET {set_clause} WHERE id = %s"
        self._execute_query(query, values)
        return self.get_course(course_id)

    def delete_course(self, course_id: int) -> bool:
        query = "DELETE FROM courses WHERE id = %s"
        return self._execute_query(query, (course_id,)) > 0

    # ==================== ROOMS ====================

    def get_rooms(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM rooms ORDER BY name"
        return self._execute_query(query, fetch=True)

    def get_room(self, room_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM rooms WHERE id = %s"
        result = self._execute_query(query, (room_id,), fetch=True)
        return result[0] if result else None

    def get_room_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM rooms WHERE name = %s"
        result = self._execute_query(query, (name,), fetch=True)
        return result[0] if result else None

    def create_room(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        columns = ', '.join(room_data.keys())
        placeholders = ', '.join(['%s'] * len(room_data))
        values = tuple(room_data.values())

        query = f"INSERT INTO rooms ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return room_data

    def update_room(self, room_id: int, room_data: Dict[str, Any]) -> Dict[str, Any]:
        set_clause = ', '.join([f"{k} = %s" for k in room_data.keys()])
        values = tuple(room_data.values()) + (room_id,)

        query = f"UPDATE rooms SET {set_clause} WHERE id = %s"
        self._execute_query(query, values)
        return self.get_room(room_id)

    def delete_room(self, room_id: int) -> bool:
        query = "DELETE FROM rooms WHERE id = %s"
        return self._execute_query(query, (room_id,)) > 0

    # ==================== ATTENDANCE SESSIONS ====================

    def get_attendance_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            query = "SELECT * FROM attendance_sessions WHERE status = %s ORDER BY start_time DESC"
            return self._execute_query(query, (status,), fetch=True)
        else:
            query = "SELECT * FROM attendance_sessions ORDER BY start_time DESC"
            return self._execute_query(query, fetch=True)

    def get_attendance_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM attendance_sessions WHERE id = %s"
        result = self._execute_query(query, (session_id,), fetch=True)
        return result[0] if result else None

    def create_attendance_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'id' not in session_data:
            session_data['id'] = str(uuid.uuid4())

        columns = ', '.join(session_data.keys())
        placeholders = ', '.join(['%s'] * len(session_data))
        values = tuple(session_data.values())

        query = f"INSERT INTO attendance_sessions ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return session_data

    def update_attendance_session(self, session_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        set_clause = ', '.join([f"{k} = %s" for k in session_data.keys()])
        values = tuple(session_data.values()) + (session_id,)

        query = f"UPDATE attendance_sessions SET {set_clause} WHERE id = %s"
        self._execute_query(query, values)
        return self.get_attendance_session(session_id)

    def delete_attendance_session(self, session_id: str) -> bool:
        query = "DELETE FROM attendance_sessions WHERE id = %s"
        return self._execute_query(query, (session_id,)) > 0

    # ==================== CANCELLATIONS ====================

    def get_cancellations(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM cancellations ORDER BY cancelled_at DESC"
        return self._execute_query(query, fetch=True)

    def get_cancellation(self, cancellation_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM cancellations WHERE id = %s"
        result = self._execute_query(query, (cancellation_id,), fetch=True)
        return result[0] if result else None

    def create_cancellation(self, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'id' not in cancellation_data:
            cancellation_data['id'] = str(uuid.uuid4())

        columns = ', '.join(cancellation_data.keys())
        placeholders = ', '.join(['%s'] * len(cancellation_data))
        values = tuple(cancellation_data.values())

        query = f"INSERT INTO cancellations ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return cancellation_data

    def update_cancellation(self, cancellation_id: str, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        set_clause = ', '.join([f"{k} = %s" for k in cancellation_data.keys()])
        values = tuple(cancellation_data.values()) + (cancellation_id,)

        query = f"UPDATE cancellations SET {set_clause} WHERE id = %s"
        self._execute_query(query, values)
        return self.get_cancellation(cancellation_id)

    def delete_cancellation(self, cancellation_id: str) -> bool:
        query = "DELETE FROM cancellations WHERE id = %s"
        return self._execute_query(query, (cancellation_id,)) > 0

    # ==================== EXCUSES ====================

    def get_excuses(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            query = "SELECT * FROM excuses WHERE status = %s ORDER BY submitted_at DESC"
            return self._execute_query(query, (status,), fetch=True)
        else:
            query = "SELECT * FROM excuses ORDER BY submitted_at DESC"
            return self._execute_query(query, fetch=True)

    def get_excuse(self, excuse_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM excuses WHERE id = %s"
        result = self._execute_query(query, (excuse_id,), fetch=True)
        return result[0] if result else None

    def get_excuses_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM excuses WHERE student_id = %s ORDER BY submitted_at DESC"
        return self._execute_query(query, (student_id,), fetch=True)

    def create_excuse(self, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'id' not in excuse_data:
            excuse_data['id'] = str(uuid.uuid4())

        columns = ', '.join(excuse_data.keys())
        placeholders = ', '.join(['%s'] * len(excuse_data))
        values = tuple(excuse_data.values())

        query = f"INSERT INTO excuses ({columns}) VALUES ({placeholders})"
        self._execute_query(query, values)
        return excuse_data

    def update_excuse(self, excuse_id: str, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        set_clause = ', '.join([f"{k} = %s" for k in excuse_data.keys()])
        values = tuple(excuse_data.values()) + (excuse_id,)

        query = f"UPDATE excuses SET {set_clause} WHERE id = %s"
        self._execute_query(query, values)
        return self.get_excuse(excuse_id)

    def delete_excuse(self, excuse_id: str) -> bool:
        query = "DELETE FROM excuses WHERE id = %s"
        return self._execute_query(query, (excuse_id,)) > 0

    def __del__(self):
        if self.connection and not self.connection.closed:
            self.connection.close()