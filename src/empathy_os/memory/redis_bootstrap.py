"""Redis Bootstrap for Empathy Framework

Automatically starts Redis if not running, with graceful fallback.
Supports:
  - macOS: Homebrew
  - Linux: systemd, direct
  - Windows: Windows Service, Chocolatey, Scoop, WSL, direct
  - All platforms: Docker

Usage:
    from empathy_os.memory.redis_bootstrap import ensure_redis

    # Returns True if Redis is available (started or already running)
    redis_available = ensure_redis()

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import platform
import shutil
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)

# Detect platform
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


class RedisStartMethod(Enum):
    """Methods for starting Redis, in order of preference."""

    ALREADY_RUNNING = "already_running"
    HOMEBREW = "homebrew"
    SYSTEMD = "systemd"
    WINDOWS_SERVICE = "windows_service"
    CHOCOLATEY = "chocolatey"
    SCOOP = "scoop"
    WSL = "wsl"
    DOCKER = "docker"
    DIRECT = "direct"
    MOCK = "mock"


@dataclass
class RedisStatus:
    """Status of Redis connection/startup."""

    available: bool
    method: RedisStartMethod
    host: str = "localhost"
    port: int = 6379
    message: str = ""
    pid: int | None = None


def _check_redis_running(host: str = "localhost", port: int = 6379) -> bool:
    """Check if Redis is responding to ping."""
    try:
        import redis

        client = redis.Redis(host=host, port=port, socket_connect_timeout=1)
        return client.ping()
    except Exception:
        return False


def _find_command(cmd: str) -> str | None:
    """Find command in PATH."""
    return shutil.which(cmd)


def _run_silent(cmd: list[str], timeout: int = 5) -> tuple[bool, str]:
    """Run command silently, return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def _start_via_homebrew() -> bool:
    """Try to start Redis via Homebrew (macOS)."""
    if not _find_command("brew"):
        return False

    # Check if redis is installed
    success, output = _run_silent(["brew", "list", "redis"])
    if not success:
        logger.debug("redis_not_installed_via_homebrew")
        return False

    # Try to start
    success, output = _run_silent(["brew", "services", "start", "redis"], timeout=10)
    if success:
        logger.info("redis_started_via_homebrew")
        time.sleep(1)  # Give it time to start
        return True

    logger.debug("homebrew_start_failed", output=output)
    return False


def _start_via_systemd() -> bool:
    """Try to start Redis via systemd (Linux)."""
    if not _find_command("systemctl"):
        return False

    # Try to start (may require sudo, which we avoid)
    success, output = _run_silent(["systemctl", "start", "redis"], timeout=10)
    if success:
        logger.info("redis_started_via_systemd")
        time.sleep(1)
        return True

    # Try redis-server service name variant
    success, output = _run_silent(["systemctl", "start", "redis-server"], timeout=10)
    if success:
        logger.info("redis_started_via_systemd", service="redis-server")
        time.sleep(1)
        return True

    logger.debug("systemd_start_failed", output=output)
    return False


def _start_via_docker(port: int = 6379) -> bool:
    """Try to start Redis via Docker."""
    if not _find_command("docker"):
        return False

    # Check if Docker daemon is running
    success, _ = _run_silent(["docker", "info"], timeout=5)
    if not success:
        logger.debug("docker_daemon_not_running")
        return False

    container_name = "empathy-redis"

    # Check if container exists
    success, output = _run_silent(
        ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
    )

    if container_name in output:
        # Container exists, try to start it
        success, _ = _run_silent(["docker", "start", container_name], timeout=10)
        if success:
            logger.info("redis_started_via_docker", action="started_existing")
            time.sleep(1)
            return True

    # Create and start new container
    success, output = _run_silent(
        ["docker", "run", "-d", "--name", container_name, "-p", f"{port}:6379", "redis:alpine"],
        timeout=30,
    )

    if success:
        logger.info("redis_started_via_docker", action="created_new")
        time.sleep(2)  # Give container time to start
        return True

    logger.debug("docker_start_failed", output=output)
    return False


