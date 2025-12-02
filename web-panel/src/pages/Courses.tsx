import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Course } from '@shared/types'
import TimeTable from '@/components/TimeTable'

export default function Courses() {
  const { profile } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [showForm, setShowForm] = useState(false)
  const [activeTab, setActiveTab] = useState<'list' | 'timetable'>('list')
  const [formData, setFormData] = useState({
    course_code: '',
    course_name: '',
    description: '',
    academic_year: '2024-2025',
    semester: 'Güz',
  })

  useEffect(() => {
    loadCourses()
  }, [profile])

  const loadCourses = async () => {
    if (!profile) return

    const query = supabase
      .from('courses')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false })

    if (profile.role !== 'admin') {
      query.eq('teacher_id', profile.id)
    }

    const { data } = await query
    if (data) setCourses(data)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const { error } = await supabase
      .from('courses')
      .insert({
        ...formData,
        teacher_id: profile?.id,
      })

    if (!error) {
      setShowForm(false)
      setFormData({
        course_code: '',
        course_name: '',
        description: '',
        academic_year: '2024-2025',
        semester: 'Güz',
      })
      loadCourses()
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Bu dersi silmek istediğinizden emin misiniz?')) return

    await supabase
      .from('courses')
      .update({ is_active: false })
      .eq('id', id)

    loadCourses()
  }

  return (
    <div className="max-w-7xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dersler</h1>
        {activeTab === 'list' && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2.5 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity font-medium"
          >
            {showForm ? 'İptal' : '+ Yeni Ders'}
          </button>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-6 border-b border-gray-200">
        <button
          onClick={() => {
            setActiveTab('list')
            setShowForm(false)
          }}
          className={`pb-3 px-2 font-medium transition-colors relative ${
            activeTab === 'list'
              ? 'text-primary'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📚 Ders Listesi
          {activeTab === 'list' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>
          )}
        </button>
        <button
          onClick={() => {
            setActiveTab('timetable')
            setShowForm(false)
          }}
          className={`pb-3 px-2 font-medium transition-colors relative ${
            activeTab === 'timetable'
              ? 'text-primary'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📅 Ders Programı
          {activeTab === 'timetable' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>
          )}
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'list' && (
        <>
          {showForm && (
        <div className="bg-white p-6 rounded-xl shadow-sm mb-6">
          <h2 className="text-xl font-semibold mb-5">Yeni Ders Ekle</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700">Ders Kodu</label>
              <input
                value={formData.course_code}
                onChange={(e) => setFormData({ ...formData, course_code: e.target.value })}
                required
                className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700">Ders Adı</label>
              <input
                value={formData.course_name}
                onChange={(e) => setFormData({ ...formData, course_name: e.target.value })}
                required
                className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700">Açıklama</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent min-h-[80px] resize-y"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Akademik Yıl</label>
                <input
                  value={formData.academic_year}
                  onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                  required
                  className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Dönem</label>
                <select
                  value={formData.semester}
                  onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                  className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option>Güz</option>
                  <option>Bahar</option>
                  <option>Yaz</option>
                </select>
              </div>
            </div>
            <button type="submit" className="px-4 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity font-medium">
              Kaydet
            </button>
          </form>
        </div>
      )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {courses.map((course) => (
              <div key={course.id} className="bg-white p-5 rounded-xl shadow-sm">
                <div className="flex justify-between items-start mb-3">
                  <span className="px-3 py-1 bg-primary text-white rounded text-xs font-semibold">
                    {course.course_code}
                  </span>
                  <button
                    onClick={() => handleDelete(course.id)}
                    className="text-danger hover:opacity-70 text-xl font-bold leading-none"
                  >
                    ✕
                  </button>
                </div>
                <h3 className="text-lg font-medium mb-2">{course.course_name}</h3>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{course.description}</p>
                <div className="text-sm text-gray-500">
                  {course.academic_year} • {course.semester}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {activeTab === 'timetable' && <TimeTable />}
    </div>
  )
}
