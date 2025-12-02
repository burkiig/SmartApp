import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from 'react-native'
import { router } from 'expo-router'
import { useAuth } from '@/contexts/AuthContext'
import { Ionicons } from '@expo/vector-icons'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [userType, setUserType] = useState<'student' | 'instructor'>('student')
  const [rememberMe, setRememberMe] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const { signIn } = useAuth()

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Hata', 'Lütfen email ve şifre girin')
      return
    }

    setLoading(true)
    try {
      await signIn(email, password)
      router.replace('/(tabs)/home')
    } catch (error: any) {
      Alert.alert('Giriş Başarısız', error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-background"
    >
      <ScrollView 
        contentContainerStyle={{ flexGrow: 1 }}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-1 justify-center px-6 py-12">
          {/* Logo and Header */}
          <View className="items-center mb-8">
            <View className="w-20 h-20 bg-primary rounded-3xl items-center justify-center mb-6 shadow-lg">
              <Ionicons name="school" size={40} color="white" />
            </View>
            <Text className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</Text>
            <Text className="text-base text-primary font-medium">Sign in to mark your attendance</Text>
          </View>

          {/* Login Form Card */}
          <View className="bg-white rounded-3xl p-6 shadow-lg">
            {/* User Type Toggle */}
            <Text className="text-sm text-gray-600 mb-3">I am a</Text>
            <View className="flex-row mb-6 bg-gray-100 rounded-xl p-1">
              <TouchableOpacity
                className={`flex-1 py-3 rounded-lg ${userType === 'student' ? 'bg-primary' : 'bg-transparent'}`}
                onPress={() => setUserType('student')}
              >
                <View className="flex-row items-center justify-center">
                  <Ionicons 
                    name="person" 
                    size={18} 
                    color={userType === 'student' ? 'white' : '#6B7280'} 
                  />
                  <Text className={`ml-2 font-semibold ${userType === 'student' ? 'text-white' : 'text-gray-500'}`}>
                    Student
                  </Text>
                </View>
              </TouchableOpacity>
              
              <TouchableOpacity
                className={`flex-1 py-3 rounded-lg ${userType === 'instructor' ? 'bg-primary' : 'bg-transparent'}`}
                onPress={() => setUserType('instructor')}
              >
                <View className="flex-row items-center justify-center">
                  <Ionicons 
                    name="briefcase" 
                    size={18} 
                    color={userType === 'instructor' ? 'white' : '#6B7280'} 
                  />
                  <Text className={`ml-2 font-semibold ${userType === 'instructor' ? 'text-white' : 'text-gray-500'}`}>
                    Instructor
                  </Text>
                </View>
              </TouchableOpacity>
            </View>

            {/* Email Input */}
            <Text className="text-sm font-medium text-gray-700 mb-2">School Email</Text>
            <View className="flex-row items-center bg-gray-50 rounded-xl px-4 mb-4 border border-gray-200">
              <Ionicons name="mail-outline" size={20} color="#9CA3AF" />
              <TextInput
                className="flex-1 py-3.5 px-3 text-base text-gray-900"
                placeholder="student@school.edu"
                placeholderTextColor="#9CA3AF"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
              />
            </View>

            {/* Password Input */}
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-sm font-medium text-gray-700">Password</Text>
              <TouchableOpacity>
                <Text className="text-sm text-primary font-medium">Forgot?</Text>
              </TouchableOpacity>
            </View>
            <View className="flex-row items-center bg-gray-50 rounded-xl px-4 mb-4 border border-gray-200">
              <Ionicons name="lock-closed-outline" size={20} color="#9CA3AF" />
              <TextInput
                className="flex-1 py-3.5 px-3 text-base text-gray-900"
                placeholder="Enter your password"
                placeholderTextColor="#9CA3AF"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoComplete="password"
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <Ionicons 
                  name={showPassword ? "eye-off-outline" : "eye-outline"} 
                  size={20} 
                  color="#9CA3AF" 
                />
              </TouchableOpacity>
            </View>

            {/* Remember Me */}
            <TouchableOpacity 
              className="flex-row items-center mb-6"
              onPress={() => setRememberMe(!rememberMe)}
            >
              <View className={`w-5 h-5 rounded border-2 mr-2 items-center justify-center ${rememberMe ? 'bg-primary border-primary' : 'border-gray-300'}`}>
                {rememberMe && <Ionicons name="checkmark" size={14} color="white" />}
              </View>
              <Text className="text-sm text-gray-700">Remember me</Text>
            </TouchableOpacity>

            {/* Sign In Button */}
            <TouchableOpacity
              className={`bg-primary py-4 rounded-xl items-center ${loading ? 'opacity-60' : ''}`}
              onPress={handleLogin}
              disabled={loading}
            >
              <Text className="text-white text-base font-bold">
                {loading ? 'Signing in...' : 'Sign In'}
              </Text>
            </TouchableOpacity>

            {/* Social Login Divider */}
            <View className="flex-row items-center my-6">
              <View className="flex-1 h-px bg-gray-200" />
              <Text className="text-sm text-gray-500 mx-4">Or continue with</Text>
              <View className="flex-1 h-px bg-gray-200" />
            </View>

            {/* Social Login Buttons */}
            <View className="flex-row space-x-3">
              <TouchableOpacity className="flex-1 flex-row items-center justify-center py-3 border border-gray-200 rounded-xl">
                <Ionicons name="logo-google" size={20} color="#DB4437" />
                <Text className="ml-2 text-gray-700 font-medium">Google</Text>
              </TouchableOpacity>
              
              <TouchableOpacity className="flex-1 flex-row items-center justify-center py-3 border border-gray-200 rounded-xl">
                <Ionicons name="logo-facebook" size={20} color="#1877F2" />
                <Text className="ml-2 text-gray-700 font-medium">Facebook</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Sign Up Link */}
          <View className="flex-row justify-center mt-6">
            <Text className="text-gray-600">Don't have an account? </Text>
            <TouchableOpacity>
              <Text className="text-primary font-semibold">Sign up</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

