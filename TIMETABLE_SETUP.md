# 📅 Ders Programı (TimeTable) Kurulum Rehberi

Bu dokümanda, öğretmenlerin haftalık ders programlarını oluşturabilecekleri TimeTable özelliğinin nasıl kurulacağı anlatılmaktadır.

## 🎯 Özellikler

- ✅ Pazartesi - Cuma arası haftalık program görünümü
- ✅ 08:30 - 17:30 arası saat dilimleri (30 dakikalık bloklar)
- ✅ Boş hücreye tıklayarak ders ekleme
- ✅ Mevcut derse tıklayarak düzenleme/silme
- ✅ Otomatik renk kodlama (her ders farklı renk)
- ✅ Sınıf bilgisi (CMP210, A101, vb.)
- ✅ Çakışma kontrolü (aynı saatte iki ders eklenemez)
- ✅ Responsive tasarım (mobil/tablet uyumlu)

## 📋 Kurulum Adımları

### 1️⃣ Veritabanı Tablosu Oluşturma

Supabase Dashboard'a gidin ve şu adımları izleyin:

1. **SQL Editor** açın
2. `supabase/course-schedules-schema.sql` dosyasını açın
3. Tüm SQL kodunu kopyalayıp SQL Editor'e yapıştırın
4. **Run** butonuna basın

Bu işlem şunları yapacak:
- `course_schedules` tablosunu oluşturur
- Gerekli indeksleri ekler
- RLS (Row Level Security) politikalarını ayarlar
- Çakışma kontrolü için yardımcı fonksiyon ekler

### 2️⃣ Veritabanı Kontrolü

Tablonun başarıyla oluşturulduğunu kontrol edin:

```sql
-- Tablo yapısını kontrol et
SELECT * FROM course_schedules LIMIT 1;

-- RLS politikalarını kontrol et
SELECT * FROM pg_policies WHERE tablename = 'course_schedules';
```

### 3️⃣ Web Panel'de Test Etme

1. Web panel'i başlatın (eğer çalışmıyorsa):
   ```bash
   cd web-panel
   npm run dev
   ```

2. Öğretmen hesabıyla giriş yapın
3. **Dersler** sayfasına gidin
4. **📅 Ders Programı** sekmesine tıklayın

### 4️⃣ İlk Ders Programını Ekleme

1. Önce **📚 Ders Listesi** sekmesinden en az bir ders ekleyin
2. **📅 Ders Programı** sekmesine dönün
3. Boş bir hücreye tıklayın
4. Modal formda:
   - Ders seçin
   - Gün ve saat belirleyin
   - İsteğe bağlı: Sınıf bilgisi ekleyin
   - **Kaydet** butonuna basın

## 🎨 Görsel Önizleme

### Grid Yapısı
```
┌─────────┬───────────┬───────────┬───────────┬───────────┬───────────┐
│  Saat   │ Pazartesi │   Salı    │ Çarşamba  │ Perşembe  │   Cuma    │
├─────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
│ 08:30   │           │           │           │           │           │
│ 09:00   │  CMSE107  │           │  CMSE107  │           │  CMSE107  │
│ 09:30   │  Veri     │           │  Veri     │           │  Veri     │
│ 10:00   │  Yapıları │           │  Yapıları │           │  Yapıları │
│ 10:30   │           │  MATH201  │           │           │           │
│ 11:00   │           │  Calculus │           │           │           │
└─────────┴───────────┴───────────┴───────────┴───────────┴───────────┘
```

### Renk Kodlama
Her ders otomatik olarak farklı bir renk alır:
- 🔵 Mavi
- 🟢 Yeşil  
- 🟣 Mor
- 🩷 Pembe
- 🟠 Turuncu
- 🔷 Cyan
- vb.

## 🔧 Teknik Detaylar

### Veritabanı Şeması

```sql
CREATE TABLE course_schedules (
    id UUID PRIMARY KEY,
    course_id UUID REFERENCES courses(id),
    teacher_id UUID REFERENCES profiles(id),
    day_of_week INTEGER CHECK (1-5), -- 1=Pazartesi
    start_time TIME,
    end_time TIME,
    classroom TEXT,
    notes TEXT,
    academic_year TEXT,
    semester TEXT,
    is_active BOOLEAN,
    ...
)
```

### TypeScript Tipleri

```typescript
interface CourseSchedule {
  id: string
  course_id: string
  teacher_id: string
  day_of_week: number // 1=Pazartesi, 5=Cuma
  start_time: string // "08:30:00"
  end_time: string // "09:20:00"
  classroom?: string
  notes?: string
  academic_year: string
  semester: string
  is_active: boolean
  course?: Course
}
```

### RLS Politikaları

- ✅ **Admin**: Tüm programlara tam erişim
- ✅ **Teacher**: Sadece kendi programını görüntüleme/düzenleme
- ✅ **Student**: Erişim yok (şimdilik)

## 🚨 Sorun Giderme

### "Tablo bulunamadı" Hatası

```bash
# RLS politikalarını kontrol et
SELECT * FROM pg_policies WHERE tablename = 'course_schedules';

# Tabloyu yeniden oluştur
# supabase/course-schedules-schema.sql dosyasını tekrar çalıştır
```

### "Permission denied" Hatası

RLS politikalarının doğru yüklendiğinden emin olun:

```sql
-- Mevcut politikaları kontrol et
SELECT policyname, cmd, qual 
FROM pg_policies 
WHERE tablename = 'course_schedules';
```

### Dersler Görünmüyor

1. **Ders Listesi** sekmesinde aktif derslerin olduğundan emin olun
2. Tarayıcı konsolunu kontrol edin (F12)
3. Network sekmesinde Supabase isteklerini kontrol edin

### Çakışma Hatası Alıyorum

Bu normal bir durumdur. Aynı gün ve saatte iki farklı ders ekleyemezsiniz. Mevcut dersi:
1. Tıklayarak açın
2. **Sil** butonuna basın
3. Yeni ders ekleyin

## 📱 Mobil Uyumluluk

TimeTable responsive tasarıma sahiptir:

- **Desktop**: Tam grid görünümü
- **Tablet**: Yatay kaydırma ile görünüm
- **Mobil**: Kompakt grid, yatay scroll

## 🔮 Gelecek Özellikler (Planlanan)

- [ ] Drag & drop ile ders taşıma
- [ ] Excel/PDF olarak dışa aktarma
- [ ] Ders tekrarları (her hafta aynı saat)
- [ ] Farklı dönemler arası geçiş
- [ ] Öğrenciler için görüntüleme modu
- [ ] Sınıf bazlı ders programları
- [ ] Birden fazla sınıf ataması

## 📞 Destek

Sorun yaşarsanız:

1. Tarayıcı konsolunu kontrol edin (F12)
2. Supabase logs'larını inceleyin
3. GitHub Issues'a rapor edin

---

**Not**: Bu özellik sadece öğretmen ve admin hesapları için kullanılabilir. Öğrenci hesapları ders programı oluşturamaz (sadece görüntüleme yapabilir - gelecekte eklenecek).


