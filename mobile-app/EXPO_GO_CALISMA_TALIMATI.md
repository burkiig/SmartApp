# 📱 Expo Go'da Çalıştırma Talimatı

## ✅ Cache Temizliği Yapıldı

Tüm cache'ler temizlendi ve Expo temiz başlatıldı!

## 🎯 ŞİMDİ YAPMANIZ GEREKENLER

### 1️⃣ iPhone'da Expo Go'yu Tamamen Kapatın

**ÖNEMLİ:** Sadece arka plana atmak yetmez!

1. iPhone'da **Expo Go uygulamasını açın**
2. Ana ekrana dönün
3. **Aşağıdan yukarı kaydırın** (veya home'a çift tıklayın)
4. **Expo Go'yu yukarı kaydırarak TAMAMEN KAPATIN**

### 2️⃣ Expo Go'daki Eski Projeyi Silin (Önerilen)

1. Expo Go'yu yeniden açın
2. "Recently opened" bölümünde **Smart Attendance** projesini bulun
3. **Sola kaydırın** ve **Delete** yapın
4. Expo Go'yu tekrar tamamen kapatın

### 3️⃣ Yeni QR Kodu Tarayın

1. **iPhone Camera** uygulamasını açın
2. Terminal'deki **YENİ QR kodu tarayın**
3. **Expo Go otomatik açılacak**
4. **İlk yüklemede 30-60 saniye bekleyin** (bundle indiriyor)

### 4️⃣ Sorun Devam Ederse

#### A) iPhone'u Yeniden Başlatın
- Bazen iOS cache'i tutabiliyor
- iPhone'u kapatıp açın
- Adım 1-3'ü tekrarlayın

#### B) Expo Go'yu Yeniden Yükleyin
1. Expo Go'yu **tamamen silin** iPhone'dan
2. App Store'dan **yeniden yükleyin**
3. Açın ve QR kodu tarayın

#### C) WiFi Bağlantısını Kontrol Edin
- iPhone ve bilgisayar **aynı WiFi ağında** olmalı
- Firewall veya antivirus **8081 portunu engelliyor olabilir**
- Modem/router'ı yeniden başlatmayı deneyin

## 🔍 Terminal'de Göreceğiniz QR Kod

```
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█ ▄▄▄▄▄ █ ██▀▀ ▀▄▀█ ▄▄▄▄▄ █
█ █   █ █  ▀█ ▀█ ▄█ █   █ █
█ █▄▄▄█ █▀  █▄▄▀▄██ █▄▄▄█ █
...
```

Bu QR kodu iPhone Camera ile tarayın!

## ⚡ Hızlı Komutlar (Expo Çalışırken)

Terminal'de şu tuşlara basabilirsiniz:

- **`r`** - Uygulamayı reload et (değişiklik sonrası)
- **`m`** - Developer menüyü aç
- **`j`** - Debugger'ı aç
- **`c`** - Console logları temizle
- **`Ctrl+C`** - Expo'yu durdur

## 🎨 Uygulama Özellikleri

Başarıyla yüklendiğinde göreceksiniz:

1. ✅ **Modern Login Ekranı**
   - Student/Instructor toggle
   - Email ve şifre input'ları
   - Social login butonları

2. ✅ **Home Dashboard**
   - Gradient header
   - Today's status card
   - Face ID ve QR Code kartları
   - Aylık istatistikler

3. ✅ **Face ID Scan** (Mor gradient)
4. ✅ **QR Code Scanner** (Mavi gradient)
5. ✅ **Attendance History** (Filtreler ile)
6. ✅ **Profile** (Modern card layout)

## ❌ Hala "App Entry Not Found" Hatası Alıyorsanız

### Son Çare: Node Modules Temizliği

```bash
# Terminal'de Expo'yu durdurun (Ctrl+C)

cd mobile-app

# Node modules'u sil
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json

# Yeniden yükle
npm install

# Temiz başlat
npx expo start -c --clear
```

### Kesin Çözüm: Development Build (Mac Gerekli)

Expo Go sınırlamalarından tamamen kurtulmak için:

```bash
# Native binary oluştur
npx expo prebuild

# iOS'ta çalıştır (sadece Mac'te)
npx expo run:ios
```

Bu şekilde tüm native özellikler çalışır.

## 📞 Destek

Sorun devam ederse:
1. Terminal loglarını kontrol edin
2. iPhone Console loglarını kontrol edin (Xcode > Devices)
3. Expo Go versiyonunu kontrol edin (en son versiyon olmalı)

## ✨ Başarı Mesajı

Uygulama başarıyla yüklendiğinde şunu göreceksiniz:

```
✓ Bundled successfully
✓ Running on iOS
```

Ve iPhone'da modern, gradient'li login ekranı açılacak! 🎉

---

**Son Güncelleme:** 30 Kasım 2025  
**Durum:** Cache temizlendi, Expo başlatıldı  
**Sonraki Adım:** iPhone'da QR kodu tarayın!

