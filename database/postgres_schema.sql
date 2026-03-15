-- Smart Attendance System - PostgreSQL schema
-- Run once to create tables and indexes (or use adapter auto-apply).

-- Students
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image TEXT,
    push_token TEXT,
    registered_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- Attendance records (attendance_logs)
CREATE TABLE IF NOT EXISTS attendance_logs (
    id UUID PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL,
    name VARCHAR(255),
    timestamp TIMESTAMPTZ NOT NULL,
    status VARCHAR(32) NOT NULL CHECK (status IN ('present', 'absent', 'late')),
    session_id VARCHAR(64),
    course_id INTEGER,
    verification_steps JSONB,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    face_confidence DOUBLE PRECISION,
    location JSONB,
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_attendance_logs_student_id ON attendance_logs(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_logs_timestamp ON attendance_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_attendance_logs_session_id ON attendance_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_logs_is_flagged ON attendance_logs(is_flagged);

-- Users
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(128) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL CHECK (role IN ('admin', 'instructor', 'student')),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    student_id VARCHAR(64),
    push_token TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Courses
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    instructor VARCHAR(255) NOT NULL,
    schedule JSONB,
    static_qr_code VARCHAR(255),
    enrolled_students JSONB DEFAULT '[]',
    room VARCHAR(255),
    students INTEGER,
    created_at TIMESTAMPTZ
);

-- Rooms
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity >= 1),
    type VARCHAR(32) NOT NULL CHECK (type IN ('classroom', 'lab', 'auditorium', 'other')),
    equipment TEXT,
    status VARCHAR(32) CHECK (status IN ('available', 'occupied', 'maintenance')),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geofence_radius INTEGER DEFAULT 50,
    created_at TIMESTAMPTZ
);

-- Attendance sessions
CREATE TABLE IF NOT EXISTS attendance_sessions (
    id UUID PRIMARY KEY,
    course_id INTEGER NOT NULL,
    date VARCHAR(16) NOT NULL,
    start_time VARCHAR(32),
    end_time VARCHAR(32),
    status VARCHAR(32) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'closed', 'cancelled')),
    qr_code VARCHAR(255),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_attendance_sessions_course_id ON attendance_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_attendance_sessions_status ON attendance_sessions(status);

-- Cancellations
CREATE TABLE IF NOT EXISTS cancellations (
    id UUID PRIMARY KEY,
    course_id INTEGER NOT NULL,
    instructor_id VARCHAR(128) NOT NULL,
    date VARCHAR(16) NOT NULL,
    reason TEXT NOT NULL,
    notified_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_cancellations_course_id ON cancellations(course_id);

-- Excuses
CREATE TABLE IF NOT EXISTS excuses (
    id UUID PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL,
    course_id INTEGER NOT NULL,
    session_date VARCHAR(16) NOT NULL,
    document_url TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    instructor_notes TEXT,
    submitted_at TIMESTAMPTZ,
    reviewed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_excuses_student_id ON excuses(student_id);
CREATE INDEX IF NOT EXISTS idx_excuses_course_id ON excuses(course_id);
