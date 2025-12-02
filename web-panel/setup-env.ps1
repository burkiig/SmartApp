# Web Panel Environment Setup Script
# Bu script .env dosyasını otomatik oluşturur

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Smart Attendance - Web Panel Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$envFile = ".env"
$configFile = "supabase.config.txt"

# Zaten .env varsa uyar
if (Test-Path $envFile) {
    Write-Host "⚠️  .env dosyası zaten mevcut!" -ForegroundColor Yellow
    $overwrite = Read-Host "Üzerine yazmak ister misiniz? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "❌ İşlem iptal edildi." -ForegroundColor Red
        exit
    }
}

# supabase.config.txt'den bilgileri oku
if (Test-Path $configFile) {
    Write-Host "📄 $configFile dosyasından bilgiler okunuyor..." -ForegroundColor Green
    
    $url = (Get-Content $configFile | Select-String "VITE_SUPABASE_URL=").ToString().Split("=")[1]
    $key = (Get-Content $configFile | Select-String "VITE_SUPABASE_ANON_KEY=").ToString().Split("=")[1]
    
    if ($url -and $key) {
        Write-Host "✅ Supabase bilgileri bulundu" -ForegroundColor Green
        Write-Host "   URL: $url" -ForegroundColor Gray
        Write-Host "   Key: $($key.Substring(0,20))..." -ForegroundColor Gray
        
        # .env dosyasını oluştur
        @"
VITE_SUPABASE_URL=$url
VITE_SUPABASE_ANON_KEY=$key
"@ | Out-File -FilePath $envFile -Encoding UTF8
        
        Write-Host ""
        Write-Host "✅ .env dosyası başarıyla oluşturuldu!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Sıradaki Adımlar:" -ForegroundColor Cyan
        Write-Host "   1. Supabase veritabanını kontrol edin (SETUP.md'ye bakın)" -ForegroundColor White
        Write-Host "   2. Test kullanıcısı oluşturun" -ForegroundColor White
        Write-Host "   3. Dev server'ı başlatın: npm run dev" -ForegroundColor White
        Write-Host ""
        Write-Host "📖 Detaylı bilgi için SETUP.md dosyasını okuyun" -ForegroundColor Yellow
        
    } else {
        Write-Host "❌ Supabase bilgileri okunamadı!" -ForegroundColor Red
        Write-Host "   Lütfen $configFile dosyasını kontrol edin" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "❌ $configFile dosyası bulunamadı!" -ForegroundColor Red
    Write-Host "   Manuel olarak .env dosyası oluşturun:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   VITE_SUPABASE_URL=your_url" -ForegroundColor Gray
    Write-Host "   VITE_SUPABASE_ANON_KEY=your_key" -ForegroundColor Gray
}

Write-Host ""

