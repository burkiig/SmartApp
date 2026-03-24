export default {
  expo: {
    name: "Smart Attendance",
    slug: "smart-attendance",
    version: "1.0.0",
    orientation: "portrait",
    userInterfaceStyle: "light",
    scheme: "smartattendance",
    splash: {
      resizeMode: "contain",
      backgroundColor: "#5B7FFF"
    },
    assetBundlePatterns: [
      "**/*"
    ],
    ios: {
      supportsTablet: true,
      bundleIdentifier: "com.smartattendance.app",
      infoPlist: {
        NSLocationWhenInUseUsageDescription:
          "Yoklama doğrulaması için konum erişimi gereklidir.",
        NSLocationAlwaysAndWhenInUseUsageDescription:
          "Yoklama doğrulaması için konum erişimi gereklidir.",
        NSCameraUsageDescription:
          "Yüz tanıma ve QR kod okuma için kamera erişimi gereklidir."
      }
    },
    android: {
      package: "com.smartattendance.app",
      permissions: [
        "android.permission.CAMERA",
        "android.permission.RECORD_AUDIO",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION"
      ]
    },
    web: {},
    plugins: [
      [
        "expo-camera",
        {
          cameraPermission: "Yüz tanıma ve QR kod okuma için kamera erişimi gereklidir."
        }
      ],
      [
        "expo-location",
        {
          locationAlwaysAndWhenInUsePermission:
            "Yoklama doğrulaması için konum erişimi gereklidir."
        }
      ]
    ],
    extra: {
      API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:5000/api',
    }
  }
};
