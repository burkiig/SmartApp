# 🚀 Supabase Kurulum Rehberi - Adım Adım

## Sorun
"Invalid login credentials" hatası alıyorsanız, henüz Supabase veritabanınız kurulmamış demektir.

## Çözüm (5-10 dakika)

### 📍 ADIM 1: Supabase Dashboard'a Gidin

1. Tarayıcınızda şu adresi açın:
   ```
   https://supabase.com/dashboard/project/yoprqlfctuwifbvwrirn
   ```

2. Supabase hesabınızla giriş yapın

---

### 📍 ADIM 2: Veritabanı Tablolarını Oluşturun

1. Sol menüden **SQL Editor** seçeneğine tıklayın
2. **+ New Query** butonuna tıklayın
3. Aşağıdaki **TÜM** SQL kodunu kopyalayıp yapıştırın:

```sql
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
    location_radius INTEGER DEFAULT 100,
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
```

4. **RUN** (veya Ctrl+Enter) butonuna basın
5. ✅ "Success" mesajını bekleyin (1-2 saniye)

---

### 📍 ADIM 3: Güvenlik Politikalarını Ekleyin

1. Yine **SQL Editor** içinde **+ New Query** yapın
2. Aşağıdaki SQL kodunu yapıştırın:

```sql
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

CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles"
    ON profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can manage profiles"
    ON profiles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

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

CREATE POLICY "Students can view enrolled courses"
    ON courses FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM enrollments
            WHERE course_id = courses.id
            AND student_id = auth.uid()
        )
    );

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

CREATE POLICY "Teachers can manage course enrollments"
    ON enrollments FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM courses
            WHERE id = enrollments.course_id
            AND teacher_id = auth.uid()
        )
    );

CREATE POLICY "Students can view own enrollments"
    ON enrollments FOR SELECT
    USING (student_id = auth.uid());

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

CREATE POLICY "Teachers can manage own sessions"
    ON attendance_sessions FOR ALL
    USING (teacher_id = auth.uid());

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

CREATE POLICY "Students can create own records"
    ON attendance_records FOR INSERT
    WITH CHECK (student_id = auth.uid());

CREATE POLICY "Students can view own records"
    ON attendance_records FOR SELECT
    USING (student_id = auth.uid());

CREATE POLICY "Teachers can view course records"
    ON attendance_records FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM attendance_sessions s
            WHERE s.id = attendance_records.session_id
            AND s.teacher_id = auth.uid()
        )
    );

CREATE POLICY "Teachers can update course records"
    ON attendance_records FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM attendance_sessions s
            WHERE s.id = attendance_records.session_id
            AND s.teacher_id = auth.uid()
        )
    );

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

CREATE POLICY "Admins can view audit logs"
    ON audit_logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );
```

3. **RUN** butonuna basın
4. ✅ "Success" mesajını bekleyin

---

### 📍 ADIM 4: İlk Admin Kullanıcısını Oluşturun

#### 4a. Authentication'da Kullanıcı Oluştur

1. Sol menüden **Authentication** > **Users** seçin
2. **Add User** > **Create new user** butonuna tıklayın
3. Şu bilgileri girin:
   - **Email**: `admin@test.com`
   - **Password**: `admin123456`
   - **Auto Confirm User**: ✅ **İŞARETLEYİN** (ÇOK ÖNEMLİ!)
4. **Create User** butonuna basın
5. Oluşan kullanıcının **User ID**'sini kopyalayın (örn: `a1b2c3d4-...`)

#### 4b. Profile Tablosuna Ekle

1. Tekrar **SQL Editor** > **+ New Query** açın
2. Aşağıdaki SQL'i yapıştırın (HİÇBİR ŞEYİ DEĞİŞTİRMEYİN):

```sql
-- Admin kullanıcıya profil ekle
INSERT INTO profiles (id, email, full_name, role, is_active, consent_given, consent_date)
VALUES (
  (SELECT id FROM auth.users WHERE email = 'admin@test.com'),
  'admin@test.com',
  'Test Admin',
  'admin',
  true,
  true,
  NOW()
)
ON CONFLICT (id) DO UPDATE SET
  role = 'admin',
  full_name = 'Test Admin',
  is_active = true,
  consent_given = true;

-- Kontrol et
SELECT id, email, full_name, role, is_active 
FROM profiles 
WHERE email = 'admin@test.com';
```

3. **RUN** yapın
4. ✅ Altta tabloda admin kullanıcıyı görmelisiniz

---

### 📍 ADIM 5: Storage Bucket'ları Oluşturun (Opsiyonel)

1. Sol menüden **Storage** seçin
2. **New Bucket** butonuna tıklayın
3. İlk bucket:
   - **Name**: `face-photos`
   - **Public**: ❌ KAPALI (Private)
   - **Create bucket**
4. İkinci bucket:
   - **Name**: `verification-photos`
   - **Public**: ❌ KAPALI (Private)
   - **Create bucket**

---

## ✅ Tamamlandı! Şimdi Giriş Yapabilirsiniz

1. Web panel'i yeniden yükleyin: http://localhost:5173
2. Giriş bilgileri:
   - **Email**: `admin@test.com`
   - **Şifre**: `admin123456`
3. **Giriş Yap** butonuna basın

---

## 🎉 Başarılı!

Artık sisteme giriş yapabilir ve:
- ✅ Dersler oluşturabilir
- ✅ Öğrenci ekleyebilir
- ✅ Yoklama oturumları başlatabilirsiniz

---

## ❓ Sorun mu Yaşıyorsunuz?

### Hata: "Only teachers and admins can access"
- **Çözüm**: ADIM 4b'yi tekrar yapın, profil tablosunda kullanıcı eksik

### Hata: "relation profiles does not exist"
- **Çözüm**: ADIM 2'yi tekrar yapın, tablolar oluşmamış

### Giriş sonrası beyaz ekran
- **Çözüm**: Tarayıcı konsolu (F12) açın ve hataları kontrol edin

---

**Daha fazla yardım için**: GETTING_STARTED.md dosyasına bakın

