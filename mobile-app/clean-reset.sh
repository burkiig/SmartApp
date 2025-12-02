#!/bin/bash

# Smart Attendance Mobile - Temizlik ve Reset Script
# macOS / Linux için

echo "🧹 Smart Attendance Mobile - Tam Temizlik Başlatılıyor..."

# 1. Watchman cache temizle
echo ""
echo "📡 Watchman cache temizleniyor..."
if command -v watchman &> /dev/null; then
    watchman watch-del-all
    echo "✅ Watchman cache temizlendi"
else
    echo "⚠️  Watchman bulunamadı, atlanıyor..."
fi

# 2. Node modules sil
echo ""
echo "📦 node_modules siliniyor..."
rm -rf node_modules
echo "✅ node_modules silindi"

# 3. .expo cache sil
echo ""
echo "🎯 .expo cache siliniyor..."
rm -rf .expo
echo "✅ .expo cache silindi"

# 4. package-lock.json sil
echo ""
echo "🔒 package-lock.json siliniyor..."
rm -f package-lock.json
echo "✅ package-lock.json silindi"

# 5. Metro bundler cache temizle
echo ""
echo "🚇 Metro bundler cache temizleniyor..."
rm -rf $TMPDIR/metro-* 2>/dev/null
rm -rf $TMPDIR/haste-* 2>/dev/null
rm -rf /tmp/metro-* 2>/dev/null
rm -rf /tmp/haste-* 2>/dev/null
echo "✅ Metro cache temizlendi"

# 6. npm cache temizle
echo ""
echo "📦 npm cache temizleniyor..."
npm cache clean --force
echo "✅ npm cache temizlendi"

# 7. iOS pods temizle (eğer ios klasörü varsa)
if [ -d "ios" ]; then
    echo ""
    echo "🍎 iOS Pods temizleniyor..."
    cd ios
    pod deintegrate 2>/dev/null
    rm -rf Pods
    rm -f Podfile.lock
    cd ..
    echo "✅ iOS Pods temizlendi"
fi

# 8. Paketleri yeniden yükle
echo ""
echo "📥 Paketler yeniden yükleniyor..."
npm install
echo "✅ Paketler yüklendi"

# 9. iOS pods yükle (eğer ios klasörü varsa)
if [ -d "ios" ]; then
    echo ""
    echo "🍎 iOS Pods yükleniyor..."
    npx pod-install ios
    echo "✅ iOS Pods yüklendi"
fi

# 10. Expo doctor çalıştır
echo ""
echo "🩺 Expo Doctor kontrolü yapılıyor..."
npx expo doctor

echo ""
echo "✨ Temizlik tamamlandı! Şimdi çalıştırmayı deneyin:"
echo "   expo start -c"

