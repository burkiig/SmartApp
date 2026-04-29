"""
Flask application configuration.
Never instantiate Config directly — use create_app(config_class=...).
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Environment ────────────────────────────────────────────────────────────
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # 'development' | 'production'

    # ── Secrets ────────────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ── Database ───────────────────────────────────────────────────────────────
    #   Supported drivers: 'json' | 'sqlite' | 'mongodb'
    DB_DRIVER = os.getenv("DB_DRIVER", "json")

    # JSON adapter
    JSON_BASE_DIR = os.getenv("JSON_BASE_DIR", "static")

    # SQLite adapter
    SQLITE_PATH = os.getenv("SQLITE_PATH", "smart_attendance.db")

    # MongoDB adapter
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "smart_attendance")

    # PostgreSQL adapter
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "smart_attendance")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))

    # ── Face Recognition ───────────────────────────────────────────────────────
    FACE_RECOGNITION_TOLERANCE = float(os.getenv("FACE_RECOGNITION_TOLERANCE", "0.65"))
    FACE_DETECTION_MODEL = os.getenv("FACE_DETECTION_MODEL", "hog")  # 'hog' | 'cnn'
    FACE_FLAGGED_DISTANCE_MIN = float(os.getenv("FACE_FLAGGED_DISTANCE_MIN", "0.50"))
    FACE_FLAGGED_DISTANCE_MAX = float(os.getenv("FACE_FLAGGED_DISTANCE_MAX", "0.65"))

    # ── Geofence ───────────────────────────────────────────────────────────────
    DEFAULT_GEOFENCE_RADIUS_M = int(os.getenv("DEFAULT_GEOFENCE_RADIUS_M", "40"))

    # ── Attendance Engine ──────────────────────────────────────────────────────
    ATTENDANCE_STEP_TIMEOUT_SECONDS = int(os.getenv("ATTENDANCE_STEP_TIMEOUT_SECONDS", "120"))

    # ── CORS ───────────────────────────────────────────────────────────────────
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")

    # ── Server ─────────────────────────────────────────────────────────────────
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "") or None

    # ── Expo Push Notifications ────────────────────────────────────────────────
    EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

    @classmethod
    def validate_production(cls):
        """
        Call this inside create_app() to enforce production-only constraints.
        Raises ValueError if any critical setting is missing or insecure.
        """
        if cls.ENVIRONMENT != "production":
            return

        errors = []
        if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-secret-key-change-in-production":
            errors.append("SECRET_KEY must be set to a strong random value in production.")
        if cls.SECRET_KEY and len(cls.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters long.")
        if cls.DEBUG:
            errors.append("DEBUG must be False in production.")

        if errors:
            raise ValueError("Production configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


class DevelopmentConfig(Config):
    DEBUG = True
    ENVIRONMENT = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENVIRONMENT = "production"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENVIRONMENT = "testing"
    DB_DRIVER = "json"
    JSON_BASE_DIR = "tests/fixtures"
    SECRET_KEY = "test-secret-key-at-least-32-chars-long"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
