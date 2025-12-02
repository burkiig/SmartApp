# Supabase Backend

Smart Attendance System için backend altyapısı

## Dizin Yapısı

```
supabase/
├── schema.sql              # Veritabanı şeması, tablolar, tipler
├── rls_policies.sql        # Row Level Security politikaları
├── config.toml             # Local development ayarları
└── functions/
    └── face-verification/  # Yüz tanıma Edge Function
```

## Kurulum

### 1. Supabase CLI Kurulumu
```bash
npm install -g supabase
```

### 2. Proje Başlatma
```bash
# Yeni bir Supabase projesi başlat
supabase init

# Var olan projeye bağlan
supabase login
supabase link --project-ref your-project-ref
```

### 3. Local Development
```bash
# Docker ile local Supabase başlat
supabase start

# Migrations uygula
supabase db reset

# Edge Functions test et
supabase functions serve face-verification
```

## Veritabanı Şeması

### Tablolar

#### `profiles`
Kullanıcı profil bilgileri (auth.users'a bağlı)
- `role`: student | teacher | admin
- `face_image_url`: Referans yüz fotoğrafı
- `consent_given`: Biyometrik veri izni

#### `courses`
Ders bilgileri
- Eğitmen tarafından oluşturulur
- `is_active`: Aktif/pasif durum

#### `enrollments`
Öğrenci-Ders ilişkisi
- Many-to-many relationship

#### `attendance_sessions`
Yoklama oturumları
- `qr_code`: Benzersiz QR kod
- `location_lat/lng`: GPS koordinatları
- `require_*`: Doğrulama gereksinimleri

#### `attendance_records`
Yoklama kayıtları
- `status`: present | absent | late | excused
- `*_verified`: Doğrulama sonuçları
- `face_confidence_score`: Yüz tanıma skoru

#### `audit_logs`
Denetim kayıtları
- Tüm kritik işlemler loglanır

## Row Level Security (RLS)

### Temel Prensipler
1. Tüm tablolarda RLS aktif
2. Her rol için ayrı politikalar
3. Varsayılan: Erişim yok, açıkça izin ver

### Örnek Politikalar

```sql
-- Öğrenci kendi kayıtlarını görebilir
CREATE POLICY "Students view own records"
ON attendance_records FOR SELECT
USING (student_id = auth.uid());

-- Eğitmen kendi derslerini yönetebilir
CREATE POLICY "Teachers manage own courses"
ON courses FOR ALL
USING (teacher_id = auth.uid());

-- Admin her şeyi görebilir
CREATE POLICY "Admins view all"
ON profiles FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM profiles
    WHERE id = auth.uid() AND role = 'admin'
  )
);
```

## Edge Functions

### face-verification

Yüz tanıma servisi entegrasyonu (Azure Face API)

**Input:**
```json
{
  "referenceImageUrl": "https://...",
  "verificationImageUrl": "https://..."
}
```

**Output:**
```json
{
  "success": true,
  "confidence": 95,
  "isIdentical": true
}
```

**Environment Variables:**
```bash
AZURE_FACE_API_KEY=your_key
AZURE_FACE_API_ENDPOINT=your_endpoint
```

**Test:**
```bash
curl -i --location --request POST \
  'http://localhost:54321/functions/v1/face-verification' \
  --header 'Authorization: Bearer YOUR_ANON_KEY' \
  --header 'Content-Type: application/json' \
  --data '{"referenceImageUrl":"...","verificationImageUrl":"..."}'
```

## Storage Buckets

### face-photos
- Öğrenci referans yüz fotoğrafları
- Private bucket
- RLS: Kullanıcı kendi fotoğrafını upload/read edebilir

### verification-photos
- Yoklama anındaki doğrulama fotoğrafları
- Private bucket
- RLS: Eğitmenler okuyabilir

## Migrations

Yeni migration oluşturma:
```bash
supabase migration new add_new_feature
```

Migration uygulama:
```bash
supabase db push
```

Migration geri alma:
```bash
supabase db reset
```

## Database Functions

### update_updated_at_column()
Otomatik `updated_at` güncellemesi için trigger function

```sql
CREATE TRIGGER update_profiles_updated_at 
BEFORE UPDATE ON profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Monitoring

### Logs
```bash
# Database logs
supabase db logs

# Edge function logs
supabase functions logs face-verification
```

### Performance
```sql
-- Slow queries
SELECT * FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan;
```

## Backup & Recovery

### Manual Backup
```bash
supabase db dump -f backup.sql
```

### Restore
```bash
psql -h db.xxx.supabase.co -U postgres -d postgres -f backup.sql
```

## Troubleshooting

### RLS Debugging
```sql
-- RLS politikalarını kontrol et
SELECT * FROM pg_policies WHERE tablename = 'attendance_records';

-- Service role ile test et (RLS bypass)
-- Dashboard > Settings > API > service_role key
```

### Connection Issues
```bash
# Local Supabase restart
supabase stop
supabase start
```

### Migration Conflicts
```bash
# Squash migrations
supabase db reset
supabase migration squash
```