def _start_via_direct(port: int = 6379) -> bool:
    """Try to start redis-server directly in background."""
    # On Windows, look for redis-server.exe
    if IS_WINDOWS:
        redis_server = _find_command("redis-server.exe") or _find_command("redis-server")
    else:
        redis_server = _find_command("redis-server")

    if not redis_server:
        return False

    try:
        if IS_WINDOWS:
            # Windows: Start without daemonize (run in background via subprocess)
            process = subprocess.Popen(
                [redis_server, "--port", str(port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
                ),
            )
            # Don't wait - let it run in background
            time.sleep(2)
            if process.poll() is None:  # Still running
                logger.info("redis_started_directly_windows")
                return True
        else:
            # Unix: Use daemonize
            process = subprocess.Popen(
                [redis_server, "--port", str(port), "--daemonize", "yes"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            process.wait(timeout=5)

            if process.returncode == 0:
                logger.info("redis_started_directly")
                time.sleep(1)
                return True
    except Exception as e:
        logger.debug("direct_start_failed", error=str(e))

    return False


def _start_via_windows_service() -> bool:
    """Try to start Redis via Windows Service."""
    if not IS_WINDOWS:
        return False

    try:
        # Try to start Redis service
        success, output = _run_silent(["net", "start", "Redis"], timeout=10)
        if success or "already been started" in output:
            logger.info("redis_started_via_windows_service")
            time.sleep(1)
            return True
    except Exception as e:
        logger.debug("windows_service_start_failed", error=str(e))

    return False


def _start_via_chocolatey() -> bool:
    """Try to start Redis installed via Chocolatey (Windows)."""
    if not IS_WINDOWS:
        return False

    choco = _find_command("choco")
    if not choco:
        return False

    # Check if redis is installed via chocolatey
    success, output = _run_silent(["choco", "list", "--local-only", "redis"])
    if not success or "redis" not in output.lower():
        logger.debug("redis_not_installed_via_chocolatey")
        return False

    # Chocolatey installs Redis as a service, try to start it
    return _start_via_windows_service()


def _start_via_scoop() -> bool:
    """Try to start Redis installed via Scoop (Windows)."""
    if not IS_WINDOWS:
        return False

    scoop = _find_command("scoop")
    if not scoop:
        return False

    # Check if redis is installed via scoop
    success, output = _run_silent(["scoop", "list", "redis"])
    if not success or "redis" not in output.lower():
        logger.debug("redis_not_installed_via_scoop")
        return False

    # Scoop typically installs to ~/scoop/apps/redis/current/
    scoop_redis = os.path.expanduser("~/scoop/apps/redis/current/redis-server.exe")
    if os.path.exists(scoop_redis):
        try:
            process = subprocess.Popen(
                [scoop_redis],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
                ),
            )
            time.sleep(2)
            if process.poll() is None:
                logger.info("redis_started_via_scoop")
                return True
        except Exception as e:
            logger.debug("scoop_start_failed", error=str(e))

    return False


def _start_via_wsl() -> bool:
    """Try to start Redis via WSL (Windows Subsystem for Linux)."""
    if not IS_WINDOWS:
        return False

    wsl = _find_command("wsl")
    if not wsl:
        return False

    try:
        # Check if Redis is installed in WSL
        success, output = _run_silent(["wsl", "which", "redis-server"])
        if not success:
            logger.debug("redis_not_installed_in_wsl")
            return False

        # Start Redis in WSL
        process = subprocess.Popen(
            ["wsl", "redis-server", "--daemonize", "yes"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process.wait(timeout=5)

        if process.returncode == 0:
            logger.info("redis_started_via_wsl")
            time.sleep(1)
            return True
    except Exception as e:
        logger.debug("wsl_start_failed", error=str(e))

    return False


def ensure_redis(
    host: str = "localhost",
    port: int = 6379,
    auto_start: bool = True,
    verbose: bool = True,
) -> RedisStatus:
    """Ensure Redis is available, starting it if necessary.

    Args:
        host: Redis host
        port: Redis port
        auto_start: Attempt to start Redis if not running
        verbose: Print status messages to console

    Returns:
        RedisStatus with availability info

    Example:
        >>> status = ensure_redis()
        >>> if status.available:
        ...     print(f"Redis ready via {status.method.value}")
        ... else:
        ...     print(f"Redis unavailable: {status.message}")

    """
    # Check if already running
    if _check_redis_running(host, port):
        status = RedisStatus(
            available=True,
            method=RedisStartMethod.ALREADY_RUNNING,
            host=host,
            port=port,
            message="Redis is running",
        )
        if verbose:
            logger.info("redis_already_running", host=host, port=port)
        return status

    if not auto_start:
        return RedisStatus(
            available=False,
            method=RedisStartMethod.MOCK,
            host=host,
            port=port,
            message="Redis not running and auto_start=False",
        )

    if verbose:
        print("Redis not running. Attempting to start...")

    # Build platform-specific method list
    start_methods: list[tuple[RedisStartMethod, Callable[[], bool]]] = []

    if IS_MACOS:
        start_methods.append((RedisStartMethod.HOMEBREW, _start_via_homebrew))
    elif IS_LINUX:
        start_methods.append((RedisStartMethod.SYSTEMD, _start_via_systemd))
    elif IS_WINDOWS:
        # Windows-specific methods
        start_methods.extend(
            [
                (RedisStartMethod.WINDOWS_SERVICE, _start_via_windows_service),
                (RedisStartMethod.CHOCOLATEY, _start_via_chocolatey),
                (RedisStartMethod.SCOOP, _start_via_scoop),
                (RedisStartMethod.WSL, _start_via_wsl),
            ],
        )

    # Docker and direct work on all platforms
    start_methods.extend(
        [
            (RedisStartMethod.DOCKER, lambda: _start_via_docker(port)),
            (RedisStartMethod.DIRECT, lambda: _start_via_direct(port)),
        ],
    )

    for method, start_func in start_methods:
        try:
            if start_func():
                # Verify it's actually running
                if _check_redis_running(host, port):
                    status = RedisStatus(
                        available=True,
                        method=method,
                        host=host,
                        port=port,
                        message=f"Redis started via {method.value}",
                    )
                    if verbose:
                        print(f"✓ Redis started via {method.value}")
                    return status
        except Exception as e:
            logger.debug(f"{method.value}_failed", error=str(e))
            continue

    # All methods failed - build platform-specific message
    if IS_WINDOWS:
        install_instructions = (
            "Could not start Redis. For full functionality, install Redis:\n"
            "  Chocolatey: choco install redis-64\n"
            "  Scoop:      scoop install redis\n"
            "  WSL:        wsl sudo apt install redis-server\n"
            "  Docker:     docker run -d -p 6379:6379 redis:alpine\n"
            "  Manual:     Download from https://github.com/microsoftarchive/redis/releases"
        )
    elif IS_MACOS:
        install_instructions = (
            "Could not start Redis. For full functionality, install Redis:\n"
            "  Homebrew: brew install redis && brew services start redis\n"
            "  Docker:   docker run -d -p 6379:6379 redis:alpine"
        )
    else:  # Linux
        install_instructions = (
            "Could not start Redis. For full functionality, install Redis:\n"
            "  Ubuntu/Debian: sudo apt install redis-server\n"
            "  RHEL/CentOS:   sudo yum install redis\n"
            "  Docker:        docker run -d -p 6379:6379 redis:alpine"
        )

    message = f"{install_instructions}\n\nFalling back to in-memory mock (single-process only)."

    if verbose:
        print(f"\n⚠ {message}")

    return RedisStatus(
        available=False,
        method=RedisStartMethod.MOCK,
        host=host,
        port=port,
        message=message,
    )


def stop_redis(method: RedisStartMethod) -> bool:
    """Stop Redis if we started it.

    Args:
        method: The method used to start Redis

    Returns:
        True if stopped successfully

    """
    if method == RedisStartMethod.HOMEBREW:
        success, _ = _run_silent(["brew", "services", "stop", "redis"])
        return success

    if method == RedisStartMethod.SYSTEMD:
        success, _ = _run_silent(["systemctl", "stop", "redis"])
        if not success:
            success, _ = _run_silent(["systemctl", "stop", "redis-server"])
        return success

    if method == RedisStartMethod.WINDOWS_SERVICE:
        success, _ = _run_silent(["net", "stop", "Redis"])
        return success

    if method == RedisStartMethod.CHOCOLATEY:
        # Chocolatey uses Windows Service
        success, _ = _run_silent(["net", "stop", "Redis"])
        return success

    if method == RedisStartMethod.WSL:
        success, _ = _run_silent(["wsl", "redis-cli", "shutdown", "nosave"])
        return success

    if method == RedisStartMethod.DOCKER:
        success, _ = _run_silent(["docker", "stop", "empathy-redis"])
        return success

    if method == RedisStartMethod.DIRECT:
        # Try redis-cli shutdown
        if IS_WINDOWS:
            redis_cli = _find_command("redis-cli.exe") or _find_command("redis-cli")
        else:
            redis_cli = _find_command("redis-cli")

        if redis_cli:
            success, _ = _run_silent([redis_cli, "shutdown", "nosave"])
            return success

    return False


# Convenience function for simple usage
def get_redis_or_mock(host: str = "localhost", port: int = 6379):
    """Get a Redis connection, starting Redis if needed, or return mock.

    Returns:
        tuple: (RedisShortTermMemory instance, RedisStatus)

    """
    from .short_term import RedisShortTermMemory

    status = ensure_redis(host=host, port=port)

    if status.available:
        memory = RedisShortTermMemory(host=host, port=port, use_mock=False)
    else:
        memory = RedisShortTermMemory(use_mock=True)

    return memory, status
