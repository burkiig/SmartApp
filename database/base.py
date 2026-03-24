"""
Abstract base class for database adapters
Defines the interface that all adapters must implement
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class DatabaseAdapter(ABC):
    """Abstract base class for database operations"""

    # ==================== STUDENTS ====================

    @abstractmethod
    def get_students(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_student(self, student_id: str, student_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_student(self, student_id: str) -> bool:
        pass

    # ==================== ATTENDANCE RECORDS ====================

    @abstractmethod
    def get_attendance_records(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get attendance records, optionally filtered by date"""
        pass

    @abstractmethod
    def create_attendance_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_attendance_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_attendance_record(self, record_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an attendance record (e.g., flag it for manual review)"""
        pass

    @abstractmethod
    def get_flagged_attendance(self) -> List[Dict[str, Any]]:
        """Return all attendance records where is_flagged=True"""
        pass

    # ==================== USERS ====================

    @abstractmethod
    def get_users(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_user(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_user(self, username: str) -> bool:
        pass

    # ==================== COURSES ====================

    @abstractmethod
    def get_courses(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_course(self, course_id: int) -> bool:
        pass

    # ==================== ROOMS ====================

    @abstractmethod
    def get_rooms(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_room(self, room_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_room(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_room(self, room_id: int) -> bool:
        pass

    # ==================== ATTENDANCE SESSIONS ====================

    @abstractmethod
    def get_sessions(
        self,
        course_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get attendance sessions, optionally filtered by course or status"""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a session — e.g., change status to 'closed'"""
        pass

    # ==================== CANCELLATIONS ====================

    @abstractmethod
    def get_cancellations(self, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_cancellation(self, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    # ==================== EXCUSES ====================

    @abstractmethod
    def get_excuses(
        self,
        student_id: Optional[str] = None,
        course_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_excuse(self, excuse_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_excuse(self, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_excuse(self, excuse_id: str, excuse_data: Dict[str, Any]) -> Dict[str, Any]:
        """Approve or reject an excuse"""
        pass

    # ==================== ATTENDANCE STEPS (3-step flow state) ====================

    @abstractmethod
    def get_attendance_step(self, step_id: str) -> Optional[Dict[str, Any]]:
        """Get a temporary attendance step record by ID."""
        pass

    @abstractmethod
    def create_attendance_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new attendance step record."""
        pass

    @abstractmethod
    def update_attendance_step(self, step_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on an existing attendance step (e.g. face_verified)."""
        pass

    @abstractmethod
    def delete_attendance_step(self, step_id: str) -> bool:
        """Delete a step record after QR verification completes."""
        pass

    @abstractmethod
    def delete_expired_attendance_steps(self) -> int:
        """
        Delete all attendance step records whose expires_at is in the past.
        Returns the number of deleted records.
        """
        pass

    # ==================== UTILITY ====================

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        pass
