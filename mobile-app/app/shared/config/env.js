import Constants from 'expo-constants';

/**
 * Environment configuration for mobile app
 * Manages API URLs and environment-specific settings
 */

const ENV = {
    development: {
        // Geliştirme ortamı için API URL'sini ayarlayın:
        //
        // SECENEK 1 — Yerel geliştirme (Android emülatör veya aynı makine):
        //   API_URL: 'http://10.0.2.2:5000'   // Android emülatör
        //   API_URL: 'http://localhost:5000'   // iOS simülatör
        //
        // SECENEK 2 — Yerel IP (aynı WiFi ağındaysanız):
        //   ipconfig komutuyla IPv4 adresinizi bulun, buraya yazın.
        //   API_URL: 'http://192.168.x.x:5000'
        //
        // SECENEK 3 — ngrok (önerilen, IP değişse de çalışır):
        //   ngrok http 5000 → http://localhost:4040 → HTTPS URL'yi kopyalayın.
        //   API_URL: 'https://xxxx-xxxx.ngrok-free.app'
        //
        // UYARI: Gerçek URL'leri bu dosyaya yazmayın — .env.local kullanın.
        API_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5000',
        ENABLE_DEVTOOLS: true,
        LOG_LEVEL: 'debug'
    },
    production: {
        API_URL: 'https://api.smartattendance.com',
        ENABLE_DEVTOOLS: false,
        LOG_LEVEL: 'error'
    }
};

const getEnvVars = () => {
    if (__DEV__) {
        return ENV.development;
    }
    return ENV.production;
};

export const config = getEnvVars();
export const API_URL = config.API_URL;
export const ENABLE_DEVTOOLS = config.ENABLE_DEVTOOLS;
export const LOG_LEVEL = config.LOG_LEVEL;
