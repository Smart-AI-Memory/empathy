"""Tests for src/empathy_os/resilience/timeout.py

Comprehensive tests for the timeout decorator and with_timeout utility.
"""

import asyncio
import platform
from unittest.mock import patch

import pytest

from empathy_os.resilience.timeout import TimeoutError, timeout, with_timeout


class TestTimeoutError:
    """Tests for the TimeoutError exception class."""

    def test_timeout_error_stores_operation(self):
        """TimeoutError should store the operation name."""
        error = TimeoutError("test_operation", 5.0)
        assert error.operation == "test_operation"

    def test_timeout_error_stores_timeout_value(self):
        """TimeoutError should store the timeout value."""
        error = TimeoutError("test_operation", 30.5)
        assert error.timeout == 30.5

    def test_timeout_error_message_format(self):
        """TimeoutError should have a descriptive error message."""
        error = TimeoutError("slow_query", 10.0)
        assert str(error) == "Operation 'slow_query' timed out after 10.0s"

    def test_timeout_error_inherits_from_exception(self):
        """TimeoutError should be a proper Exception subclass."""
        error = TimeoutError("op", 1.0)
        assert isinstance(error, Exception)


class TestTimeoutDecoratorAsync:
    """Tests for the timeout decorator with async functions."""

    @pytest.mark.asyncio
    async def test_async_function_completes_within_timeout(self):
        """Async function should return normally when completing within timeout."""

        @timeout(5.0)
        async def fast_operation():
            await asyncio.sleep(0.01)
            return "success"

        result = await fast_operation()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_async_function_raises_timeout_error_when_exceeds_limit(self):
        """Async function should raise TimeoutError when exceeding timeout limit."""

        @timeout(0.05)
        async def slow_operation():
            await asyncio.sleep(1.0)
            return "never returned"

        with pytest.raises(TimeoutError) as exc_info:
            await slow_operation()

        assert exc_info.value.timeout == 0.05
        assert exc_info.value.operation == "slow_operation"

    @pytest.mark.asyncio
    async def test_async_function_with_custom_error_message(self):
        """Timeout decorator should use custom error message when provided."""

        @timeout(0.05, error_message="Custom operation description")
        async def slow_operation():
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError) as exc_info:
            await slow_operation()

        assert exc_info.value.operation == "Custom operation description"

    @pytest.mark.asyncio
    async def test_async_function_with_sync_fallback(self):
        """Timeout decorator should use sync fallback when timeout occurs."""

        def fallback_fn():
            return "fallback_value"

        @timeout(0.05, fallback=fallback_fn)
        async def slow_operation():
            await asyncio.sleep(1.0)
            return "success"

        result = await slow_operation()
        assert result == "fallback_value"

    @pytest.mark.asyncio
    async def test_async_function_with_async_fallback(self):
        """Timeout decorator should use async fallback when timeout occurs."""

        async def async_fallback_fn():
            return "async_fallback_value"

        @timeout(0.05, fallback=async_fallback_fn)
        async def slow_operation():
            await asyncio.sleep(1.0)
            return "success"

        result = await slow_operation()
        assert result == "async_fallback_value"

    @pytest.mark.asyncio
    async def test_async_function_fallback_receives_args(self):
        """Fallback function should receive the same arguments as the decorated function."""
        received_args = []

        async def fallback_fn(*args, **kwargs):
            received_args.extend(args)
            received_args.append(kwargs)
            return "fallback"

        @timeout(0.05, fallback=fallback_fn)
        async def slow_operation(a, b, c=None):
            await asyncio.sleep(1.0)
            return "success"

        result = await slow_operation(1, 2, c=3)
        assert result == "fallback"
        assert received_args == [1, 2, {"c": 3}]

    @pytest.mark.asyncio
    async def test_async_function_preserves_function_name(self):
        """Timeout decorator should preserve the original function name."""

        @timeout(5.0)
        async def my_special_function():
            return "value"

        assert my_special_function.__name__ == "my_special_function"

    @pytest.mark.asyncio
    async def test_async_function_preserves_docstring(self):
        """Timeout decorator should preserve the original function docstring."""

        @timeout(5.0)
        async def documented_function():
            """This is the docstring."""
            return "value"

        assert documented_function.__doc__ == "This is the docstring."

    @pytest.mark.asyncio
    async def test_async_function_with_return_value(self):
        """Timeout decorator should pass through return values correctly."""

        @timeout(5.0)
        async def return_dict():
            return {"key": "value", "number": 42}

        result = await return_dict()
        assert result == {"key": "value", "number": 42}

    @pytest.mark.asyncio
    async def test_async_function_propagates_exceptions(self):
        """Timeout decorator should propagate non-timeout exceptions."""

        @timeout(5.0)
        async def raises_error():
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError, match="Something went wrong"):
            await raises_error()


