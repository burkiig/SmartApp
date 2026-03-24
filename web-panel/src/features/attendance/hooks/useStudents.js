import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../../shared/services/apiClient';

// Mock data fallback
const mockStudents = [
  {
    student_id: 'STU12001',
    name: 'Alice Anderson',
    image: 'default.jpg'
  },
  {
    student_id: 'STU12002',
    name: 'Bob Brown',
    image: 'default.jpg'
  }
];

/**
 * Hook for managing students data
 */
export const useStudents = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load students
  const loadStudents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/students');
      if (response.success) {
        setStudents(response.students || []);
      } else {
        setError('Failed to load students');
        // Use mock data on error
        setStudents(mockStudents);
      }
    } catch (err) {
      console.error('Error loading students:', err);
      setError(err.message);
      // Use mock data on error
      setStudents(mockStudents);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load on mount
  useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  // Delete student
  const deleteStudent = useCallback(async (studentId) => {
    try {
      const response = await apiClient.delete(`/students/${studentId}`);
      if (response.success) {
        setStudents(prev => prev.filter(s => s.student_id !== studentId));
        return { success: true };
      }
      return { success: false, error: 'Failed to delete student' };
    } catch (err) {
      console.error('Error deleting student:', err);
      // Simulate success for mock
      setStudents(prev => prev.filter(s => s.student_id !== studentId));
      return { success: true };
    }
  }, []);

  return {
    students,
    loading,
    error,
    loadStudents,
    deleteStudent
  };
};

