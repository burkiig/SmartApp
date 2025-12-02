import { useEffect } from 'react'
import { View, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { useAuth } from '@/contexts/AuthContext'

export default function Index() {
  const { session, profile, loading } = useAuth()

  useEffect(() => {
    if (!loading) {
      if (session && profile) {
        router.replace('/(tabs)/home')
      } else {
        router.replace('/login')
      }
    }
  }, [session, profile, loading])

  return (
    <View className="flex-1 justify-center items-center">
      <ActivityIndicator size="large" color="#007AFF" />
    </View>
  )
}

