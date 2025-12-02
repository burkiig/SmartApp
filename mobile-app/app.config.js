module.exports = {
  expo: {
    name: 'Smart Attendance',
    slug: 'smart-attendance',
    version: '1.0.0',
    orientation: 'portrait',
    // icon: './assets/icon.png',  // Geçici olarak yorum satırı yapın
    userInterfaceStyle: 'light',
    jsEngine: 'hermes',
    splash: {
      // image: './assets/splash.png',  // Geçici olarak yorum satırı yapın
      resizeMode: 'contain',
      backgroundColor: '#ffffff'
    },
    assetBundlePatterns: [
      '**/*'
    ],
    ios: {
      supportsTablet: true,
      bundleIdentifier: 'com.smartattendance.app'
    },
    android: {
      adaptiveIcon: {
        // foregroundImage: './assets/adaptive-icon.png',  // Geçici olarak yorum satırı yapın
        backgroundColor: '#ffffff'
      },
      package: 'com.smartattendance.app',
      permissions: [
        'CAMERA',
        'ACCESS_FINE_LOCATION',
        'ACCESS_COARSE_LOCATION'
      ]
    },
    plugins: [
      'expo-router',
      [
        'expo-camera',
        {
          cameraPermission: 'Allow $(PRODUCT_NAME) to access your camera for attendance verification.'
        }
      ],
      [
        'expo-location',
        {
          locationAlwaysAndWhenInUsePermission: 'Allow $(PRODUCT_NAME) to use your location for attendance verification.'
        }
      ]
    ],
    scheme: 'smart-attendance',
    extra: {
      supabaseUrl: process.env.EXPO_PUBLIC_SUPABASE_URL,
      supabaseAnonKey: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY
    }
  }
}
