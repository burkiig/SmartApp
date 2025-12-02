// Shared TypeScript types for the entire project

export type UserRole = 'student' | 'teacher' | 'admin'
export type AttendanceStatus = 'present' | 'absent' | 'late' | 'excused'
export type VerificationMethod = 'qr' | 'gps' | 'face' | 'device'

export interface Profile {
  id: string
  email: string
  full_name: string
  role: UserRole
  phone?: string
  student_number?: string
  face_image_url?: string
  device_uuid?: string
  is_active: boolean
  consent_given: boolean
  consent_date?: string
  created_at: string
  updated_at: string
}

export interface Course {
  id: string
  teacher_id: string
  course_code: string
  course_name: string
  description?: string
  academic_year: string
  semester: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Enrollment {
  id: string
  course_id: string
  student_id: string
  enrolled_at: string
}

export interface AttendanceSession {
  id: string
  course_id: string
  teacher_id: string
  session_name: string
  session_date: string
  start_time: string
  end_time?: string
  qr_code?: string
  qr_expires_at?: string
  location_lat?: number
  location_lng?: number
  location_radius: number
  is_active: boolean
  require_face_recognition: boolean
  require_gps: boolean
  require_device_check: boolean
  created_at: string
}

export interface AttendanceRecord {
  id: string
  session_id: string
  student_id: string
  status: AttendanceStatus
  check_in_time: string
  qr_verified: boolean
  gps_verified: boolean
  face_verified: boolean
  device_verified: boolean
  face_confidence_score?: number
  submitted_lat?: number
  submitted_lng?: number
  distance_from_class?: number
  device_uuid?: string
  verification_image_url?: string
  notes?: string
  created_at: string
}

export interface FaceVerificationResponse {
  success: boolean
  confidence: number
  isIdentical: boolean
  error?: string
}

export interface CourseSchedule {
  id: string
  course_id: string
  teacher_id: string
  day_of_week: number // 1=Pazartesi, 2=Salı, 3=Çarşamba, 4=Perşembe, 5=Cuma
  start_time: string // "08:30:00"
  end_time: string // "09:20:00"
  classroom?: string
  notes?: string
  academic_year: string
  semester: string
  is_active: boolean
  created_at: string
  updated_at: string
  
  // Join ile gelen ek bilgiler (opsiyonel)
  course?: Course
}

export interface TimeSlot {
  hour: number
  minute: number
  label: string // "08:30"
}

