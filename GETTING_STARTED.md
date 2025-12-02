# Başlangıç Rehberi - Smart Attendance System

Bu rehber, projeyi sıfırdan çalıştırmanız için adım adım yol gösterir.

## Ön Gereksinimler

### Gerekli Yazılımlar
- Node.js 18+ ([nodejs.org](https://nodejs.org))
- npm veya yarn
- Git
- Docker Desktop (local Supabase için)

### Mobil Geliştirme İçin
- Android Studio (Android için)
- Xcode (iOS için - sadece macOS)

## 1. Projeyi İndirme

```bash
git clone <repository-url>
cd "Smart Attendace System"
```

## 2. Supabase Setup

### Seçenek A: Cloud Supabase (Önerilen)

1. [supabase.com](https://supabase.com) hesabı oluşturun
2. "New Project" ile yeni proje oluşturun
3. Project Settings > API kısmından:
   - `URL` değerini kopyalayın
   - `anon/public` key'i kopyalayın

4. Veritabanı şemasını yükleyin:
   - Supabase Dashboard > SQL Editor
   - `supabase/schema.sql` içeriğini yapıştırıp çalıştırın
   - `supabase/rls_policies.sql` içeriğini yapıştırıp çalıştırın

5. Storage bucket'ları oluşturun:
   - Storage > New Bucket > `face-photos` (private)
   - Storage > New Bucket > `verification-photos` (private)

### Seçenek B: Local Supabase

```bash
# Supabase CLI yükle
npm install -g supabase

# Docker'ın çalıştığından emin olun
docker --version

# Local Supabase başlat
cd supabase
supabase start

# Credentials not edilecek (API URL ve keys)
```

## 3. Mobil Uygulama Setup

```bash
cd mobile-app

# Dependencies yükle
npm install

# .env dosyası oluştur
cat > .env << EOF
EXPO_PUBLIC_SUPABASE_URL=YOUR_SUPABASE_URL
EXPO_PUBLIC_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
EOF
```

### iOS Simulator'da Çalıştırma (macOS)
```bash
npm run ios
```

### Android Emulator'da Çalıştırma
```bash
npm run android
```

### Fiziksel Cihazda Çalıştırma
```bash
npm start
# QR kodu Expo Go uygulaması ile taratın
```

## 4. Web Panel Setup

```bash
cd web-panel

# Dependencies yükle
npm install

# .env dosyası oluştur
cat > .env << EOF
VITE_SUPABASE_URL=YOUR_SUPABASE_URL
VITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
EOF

# Development server başlat
npm run dev
```

Web panel: http://localhost:5173

## 5. İlk Kullanıcı Oluşturma

### Admin Kullanıcı

1. Supabase Dashboard > Authentication > Users > Add user
   - Email: `admin@test.com`
   - Password: `test123456`
   - Auto Confirm User: ✅

2. User ID'yi kopyalayın

3. SQL Editor'de:
```sql
INSERT INTO profiles (id, email, full_name, role)
VALUES (
  'COPIED_USER_ID',
  'admin@test.com',
  'Admin User',
  'admin'
);
```

### Eğitmen Kullanıcı

Aynı şekilde oluşturun, sadece `role = 'teacher'` olarak ayarlayın.

### Öğrenci Kullanıcı

```sql
INSERT INTO profiles (id, email, full_name, role, student_number)
VALUES (
  'COPIED_USER_ID',
  'student@test.com',
  'Test Student',
  'student',
  '2024001'
);
```

## 6. Test Verisi Oluşturma

```sql
-- Bir ders oluştur
INSERT INTO courses (teacher_id, course_code, course_name, academic_year, semester)
VALUES (
  'TEACHER_USER_ID',
  'CS101',
  'Introduction to Computer Science',
  '2024-2025',
  'Güz'
);

-- Öğrenciyi derse kaydet
INSERT INTO enrollments (course_id, student_id)
VALUES (
  'COURSE_ID_FROM_ABOVE',
  'STUDENT_USER_ID'
);
```

## 7. Edge Function Setup (Yüz Tanıma)

### Azure Face API Alma

1. [Azure Portal](https://portal.azure.com) > Create a resource
2. "Face" ara ve seç
3. Free tier (F0) seç
4. Deploy et
5. Keys and Endpoint kopyala

### Edge Function Deploy

```bash
cd supabase

# Functions deploy
supabase functions deploy face-verification

# Secrets ayarla
supabase secrets set AZURE_FACE_API_KEY=your_key_here
supabase secrets set AZURE_FACE_API_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com
```

## 8. Test Senaryosu

### Senaryo: Öğrenci Yoklama Verme

1. **Web Panel (Eğitmen)**
   - http://localhost:5173 aç
   - `admin@test.com` ile giriş yap
   - Courses > Yeni Ders ekle
   - Sessions > Yeni Oturum başlat
   - QR kod göster

2. **Mobil Uygulama (Öğrenci)**
   - Expo Go ile uygulamayı aç
   - `student@test.com` ile giriş yap
   - Profile > Yüz Fotoğrafı Yükle
   - Biyometrik veri izni ver
   - Attendance > QR Kod Tara
   - Ekrandaki QR kodu tarat
   - Kamera ile yüz fotoğrafı çek
   - Yoklama kaydedildi mesajı

3. **Web Panel (Raporlar)**
   - Reports > Ders seç
   - Rapor Oluştur
   - Öğrencinin kaydını gör

## 9. Sorun Giderme

### Mobil Uygulama Bağlanamıyor

```bash
# Metro bundler'ı temizle
cd mobile-app
rm -rf node_modules
npm install
npx expo start --clear
```

### Web Panel Build Hatası

```bash
cd web-panel
rm -rf node_modules dist
npm install
npm run build
```

### Supabase RLS Hatası

```sql
-- RLS geçici olarak devre dışı bırak (sadece test için!)
ALTER TABLE tablename DISABLE ROW LEVEL SECURITY;
```

### Edge Function Çalışmıyor

```bash
# Local test
supabase functions serve face-verification

# Logs kontrol
supabase functions logs face-verification
```

## 10. Sonraki Adımlar

- [ ] Production deployment için [DEPLOYMENT.md](DEPLOYMENT.md) okuyun
- [ ] Güvenlik için [SECURITY.md](SECURITY.md) inceleyin
- [ ] Kod katkısı için [CONTRIBUTING.md](CONTRIBUTING.md) okuyun
- [ ] API dokümantasyonu için Supabase auto-docs kullanın

## Yardım ve Destek

- GitHub Issues: Hata bildirimi
- Documentation: `/docs` klasörü
- Supabase Docs: [supabase.com/docs](https://supabase.com/docs)
- Expo Docs: [docs.expo.dev](https://docs.expo.dev)

## Lisans

Bu proje MIT lisansı altındadır. Detaylar için LICENSE dosyasına bakın.

