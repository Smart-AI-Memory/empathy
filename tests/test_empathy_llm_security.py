"""
Unit tests for EmpathyLLM Phase 3 Security Integration

Tests the integration of Phase 2 security controls (PII scrubbing, secrets detection,
audit logging) into the core EmpathyLLM.interact() method.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empathy_llm_toolkit.core import EmpathyLLM
from empathy_llm_toolkit.security import SecurityError

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_provider_response():
    """Create mock provider response"""
    response = MagicMock()
    response.content = "Mock LLM response"
    response.model = "claude-test"
    response.tokens_used = 100
    return response


@pytest.fixture
def mock_provider(mock_provider_response):
    """Create mock LLM provider"""
    provider = AsyncMock()
    provider.generate = AsyncMock(return_value=mock_provider_response)
    return provider


@pytest.fixture
def temp_audit_dir():
    """Create temporary directory for audit logs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ============================================================================
# Initialization Tests
# ============================================================================


def test_empathy_llm_security_disabled_by_default():
    """Test that security is disabled by default (backward compatibility)"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        assert llm.enable_security is False
        assert llm.pii_scrubber is None
        assert llm.secrets_detector is None
        assert llm.audit_logger is None


def test_empathy_llm_security_enabled():
    """Test that security modules are initialized when enabled"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = EmpathyLLM(
                provider="anthropic",
                enable_security=True,
                security_config={"audit_log_dir": tmpdir},
            )

            assert llm.enable_security is True
            assert llm.pii_scrubber is not None
            assert llm.secrets_detector is not None
            assert llm.audit_logger is not None


def test_empathy_llm_security_custom_config():
    """Test security with custom configuration"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        with tempfile.TemporaryDirectory() as tmpdir:
            security_config = {
                "audit_log_dir": tmpdir,
                "block_on_secrets": False,
                "enable_pii_scrubbing": True,
                "enable_name_detection": True,
                "enable_audit_logging": True,
            }

            llm = EmpathyLLM(
                provider="anthropic", enable_security=True, security_config=security_config
            )

            assert llm.enable_security is True
            assert llm.security_config == security_config
            # PII scrubber should be initialized with name detection enabled
            assert llm.pii_scrubber is not None


def test_empathy_llm_security_pii_scrubbing_disabled():
    """Test security with PII scrubbing disabled"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        with tempfile.TemporaryDirectory() as tmpdir:
            security_config = {
                "audit_log_dir": tmpdir,
                "enable_pii_scrubbing": False,
            }

            llm = EmpathyLLM(
                provider="anthropic", enable_security=True, security_config=security_config
            )

            assert llm.enable_security is True
            assert llm.pii_scrubber is None  # Should be None when disabled
            assert llm.secrets_detector is not None  # Still initialized


# ============================================================================
# PII Scrubbing Tests
# ============================================================================


@pytest.mark.asyncio
async def test_interact_with_pii_scrubbing(mock_provider, temp_audit_dir):
    """Test that PII is scrubbed from user input before LLM call"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        # Input contains email and phone number
        user_input = "Contact me at john.doe@example.com or call 555-123-4567"

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Should return successful response
        assert result["content"] == "Mock LLM response"
        assert result["level_used"] == 1

        # Check security metadata
        assert "security" in result
        assert result["security"]["pii_detected"] > 0
        assert result["security"]["pii_scrubbed"] is True

        # Verify the provider was called with sanitized input
        mock_provider.generate.assert_called_once()
        call_args = mock_provider.generate.call_args
        messages = call_args[1]["messages"]
        sanitized_content = messages[0]["content"]

        # Sanitized content should have PII replaced
        assert "john.doe@example.com" not in sanitized_content
        assert "555-123-4567" not in sanitized_content
        assert "[EMAIL]" in sanitized_content
        assert "[PHONE]" in sanitized_content


@pytest.mark.asyncio
async def test_interact_without_pii(mock_provider, temp_audit_dir):
    """Test interaction with no PII in input"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        user_input = "What is the weather like today?"

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Check security metadata shows no PII
        assert "security" in result
        assert result["security"]["pii_detected"] == 0
        assert result["security"]["pii_scrubbed"] is False


@pytest.mark.asyncio
async def test_interact_pii_all_empathy_levels(mock_provider, temp_audit_dir):
    """Test PII scrubbing works across all empathy levels"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=5,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        user_input = "My email is test@example.com and SSN is 123-45-6789"

        # Test all 5 levels
        for level in range(1, 6):
            result = await llm.interact(
                user_id=f"test_user_{level}", user_input=user_input, force_level=level
            )

            # All levels should scrub PII
            assert "security" in result
            assert result["security"]["pii_detected"] > 0
            assert result["level_used"] == level


# ============================================================================
# Secrets Detection Tests
# ============================================================================


@pytest.mark.asyncio
async def test_interact_blocks_secrets(mock_provider, temp_audit_dir):
    """Test that requests with secrets are blocked by default"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={
                "audit_log_dir": temp_audit_dir,
                "block_on_secrets": True,
            },
        )

        # Input contains API key
        user_input = 'ANTHROPIC_API_KEY = "sk-ant-api03-abc123xyz789..."'

        # Should raise SecurityError
        with pytest.raises(SecurityError, match="Request blocked.*secret"):
            await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Provider should NOT have been called
        mock_provider.generate.assert_not_called()


