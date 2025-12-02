# Güvenlik ve Gizlilik Politikaları

## 1. Veri Güvenliği

### Biyometrik Veri Koruma
- Yüz fotoğrafları **şifreli** Supabase Storage'da saklanır
- Her öğrencinin rızası (`consent_given`) alınmadan yüz tanıma kullanılmaz
- Yüz fotoğraflarına sadece ilgili kullanıcı ve yetkili eğitmenler erişebilir
- Verification fotoğrafları oturum sonrası saklanabilir (denetim için)

### Konum Verileri
- GPS koordinatları sadece yoklama doğrulama için kullanılır
- Öğrenci konumu sürekli takip edilmez, sadece yoklama anında alınır
- Konum verileri şifrelenmiş veritabanında saklanır

### Cihaz Kimliği (UUID)
- Cihaz UUID'leri sadece aynı cihazdan yoklama verilmesini sağlamak için kullanılır
- Cihaz değiştiren öğrenciler admin/eğitmene başvurabilir

## 2. Kimlik Doğrulama ve Yetkilendirme

### Supabase Auth (JWT)
- Her kullanıcı güvenli JWT token ile doğrulanır
- Token'lar otomatik olarak yenilenir
- Session süresi: 1 saat (ayarlanabilir)

### Rol Tabanlı Erişim (RBAC)
- **Student**: Sadece mobil uygulama, kendi verilerine erişim
- **Teacher**: Web panel, kendi derslerine erişim
- **Admin**: Tam sistem erişimi

### Row Level Security (RLS)
Tüm tablolarda RLS aktif:
```sql
-- Örnek: Öğrenci sadece kendi kayıtlarını görebilir
CREATE POLICY "Students view own records"
ON attendance_records FOR SELECT
USING (student_id = auth.uid());
```

## 3. API Güvenliği

### Supabase API Keys
- **Anon Key**: Client-side kullanılır, RLS ile korunur ✅
- **Service Role Key**: Sadece backend/edge functions, ASLA client'ta kullanılmaz ⚠️

### Rate Limiting
Supabase otomatik olarak rate limiting uygular:
- Anonymous users: 60 requests/minute
- Authenticated users: 200 requests/minute

### CORS Ayarları
Edge Functions'da CORS headers doğru ayarlanmış:
```typescript
const corsHeaders = {
  'Access-Control-Allow-Origin': '*', // Production'da specific domain kullanın
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}
```

## 4. KVKK/GDPR Uyumluluğu

### Veri Toplama İzni
Öğrencilerden alınması gereken izinler:
- ✅ Yüz fotoğrafı çekme ve saklama
- ✅ Konum verisi toplama
- ✅ Cihaz kimliği saklama

### İzin Yönetimi
```typescript
// Profil ekranında:
if (!profile?.consent_given) {
  // Kullanıcıya açık rıza formu göster
  // consent_given = true + consent_date kaydet
}
```

### Veri Silme Hakkı (Right to be Forgotten)
Öğrenci hesabı silindiğinde:
- Profil verisi silinir
- Yüz fotoğrafları Storage'dan silinir
- Yoklama kayıtları anonim hale getirilebilir veya silinir

```sql
-- Cascade delete ile otomatik temizlik
ON DELETE CASCADE
```

### Veri İşleme Kayıtları
`audit_logs` tablosu tüm kritik işlemleri kaydeder:
- Kim, ne zaman, hangi veriyi değiştirdi
- IP adresi kayıtları
- JSONB formatında eski/yeni veri

## 5. Mobil Uygulama Güvenliği

### Cihaz İzinleri
```json
// app.json
"permissions": [
  "CAMERA",           // Sadece QR ve yüz tanıma için
  "ACCESS_FINE_LOCATION"  // Sadece yoklama anında
]
```

### Secure Storage
```typescript
// Expo SecureStore kullanımı
import * as SecureStore from 'expo-secure-store';
// Session token'lar güvenli saklanır
```

### SSL Pinning (Önerilen)
Production'da SSL certificate pinning ekleyin:
```typescript
// Supabase isteklerinde MITM saldırılarını önler
```

## 6. Web Panel Güvenliği

### HTTPS Zorunlu
- Tüm deployment'lar HTTPS üzerinden olmalı
- Mixed content (HTTP/HTTPS) kullanılmamalı

### XSS Koruması
React otomatik olarak XSS'e karşı korur:
```typescript
// Güvenli: React otomatik escape eder
<div>{userInput}</div>

// Tehlikeli: Kullanmayın
<div dangerouslySetInnerHTML={{__html: userInput}} />
```

### CSRF Koruması
Supabase JWT auth otomatik CSRF koruması sağlar

## 7. Edge Functions Güvenliği

### Environment Variables
```bash
# Hassas veriler environment variables'da
supabase secrets set AZURE_FACE_API_KEY=xxx
```

### Input Validation
```typescript
// Her input doğrulanmalı
if (!referenceImageUrl || !verificationImageUrl) {
  throw new Error('Invalid input')
}
```

### Error Handling
```typescript
// Hassas bilgi sızdırmayın
catch (error) {
  // ❌ return { error: error.stack }
  // ✅ return { error: 'Face verification failed' }
}
```

## 8. Güvenlik En İyi Pratikleri

### Şifre Politikası
- Minimum 6 karakter (production'da 8+ önerilir)
- Supabase otomatik hash yapar (bcrypt)
- 2FA eklenmesi önerilir

### Audit Logging
Tüm kritik işlemler loglanmalı:
- Kullanıcı oluşturma/silme
- Rol değişiklikleri
- Yüz fotoğrafı güncellemeleri
- Yoklama kayıt manipülasyonları

### Regular Updates
```bash
# Dependency'leri düzenli güncelleyin
npm audit
npm update
```

### Penetration Testing
- Deployment öncesi güvenlik testleri
- OWASP Top 10 kontrolü
- SQL injection testleri
- RLS bypass denemeleri

## 9. Incident Response Plan

### Veri İhlali Durumunda
1. Sistemleri hemen izole edin
2. Etkilenen kullanıcıları belirleyin
3. KVKK/GDPR gereksinimlerine göre bildirim yapın (72 saat içinde)
4. Güvenlik açığını patch'leyin
5. Incident raporu hazırlayın

### Şüpheli Aktivite
```sql
-- Audit logs'u kontrol edin
SELECT * FROM audit_logs 
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

## 10. Compliance Checklist

- [ ] KVKK açık rıza metni hazırlanmış
- [ ] Gizlilik politikası oluşturulmuş
- [ ] Kullanım koşulları yazılmış
- [ ] Veri saklama süreleri belirlenmişi
- [ ] Veri silme prosedürü tanımlı
- [ ] Audit logging aktif
- [ ] RLS tüm tablolarda aktif
- [ ] SSL/TLS sertifikaları geçerli
- [ ] API keys güvenli saklanıyor
- [ ] Regular security audits planlanmış
- [ ] Incident response plan hazır
- [ ] Backup ve recovery stratejisi mevcut

