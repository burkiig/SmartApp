# Web Panel Kurulum Rehberi

## 🔴 SORUN: Boş Sayfa Görünüyor

Web panel açıldığında boş sayfa görüyorsanız, aşağıdaki adımları takip edin.

---

## ✅ ÇÖZÜM ADIMLARI

### 1️⃣ `.env` Dosyası Oluşturun

`web-panel` klasörüne gidin ve `.env` adında yeni bir dosya oluşturun:

```bash
# Windows (PowerShell)
cd web-panel
New-Item .env
```

Dosyanın içeriği:

```env
VITE_SUPABASE_URL=https://bpkmxqtsobrcrnzsecex.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwa214cXRzb2JyY3JuenNlY2V4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDY0NjE4MiwiZXhwIjoyMDc2MjIyMTgyfQ.8icFEYQIfSBsYE7scMSHyMphNjRtHmiKT7P_R2PTiZ8
```

⚠️ **ÖNEMLİ:** Dosya adı tam olarak `.env` olmalı (başında nokta var!)

---

### 2️⃣ Supabase Veritabanını Kontrol Edin

1. Tarayıcınızda açın: https://supabase.com/dashboard
2. Projenizi seçin: `bpkmxqtsobrcrnzsecex`
3. Sol menüden **SQL Editor** seçin
4. Şu sorguyu çalıştırın:

```sql
-- Tabloları kontrol et
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Beklenen Sonuç:**
```
- attendance_records
- attendance_sessions
- audit_logs
- courses
- enrollments
- profiles
```

Eğer tablolar yoksa:

5. `../supabase/schema.sql` dosyasındaki **TÜM** kodu kopyalayın
6. SQL Editor'e yapıştırın ve **Run** tıklayın

---

### 3️⃣ Test Kullanıcısı Oluşturun

#### A) Authentication → Users

1. Sol menüden **Authentication** → **Users**
2. **Add User** → **Create new user**
3. Email: `admin@test.com`
4. Password: `admin123456`
5. **Auto Confirm User**: ✅ (İşaretli olmalı)
6. **Create User**

#### B) Profile Kaydı Ekleyin

SQL Editor'de:

```sql
-- Admin kullanıcıya profil ekle
INSERT INTO profiles (id, email, full_name, role, is_active, consent_given)
VALUES (
  (SELECT id FROM auth.users WHERE email = 'admin@test.com'),
  'admin@test.com',
  'Test Admin',
  'admin',
  true,
  true
)
ON CONFLICT (id) DO UPDATE SET
  role = 'admin',
  is_active = true;
```

---

### 4️⃣ RLS (Row Level Security) Politikalarını Ekleyin

SQL Editor'de `../supabase/rls_policies.sql` dosyasındaki tüm kodu çalıştırın.

Veya manuel olarak en azından bu politikayı ekleyin:

```sql
-- Profiles tablosuna herkesin kendi profilini okuma izni
CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

-- Teacher ve Admin'ler tüm profilleri görebilir
CREATE POLICY "Teachers and admins can view all profiles"
ON profiles FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM profiles
    WHERE id = auth.uid()
    AND role IN ('teacher', 'admin')
  )
);
```

---

### 5️⃣ Dev Server'ı Başlatın

```bash
cd web-panel
npm run dev
```

Tarayıcınızda: http://localhost:5173

---

## 🔍 HATA AYIKLAMA

### Console'u Kontrol Edin

Tarayıcıda **F12** basın → **Console** sekmesine gidin.

#### Göreceğiniz Mesajlar:

✅ **BAŞARILI:**
```
🔧 Supabase Config:
  URL: ✅ Set
  Key: ✅ Set
🔍 Session check: Not logged in
```

❌ **HATALI:**
```
❌ CRITICAL: Supabase credentials missing!
Please create web-panel/.env file
```
→ **ÇÖZÜM:** Adım 1'e dönün, `.env` dosyasını oluşturun

---

### Login Testi

1. `admin@test.com` / `admin123456` ile giriş yapın
2. Console'da görmeli:
```
🔍 Session check: Logged in
🔍 Loading profile for user: xxx-xxx-xxx
🔍 Profile data: { role: 'admin', ... }
✅ Access granted. Role: admin
```

❌ **Hata Görürseniz:**

**"Profile error: relation profiles does not exist"**
→ Adım 2'ye dönün, schema.sql'i çalıştırın

**"Profile data: null"**
→ Adım 3'e dönün, INSERT komutunu çalıştırın

**"Access denied. Role: student"**
→ Kullanıcı rolü student, teacher/admin yapın:
```sql
UPDATE profiles SET role = 'admin' WHERE email = 'admin@test.com';
```

---

## 📝 Ek Test Kullanıcıları

### Teacher Kullanıcısı

```sql
-- 1. Authentication User
-- Dashboard → Authentication → Add User
-- Email: teacher@test.com
-- Password: teacher123456

-- 2. Profile
INSERT INTO profiles (id, email, full_name, role, is_active, consent_given)
VALUES (
  (SELECT id FROM auth.users WHERE email = 'teacher@test.com'),
  'teacher@test.com',
  'Test Teacher',
  'teacher',
  true,
  true
);
```

### Student Kullanıcısı (Panel Erişimi YOK)

```sql
-- Student ekleyin (mobil app test için)
INSERT INTO profiles (id, email, full_name, role, student_number, is_active, consent_given)
VALUES (
  (SELECT id FROM auth.users WHERE email = 'student@test.com'),
  'student@test.com',
  'Test Student',
  'student',
  '2024001',
  true,
  true
);
```

---

## 🎯 Hızlı Kontrol Listesi

- [ ] `.env` dosyası oluşturuldu
- [ ] `VITE_SUPABASE_URL` ve `VITE_SUPABASE_ANON_KEY` ayarlandı
- [ ] Supabase'de tablolar var (6 tablo)
- [ ] Admin kullanıcı oluşturuldu
- [ ] Admin kullanıcının `profiles` kaydı var
- [ ] RLS politikaları eklendi
- [ ] Dev server başlatıldı
- [ ] Console'da hata yok
- [ ] Login başarılı

---

## 🆘 Hala Sorun mu Var?

Console'daki **TAM** hata mesajını ve ekran görüntüsünü paylaşın.

