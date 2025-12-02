import { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, Alert, StyleSheet } from 'react-native'
import { CameraView, useCameraPermissions } from 'expo-camera'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import * as Location from 'expo-location'
import * as Device from 'expo-device'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'

export default function QRScan() {
  const { profile } = useAuth()
  const [permission, requestPermission] = useCameraPermissions()
  const [scanning, setScanning] = useState(false)
  const [processing, setProcessing] = useState(false)

  const handleQRScan = async ({ data }: { data: string }) => {
    if (processing) return
    setProcessing(true)

    try {
      // Parse QR code (session ID)
      const sessionId = data

      // Get session details
      const { data: session, error } = await supabase
        .from('attendance_sessions')
        .select('*')
        .eq('id', sessionId)
        .eq('is_active', true)
        .single()

      if (error || !session) {
        Alert.alert('Error', 'Invalid or expired QR code')
        setProcessing(false)
        return
      }

      // Verify GPS if required
      let gpsVerified = false
      let distance = null
      if (session.require_gps) {
        const { status } = await Location.requestForegroundPermissionsAsync()
        if (status === 'granted') {
          const location = await Location.getCurrentPositionAsync({})
          const dist = calculateDistance(
            location.coords.latitude,
            location.coords.longitude,
            session.location_lat,
            session.location_lng
          )
          distance = dist
          gpsVerified = dist <= session.location_radius
        }
      }

      // Get device UUID
      const deviceUuid = Device.modelId || 'unknown'

      // Create attendance record
      const { error: insertError } = await supabase
        .from('attendance_records')
        .insert({
          session_id: sessionId,
          student_id: profile?.id,
          status: 'present',
          qr_verified: true,
          gps_verified,
          device_verified: session.require_device_check,
          distance_from_class: distance,
          device_uuid: deviceUuid,
        })

      if (insertError) {
        Alert.alert('Error', insertError.message)
      } else {
        Alert.alert(
          'Success', 
          'Attendance marked successfully!',
          [{ text: 'OK', onPress: () => router.back() }]
        )
      }
    } catch (error: any) {
      Alert.alert('Error', error.message)
    } finally {
      setProcessing(false)
    }
  }

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371e3 // Earth radius in meters
    const φ1 = lat1 * Math.PI / 180
    const φ2 = lat2 * Math.PI / 180
    const Δφ = (lat2 - lat1) * Math.PI / 180
    const Δλ = (lon2 - lon1) * Math.PI / 180

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

    return R * c // Distance in meters
  }

  if (!permission) {
    return (
      <View className="flex-1 bg-background items-center justify-center">
        <Text className="text-gray-600">Requesting camera permission...</Text>
      </View>
    )
  }

  if (!permission.granted) {
    return (
      <View className="flex-1 bg-background">
        <View className="pt-12 px-6 pb-6">
          <TouchableOpacity 
            onPress={() => router.back()}
            className="flex-row items-center mb-6"
          >
            <Ionicons name="arrow-back" size={24} color="#4F46E5" />
            <Text className="text-primary text-base font-semibold ml-2">Back</Text>
          </TouchableOpacity>
        </View>

        <View className="flex-1 items-center justify-center px-6">
          <View className="bg-primary/10 w-20 h-20 rounded-full items-center justify-center mb-6">
            <Ionicons name="camera" size={40} color="#4F46E5" />
          </View>
          <Text className="text-gray-900 text-xl font-bold mb-2 text-center">Camera Permission Required</Text>
          <Text className="text-gray-600 text-center mb-8">
            We need access to your camera to scan QR codes
          </Text>
          <TouchableOpacity
            className="bg-primary px-8 py-4 rounded-xl"
            onPress={requestPermission}
          >
            <Text className="text-white font-bold">Grant Permission</Text>
          </TouchableOpacity>
        </View>
      </View>
    )
  }

  return (
    <View className="flex-1 bg-gradient-to-b from-blue-500 to-blue-300">
      {/* Header */}
      <View className="pt-12 px-6 pb-6 z-10">
        <TouchableOpacity 
          onPress={() => router.back()}
          className="flex-row items-center mb-6"
        >
          <Ionicons name="arrow-back" size={24} color="white" />
          <Text className="text-white text-base font-semibold ml-2">Back</Text>
        </TouchableOpacity>

        <Text className="text-white text-3xl font-bold mb-2">QR Code Scanner</Text>
        <Text className="text-white/80 text-base">Scan the QR code to mark attendance</Text>
      </View>

      {/* Camera View */}
      <View className="flex-1 items-center justify-center px-6">
        <View className="relative w-full max-w-sm aspect-square">
          {/* Camera */}
          <View className="absolute inset-0 rounded-3xl overflow-hidden bg-gray-900">
            <CameraView
              style={StyleSheet.absoluteFillObject}
              facing="back"
              barcodeScannerSettings={{
                barcodeTypes: ['qr'],
              }}
              onBarcodeScanned={processing ? undefined : handleQRScan}
            />
          </View>

          {/* Scanning Frame Overlay */}
          <View className="absolute inset-0 items-center justify-center">
            {/* Corner Brackets */}
            <View className="w-64 h-64 relative">
              <View className="absolute top-0 left-0 w-16 h-16 border-l-4 border-t-4 border-white rounded-tl-2xl" />
              <View className="absolute top-0 right-0 w-16 h-16 border-r-4 border-t-4 border-white rounded-tr-2xl" />
              <View className="absolute bottom-0 left-0 w-16 h-16 border-l-4 border-b-4 border-white rounded-bl-2xl" />
              <View className="absolute bottom-0 right-0 w-16 h-16 border-r-4 border-b-4 border-white rounded-br-2xl" />
              
              {/* QR Icon in center */}
              <View className="absolute inset-0 items-center justify-center">
                <View className="bg-white/20 backdrop-blur-sm p-4 rounded-2xl">
                  <Ionicons name="qr-code" size={48} color="white" />
                </View>
              </View>
            </View>
          </View>

          {/* Camera Active Indicator */}
          <View className="absolute top-4 right-4 bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-full flex-row items-center">
            <View className="w-2 h-2 bg-green-400 rounded-full mr-2" />
            <Text className="text-white text-xs font-semibold">Camera Active</Text>
          </View>
        </View>

        {/* Status Text */}
        <View className="mt-8 bg-white/20 backdrop-blur-lg rounded-2xl px-6 py-4">
          <Text className="text-white text-center text-lg font-semibold">
            {processing ? 'Processing...' : 'Ready to Scan'}
          </Text>
          <Text className="text-white/70 text-center text-sm mt-1">
            {processing ? 'Please wait' : 'Position QR code within the frame'}
          </Text>
        </View>
      </View>

      {/* Instructions */}
      <View className="bg-white rounded-t-3xl px-6 py-6">
        <Text className="text-gray-900 font-bold text-lg mb-4">How to Scan</Text>
        
        <View className="space-y-3">
          <View className="flex-row items-start">
            <View className="bg-blue-100 w-6 h-6 rounded-full items-center justify-center mr-3 mt-0.5">
              <Text className="text-blue-600 font-bold text-sm">1</Text>
            </View>
            <Text className="flex-1 text-gray-700">
              Allow camera access when prompted
            </Text>
          </View>

          <View className="flex-row items-start">
            <View className="bg-blue-100 w-6 h-6 rounded-full items-center justify-center mr-3 mt-0.5">
              <Text className="text-blue-600 font-bold text-sm">2</Text>
            </View>
            <Text className="flex-1 text-gray-700">
              Position the QR code within the scanning frame
            </Text>
          </View>

          <View className="flex-row items-start">
            <View className="bg-blue-100 w-6 h-6 rounded-full items-center justify-center mr-3 mt-0.5">
              <Text className="text-blue-600 font-bold text-sm">3</Text>
            </View>
            <Text className="flex-1 text-gray-700">
              Hold steady until the scan completes
            </Text>
          </View>
        </View>
      </View>
    </View>
  )
}

