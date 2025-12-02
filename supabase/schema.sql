-- =============================================
-- SMART ATTENDANCE SYSTEM - DATABASE SCHEMA
-- =============================================

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- ENUM TYPES
-- =============================================

CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');
CREATE TYPE attendance_status AS ENUM ('present', 'absent', 'late', 'excused');
CREATE TYPE verification_method AS ENUM ('qr', 'gps', 'face', 'device');

-- =============================================
-- PROFILES TABLE
-- =============================================

CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    phone TEXT,
    student_number TEXT UNIQUE,
    face_image_url TEXT,
    device_uuid TEXT,
    is_active BOOLEAN DEFAULT true,
    consent_given BOOLEAN DEFAULT false,
    consent_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profiles_role ON profiles(role);
CREATE INDEX idx_profiles_student_number ON profiles(student_number);

-- =============================================
-- COURSES TABLE
-- =============================================

CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    description TEXT,
    academic_year TEXT NOT NULL,
    semester TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_courses_teacher ON courses(teacher_id);
CREATE INDEX idx_courses_code ON courses(course_code);

-- =============================================
-- COURSE ENROLLMENTS
-- =============================================

CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, student_id)
);

CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);

-- =============================================
-- ATTENDANCE SESSIONS
-- =============================================

CREATE TABLE attendance_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES profiles(id),
    session_name TEXT NOT NULL,
    session_date DATE NOT NULL DEFAULT CURRENT_DATE,
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    qr_code TEXT UNIQUE,
    qr_expires_at TIMESTAMPTZ,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_radius INTEGER DEFAULT 100, -- meters
    is_active BOOLEAN DEFAULT true,
    require_face_recognition BOOLEAN DEFAULT true,
    require_gps BOOLEAN DEFAULT true,
    require_device_check BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_course ON attendance_sessions(course_id);
CREATE INDEX idx_sessions_active ON attendance_sessions(is_active);
CREATE INDEX idx_sessions_qr ON attendance_sessions(qr_code);

-- =============================================
-- ATTENDANCE RECORDS
-- =============================================

CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    status attendance_status NOT NULL DEFAULT 'present',
    check_in_time TIMESTAMPTZ DEFAULT NOW(),
    qr_verified BOOLEAN DEFAULT false,
    gps_verified BOOLEAN DEFAULT false,
    face_verified BOOLEAN DEFAULT false,
    device_verified BOOLEAN DEFAULT false,
    face_confidence_score DECIMAL(5, 2),
    submitted_lat DECIMAL(10, 8),
    submitted_lng DECIMAL(11, 8),
    distance_from_class DECIMAL(10, 2),
    device_uuid TEXT,
    verification_image_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, student_id)
);

CREATE INDEX idx_records_session ON attendance_records(session_id);
CREATE INDEX idx_records_student ON attendance_records(student_id);
CREATE INDEX idx_records_status ON attendance_records(status);

-- =============================================
-- AUDIT LOG
-- =============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id),
    action TEXT NOT NULL,
    table_name TEXT,
    record_id UUID,
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- =============================================
-- UPDATED_AT TRIGGER FUNCTION
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

