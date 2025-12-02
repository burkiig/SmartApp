import { View, Text, TouchableOpacity, ScrollView, RefreshControl } from 'react-native'
import { useAuth } from '@/contexts/AuthContext'
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { Ionicons } from '@expo/vector-icons'
import { router } from 'expo-router'

interface AttendanceStats {
  total: number
  present: number
  late: number
  attendanceRate: number
}

export default function Home() {
  const { profile } = useAuth()
  const [stats, setStats] = useState<AttendanceStats>({ total: 0, present: 0, late: 0, attendanceRate: 0 })
  const [lastAttendance, setLastAttendance] = useState<any>(null)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    if (!profile) return

    // Load attendance stats
    const { data: records } = await supabase
      .from('attendance_records')
      .select('status, created_at, attendance_sessions(course_schedules(courses(course_name, course_code)))')
      .eq('student_id', profile.id)
      .order('created_at', { ascending: false })

    if (records) {
      const total = records.length
      const present = records.filter(r => r.status === 'present').length
      const late = records.filter(r => r.status === 'late').length
      const attendanceRate = total > 0 ? Math.round((present / total) * 100) : 0

      setStats({ total, present, late, attendanceRate })
      
      if (records.length > 0) {
        setLastAttendance(records[0])
      }
    }
  }

  const onRefresh = async () => {
    setRefreshing(true)
    await loadData()
    setRefreshing(false)
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good Morning'
    if (hour < 18) return 'Good Afternoon'
    return 'Good Evening'
  }

  return (
    <ScrollView 
      className="flex-1 bg-background"
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header with Gradient Background */}
      <View className="bg-primary pt-12 pb-8 px-6 rounded-b-3xl">
        <View className="flex-row justify-between items-start mb-6">
          <View className="flex-1">
            <Text className="text-white/80 text-base mb-1">{getGreeting()},</Text>
            <Text className="text-white text-2xl font-bold">{profile?.full_name?.split(' ')[0] || 'Student'}</Text>
          </View>
          <TouchableOpacity className="bg-white/20 p-3 rounded-xl">
            <Ionicons name="calendar-outline" size={24} color="white" />
          </TouchableOpacity>
        </View>

        {/* Today's Status Card */}
        {lastAttendance ? (
          <View className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
            <Text className="text-white/80 text-sm mb-2">Today's Status</Text>
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-white text-xl font-bold mb-1">
                  {lastAttendance.status === 'present' ? 'Marked Present' : 'Marked Late'}
                </Text>
                <Text className="text-white/70 text-sm">
                  {new Date(lastAttendance.created_at).toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })} • QR Code
                </Text>
              </View>
              <View className={`w-14 h-14 rounded-full items-center justify-center ${
                lastAttendance.status === 'present' ? 'bg-success' : 'bg-warning'
              }`}>
                <Ionicons 
                  name={lastAttendance.status === 'present' ? 'checkmark' : 'time'} 
                  size={28} 
                  color="white" 
                />
              </View>
            </View>
          </View>
        ) : (
          <View className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
            <Text className="text-white/80 text-sm mb-2">Today's Status</Text>
            <Text className="text-white text-lg font-semibold">No attendance marked yet</Text>
          </View>
        )}
      </View>

      {/* Mark Attendance Section */}
      <View className="px-6 mt-6">
        <Text className="text-gray-900 text-lg font-bold mb-4">Mark Attendance</Text>
        
        <View className="flex-row space-x-4">
          {/* Face ID Card */}
          <TouchableOpacity 
            className="flex-1 bg-gradient-to-br from-secondary to-secondary-light rounded-2xl p-5 shadow-sm"
            onPress={() => router.push('/face-scan')}
          >
            <View className="bg-white/20 w-12 h-12 rounded-xl items-center justify-center mb-3">
              <Ionicons name="scan" size={24} color="#8B5CF6" />
            </View>
            <Text className="text-gray-900 font-bold text-base mb-1">Face ID</Text>
            <Text className="text-gray-600 text-xs">Scan your face</Text>
          </TouchableOpacity>

          {/* QR Code Card */}
          <TouchableOpacity 
            className="flex-1 bg-gradient-to-br from-blue-400 to-blue-100 rounded-2xl p-5 shadow-sm"
            onPress={() => router.push('/qr-scan')}
          >
            <View className="bg-white/20 w-12 h-12 rounded-xl items-center justify-center mb-3">
              <Ionicons name="qr-code" size={24} color="#3B82F6" />
            </View>
            <Text className="text-gray-900 font-bold text-base mb-1">QR Code</Text>
            <Text className="text-gray-600 text-xs">Scan QR code</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* This Month Stats */}
      <View className="px-6 mt-6">
        <Text className="text-gray-900 text-lg font-bold mb-4">This Month</Text>
        
        <View className="bg-white rounded-2xl p-5 shadow-sm">
          {/* Attendance Rate */}
          <View className="flex-row items-center justify-between mb-4">
            <Text className="text-gray-700 font-semibold">Attendance Rate</Text>
            <View className="bg-success/10 px-3 py-1.5 rounded-full">
              <Text className="text-success font-bold text-lg">{stats.attendanceRate}%</Text>
            </View>
          </View>

          {/* Progress Bar */}
          <View className="bg-gray-100 h-3 rounded-full mb-5 overflow-hidden">
            <View 
              className="bg-success h-full rounded-full" 
              style={{ width: `${stats.attendanceRate}%` }}
            />
          </View>

          {/* Stats Row */}
          <View className="flex-row justify-between">
            <View className="items-center flex-1">
              <Text className="text-gray-500 text-xs mb-1">Total Days</Text>
              <Text className="text-gray-900 text-2xl font-bold">{stats.total}</Text>
            </View>
            
            <View className="w-px bg-gray-200 mx-2" />
            
            <View className="items-center flex-1">
              <Text className="text-gray-500 text-xs mb-1">Present</Text>
              <Text className="text-success text-2xl font-bold">{stats.present}</Text>
            </View>
            
            <View className="w-px bg-gray-200 mx-2" />
            
            <View className="items-center flex-1">
              <Text className="text-gray-500 text-xs mb-1">Late</Text>
              <Text className="text-warning text-2xl font-bold">{stats.late}</Text>
            </View>
          </View>
        </View>
      </View>

      {/* Recent Activity */}
      <View className="px-6 mt-6 mb-8">
        <View className="flex-row items-center justify-between mb-4">
          <Text className="text-gray-900 text-lg font-bold">Recent Activity</Text>
          <TouchableOpacity onPress={() => router.push('/(tabs)/history')}>
            <Text className="text-primary font-semibold text-sm">View All</Text>
          </TouchableOpacity>
        </View>

        {lastAttendance && (
          <View className="bg-white rounded-2xl p-4 shadow-sm flex-row items-center">
            <View className="bg-blue-50 w-12 h-12 rounded-xl items-center justify-center mr-4">
              <Ionicons name="qr-code" size={24} color="#3B82F6" />
            </View>
            
            <View className="flex-1">
              <Text className="text-gray-900 font-semibold mb-1">
                {new Date(lastAttendance.created_at).toLocaleDateString('en-US', { 
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric'
                })}
              </Text>
              <Text className="text-gray-500 text-sm">
                {new Date(lastAttendance.created_at).toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })} • Main Building
              </Text>
            </View>

            <View className={`px-3 py-1.5 rounded-full ${
              lastAttendance.status === 'present' ? 'bg-success/10' : 'bg-warning/10'
            }`}>
              <Text className={`text-xs font-semibold ${
                lastAttendance.status === 'present' ? 'text-success' : 'text-warning'
              }`}>
                {lastAttendance.status === 'present' ? 'Present' : 'Late'}
              </Text>
            </View>
          </View>
        )}
      </View>
    </ScrollView>
  )
}
