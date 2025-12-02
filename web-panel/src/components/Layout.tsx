import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

export default function Layout() {
  const { profile, signOut } = useAuth()
  const navigate = useNavigate()
  const isAdmin = profile?.role === 'admin'

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold mb-1">Smart Attendance</h2>
          <p className="text-sm text-gray-600">
            {profile?.role === 'admin' ? 'Admin Panel' : 'Eğitmen Paneli'}
          </p>
        </div>
        
        <nav className="flex-1 p-4 flex flex-col gap-1">
          <NavLink 
            to="/" 
            className={({ isActive }) => 
              `px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-primary text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            Dashboard
          </NavLink>
          <NavLink 
            to="/courses" 
            className={({ isActive }) => 
              `px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-primary text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            Dersler
          </NavLink>
          <NavLink 
            to="/sessions" 
            className={({ isActive }) => 
              `px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-primary text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            Yoklama Oturumları
          </NavLink>
          <NavLink 
            to="/reports" 
            className={({ isActive }) => 
              `px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-primary text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            Raporlar
          </NavLink>
          {isAdmin && (
            <NavLink 
              to="/users" 
              className={({ isActive }) => 
                `px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-primary text-white' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              Kullanıcı Yönetimi
            </NavLink>
          )}
        </nav>
        
        <div className="p-4 border-t border-gray-200">
          <p className="text-sm font-medium mb-1">{profile?.full_name}</p>
          <p className="text-xs text-gray-600 mb-3">{profile?.email}</p>
          <button 
            onClick={handleSignOut} 
            className="w-full px-4 py-2 bg-danger text-white rounded-lg hover:opacity-90 transition-opacity text-sm font-medium"
          >
            Çıkış Yap
          </button>
        </div>
      </aside>
      
      <main className="flex-1 p-6 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}

