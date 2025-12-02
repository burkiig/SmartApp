import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'

interface Stats {
  totalCourses: number
  activeSessions: number
  totalStudents: number
  todayAttendance: number
}

export default function Dashboard() {
  const { profile } = useAuth()
  const [stats, setStats] = useState<Stats>({
    totalCourses: 0,
    activeSessions: 0,
    totalStudents: 0,
    todayAttendance: 0,
  })

  useEffect(() => {
    loadStats()
  }, [profile])

  const loadStats = async () => {
    if (!profile) return

    const isAdmin = profile.role === 'admin'

    // Courses
    const coursesQuery = supabase
      .from('courses')
      .select('id', { count: 'exact' })
      .eq('is_active', true)
    
    if (!isAdmin) {
      coursesQuery.eq('teacher_id', profile.id)
    }
    
    const { count: coursesCount } = await coursesQuery

    // Active sessions
    const sessionsQuery = supabase
      .from('attendance_sessions')
      .select('id', { count: 'exact' })
      .eq('is_active', true)
    
    if (!isAdmin) {
      sessionsQuery.eq('teacher_id', profile.id)
    }
    
    const { count: sessionsCount } = await sessionsQuery

    // Total students
    let studentsCount = 0
    if (isAdmin) {
      const { count } = await supabase
        .from('profiles')
        .select('id', { count: 'exact' })
        .eq('role', 'student')
      studentsCount = count || 0
    } else {
      const { data: courses } = await supabase
        .from('courses')
        .select('id')
        .eq('teacher_id', profile.id)
      
      if (courses) {
        const courseIds = courses.map(c => c.id)
        const { count } = await supabase
          .from('enrollments')
          .select('student_id', { count: 'exact' })
          .in('course_id', courseIds)
        studentsCount = count || 0
      }
    }

    // Today's attendance
    const today = new Date().toISOString().split('T')[0]
    const attendanceQuery = supabase
      .from('attendance_records')
      .select('id', { count: 'exact' })
      .gte('created_at', today)
    
    const { count: attendanceCount } = await attendanceQuery

    setStats({
      totalCourses: coursesCount || 0,
      activeSessions: sessionsCount || 0,
      totalStudents: studentsCount,
      todayAttendance: attendanceCount || 0,
    })
  }

  return (
    <div className="max-w-7xl">
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <p className="text-gray-600 mb-8">Hoş geldiniz, {profile?.full_name}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="text-4xl font-bold text-primary mb-2">{stats.totalCourses}</div>
          <div className="text-sm text-gray-600 uppercase tracking-wide">Aktif Dersler</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="text-4xl font-bold text-primary mb-2">{stats.activeSessions}</div>
          <div className="text-sm text-gray-600 uppercase tracking-wide">Açık Yoklama Oturumları</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="text-4xl font-bold text-primary mb-2">{stats.totalStudents}</div>
          <div className="text-sm text-gray-600 uppercase tracking-wide">Toplam Öğrenci</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="text-4xl font-bold text-primary mb-2">{stats.todayAttendance}</div>
          <div className="text-sm text-gray-600 uppercase tracking-wide">Bugünkü Yoklama</div>
        </div>
      </div>
    </div>
  )
}

