"""
MySQL database adapter for Smart Attendance System.
Uses mysql-connector-python for database operations.
"""

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
from .base import DatabaseAdapter


class MySQLAdapter(DatabaseAdapter):
    """MySQL implementation of DatabaseAdapter."""

    def __init__(self, host: str, database: str, user: str, password: str, port: int = 3306):
        """Initialize MySQL connection."""
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self._connection = None

    def _get_connection(self):
        """Get database connection."""
        if self._connection is None or not self._connection.is_connected():
            try:
                self._connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    port=self.port,
                    autocommit=False
                )
            except Error as e:
                raise Exception(f"MySQL connection failed: {e}")
        return self._connection

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[List[Dict[str, Any]]]:
        """Execute a query with optional parameters."""
        connection = self._get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return None
        except Error as e:
            connection.rollback()
            raise Exception(f"MySQL query failed: {e}")
        finally:
            cursor.close()

    def _create_tables(self):
        """Create all necessary tables if they don't exist."""
        # Users table
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # Students table
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                student_id VARCHAR(20) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                face_encoding TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        # Courses table
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_code VARCHAR(20) UNIQUE NOT NULL,
                course_name VARCHAR(100) NOT NULL,
                instructor_id INT,
                schedule TEXT,
                location VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        # Attendance table
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_out_time TIMESTAMP NULL,
                status ENUM('present', 'late', 'absent') DEFAULT 'present',
                location_lat DECIMAL(10, 8),
                location_lng DECIMAL(11, 8),
                verification_method ENUM('face', 'qr', 'manual') DEFAULT 'manual',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)

        # Sessions table
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL,
                session_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                location VARCHAR(100),
                qr_code TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)

        # Excuses table
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS excuses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT,
                excuse_date DATE NOT NULL,
                reason TEXT NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP NULL,
                reviewed_by INT,
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

    # User operations
    def create_user(self, username: str, email: str, password_hash: str, role: str = 'student') -> int:
        query = """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """
        self._execute_query(query, (username, email, password_hash, role))

        # Get the inserted user ID
        result = self._execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        return result[0]['id'] if result else 0

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE username = %s"
        result = self._execute_query(query, (username,), fetch=True)
        return result[0] if result else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = %s"
        result = self._execute_query(query, (email,), fetch=True)
        return result[0] if result else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE id = %s"
        result = self._execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None

    def update_user(self, user_id: int, **kwargs) -> bool:
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        self._execute_query(query, tuple(values))
        return True

    def delete_user(self, user_id: int) -> bool:
        query = "DELETE FROM users WHERE id = %s"
        self._execute_query(query, (user_id,))
        return True

    def get_all_users(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return self._execute_query(query, fetch=True) or []

    # Student operations
    def create_student(self, student_id: str, first_name: str, last_name: str, email: str = None,
                      phone: str = None, user_id: int = None) -> int:
        query = """
            INSERT INTO students (user_id, student_id, first_name, last_name, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self._execute_query(query, (user_id, student_id, first_name, last_name, email, phone))

        result = self._execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        return result[0]['id'] if result else 0

    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM students WHERE id = %s"
        result = self._execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None

    def get_student_by_student_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM students WHERE student_id = %s"
        result = self._execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None

    def update_student(self, student_id: int, **kwargs) -> bool:
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [student_id]

        query = f"UPDATE students SET {set_clause} WHERE id = %s"
        self._execute_query(query, tuple(values))
        return True

    def delete_student(self, student_id: int) -> bool:
        query = "DELETE FROM students WHERE id = %s"
        self._execute_query(query, (student_id,))
        return True

    def get_all_students(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM students ORDER BY created_at DESC"
        return self._execute_query(query, fetch=True) or []

    # Course operations
    def create_course(self, course_code: str, course_name: str, instructor_id: int = None,
                     schedule: str = None, location: str = None) -> int:
        query = """
            INSERT INTO courses (course_code, course_name, instructor_id, schedule, location)
            VALUES (%s, %s, %s, %s, %s)
        """
        self._execute_query(query, (course_code, course_name, instructor_id, schedule, location))

        result = self._execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        return result[0]['id'] if result else 0

    def get_course_by_id(self, course_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM courses WHERE id = %s"
        result = self._execute_query(query, (course_id,), fetch=True)
        return result[0] if result else None

    def get_course_by_code(self, course_code: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM courses WHERE course_code = %s"
        result = self._execute_query(query, (course_code,), fetch=True)
        return result[0] if result else None

    def update_course(self, course_id: int, **kwargs) -> bool:
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [course_id]

        query = f"UPDATE courses SET {set_clause} WHERE id = %s"
        self._execute_query(query, tuple(values))
        return True

    def delete_course(self, course_id: int) -> bool:
        query = "DELETE FROM courses WHERE id = %s"
        self._execute_query(query, (course_id,))
        return True

    def get_all_courses(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM courses ORDER BY created_at DESC"
        return self._execute_query(query, fetch=True) or []

    # Attendance operations
    def create_attendance(self, student_id: int, course_id: int, status: str = 'present',
                         location_lat: float = None, location_lng: float = None,
                         verification_method: str = 'manual', notes: str = None) -> int:
        query = """
            INSERT INTO attendance (student_id, course_id, status, location_lat, location_lng, verification_method, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self._execute_query(query, (student_id, course_id, status, location_lat, location_lng, verification_method, notes))

        result = self._execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        return result[0]['id'] if result else 0

    def get_attendance_by_id(self, attendance_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM attendance WHERE id = %s"
        result = self._execute_query(query, (attendance_id,), fetch=True)
        return result[0] if result else None

    def get_attendance_by_student_course(self, student_id: int, course_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM attendance WHERE student_id = %s AND course_id = %s ORDER BY check_in_time DESC"
        return self._execute_query(query, (student_id, course_id), fetch=True) or []

    def update_attendance(self, attendance_id: int, **kwargs) -> bool:
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [attendance_id]

        query = f"UPDATE attendance SET {set_clause} WHERE id = %s"
        self._execute_query(query, tuple(values))
        return True

    def get_all_attendance(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM attendance ORDER BY check_in_time DESC"
        return self._execute_query(query, fetch=True) or []

    # Session operations
    def create_session(self, course_id: int, session_date: str, start_time: str, end_time: str,
                      location: str = None, qr_code: str = None) -> int:
        query = """
            INSERT INTO sessions (course_id, session_date, start_time, end_time, location, qr_code)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self._execute_query(query, (course_id, session_date, start_time, end_time, location, qr_code))

        result = self._execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        return result[0]['id'] if result else 0

    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM sessions WHERE id = %s"
        result = self._execute_query(query, (session_id,), fetch=True)
        return result[0] if result else None

    def get_sessions_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM sessions WHERE course_id = %s ORDER BY session_date DESC, start_time DESC"
        return self._execute_query(query, (course_id,), fetch=True) or []

    def update_session(self, session_id: int, **kwargs) -> bool:
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [session_id]

        query = f"UPDATE sessions SET {set_clause} WHERE id = %s"
        self._execute_query(query, tuple(values))
        return True

    def delete_session(self, session_id: int) -> bool:
        query = "DELETE FROM sessions WHERE id = %s"
        self._execute_query(query, (session_id,))
        return True

    # Excuse operations
    def create_excuse(self, student_id: int, excuse_date: str, reason: str, course_id: int = None) -> int:
        query = """
            INSERT INTO excuses (student_id, course_id, excuse_date, reason)
            VALUES (%s, %s, %s, %s)
        """
        self._execute_query(query, (student_id, course_id, excuse_date, reason))

        result = self._execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        return result[0]['id'] if result else 0

    def get_excuse_by_id(self, excuse_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM excuses WHERE id = %s"
        result = self._execute_query(query, (excuse_id,), fetch=True)
        return result[0] if result else None

    def get_excuses_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM excuses WHERE student_id = %s ORDER BY submitted_at DESC"
        return self._execute_query(query, (student_id,), fetch=True) or []

    def update_excuse(self, excuse_id: int, **kwargs) -> bool:
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [excuse_id]

        query = f"UPDATE excuses SET {set_clause} WHERE id = %s"
        self._execute_query(query, tuple(values))
        return True

    def get_all_excuses(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM excuses ORDER BY submitted_at DESC"
        return self._execute_query(query, fetch=True) or []

    def close(self):
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()