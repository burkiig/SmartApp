import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

console.log('🔧 Supabase Config:')
console.log('  URL:', supabaseUrl ? '✅ Set' : '❌ Missing')
console.log('  Key:', supabaseAnonKey ? '✅ Set' : '❌ Missing')

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ CRITICAL: Supabase credentials missing!')
  console.error('Please create web-panel/.env file with:')
  console.error('VITE_SUPABASE_URL=your_url')
  console.error('VITE_SUPABASE_ANON_KEY=your_key')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

