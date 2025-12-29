"""
Memory Control Panel for Empathy Framework

Enterprise-grade control panel for managing AI memory systems.
Provides both programmatic API and CLI interface.

Features:
- Redis lifecycle management (start/stop/status)
- Memory statistics and health monitoring
- Pattern management (list, search, delete)
- Configuration management
- Export/import capabilities

Usage (Python API):
    from empathy_os.memory import MemoryControlPanel

    panel = MemoryControlPanel()
    print(panel.status())
    panel.start_redis()
    panel.show_statistics()

Usage (CLI):
    python -m empathy_os.memory.control_panel status
    python -m empathy_os.memory.control_panel start
    python -m empathy_os.memory.control_panel stats
    python -m empathy_os.memory.control_panel patterns --list

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import argparse
import hashlib
import json
import logging
import os
import re
import signal
import ssl
import sys
import time
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import structlog

from .long_term import Classification, SecureMemDocsIntegration
from .redis_bootstrap import (
    RedisStartMethod,
    RedisStatus,
    _check_redis_running,
    ensure_redis,
    stop_redis,
)
from .short_term import AccessTier, AgentCredentials, RedisShortTermMemory

# Suppress noisy warnings in CLI mode
warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")

# Version
__version__ = "2.2.0"

logger = structlog.get_logger(__name__)

# =============================================================================
# Security Configuration
# =============================================================================

# Pattern ID validation regex - matches format: pat_YYYYMMDDHHMMSS_hexstring
PATTERN_ID_REGEX = re.compile(r"^pat_\d{14}_[a-f0-9]{8,16}$")

# Alternative pattern formats that are also valid
PATTERN_ID_ALT_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{2,63}$")

# Rate limiting configuration
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 100  # Per IP per window


def _validate_pattern_id(pattern_id: str) -> bool:
    """
    Validate pattern ID to prevent path traversal and injection attacks.

    Args:
        pattern_id: The pattern ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not pattern_id or not isinstance(pattern_id, str):
        return False

    # Check for path traversal attempts
    if ".." in pattern_id or "/" in pattern_id or "\\" in pattern_id:
        return False

    # Check for null bytes
    if "\x00" in pattern_id:
        return False

    # Check length bounds
    if len(pattern_id) < 3 or len(pattern_id) > 64:
        return False

    # Must match one of the valid formats
    return bool(PATTERN_ID_REGEX.match(pattern_id) or PATTERN_ID_ALT_REGEX.match(pattern_id))


