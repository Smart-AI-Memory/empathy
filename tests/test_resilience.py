"""
Tests for Resilience Module

Tests retry, circuit breaker, timeout, fallback, and health check patterns.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import time

import pytest

from empathy_os.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    Fallback,
    HealthCheck,
    HealthStatus,
    ResilienceTimeoutError,
    RetryConfig,
    circuit_breaker,
    fallback,
    retry,
    timeout,
    with_timeout,
)


class TestRetry:
    """Tests for retry pattern."""

    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0

        @retry(max_attempts=3)
        async def succeeds():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await succeeds()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Test function succeeds after initial failures."""
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.01)
        async def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient error")
            return "success"

        result = await fails_twice()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_all_attempts_fail(self):
        """Test raises after all attempts fail."""
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Permanent error")

        with pytest.raises(ValueError, match="Permanent error"):
            await always_fails()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_config_backoff(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_factor=2.0,
            max_delay=60.0,
            jitter=False,
        )

        assert config.get_delay(1) == 1.0
        assert config.get_delay(2) == 2.0
        assert config.get_delay(3) == 4.0
        assert config.get_delay(10) == 60.0  # Capped at max_delay

    def test_retry_sync_function(self):
        """Test retry with synchronous function."""
        call_count = 0

        @retry(max_attempts=2, initial_delay=0.01)
        def sync_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail once")
            return "done"

        result = sync_func()
        assert result == "done"
        assert call_count == 2


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""

    def test_circuit_starts_closed(self):
        """Test circuit starts in closed state."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed

    def test_circuit_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        cb = CircuitBreaker(name="test", failure_threshold=3)

        for _ in range(3):
            cb.record_failure(ValueError("error"))

        assert cb.state == CircuitState.OPEN
        assert cb.is_open

    def test_circuit_half_open_after_timeout(self):
        """Test circuit transitions to half-open."""
        cb = CircuitBreaker(name="test", failure_threshold=2, reset_timeout=0.01)

        cb.record_failure(ValueError("error"))
        cb.record_failure(ValueError("error"))
        assert cb.is_open

        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN

    def test_circuit_closes_on_success(self):
        """Test circuit closes after successful recovery."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            reset_timeout=0.01,
            half_open_max_calls=2,
        )

        cb.record_failure(ValueError("error"))
        cb.record_failure(ValueError("error"))
        time.sleep(0.02)

        # In half-open, record successes
        cb.record_success()
        cb.record_success()

        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_decorator(self):
        """Test circuit breaker decorator."""
        call_count = 0

        @circuit_breaker(name="test_dec", failure_threshold=2, reset_timeout=0.01)
        async def flaky_service():
            nonlocal call_count
            call_count += 1
            raise ValueError("Service down")

        # First two calls fail and open circuit
        with pytest.raises(ValueError):
            await flaky_service()
        with pytest.raises(ValueError):
            await flaky_service()

        # Third call should fail fast
        with pytest.raises(CircuitOpenError):
            await flaky_service()

        assert call_count == 2  # Only 2 actual calls

    @pytest.mark.asyncio
    async def test_circuit_breaker_with_fallback(self):
        """Test circuit breaker with fallback function."""

        async def fallback_func():
            return "fallback"

        @circuit_breaker(name="test_fb", failure_threshold=1, fallback=fallback_func)
        async def service():
            raise ValueError("Down")

        # First call fails and opens
        with pytest.raises(ValueError):
            await service()

        # Second call uses fallback
        result = await service()
        assert result == "fallback"


