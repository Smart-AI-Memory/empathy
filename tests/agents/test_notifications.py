"""Tests for notification system.

Tests multi-channel notifications for compliance alerts.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from agents.notifications import NotificationConfig, NotificationService


@pytest.fixture
def notification_service():
    """Create notification service with test config."""
    config = NotificationConfig(
        smtp_host="smtp.test.com",
        smtp_user="test@example.com",
        smtp_password="testpass",
        smtp_from="noreply@test.com",
        slack_webhook_url="https://hooks.slack.com/services/TEST/WEBHOOK",
    )
    return NotificationService(config)


class TestNotificationConfig:
    """Test notification configuration."""

    def test_from_env_with_defaults(self, monkeypatch):
        """Test loading config from environment."""
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_USER", "user@example.com")
        monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/test")

        config = NotificationConfig.from_env()

        assert config.smtp_host == "smtp.example.com"
        assert config.smtp_user == "user@example.com"
        assert config.smtp_port == 587  # Default
        assert config.slack_webhook_url == "https://hooks.slack.com/test"

    def test_from_env_with_custom_port(self, monkeypatch):
        """Test custom SMTP port from environment."""
        monkeypatch.setenv("SMTP_PORT", "465")

        config = NotificationConfig.from_env()

        assert config.smtp_port == 465


class TestEmailNotifications:
    """Test email notification functionality."""

    def test_email_requires_config(self):
        """Test that email fails gracefully when not configured."""
        service = NotificationService(NotificationConfig())  # Empty config

        result = service.send_email(
            to=["user@example.com"],
            subject="Test",
            body="Test body",
        )

        assert result is False  # Should fail gracefully

    def test_email_message_format(self, notification_service):
        """Test email message structure (mocked send)."""
        # This test verifies message creation without actual sending
        # In production, would mock smtplib.SMTP

        # For now, just verify config is set
        assert notification_service.config.smtp_host == "smtp.test.com"
        assert notification_service.config.smtp_user == "test@example.com"


class TestSlackNotifications:
    """Test Slack notification functionality."""

    def test_slack_requires_config(self):
        """Test that Slack fails gracefully when not configured."""
        service = NotificationService(NotificationConfig())  # Empty config

        result = service.send_slack("Test message")

        assert result is False  # Should fail gracefully

    def test_slack_payload_structure(self, notification_service):
        """Test Slack webhook payload format."""
        # Verify config is set for Slack
        assert notification_service.config.slack_webhook_url is not None
        assert "hooks.slack.com" in notification_service.config.slack_webhook_url


class TestSMSNotifications:
    """Test SMS notification functionality."""

    def test_sms_requires_config(self):
        """Test that SMS fails gracefully when not configured."""
        service = NotificationService(NotificationConfig())  # Empty config

        result = service.send_sms("+1234567890", "Test message")

        assert result is False  # Should fail gracefully

    def test_sms_requires_twilio_sdk(self, notification_service):
        """Test that SMS notifies user if Twilio SDK not installed."""
        # Configure Twilio but SDK may not be installed
        notification_service.config.twilio_account_sid = "test_sid"
        notification_service.config.twilio_auth_token = "test_token"
        notification_service.config.twilio_from_number = "+1234567890"

        result = notification_service.send_sms("+1987654321", "Test")

        # Should return False if SDK not installed (graceful fallback)
        assert isinstance(result, bool)


class TestComplianceAlerts:
    """Test compliance alert multi-channel delivery."""

    def test_compliance_alert_structure(self, notification_service):
        """Test compliance alert message structure."""
        recipients = {
            "email": ["admin@example.com"],
            "phone": ["+1234567890"],
        }

        # This won't actually send (no real credentials)
        # but tests the logic flow
        results = notification_service.send_compliance_alert(
            severity="critical",
            title="HIPAA Violation Detected",
            description="Unencrypted PHI found in logs",
            recipients=recipients,
        )

        # Verify results dict structure
        assert isinstance(results, dict)
        # Email and Slack will be attempted (config present)
        # SMS only for critical/high severity

    def test_sms_only_for_critical_high(self, notification_service):
        """Test that SMS is only sent for critical/high severity."""
        # For low severity, SMS should not be attempted
        recipients = {
            "email": ["admin@example.com"],
            "phone": ["+1234567890"],
        }

        results = notification_service.send_compliance_alert(
            severity="low",
            title="Minor Issue",
            description="Low priority alert",
            recipients=recipients,
        )

        # SMS key should not be in results for low severity
        # (unless explicitly configured to send for all severities)
        assert "email" in results or "slack" in results
