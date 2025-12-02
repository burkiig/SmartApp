-- Smart Attendance System
-- Admin Kullanıcı Oluşturma Script'i
-- 
-- KULLANIM:
-- 1. Önce Supabase Dashboard → Authentication → Users → Add User
--    Email: admin@test.com
--    Password: admin123456
--    Auto Confirm: ✅
-- 
-- 2. Sonra bu SQL'i SQL Editor'de çalıştırın

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

