# Deployment Rehberi - Smart Attendance System

## 1. Supabase Kurulumu

### Yeni Proje Oluşturma
1. [supabase.com](https://supabase.com) adresine gidin
2. "New Project" butonuna tıklayın
3. Proje adı, veritabanı şifresi ve region seçin

### Veritabanı Şemasını Yükleme
```bash
# Supabase CLI kurulumu
npm install -g supabase

# Supabase'e bağlanma
supabase login
supabase link --project-ref your-project-ref

# SQL scriptlerini çalıştırma
supabase db push
```

Veya manuel olarak:
1. Supabase Dashboard > SQL Editor
2. `supabase/schema.sql` dosyasının içeriğini yapıştırın ve çalıştırın
3. `supabase/rls_policies.sql` dosyasını aynı şekilde çalıştırın

### Storage Bucket'ları Oluşturma
1. Storage > New Bucket
2. İki bucket oluşturun:
   - `face-photos` (private)
   - `verification-photos` (private)
3. Her bucket için RLS politikaları:

```sql
-- face-photos bucket için
CREATE POLICY "Users can upload own face photo"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'face-photos' AND
  auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can read own face photo"
ON storage.objects FOR SELECT
USING (bucket_id = 'face-photos');

-- verification-photos bucket için
CREATE POLICY "Users can upload verification photo"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'verification-photos');

CREATE POLICY "Teachers can read verification photos"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'verification-photos' AND
  EXISTS (
    SELECT 1 FROM profiles
    WHERE id = auth.uid() AND role IN ('teacher', 'admin')
  )
);
```

### Edge Function Deploy Etme
```bash
# Face verification function
supabase functions deploy face-verification

# Environment variables ayarlama
supabase secrets set AZURE_FACE_API_KEY=your_key
supabase secrets set AZURE_FACE_API_ENDPOINT=your_endpoint
```

## 2. React Native (Mobil Uygulama) Deployment

### Android Build
```bash
cd mobile-app

# .env dosyasını oluştur
cat > .env << EOF
EXPO_PUBLIC_SUPABASE_URL=your_supabase_url
EXPO_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
EOF

# EAS Build ile build alma
npm install -g eas-cli
eas login
eas build:configure
eas build --platform android
```

### iOS Build
```bash
# iOS için sertifika gerektirir
eas build --platform ios
```

### Google Play Store / App Store
1. EAS Submit kullanarak otomatik yükleme:
```bash
eas submit --platform android
eas submit --platform ios
```

## 3. React Web Panel Deployment

### Vercel ile Deployment (Önerilen)
```bash
cd web-panel

# .env dosyası oluştur
cat > .env << EOF
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
EOF

# Vercel CLI
npm install -g vercel
vercel login
vercel --prod
```

### Netlify ile Deployment
```bash
# Build
npm run build

# Netlify'a yükle
netlify deploy --prod --dir=dist
```

### Environment Variables (Vercel/Netlify)
Dashboard'dan ekleyin:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

## 4. İlk Kullanıcı Oluşturma

### Admin Kullanıcı Oluşturma
```sql
-- Supabase SQL Editor'de çalıştırın
-- Önce Supabase Dashboard > Authentication > Users 
-- kısmından manuel olarak bir kullanıcı oluşturun

-- Sonra profiles tablosuna ekleyin:
INSERT INTO profiles (id, email, full_name, role)
VALUES (
  'user-id-from-auth-users',
  'admin@example.com',
  'Admin User',
  'admin'
);
```

## 5. Güvenlik Kontrolleri

### RLS Aktif mi Kontrol
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

### API Keys Kontrolü
- Anon key public olabilir (RLS ile korunur)
- Service role key ASLA client tarafında kullanılmamalı
- Edge Function environment variables güvenli mi?

## 6. Monitoring ve Bakım

### Supabase Dashboard
- Database > Logs: SQL hatalarını izle
- Auth > Users: Kullanıcı aktivitesini kontrol et
- Storage > Logs: Upload problemlerini gör
- Edge Functions > Logs: Function hatalarını takip et

### Günlük Yedekleme
Supabase Dashboard > Database > Backups
- Otomatik yedekleme aktif mi kontrol edin
- Manuel yedekleme alın (önemli güncellemeler öncesi)

## 7. Azure Face API Setup (Yüz Tanıma)

1. [Azure Portal](https://portal.azure.com) > Create a resource
2. "Face" servisini seçin
3. Pricing tier seçin (F0 ücretsiz tier test için yeterli)
4. Deploy edildikten sonra:
   - Keys and Endpoint kısmından Key1 ve Endpoint'i kopyalayın
   - Supabase Edge Function secrets'a ekleyin

### Alternatif: AWS Rekognition
```typescript
// supabase/functions/face-verification/index.ts dosyasında
// Azure yerine AWS SDK kullanabilirsiniz
import { RekognitionClient, CompareFacesCommand } from "@aws-sdk/client-rekognition";
```

## 8. Production Checklist

- [ ] Supabase RLS politikaları aktif ve test edilmiş
- [ ] Storage buckets oluşturulmuş ve politikalar ayarlanmış
- [ ] Edge Functions deploy edilmiş ve test edilmiş
- [ ] Environment variables tüm platformlarda ayarlanmış
- [ ] İlk admin kullanıcı oluşturulmuş
- [ ] Mobil uygulama store'lara yüklenmiş
- [ ] Web panel canlıya alınmış
- [ ] Yedekleme stratejisi aktif
- [ ] Error monitoring kurulmuş (Sentry, LogRocket vb.)
- [ ] SSL/HTTPS aktif
- [ ] GDPR/KVKK uyumluluğu kontrol edilmiş

