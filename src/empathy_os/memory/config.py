"""Redis Configuration for Empathy Framework

Handles connection to Redis from environment variables.
Supports Railway, redis.com, local Docker, or mock mode.

Environment Variables:
    REDIS_URL: Full Redis URL (redis://user:pass@host:port)  # pragma: allowlist secret
    REDIS_HOST: Redis host (default: localhost)
    REDIS_PORT: Redis port (default: 6379)
    REDIS_PASSWORD: Redis password (optional)
    REDIS_DB: Redis database number (default: 0)
    EMPATHY_REDIS_MOCK: Set to "true" to use mock mode

Railway Auto-Detection:
    When deployed on Railway, REDIS_URL is automatically set.

Usage:
    from empathy_os.redis_config import get_redis_memory

    # Automatically uses environment variables
    memory = get_redis_memory()

    # Or with explicit URL
    memory = get_redis_memory(url="redis://localhost:6379")

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
from urllib.parse import urlparse

from .short_term import RedisShortTermMemory


def parse_redis_url(url: str) -> dict:
    """Parse Redis URL into connection parameters.

    Args:
        url: Redis URL (redis://user:pass@host:port/db)  # pragma: allowlist secret

    Returns:
        Dict with host, port, password, db

    """
    parsed = urlparse(url)

    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "password": parsed.password,
        "db": int(parsed.path.lstrip("/") or 0) if parsed.path else 0,
    }


def get_redis_config() -> dict:
    """Get Redis configuration from environment variables.

    Priority:
    1. REDIS_URL (full URL, used by Railway)
    2. Individual env vars (REDIS_HOST, REDIS_PORT, etc.)
    3. Defaults (localhost:6379)

    Returns:
        Dict with connection parameters or {"use_mock": True}

    """
    # Check for mock mode
    if os.getenv("EMPATHY_REDIS_MOCK", "").lower() == "true":
        return {"use_mock": True}

    # Check for full URL (Railway, Heroku, etc.)
    # Priority: REDIS_URL > REDIS_PUBLIC_URL > REDIS_PRIVATE_URL
    redis_url = (
        os.getenv("REDIS_URL") or os.getenv("REDIS_PUBLIC_URL") or os.getenv("REDIS_PRIVATE_URL")
    )
    if redis_url:
        config = parse_redis_url(redis_url)
        config["use_mock"] = False
        return config

    # Fall back to individual env vars
    return {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "password": os.getenv("REDIS_PASSWORD"),
        "db": int(os.getenv("REDIS_DB", "0")),
        "use_mock": False,
    }


def get_redis_memory(
    url: str | None = None,
    use_mock: bool | None = None,
) -> RedisShortTermMemory:
    """Create a RedisShortTermMemory instance with environment-based config.

    Args:
        url: Optional explicit Redis URL (overrides env vars)
        use_mock: Optional explicit mock mode (overrides env vars)

    Returns:
        Configured RedisShortTermMemory instance

    Examples:
        # Auto-configure from environment
        memory = get_redis_memory()

        # Explicit URL
        memory = get_redis_memory(url="redis://localhost:6379")

        # Force mock mode
        memory = get_redis_memory(use_mock=True)

    """
    # Explicit mock mode
    if use_mock is True:
        return RedisShortTermMemory(use_mock=True)

    # Explicit URL
    if url:
        config = parse_redis_url(url)
        return RedisShortTermMemory(
            host=config["host"],
            port=config["port"],
            password=config["password"],
            db=config["db"],
            use_mock=False,
        )

    # Environment-based config
    config = get_redis_config()

    if config.get("use_mock"):
        return RedisShortTermMemory(use_mock=True)

    return RedisShortTermMemory(
        host=config["host"],
        port=config["port"],
        password=config.get("password"),
        db=config.get("db", 0),
        use_mock=False,
    )


def check_redis_connection() -> dict:
    """Check Redis connection and return status.

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
        "use_mock": config.get("use_mock", False),
        "host": config.get("host"),
        "port": config.get("port"),
        "has_password": bool(config.get("password")),
        "db": config.get("db", 0),
        "connected": False,
        "error": None,
    }

    # Determine config source
    if os.getenv("REDIS_URL"):
        result["config_source"] = "REDIS_URL"
    elif os.getenv("REDIS_PUBLIC_URL"):
        result["config_source"] = "REDIS_PUBLIC_URL (Railway)"
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
    """Get Redis configured for Railway deployment.

    Railway automatically sets REDIS_URL when you add a Redis service.
    For external access (like from VSCode extension), use REDIS_PUBLIC_URL.

    Returns:
        RedisShortTermMemory configured for Railway

    Raises:
        EnvironmentError: If no Redis URL is set

    """
    redis_url = (
        os.getenv("REDIS_URL") or os.getenv("REDIS_PUBLIC_URL") or os.getenv("REDIS_PRIVATE_URL")
    )

    if not redis_url:
        raise OSError(
            "REDIS_URL not found. Make sure Redis is added to your Railway project.\n"
            "Run: railway add --database redis\n"
            "For external access, use REDIS_PUBLIC_URL",
        )

    return get_redis_memory(url=redis_url)
