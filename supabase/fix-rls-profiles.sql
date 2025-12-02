-- =============================================
-- FIX: Profile RLS Policies - Allow users to read their own profile
-- =============================================

-- Bu script, kullanıcıların kendi profillerini okuyabilmesini sağlar
-- Otomatik çıkış yapma sorununu çözer

-- Önce mevcut politikaları kontrol et
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'profiles'
ORDER BY policyname;

-- Eğer "Users can view own profile" politikası yoksa veya çalışmıyorsa:

-- 1. Önce eski politikayı sil (varsa)
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;

-- 2. Yeniden oluştur (daha basit ve güvenilir)
CREATE POLICY "Users can view own profile"
    ON profiles 
    FOR SELECT
    USING (auth.uid() = id);

-- 3. Test et: Admin kullanıcı profilini görebilmeli
SELECT 
    id, 
    email, 
    full_name, 
    role, 
    is_active,
    created_at
FROM profiles 
WHERE email = 'admin@test.com';

-- 4. RLS'in aktif olduğunu kontrol et
SELECT 
    tablename,
    rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'profiles';

-- Eğer rowsecurity = false ise, RLS'i etkinleştir:
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 5. Tüm profil politikalarını listele
SELECT 
    policyname,
    cmd,
    CASE 
        WHEN qual IS NOT NULL THEN 'USING: ' || qual 
        ELSE 'No USING clause'
    END as using_clause,
    CASE 
        WHEN with_check IS NOT NULL THEN 'WITH CHECK: ' || with_check 
        ELSE 'No WITH CHECK clause'
    END as with_check_clause
FROM pg_policies 
WHERE tablename = 'profiles'
ORDER BY cmd, policyname;

-- =============================================
-- ALTERNATIF ÇÖZÜM: Tüm politikaları sil ve yeniden oluştur
-- =============================================

-- Sadece sorun devam ederse aşağıdaki kodu kullanın:

/*
-- Tüm profil politikalarını sil
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can manage profiles" ON profiles;
DROP POLICY IF EXISTS "Teachers can view their students" ON profiles;

-- Yeniden oluştur (basitleştirilmiş)
-- 1. Kullanıcılar kendi profilini görebilir
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

-- 2. Kullanıcılar kendi profilini güncelleyebilir
CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- 3. Adminler tüm profilleri görebilir
CREATE POLICY "Admins can view all profiles"
    ON profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- 4. Adminler profilleri yönetebilir
CREATE POLICY "Admins can insert profiles"
    ON profiles FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can update profiles"
    ON profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can delete profiles"
    ON profiles FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- 5. Öğretmenler kendi öğrencilerini görebilir
CREATE POLICY "Teachers can view enrolled students"
    ON profiles FOR SELECT
    USING (
        role = 'student' AND
        EXISTS (
            SELECT 1 FROM profiles teacher
            WHERE teacher.id = auth.uid() 
            AND teacher.role = 'teacher'
        ) AND
        EXISTS (
            SELECT 1 
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = profiles.id
            AND c.teacher_id = auth.uid()
        )
    );
*/

-- =============================================
-- VERIFICATION QUERIES
-- =============================================

-- Son kontrol: Profil sayıları
SELECT 
    role,
    COUNT(*) as count,
    COUNT(CASE WHEN is_active THEN 1 END) as active_count
FROM profiles
GROUP BY role
ORDER BY role;

-- RLS durumu
SELECT 
    tablename,
    CASE WHEN rowsecurity THEN '✅ Enabled' ELSE '❌ Disabled' END as rls_status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('profiles', 'courses', 'enrollments', 'attendance_sessions', 'attendance_records')
ORDER BY tablename;

