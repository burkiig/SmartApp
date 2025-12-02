# 🔧 Troubleshooting Guide - Smart Attendance Mobile

## TurboModuleRegistry 'PlatformConstants' Hatası Çözümü

### Sorun
```
[runtime not ready]: Invariant Violation: TurboModuleRegistry.getEnforcing(...):
'PlatformConstants' could not be found.
```

### Çözüm Adımları

#### 1. **Tam Temizlik Yap (Önerilen)**

```bash
cd mobile-app

# Watchman cache temizle
watchman watch-del-all

# Node modules ve cache temizle
rm -rf node_modules
rm -rf .expo
npm cache clean --force

# Metro bundler cache temizle
rm -rf $TMPDIR/metro-*
rm -rf $TMPDIR/haste-*
rm -rf /tmp/metro-*
rm -rf /tmp/haste-*

# Paketleri yeniden yükle
npm install

# Expo'yu temiz başlat
expo start -c
```

#### 2. **Hızlı Reset (Script ile)**

```bash
npm run reset
```

Bu komut yukarıdaki tüm adımları otomatik yapar.

#### 3. **iOS Specific - Pod Kurulumu**

Eğer iOS'ta sorun devam ediyorsa:

```bash
cd ios
pod deintegrate
pod install
cd ..
expo start -c
```

#### 4. **Expo Doctor ile Kontrol**

```bash
npx expo doctor
```

Bu komut sürüm uyumsuzluklarını tespit eder ve düzeltme önerileri sunar.

---

## 📦 Sürüm Bilgileri

Bu proje şu stabil sürümlerle çalışır:

- **Expo SDK:** 54.0.0
- **React Native:** 0.81.5
- **React:** 19.1.0
- **Expo Router:** 6.0.15

### Kritik Bağımlılıklar

- `react-native-reanimated`: ~4.1.1
- `react-native-gesture-handler`: ~2.28.0
- `react-native-safe-area-context`: ~5.6.0
- `react-native-screens`: ~4.16.0
- `react-native-worklets`: (required peer dependency)

---

## 🚨 Yaygın Hatalar ve Çözümler

### 1. Metro Bundler %100'de Takılı Kalıyor

**Çözüm:**
```bash
npm run clean:metro
expo start -c
```

### 2. "Unable to resolve module" Hatası

**Çözüm:**
```bash
rm -rf node_modules
npm install
expo start -c
```

### 3. Expo Go'da Native Module Hatası

**Sebep:** Expo Go bazı native modülleri desteklemez.

**Çözüm 1 - Development Build:**
```bash
npx expo prebuild
npx expo run:ios
```

**Çözüm 2 - EAS Build:**
```bash
eas build --profile development --platform ios
```

### 4. Hermes Motor Sorunları

Eğer Hermes ile ilgili sorun yaşıyorsanız, `app.config.js` içinde JSC'ye geçebilirsiniz:

```javascript
ios: {
  jsEngine: 'jsc'
}
```

---

## 📱 Test Etme

### Expo Go ile Test
```bash
expo start
# QR kod ile telefondan tarayın
```

### iOS Simulator
```bash
expo start --ios
```

### Android Emulator
```bash
expo start --android
```

---

## 🛠️ Geliştirme İpuçları

### Cache Temizleme Sırası
1. Watchman
2. Node modules
3. Metro bundler
4. Expo cache
5. iOS Pods (iOS için)

### Paket Güncellemeleri
```bash
# Expo paketlerini güncelle
npx expo install --fix

# Tüm paketleri kontrol et
npx expo doctor --fix-dependencies
```

### Debug Modu
```bash
# Detaylı log ile başlat
EXPO_DEBUG=true expo start -c
```

---

## 📞 Ek Kaynaklar

- [Expo Documentation](https://docs.expo.dev)
- [React Native Troubleshooting](https://reactnative.dev/docs/troubleshooting)
- [Expo Router Docs](https://docs.expo.dev/router/introduction/)

---

**Son Güncelleme:** 2025-10-21