@pytest.mark.asyncio
async def test_interact_logs_secrets_when_not_blocking(mock_provider, temp_audit_dir):
    """Test that secrets are logged but request proceeds when block_on_secrets=False"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={
                "audit_log_dir": temp_audit_dir,
                "block_on_secrets": False,  # Don't block
            },
        )

        user_input = 'OPENAI_API_KEY = "sk-proj-abc123xyz789..."'

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Should succeed
        assert result["content"] == "Mock LLM response"
        assert "security" in result
        assert result["security"]["secrets_detected"] > 0

        # Provider should have been called
        mock_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_interact_detects_multiple_secret_types(mock_provider, temp_audit_dir):
    """Test detection of multiple types of secrets"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={
                "audit_log_dir": temp_audit_dir,
                "block_on_secrets": False,
            },
        )

        # Input contains multiple secrets
        user_input = """
        AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
        password = "my_secret_password123"
        """

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Should detect multiple secrets
        assert result["security"]["secrets_detected"] >= 2


@pytest.mark.asyncio
async def test_interact_no_secrets_detected(mock_provider, temp_audit_dir):
    """Test interaction with no secrets in input"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        user_input = "What is the capital of France?"

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Should succeed with no secrets
        assert result["content"] == "Mock LLM response"
        assert result["security"]["secrets_detected"] == 0


# ============================================================================
# Audit Logging Tests
# ============================================================================


@pytest.mark.asyncio
async def test_interact_logs_successful_request(mock_provider, temp_audit_dir):
    """Test that successful requests are logged to audit trail"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=2,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        user_input = "Help me with my project"

        result = await llm.interact(
            user_id="test_user@company.com", user_input=user_input, force_level=2
        )

        assert result["content"] == "Mock LLM response"

        # Check that audit log file was created
        audit_log_path = Path(temp_audit_dir) / "audit.jsonl"
        assert audit_log_path.exists()

        # Read and verify log contents
        with open(audit_log_path) as f:
            log_lines = f.readlines()
            assert len(log_lines) > 0

            import json

            log_entry = json.loads(log_lines[0])
            assert log_entry["event_type"] == "llm_request"
            assert log_entry["user_id"] == "test_user@company.com"
            assert log_entry["status"] == "success"
            assert log_entry["llm"]["empathy_level"] == 2
            assert log_entry["security"]["pii_detected"] == 0
            assert log_entry["security"]["secrets_detected"] == 0


@pytest.mark.asyncio
async def test_interact_logs_pii_detection(mock_provider, temp_audit_dir):
    """Test that PII detections are logged in audit trail"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        user_input = "Email: john@example.com, Phone: 555-123-4567"

        await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Read audit log
        audit_log_path = Path(temp_audit_dir) / "audit.jsonl"
        with open(audit_log_path) as f:
            import json

            log_entry = json.loads(f.readline())
            assert log_entry["security"]["pii_detected"] > 0
            assert log_entry["security"]["sanitization_applied"] is True


@pytest.mark.asyncio
async def test_interact_logs_security_violation(mock_provider, temp_audit_dir):
    """Test that security violations are logged separately"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={
                "audit_log_dir": temp_audit_dir,
                "block_on_secrets": True,
            },
        )

        # Use a proper Anthropic API key format that will be detected
        user_input = (
            'ANTHROPIC_API_KEY = "sk-ant-api03-' + "x" * 95 + '"'
        )  # Minimum 95 chars after prefix

        # Should raise SecurityError
        try:
            await llm.interact(user_id="test_user", user_input=user_input, force_level=1)
        except SecurityError:
            pass

        # Check audit log for security violation
        audit_log_path = Path(temp_audit_dir) / "audit.jsonl"
        with open(audit_log_path) as f:
            import json

            log_lines = f.readlines()
            # Should have a security_violation event
            violation_found = False
            for line in log_lines:
                log_entry = json.loads(line)
                if log_entry["event_type"] == "security_violation":
                    violation_found = True
                    assert log_entry["violation"]["type"] == "secrets_detected"
                    assert log_entry["violation"]["severity"] == "HIGH"
                    assert log_entry["violation"]["blocked"] is True
                    break

            assert violation_found, "Security violation not logged"


# ============================================================================
# Combined Security Features Tests
# ============================================================================


