import { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, ScrollView, RefreshControl } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'
import { router } from 'expo-router'

interface AttendanceRecord {
  id: string
  status: 'present' | 'late' | 'absent'
  created_at: string
  qr_verified: boolean
}

export default function Attendance() {
  const { profile } = useAuth()
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [stats, setStats] = useState({ total: 0, present: 0, late: 0, attendanceRate: 0 })
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
        .select('id, status, created_at, qr_verified')
        .eq('student_id', profile.id)
        .order('created_at', { ascending: false })
        .limit(10)

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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short',
      day: 'numeric'
    })
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <ScrollView 
      className="flex-1 bg-background"
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View className="bg-primary pt-12 pb-8 px-6 rounded-b-3xl">
        <Text className="text-white text-3xl font-bold mb-2">Attendance History</Text>
        <Text className="text-white/80 text-base">Track your attendance records</Text>
      </View>

      {/* Quick Stats */}
      <View className="px-6 mt-6">
        <View className="flex-row space-x-3 mb-6">
          <View className="flex-1 bg-white rounded-2xl p-4 shadow-sm">
            <Ionicons name="calendar" size={24} color="#4F46E5" />
            <Text className="text-gray-900 text-2xl font-bold mt-2">{stats.total}</Text>
            <Text className="text-gray-500 text-xs">Total</Text>
          </View>

          <View className="flex-1 bg-white rounded-2xl p-4 shadow-sm">
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text className="text-gray-900 text-2xl font-bold mt-2">{stats.present}</Text>
            <Text className="text-gray-500 text-xs">Present</Text>
          </View>

          <View className="flex-1 bg-white rounded-2xl p-4 shadow-sm">
            <Ionicons name="time" size={24} color="#F59E0B" />
            <Text className="text-gray-900 text-2xl font-bold mt-2">{stats.late}</Text>
            <Text className="text-gray-500 text-xs">Late</Text>
          </View>
        </View>

        {/* View All Button */}
        <TouchableOpacity 
          className="bg-primary rounded-2xl p-4 mb-6 flex-row items-center justify-between"
          onPress={() => router.push('/history')}
        >
          <View>
            <Text className="text-white font-bold text-lg">View Full History</Text>
            <Text className="text-white/70 text-sm">See all your attendance records</Text>
          </View>
          <Ionicons name="arrow-forward" size={24} color="white" />
        </TouchableOpacity>

        {/* Recent Records */}
        <Text className="text-gray-900 font-bold text-lg mb-4">Recent Records</Text>
        
        {loading ? (
          <View className="bg-white rounded-2xl p-8 items-center">
            <Text className="text-gray-500">Loading...</Text>
          </View>
        ) : records.length === 0 ? (
          <View className="bg-white rounded-2xl p-8 items-center">
            <Ionicons name="document-text-outline" size={48} color="#D1D5DB" />
            <Text className="text-gray-500 mt-4">No records found</Text>
          </View>
        ) : (
          <View className="space-y-3 mb-6">
            {records.map((record) => (
              <View key={record.id} className="bg-white rounded-2xl p-4 shadow-sm flex-row items-center">
                <View className={`w-12 h-12 rounded-xl items-center justify-center mr-4 ${
                  record.qr_verified ? 'bg-blue-50' : 'bg-purple-50'
                }`}>
                  <Ionicons 
                    name={record.qr_verified ? 'qr-code' : 'scan'} 
                    size={24} 
                    color={record.qr_verified ? '#3B82F6' : '#8B5CF6'} 
                  />
                </View>
                
                <View className="flex-1">
                  <Text className="text-gray-900 font-semibold mb-1">
                    {formatDate(record.created_at)} • {formatTime(record.created_at)}
                  </Text>
                  <Text className="text-gray-500 text-sm">
                    {record.qr_verified ? 'QR Code' : 'Face ID'} Scan
                  </Text>
                </View>

                <View className={`px-3 py-1.5 rounded-full ${
                  record.status === 'present' ? 'bg-success/10' : 'bg-warning/10'
                }`}>
                  <Text className={`text-xs font-bold ${
                    record.status === 'present' ? 'text-success' : 'text-warning'
                  }`}>
                    {record.status === 'present' ? 'Present' : 'Late'}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </View>
    </ScrollView>
  )
}

