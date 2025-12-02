import { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, ScrollView, RefreshControl } from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'

interface AttendanceRecord {
  id: string
  status: 'present' | 'late' | 'absent'
  created_at: string
  qr_verified: boolean
  attendance_sessions: {
    course_schedules: {
      courses: {
        course_name: string
        course_code: string
      }
    }
  }
}

export default function History() {
  const { profile } = useAuth()
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [stats, setStats] = useState({ total: 0, present: 0, late: 0, attendanceRate: 0 })
  const [filter, setFilter] = useState<'all' | 'present' | 'late'>('all')
  const [refreshing, setRefreshing] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRecords()
  }, [])

  const loadRecords = async () => {
    if (!profile) return

    try {
      const { data, error } = await supabase
        .from('attendance_records')
        .select(`
          id,
          status,
          created_at,
          qr_verified,
          attendance_sessions(
            course_schedules(
              courses(
                course_name,
                course_code
              )
            )
          )
        `)
        .eq('student_id', profile.id)
        .order('created_at', { ascending: false })

      if (error) throw error

      if (data) {
        setRecords(data as any)
        
        const total = data.length
        const present = data.filter(r => r.status === 'present').length
        const late = data.filter(r => r.status === 'late').length
        const attendanceRate = total > 0 ? Math.round((present / total) * 100) : 0

        setStats({ total, present, late, attendanceRate })
      }
    } catch (error) {
      console.error('Error loading records:', error)
    } finally {
      setLoading(false)
    }
  }

  const onRefresh = async () => {
    setRefreshing(true)
    await loadRecords()
    setRefreshing(false)
  }

  const filteredRecords = records.filter(record => {
    if (filter === 'all') return true
    return record.status === filter
  })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const day = date.toLocaleDateString('en-US', { weekday: 'short' })
    const month = date.toLocaleDateString('en-US', { month: 'short' })
    const dayNum = date.getDate()
    return { day, month, dayNum }
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="bg-primary pt-12 pb-6 px-6 rounded-b-3xl">
        <View className="flex-row items-center justify-between mb-6">
          <TouchableOpacity 
            onPress={() => router.back()}
            className="flex-row items-center"
          >
            <Ionicons name="arrow-back" size={24} color="white" />
            <Text className="text-white text-base font-semibold ml-2">Back</Text>
          </TouchableOpacity>

          <TouchableOpacity className="bg-white/20 p-2 rounded-lg">
            <Ionicons name="download-outline" size={20} color="white" />
          </TouchableOpacity>
        </View>

        <Text className="text-white text-3xl font-bold mb-2">Attendance History</Text>
        <Text className="text-white/80 text-base">View your attendance records</Text>
      </View>

      <ScrollView
        className="flex-1"
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Stats Cards */}
        <View className="px-6 mt-6">
          <View className="flex-row space-x-3 mb-4">
            <View className="flex-1 bg-white rounded-2xl p-4 shadow-sm">
              <View className="flex-row items-center justify-between mb-1">
                <Ionicons name="calendar-outline" size={20} color="#6B7280" />
                <View className="bg-primary/10 px-2 py-0.5 rounded-full">
                  <Ionicons name="checkmark" size={12} color="#4F46E5" />
                </View>
              </View>
              <Text className="text-gray-900 text-2xl font-bold mb-1">{stats.total}</Text>
              <Text className="text-gray-500 text-xs">Total</Text>
            </View>

            <View className="flex-1 bg-white rounded-2xl p-4 shadow-sm">
              <View className="flex-row items-center justify-between mb-1">
                <Ionicons name="checkmark-circle" size={20} color="#10B981" />
                <View className="bg-success/10 px-2 py-0.5 rounded-full">
                  <Ionicons name="trending-up" size={12} color="#10B981" />
                </View>
              </View>
              <Text className="text-gray-900 text-2xl font-bold mb-1">{stats.present}</Text>
              <Text className="text-gray-500 text-xs">Present</Text>
            </View>

            <View className="flex-1 bg-white rounded-2xl p-4 shadow-sm">
              <View className="flex-row items-center justify-between mb-1">
                <Ionicons name="time" size={20} color="#F59E0B" />
                <View className="bg-warning/10 px-2 py-0.5 rounded-full">
                  <Ionicons name="alert" size={12} color="#F59E0B" />
                </View>
              </View>
              <Text className="text-gray-900 text-2xl font-bold mb-1">{stats.late}</Text>
              <Text className="text-gray-500 text-xs">Late</Text>
            </View>
          </View>

          {/* Overall Attendance Rate */}
          <View className="bg-primary rounded-2xl p-5 shadow-sm mb-6">
            <View className="flex-row items-center justify-between mb-3">
              <Text className="text-white font-bold text-lg">Overall Attendance Rate</Text>
              <Text className="text-white text-3xl font-bold">{stats.attendanceRate}%</Text>
            </View>
            <View className="bg-white/20 h-2 rounded-full overflow-hidden">
              <View 
                className="bg-white h-full rounded-full" 
                style={{ width: `${stats.attendanceRate}%` }}
              />
            </View>
          </View>

          {/* Filter Tabs */}
          <View className="flex-row bg-white rounded-xl p-1 mb-4 shadow-sm">
            <TouchableOpacity
              className={`flex-1 py-2.5 rounded-lg ${filter === 'all' ? 'bg-primary' : 'bg-transparent'}`}
              onPress={() => setFilter('all')}
            >
              <Text className={`text-center font-semibold ${filter === 'all' ? 'text-white' : 'text-gray-600'}`}>
                All
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              className={`flex-1 py-2.5 rounded-lg ${filter === 'present' ? 'bg-success' : 'bg-transparent'}`}
              onPress={() => setFilter('present')}
            >
              <Text className={`text-center font-semibold ${filter === 'present' ? 'text-white' : 'text-gray-600'}`}>
                Present
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              className={`flex-1 py-2.5 rounded-lg ${filter === 'late' ? 'bg-warning' : 'bg-transparent'}`}
              onPress={() => setFilter('late')}
            >
              <Text className={`text-center font-semibold ${filter === 'late' ? 'text-white' : 'text-gray-600'}`}>
                Late
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Records List */}
        <View className="px-6 pb-6">
          <View className="flex-row items-center justify-between mb-4">
            <Text className="text-gray-900 font-bold text-lg">Records</Text>
            <TouchableOpacity className="flex-row items-center">
              <Ionicons name="filter" size={18} color="#4F46E5" />
              <Text className="text-primary font-semibold text-sm ml-1">Filter</Text>
            </TouchableOpacity>
          </View>

          {loading ? (
            <View className="bg-white rounded-2xl p-8 items-center">
              <Text className="text-gray-500">Loading...</Text>
            </View>
          ) : filteredRecords.length === 0 ? (
            <View className="bg-white rounded-2xl p-8 items-center">
              <Ionicons name="document-text-outline" size={48} color="#D1D5DB" />
              <Text className="text-gray-500 mt-4">No records found</Text>
            </View>
          ) : (
            <View className="space-y-3">
              {filteredRecords.map((record) => {
                const { day, month, dayNum } = formatDate(record.created_at)
                const time = formatTime(record.created_at)
                
                return (
                  <View key={record.id} className="bg-white rounded-2xl p-4 shadow-sm flex-row items-center">
                    {/* Date Badge */}
                    <View className="bg-primary rounded-xl w-16 h-16 items-center justify-center mr-4">
                      <Text className="text-white text-xs font-semibold">{day}</Text>
                      <Text className="text-white text-xl font-bold">{dayNum}</Text>
                    </View>

                    {/* Info */}
                    <View className="flex-1">
                      <View className="flex-row items-center mb-1">
                        <Ionicons 
                          name={record.qr_verified ? 'qr-code' : 'scan'} 
                          size={16} 
                          color="#3B82F6" 
                        />
                        <Text className="text-gray-900 font-semibold ml-2">{time}</Text>
                      </View>
                      <Text className="text-gray-500 text-sm">
                        {record.qr_verified ? 'QR Code' : 'Face ID'} • Main Building
                      </Text>
                    </View>

                    {/* Status Badge */}
                    <View className={`px-4 py-2 rounded-xl ${
                      record.status === 'present' ? 'bg-success/10' : 'bg-warning/10'
                    }`}>
                      <Text className={`text-xs font-bold ${
                        record.status === 'present' ? 'text-success' : 'text-warning'
                      }`}>
                        {record.status === 'present' ? 'Present' : 'Late'}
                      </Text>
                    </View>
                  </View>
                )
              })}
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  )
}

