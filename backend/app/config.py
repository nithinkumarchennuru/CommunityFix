import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

# Automatically load .env from backend directory or project root
backend_dir = Path(__file__).resolve().parent.parent
dotenv_path = backend_dir / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()


class Config:
    """Base configuration with shared defaults and environment parsing."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key-communityfix")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")

    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "communityfix_db")

    # Safely URL-encode the password to support special characters
    _encoded_password = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    _auth_segment = f"{DB_USER}:{_encoded_password}" if _encoded_password else DB_USER

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{_auth_segment}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # CORS configuration
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    TESTING = True
    DB_NAME = os.getenv("TEST_DB_NAME", "communityfix_test_db")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{Config.DB_USER}:{urllib.parse.quote_plus(Config.DB_PASSWORD)}@"
        f"{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}?charset=utf8mb4"
        if Config.DB_PASSWORD else
        f"mysql+pymysql://{Config.DB_USER}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
