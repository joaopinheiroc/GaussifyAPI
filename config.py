"""
Configuration management for the application.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-do-not-use-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JSON configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    @classmethod
    def init_app(cls, _app):
        """Initialize application with this config."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///instance/gaussify.db"
    )
    SQLALCHEMY_ECHO = False  # Set to True to log SQL queries


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    @classmethod
    def init_app(cls, app):
        """Initialize production app."""
        Config.init_app(app)

        # Ensure SECRET_KEY is set in production
        if not os.getenv("SECRET_KEY"):
            raise ValueError("SECRET_KEY environment variable must be set in production")


config_by_name: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
