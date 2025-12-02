import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { AttendanceSession, Course } from '@shared/types'
import QRCode from 'qrcode'

export default function Sessions() {
  const { profile } = useAuth()
  const [sessions, setSessions] = useState<AttendanceSession[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [showForm, setShowForm] = useState(false)
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    course_id: '',
    session_name: '',
    location_lat: '',
    location_lng: '',
    location_radius: '100',
    require_face_recognition: true,
    require_gps: true,
    require_device_check: true,
  })

  useEffect(() => {
    loadCourses()
    loadSessions()
  }, [profile])

  const loadCourses = async () => {
    if (!profile) return

    const query = supabase
      .from('courses')
      .select('*')
      .eq('is_active', true)

    if (profile.role !== 'admin') {
      query.eq('teacher_id', profile.id)
    }

    const { data } = await query
    if (data) setCourses(data)
  }

  const loadSessions = async () => {
    if (!profile) return

    const query = supabase
      .from('attendance_sessions')
      .select('*')
      .order('created_at', { ascending: false })

    if (profile.role !== 'admin') {
      query.eq('teacher_id', profile.id)
    }

    const { data } = await query
    if (data) setSessions(data)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Generate unique QR code
    const sessionId = crypto.randomUUID()
    const qrExpiry = new Date()
    qrExpiry.setHours(qrExpiry.getHours() + 2)

    const { error } = await supabase
      .from('attendance_sessions')
      .insert({
        id: sessionId,
        ...formData,
        teacher_id: profile?.id,
        qr_code: sessionId,
        qr_expires_at: qrExpiry.toISOString(),
        location_lat: formData.location_lat ? parseFloat(formData.location_lat) : null,
        location_lng: formData.location_lng ? parseFloat(formData.location_lng) : null,
        location_radius: parseInt(formData.location_radius),
      })

    if (!error) {
      // Generate QR code
      const qr = await QRCode.toDataURL(sessionId)
      setQrCodeUrl(qr)
      
      setShowForm(false)
      loadSessions()
    }
  }

  const handleEndSession = async (id: string) => {
    await supabase
      .from('attendance_sessions')
      .update({ is_active: false, end_time: new Date().toISOString() })
      .eq('id', id)

    loadSessions()
  }

  const handleGenerateQR = async (sessionId: string) => {
    const qr = await QRCode.toDataURL(sessionId)
    setQrCodeUrl(qr)
  }

  return (
    <div className={styles.sessions}>
      <div className={styles.header}>
        <h1>Yoklama Oturumları</h1>
        <button onClick={() => setShowForm(!showForm)} className={styles.addButton}>
          {showForm ? 'İptal' : '+ Yeni Oturum'}
        </button>
      </div>

      {showForm && (
        <div className={styles.formCard}>
          <h2>Yeni Yoklama Oturumu</h2>
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.field}>
              <label>Ders</label>
              <select
                value={formData.course_id}
                onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
                required
              >
                <option value="">Ders seçin</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.course_code} - {course.course_name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label>Oturum Adı</label>
              <input
                value={formData.session_name}
                onChange={(e) => setFormData({ ...formData, session_name: e.target.value })}
                placeholder="Örn: Hafta 1 - Giriş"
                required
              />
            </div>
            <div className={styles.row}>
              <div className={styles.field}>
                <label>Konum - Enlem</label>
                <input
                  type="number"
                  step="any"
                  value={formData.location_lat}
                  onChange={(e) => setFormData({ ...formData, location_lat: e.target.value })}
                  placeholder="41.0082"
                />
              </div>
              <div className={styles.field}>
                <label>Konum - Boylam</label>
                <input
                  type="number"
                  step="any"
                  value={formData.location_lng}
                  onChange={(e) => setFormData({ ...formData, location_lng: e.target.value })}
                  placeholder="28.9784"
                />
              </div>
            </div>
            <div className={styles.field}>
              <label>Konum Yarıçapı (metre)</label>
              <input
                type="number"
                value={formData.location_radius}
                onChange={(e) => setFormData({ ...formData, location_radius: e.target.value })}
              />
            </div>
            <div className={styles.checkboxes}>
              <label>
                <input
                  type="checkbox"
                  checked={formData.require_face_recognition}
                  onChange={(e) => setFormData({ ...formData, require_face_recognition: e.target.checked })}
                />
                Yüz tanıma zorunlu
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={formData.require_gps}
                  onChange={(e) => setFormData({ ...formData, require_gps: e.target.checked })}
                />
                GPS doğrulama zorunlu
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={formData.require_device_check}
                  onChange={(e) => setFormData({ ...formData, require_device_check: e.target.checked })}
                />
                Cihaz kontrolü zorunlu
              </label>
            </div>
            <button type="submit" className={styles.submitButton}>
              Oturumu Başlat ve QR Oluştur
            </button>
          </form>
        </div>
      )}

      {qrCodeUrl && (
        <div className={styles.qrModal}>
          <div className={styles.qrCard}>
            <h2>QR Kod</h2>
            <img src={qrCodeUrl} alt="QR Code" />
            <p>Öğrenciler bu QR kodu taratarak yoklama verebilir</p>
            <button onClick={() => setQrCodeUrl(null)}>Kapat</button>
          </div>
        </div>
      )}

      <div className={styles.list}>
        {sessions.map((session) => (
          <div key={session.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <div>
                <h3>{session.session_name}</h3>
                <p className={styles.date}>{new Date(session.session_date).toLocaleDateString('tr-TR')}</p>
              </div>
              <span className={session.is_active ? styles.badgeActive : styles.badgeInactive}>
                {session.is_active ? 'Aktif' : 'Kapalı'}
              </span>
            </div>
            <div className={styles.requirements}>
              {session.require_qr && <span>QR</span>}
              {session.require_gps && <span>GPS</span>}
              {session.require_face_recognition && <span>Yüz Tanıma</span>}
              {session.require_device_check && <span>Cihaz</span>}
            </div>
            <div className={styles.actions}>
              {session.is_active && (
                <>
                  <button onClick={() => handleGenerateQR(session.id)} className={styles.qrButton}>
                    QR Göster
                  </button>
                  <button onClick={() => handleEndSession(session.id)} className={styles.endButton}>
                    Oturumu Kapat
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

