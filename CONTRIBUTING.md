# Katkıda Bulunma Rehberi

Smart Attendance System projesine katkıda bulunmak istediğiniz için teşekkürler! 🎉

## 🚀 Başlamadan Önce

1. [GETTING_STARTED.md](GETTING_STARTED.md) rehberini okuyun
2. Projeyi local'de çalıştırın
3. [Issues](https://github.com/your-repo/issues) sayfasını kontrol edin

## 📝 Katkı Türleri

### 🐛 Bug Report
- GitHub Issues'da yeni issue açın
- Bug template'ini kullanın
- Repro steps ekleyin
- Screenshots/logs ekleyin

### 💡 Feature Request
- Önce Issues'da tartışın
- Use case açıklayın
- Mockup/wireframe ekleyin (varsa)

### 🔧 Code Contribution
Pull Request açmadan önce:
1. Issue oluşturun ve tartışın
2. Fork yapın
3. Feature branch oluşturun
4. Kod yazın
5. Test edin
6. PR açın

## 🌳 Branch Stratejisi

```
main          # Production-ready code
├── develop   # Development branch
└── feature/* # Feature branches
```

Branch isimlendirme:
- `feature/add-realtime-notifications`
- `fix/qr-scanner-crash`
- `docs/update-deployment-guide`

## 💻 Kod Standartları

### TypeScript
```typescript
// ✅ Good
interface AttendanceRecord {
  id: string
  studentId: string
  status: AttendanceStatus
}

// ❌ Bad
const data: any = {}
```

### React Components
```typescript
// ✅ Good - Functional component with proper types
interface Props {
  title: string
  onPress: () => void
}

export function Button({ title, onPress }: Props) {
  return <button onClick={onPress}>{title}</button>
}

// ❌ Bad - No types
export function Button(props) {
  return <button onClick={props.onPress}>{props.title}</button>
}
```

### Naming Conventions
- **Components**: PascalCase (`UserProfile.tsx`)
- **Functions**: camelCase (`handleSubmit`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)
- **Files**: kebab-case (`user-profile.ts`)

## 🧪 Testing

### Mobil Uygulama
```bash
cd mobile-app
npm run test
```

### Web Panel
```bash
cd web-panel
npm run test
```

### E2E Tests (gelecek)
```bash
npm run test:e2e
```

## 📦 Commit Mesajları

[Conventional Commits](https://www.conventionalcommits.org/) kullanın:

```
feat: Add face recognition confidence threshold
fix: Resolve QR scanner crash on iOS
docs: Update API documentation
style: Format code with prettier
refactor: Simplify attendance logic
test: Add unit tests for auth context
chore: Update dependencies
```

Örnekler:
- ✅ `feat(mobile): Add QR code scanner`
- ✅ `fix(web): Resolve login redirect issue`
- ✅ `docs: Add deployment guide for Azure`
- ❌ `Update stuff`
- ❌ `Fixed bug`

## 🔍 Pull Request Süreci

1. **Branch Oluştur**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Kod Yaz ve Test Et**
   ```bash
   npm run test
   npm run build
   ```

3. **Commit Yap**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

4. **Push Et**
   ```bash
   git push origin feature/my-feature
   ```

5. **PR Aç**
   - Base branch: `develop`
   - Clear title ve description
   - Screenshots ekle (UI değişiklikleri için)
   - Related issues'ı link'le

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Tested on iOS
- [ ] Tested on Android
- [ ] Tested on web

## Screenshots
(if applicable)

## Related Issues
Closes #123
```

## 📋 Checklist

PR açmadan önce kontrol edin:

- [ ] Kod derlenebiliyor (`npm run build`)
- [ ] Testler geçiyor (`npm run test`)
- [ ] TypeScript hataları yok (`npx tsc --noEmit`)
- [ ] Linter hataları yok
- [ ] Console.log'lar temizlendi
- [ ] Environment variables güvenli
- [ ] RLS politikaları güncel
- [ ] Dokümantasyon güncellendi
- [ ] Commit mesajları düzenli
- [ ] Branch güncel (`git pull origin develop`)

## 🎨 UI/UX Katkıları

- Figma/Sketch dosyaları kabul edilir
- Accessibility düşünün (WCAG 2.1)
- Mobile-first yaklaşım
- Dark mode desteği (gelecek)

## 🔒 Güvenlik

Güvenlik açığı bulursanız:
- ❌ Public issue açmayın
- ✅ security@example.com adresine email gönderin
- Responsible disclosure policy'yi takip edin

## 📖 Dokümantasyon

Dokümantasyon katkıları çok değerlidir:
- README güncellemeleri
- Kod yorumları (JSDoc)
- API dokümantasyonu
- Tutorial'lar
- Çeviri (i18n)

## 🌍 Yerelleştirme (i18n)

Şu an sadece Türkçe destekleniyor. İngilizce ve diğer diller için katkılar bekliyoruz.

## ❓ Sorular

- 📧 Email: support@example.com
- 💬 Discussions: GitHub Discussions
- 📚 Wiki: Project Wiki

## 🙏 Code of Conduct

- Saygılı olun
- Yapıcı geri bildirim verin
- Kapsayıcı bir topluluk oluşturun
- Başkalarının fikirlerine açık olun

## 📜 Lisans

Katkıda bulunarak, kodunuzun MIT lisansı altında lisanslanmasını kabul edersiniz.

---

Teşekkürler! 🎉

