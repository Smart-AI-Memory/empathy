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
import json
import logging
import signal
import sys
import time
import warnings
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
__version__ = "2.1.1"

logger = structlog.get_logger(__name__)


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

    def log_message(self, format, *args):
        """Override to use structlog instead of stderr."""
        logger.debug("api_request", message=format % args)

    def _send_json(self, data: Any, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message: str, status: int = 400):
        """Send error response."""
        self._send_json({"error": message, "status_code": status}, status)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
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
            limit = int(query.get("limit", [100])[0])
            patterns = self.panel.list_patterns(classification=classification, limit=limit)
            self._send_json(patterns)

        elif path == "/api/patterns/export":
            classification = query.get("classification", [None])[0]
            patterns = self.panel.list_patterns(classification=classification)
            export_data = {
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "classification_filter": classification,
                "patterns": patterns,
            }
            self._send_json({"pattern_count": len(patterns), "export_data": export_data})

        elif path.startswith("/api/patterns/"):
            pattern_id = path.split("/")[-1]
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
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body if present
        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length > 0:
            body = json.loads(self.rfile.read(content_length).decode())

        if path == "/api/redis/start":
            status = self.panel.start_redis(verbose=False)
            self._send_json(
                {
                    "success": status.available,
                    "message": f"Redis {'started' if status.available else 'failed'} via {status.method.value}",
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
            deleted = self.panel.clear_short_term(agent_id)
            self._send_json({"keys_deleted": deleted})

        else:
            self._send_error("Not found", 404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/patterns/"):
            pattern_id = path.split("/")[-1]
            deleted = self.panel.delete_pattern(pattern_id)
            self._send_json({"success": deleted})
        else:
            self._send_error("Not found", 404)


def run_api_server(panel: MemoryControlPanel, host: str = "localhost", port: int = 8765):
    """Run the Memory API server."""
    MemoryAPIHandler.panel = panel

    server = HTTPServer((host, port), MemoryAPIHandler)

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
    print(f"\nServer running at http://{host}:{port}")
    print("\nEndpoints:")
    print("  GET  /api/ping           Health check")
    print("  GET  /api/status         Memory system status")
    print("  GET  /api/stats          Detailed statistics")
    print("  GET  /api/health         Health check with recommendations")
    print("  GET  /api/patterns       List patterns")
    print("  GET  /api/patterns/export Export patterns")
    print("  POST /api/redis/start    Start Redis")
    print("  POST /api/redis/stop     Stop Redis")
    print("  POST /api/memory/clear   Clear short-term memory")
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
                    f"  [{p.get('classification', 'UNKNOWN')}] {p.get('pattern_id', 'unknown')} ({p.get('pattern_type', 'unknown')})"
                )

    elif args.command == "export":
        output = args.output or "patterns_export.json"
        count = panel.export_patterns(output, classification=args.classification)
        print(f"✓ Exported {count} patterns to {output}")

    elif args.command == "api":
        run_api_server(panel, host=args.host, port=args.api_port)

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

        print("\n[2/2] Starting API server...")
        run_api_server(panel, host=args.host, port=args.api_port)


if __name__ == "__main__":
    main()
