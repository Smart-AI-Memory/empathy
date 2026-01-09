"""Tests for Memory Control Panel security features.

Tests cover:
- Input validation (pattern IDs, agent IDs, classifications)
- Rate limiting
- API key authentication

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time

from empathy_os.memory.control_panel import (
    APIKeyAuth,
    RateLimiter,
    _validate_agent_id,
    _validate_classification,
    _validate_pattern_id,
)

# =============================================================================
# Pattern ID Validation Tests
# =============================================================================


class TestValidatePatternId:
    """Tests for _validate_pattern_id function."""

    def test_valid_standard_pattern_id(self):
        """Valid pattern ID in standard format should pass."""
        assert _validate_pattern_id("pat_20251229120000_abcdef12") is True
        assert _validate_pattern_id("pat_20251229120000_abcdef123456") is True

    def test_valid_alternative_pattern_id(self):
        """Valid pattern ID in alternative format should pass."""
        assert _validate_pattern_id("bug_async_001") is True
        assert _validate_pattern_id("pattern_test") is True
        assert _validate_pattern_id("MyPattern123") is True
        assert _validate_pattern_id("test-pattern-name") is True

    def test_empty_pattern_id(self):
        """Empty or None pattern ID should fail."""
        assert _validate_pattern_id("") is False
        assert _validate_pattern_id(None) is False

    def test_path_traversal_attempts(self):
        """Path traversal attempts should fail."""
        assert _validate_pattern_id("../etc/passwd") is False
        assert _validate_pattern_id("..\\windows\\system32") is False
        assert _validate_pattern_id("pattern/../secret") is False
        assert _validate_pattern_id("/etc/passwd") is False
        assert _validate_pattern_id("C:\\Windows") is False

    def test_null_byte_injection(self):
        """Null byte injection should fail."""
        assert _validate_pattern_id("pattern\x00.txt") is False
        assert _validate_pattern_id("\x00malicious") is False

    def test_too_short_pattern_id(self):
        """Pattern ID shorter than 3 chars should fail."""
        assert _validate_pattern_id("ab") is False
        assert _validate_pattern_id("x") is False

    def test_too_long_pattern_id(self):
        """Pattern ID longer than 64 chars should fail."""
        long_id = "a" * 65
        assert _validate_pattern_id(long_id) is False

    def test_boundary_length_pattern_id(self):
        """Pattern ID at boundary lengths should work correctly."""
        assert _validate_pattern_id("abc") is True  # Min length
        assert _validate_pattern_id("a" * 64) is True  # Max length

    def test_invalid_characters(self):
        """Pattern IDs with invalid characters should fail."""
        assert _validate_pattern_id("pattern;rm -rf") is False
        assert _validate_pattern_id("pattern|cat") is False
        assert _validate_pattern_id("pattern&echo") is False

    def test_non_string_input(self):
        """Non-string input should fail."""
        assert _validate_pattern_id(123) is False
        assert _validate_pattern_id(["list"]) is False
        assert _validate_pattern_id({"dict": "value"}) is False


# =============================================================================
# Agent ID Validation Tests
# =============================================================================


class TestValidateAgentId:
    """Tests for _validate_agent_id function."""

    def test_valid_agent_ids(self):
        """Valid agent IDs should pass."""
        assert _validate_agent_id("admin") is True
        assert _validate_agent_id("user123") is True
        assert _validate_agent_id("agent_worker_1") is True
        assert _validate_agent_id("user@example") is True

    def test_empty_agent_id(self):
        """Empty or None agent ID should fail."""
        assert _validate_agent_id("") is False
        assert _validate_agent_id(None) is False

    def test_dangerous_characters(self):
        """Agent IDs with dangerous characters should fail."""
        assert _validate_agent_id("user.name") is False  # dot
        assert _validate_agent_id("user/name") is False  # forward slash
        assert _validate_agent_id("user\\name") is False  # backslash
        assert _validate_agent_id("user;rm") is False  # semicolon
        assert _validate_agent_id("user|cat") is False  # pipe
        assert _validate_agent_id("user&echo") is False  # ampersand

    def test_null_byte_injection(self):
        """Null byte injection should fail."""
        assert _validate_agent_id("user\x00admin") is False

    def test_too_long_agent_id(self):
        """Agent ID longer than 64 chars should fail."""
        long_id = "a" * 65
        assert _validate_agent_id(long_id) is False

    def test_boundary_length_agent_id(self):
        """Agent ID at boundary lengths should work correctly."""
        assert _validate_agent_id("a") is True  # Min length
        assert _validate_agent_id("a" * 64) is True  # Max length

    def test_non_string_input(self):
        """Non-string input should fail."""
        assert _validate_agent_id(123) is False
        assert _validate_agent_id(["list"]) is False


# =============================================================================
# Classification Validation Tests
# =============================================================================


class TestValidateClassification:
    """Tests for _validate_classification function."""

    def test_valid_classifications(self):
        """Valid classifications should pass."""
        assert _validate_classification("PUBLIC") is True
        assert _validate_classification("INTERNAL") is True
        assert _validate_classification("SENSITIVE") is True

    def test_case_insensitive(self):
        """Classification should be case-insensitive."""
        assert _validate_classification("public") is True
        assert _validate_classification("Public") is True
        assert _validate_classification("internal") is True
        assert _validate_classification("sensitive") is True

    def test_none_classification(self):
        """None classification should be valid (no filter)."""
        assert _validate_classification(None) is True

    def test_invalid_classification(self):
        """Invalid classifications should fail."""
        assert _validate_classification("INVALID") is False
        assert _validate_classification("SECRET") is False
        assert _validate_classification("TOP_SECRET") is False
        assert _validate_classification("") is False

    def test_non_string_input(self):
        """Non-string input (except None) should fail."""
        assert _validate_classification(123) is False
        assert _validate_classification(["PUBLIC"]) is False


# =============================================================================
# Rate Limiter Tests
# =============================================================================


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allows_requests_under_limit(self):
        """Requests under the limit should be allowed."""
        limiter = RateLimiter(window_seconds=60, max_requests=10)

        for _ in range(10):
            assert limiter.is_allowed("127.0.0.1") is True

    def test_blocks_requests_over_limit(self):
        """Requests over the limit should be blocked."""
        limiter = RateLimiter(window_seconds=60, max_requests=5)

        # Use up the limit
        for _ in range(5):
            assert limiter.is_allowed("127.0.0.1") is True

        # Next request should be blocked
        assert limiter.is_allowed("127.0.0.1") is False

    def test_separate_limits_per_ip(self):
        """Each IP should have its own limit."""
        limiter = RateLimiter(window_seconds=60, max_requests=2)

        # IP 1 uses its limit
        assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is False

        # IP 2 should still have its full limit
        assert limiter.is_allowed("192.168.1.2") is True
        assert limiter.is_allowed("192.168.1.2") is True

    def test_get_remaining_requests(self):
        """get_remaining should return correct count."""
        limiter = RateLimiter(window_seconds=60, max_requests=10)

        assert limiter.get_remaining("127.0.0.1") == 10

        limiter.is_allowed("127.0.0.1")
        assert limiter.get_remaining("127.0.0.1") == 9

        limiter.is_allowed("127.0.0.1")
        limiter.is_allowed("127.0.0.1")
        assert limiter.get_remaining("127.0.0.1") == 7

    def test_window_expiration(self):
        """Requests should be allowed again after window expires."""
        limiter = RateLimiter(window_seconds=1, max_requests=2)

        # Use up the limit
        assert limiter.is_allowed("127.0.0.1") is True
        assert limiter.is_allowed("127.0.0.1") is True
        assert limiter.is_allowed("127.0.0.1") is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.is_allowed("127.0.0.1") is True

    def test_default_values(self):
        """Default values should be sensible."""
        limiter = RateLimiter()
        assert limiter.window_seconds == 60
        assert limiter.max_requests == 100


# =============================================================================
# API Key Authentication Tests
# =============================================================================


class TestAPIKeyAuth:
    """Tests for APIKeyAuth class."""

    def test_auth_disabled_when_no_key(self):
        """Auth should be disabled when no key is provided."""
        auth = APIKeyAuth(api_key=None)
        assert auth.enabled is False
        assert auth.is_valid(None) is True
        assert auth.is_valid("any-key") is True

    def test_auth_enabled_when_key_provided(self):
        """Auth should be enabled when key is provided."""
        auth = APIKeyAuth(api_key="secret-key-123")
        assert auth.enabled is True

    def test_valid_key_accepted(self):
        """Valid API key should be accepted."""
        auth = APIKeyAuth(api_key="my-secret-key")
        assert auth.is_valid("my-secret-key") is True

    def test_invalid_key_rejected(self):
        """Invalid API key should be rejected."""
        auth = APIKeyAuth(api_key="my-secret-key")
        assert auth.is_valid("wrong-key") is False
        assert auth.is_valid("MY-SECRET-KEY") is False  # Case sensitive
        assert auth.is_valid("") is False
        assert auth.is_valid(None) is False

    def test_key_from_environment(self, monkeypatch):
        """API key should be read from environment variable."""
        monkeypatch.setenv("EMPATHY_MEMORY_API_KEY", "env-secret-key")

        auth = APIKeyAuth()  # No key provided, should read from env
        assert auth.enabled is True
        assert auth.is_valid("env-secret-key") is True
        assert auth.is_valid("wrong-key") is False

    def test_explicit_key_overrides_env(self, monkeypatch):
        """Explicit key should override environment variable."""
        monkeypatch.setenv("EMPATHY_MEMORY_API_KEY", "env-key")

        auth = APIKeyAuth(api_key="explicit-key")
        assert auth.is_valid("explicit-key") is True
        assert auth.is_valid("env-key") is False

    def test_constant_time_comparison(self):
        """Key comparison should use constant-time algorithm (hash-based)."""
        auth = APIKeyAuth(api_key="test-key")

        # This tests that the implementation uses hashing
        # The internal _key_hash should be set
        assert auth._key_hash is not None
        assert len(auth._key_hash) == 64  # SHA-256 produces 64 hex chars


# =============================================================================
# Integration Tests
# =============================================================================


class TestSecurityIntegration:
    """Integration tests for security features working together."""

    def test_rate_limiter_with_valid_auth(self):
        """Rate limiter should work independently of auth."""
        auth = APIKeyAuth(api_key="secret")
        limiter = RateLimiter(window_seconds=60, max_requests=3)

        # Valid auth, within rate limit
        assert auth.is_valid("secret") is True
        assert limiter.is_allowed("127.0.0.1") is True

        # Valid auth, but rate limited
        limiter.is_allowed("127.0.0.1")
        limiter.is_allowed("127.0.0.1")
        assert limiter.is_allowed("127.0.0.1") is False

    def test_validation_before_processing(self):
        """Input validation should catch malicious inputs."""
        malicious_inputs = [
            "../../../etc/passwd",
            "pattern\x00.json",
            "admin; DROP TABLE patterns;",
            "a" * 100,
        ]

        for malicious in malicious_inputs:
            assert _validate_pattern_id(malicious) is False
            # Agent ID validation should also catch these
            assert _validate_agent_id(malicious) is False
