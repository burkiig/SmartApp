-- =============================================
-- COURSE SCHEDULES TABLE - Ders Programı Tablosu
-- =============================================
-- Bu dosyayı Supabase SQL Editor'de çalıştırın

-- Ders programı tablosu
CREATE TABLE IF NOT EXISTS course_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Zaman bilgileri
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 1 AND day_of_week <= 5), -- 1=Pazartesi, 5=Cuma
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Ek bilgiler
    classroom TEXT, -- Sınıf bilgisi (CMP210, A101, vb.)
    notes TEXT,
    
    -- Dönem bilgisi
    academic_year TEXT NOT NULL,
    semester TEXT NOT NULL,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Çakışma kontrolü için unique constraint
    -- Aynı öğretmen, aynı gün, aynı saat, aynı dönemde iki ders olamaz
    CONSTRAINT unique_teacher_time_slot UNIQUE(teacher_id, day_of_week, start_time, academic_year, semester)
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_schedules_course ON course_schedules(course_id);
CREATE INDEX IF NOT EXISTS idx_schedules_teacher ON course_schedules(teacher_id);
CREATE INDEX IF NOT EXISTS idx_schedules_day ON course_schedules(day_of_week);
CREATE INDEX IF NOT EXISTS idx_schedules_active ON course_schedules(is_active);

-- Updated_at trigger
DROP TRIGGER IF EXISTS update_schedules_updated_at ON course_schedules;
CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON course_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- RLS POLICIES
-- =============================================

-- Enable RLS
ALTER TABLE course_schedules ENABLE ROW LEVEL SECURITY;

-- Admin: Tüm erişim
CREATE POLICY "Admins can do everything with schedules"
ON course_schedules FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.id = auth.uid()
    AND profiles.role = 'admin'
  )
);

-- Teacher: Kendi programını görebilir
CREATE POLICY "Teachers can view their own schedules"
ON course_schedules FOR SELECT
TO authenticated
USING (teacher_id = auth.uid());

-- Teacher: Kendi programına ders ekleyebilir
CREATE POLICY "Teachers can insert their own schedules"
ON course_schedules FOR INSERT
TO authenticated
WITH CHECK (
  teacher_id = auth.uid()
  AND EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.id = auth.uid()
    AND profiles.role IN ('teacher', 'admin')
  )
);

-- Teacher: Kendi programını güncelleyebilir
CREATE POLICY "Teachers can update their own schedules"
ON course_schedules FOR UPDATE
TO authenticated
USING (teacher_id = auth.uid())
WITH CHECK (teacher_id = auth.uid());

-- Teacher: Kendi programını silebilir (soft delete)
CREATE POLICY "Teachers can delete their own schedules"
ON course_schedules FOR DELETE
TO authenticated
USING (teacher_id = auth.uid());

-- =============================================
-- YARDIMCI FONKSIYON - Çakışma Kontrolü
-- =============================================

-- Zaman çakışması kontrol eden fonksiyon
CREATE OR REPLACE FUNCTION check_schedule_conflict(
  p_teacher_id UUID,
  p_day_of_week INTEGER,
  p_start_time TIME,
  p_end_time TIME,
  p_academic_year TEXT,
  p_semester TEXT,
  p_exclude_id UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
  conflict_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO conflict_count
  FROM course_schedules
  WHERE teacher_id = p_teacher_id
    AND day_of_week = p_day_of_week
    AND academic_year = p_academic_year
    AND semester = p_semester
    AND is_active = true
    AND (p_exclude_id IS NULL OR id != p_exclude_id)
    AND (
      -- Yeni ders, mevcut dersin içinde başlıyor
      (p_start_time >= start_time AND p_start_time < end_time)
      OR
      -- Yeni ders, mevcut dersin içinde bitiyor
      (p_end_time > start_time AND p_end_time <= end_time)
      OR
      -- Yeni ders, mevcut dersi kapsıyor
      (p_start_time <= start_time AND p_end_time >= end_time)
    );
  
  RETURN conflict_count > 0;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- TEST VERİSİ (Opsiyonel)
-- =============================================

-- Test için örnek ders programı eklemek isterseniz:
/*
-- Önce bir öğretmen kullanıcısı olduğundan emin olun
-- Sonra course_id'yi kendi dersinizin ID'si ile değiştirin

INSERT INTO course_schedules (
  course_id,
  teacher_id,
  day_of_week,
  start_time,
  end_time,
  classroom,
  academic_year,
  semester
) VALUES (
  'YOUR_COURSE_ID_HERE',
  (SELECT id FROM auth.users WHERE email = 'teacher@test.com'),
  1, -- Pazartesi
  '09:00:00',
  '10:50:00',
  'CMP210',
  '2024-2025',
  'Güz'
);
*/

-- Kontrol sorgusu
SELECT 
  cs.*,
  c.course_code,
  c.course_name,
  p.full_name as teacher_name
FROM course_schedules cs
JOIN courses c ON cs.course_id = c.id
JOIN profiles p ON cs.teacher_id = p.id
WHERE cs.is_active = true
ORDER BY cs.day_of_week, cs.start_time;


