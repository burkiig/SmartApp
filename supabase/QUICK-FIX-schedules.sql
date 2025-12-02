-- =============================================
-- HIZLI ÇÖZÜM: Course Schedules Tablosu
-- =============================================
-- Bu SQL'i Supabase SQL Editor'de çalıştırın

-- 1. Tabloyu tamamen sil ve yeniden oluştur
DROP TABLE IF EXISTS course_schedules CASCADE;

-- 2. Tabloyu yeniden oluştur
CREATE TABLE course_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 1 AND day_of_week <= 5),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    classroom TEXT,
    notes TEXT,
    academic_year TEXT NOT NULL,
    semester TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_teacher_time_slot UNIQUE(teacher_id, day_of_week, start_time, academic_year, semester)
);

-- 3. İndeksler
CREATE INDEX idx_schedules_course ON course_schedules(course_id);
CREATE INDEX idx_schedules_teacher ON course_schedules(teacher_id);
CREATE INDEX idx_schedules_day ON course_schedules(day_of_week);
CREATE INDEX idx_schedules_active ON course_schedules(is_active);

-- 4. Trigger
CREATE TRIGGER update_schedules_updated_at 
BEFORE UPDATE ON course_schedules
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- 5. RLS - Basit ve Güçlü
ALTER TABLE course_schedules ENABLE ROW LEVEL SECURITY;

-- Admin her şeyi yapabilir
CREATE POLICY "admin_full_access"
ON course_schedules
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.id = auth.uid()
    AND profiles.role = 'admin'
  )
);

-- Teacher sadece kendi kayıtlarını görebilir
CREATE POLICY "teacher_select"
ON course_schedules
FOR SELECT
TO authenticated
USING (teacher_id = auth.uid());

-- Teacher sadece kendi kayıtlarını ekleyebilir
CREATE POLICY "teacher_insert"
ON course_schedules
FOR INSERT
TO authenticated
WITH CHECK (teacher_id = auth.uid());

-- Teacher sadece kendi kayıtlarını güncelleyebilir
CREATE POLICY "teacher_update"
ON course_schedules
FOR UPDATE
TO authenticated
USING (teacher_id = auth.uid())
WITH CHECK (teacher_id = auth.uid());

-- Teacher sadece kendi kayıtlarını silebilir
CREATE POLICY "teacher_delete"
ON course_schedules
FOR DELETE
TO authenticated
USING (teacher_id = auth.uid());

-- 6. Kontrol
SELECT 
    'Tablo: ' || tablename as info,
    'Politika: ' || policyname as policy_name,
    cmd as operation
FROM pg_policies 
WHERE tablename = 'course_schedules';

-- Başarı mesajı
SELECT '✅ ✅ ✅ BAŞARILI! course_schedules tablosu hazır.' as result;





