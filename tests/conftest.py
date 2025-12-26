"""
Shared Pytest Fixtures for Empathy Framework Tests

Provides common fixtures used across test modules:
- Mock executors and circuit breakers
- Telemetry stores
- Workflow configurations

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_os.models import MockLLMExecutor
from empathy_os.models.fallback import CircuitBreaker, ResilientExecutor, RetryPolicy
from empathy_os.models.telemetry import TelemetryStore


@pytest.fixture
def mock_executor():
    """Create a mock executor with default response."""
    return MockLLMExecutor(default_response="Test response")


@pytest.fixture
def circuit_breaker():
    """Create a circuit breaker with test-friendly settings."""
    return CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=1)


@pytest.fixture
def retry_policy():
    """Create a retry policy with fast delays for testing."""
    return RetryPolicy(max_retries=2, initial_delay_ms=10)


@pytest.fixture
def resilient_executor(mock_executor, circuit_breaker, retry_policy):
    """Create a resilient executor wrapping a mock executor."""
    return ResilientExecutor(
        executor=mock_executor,
        circuit_breaker=circuit_breaker,
        retry_policy=retry_policy,
    )


@pytest.fixture
def telemetry_store(tmp_path):
    """Create a telemetry store in a temporary directory."""
    return TelemetryStore(storage_dir=tmp_path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_code():
    """Sample Python code for testing code review workflows."""
    return '''
def calculate_total(items: list[dict]) -> float:
    """Calculate the total price of items."""
    total = 0.0
    for item in items:
        price = item.get("price", 0)
        quantity = item.get("quantity", 1)
        total += price * quantity
    return total


class ShoppingCart:
    """Shopping cart with item management."""

    def __init__(self):
        self.items = []

    def add_item(self, item: dict) -> None:
        self.items.append(item)

    def get_total(self) -> float:
        return calculate_total(self.items)
'''


@pytest.fixture
def sample_diff():
    """Sample git diff for testing code review workflows."""
    return """
diff --git a/src/cart.py b/src/cart.py
index 1234567..abcdefg 100644
--- a/src/cart.py
+++ b/src/cart.py
@@ -10,6 +10,12 @@ class ShoppingCart:
     def add_item(self, item: dict) -> None:
         self.items.append(item)

+    def remove_item(self, item_id: str) -> bool:
+        for i, item in enumerate(self.items):
+            if item.get("id") == item_id:
+                del self.items[i]
+                return True
+        return False
+
     def get_total(self) -> float:
         return calculate_total(self.items)
"""


@pytest.fixture
def workflow_config():
    """Default workflow configuration for testing."""
    return {
        "provider": "anthropic",
        "enable_xml_prompts": False,
        "skip_expensive_stages": True,
    }
