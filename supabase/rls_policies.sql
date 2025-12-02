-- =============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- =============================================
-- PROFILES POLICIES
-- =============================================

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- Admins can view all profiles
CREATE POLICY "Admins can view all profiles"
    ON profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admins can insert/update/delete profiles
CREATE POLICY "Admins can manage profiles"
    ON profiles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Teachers can view students in their courses
CREATE POLICY "Teachers can view their students"
    ON profiles FOR SELECT
    USING (
        role = 'student' AND
        EXISTS (
            SELECT 1 FROM profiles p
            WHERE p.id = auth.uid() AND p.role = 'teacher'
        ) AND
        EXISTS (
            SELECT 1 FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = profiles.id
            AND c.teacher_id = auth.uid()
        )
    );

-- =============================================
-- COURSES POLICIES
-- =============================================

-- Teachers can view and manage their own courses
CREATE POLICY "Teachers can view own courses"
    ON courses FOR SELECT
    USING (teacher_id = auth.uid());

CREATE POLICY "Teachers can create courses"
    ON courses FOR INSERT
    WITH CHECK (
        teacher_id = auth.uid() AND
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role IN ('teacher', 'admin')
        )
    );

CREATE POLICY "Teachers can update own courses"
    ON courses FOR UPDATE
    USING (teacher_id = auth.uid());

CREATE POLICY "Teachers can delete own courses"
    ON courses FOR DELETE
    USING (teacher_id = auth.uid());

-- Students can view courses they're enrolled in
CREATE POLICY "Students can view enrolled courses"
    ON courses FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM enrollments
            WHERE course_id = courses.id
            AND student_id = auth.uid()
        )
    );

-- Admins can view all courses
CREATE POLICY "Admins can manage all courses"
    ON courses FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- ENROLLMENTS POLICIES
-- =============================================

-- Teachers can manage enrollments for their courses
CREATE POLICY "Teachers can manage course enrollments"
    ON enrollments FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM courses
            WHERE id = enrollments.course_id
            AND teacher_id = auth.uid()
        )
    );

-- Students can view their own enrollments
CREATE POLICY "Students can view own enrollments"
    ON enrollments FOR SELECT
    USING (student_id = auth.uid());

-- Admins can manage all enrollments
CREATE POLICY "Admins can manage all enrollments"
    ON enrollments FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- ATTENDANCE SESSIONS POLICIES
-- =============================================

-- Teachers can manage their course sessions
CREATE POLICY "Teachers can manage own sessions"
    ON attendance_sessions FOR ALL
    USING (teacher_id = auth.uid());

-- Students can view active sessions for enrolled courses
CREATE POLICY "Students can view active sessions"
    ON attendance_sessions FOR SELECT
    USING (
        is_active = true AND
        EXISTS (
            SELECT 1 FROM enrollments
            WHERE course_id = attendance_sessions.course_id
            AND student_id = auth.uid()
        )
    );

-- Admins can manage all sessions
CREATE POLICY "Admins can manage all sessions"
    ON attendance_sessions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- ATTENDANCE RECORDS POLICIES
-- =============================================

-- Students can create their own attendance records
CREATE POLICY "Students can create own records"
    ON attendance_records FOR INSERT
    WITH CHECK (student_id = auth.uid());

-- Students can view their own attendance records
CREATE POLICY "Students can view own records"
    ON attendance_records FOR SELECT
    USING (student_id = auth.uid());

-- Teachers can view records for their course sessions
CREATE POLICY "Teachers can view course records"
    ON attendance_records FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM attendance_sessions s
            WHERE s.id = attendance_records.session_id
            AND s.teacher_id = auth.uid()
        )
    );

-- Teachers can update records for their sessions
CREATE POLICY "Teachers can update course records"
    ON attendance_records FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM attendance_sessions s
            WHERE s.id = attendance_records.session_id
            AND s.teacher_id = auth.uid()
        )
    );

-- Admins can manage all records
CREATE POLICY "Admins can manage all records"
    ON attendance_records FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- AUDIT LOGS POLICIES
-- =============================================

-- Only admins can view audit logs
CREATE POLICY "Admins can view audit logs"
    ON audit_logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