class TestTimeout:
    """Tests for timeout pattern."""

    @pytest.mark.asyncio
    async def test_timeout_success(self):
        """Test function completes within timeout."""

        @timeout(1.0)
        async def fast_func():
            await asyncio.sleep(0.01)
            return "done"

        result = await fast_func()
        assert result == "done"

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Test function exceeds timeout."""

        @timeout(0.01)
        async def slow_func():
            await asyncio.sleep(1.0)
            return "done"

        with pytest.raises(ResilienceTimeoutError):
            await slow_func()

    @pytest.mark.asyncio
    async def test_timeout_with_fallback(self):
        """Test timeout with fallback value."""

        @timeout(0.01, fallback=lambda: "fallback")
        async def slow_func():
            await asyncio.sleep(1.0)
            return "done"

        result = await slow_func()
        assert result == "fallback"

    @pytest.mark.asyncio
    async def test_with_timeout_helper(self):
        """Test with_timeout helper function."""

        async def slow_coro():
            await asyncio.sleep(1.0)
            return "done"

        result = await with_timeout(slow_coro(), 0.01, fallback_value="default")
        assert result == "default"


class TestFallback:
    """Tests for fallback pattern."""

    @pytest.mark.asyncio
    async def test_fallback_chain(self):
        """Test fallback chain execution."""
        fb = Fallback(name="test")

        async def fails():
            raise ValueError("Primary fails")

        async def succeeds():
            return "backup"

        fb.add(fails)
        fb.add(succeeds)

        result = await fb.execute()
        assert result == "backup"

    @pytest.mark.asyncio
    async def test_fallback_default_value(self):
        """Test fallback uses default when all fail."""
        fb = Fallback(name="test", default_value="default")

        async def fails():
            raise ValueError("Fails")

        fb.add(fails)

        result = await fb.execute()
        assert result == "default"

    @pytest.mark.asyncio
    async def test_fallback_decorator(self):
        """Test fallback decorator."""
        call_order = []

        def backup():
            call_order.append("backup")
            return "backup_result"

        @fallback(backup, default="default")
        async def primary():
            call_order.append("primary")
            raise ValueError("Primary fails")

        result = await primary()
        assert result == "backup_result"
        assert call_order == ["primary", "backup"]


class TestHealthCheck:
    """Tests for health check module."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """Test healthy check returns healthy status."""
        health = HealthCheck(version="1.0.0")

        @health.register("test")
        async def check():
            return True

        result = await health.run_check("test")
        assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test unhealthy check returns unhealthy status."""
        health = HealthCheck()

        @health.register("test")
        async def check():
            return False

        result = await health.run_check("test")
        assert result.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test exception results in unhealthy status."""
        health = HealthCheck()

        @health.register("test")
        async def check():
            raise RuntimeError("Database down")

        result = await health.run_check("test")
        assert result.status == HealthStatus.UNHEALTHY
        assert "Database down" in result.message

    @pytest.mark.asyncio
    async def test_health_check_with_details(self):
        """Test health check with detailed response."""
        health = HealthCheck()

        @health.register("test")
        async def check():
            return {
                "healthy": True,
                "message": "All good",
                "connections": 10,
            }

        result = await health.run_check("test")
        assert result.status == HealthStatus.HEALTHY
        assert result.details["connections"] == 10

    @pytest.mark.asyncio
    async def test_run_all_checks(self):
        """Test running all health checks."""
        health = HealthCheck(version="1.0.0")

        @health.register("check1")
        async def check1():
            return True

        @health.register("check2")
        async def check2():
            return True

        system_health = await health.run_all()
        assert system_health.status == HealthStatus.HEALTHY
        assert len(system_health.checks) == 2
        assert system_health.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_system_health_to_dict(self):
        """Test health status serialization."""
        health = HealthCheck(version="1.0.0")

        @health.register("test")
        async def check():
            return True

        system_health = await health.run_all()
        data = system_health.to_dict()

        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "uptime_seconds" in data
        assert len(data["checks"]) == 1

    @pytest.mark.asyncio
    async def test_health_check_timeout(self):
        """Test health check times out."""
        health = HealthCheck()

        @health.register("slow", timeout=0.01)
        async def slow_check():
            await asyncio.sleep(1.0)
            return True

        result = await health.run_check("slow")
        assert result.status == HealthStatus.UNHEALTHY
        assert "timed out" in result.message


class TestIntegration:
    """Integration tests for resilience patterns."""

    @pytest.mark.asyncio
    async def test_retry_with_circuit_breaker(self):
        """Test combining retry with circuit breaker."""
        call_count = 0

        @circuit_breaker(name="integrated", failure_threshold=5)
        @retry(max_attempts=3, initial_delay=0.01)
        async def flaky_service():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient")
            return "success"

        # Should retry within circuit breaker and succeed on 3rd attempt
        result = await flaky_service()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_with_fallback(self):
        """Test combining timeout with fallback."""

        async def backup():
            return "backup"

        @fallback(backup)
        @timeout(0.01)
        async def slow_service():
            await asyncio.sleep(1.0)
            return "primary"

        result = await slow_service()
        assert result == "backup"
