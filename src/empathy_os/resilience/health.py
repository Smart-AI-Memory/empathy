"""
Health Check Module

Provides system health monitoring and status reporting.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""

    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SystemHealth:
    """Overall system health status."""

    status: HealthStatus
    checks: list[HealthCheckResult]
    version: str = "unknown"
    uptime_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "version": self.version,
            "uptime_seconds": self.uptime_seconds,
            "timestamp": self.timestamp.isoformat(),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


class HealthCheck:
    """
    Health check manager for monitoring system components.

    Example:
        health = HealthCheck(version="3.1.0")

        @health.register("database")
        async def check_database():
            await db.ping()
            return True

        @health.register("memory_graph")
        async def check_memory_graph():
            graph = MemoryGraph()
            return len(graph.nodes) >= 0

        status = await health.run_all()
        print(status.to_dict())
    """

    def __init__(self, version: str = "unknown"):
        self.version = version
        self.start_time = time.time()
        self._checks: dict[str, Callable] = {}
        self._timeouts: dict[str, float] = {}

    def register(
        self,
        name: str,
        timeout: float = 10.0,
        critical: bool = False,
    ) -> Callable:
        """
        Decorator to register a health check.

        Args:
            name: Name of the health check
            timeout: Maximum time for check in seconds
            critical: If True, failure makes system unhealthy

        The decorated function should:
        - Return True for healthy
        - Return False for unhealthy
        - Raise exception for error
        - Return dict with 'healthy' key for details
        """

        def decorator(func: Callable) -> Callable:
            self._checks[name] = func
            self._timeouts[name] = timeout
            return func

        return decorator

    async def run_check(self, name: str) -> HealthCheckResult:
        """Run a single health check."""
        if name not in self._checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Check '{name}' not found",
            )

        check_func = self._checks[name]
        timeout = self._timeouts.get(name, 10.0)
        start = time.time()

        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await asyncio.wait_for(check_func(), timeout=timeout)
            else:
                result = check_func()

            latency = (time.time() - start) * 1000

            # Parse result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                return HealthCheckResult(
                    name=name,
                    status=status,
                    latency_ms=latency,
                )
            elif isinstance(result, dict):
                healthy = result.get("healthy", True)
                status = HealthStatus.HEALTHY if healthy else HealthStatus.UNHEALTHY
                return HealthCheckResult(
                    name=name,
                    status=status,
                    message=result.get("message", ""),
                    latency_ms=latency,
                    details=result,
                )
            else:
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check timed out after {timeout}s",
                latency_ms=timeout * 1000,
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                latency_ms=latency,
            )

    async def run_all(self) -> SystemHealth:
        """Run all registered health checks."""
        results = await asyncio.gather(*[self.run_check(name) for name in self._checks.keys()])

        # Determine overall status
        statuses = [r.status for r in results]

        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.UNKNOWN

        return SystemHealth(
            status=overall,
            checks=list(results),
            version=self.version,
            uptime_seconds=time.time() - self.start_time,
        )

    def run_all_sync(self) -> SystemHealth:
        """Synchronous version of run_all."""
        return asyncio.get_event_loop().run_until_complete(self.run_all())


# Global health check instance
_health_check: HealthCheck | None = None


def get_health_check() -> HealthCheck:
    """Get or create global health check instance."""
    global _health_check
    if _health_check is None:
        _health_check = HealthCheck()
    return _health_check


def register_default_checks(health: HealthCheck) -> None:
    """Register default health checks for Empathy Framework."""

    @health.register("wizard_registry")
    async def check_wizard_registry() -> dict[str, Any]:
        """Check wizard registry is loaded."""
        try:
            from empathy_os.routing import WizardRegistry

            registry = WizardRegistry()
            wizard_count = len(registry.list_all())
            return {
                "healthy": wizard_count > 0,
                "wizard_count": wizard_count,
                "message": f"{wizard_count} wizards registered",
            }
        except Exception as e:
            return {"healthy": False, "message": str(e)}

    @health.register("memory_graph")
    async def check_memory_graph() -> dict[str, Any]:
        """Check memory graph is accessible."""
        try:
            from empathy_os.memory import MemoryGraph

            graph_path = Path("patterns/memory_graph.json")
            if graph_path.exists():
                graph = MemoryGraph(path=graph_path)
                return {
                    "healthy": True,
                    "node_count": len(graph.nodes),
                    "edge_count": len(graph.edges),
                }
            return {
                "healthy": True,
                "node_count": 0,
                "edge_count": 0,
                "message": "Graph file not yet created",
            }
        except Exception as e:
            return {"healthy": False, "message": str(e)}

    @health.register("smart_router")
    async def check_smart_router() -> dict[str, Any]:
        """Check smart router is functional."""
        try:
            from empathy_os.routing import SmartRouter

            router = SmartRouter()
            # Test with a simple request
            decision = router.route_sync("test request")
            return {
                "healthy": decision is not None,
                "primary_wizard": decision.primary_wizard,
            }
        except Exception as e:
            return {"healthy": False, "message": str(e)}

    @health.register("chain_executor")
    async def check_chain_executor() -> dict[str, Any]:
        """Check chain executor is loaded."""
        try:
            from empathy_os.routing import ChainExecutor

            executor = ChainExecutor()
            templates = executor.list_templates()
            return {
                "healthy": True,
                "template_count": len(templates),
            }
        except Exception as e:
            return {"healthy": False, "message": str(e)}
