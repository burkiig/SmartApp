# Smart Attendance - Web Panel (Eğitmen & Admin)

React + Vite + Tailwind CSS web paneli - Eğitmen ve Admin kullanıcıları için

## Özellikler

### Eğitmen Yetkiler
- Ders oluşturma ve yönetme
- Yoklama oturumları başlatma/durdurma
- QR kod üretme
- Kendi dersleri için raporlar

### Admin Yetkiler
- Tüm eğitmen yetkilerine ek olarak:
- Kullanıcı yönetimi (CRUD)
- Sistem geneli raporlar
- Tüm derslere erişim

## Kurulum

```bash
npm install
```

## Çalıştırma

```bash
# .env dosyası oluştur
cp .env.example .env

# Geliştirme sunucusu
npm run dev

# Production build
npm run build
```

## Teknolojiler

- React 18
- Vite 5
- **Tailwind CSS 3** ✨
- TypeScript
- React Router
- Supabase Client
- QR Code Generator
- TanStack Query

## Tailwind CSS

Projeye Tailwind CSS entegre edilmiştir. Tüm stil işlemleri için Tailwind utility class'ları kullanılır.

### Özel Renkler
```js
colors: {
  primary: '#007AFF',
  secondary: '#5856D6',
  success: '#34C759',
  warning: '#FF9500',
  danger: '#FF3B30',
}
```

### Kullanım Örneği
```tsx
<button className="bg-primary text-white px-4 py-2 rounded-lg hover:opacity-90">
  Kaydet
</button>
```
