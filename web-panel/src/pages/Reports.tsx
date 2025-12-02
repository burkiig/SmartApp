import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Course } from '@shared/types'

interface AttendanceStats {
  student_name: string
  student_number: string
  total_sessions: number
  attended: number
  attendance_rate: number
}

export default function Reports() {
  const { profile } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourse, setSelectedCourse] = useState('')
  const [stats, setStats] = useState<AttendanceStats[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadCourses()
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

  const loadReport = async () => {
    if (!selectedCourse) return

    setLoading(true)

    // Get all sessions for this course
    const { data: sessions } = await supabase
      .from('attendance_sessions')
      .select('id')
      .eq('course_id', selectedCourse)

    if (!sessions) {
      setLoading(false)
      return
    }

    const sessionIds = sessions.map(s => s.id)
    const totalSessions = sessionIds.length

    // Get enrollments
    const { data: enrollments } = await supabase
      .from('enrollments')
      .select('student_id, profiles!inner(*)')
      .eq('course_id', selectedCourse)

    if (!enrollments) {
      setLoading(false)
      return
    }

    // Calculate attendance for each student
    const statsPromises = enrollments.map(async (enrollment: any) => {
      const { count } = await supabase
        .from('attendance_records')
        .select('id', { count: 'exact' })
        .eq('student_id', enrollment.student_id)
        .in('session_id', sessionIds)
        .eq('status', 'present')

      const attended = count || 0
      const rate = totalSessions > 0 ? (attended / totalSessions) * 100 : 0

      return {
        student_name: enrollment.profiles.full_name,
        student_number: enrollment.profiles.student_number,
        total_sessions: totalSessions,
        attended,
        attendance_rate: Math.round(rate),
      }
    })

    const results = await Promise.all(statsPromises)
    setStats(results.sort((a, b) => b.attendance_rate - a.attendance_rate))
    setLoading(false)
  }

  const exportToCSV = () => {
    const headers = ['Öğrenci No', 'Ad Soyad', 'Toplam Oturum', 'Katıldığı Oturum', 'Devam Oranı (%)']
    const rows = stats.map(s => [
      s.student_number,
      s.student_name,
      s.total_sessions,
      s.attended,
      s.attendance_rate,
    ])

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `devamsizlik-raporu-${Date.now()}.csv`
    a.click()
  }

  return (
    <div className={styles.reports}>
      <h1>Devamsızlık Raporları</h1>

      <div className={styles.filters}>
        <div className={styles.field}>
          <label>Ders Seçin</label>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
          >
            <option value="">Ders seçin</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.course_code} - {course.course_name}
              </option>
            ))}
          </select>
        </div>
        <button onClick={loadReport} disabled={!selectedCourse || loading} className={styles.generateButton}>
          {loading ? 'Yükleniyor...' : 'Rapor Oluştur'}
        </button>
      </div>

      {stats.length > 0 && (
        <>
          <div className={styles.actions}>
            <button onClick={exportToCSV} className={styles.exportButton}>
              CSV İndir
            </button>
          </div>

          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Öğrenci No</th>
                  <th>Ad Soyad</th>
                  <th>Toplam Oturum</th>
                  <th>Katıldığı</th>
                  <th>Devam Oranı</th>
                </tr>
              </thead>
              <tbody>
                {stats.map((stat, index) => (
                  <tr key={index}>
                    <td>{stat.student_number}</td>
                    <td>{stat.student_name}</td>
                    <td>{stat.total_sessions}</td>
                    <td>{stat.attended}</td>
                    <td>
                      <span className={
                        stat.attendance_rate >= 80 ? styles.good :
                        stat.attendance_rate >= 60 ? styles.warning :
                        styles.danger
                      }>
                        %{stat.attendance_rate}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}

