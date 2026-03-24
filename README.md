1. Temel Hedef: Eğitmen tarafında yoklama alma süresini ve eforunu sıfıra indirmek; öğrenci tarafında güvenli, hızlı ve otonom bir yoklama deneyimi sunmak.
2. Eğitmen (Instructor) Deneyimi ve Yetkileri:
•	Eğitmen ders esnasında herhangi bir uygulama açmaz veya yoklama başlatma butonu kullanmaz.
•	Sistem, eğitmene haftalık veya statik bir QR kod üretir. Eğitmen bu QR kodu ders materyallerine (slayt/not) ekler.
•	Yoklama oturumları, veritabanındaki ders programına (Course Schedule) göre sistem tarafından otomatik olarak başlatılır ve süresi dolduğunda kapatılır.
•	Ders İptali (Class Cancellation): Eğitmen derse katılamayacağı durumlarda, kendi paneli üzerinden o günkü/haftaki dersi iptal edebilir. Bu durumda sistem o gün için otomatik yoklama oturumu açmaz.
•	Eğitmen, sadece istisnai durumlarda manuel yoklama (Manual Attendance) girebilir.
3. Öğrenci (Student) Deneyimi ve Güvenlik Zinciri: Yoklama sürecinin başarılı sayılması için aşağıdaki adımlar sırasıyla, katı bir şekilde uygulanır:
•	Adım 1 (Location/GPS): Öğrencinin cihazından alınan GPS koordinatları, sınıfın kayıtlı koordinatlarıyla eşleşmelidir (Geofencing). Sınıf sınırları dışındaki öğrenciler için yüz tanıma ve QR okuma fonksiyonları kilitlenir/devre dışı bırakılır.
•	Adım 2 (Face Scan): GPS doğrulaması geçen öğrenci, yüz taraması (Face Recognition) yapmak zorundadır. (Sisteme kayıtlı değilse önce yüz kayıt işlemi gerçekleşir).
•	Adım 3 (QR Scan): Yüzü eşleşen öğrenciye QR okuyucu ekranı açılır. Öğrenci, eğitmenin materyalindeki QR kodu okutur.
•	Bu 3 adım başarılı olduğunda yoklama sisteme otomatik olarak "Present" (Geldi) şeklinde kaydedilir.
4. İstisnai Durumlar ve Ekstra Özellikler (Edge Cases & Features):
•	Anlık Bildirimler (Push Notifications): Eğitmen bir dersi iptal ettiğinde, o derse kayıtlı olan tüm öğrencilerin mobil cihazlarına anında iptal bildirimi (Push Notification) gönderilir.
•	Flagged Attendance (Şüpheli Yoklama): Sistem bir anormallik sezerse (örn: yüz eşleşme oranı sınırda ise veya konum sınıf sınırının çok ucunda görünüyorsa), yoklama reddedilmez ancak eğitmenin paneline "Flagged (İncelenmeli)" olarak düşer.
•	Excuses (Mazeret Bildirimi): Derse katılamayan öğrenci, mobil uygulama üzerinden ilgili dersi seçerek mazeret (doktor raporu, fotoğraf vb. belge) yükleyebilir. Bu mazeretler eğitmenin paneline onay/red için düşer.