class TestTimeoutDecoratorSync:
    """Tests for the timeout decorator with sync functions."""

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Sync timeout uses SIGALRM which is not available on Windows",
    )
    def test_sync_function_completes_within_timeout(self):
        """Sync function should return normally when completing within timeout."""

        @timeout(5.0)
        def fast_operation():
            return "success"

        result = fast_operation()
        assert result == "success"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Sync timeout uses SIGALRM which is not available on Windows",
    )
    def test_sync_function_raises_timeout_error_when_exceeds_limit(self):
        """Sync function should raise TimeoutError when exceeding timeout limit."""
        import time

        @timeout(0.1)
        def slow_operation():
            time.sleep(1.0)
            return "never returned"

        with pytest.raises(TimeoutError):
            slow_operation()

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Sync timeout uses SIGALRM which is not available on Windows",
    )
    def test_sync_function_with_fallback(self):
        """Sync function should use fallback when timeout occurs."""
        import time

        def fallback_fn():
            return "fallback_value"

        @timeout(0.1, fallback=fallback_fn)
        def slow_operation():
            time.sleep(1.0)
            return "success"

        result = slow_operation()
        assert result == "fallback_value"

    def test_sync_function_on_windows_runs_without_timeout(self):
        """On Windows, sync functions should run without timeout enforcement."""
        with patch("platform.system", return_value="Windows"):

            @timeout(0.01)
            def operation():
                return "completed"

            result = operation()
            assert result == "completed"

    def test_sync_function_preserves_function_metadata(self):
        """Timeout decorator should preserve sync function metadata."""

        @timeout(5.0)
        def my_sync_function():
            """Sync function docstring."""
            return "value"

        assert my_sync_function.__name__ == "my_sync_function"
        assert my_sync_function.__doc__ == "Sync function docstring."


class TestWithTimeoutFunction:
    """Tests for the with_timeout utility function."""

    @pytest.mark.asyncio
    async def test_with_timeout_returns_result_on_success(self):
        """with_timeout should return coroutine result when completing in time."""

        async def quick_coro():
            await asyncio.sleep(0.01)
            return "result"

        result = await with_timeout(quick_coro(), 5.0)
        assert result == "result"

    @pytest.mark.asyncio
    async def test_with_timeout_raises_error_on_timeout(self):
        """with_timeout should raise TimeoutError when coroutine times out."""

        async def slow_coro():
            await asyncio.sleep(1.0)
            return "never returned"

        with pytest.raises(TimeoutError) as exc_info:
            await with_timeout(slow_coro(), 0.05)

        assert exc_info.value.operation == "coroutine"
        assert exc_info.value.timeout == 0.05

    @pytest.mark.asyncio
    async def test_with_timeout_returns_fallback_value_on_timeout(self):
        """with_timeout should return fallback_value when timeout occurs and fallback is provided."""

        async def slow_coro():
            await asyncio.sleep(1.0)
            return "never returned"

        result = await with_timeout(slow_coro(), 0.05, fallback_value="default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_with_timeout_fallback_value_none_raises_error(self):
        """with_timeout should raise error when fallback_value is None (default)."""

        async def slow_coro():
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError):
            await with_timeout(slow_coro(), 0.05, fallback_value=None)

    @pytest.mark.asyncio
    async def test_with_timeout_fallback_empty_dict(self):
        """with_timeout should support empty dict as fallback value."""

        async def slow_coro():
            await asyncio.sleep(1.0)
            return {"data": "value"}

        result = await with_timeout(slow_coro(), 0.05, fallback_value={})
        assert result == {}

    @pytest.mark.asyncio
    async def test_with_timeout_fallback_empty_list(self):
        """with_timeout should support empty list as fallback value."""

        async def slow_coro():
            await asyncio.sleep(1.0)
            return [1, 2, 3]

        result = await with_timeout(slow_coro(), 0.05, fallback_value=[])
        assert result == []

    @pytest.mark.asyncio
    async def test_with_timeout_propagates_exceptions(self):
        """with_timeout should propagate non-timeout exceptions from coroutine."""

        async def error_coro():
            raise RuntimeError("Coroutine failed")

        with pytest.raises(RuntimeError, match="Coroutine failed"):
            await with_timeout(error_coro(), 5.0)

    @pytest.mark.asyncio
    async def test_with_timeout_with_complex_return_type(self):
        """with_timeout should handle complex return types correctly."""

        async def complex_coro():
            return {"users": [{"id": 1}, {"id": 2}], "count": 2}

        result = await with_timeout(complex_coro(), 5.0)
        assert result == {"users": [{"id": 1}, {"id": 2}], "count": 2}


class TestTimeoutEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_timeout_with_zero_seconds(self):
        """Timeout of 0 seconds should immediately timeout."""

        @timeout(0)
        async def any_operation():
            return "value"

        # A timeout of 0 should cause immediate timeout
        with pytest.raises(TimeoutError):
            await any_operation()

    @pytest.mark.asyncio
    async def test_timeout_with_very_small_value(self):
        """Very small timeout should still work correctly."""

        @timeout(0.001)
        async def quick_operation():
            return "quick"

        # This might complete or timeout depending on system load
        # The important thing is it doesn't hang or crash
        try:
            result = await quick_operation()
            assert result == "quick"
        except TimeoutError:
            pass  # Also acceptable

    @pytest.mark.asyncio
    async def test_timeout_with_large_value(self):
        """Large timeout value should work without issues."""

        @timeout(3600.0)  # 1 hour
        async def operation():
            return "completed"

        result = await operation()
        assert result == "completed"

    @pytest.mark.asyncio
    async def test_multiple_timeout_decorators_independent(self):
        """Multiple decorated functions should have independent timeouts."""

        @timeout(0.05)
        async def short_timeout():
            await asyncio.sleep(0.01)
            return "short"

        @timeout(5.0)
        async def long_timeout():
            await asyncio.sleep(0.01)
            return "long"

        result1 = await short_timeout()
        result2 = await long_timeout()

        assert result1 == "short"
        assert result2 == "long"

    @pytest.mark.asyncio
    async def test_timeout_with_cancellation(self):
        """Cancelled tasks should handle timeout cleanup properly."""

        @timeout(5.0)
        async def cancellable_operation():
            await asyncio.sleep(10.0)
            return "never"

        task = asyncio.create_task(cancellable_operation())
        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task


class TestTimeoutLogging:
    """Tests for timeout logging behavior."""

    @pytest.mark.asyncio
    async def test_timeout_logs_warning_on_timeout(self, caplog):
        """Timeout should log a warning when operation times out."""
        import logging

        with caplog.at_level(logging.WARNING):

            @timeout(0.05)
            async def slow_operation():
                await asyncio.sleep(1.0)

            with pytest.raises(TimeoutError):
                await slow_operation()

            # Check that a warning was logged about the timeout
            assert any(
                "0.05" in record.message or "Timeout" in record.message for record in caplog.records
            )

    @pytest.mark.asyncio
    async def test_timeout_logs_info_when_using_fallback(self, caplog):
        """Timeout should log info when fallback is used."""
        import logging

        with caplog.at_level(logging.INFO):

            @timeout(0.05, fallback=lambda: "default")
            async def slow_operation():
                await asyncio.sleep(1.0)

            await slow_operation()

            # Check that an info log was recorded about fallback
            assert any("fallback" in record.message.lower() for record in caplog.records)


class TestTimeoutIntegration:
    """Integration tests for timeout functionality."""

    @pytest.mark.asyncio
    async def test_timeout_with_real_async_io_operation(self):
        """Timeout should work with real async I/O-like operations."""

        @timeout(5.0)
        async def simulated_io():
            # Simulate gathering data from multiple sources
            results = await asyncio.gather(
                asyncio.sleep(0.01),
                asyncio.sleep(0.01),
                asyncio.sleep(0.01),
            )
            return len(results)

        result = await simulated_io()
        assert result == 3

    @pytest.mark.asyncio
    async def test_chained_with_timeout_calls(self):
        """Multiple with_timeout calls should work in sequence."""

        async def step1():
            await asyncio.sleep(0.01)
            return 1

        async def step2():
            await asyncio.sleep(0.01)
            return 2

        async def step3():
            await asyncio.sleep(0.01)
            return 3

        results = []
        results.append(await with_timeout(step1(), 5.0))
        results.append(await with_timeout(step2(), 5.0))
        results.append(await with_timeout(step3(), 5.0))

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_timeout_preserves_exception_traceback(self):
        """TimeoutError should have proper traceback information."""

        @timeout(0.05)
        async def slow_operation():
            await asyncio.sleep(1.0)

        try:
            await slow_operation()
            pytest.fail("Should have raised TimeoutError")
        except TimeoutError as e:
            # Verify exception has proper attributes
            assert hasattr(e, "operation")
            assert hasattr(e, "timeout")
            assert e.__traceback__ is not None
