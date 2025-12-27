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


# =============================================================================
# Integration Test Fixtures - Mock LLM Responses
# =============================================================================


@pytest.fixture
def mock_llm_responses():
    """
    Configurable mock LLM responses for integration testing.

    Usage:
        def test_something(mock_llm_responses):
            mock_llm_responses["security_scan"] = "No vulnerabilities found"
            # Run workflow...
    """
    return {
        # Code review responses
        "classify": "feature: Adding new functionality",
        "security_scan": '{"vulnerabilities": [], "score": 100}',
        "code_analysis": '{"quality_score": 85, "issues": []}',
        "architect_review": "Architecture looks good. No concerns.",
        # Security audit responses
        "identify_vulnerabilities": '{"vulnerabilities": [], "risk_level": "low"}',
        "analyze_risk": '{"overall_risk": "low", "recommendations": []}',
        "generate_report": "# Security Audit Report\n\nNo issues found.",
        # Document generation responses
        "analyze_structure": '{"modules": [], "functions": []}',
        "generate_documentation": "# API Documentation\n\nGenerated docs here.",
        # Health check responses
        "diagnose": '{"health_score": 95, "issues": []}',
        "fix": '{"fixes_applied": 0, "fixes": []}',
        # Generic fallback
        "default": "Task completed successfully.",
    }


@pytest.fixture
def mock_anthropic_client(mock_llm_responses):
    """
    Mock Anthropic client for integration tests.

    Returns deterministic responses based on the prompt content.
    """
    from unittest.mock import MagicMock

    def create_mock_response(prompt: str) -> MagicMock:
        """Create a mock response based on prompt content."""
        response = MagicMock()

        # Determine response based on keywords in prompt
        content = mock_llm_responses["default"]
        for key, value in mock_llm_responses.items():
            if key.lower() in prompt.lower():
                content = value
                break

        response.content = [MagicMock(text=content)]
        response.usage = MagicMock(input_tokens=100, output_tokens=50)
        return response

    client = MagicMock()
    client.messages.create = MagicMock(
        side_effect=lambda **kwargs: create_mock_response(
            kwargs.get("messages", [{}])[-1].get("content", "")
            if isinstance(kwargs.get("messages", [{}])[-1], dict)
            else str(kwargs.get("messages", []))
        )
    )

    return client


@pytest.fixture
def patch_llm_client(mock_anthropic_client):
    """
    Patch the Anthropic client globally for integration tests.

    Usage:
        def test_workflow(patch_llm_client):
            # LLM calls will return mock responses
            result = await workflow.execute(...)
    """
    from unittest.mock import patch

    with patch("anthropic.Anthropic", return_value=mock_anthropic_client):
        yield mock_anthropic_client


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for testing file-based workflows."""
    code = '''"""Sample module for testing."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:
    """Simple calculator class."""

    def __init__(self):
        self.history = []

    def calculate(self, op: str, a: int, b: int) -> float:
        if op == "add":
            result = add(a, b)
        elif op == "divide":
            result = divide(a, b)
        else:
            raise ValueError(f"Unknown operation: {op}")
        self.history.append((op, a, b, result))
        return result
'''
    file_path = temp_dir / "sample.py"
    file_path.write_text(code)
    return file_path


@pytest.fixture
def sample_project_dir(temp_dir):
    """Create a sample project directory structure for testing."""
    # Create src directory
    src_dir = temp_dir / "src"
    src_dir.mkdir()

    # Create main module
    (src_dir / "__init__.py").write_text("")
    (src_dir / "main.py").write_text(
        '''
"""Main application module."""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
    )

    # Create utils module
    (src_dir / "utils.py").write_text(
        '''
"""Utility functions."""

def format_name(first: str, last: str) -> str:
    """Format a full name."""
    return f"{first} {last}"
'''
    )

    # Create tests directory
    tests_dir = temp_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_main.py").write_text(
        '''
"""Tests for main module."""

def test_placeholder():
    assert True
'''
    )

    # Create pyproject.toml
    (temp_dir / "pyproject.toml").write_text(
        """
[project]
name = "sample-project"
version = "0.1.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
    )

    return temp_dir
