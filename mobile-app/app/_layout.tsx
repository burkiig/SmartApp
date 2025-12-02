import 'react-native-gesture-handler'
import { Stack } from 'expo-router'
import { AuthProvider } from '@/contexts/AuthContext'
import { StatusBar } from 'expo-status-bar'
import { GestureHandlerRootView } from 'react-native-gesture-handler'

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <StatusBar style="auto" />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="login" />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen 
            name="face-scan" 
            options={{ 
              presentation: 'modal',
              animation: 'slide_from_bottom'
            }} 
          />
          <Stack.Screen 
            name="qr-scan" 
            options={{ 
              presentation: 'modal',
              animation: 'slide_from_bottom'
            }} 
          />
          <Stack.Screen 
            name="history" 
            options={{ 
              presentation: 'card',
              animation: 'slide_from_right'
            }} 
          />
        </Stack>
      </AuthProvider>
    </GestureHandlerRootView>
  )
}

