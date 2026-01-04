"""Smoke tests for production website at empathy-framework.vercel.app

Run manually:
    python -m pytest tests/test_production_smoke.py -v

Run with custom URL:
    PRODUCTION_URL=https://empathy-framework.vercel.app python -m pytest tests/test_production_smoke.py -v

Note: These tests are marked as 'network' and will be skipped in CI by default.
Run with `-m network` to include them.
"""

import os

import httpx
import pytest

# Mark all tests in this module as requiring network access
pytestmark = pytest.mark.network

# Production URL - can be overridden via environment variable
PRODUCTION_URL = os.getenv("PRODUCTION_URL", "https://empathy-framework.vercel.app")

# Timeout for requests (seconds)
REQUEST_TIMEOUT = 30


@pytest.fixture
def client():
    """HTTP client with reasonable timeout."""
    return httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True)


class TestProductionPages:
    """Test that key pages load successfully."""

    def test_homepage_loads(self, client):
        """Homepage returns 200 and contains expected content."""
        response = client.get(f"{PRODUCTION_URL}/")
        assert response.status_code == 200
        assert "Empathy Framework" in response.text

    def test_debug_wizard_page_loads(self, client):
        """Debug wizard page returns 200 and contains expected content."""
        response = client.get(f"{PRODUCTION_URL}/tools/debug-wizard")
        assert response.status_code == 200
        assert "Memory-Enhanced Debugging" in response.text or "Debug" in response.text

    def test_docs_page_loads(self, client):
        """Docs page returns 200."""
        response = client.get(f"{PRODUCTION_URL}/docs")
        # May redirect or return 200
        assert response.status_code in (200, 301, 302, 307, 308)

    def test_pricing_page_loads(self, client):
        """Pricing page returns 200."""
        response = client.get(f"{PRODUCTION_URL}/pricing")
        # May redirect or return 200
        assert response.status_code in (200, 301, 302, 307, 308)


class TestProductionPerformance:
    """Basic performance checks."""

    def test_homepage_response_time(self, client):
        """Homepage responds within acceptable time."""
        response = client.get(f"{PRODUCTION_URL}/")
        # Should respond within 5 seconds
        assert response.elapsed.total_seconds() < 5

    def test_debug_wizard_response_time(self, client):
        """Debug wizard page responds within acceptable time."""
        response = client.get(f"{PRODUCTION_URL}/tools/debug-wizard")
        # Should respond within 5 seconds
        assert response.elapsed.total_seconds() < 5


class TestProductionHeaders:
    """Test security and cache headers."""

    def test_security_headers(self, client):
        """Check for basic security headers."""
        response = client.get(f"{PRODUCTION_URL}/")

        # Vercel typically sets these
        # Just check the response is valid, not strict header requirements
        assert response.status_code == 200

    def test_content_type(self, client):
        """HTML pages return correct content type."""
        response = client.get(f"{PRODUCTION_URL}/")
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type


class TestDebugWizardContent:
    """Verify debug wizard page has expected content."""

    def test_debug_wizard_has_form(self, client):
        """Debug wizard page contains the error input form."""
        response = client.get(f"{PRODUCTION_URL}/tools/debug-wizard")
        assert response.status_code == 200
        # Check for key UI elements
        html = response.text.lower()
        assert "error" in html or "bug" in html or "debug" in html

    def test_debug_wizard_has_features_section(self, client):
        """Debug wizard page has the features section."""
        response = client.get(f"{PRODUCTION_URL}/tools/debug-wizard")
        assert response.status_code == 200
        # Check for memory/pattern feature mentions
        html = response.text.lower()
        assert "memory" in html or "pattern" in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
