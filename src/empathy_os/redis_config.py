"""
Redis Configuration for Empathy Framework

Handles connection to Redis from environment variables.
Supports Railway, redis.com, local Docker, managed Redis, or mock mode.

Environment Variables:
    REDIS_URL: Full Redis URL (redis://user:pass@host:port)
    REDIS_HOST: Redis host (default: localhost)
    REDIS_PORT: Redis port (default: 6379)
    REDIS_PASSWORD: Redis password (optional)
    REDIS_DB: Redis database number (default: 0)
    EMPATHY_REDIS_MOCK: Set to "true" to use mock mode

    # SSL/TLS (for managed Redis services)
    REDIS_SSL: Set to "true" to enable SSL
    REDIS_SSL_CERT_REQS: Certificate requirement ("required", "optional", "none")
    REDIS_SSL_CA_CERTS: Path to CA certificate file
    REDIS_SSL_CERTFILE: Path to client certificate
    REDIS_SSL_KEYFILE: Path to client key

    # Connection settings
    REDIS_SOCKET_TIMEOUT: Socket timeout in seconds (default: 5.0)
    REDIS_MAX_CONNECTIONS: Connection pool size (default: 10)

    # Retry settings
    REDIS_RETRY_MAX_ATTEMPTS: Max retry attempts (default: 3)
    REDIS_RETRY_BASE_DELAY: Base retry delay in seconds (default: 0.1)
    REDIS_RETRY_MAX_DELAY: Max retry delay in seconds (default: 2.0)

    # Sentinel (for high availability)
    REDIS_SENTINEL_HOSTS: Comma-separated host:port pairs
    REDIS_SENTINEL_MASTER: Sentinel master name

Railway Auto-Detection:
    When deployed on Railway, REDIS_URL is automatically set.
    For Railway Redis with SSL, the URL starts with "rediss://"

Usage:
    from empathy_os.redis_config import get_redis_memory

    # Automatically uses environment variables
    memory = get_redis_memory()

    # Or with explicit URL (SSL auto-detected from rediss://)
    memory = get_redis_memory(url="rediss://user:pass@managed-redis.com:6379")

    # Or with explicit config
    from empathy_os.memory.short_term import RedisConfig
    config = RedisConfig(host="localhost", ssl=True)
    memory = get_redis_memory(config=config)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
from urllib.parse import urlparse

from .memory.short_term import RedisConfig, RedisShortTermMemory


def parse_redis_url(url: str) -> dict:
    """
    Parse Redis URL into connection parameters.

    Supports:
    - redis://user:pass@host:port/db (standard)
    - rediss://user:pass@host:port/db (SSL enabled)

    Args:
        url: Redis URL (redis:// or rediss://)

    Returns:
        Dict with host, port, password, db, ssl
    """
    parsed = urlparse(url)

    # Detect SSL from scheme
    ssl = parsed.scheme == "rediss"

    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "password": parsed.password,
        "db": int(parsed.path.lstrip("/") or 0) if parsed.path else 0,
        "ssl": ssl,
    }


def get_redis_config() -> RedisConfig:
    """
    Get Redis configuration from environment variables.

    Priority:
    1. REDIS_URL (full URL, used by Railway/Heroku/managed services)
    2. Individual env vars (REDIS_HOST, REDIS_PORT, etc.)
    3. Defaults (localhost:6379)

    Returns:
        RedisConfig with all connection parameters
    """
    # Check for mock mode
    if os.getenv("EMPATHY_REDIS_MOCK", "").lower() == "true":
        return RedisConfig(use_mock=True)

    # Check for full URL (Railway, Heroku, managed services)
    redis_url = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")
    if redis_url:
        url_config = parse_redis_url(redis_url)
        return RedisConfig(
            host=url_config["host"],
            port=url_config["port"],
            password=url_config["password"],
            db=url_config["db"],
            ssl=url_config.get("ssl", False),
            use_mock=False,
            # Apply additional env var overrides
            socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            retry_max_attempts=int(os.getenv("REDIS_RETRY_MAX_ATTEMPTS", "3")),
            retry_base_delay=float(os.getenv("REDIS_RETRY_BASE_DELAY", "0.1")),
            retry_max_delay=float(os.getenv("REDIS_RETRY_MAX_DELAY", "2.0")),
        )

    # Build config from individual env vars
    return RedisConfig(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD"),
        db=int(os.getenv("REDIS_DB", "0")),
        use_mock=False,
        # SSL settings
        ssl=os.getenv("REDIS_SSL", "").lower() == "true",
        ssl_cert_reqs=os.getenv("REDIS_SSL_CERT_REQS"),
        ssl_ca_certs=os.getenv("REDIS_SSL_CA_CERTS"),
        ssl_certfile=os.getenv("REDIS_SSL_CERTFILE"),
        ssl_keyfile=os.getenv("REDIS_SSL_KEYFILE"),
        # Connection settings
        socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")),
        socket_connect_timeout=float(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5.0")),
        max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
        # Retry settings
        retry_on_timeout=os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true",
        retry_max_attempts=int(os.getenv("REDIS_RETRY_MAX_ATTEMPTS", "3")),
        retry_base_delay=float(os.getenv("REDIS_RETRY_BASE_DELAY", "0.1")),
        retry_max_delay=float(os.getenv("REDIS_RETRY_MAX_DELAY", "2.0")),
    )


def get_redis_config_dict() -> dict:
    """
    Get Redis configuration as a dictionary (legacy compatibility).

    Returns:
        Dict with connection parameters
    """
    config = get_redis_config()
    return {
        "host": config.host,
        "port": config.port,
        "password": config.password,
        "db": config.db,
        "use_mock": config.use_mock,
        "ssl": config.ssl,
    }


def get_redis_memory(
    url: str | None = None,
    use_mock: bool | None = None,
    config: RedisConfig | None = None,
) -> RedisShortTermMemory:
    """
    Create a RedisShortTermMemory instance with environment-based config.

    Args:
        url: Optional explicit Redis URL (overrides env vars)
        use_mock: Optional explicit mock mode (overrides env vars)
        config: Optional explicit RedisConfig (overrides all other options)

    Returns:
        Configured RedisShortTermMemory instance

    Examples:
        # Auto-configure from environment
        memory = get_redis_memory()

        # Explicit URL (SSL auto-detected from rediss://)
        memory = get_redis_memory(url="rediss://user:pass@managed-redis.com:6379")

        # Force mock mode
        memory = get_redis_memory(use_mock=True)

        # Explicit config with all options
        from empathy_os.memory.short_term import RedisConfig
        config = RedisConfig(
            host="redis.example.com",
            port=6379,
            ssl=True,
            retry_max_attempts=5,
        )
        memory = get_redis_memory(config=config)
    """
    # Explicit config takes highest priority
    if config is not None:
        return RedisShortTermMemory(config=config)

    # Explicit mock mode
    if use_mock is True:
        return RedisShortTermMemory(use_mock=True)

    # Explicit URL
    if url:
        url_config = parse_redis_url(url)
        redis_config = RedisConfig(
            host=url_config["host"],
            port=url_config["port"],
            password=url_config["password"],
            db=url_config["db"],
            ssl=url_config.get("ssl", False),
            use_mock=False,
        )
        return RedisShortTermMemory(config=redis_config)

    # Environment-based config
    env_config = get_redis_config()
    return RedisShortTermMemory(config=env_config)


def check_redis_connection() -> dict:
    """
    Check Redis connection and return status.

    Returns:
        Dict with connection status and info

    Example:
        >>> status = check_redis_connection()
        >>> if status["connected"]:
        ...     print(f"Connected to {status['host']}:{status['port']}")
    """
    config = get_redis_config()

    result = {
        "config_source": "environment",
        "use_mock": config.use_mock,
        "host": config.host,
        "port": config.port,
        "has_password": bool(config.password),
        "db": config.db,
        "connected": False,
        "error": None,
    }

    # Determine config source
    if os.getenv("REDIS_URL"):
        result["config_source"] = "REDIS_URL"
    elif os.getenv("REDIS_PRIVATE_URL"):
        result["config_source"] = "REDIS_PRIVATE_URL"
    elif os.getenv("REDIS_HOST"):
        result["config_source"] = "REDIS_HOST"

    if result["use_mock"]:
        result["connected"] = True
        result["config_source"] = "mock_mode"
        return result

    try:
        memory = get_redis_memory()
        result["connected"] = memory.ping()
        if result["connected"]:
            stats = memory.get_stats()
            result["memory_used"] = stats.get("used_memory")
            result["total_keys"] = stats.get("total_keys")
    except Exception as e:
        result["error"] = str(e)

    return result


# Convenience function for Railway deployments
def get_railway_redis() -> RedisShortTermMemory:
    """
    Get Redis configured for Railway deployment.

    Railway automatically sets REDIS_URL when you add a Redis service.

    Returns:
        RedisShortTermMemory configured for Railway

    Raises:
        EnvironmentError: If REDIS_URL is not set
    """
    redis_url = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")

    if not redis_url:
        raise OSError(
            "REDIS_URL not found. Make sure Redis is added to your Railway project.\n"
            "Run: railway add --database redis"
        )

    return get_redis_memory(url=redis_url)
