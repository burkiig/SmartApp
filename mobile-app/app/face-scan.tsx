import { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, Alert, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import * as ImagePicker from 'expo-image-picker'
import * as Location from 'expo-location'
import * as Device from 'expo-device'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'

export default function FaceScan() {
  const { profile } = useAuth()
  const [scanning, setScanning] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    // Simulate ready state after animation
    setTimeout(() => setReady(true), 500)
  }, [])

  const handleStartScan = async () => {
    if (scanning) return
    setScanning(true)

    try {
      // Request camera permission
      const { status } = await ImagePicker.requestCameraPermissionsAsync()
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Camera permission is required for face scanning')
        setScanning(false)
        return
      }

      // Launch camera
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.8,
        allowsEditing: false,
        cameraType: ImagePicker.CameraType.front,
      })

      if (result.canceled) {
        setScanning(false)
        return
      }

      // Get location
      const { status: locationStatus } = await Location.requestForegroundPermissionsAsync()
      let location = null
      if (locationStatus === 'granted') {
        location = await Location.getCurrentPositionAsync({})
      }

      // Upload photo
      const photo = result.assets[0]
      const ext = photo.uri.split('.').pop()
      const fileName = `${profile?.id}_${Date.now()}.${ext}`

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('verification-photos')
        .upload(fileName, {
          uri: photo.uri,
          type: `image/${ext}`,
          name: fileName,
        } as any)

      if (uploadError) throw uploadError

      const { data: { publicUrl } } = supabase.storage
        .from('verification-photos')
        .getPublicUrl(uploadData.path)

      // Call face verification (simplified - you'll need active session)
      // For now, just create a mock attendance record
      Alert.alert(
        'Success', 
        'Face scan completed! In production, this would verify against your reference photo.',
        [{ text: 'OK', onPress: () => router.back() }]
      )

    } catch (error: any) {
      Alert.alert('Error', error.message)
    } finally {
      setScanning(false)
    }
  }

  return (
    <View className="flex-1 bg-gradient-to-b from-secondary to-secondary-light">
      {/* Header */}
      <View className="pt-12 px-6 pb-6">
        <TouchableOpacity 
          onPress={() => router.back()}
          className="flex-row items-center mb-6"
        >
          <Ionicons name="arrow-back" size={24} color="white" />
          <Text className="text-white text-base font-semibold ml-2">Back</Text>
        </TouchableOpacity>

        <Text className="text-white text-3xl font-bold mb-2">Face ID Attendance</Text>
        <Text className="text-white/80 text-base">Position your face within the frame</Text>
      </View>

      {/* Main Content */}
      <View className="flex-1 items-center justify-center px-6">
        {/* Face Scan Frame */}
        <View className="relative items-center justify-center mb-8">
          {/* Outer Frame */}
          <View className="w-72 h-72 rounded-3xl border-4 border-white/30 items-center justify-center">
            {/* Inner Circle */}
            <View className="w-56 h-56 rounded-full bg-white/10 items-center justify-center">
              {/* Face Icon */}
              <View className={`${ready ? 'opacity-100' : 'opacity-50'} transition-opacity duration-300`}>
                <Ionicons name="scan" size={80} color="white" />
              </View>
            </View>
          </View>

          {/* Corner Brackets */}
          <View className="absolute top-0 left-0 w-16 h-16 border-l-4 border-t-4 border-secondary rounded-tl-3xl" />
          <View className="absolute top-0 right-0 w-16 h-16 border-r-4 border-t-4 border-secondary rounded-tr-3xl" />
          <View className="absolute bottom-0 left-0 w-16 h-16 border-l-4 border-b-4 border-secondary rounded-bl-3xl" />
          <View className="absolute bottom-0 right-0 w-16 h-16 border-r-4 border-b-4 border-secondary rounded-br-3xl" />
        </View>

        {/* Status Text */}
        <View className="bg-white/20 backdrop-blur-lg rounded-2xl px-6 py-4 mb-8">
          <Text className="text-white text-center text-lg font-semibold">
            {scanning ? 'Scanning...' : ready ? 'Ready to Scan' : 'Preparing...'}
          </Text>
          <Text className="text-white/70 text-center text-sm mt-1">
            {scanning ? 'Please wait' : 'Press the button below to start'}
          </Text>
        </View>

        {/* Scan Button */}
        <TouchableOpacity
          className={`bg-white rounded-2xl px-12 py-4 shadow-lg ${scanning ? 'opacity-60' : ''}`}
          onPress={handleStartScan}
          disabled={scanning || !ready}
        >
          {scanning ? (
            <ActivityIndicator color="#8B5CF6" size="small" />
          ) : (
            <Text className="text-secondary text-lg font-bold">Start Face Scan</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Instructions */}
      <View className="bg-white rounded-t-3xl px-6 py-6">
        <Text className="text-gray-900 font-bold text-lg mb-4">Instructions</Text>
        
        <View className="space-y-3">
          <View className="flex-row items-start">
            <View className="bg-secondary/10 w-6 h-6 rounded-full items-center justify-center mr-3 mt-0.5">
              <Text className="text-secondary font-bold text-sm">1</Text>
            </View>
            <Text className="flex-1 text-gray-700">
              Position your face in the center of the frame
            </Text>
          </View>

          <View className="flex-row items-start">
            <View className="bg-secondary/10 w-6 h-6 rounded-full items-center justify-center mr-3 mt-0.5">
              <Text className="text-secondary font-bold text-sm">2</Text>
            </View>
            <Text className="flex-1 text-gray-700">
              Ensure good lighting for better recognition
            </Text>
          </View>

          <View className="flex-row items-start">
            <View className="bg-secondary/10 w-6 h-6 rounded-full items-center justify-center mr-3 mt-0.5">
              <Text className="text-secondary font-bold text-sm">3</Text>
            </View>
            <Text className="flex-1 text-gray-700">
              Hold still during the scanning process
            </Text>
          </View>
        </View>
      </View>
    </View>
  )
}

