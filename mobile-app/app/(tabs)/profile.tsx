import { View, Text, TouchableOpacity, Image, Alert, ScrollView } from 'react-native'
import * as ImagePicker from 'expo-image-picker'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { router } from 'expo-router'
import { useState } from 'react'
import { Ionicons } from '@expo/vector-icons'

export default function Profile() {
  const { profile, signOut } = useAuth()
  const [uploading, setUploading] = useState(false)

  const handleUploadFacePhoto = async () => {
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
      allowsEditing: true,
      aspect: [1, 1],
    })

    if (result.canceled) return

    setUploading(true)
    try {
      const photo = result.assets[0]
      const ext = photo.uri.split('.').pop()
      const fileName = `${profile?.id}_reference.${ext}`

      const { error: uploadError } = await supabase.storage
        .from('face-photos')
        .upload(fileName, {
          uri: photo.uri,
          type: `image/${ext}`,
          name: fileName,
        } as any, { upsert: true })

      if (uploadError) throw uploadError

      const { data: { publicUrl } } = supabase.storage
        .from('face-photos')
        .getPublicUrl(fileName)

      const { error: updateError } = await supabase
        .from('profiles')
        .update({ face_image_url: publicUrl })
        .eq('id', profile?.id)

      if (updateError) throw updateError

      Alert.alert('Success', 'Face photo updated successfully')
    } catch (error: any) {
      Alert.alert('Error', error.message)
    } finally {
      setUploading(false)
    }
  }

  const handleSignOut = async () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Sign Out', 
          style: 'destructive',
          onPress: async () => {
            await signOut()
            router.replace('/login')
          }
        }
      ]
    )
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <ScrollView className="flex-1 bg-background">
      {/* Header with Gradient */}
      <View className="bg-primary pt-12 pb-24 px-6">
        <View className="flex-row items-center justify-between mb-8">
          <TouchableOpacity onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
          <Text className="text-white text-xl font-bold">Profile</Text>
          <TouchableOpacity onPress={handleUploadFacePhoto}>
            <Ionicons name="settings-outline" size={24} color="white" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Profile Card - Overlapping Header */}
      <View className="px-6 -mt-16">
        <View className="bg-white rounded-3xl p-6 shadow-lg">
          {/* Avatar */}
          <View className="items-center -mt-16 mb-4">
            {profile?.face_image_url ? (
              <View className="relative">
                <Image 
                  source={{ uri: profile.face_image_url }} 
                  className="w-28 h-28 rounded-full border-4 border-white"
                />
                <TouchableOpacity 
                  className="absolute bottom-0 right-0 bg-primary w-10 h-10 rounded-full items-center justify-center border-4 border-white"
                  onPress={handleUploadFacePhoto}
                >
                  <Ionicons name="camera" size={18} color="white" />
                </TouchableOpacity>
              </View>
            ) : (
              <View className="relative">
                <View className="w-28 h-28 rounded-full bg-primary justify-center items-center border-4 border-white">
                  <Text className="text-4xl text-white font-bold">
                    {getInitials(profile?.full_name || 'User')}
                  </Text>
                </View>
                <TouchableOpacity 
                  className="absolute bottom-0 right-0 bg-primary w-10 h-10 rounded-full items-center justify-center border-4 border-white"
                  onPress={handleUploadFacePhoto}
                >
                  <Ionicons name="camera" size={18} color="white" />
                </TouchableOpacity>
              </View>
            )}
          </View>

          {/* User Info */}
          <Text className="text-2xl font-bold text-gray-900 text-center mb-1">
            {profile?.full_name || 'John Doe'}
          </Text>
          <Text className="text-base text-gray-500 text-center mb-6">
            Employee ID: {profile?.student_number || 'EMP001'}
          </Text>

          {/* Info Items */}
          <View className="space-y-4">
            <View className="flex-row items-center bg-gray-50 rounded-xl p-4">
              <View className="bg-blue-100 w-10 h-10 rounded-xl items-center justify-center mr-4">
                <Ionicons name="mail" size={20} color="#3B82F6" />
              </View>
              <View className="flex-1">
                <Text className="text-gray-500 text-xs mb-1">Email</Text>
                <Text className="text-gray-900 font-semibold">
                  {profile?.email || 'john.doe@company.com'}
                </Text>
              </View>
            </View>

            <View className="flex-row items-center bg-gray-50 rounded-xl p-4">
              <View className="bg-green-100 w-10 h-10 rounded-xl items-center justify-center mr-4">
                <Ionicons name="call" size={20} color="#10B981" />
              </View>
              <View className="flex-1">
                <Text className="text-gray-500 text-xs mb-1">Phone</Text>
                <Text className="text-gray-900 font-semibold">+1 (555) 123-4567</Text>
              </View>
            </View>

            <View className="flex-row items-center bg-gray-50 rounded-xl p-4">
              <View className="bg-purple-100 w-10 h-10 rounded-xl items-center justify-center mr-4">
                <Ionicons name="briefcase" size={20} color="#8B5CF6" />
              </View>
              <View className="flex-1">
                <Text className="text-gray-500 text-xs mb-1">Department</Text>
                <Text className="text-gray-900 font-semibold">Engineering</Text>
              </View>
            </View>

            <View className="flex-row items-center bg-gray-50 rounded-xl p-4">
              <View className="bg-yellow-100 w-10 h-10 rounded-xl items-center justify-center mr-4">
                <Ionicons name="location" size={20} color="#F59E0B" />
              </View>
              <View className="flex-1">
                <Text className="text-gray-500 text-xs mb-1">Location</Text>
                <Text className="text-gray-900 font-semibold">Main Building, Floor 3</Text>
              </View>
            </View>

            <View className="flex-row items-center bg-gray-50 rounded-xl p-4">
              <View className="bg-orange-100 w-10 h-10 rounded-xl items-center justify-center mr-4">
                <Ionicons name="calendar" size={20} color="#F97316" />
              </View>
              <View className="flex-1">
                <Text className="text-gray-500 text-xs mb-1">Joined Date</Text>
                <Text className="text-gray-900 font-semibold">January 15, 2024</Text>
              </View>
            </View>
          </View>
        </View>
      </View>

      {/* Settings Section */}
      <View className="px-6 mt-6">
        <Text className="text-gray-900 font-bold text-lg mb-4">Settings</Text>

        <View className="bg-white rounded-2xl overflow-hidden shadow-sm">
          <TouchableOpacity className="flex-row items-center p-4 border-b border-gray-100">
            <View className="bg-blue-50 w-10 h-10 rounded-xl items-center justify-center mr-4">
              <Ionicons name="notifications" size={20} color="#3B82F6" />
            </View>
            <View className="flex-1">
              <Text className="text-gray-900 font-semibold">Notifications</Text>
              <Text className="text-gray-500 text-xs">Manage your notifications</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
          </TouchableOpacity>

          <TouchableOpacity className="flex-row items-center p-4 border-b border-gray-100">
            <View className="bg-purple-50 w-10 h-10 rounded-xl items-center justify-center mr-4">
              <Ionicons name="shield-checkmark" size={20} color="#8B5CF6" />
            </View>
            <View className="flex-1">
              <Text className="text-gray-900 font-semibold">Privacy & Security</Text>
              <Text className="text-gray-500 text-xs">Manage your privacy settings</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
          </TouchableOpacity>

          <TouchableOpacity 
            className="flex-row items-center p-4"
            onPress={handleSignOut}
          >
            <View className="bg-red-50 w-10 h-10 rounded-xl items-center justify-center mr-4">
              <Ionicons name="log-out" size={20} color="#EF4444" />
            </View>
            <View className="flex-1">
              <Text className="text-danger font-semibold">Logout</Text>
              <Text className="text-gray-500 text-xs">Sign out of your account</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
          </TouchableOpacity>
        </View>
      </View>

      {/* App Info */}
      <View className="items-center py-8">
        <Text className="text-gray-400 text-sm">Smart Attendance System</Text>
        <Text className="text-gray-400 text-xs mt-1">Version 1.0.0</Text>
      </View>
    </ScrollView>
  )
}
