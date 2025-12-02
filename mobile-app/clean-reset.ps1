# Smart Attendance Mobile - Temizlik ve Reset Script
# Windows PowerShell için

Write-Host "🧹 Smart Attendance Mobile - Tam Temizlik Başlatılıyor..." -ForegroundColor Cyan

# 1. Watchman cache temizle
Write-Host "`n📡 Watchman cache temizleniyor..." -ForegroundColor Yellow
if (Get-Command watchman -ErrorAction SilentlyContinue) {
    watchman watch-del-all
    Write-Host "✅ Watchman cache temizlendi" -ForegroundColor Green
} else {
    Write-Host "⚠️  Watchman bulunamadı, atlanıyor..." -ForegroundColor DarkYellow
}

# 2. Node modules sil
Write-Host "`n📦 node_modules siliniyor..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "✅ node_modules silindi" -ForegroundColor Green
}

# 3. .expo cache sil
Write-Host "`n🎯 .expo cache siliniyor..." -ForegroundColor Yellow
if (Test-Path ".expo") {
    Remove-Item -Recurse -Force ".expo"
    Write-Host "✅ .expo cache silindi" -ForegroundColor Green
}

# 4. package-lock.json sil
Write-Host "`n🔒 package-lock.json siliniyor..." -ForegroundColor Yellow
if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json"
    Write-Host "✅ package-lock.json silindi" -ForegroundColor Green
}

# 5. Metro bundler cache temizle
Write-Host "`n🚇 Metro bundler cache temizleniyor..." -ForegroundColor Yellow
$tempPath = $env:TEMP
if (Test-Path "$tempPath\metro-*") {
    Remove-Item -Recurse -Force "$tempPath\metro-*" -ErrorAction SilentlyContinue
}
if (Test-Path "$tempPath\haste-*") {
    Remove-Item -Recurse -Force "$tempPath\haste-*" -ErrorAction SilentlyContinue
}
Write-Host "✅ Metro cache temizlendi" -ForegroundColor Green

# 6. npm cache temizle
Write-Host "`n📦 npm cache temizleniyor..." -ForegroundColor Yellow
npm cache clean --force
Write-Host "✅ npm cache temizlendi" -ForegroundColor Green

# 7. Paketleri yeniden yükle
Write-Host "`n📥 Paketler yeniden yükleniyor..." -ForegroundColor Yellow
npm install --legacy-peer-deps
Write-Host "✅ Paketler yüklendi" -ForegroundColor Green

# 8. Expo doctor çalıştır
Write-Host "`n🩺 Expo Doctor kontrolü yapılıyor..." -ForegroundColor Yellow
npx expo-doctor

Write-Host "`n✨ Temizlik tamamlandı! Şimdi çalıştırmayı deneyin:" -ForegroundColor Green
Write-Host "   expo start -c" -ForegroundColor Cyan

