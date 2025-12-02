import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { Course, CourseSchedule, TimeSlot } from '@shared/types'
import { useAuth } from '@/contexts/AuthContext'

// Zaman dilimlerini oluştur (08:30 - 17:30, 30dk bloklar)
const generateTimeSlots = (): TimeSlot[] => {
  const slots: TimeSlot[] = []
  for (let hour = 8; hour < 18; hour++) {
    for (let minute of [0, 30]) {
      if (hour === 17 && minute === 30) break
      slots.push({
        hour,
        minute,
        label: `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
      })
    }
  }
  return slots
}

const DAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
const TIME_SLOTS = generateTimeSlots()

interface ScheduleFormData {
  course_id: string
  day_of_week: number
  start_time: string
  end_time: string
  classroom: string
  notes: string
}

interface Teacher {
  id: string
  full_name: string
  email: string
}

export default function TimeTable() {
  const { profile } = useAuth()
  const [schedules, setSchedules] = useState<CourseSchedule[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [selectedTeacherId, setSelectedTeacherId] = useState<string>('')
  const [showModal, setShowModal] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<CourseSchedule | null>(null)
  const [formData, setFormData] = useState<ScheduleFormData>({
    course_id: '',
    day_of_week: 1,
    start_time: '08:30',
    end_time: '09:20',
    classroom: '',
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const isAdmin = profile?.role === 'admin'
  const currentTeacherId = selectedTeacherId || profile?.id || ''

  useEffect(() => {
    if (isAdmin) {
      loadTeachers()
    }
  }, [profile])

  useEffect(() => {
    loadCourses()
    loadSchedules()
  }, [profile, selectedTeacherId])

  const loadTeachers = async () => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('id, full_name, email')
        .eq('role', 'teacher')
        .eq('is_active', true)
        .order('full_name')
      
      if (error) throw error
      if (data) setTeachers(data)
    } catch (err) {
      console.error('Error loading teachers:', err)
    }
  }

  const loadCourses = async () => {
    if (!profile) return
    
    try {
      const teacherId = isAdmin ? currentTeacherId : profile.id
      if (!teacherId) {
        setCourses([])
        return
      }

      const { data, error } = await supabase
        .from('courses')
        .select('*')
        .eq('teacher_id', teacherId)
        .eq('is_active', true)
      
      if (error) throw error
      if (data) setCourses(data)
    } catch (err) {
      console.error('Error loading courses:', err)
    }
  }

  const loadSchedules = async () => {
    if (!profile) return
    
    try {
      const teacherId = isAdmin ? currentTeacherId : profile.id
      if (!teacherId) {
        setSchedules([])
        return
      }

      const { data, error } = await supabase
        .from('course_schedules')
        .select(`
          *,
          course:courses(*)
        `)
        .eq('teacher_id', teacherId)
        .eq('is_active', true)
      
      if (error) throw error
      if (data) setSchedules(data)
    } catch (err) {
      console.error('Error loading schedules:', err)
    }
  }

  const handleCellClick = (day: number, time: string) => {
    // Bu slotta zaten ders var mı kontrol et
    const existingSchedule = findScheduleAtSlot(day, time)
    
    if (existingSchedule) {
      // Düzenleme modunda aç
      setEditingSchedule(existingSchedule)
      setFormData({
        course_id: existingSchedule.course_id,
        day_of_week: existingSchedule.day_of_week,
        start_time: existingSchedule.start_time.substring(0, 5),
        end_time: existingSchedule.end_time.substring(0, 5),
        classroom: existingSchedule.classroom || '',
        notes: existingSchedule.notes || ''
      })
    } else {
      // Yeni ekleme modu
      setEditingSchedule(null)
      setFormData({
        course_id: '',
        day_of_week: day,
        start_time: time,
        end_time: addMinutes(time, 50),
        classroom: '',
        notes: ''
      })
    }
    
    setShowModal(true)
    setError(null)
  }

  const findScheduleAtSlot = (day: number, time: string): CourseSchedule | undefined => {
    return schedules.find(s => {
      if (s.day_of_week !== day) return false
      const slotTime = timeToMinutes(time)
      const startTime = timeToMinutes(s.start_time)
      const endTime = timeToMinutes(s.end_time)
      return slotTime >= startTime && slotTime < endTime
    })
  }

  const timeToMinutes = (time: string): number => {
    const [hours, minutes] = time.split(':').map(Number)
    return hours * 60 + minutes
  }

  const addMinutes = (time: string, mins: number): string => {
    const totalMins = timeToMinutes(time) + mins
    const hours = Math.floor(totalMins / 60)
    const minutes = totalMins % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
    const scheduleData = {
      course_id: formData.course_id,
      teacher_id: currentTeacherId,
      day_of_week: formData.day_of_week,
      start_time: formData.start_time + ':00',
      end_time: formData.end_time + ':00',
      classroom: formData.classroom || null,
      notes: formData.notes || null,
      academic_year: '2024-2025',
      semester: 'Güz'
    }

      if (editingSchedule) {
        // Güncelleme
        const { error } = await supabase
          .from('course_schedules')
          .update(scheduleData)
          .eq('id', editingSchedule.id)
        
        if (error) throw error
      } else {
        // Yeni ekleme
        const { error } = await supabase
          .from('course_schedules')
          .insert(scheduleData)
        
        if (error) throw error
      }

      setShowModal(false)
      loadSchedules()
    } catch (err: any) {
      console.error('Error saving schedule:', err)
      if (err.message?.includes('unique_teacher_time_slot')) {
        setError('Bu zaman diliminde zaten bir dersiniz var!')
      } else {
        setError('Ders programı kaydedilirken bir hata oluştu.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!editingSchedule) return
    if (!confirm('Bu ders saatini silmek istediğinizden emin misiniz?')) return

    setLoading(true)
    try {
      const { error } = await supabase
        .from('course_schedules')
        .update({ is_active: false })
        .eq('id', editingSchedule.id)
      
      if (error) throw error

      setShowModal(false)
      loadSchedules()
    } catch (err) {
      console.error('Error deleting schedule:', err)
      setError('Ders programı silinirken bir hata oluştu.')
    } finally {
      setLoading(false)
    }
  }

  const getScheduleColor = (courseId: string): string => {
    // Ders ID'sine göre tutarlı renk oluştur
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-orange-500',
      'bg-teal-500',
      'bg-cyan-500',
      'bg-rose-500',
      'bg-violet-500'
    ]
    const index = parseInt(courseId.substring(0, 8), 16) % colors.length
    return colors[index]
  }

  const renderCell = (day: number, timeSlot: TimeSlot) => {
    const schedule = findScheduleAtSlot(day, timeSlot.label)
    
    if (schedule) {
      const course = courses.find(c => c.id === schedule.course_id)
      const colorClass = getScheduleColor(schedule.course_id)
      
      // Bu schedule'ın kaç slot kapladığını hesapla
      const duration = timeToMinutes(schedule.end_time) - timeToMinutes(schedule.start_time)
      const slotsCount = Math.ceil(duration / 30)
      
      // Sadece başlangıç slotunda render et
      if (schedule.start_time.substring(0, 5) === timeSlot.label) {
        return (
          <div
            onClick={() => handleCellClick(day, timeSlot.label)}
            className={`${colorClass} text-white p-2 rounded-lg cursor-pointer hover:opacity-90 transition-opacity shadow-sm flex flex-col justify-center`}
            style={{ 
              gridRow: `span ${slotsCount}`,
              minHeight: `${slotsCount * 64}px`
            }}
          >
            <div className="font-semibold text-sm">{course?.course_code}</div>
            <div className="text-xs opacity-90 line-clamp-1">{course?.course_name}</div>
            {schedule.classroom && (
              <div className="text-xs mt-1 opacity-75">📍 {schedule.classroom}</div>
            )}
            <div className="text-xs opacity-75 mt-1">
              {schedule.start_time.substring(0, 5)} - {schedule.end_time.substring(0, 5)}
            </div>
          </div>
        )
      }
      return null // Devam eden slotlar için hiçbir şey render etme
    }

    return (
      <div
        onClick={() => handleCellClick(day, timeSlot.label)}
        className="h-16 border border-gray-200 hover:bg-blue-50 cursor-pointer transition-colors"
      />
    )
  }

  return (
    <div className="max-w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Haftalık Ders Programı</h2>
        <p className="text-gray-600 text-sm">
          Boş bir hücreye tıklayarak yeni ders ekleyebilir, mevcut derslere tıklayarak düzenleyebilirsiniz.
        </p>
      </div>

      {/* Admin: Öğretmen Seçici */}
      {isAdmin && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <label className="block text-sm font-medium mb-2">👨‍🏫 Öğretmen Seçin</label>
          <select
            value={selectedTeacherId}
            onChange={(e) => setSelectedTeacherId(e.target.value)}
            className="w-full max-w-md px-3 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="">Bir öğretmen seçin...</option>
            {teachers.map(teacher => (
              <option key={teacher.id} value={teacher.id}>
                {teacher.full_name} ({teacher.email})
              </option>
            ))}
          </select>
          {selectedTeacherId && (
            <p className="text-sm text-blue-700 mt-2">
              ✅ {teachers.find(t => t.id === selectedTeacherId)?.full_name} için ders programı gösteriliyor
            </p>
          )}
        </div>
      )}

      {!currentTeacherId && isAdmin && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600">
            👆 Lütfen yukarıdan bir öğretmen seçin
          </p>
        </div>
      )}

      {currentTeacherId && courses.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800">
            📚 {isAdmin ? 'Bu öğretmenin' : 'Henüz'} hiç dersi yok. Önce "Ders Listesi" sekmesinden ders ekleyin.
          </p>
        </div>
      )}

      {currentTeacherId && (
        <>

      {/* Timetable Grid */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <div className="grid grid-cols-[80px_repeat(5,minmax(120px,1fr))] gap-0">
              {/* Header */}
              <div className="bg-gray-100 p-3 border-b-2 border-r border-gray-300 font-semibold text-sm text-center sticky left-0 z-10">
                Saat
              </div>
              {DAYS.map((day) => (
                <div key={day} className="bg-gray-100 p-3 border-b-2 border-gray-300 font-semibold text-sm text-center">
                  {day}
                </div>
              ))}

              {/* Time slots */}
              {TIME_SLOTS.map((slot) => (
                <>
                  <div 
                    key={`time-${slot.label}`} 
                    className="bg-gray-50 p-3 border-b border-r border-gray-200 text-xs text-gray-600 text-center sticky left-0 z-10 flex items-center justify-center"
                  >
                    {slot.label}
                  </div>
                  {DAYS.map((day, dayIdx) => (
                    <div key={`${day}-${slot.label}`} className="border-b border-r border-gray-200">
                      {renderCell(dayIdx + 1, slot)}
                    </div>
                  ))}
                </>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">
              {editingSchedule ? 'Ders Saatini Düzenle' : 'Yeni Ders Saati Ekle'}
            </h3>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">Ders *</label>
                <select
                  value={formData.course_id}
                  onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
                  required
                  disabled={loading}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                >
                  <option value="">Ders Seçin</option>
                  {courses.map(course => (
                    <option key={course.id} value={course.id}>
                      {course.course_code} - {course.course_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1.5">Gün *</label>
                <select
                  value={formData.day_of_week}
                  onChange={(e) => setFormData({ ...formData, day_of_week: Number(e.target.value) })}
                  disabled={loading}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                >
                  {DAYS.map((day, idx) => (
                    <option key={day} value={idx + 1}>{day}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1.5">Başlangıç *</label>
                  <input
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    required
                    disabled={loading}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">Bitiş *</label>
                  <input
                    type="time"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    required
                    disabled={loading}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1.5">Sınıf</label>
                <input
                  type="text"
                  value={formData.classroom}
                  onChange={(e) => setFormData({ ...formData, classroom: e.target.value })}
                  placeholder="örn: CMP210, A101"
                  disabled={loading}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1.5">Notlar</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Ekstra bilgiler..."
                  disabled={loading}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 min-h-[60px] resize-y"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Kaydediliyor...' : (editingSchedule ? 'Güncelle' : 'Kaydet')}
                </button>
                {editingSchedule && (
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={loading}
                    className="px-4 bg-red-600 text-white py-2.5 rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Sil
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  disabled={loading}
                  className="px-4 bg-gray-200 text-gray-700 py-2.5 rounded-lg hover:bg-gray-300 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  İptal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      </>
      )}
    </div>
  )
}

