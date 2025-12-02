import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Profile } from '@shared/types'

export default function Users() {
  const { profile } = useAuth()
  const [users, setUsers] = useState<Profile[]>([])
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'student' as 'student' | 'teacher' | 'admin',
    student_number: '',
    phone: '',
  })

  useEffect(() => {
    if (profile?.role === 'admin') {
      loadUsers()
    }
  }, [profile])

  const loadUsers = async () => {
    const { data } = await supabase
      .from('profiles')
      .select('*')
      .order('created_at', { ascending: false })

    if (data) setUsers(data)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Create auth user
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email: formData.email,
      password: formData.password,
      email_confirm: true,
    })

    if (authError || !authData.user) {
      alert('Kullanıcı oluşturulamadı: ' + authError?.message)
      return
    }

    // Create profile
    const { error: profileError } = await supabase
      .from('profiles')
      .insert({
        id: authData.user.id,
        email: formData.email,
        full_name: formData.full_name,
        role: formData.role,
        student_number: formData.student_number || null,
        phone: formData.phone || null,
      })

    if (profileError) {
      alert('Profil oluşturulamadı: ' + profileError.message)
      return
    }

    setShowForm(false)
    setFormData({
      email: '',
      password: '',
      full_name: '',
      role: 'student',
      student_number: '',
      phone: '',
    })
    loadUsers()
  }

  const handleDelete = async (userId: string) => {
    if (!confirm('Bu kullanıcıyı silmek istediğinizden emin misiniz?')) return

    const { error } = await supabase.auth.admin.deleteUser(userId)
    
    if (!error) {
      loadUsers()
    } else {
      alert('Silme işlemi başarısız: ' + error.message)
    }
  }

  if (profile?.role !== 'admin') {
    return (
      <div className="max-w-7xl">
        <h1 className="text-2xl font-bold">Yetkisiz Erişim</h1>
        <p className="text-gray-600 mt-2">Bu sayfaya erişim yetkiniz yok.</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Kullanıcı Yönetimi</h1>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="px-4 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity font-semibold"
        >
          {showForm ? 'İptal' : '+ Yeni Kullanıcı'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-8 rounded-xl shadow-sm mb-8">
          <h2 className="text-xl font-bold mb-6">Yeni Kullanıcı Ekle</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Şifre</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  minLength={6}
                  className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700">Ad Soyad</label>
              <input
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                required
                className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Rol</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                  className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="student">Öğrenci</option>
                  <option value="teacher">Eğitmen</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Öğrenci No (Sadece öğrenci için)</label>
                <input
                  value={formData.student_number}
                  onChange={(e) => setFormData({ ...formData, student_number: e.target.value })}
                  disabled={formData.role !== 'student'}
                  className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
              </div>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700">Telefon</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <button 
              type="submit" 
              className="mt-4 px-4 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity font-semibold"
            >
              Kullanıcı Ekle
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ad Soyad</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Öğrenci No</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlem</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.full_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                      user.role === 'teacher' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {user.role === 'student' ? 'Öğrenci' : 
                       user.role === 'teacher' ? 'Eğitmen' : 'Admin'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{user.student_number || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => handleDelete(user.id)}
                      disabled={user.id === profile?.id}
                      className="px-3 py-1 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-xs font-semibold"
                    >
                      Sil
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
