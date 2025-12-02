import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Session } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'
import { Profile } from '@shared/types'

interface AuthContextType {
  session: Session | null
  profile: Profile | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      console.log('🔍 Session check:', session ? 'Logged in' : 'Not logged in')
      setSession(session)
      if (session) loadProfile(session.user.id)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      if (session) {
        loadProfile(session.user.id)
      } else {
        setProfile(null)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const loadProfile = async (userId: string) => {
    console.log('🔍 Loading profile for user:', userId)
    
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()
      
      console.log('🔍 Profile data:', data)
      console.log('🔍 Profile error:', error)
      
      if (error) {
        console.error('❌ Error loading profile:', error)
        console.error('❌ Error details:', error.message, error.hint, error.details)
        
        // PGSQL 42501: RLS policy violation - do not sign out immediately
        if (error.code === 'PGRST116' || error.code === '42501') {
          console.warn('⚠️ RLS policy issue detected. User might not have profile access.')
        }
        
        // Only sign out for non-RLS errors
        if (error.code !== 'PGRST116' && error.code !== '42501') {
          await signOut()
          throw error
        }
        return
      }
      
      if (data && (data.role === 'teacher' || data.role === 'admin')) {
        console.log('✅ Access granted. Role:', data.role)
        setProfile(data)
      } else {
        console.log('❌ Access denied. Role:', data?.role || 'none')
        await signOut()
        throw new Error('Only teachers and admins can access the web panel')
      }
    } catch (err) {
      console.error('❌ Unexpected error in loadProfile:', err)
      // Don't sign out on unexpected errors, let user stay logged in
      return
    }
  }

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setProfile(null)
  }

  return (
    <AuthContext.Provider value={{ session, profile, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}

