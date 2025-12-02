-- Smart Attendance System
-- Teacher Kullanıcı Oluşturma Script'i
-- 
-- KULLANIM:
-- 1. Önce Supabase Dashboard → Authentication → Users → Add User
--    Email: teacher@test.com
--    Password: teacher123456
--    Auto Confirm: ✅
-- 
-- 2. Sonra bu SQL'i SQL Editor'de çalıştırın

-- Teacher kullanıcıya profil ekle
INSERT INTO profiles (id, email, full_name, role, is_active, consent_given, consent_date)
VALUES (
  (SELECT id FROM auth.users WHERE email = 'teacher@test.com'),
  'teacher@test.com',
  'Test Teacher',
  'teacher',
  true,
  true,
  NOW()
)
ON CONFLICT (id) DO UPDATE SET
  role = 'teacher',
  full_name = 'Test Teacher',
  is_active = true,
  consent_given = true;

-- Kontrol et
SELECT id, email, full_name, role, is_active 
FROM profiles 
WHERE email = 'teacher@test.com';

