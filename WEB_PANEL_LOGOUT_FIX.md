# 🔧 Otomatik Çıkış Yapma Sorununu Çözme

## Sorun
Web panele admin olarak giriş yapabiliyorsunuz ama **birkaç saniye sonra otomatik çıkış yapıyor**.

## Sebep
Bu sorun genellikle **Row Level Security (RLS)** politikalarının yanlış yapılandırılmasından kaynaklanır. Kullanıcı giriş yaptıktan sonra kendi profilini okumaya çalışır, ancak RLS politikası buna izin vermezse sistem otomatik çıkış yapar.

---

## ✅ Hızlı Çözüm (2 Dakika)

### ADIM 1: Supabase Dashboard'a Gidin
```
https://supabase.com/dashboard/project/yoprqlfctuwifbvwrirn
```

### ADIM 2: SQL Editor'de Bu Kodu Çalıştırın

1. Sol menüden **SQL Editor** seçin
2. **+ New Query** tıklayın
3. Aşağıdaki kodu yapıştırın:

```sql
-- Önce mevcut politikayı sil
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;

-- Yeniden oluştur
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

-- Test et
SELECT id, email, full_name, role, is_active
FROM profiles 
WHERE email = 'admin@test.com';
```

4. **RUN** butonuna basın
5. ✅ Altta admin kullanıcıyı görmelisiniz

### ADIM 3: Web Panel'i Yenileyin
1. Tarayıcıda web panel'i yenileyin (F5)
2. Tekrar giriş yapın: `admin@test.com` / `admin123456`
3. ✅ Artık içerde kalabilmelisiniz!

---

## 🔍 Detaylı Teşhis ve Çözüm

### Problemi Teşhis Etme

#### 1. Tarayıcı Konsolunu Açın
- Chrome/Edge: `F12` veya `Ctrl+Shift+I`
- Console sekmesine geçin

#### 2. Şu Hataları Arayın:
```
❌ Error loading profile: ...
⚠️ RLS policy issue detected
```

Eğer bu hataları görüyorsanız, RLS sorunu var demektir.

---

### Tam Çözüm (RLS Politikalarını Sıfırlama)

Eğer hızlı çözüm işe yaramadıysa:

1. **Supabase SQL Editor**'de aşağıdaki scripti çalıştırın:

```sql
-- =============================================
-- PROFILES TABLE - COMPLETE RLS RESET
-- =============================================

-- Tüm mevcut politikaları sil
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can manage profiles" ON profiles;
DROP POLICY IF EXISTS "Teachers can view their students" ON profiles;

-- RLS'i aktif et
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- =============================================
-- YENİDEN OLUŞTUR - BASİTLEŞTİRİLMİŞ
-- =============================================

-- 1. Kullanıcılar kendi profilini görebilir (EN ÖNEMLİ!)
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

-- 4. Adminler profil oluşturabilir
CREATE POLICY "Admins can insert profiles"
    ON profiles FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- 5. Adminler profilleri güncelleyebilir
CREATE POLICY "Admins can update profiles"
    ON profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- 6. Adminler profilleri silebilir
CREATE POLICY "Admins can delete profiles"
    ON profiles FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- VERIFICATION
-- =============================================

-- Politikaları kontrol et
SELECT policyname, cmd
FROM pg_policies 
WHERE tablename = 'profiles'
ORDER BY policyname;

-- RLS durumunu kontrol et
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'profiles';
```

2. **Scripti çalıştırdıktan sonra:**
   - Web panel'i tamamen kapatın
   - Tarayıcı cache'ini temizleyin (Ctrl+Shift+Delete)
   - Web panel'i tekrar açın ve giriş yapın

---

## 🛠️ Kod İyileştirmesi Yapıldı

AuthContext kodunda da bir iyileştirme yaptım. Artık RLS hatalarında kullanıcı hemen çıkış yapmıyor, sadece profil bilgisi yüklenmiyor. Bu şekilde daha az agresif bir davranış sergiliyor.

**Güncellenen Dosya:** `web-panel/src/contexts/AuthContext.tsx`

---

## ✅ Kontrol Listesi

Sorun çözüldüğünü şu şekilde anlayabilirsiniz:

- [ ] Web panel'e giriş yapabiliyorsunuz
- [ ] Dashboard'da "Hoş geldiniz, Test Admin" yazısını görüyorsunuz
- [ ] En az 30 saniye içerde kalabiliyorsunuz
- [ ] Sayfalar arası geçiş yapabiliyorsunuz (Dashboard, Courses, vb.)
- [ ] Tarayıcı konsolunda "✅ Access granted. Role: admin" görünüyor
- [ ] Hiçbir RLS hatası görmüyorsunuz

---

## 🔍 Hala Sorun mu Var?

### 1. Admin Kullanıcının Doğru Oluşturulduğunu Kontrol Edin

Supabase SQL Editor'de:
```sql
-- Admin kullanıcıyı kontrol et
SELECT 
    p.id,
    p.email,
    p.full_name,
    p.role,
    p.is_active,
    u.email as auth_email,
    u.email_confirmed_at
FROM profiles p
JOIN auth.users u ON p.id = u.id
WHERE p.email = 'admin@test.com';
```

Beklenen sonuç:
- ✅ role = 'admin'
- ✅ is_active = true
- ✅ email_confirmed_at = bir tarih (null değil!)

### 2. Email Onaylanmış mı?

Eğer `email_confirmed_at` NULL ise:

```sql
UPDATE auth.users
SET email_confirmed_at = NOW(),
    confirmed_at = NOW()
WHERE email = 'admin@test.com';
```

### 3. .env Dosyası Doğru mu?

`web-panel/.env` dosyasını kontrol edin:
```
VITE_SUPABASE_URL=https://yoprqlfctuwifbvwrirn.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Web Panel Yeniden Başlatın

```powershell
cd web-panel
npm run dev
```

---

## 📞 İlave Yardım

Eğer sorun devam ediyorsa:

1. Tarayıcı konsolundaki tam hata mesajını kaydedin
2. Supabase Dashboard > Logs > PostgREST logs kontrol edin
3. Auth logs'a bakın (Authentication > Logs)

---

## 🎯 Özet

| Adım | Eylem | Süre |
|------|-------|------|
| 1 | Supabase SQL Editor'de RLS politikasını düzelt | 1 dk |
| 2 | Web panel'i yenile ve tekrar giriş yap | 30 sn |
| 3 | Test et: 30+ saniye içerde kal | 1 dk |

**Toplam Süre:** ~3 dakika

---

✅ Düzeltme yapıldı! Şimdi test edin ve başarılı olursa bana bildirin! 🚀

