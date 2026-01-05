"""Notification system for compliance alerts.

Supports multiple channels: Email (SMTP), Slack webhooks, SMS (Twilio).
Graceful fallback when notification delivery fails.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
import os
import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import requests

logger = logging.getLogger(__name__)


@dataclass
class NotificationConfig:
    """Configuration for notification channels."""

    # Email (SMTP)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None

    # Slack
    slack_webhook_url: str | None = None

    # Twilio SMS
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None

    @classmethod
    def from_env(cls) -> "NotificationConfig":
        """Load configuration from environment variables."""
        return cls(
            # Email
            smtp_host=os.getenv("SMTP_HOST"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            smtp_from=os.getenv("SMTP_FROM"),
            # Slack
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
            # Twilio
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
            twilio_from_number=os.getenv("TWILIO_FROM_NUMBER"),
        )


class NotificationService:
    """Multi-channel notification service with graceful fallback."""

    def __init__(self, config: NotificationConfig | None = None):
        """Initialize notification service.

        Args:
            config: Notification configuration (loads from env if None)
        """
        self.config = config or NotificationConfig.from_env()

    def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        html_body: str | None = None,
    ) -> bool:
        """Send email notification via SMTP.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.config.smtp_host:
            logger.warning("SMTP not configured, skipping email notification")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.config.smtp_from or "noreply@smartaimemory.com"
            msg["To"] = ", ".join(to)

            # Attach plain text and HTML
            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            # Send via SMTP
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {len(to)} recipients: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_slack(
        self,
        message: str,
        channel: str | None = None,
        blocks: list[dict[str, Any]] | None = None,
    ) -> bool:
        """Send Slack notification via webhook.

        Args:
            message: Message text (fallback for blocks)
            channel: Optional channel override
            blocks: Optional Slack blocks for rich formatting

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.config.slack_webhook_url:
            logger.warning("Slack webhook not configured, skipping notification")
            return False

        try:
            payload: dict[str, Any] = {"text": message}

            if channel:
                payload["channel"] = channel

            if blocks:
                payload["blocks"] = blocks

            response = requests.post(
                self.config.slack_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                logger.info(f"Slack notification sent: {message[:50]}...")
                return True
            else:
                logger.error(f"Slack webhook failed: {response.status_code} {response.text}")
                return False

        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False

    def send_sms(self, to: str, message: str) -> bool:
        """Send SMS notification via Twilio.

        Args:
            to: Phone number (E.164 format: +1234567890)
            message: SMS message text (max 160 chars recommended)

        Returns:
            True if sent successfully, False otherwise
        """
        if not all([self.config.twilio_account_sid, self.config.twilio_auth_token]):
            logger.warning("Twilio not configured, skipping SMS notification")
            return False

        try:
            # Import Twilio client (optional dependency)
            from twilio.rest import Client

            client = Client(self.config.twilio_account_sid, self.config.twilio_auth_token)

            client.messages.create(
                to=to,
                from_=self.config.twilio_from_number,
                body=message,
            )

            logger.info(f"SMS sent to {to}")
            return True

        except ImportError:
            logger.error("Twilio SDK not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

    def send_compliance_alert(
        self,
        severity: str,
        title: str,
        description: str,
        recipients: dict[str, list[str]],  # {'email': [...], 'phone': [...]}
    ) -> dict[str, bool]:
        """Send multi-channel compliance alert.

        Args:
            severity: Alert severity ('critical', 'high', 'medium', 'low')
            title: Alert title
            description: Alert description
            recipients: Dict with 'email' and 'phone' lists

        Returns:
            Dict with channel success status: {'email': True, 'slack': True, 'sms': False}
        """
        results = {}

        # Email alert
        if recipients.get("email"):
            email_subject = f"[{severity.upper()}] Compliance Alert: {title}"
            email_body = f"""
Compliance Alert
================

Severity: {severity.upper()}
Title: {title}

Description:
{description}

---
Generated by Empathy Framework Compliance Monitor
            """.strip()

            results["email"] = self.send_email(
                to=recipients["email"],
                subject=email_subject,
                body=email_body,
            )

        # Slack alert
        slack_emoji = {
            "critical": ":rotating_light:",
            "high": ":warning:",
            "medium": ":grey_exclamation:",
            "low": ":information_source:",
        }.get(severity, ":bell:")

        slack_message = f"{slack_emoji} *[{severity.upper()}] {title}*\n\n{description}"

        slack_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{slack_emoji} Compliance Alert",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Title:*\n{title}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Description:*\n{description}"},
            },
        ]

        results["slack"] = self.send_slack(slack_message, blocks=slack_blocks)

        # SMS alert (only for critical/high)
        if severity in ["critical", "high"] and recipients.get("phone"):
            sms_message = f"[{severity.upper()}] {title}: {description[:100]}"

            # Send to all phone numbers
            sms_results = []
            for phone in recipients["phone"]:
                sms_results.append(self.send_sms(phone, sms_message))

            results["sms"] = any(sms_results)  # Success if any SMS sent

        logger.info(f"Compliance alert sent: {results}")
        return results
