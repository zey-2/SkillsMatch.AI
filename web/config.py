"""
Configuration module for SkillsMatch.AI Flask application.

Provides configuration classes for different environments:
- DevelopmentConfig: Development environment with debug enabled
- ProductionConfig: Production environment
- TestingConfig: Testing environment with test database
"""

import os
from pathlib import Path
from datetime import timedelta


class Config:
    """Base configuration class with defaults."""

    # Application settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-in-production")

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # File uploads
    UPLOAD_FOLDER = Path(__file__).parent.parent / "uploads" / "resumes"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # API configuration
    API_JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # Cache configuration
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300

    # AI Service configuration
    AI_SERVICE_TIMEOUT = 30  # seconds
    VECTOR_SERVICE_ENABLED = True
    VECTOR_SERVICE_MODEL = "all-MiniLM-L6-v2"

    # Job matching configuration
    MATCH_SCORE_THRESHOLD = 0.3  # Minimum match score to show
    MAX_MATCHES_TO_RETURN = 50

    # Pagination
    ITEMS_PER_PAGE = 20

    # Environment detection
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return bool(
            os.environ.get("RENDER")
            or os.environ.get("RAILWAY")
            or os.environ.get("HEROKU")
            or os.environ.get("VERCEL")
        )

    @property
    def is_testing(self) -> bool:
        """Check if running tests."""
        return self.TESTING

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.DEBUG and not self.is_production


class DevelopmentConfig(Config):
    """Development configuration with debug mode enabled."""

    DEBUG = True
    TESTING = False

    # Development database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///skillsmatch_dev.db"
    )
    SQLALCHEMY_ECHO = True

    # Session configuration (less strict in development)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    # File uploads to local directory
    UPLOAD_FOLDER = Path(__file__).parent.parent / "uploads" / "resumes"

    # Development features
    PROPAGATE_EXCEPTIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True

    # Logging
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration with security hardened."""

    DEBUG = False
    TESTING = False

    # Production database (must be set via environment)
    # Default to SQLite if not set, but log warning
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///skillsmatch_prod.db"
    )

    # Security - strict settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year

    # Logging
    LOG_LEVEL = "WARNING"

    # Cache longer in production
    CACHE_DEFAULT_TIMEOUT = 3600  # 1 hour


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True

    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Less strict session security in testing
    SESSION_COOKIE_SECURE = False

    # Preserve context for error handling
    PRESERVE_CONTEXT_ON_EXCEPTION = True

    # Logging
    LOG_LEVEL = "DEBUG"


# Configuration factory
def get_config(environment: str = None) -> Config:
    """
    Get configuration class for the given environment.

    Args:
        environment: Environment name ('development', 'production', 'testing')
                    If None, auto-detect from environment variables

    Returns:
        Configuration class instance

    Examples:
        >>> config = get_config('development')
        >>> config.DEBUG
        True

        >>> config = get_config('production')
        >>> config.DEBUG
        False
    """
    if environment is None:
        # Auto-detect environment
        if os.environ.get("TESTING"):
            environment = "testing"
        elif (
            os.environ.get("RENDER")
            or os.environ.get("RAILWAY")
            or os.environ.get("HEROKU")
            or os.environ.get("VERCEL")
        ):
            environment = "production"
        else:
            environment = "development"

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = config_map.get(environment, DevelopmentConfig)
    config_instance = config_class()

    # Log warnings if needed
    if environment == "production" and not os.environ.get("DATABASE_URL"):
        import warnings

        warnings.warn(
            "⚠️  DATABASE_URL not set in production! Using SQLite fallback. "
            "For production, set DATABASE_URL environment variable.",
            RuntimeWarning,
        )

    return config_instance


# Default configuration
config = get_config()
