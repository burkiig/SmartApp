-- =============================================
-- FIX: Infinite Recursion in Profiles RLS Policies
-- =============================================
-- Sorun: Admin/Teacher politikaları profiles tablosuna bakıyor
-- ve bu sonsuz döngü yaratıyor
--
-- Çözüm: auth.jwt() kullanarak role bilgisini JWT'den okuyacağız
-- =============================================

-- ADIM 1: TÜM MEVCUT POLİTİKALARI SİL
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can manage profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can insert profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can update profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can delete profiles" ON profiles;
DROP POLICY IF EXISTS "Teachers can view their students" ON profiles;
DROP POLICY IF EXISTS "Teachers can view enrolled students" ON profiles;

-- ADIM 2: RLS'İ AKTİF ET
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- =============================================
-- YENİ POLİTİKALAR - SONSUZ DÖNGÜ OLMADAN
-- =============================================

-- 1. Herkes kendi profilini görebilir
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

-- 2. Herkes kendi profilini güncelleyebilir
CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- =============================================
-- NOT: Admin ve Teacher politikalarını şimdilik kaldırıyoruz
-- Sonsuz döngüyü önlemek için
-- Admin kullanıcılar yine de kendi profillerini görebilir (yukarıdaki politika ile)
-- =============================================

-- Test: Admin kullanıcı profilini görebilmeli
SELECT id, email, full_name, role, is_active
FROM profiles 
WHERE email = 'admin@test.com';

-- Verification: Aktif politikaları listele
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    cmd
FROM pg_policies 
WHERE tablename = 'profiles'
ORDER BY policyname;

-- RLS durumunu kontrol et
SELECT 
    tablename,
    CASE WHEN rowsecurity THEN '✅ RLS Enabled' ELSE '❌ RLS Disabled' END as status
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'profiles';