def _validate_agent_id(agent_id: str) -> bool:
    """
    Validate agent ID format.

    Args:
        agent_id: The agent ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not agent_id or not isinstance(agent_id, str):
        return False

    # Check for dangerous characters
    if any(c in agent_id for c in [".", "/", "\\", "\x00", ";", "|", "&"]):
        return False

    # Check length bounds
    if len(agent_id) < 1 or len(agent_id) > 64:
        return False

    # Simple alphanumeric with some allowed chars
    return bool(re.match(r"^[a-zA-Z0-9_@.-]+$", agent_id))


def _validate_classification(classification: str | None) -> bool:
    """
    Validate classification parameter.

    Args:
        classification: The classification to validate

    Returns:
        True if valid, False otherwise
    """
    if classification is None:
        return True
    if not isinstance(classification, str):
        return False
    return classification.upper() in ("PUBLIC", "INTERNAL", "SENSITIVE")


class RateLimiter:
    """Simple in-memory rate limiter by IP address."""

    def __init__(self, window_seconds: int = 60, max_requests: int = 100):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """
        Check if request is allowed for this IP.

        Args:
            client_ip: The client IP address

        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        self._requests[client_ip] = [ts for ts in self._requests[client_ip] if ts > window_start]

        # Check if over limit
        if len(self._requests[client_ip]) >= self.max_requests:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            return False

        # Record this request
        self._requests[client_ip].append(now)
        return True

    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for this IP."""
        now = time.time()
        window_start = now - self.window_seconds
        recent = [ts for ts in self._requests[client_ip] if ts > window_start]
        return max(0, self.max_requests - len(recent))


class APIKeyAuth:
    """Simple API key authentication."""

    def __init__(self, api_key: str | None = None):
        """
        Initialize API key auth.

        Args:
            api_key: The API key to require. If None, reads from
                     EMPATHY_MEMORY_API_KEY env var. If still None, auth is disabled.
        """
        self.api_key = api_key or os.environ.get("EMPATHY_MEMORY_API_KEY")
        self.enabled = bool(self.api_key)
        if self.enabled:
            # Store hash of API key for comparison
            self._key_hash = hashlib.sha256(self.api_key.encode()).hexdigest()
            logger.info("api_key_auth_enabled")
        else:
            self._key_hash = None
            logger.info("api_key_auth_disabled", reason="no_key_configured")

    def is_valid(self, provided_key: str | None) -> bool:
        """
        Check if provided API key is valid.

        Args:
            provided_key: The key provided in the request

        Returns:
            True if valid or auth disabled, False otherwise
        """
        if not self.enabled:
            return True

        if not provided_key:
            return False

        # Constant-time comparison via hash
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return provided_hash == self._key_hash


@dataclass
class MemoryStats:
    """Statistics for memory system."""

    # Redis stats
    redis_available: bool = False
    redis_method: str = "none"
    redis_keys_total: int = 0
    redis_keys_working: int = 0
    redis_keys_staged: int = 0
    redis_memory_used: str = "0"

    # Long-term stats
    long_term_available: bool = False
    patterns_total: int = 0
    patterns_public: int = 0
    patterns_internal: int = 0
    patterns_sensitive: int = 0
    patterns_encrypted: int = 0

    # Performance stats
    redis_ping_ms: float = 0.0
    storage_bytes: int = 0
    collection_time_ms: float = 0.0

    # Timestamps
    collected_at: str = ""


@dataclass
class ControlPanelConfig:
    """Configuration for control panel."""

    redis_host: str = "localhost"
    redis_port: int = 6379
    storage_dir: str = "./memdocs_storage"
    audit_dir: str = "./logs"
    auto_start_redis: bool = True


class MemoryControlPanel:
    """
    Enterprise control panel for Empathy memory management.

    Provides unified management interface for:
    - Short-term memory (Redis)
    - Long-term memory (MemDocs/file storage)
    - Security and compliance controls

    Example:
        >>> panel = MemoryControlPanel()
        >>> status = panel.status()
        >>> print(f"Redis: {status['redis']['status']}")
        >>> print(f"Patterns: {status['long_term']['pattern_count']}")
    """

    def __init__(self, config: ControlPanelConfig | None = None):
        """
        Initialize control panel.

        Args:
            config: Configuration options (uses defaults if None)
        """
        self.config = config or ControlPanelConfig()
        self._redis_status: RedisStatus | None = None
        self._short_term: RedisShortTermMemory | None = None
        self._long_term: SecureMemDocsIntegration | None = None

    def status(self) -> dict[str, Any]:
        """
        Get comprehensive status of memory system.

        Returns:
            Dictionary with status of all memory components
        """
        redis_running = _check_redis_running(self.config.redis_host, self.config.redis_port)

        result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "redis": {
                "status": "running" if redis_running else "stopped",
                "host": self.config.redis_host,
                "port": self.config.redis_port,
                "method": self._redis_status.method.value if self._redis_status else "unknown",
            },
            "long_term": {
                "status": (
                    "available" if Path(self.config.storage_dir).exists() else "not_initialized"
                ),
                "storage_dir": self.config.storage_dir,
                "pattern_count": self._count_patterns(),
            },
            "config": {
                "auto_start_redis": self.config.auto_start_redis,
                "audit_dir": self.config.audit_dir,
            },
        }

        return result

    def start_redis(self, verbose: bool = True) -> RedisStatus:
        """
        Start Redis if not running.

        Args:
            verbose: Print status messages

        Returns:
            RedisStatus with result
        """
        self._redis_status = ensure_redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            auto_start=True,
            verbose=verbose,
        )
        return self._redis_status

    def stop_redis(self) -> bool:
        """
        Stop Redis if we started it.

        Returns:
            True if stopped successfully
        """
        if self._redis_status and self._redis_status.method != RedisStartMethod.ALREADY_RUNNING:
            return stop_redis(self._redis_status.method)
        return False

    def get_statistics(self) -> MemoryStats:
        """
        Collect comprehensive statistics.

        Returns:
            MemoryStats with all metrics
        """
        start_time = time.perf_counter()
        stats = MemoryStats(collected_at=datetime.utcnow().isoformat() + "Z")

        # Redis stats
        redis_running = _check_redis_running(self.config.redis_host, self.config.redis_port)
        stats.redis_available = redis_running

        if redis_running:
            try:
                memory = self._get_short_term()

                # Measure Redis ping latency
                ping_start = time.perf_counter()
                redis_stats = memory.get_stats()
                stats.redis_ping_ms = (time.perf_counter() - ping_start) * 1000

                stats.redis_method = redis_stats.get("mode", "redis")
                stats.redis_keys_total = redis_stats.get("total_keys", 0)
                stats.redis_keys_working = redis_stats.get("working_keys", 0)
                stats.redis_keys_staged = redis_stats.get("staged_keys", 0)
                stats.redis_memory_used = redis_stats.get("used_memory", "0")
            except Exception as e:
                logger.warning("redis_stats_failed", error=str(e))

        # Long-term stats
        storage_path = Path(self.config.storage_dir)
        if storage_path.exists():
            stats.long_term_available = True

            # Calculate storage size
            try:
                stats.storage_bytes = sum(
                    f.stat().st_size for f in storage_path.glob("**/*") if f.is_file()
                )
            except Exception:
                pass

            try:
                long_term = self._get_long_term()
                lt_stats = long_term.get_statistics()
                stats.patterns_total = lt_stats.get("total_patterns", 0)
                stats.patterns_public = lt_stats.get("by_classification", {}).get("PUBLIC", 0)
                stats.patterns_internal = lt_stats.get("by_classification", {}).get("INTERNAL", 0)
                stats.patterns_sensitive = lt_stats.get("by_classification", {}).get("SENSITIVE", 0)
                stats.patterns_encrypted = lt_stats.get("encrypted_count", 0)
            except Exception as e:
                logger.warning("long_term_stats_failed", error=str(e))

        # Total collection time
        stats.collection_time_ms = (time.perf_counter() - start_time) * 1000

        return stats

    def list_patterns(
        self,
        classification: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        List patterns in long-term storage.

        Args:
            classification: Filter by classification (PUBLIC/INTERNAL/SENSITIVE)
            limit: Maximum patterns to return

        Returns:
            List of pattern summaries
        """
        long_term = self._get_long_term()

        class_filter = None
        if classification:
            class_filter = Classification[classification.upper()]

        # Use admin user for listing
        patterns = long_term.list_patterns(
            user_id="admin@system",
            classification=class_filter,
        )

        return patterns[:limit]

    def delete_pattern(self, pattern_id: str, user_id: str = "admin@system") -> bool:
        """
        Delete a pattern from long-term storage.

        Args:
            pattern_id: Pattern to delete
            user_id: User performing deletion (for audit)

        Returns:
            True if deleted
        """
        long_term = self._get_long_term()
        try:
            return long_term.delete_pattern(pattern_id, user_id)
        except Exception as e:
            logger.error("delete_pattern_failed", pattern_id=pattern_id, error=str(e))
            return False

    def clear_short_term(self, agent_id: str = "admin") -> int:
        """
        Clear all short-term memory for an agent.

        Args:
            agent_id: Agent whose memory to clear

        Returns:
            Number of keys deleted
        """
        memory = self._get_short_term()
        creds = AgentCredentials(agent_id=agent_id, tier=AccessTier.STEWARD)
        return memory.clear_working_memory(creds)

    def export_patterns(self, output_path: str, classification: str | None = None) -> int:
        """
        Export patterns to JSON file.

        Args:
            output_path: Path to output file
            classification: Filter by classification

        Returns:
            Number of patterns exported
        """
        patterns = self.list_patterns(classification=classification)

        export_data = {
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "classification_filter": classification,
            "pattern_count": len(patterns),
            "patterns": patterns,
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        return len(patterns)

    def health_check(self) -> dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Health status with recommendations
        """
        status = self.status()
        stats = self.get_statistics()

        checks: list[dict[str, str]] = []
        recommendations: list[str] = []
        health: dict[str, Any] = {
            "overall": "healthy",
            "checks": checks,
            "recommendations": recommendations,
        }

        # Check Redis
        if status["redis"]["status"] == "running":
            checks.append({"name": "redis", "status": "pass", "message": "Redis is running"})
        else:
            checks.append({"name": "redis", "status": "warn", "message": "Redis not running"})
            recommendations.append("Start Redis for multi-agent coordination")
            health["overall"] = "degraded"

        # Check long-term storage
        if status["long_term"]["status"] == "available":
            checks.append({"name": "long_term", "status": "pass", "message": "Storage available"})
        else:
            checks.append(
                {"name": "long_term", "status": "warn", "message": "Storage not initialized"}
            )
            recommendations.append("Initialize long-term storage directory")
            health["overall"] = "degraded"

        # Check pattern count
        if stats.patterns_total > 0:
            checks.append(
                {
                    "name": "patterns",
                    "status": "pass",
                    "message": f"{stats.patterns_total} patterns stored",
                }
            )
        else:
            checks.append(
                {"name": "patterns", "status": "info", "message": "No patterns stored yet"}
            )

        # Check encryption
        if stats.patterns_sensitive > 0 and stats.patterns_encrypted < stats.patterns_sensitive:
            checks.append(
                {
                    "name": "encryption",
                    "status": "fail",
                    "message": "Some sensitive patterns are not encrypted",
                }
            )
            recommendations.append("Enable encryption for sensitive patterns")
            health["overall"] = "unhealthy"
        elif stats.patterns_sensitive > 0:
            checks.append(
                {
                    "name": "encryption",
                    "status": "pass",
                    "message": "All sensitive patterns encrypted",
                }
            )

        return health

    def _get_short_term(self) -> RedisShortTermMemory:
        """Get or create short-term memory instance."""
        if self._short_term is None:
            redis_running = _check_redis_running(self.config.redis_host, self.config.redis_port)
            self._short_term = RedisShortTermMemory(
                host=self.config.redis_host,
                port=self.config.redis_port,
                use_mock=not redis_running,
            )
        return self._short_term

    def _get_long_term(self) -> SecureMemDocsIntegration:
        """Get or create long-term memory instance."""
        if self._long_term is None:
            self._long_term = SecureMemDocsIntegration(
                storage_dir=self.config.storage_dir,
                audit_log_dir=self.config.audit_dir,
                enable_encryption=True,
            )
        return self._long_term

    def _count_patterns(self) -> int:
        """Count patterns in storage."""
        storage_path = Path(self.config.storage_dir)
        if not storage_path.exists():
            return 0
        return len(list(storage_path.glob("*.json")))


def print_status(panel: MemoryControlPanel):
    """Print status in a formatted way."""
    status = panel.status()

    print("\n" + "=" * 50)
    print("EMPATHY MEMORY STATUS")
    print("=" * 50)

    # Redis
    redis = status["redis"]
    redis_icon = "✓" if redis["status"] == "running" else "✗"
    print(f"\n{redis_icon} Redis: {redis['status'].upper()}")
    print(f"  Host: {redis['host']}:{redis['port']}")
    if redis["method"] != "unknown":
        print(f"  Method: {redis['method']}")

    # Long-term
    lt = status["long_term"]
    lt_icon = "✓" if lt["status"] == "available" else "○"
    print(f"\n{lt_icon} Long-term Storage: {lt['status'].upper()}")
    print(f"  Path: {lt['storage_dir']}")
    print(f"  Patterns: {lt['pattern_count']}")

    print()


def print_stats(panel: MemoryControlPanel):
    """Print statistics in a formatted way."""
    stats = panel.get_statistics()

    print("\n" + "=" * 50)
    print("EMPATHY MEMORY STATISTICS")
    print("=" * 50)

    print("\nShort-term Memory (Redis):")
    print(f"  Available: {stats.redis_available}")
    if stats.redis_available:
        print(f"  Total keys: {stats.redis_keys_total}")
        print(f"  Working keys: {stats.redis_keys_working}")
        print(f"  Staged patterns: {stats.redis_keys_staged}")
        print(f"  Memory used: {stats.redis_memory_used}")

    print("\nLong-term Memory (Patterns):")
    print(f"  Available: {stats.long_term_available}")
    print(f"  Total patterns: {stats.patterns_total}")
    print(f"  └─ PUBLIC: {stats.patterns_public}")
    print(f"  └─ INTERNAL: {stats.patterns_internal}")
    print(f"  └─ SENSITIVE: {stats.patterns_sensitive}")
    print(f"  Encrypted: {stats.patterns_encrypted}")

    # Performance stats
    print("\nPerformance:")
    if stats.redis_ping_ms > 0:
        print(f"  Redis latency: {stats.redis_ping_ms:.2f}ms")
    if stats.storage_bytes > 0:
        size_kb = stats.storage_bytes / 1024
        print(f"  Storage size: {size_kb:.1f} KB")
    print(f"  Stats collected in: {stats.collection_time_ms:.2f}ms")

    print()


def print_health(panel: MemoryControlPanel):
    """Print health check in a formatted way."""
    health = panel.health_check()

    print("\n" + "=" * 50)
    print("EMPATHY MEMORY HEALTH CHECK")
    print("=" * 50)

    status_icons = {"pass": "✓", "warn": "⚠", "fail": "✗", "info": "ℹ"}
    overall_icon = (
        "✓" if health["overall"] == "healthy" else "⚠" if health["overall"] == "degraded" else "✗"
    )

    print(f"\n{overall_icon} Overall: {health['overall'].upper()}")

    print("\nChecks:")
    for check in health["checks"]:
        icon = status_icons.get(check["status"], "?")
        print(f"  {icon} {check['name']}: {check['message']}")

    if health["recommendations"]:
        print("\nRecommendations:")
        for rec in health["recommendations"]:
            print(f"  • {rec}")

    print()


class MemoryAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Memory Control Panel API."""

    panel: MemoryControlPanel | None = None  # Set by server
    rate_limiter: RateLimiter | None = None  # Set by server
    api_auth: APIKeyAuth | None = None  # Set by server
    allowed_origins: list[str] | None = None  # Set by server for CORS

    def log_message(self, format, *args):
        """Override to use structlog instead of stderr."""
        logger.debug("api_request", message=format % args)

    def _get_client_ip(self) -> str:
        """Get client IP address, handling proxies."""
        # Check for X-Forwarded-For header (behind proxy)
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP in the chain
            return forwarded.split(",")[0].strip()
        # Fall back to direct connection
        return self.client_address[0]

    def _check_rate_limit(self) -> bool:
        """Check if request should be rate limited."""
        if self.rate_limiter is None:
            return True
        return self.rate_limiter.is_allowed(self._get_client_ip())

    def _check_auth(self) -> bool:
        """Check API key authentication."""
        if self.api_auth is None or not self.api_auth.enabled:
            return True

        # Check Authorization header
        auth_header = self.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return self.api_auth.is_valid(token)

        # Check X-API-Key header
        api_key = self.headers.get("X-API-Key")
        if api_key:
            return self.api_auth.is_valid(api_key)

        return False

    def _get_cors_origin(self) -> str:
        """Get appropriate CORS origin header value."""
        if self.allowed_origins is None:
            # Default: allow localhost only
            origin = self.headers.get("Origin", "")
            if origin.startswith("http://localhost") or origin.startswith("https://localhost"):
                return origin
            return "http://localhost:8765"

        if "*" in self.allowed_origins:
            return "*"

        origin = self.headers.get("Origin", "")
        if origin in self.allowed_origins:
            return origin

        return self.allowed_origins[0] if self.allowed_origins else ""

    def _send_json(self, data: Any, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", self._get_cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")

        # Add rate limit headers if available
        if self.rate_limiter:
            remaining = self.rate_limiter.get_remaining(self._get_client_ip())
            self.send_header("X-RateLimit-Remaining", str(remaining))
            self.send_header("X-RateLimit-Limit", str(self.rate_limiter.max_requests))

        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message: str, status: int = 400):
        """Send error response."""
        self._send_json({"error": message, "status_code": status}, status)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", self._get_cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        # Rate limiting check
        if not self._check_rate_limit():
            self._send_error("Rate limit exceeded. Try again later.", 429)
            return

        # Authentication check (skip for ping endpoint)
        parsed = urlparse(self.path)
        path = parsed.path

        if path != "/api/ping" and not self._check_auth():
            self._send_error("Unauthorized. Provide valid API key.", 401)
            return

        query = parse_qs(parsed.query)

        if path == "/api/ping":
            self._send_json({"status": "ok", "service": "empathy-memory"})

        elif path == "/api/status":
            self._send_json(self.panel.status())

        elif path == "/api/stats":
            stats = self.panel.get_statistics()
            self._send_json(asdict(stats))

        elif path == "/api/health":
            self._send_json(self.panel.health_check())

        elif path == "/api/patterns":
            classification = query.get("classification", [None])[0]

            # Validate classification
            if not _validate_classification(classification):
                self._send_error("Invalid classification. Use PUBLIC, INTERNAL, or SENSITIVE.", 400)
                return

            # Validate and sanitize limit
            try:
                limit = int(query.get("limit", [100])[0])
                limit = max(1, min(limit, 1000))  # Clamp between 1 and 1000
            except (ValueError, TypeError):
                limit = 100

            patterns = self.panel.list_patterns(classification=classification, limit=limit)
            self._send_json(patterns)

        elif path == "/api/patterns/export":
            classification = query.get("classification", [None])[0]

            # Validate classification
            if not _validate_classification(classification):
                self._send_error("Invalid classification. Use PUBLIC, INTERNAL, or SENSITIVE.", 400)
                return

            patterns = self.panel.list_patterns(classification=classification)
            export_data = {
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "classification_filter": classification,
                "patterns": patterns,
            }
            self._send_json({"pattern_count": len(patterns), "export_data": export_data})

        elif path.startswith("/api/patterns/"):
            pattern_id = path.split("/")[-1]

            # Validate pattern ID
            if not _validate_pattern_id(pattern_id):
                self._send_error("Invalid pattern ID format", 400)
                return

            patterns = self.panel.list_patterns()
            pattern = next((p for p in patterns if p.get("pattern_id") == pattern_id), None)
            if pattern:
                self._send_json(pattern)
            else:
                self._send_error("Pattern not found", 404)

        else:
            self._send_error("Not found", 404)

    def do_POST(self):
        """Handle POST requests."""
        # Rate limiting check
        if not self._check_rate_limit():
            self._send_error("Rate limit exceeded. Try again later.", 429)
            return

        # Authentication check
        if not self._check_auth():
            self._send_error("Unauthorized. Provide valid API key.", 401)
            return

        parsed = urlparse(self.path)
        path = parsed.path

        # Read body if present (with size limit to prevent DoS)
        content_length = int(self.headers.get("Content-Length", 0))
        max_body_size = 1024 * 1024  # 1MB limit
        if content_length > max_body_size:
            self._send_error("Request body too large", 413)
            return

        body = {}
        if content_length > 0:
            try:
                body = json.loads(self.rfile.read(content_length).decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_error("Invalid JSON body", 400)
                return

        if path == "/api/redis/start":
            status = self.panel.start_redis(verbose=False)
            self._send_json(
                {
                    "success": status.available,
                    "message": f"Redis {'OK' if status.available else 'failed'} via {status.method.value}",
                }
            )

        elif path == "/api/redis/stop":
            stopped = self.panel.stop_redis()
            self._send_json(
                {
                    "success": stopped,
                    "message": "Redis stopped" if stopped else "Could not stop Redis",
                }
            )

        elif path == "/api/memory/clear":
            agent_id = body.get("agent_id", "admin")

            # Validate agent ID
            if not _validate_agent_id(agent_id):
                self._send_error("Invalid agent ID format", 400)
                return

            deleted = self.panel.clear_short_term(agent_id)
            self._send_json({"keys_deleted": deleted})

        else:
            self._send_error("Not found", 404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        # Rate limiting check
        if not self._check_rate_limit():
            self._send_error("Rate limit exceeded. Try again later.", 429)
            return

        # Authentication check
        if not self._check_auth():
            self._send_error("Unauthorized. Provide valid API key.", 401)
            return

        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/patterns/"):
            pattern_id = path.split("/")[-1]

            # Validate pattern ID to prevent path traversal
            if not _validate_pattern_id(pattern_id):
                self._send_error("Invalid pattern ID format", 400)
                return

            deleted = self.panel.delete_pattern(pattern_id)
            self._send_json({"success": deleted})
        else:
            self._send_error("Not found", 404)


def run_api_server(
    panel: MemoryControlPanel,
    host: str = "localhost",
    port: int = 8765,
    api_key: str | None = None,
    enable_rate_limit: bool = True,
    rate_limit_requests: int = 100,
    rate_limit_window: int = 60,
    ssl_certfile: str | None = None,
    ssl_keyfile: str | None = None,
    allowed_origins: list[str] | None = None,
):
    """
    Run the Memory API server with security features.

    Args:
        panel: MemoryControlPanel instance
        host: Host to bind to
        port: Port to bind to
        api_key: API key for authentication (or set EMPATHY_MEMORY_API_KEY env var)
        enable_rate_limit: Enable rate limiting
        rate_limit_requests: Max requests per window per IP
        rate_limit_window: Rate limit window in seconds
        ssl_certfile: Path to SSL certificate file for HTTPS
        ssl_keyfile: Path to SSL key file for HTTPS
        allowed_origins: List of allowed CORS origins (None = localhost only)
    """
    # Set up handler class attributes
    MemoryAPIHandler.panel = panel
    MemoryAPIHandler.allowed_origins = allowed_origins

    # Set up rate limiting
    if enable_rate_limit:
        MemoryAPIHandler.rate_limiter = RateLimiter(
            window_seconds=rate_limit_window, max_requests=rate_limit_requests
        )
    else:
        MemoryAPIHandler.rate_limiter = None

    # Set up API key authentication
    MemoryAPIHandler.api_auth = APIKeyAuth(api_key)

    server = HTTPServer((host, port), MemoryAPIHandler)

    # Enable HTTPS if certificates provided
    use_https = False
    if ssl_certfile and ssl_keyfile:
        if Path(ssl_certfile).exists() and Path(ssl_keyfile).exists():
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(ssl_certfile, ssl_keyfile)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            use_https = True
        else:
            logger.warning("ssl_cert_not_found", certfile=ssl_certfile, keyfile=ssl_keyfile)

    protocol = "https" if use_https else "http"

    # Graceful shutdown handler
    def shutdown_handler(signum, frame):
        print("\n\nReceived shutdown signal...")
        print("Stopping API server...")
        server.shutdown()
        # Stop Redis if we started it
        if panel.stop_redis():
            print("Stopped Redis")
        print("Shutdown complete.")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    print(f"\n{'=' * 50}")
    print("EMPATHY MEMORY API SERVER")
    print(f"{'=' * 50}")
    print(f"\nServer running at {protocol}://{host}:{port}")

    # Security status
    print("\nSecurity:")
    print(f"  HTTPS:        {'✓ Enabled' if use_https else '✗ Disabled'}")
    print(f"  API Key Auth: {'✓ Enabled' if MemoryAPIHandler.api_auth.enabled else '✗ Disabled'}")
    print(
        f"  Rate Limit:   {'✓ Enabled (' + str(rate_limit_requests) + '/min)' if enable_rate_limit else '✗ Disabled'}"
    )
    print(f"  CORS Origins: {allowed_origins or ['localhost']}")

    print("\nEndpoints:")
    print("  GET  /api/ping           Health check (no auth)")
    print("  GET  /api/status         Memory system status")
    print("  GET  /api/stats          Detailed statistics")
    print("  GET  /api/health         Health check with recommendations")
    print("  GET  /api/patterns       List patterns")
    print("  GET  /api/patterns/export Export patterns")
    print("  POST /api/redis/start    Start Redis")
    print("  POST /api/redis/stop     Stop Redis")
    print("  POST /api/memory/clear   Clear short-term memory")

    if MemoryAPIHandler.api_auth.enabled:
        print("\nAuthentication:")
        print("  Add header: Authorization: Bearer <your-api-key>")
        print("  Or header:  X-API-Key: <your-api-key>")

    print("\nPress Ctrl+C to stop\n")

    server.serve_forever()


def _configure_logging(verbose: bool = False):
    """Configure logging for CLI mode."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(message)s")
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(level),
    )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Empathy Memory Control Panel - Manage Redis and pattern storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status              Show memory system status
  %(prog)s start               Start Redis if not running
  %(prog)s stop                Stop Redis (if we started it)
  %(prog)s stats               Show detailed statistics
  %(prog)s health              Run health check
  %(prog)s patterns            List stored patterns
  %(prog)s export patterns.json  Export patterns to file
  %(prog)s api --api-port 8765 Start REST API server only
  %(prog)s serve               Start Redis + API server (recommended)

Quick Start:
  1. pip install empathy-framework
  2. empathy-memory serve
  3. Open http://localhost:8765/api/status in browser
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "status",
            "start",
            "stop",
            "stats",
            "health",
            "patterns",
            "export",
            "api",
            "serve",
        ],
        help="Command to execute",
        nargs="?",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"empathy-memory {__version__}",
    )
    parser.add_argument(
        "--host", default="localhost", help="Redis host (or API host for 'api' command)"
    )
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    parser.add_argument(
        "--api-port", type=int, default=8765, help="API server port (for 'api' command)"
    )
    parser.add_argument(
        "--storage", default="./memdocs_storage", help="Long-term storage directory"
    )
    parser.add_argument(
        "--classification", "-c", help="Filter by classification (PUBLIC/INTERNAL/SENSITIVE)"
    )
    parser.add_argument("--output", "-o", help="Output file for export")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug output")

    # Security options (for api/serve commands)
    parser.add_argument(
        "--api-key", help="API key for authentication (or set EMPATHY_MEMORY_API_KEY env var)"
    )
    parser.add_argument("--no-rate-limit", action="store_true", help="Disable rate limiting")
    parser.add_argument(
        "--rate-limit", type=int, default=100, help="Max requests per minute per IP (default: 100)"
    )
    parser.add_argument("--ssl-cert", help="Path to SSL certificate file for HTTPS")
    parser.add_argument("--ssl-key", help="Path to SSL key file for HTTPS")
    parser.add_argument(
        "--cors-origins", help="Comma-separated list of allowed CORS origins (default: localhost)"
    )

    args = parser.parse_args()

    # Configure logging (quiet by default)
    _configure_logging(verbose=args.verbose)

    # If no command specified, show help
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    config = ControlPanelConfig(
        redis_host=args.host,
        redis_port=args.port,
        storage_dir=args.storage,
    )
    panel = MemoryControlPanel(config)

    if args.command == "status":
        if args.json:
            print(json.dumps(panel.status(), indent=2))
        else:
            print_status(panel)

    elif args.command == "start":
        status = panel.start_redis(verbose=not args.json)
        if args.json:
            print(json.dumps({"available": status.available, "method": status.method.value}))
        elif status.available:
            print(f"\n✓ Redis started via {status.method.value}")
        else:
            print(f"\n✗ Failed to start Redis: {status.message}")
            sys.exit(1)

    elif args.command == "stop":
        if panel.stop_redis():
            print("✓ Redis stopped")
        else:
            print("⚠ Could not stop Redis (may not have been started by us)")

    elif args.command == "stats":
        if args.json:
            print(json.dumps(asdict(panel.get_statistics()), indent=2))
        else:
            print_stats(panel)

    elif args.command == "health":
        if args.json:
            print(json.dumps(panel.health_check(), indent=2))
        else:
            print_health(panel)

    elif args.command == "patterns":
        patterns = panel.list_patterns(classification=args.classification)
        if args.json:
            print(json.dumps(patterns, indent=2))
        else:
            print(f"\nPatterns ({len(patterns)} found):")
            for p in patterns:
                print(
                    f"  [{p.get('classification', '?')}] {p.get('pattern_id', '?')} ({p.get('pattern_type', '?')})"
                )

    elif args.command == "export":
        output = args.output or "patterns_export.json"
        count = panel.export_patterns(output, classification=args.classification)
        print(f"✓ Exported {count} patterns to {output}")

    elif args.command == "api":
        # Parse CORS origins
        cors_origins = None
        if args.cors_origins:
            cors_origins = [o.strip() for o in args.cors_origins.split(",")]

        run_api_server(
            panel,
            host=args.host,
            port=args.api_port,
            api_key=args.api_key,
            enable_rate_limit=not args.no_rate_limit,
            rate_limit_requests=args.rate_limit,
            ssl_certfile=args.ssl_cert,
            ssl_keyfile=args.ssl_key,
            allowed_origins=cors_origins,
        )

    elif args.command == "serve":
        # Start Redis first
        print("\n" + "=" * 50)
        print("EMPATHY MEMORY - STARTING SERVICES")
        print("=" * 50)

        print("\n[1/2] Starting Redis...")
        redis_status = panel.start_redis(verbose=False)
        if redis_status.available:
            print(f"  ✓ Redis running via {redis_status.method.value}")
        else:
            print(f"  ⚠ Redis not available: {redis_status.message}")
            print("      (Continuing with mock memory)")

        # Parse CORS origins
        cors_origins = None
        if args.cors_origins:
            cors_origins = [o.strip() for o in args.cors_origins.split(",")]

        print("\n[2/2] Starting API server...")
        run_api_server(
            panel,
            host=args.host,
            port=args.api_port,
            api_key=args.api_key,
            enable_rate_limit=not args.no_rate_limit,
            rate_limit_requests=args.rate_limit,
            ssl_certfile=args.ssl_cert,
            ssl_keyfile=args.ssl_key,
            allowed_origins=cors_origins,
        )


if __name__ == "__main__":
    main()
