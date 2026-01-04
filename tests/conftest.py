"""Pytest configuration for Empathy Framework tests."""

import pytest


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add ini settings dynamically based on markers
    config.addinivalue_line("markers", "unit: Unit tests that import and test modules directly")
    config.addinivalue_line(
        "markers",
        "integration: Integration tests that run via subprocess (no coverage)",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle coverage properly."""
    # If running with coverage, only run unit tests unless explicitly requested
    if config.option.cov_source and not config.option.markexpr:
        skip_integration = pytest.mark.skip(reason="Integration tests don't provide coverage")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
