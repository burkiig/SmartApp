# Smart Attendance - Mobile App (Öğrenci)

React Native (Expo) + NativeWind mobil uygulaması - Sadece öğrenciler için

## Özellikler

- QR kod ile yoklama
- GPS konum doğrulama
- Yüz tanıma entegrasyonu
- Cihaz UUID kontrolü
- Profil yönetimi
- Biyometrik veri izni

## Kurulum

```bash
npm install
```

## Çalıştırma

```bash
# .env dosyası oluştur ve Supabase bilgilerini ekle
cp .env.example .env

# Geliştirme sunucusunu başlat
npm start

# Android
npm run android

# iOS
npm run ios
```

## Teknolojiler

- React Native
- Expo SDK 51
- **NativeWind 2** (Tailwind for React Native) ✨
- TypeScript
- Expo Router
- Supabase Client
- Expo Camera, Location, Device

## NativeWind

Projeye NativeWind (Tailwind CSS for React Native) entegre edilmiştir.

### Özel Renkler
```js
colors: {
  primary: '#007AFF',
  success: '#34C759',
  danger: '#FF3B30',
}
```

### Kullanım Örneği
```tsx
<View className="flex-1 p-5 bg-gray-50">
  <Text className="text-2xl font-bold text-primary">
    Merhaba
  </Text>
  <TouchableOpacity className="bg-primary p-4 rounded-lg">
    <Text className="text-white text-center">Giriş Yap</Text>
  </TouchableOpacity>
</View>
```

## Gereksinimler

- Node.js 18+
- Expo CLI
- Android Studio / Xcode
- Supabase projesi
