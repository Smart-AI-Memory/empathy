"""Configuration management for Empathy Memory Dashboard API.

Loads settings from environment variables with sensible defaults.
Supports development, staging, and production environments.
"""

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment Variables:
        API_TITLE: API title (default: Empathy Memory Dashboard API)
        API_VERSION: API version (default: 1.0.0)
        ENVIRONMENT: Deployment environment (development/staging/production)
        DEBUG: Enable debug mode (default: False in production)

        # CORS
        CORS_ORIGINS: Comma-separated allowed origins (default: localhost)
        CORS_CREDENTIALS: Allow credentials (default: True)

        # Redis
        REDIS_HOST: Redis host (default: localhost)
        REDIS_PORT: Redis port (default: 6379)
        REDIS_AUTO_START: Auto-start Redis if not running (default: True)

        # Memory Storage
        STORAGE_DIR: Long-term storage directory (default: ./memdocs_storage)
        AUDIT_DIR: Audit log directory (default: ./logs)
        ENCRYPTION_ENABLED: Enable pattern encryption (default: True)

        # Security
        JWT_SECRET_KEY: JWT signing key (required for auth)
        JWT_ALGORITHM: JWT algorithm (default: HS256)
        JWT_EXPIRATION_MINUTES: Token expiration (default: 1440 = 24 hours)
        AUTH_ENABLED: Enable JWT authentication (default: False)

        # WebSocket
        WS_HEARTBEAT_INTERVAL: WebSocket heartbeat interval in seconds (default: 30)
        METRICS_UPDATE_INTERVAL: Metrics update interval in seconds (default: 5)
    """

    # API Settings
    api_title: str = "Empathy Memory Dashboard API"
    api_version: str = "1.0.0"
    api_description: str = "REST API for managing Empathy Framework memory system"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # CORS Settings
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_auto_start: bool = True

    # Storage Settings
    storage_dir: str = "./memdocs_storage"
    audit_dir: str = "./logs"
    encryption_enabled: bool = True

    # Security Settings
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours
    auth_enabled: bool = False

    # WebSocket Settings
    ws_heartbeat_interval: int = 30
    metrics_update_interval: int = 5

    # API Rate Limiting (future)
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def model_post_init(self, __context) -> None:
        """Post-initialization validation and setup."""
        # Parse CORS origins from comma-separated string if needed
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            self.cors_origins = [origin.strip() for origin in cors_env.split(",")]

        # Disable debug in production
        if self.environment == "production":
            self.debug = False

        # Warn if using default JWT secret in production
        if (
            self.environment == "production"
            and self.jwt_secret_key == "dev-secret-key-change-in-production"
        ):
            import warnings

            warnings.warn(
                "Using default JWT secret key in production! Set JWT_SECRET_KEY environment variable.",
                UserWarning,
                stacklevel=2,
            )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses LRU cache to ensure settings are loaded only once.

    Returns:
        Settings instance with current configuration

    """
    return Settings()
