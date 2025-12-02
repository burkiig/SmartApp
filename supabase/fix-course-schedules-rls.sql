-- =============================================
-- COURSE SCHEDULES - RLS FIX
-- =============================================
-- Bu SQL'i Supabase SQL Editor'de çalıştırın

-- Önce tabloyu oluştur (eğer yoksa)
CREATE TABLE IF NOT EXISTS course_schedules (
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- İndeksler ekle (eğer yoksa)
CREATE INDEX IF NOT EXISTS idx_schedules_course ON course_schedules(course_id);
CREATE INDEX IF NOT EXISTS idx_schedules_teacher ON course_schedules(teacher_id);
CREATE INDEX IF NOT EXISTS idx_schedules_day ON course_schedules(day_of_week);
CREATE INDEX IF NOT EXISTS idx_schedules_active ON course_schedules(is_active);

-- Unique constraint ekle (eğer yoksa)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'unique_teacher_time_slot'
    ) THEN
        ALTER TABLE course_schedules 
        ADD CONSTRAINT unique_teacher_time_slot 
        UNIQUE(teacher_id, day_of_week, start_time, academic_year, semester);
    END IF;
END $$;

-- Updated_at trigger
DROP TRIGGER IF EXISTS update_schedules_updated_at ON course_schedules;
CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON course_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- RLS POLİTİKALARINI TEMİZLE VE YENİDEN OLUŞTUR
-- =============================================

-- RLS'i kapat
ALTER TABLE course_schedules DISABLE ROW LEVEL SECURITY;

-- Tüm mevcut politikaları sil
DROP POLICY IF EXISTS "Admins can do everything with schedules" ON course_schedules;
DROP POLICY IF EXISTS "Teachers can view their own schedules" ON course_schedules;
DROP POLICY IF EXISTS "Teachers can insert their own schedules" ON course_schedules;
DROP POLICY IF EXISTS "Teachers can update their own schedules" ON course_schedules;
DROP POLICY IF EXISTS "Teachers can delete their own schedules" ON course_schedules;

-- RLS'i tekrar aç
ALTER TABLE course_schedules ENABLE ROW LEVEL SECURITY;

-- YENİ POLİTİKALAR (Basitleştirilmiş)

-- 1. Admin: Her şeyi yapabilir
CREATE POLICY "admin_all_schedules"
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

-- 2. Teacher: Kendi programını görebilir
CREATE POLICY "teacher_select_own_schedules"
ON course_schedules
FOR SELECT
TO authenticated
USING (
  teacher_id = auth.uid()
  OR EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.id = auth.uid()
    AND profiles.role = 'admin'
  )
);

-- 3. Teacher: Kendi programına ders ekleyebilir
CREATE POLICY "teacher_insert_own_schedules"
ON course_schedules
FOR INSERT
TO authenticated
WITH CHECK (
  teacher_id = auth.uid()
);

-- 4. Teacher: Kendi programını güncelleyebilir
CREATE POLICY "teacher_update_own_schedules"
ON course_schedules
FOR UPDATE
TO authenticated
USING (teacher_id = auth.uid())
WITH CHECK (teacher_id = auth.uid());

-- 5. Teacher: Kendi programını silebilir
CREATE POLICY "teacher_delete_own_schedules"
ON course_schedules
FOR DELETE
TO authenticated
USING (teacher_id = auth.uid());

-- =============================================
-- KONTROL
-- =============================================

-- Politikaları kontrol et
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies 
WHERE tablename = 'course_schedules'
ORDER BY policyname;

-- Başarı mesajı
SELECT '✅ course_schedules tablosu ve RLS politikaları başarıyla oluşturuldu!' as status;


