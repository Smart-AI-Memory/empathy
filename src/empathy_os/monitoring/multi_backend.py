"""Multi-Backend Telemetry Support

Enables simultaneous logging to multiple backends (JSONL + OTEL).

**Features:**
- Composite pattern for multiple backends
- Parallel writes to all configured backends
- Graceful handling of backend failures
- Automatic backend selection based on configuration

**Example:**
```python
from empathy_os.monitoring import TelemetryStore
from empathy_os.monitoring.otel_backend import OTELBackend
from empathy_os.monitoring.multi_backend import MultiBackend

# Create composite backend
backends = [
    TelemetryStore(),           # JSONL (always enabled)
    OTELBackend(),              # OTEL (if configured)
]
multi = MultiBackend(backends)

# Logs to both backends
multi.log_call(record)
```

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from typing import Protocol, runtime_checkable

from empathy_os.models.telemetry import LLMCallRecord, TelemetryStore, WorkflowRunRecord


@runtime_checkable
class TelemetryBackend(Protocol):
    """Protocol for telemetry storage backends.

    All backends must implement log_call() and log_workflow().
    """

    def log_call(self, record: LLMCallRecord) -> None:
        """Log an LLM call record."""
        ...

    def log_workflow(self, record: WorkflowRunRecord) -> None:
        """Log a workflow run record."""
        ...


class MultiBackend:
    """Composite backend for simultaneous logging to multiple backends.

    Implements the TelemetryBackend protocol and forwards calls to all
    configured backends. Handles failures gracefully - if one backend
    fails, others continue to work.

    **Auto-Configuration:**
    - JSONL backend is always enabled (default)
    - OTEL backend is enabled if EMPATHY_OTEL_ENDPOINT is set

    Example:
        >>> backend = MultiBackend.from_config()
        >>> backend.log_call(call_record)  # Logs to JSONL + OTEL
        >>> backend.log_workflow(workflow_record)
    """

    def __init__(self, backends: list[TelemetryBackend] | None = None):
        """Initialize multi-backend.

        Args:
            backends: List of backend instances (default: auto-detect)
        """
        self.backends = backends or []
        self._failed_backends: set[int] = set()

    @classmethod
    def from_config(cls, storage_dir: str = ".empathy") -> "MultiBackend":
        """Create multi-backend from configuration.

        Auto-detects available backends:
        1. JSONL backend (always enabled)
        2. OTEL backend (if EMPATHY_OTEL_ENDPOINT is set or collector detected)

        Args:
            storage_dir: Directory for JSONL storage (default: .empathy)

        Returns:
            MultiBackend instance with all available backends
        """
        backends: list[TelemetryBackend] = []

        # Always add JSONL backend
        try:
            jsonl_backend = TelemetryStore(storage_dir)
            backends.append(jsonl_backend)
        except Exception as e:
            print(f"⚠️  Failed to initialize JSONL backend: {e}")

        # Add OTEL backend if configured
        try:
            from empathy_os.monitoring.otel_backend import OTELBackend

            otel_backend = OTELBackend()
            if otel_backend.is_available():
                backends.append(otel_backend)
        except ImportError:
            # OTEL dependencies not installed
            pass
        except Exception as e:
            print(f"⚠️  Failed to initialize OTEL backend: {e}")

        return cls(backends)

    def add_backend(self, backend: TelemetryBackend) -> None:
        """Add a backend to the multi-backend.

        Args:
            backend: Backend instance to add
        """
        if isinstance(backend, TelemetryBackend):
            self.backends.append(backend)
        else:
            raise TypeError(
                f"Backend must implement TelemetryBackend protocol, got {type(backend)}"
            )

    def remove_backend(self, backend: TelemetryBackend) -> None:
        """Remove a backend from the multi-backend.

        Args:
            backend: Backend instance to remove
        """
        if backend in self.backends:
            self.backends.remove(backend)

    def log_call(self, record: LLMCallRecord) -> None:
        """Log an LLM call record to all backends.

        Failures in individual backends are logged but don't affect other backends.

        Args:
            record: LLM call record to log
        """
        for i, backend in enumerate(self.backends):
            if i in self._failed_backends:
                # Skip backends that have failed before
                continue

            try:
                backend.log_call(record)
            except Exception as e:
                backend_name = type(backend).__name__
                print(f"⚠️  Failed to log call to {backend_name}: {e}")
                # Mark backend as failed to reduce log spam
                self._failed_backends.add(i)

    def log_workflow(self, record: WorkflowRunRecord) -> None:
        """Log a workflow run record to all backends.

        Failures in individual backends are logged but don't affect other backends.

        Args:
            record: Workflow run record to log
        """
        for i, backend in enumerate(self.backends):
            if i in self._failed_backends:
                # Skip backends that have failed before
                continue

            try:
                backend.log_workflow(record)
            except Exception as e:
                backend_name = type(backend).__name__
                print(f"⚠️  Failed to log workflow to {backend_name}: {e}")
                # Mark backend as failed to reduce log spam
                self._failed_backends.add(i)

    def get_active_backends(self) -> list[str]:
        """Get list of active backend names.

        Returns:
            List of backend class names that are active (not failed)
        """
        return [
            type(backend).__name__
            for i, backend in enumerate(self.backends)
            if i not in self._failed_backends
        ]

    def get_failed_backends(self) -> list[str]:
        """Get list of failed backend names.

        Returns:
            List of backend class names that have failed
        """
        return [
            type(self.backends[i]).__name__ for i in self._failed_backends if i < len(self.backends)
        ]

    def reset_failures(self) -> None:
        """Reset failed backend tracking.

        Allows retry of previously failed backends.
        """
        self._failed_backends.clear()

    def flush(self) -> None:
        """Flush all backends.

        Calls flush() on backends that support it (e.g., OTEL backend).
        """
        for backend in self.backends:
            if hasattr(backend, "flush"):
                try:
                    backend.flush()
                except Exception as e:
                    backend_name = type(backend).__name__
                    print(f"⚠️  Failed to flush {backend_name}: {e}")

    def __len__(self) -> int:
        """Return number of active backends."""
        return len(self.backends) - len(self._failed_backends)

    def __repr__(self) -> str:
        """String representation."""
        active = self.get_active_backends()
        failed = self.get_failed_backends()
        status = f"active={active}"
        if failed:
            status += f", failed={failed}"
        return f"MultiBackend({status})"


# Singleton instance for global access
_global_backend: MultiBackend | None = None


def get_multi_backend(storage_dir: str = ".empathy") -> MultiBackend:
    """Get or create the global multi-backend instance.

    This is the recommended way to get a multi-backend instance.
    It ensures a single instance is shared across the application.

    Args:
        storage_dir: Directory for JSONL storage (default: .empathy)

    Returns:
        Global MultiBackend instance

    Example:
        >>> backend = get_multi_backend()
        >>> backend.log_call(record)
    """
    global _global_backend
    if _global_backend is None:
        _global_backend = MultiBackend.from_config(storage_dir)
    return _global_backend


def reset_multi_backend() -> None:
    """Reset the global multi-backend instance.

    Useful for testing or reconfiguration.
    """
    global _global_backend
    if _global_backend is not None:
        _global_backend.flush()
    _global_backend = None