@pytest.mark.asyncio
async def test_interact_pii_and_secrets_combined(mock_provider, temp_audit_dir):
    """Test interaction with both PII and secrets in input"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={
                "audit_log_dir": temp_audit_dir,
                "block_on_secrets": True,
            },
        )

        # Input has both PII and secrets (use proper API key format)
        user_input = (
            'My email is john@example.com and ANTHROPIC_API_KEY = "sk-ant-api03-' + "x" * 95 + '"'
        )

        # Should block due to secrets (before PII scrubbing matters)
        with pytest.raises(SecurityError):
            await llm.interact(user_id="test_user", user_input=user_input, force_level=1)


@pytest.mark.asyncio
async def test_interact_security_across_all_levels(mock_provider, temp_audit_dir):
    """Test that security works consistently across all empathy levels"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=5,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        test_cases = [
            ("Level 1 test with email: user@example.com", 1),
            ("Level 2 test with phone: 555-123-4567", 2),
            ("Level 3 test with SSN: 123-45-6789", 3),
            ("Level 4 test with IP: 192.168.1.1", 4),
            ("Level 5 test with email: admin@example.com", 5),
        ]

        for user_input, level in test_cases:
            result = await llm.interact(
                user_id=f"test_user_level_{level}",
                user_input=user_input,
                force_level=level,
            )

            assert result["level_used"] == level
            assert "security" in result
            assert result["security"]["pii_detected"] > 0


# ============================================================================
# Security Disabled Tests (Backward Compatibility)
# ============================================================================


@pytest.mark.asyncio
async def test_interact_security_disabled_no_scrubbing(mock_provider):
    """Test that with security disabled, no scrubbing occurs (backward compatibility)"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=False,  # Explicitly disabled
        )

        user_input = "My email is john@example.com"

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Should succeed
        assert result["content"] == "Mock LLM response"

        # No security metadata in result
        assert "security" not in result

        # Provider should receive original input (not scrubbed)
        call_args = mock_provider.generate.call_args
        messages = call_args[1]["messages"]
        assert "john@example.com" in messages[0]["content"]


@pytest.mark.asyncio
async def test_interact_security_disabled_secrets_not_blocked(mock_provider):
    """Test that with security disabled, secrets are not blocked"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=False,
        )

        user_input = 'API_KEY = "sk-ant-api03-secret..."'

        # Should succeed without raising SecurityError
        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        assert result["content"] == "Mock LLM response"
        mock_provider.generate.assert_called_once()


# ============================================================================
# Performance and Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_interact_empty_input(mock_provider, temp_audit_dir):
    """Test security handling with empty input"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        user_input = ""

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        assert result["content"] == "Mock LLM response"
        assert result["security"]["pii_detected"] == 0
        assert result["security"]["secrets_detected"] == 0


@pytest.mark.asyncio
async def test_interact_large_input_with_pii(mock_provider, temp_audit_dir):
    """Test security with large input containing multiple PII instances"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        # Large input with multiple PII items
        user_input = "\n".join(
            [f"Employee {i}: email{i}@example.com, phone: 555-123-{i:04d}" for i in range(10)]
        )

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        # Should scrub all PII
        assert result["security"]["pii_detected"] >= 20  # 10 emails + 10 phones


@pytest.mark.asyncio
async def test_interact_unicode_with_pii(mock_provider, temp_audit_dir):
    """Test security with unicode characters and PII"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        user_input = "Contactez-moi à jean@example.com ou appelez 555-123-4567 🔒"

        result = await llm.interact(user_id="test_user", user_input=user_input, force_level=1)

        assert result["security"]["pii_detected"] > 0
        assert result["content"] == "Mock LLM response"


# ============================================================================
# Multiple Users Security Isolation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_multiple_users_independent_security_logging(mock_provider, temp_audit_dir):
    """Test that multiple users' interactions are logged independently"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=1,
            enable_security=True,
            security_config={"audit_log_dir": temp_audit_dir},
        )

        # User 1 interaction
        await llm.interact(
            user_id="user1@company.com",
            user_input="My email is user1@example.com",
            force_level=1,
        )

        # User 2 interaction
        await llm.interact(
            user_id="user2@company.com",
            user_input="My email is user2@example.com",
            force_level=1,
        )

        # Check audit log has both users
        audit_log_path = Path(temp_audit_dir) / "audit.jsonl"
        with open(audit_log_path) as f:
            import json

            log_lines = f.readlines()
            assert len(log_lines) >= 2

            users = [json.loads(line)["user_id"] for line in log_lines]
            assert "user1@company.com" in users
            assert "user2@company.com" in users


# ============================================================================
# Configuration Validation Tests
# ============================================================================


def test_security_config_defaults():
    """Test that security config uses sensible defaults"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Minimal config - should use defaults
            llm = EmpathyLLM(
                provider="anthropic",
                enable_security=True,
                security_config={"audit_log_dir": tmpdir},
            )

            # Check defaults are applied
            assert llm.security_config.get("block_on_secrets", True) is True
            assert llm.security_config.get("enable_pii_scrubbing", True) is True
            assert llm.pii_scrubber is not None
            assert llm.secrets_detector is not None
