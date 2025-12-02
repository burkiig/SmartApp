# Smart Attendance System 🎓

Akıllı Yoklama Sistemi - Çok katmanlı doğrulama ile modern devamsızlık takibi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Genel Bakış

Smart Attendance System, eğitim kurumları için geliştirilmiş, modern ve güvenli bir yoklama sistemidir. QR kod, GPS konum doğrulama, cihaz kimliği ve yüz tanıma teknolojilerini birleştirerek kopya çekme ve sahte yoklama girişlerini önler.

## ✨ Özellikler

### Öğrenci Özellikleri (Mobil Uygulama)
- 📱 QR kod ile hızlı yoklama
- 📍 GPS tabanlı konum doğrulama
- 👤 Yüz tanıma ile kimlik doğrulama
- 📊 Kişisel devamsızlık raporları
- 🔒 Biyometrik veri gizliliği

### Eğitmen Özellikleri (Web Panel)
- 📚 Ders oluşturma ve yönetimi
- 🎯 Yoklama oturumu başlatma
- 📱 Dinamik QR kod üretme
- 📈 Gerçek zamanlı yoklama takibi
- 📊 Ders bazlı raporlama
- 📥 CSV export

### Admin Özellikleri (Web Panel)
- 👥 Kullanıcı yönetimi (CRUD)
- 🔐 Rol atama (Student/Teacher/Admin)
- 📊 Sistem geneli istatistikler
- 🔍 Denetim logları
- ⚙️ Sistem yapılandırması

## 🏗️ Proje Yapısı

```
Smart Attendance System/
├── supabase/              # Backend & Database
│   ├── schema.sql         # Database schema
│   ├── rls_policies.sql   # Security policies
│   └── functions/         # Edge Functions
│       └── face-verification/
├── mobile-app/            # React Native (Expo)
│   ├── app/               # Expo Router pages
│   ├── contexts/          # Auth context
│   └── lib/               # Supabase client
├── web-panel/             # React + Vite
│   ├── src/
│   │   ├── pages/         # Dashboard, Courses, etc.
│   │   ├── components/    # Reusable components
│   │   └── contexts/      # Auth context
└── shared/                # Shared TypeScript types
```

## 🚀 Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Supabase (PostgreSQL, Auth, Realtime, Storage) |
| **Mobile** | React Native (Expo), TypeScript, **NativeWind** |
| **Web** | React 18, Vite 5, TypeScript, **Tailwind CSS** |
| **Styling** | **Tailwind CSS 3** + **NativeWind 2** |
| **Face Recognition** | Azure Face API / AWS Rekognition |
| **State Management** | TanStack Query, React Context |
| **Routing** | Expo Router, React Router v6 |

## 👥 Kullanıcı Rolleri

| Rol | Platform | Yetkiler |
|-----|----------|----------|
| **Student** | 📱 Mobile | Yoklama verme, kişisel raporlar |
| **Teacher** | 💻 Web | Ders yönetimi, yoklama başlatma, raporlama |
| **Admin** | 💻 Web | Tam sistem kontrolü, kullanıcı yönetimi |

## 📚 Başlangıç Rehberleri

- **Hızlı Başlangıç**: [GETTING_STARTED.md](GETTING_STARTED.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Güvenlik**: [SECURITY.md](SECURITY.md)
- **Supabase Backend**: [supabase/README.md](supabase/README.md)

## ⚡ Hızlı Kurulum

### 1. Proje Klonlama
```bash
git clone <repository-url>
cd "Smart Attendace System"
```

### 2. Supabase Setup
```bash
# Supabase hesabı oluşturun: https://supabase.com
# SQL Editor'de schema.sql ve rls_policies.sql'i çalıştırın
```

### 3. Mobil Uygulama
```bash
cd mobile-app
npm install
# .env dosyası oluştur (GETTING_STARTED.md'ye bakın)
npm start
```

### 4. Web Panel
```bash
cd web-panel
npm install
# .env dosyası oluştur
npm run dev
```

## 🔒 Güvenlik

- ✅ Row Level Security (RLS) ile veri güvenliği
- ✅ JWT tabanlı kimlik doğrulama
- ✅ Biyometrik veri şifreleme
- ✅ KVKK/GDPR uyumlu
- ✅ Denetim logları
- ✅ HTTPS zorunlu

Detaylar için: [SECURITY.md](SECURITY.md)

## 📊 Veritabanı Şeması

```sql
profiles           # Kullanıcı profilleri
├── id (PK)
├── role (student/teacher/admin)
├── face_image_url
└── consent_given

courses            # Dersler
├── id (PK)
├── teacher_id (FK)
└── course_code

enrollments        # Öğrenci-Ders İlişkisi
├── course_id (FK)
└── student_id (FK)

attendance_sessions    # Yoklama Oturumları
├── id (PK)
├── qr_code
├── location_lat/lng
└── require_face_recognition

attendance_records     # Yoklama Kayıtları
├── session_id (FK)
├── student_id (FK)
├── face_verified
└── face_confidence_score
```

## 🎯 Kullanım Senaryosu

1. **Eğitmen**: Web panelinden yoklama oturumu başlatır
2. **Sistem**: Benzersiz QR kod üretir
3. **Öğrenci**: Mobil uygulamada QR kodu tarar
4. **Sistem**: GPS konumunu kontrol eder
5. **Öğrenci**: Anlık yüz fotoğrafı çeker
6. **Sistem**: Referans fotoğraf ile karşılaştırır
7. **Sonuç**: Yoklama kaydedilir veya reddedilir

## 🧪 Test

```bash
# Mobil uygulama
cd mobile-app
npx expo start

# Web panel
cd web-panel
npm run dev

# Edge functions
cd supabase
supabase functions serve face-verification
```

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'feat: Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 Destek

- 📖 Dokümantasyon: [Tüm Rehberler](/)
- 🐛 Bug Report: GitHub Issues
- 💡 Feature Request: GitHub Discussions

## 🙏 Teşekkürler

Bu proje aşağıdaki açık kaynak projeleri kullanmaktadır:
- [Supabase](https://supabase.com)
- [Expo](https://expo.dev)
- [React](https://react.dev)
- [Vite](https://vitejs.dev)

---

Made with ❤️ for educational institutions

