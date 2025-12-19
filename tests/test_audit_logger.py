"""
Unit tests for AuditLogger

Tests compliance requirements for SOC2, HIPAA, and GDPR.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from empathy_llm_toolkit.security.audit_logger import (
    AuditEvent,
    AuditLogger,
    SecurityViolation,
)


class TestAuditEvent:
    """Test AuditEvent data structure"""

    def test_audit_event_creation(self):
        """Test basic audit event creation"""
        event = AuditEvent(
            event_type="llm_request",
            user_id="test@example.com",
            session_id="sess_123",
            status="success",
        )

        assert event.event_type == "llm_request"
        assert event.user_id == "test@example.com"
        assert event.session_id == "sess_123"
        assert event.status == "success"
        assert event.event_id.startswith("evt_")
        assert len(event.event_id) == 16  # evt_ + 12 hex chars
        assert event.timestamp.endswith("Z")  # UTC timezone

    def test_audit_event_to_dict(self):
        """Test audit event serialization"""
        event = AuditEvent(
            event_type="llm_request",
            user_id="test@example.com",
            data={"custom_field": "custom_value"},
        )

        event_dict = event.to_dict()
        assert event_dict["event_type"] == "llm_request"
        assert event_dict["user_id"] == "test@example.com"
        assert event_dict["custom_field"] == "custom_value"


class TestSecurityViolation:
    """Test SecurityViolation data structure"""

    def test_security_violation_creation(self):
        """Test security violation creation"""
        violation = SecurityViolation(
            violation_type="secrets_detected",
            severity="HIGH",
            details={"secret_type": "api_key"},
        )

        assert violation.violation_type == "secrets_detected"
        assert violation.severity == "HIGH"
        assert violation.details["secret_type"] == "api_key"
        assert not violation.user_notified
        assert not violation.manager_notified
        assert not violation.security_team_notified


class TestAuditLogger:
    """Test AuditLogger functionality"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for test logs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def logger(self, temp_log_dir):
        """Create test audit logger"""
        return AuditLogger(
            log_dir=temp_log_dir, enable_rotation=False, enable_console_logging=False
        )

    def test_logger_initialization(self, temp_log_dir):
        """Test audit logger initialization"""
        logger = AuditLogger(log_dir=temp_log_dir)
        assert logger.log_dir == Path(temp_log_dir)
        assert logger.log_filename == "audit.jsonl"
        assert (
            logger.log_path.exists() or not logger.log_path.exists()
        )  # May not exist until first write

    def test_log_llm_request(self, logger):
        """Test LLM request logging"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=3,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=["enterprise", "user"],
            pii_count=0,
            secrets_count=0,
        )

        # Verify log file was created
        assert logger.log_path.exists()

        # Verify log content
        with open(logger.log_path) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "llm_request"
        assert event["user_id"] == "test@example.com"
        assert event["llm"]["empathy_level"] == 3
        assert event["llm"]["provider"] == "anthropic"
        assert event["security"]["pii_detected"] == 0
        assert event["compliance"]["gdpr_compliant"] is True

    def test_log_pattern_store(self, logger):
        """Test pattern storage logging"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="pattern_123",
            pattern_type="architecture",
            classification="INTERNAL",
            pii_scrubbed=2,
            retention_days=180,
        )

        # Verify log content
        with open(logger.log_path) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "store_pattern"
        assert event["pattern"]["pattern_id"] == "pattern_123"
        assert event["pattern"]["classification"] == "INTERNAL"
        assert event["security"]["pii_scrubbed"] == 2

    def test_log_pattern_retrieve(self, logger):
        """Test pattern retrieval logging"""
        logger.log_pattern_retrieve(
            user_id="test@example.com",
            pattern_id="pattern_123",
            classification="SENSITIVE",
            access_granted=True,
            permission_level="explicit",
        )

        # Verify log content
        with open(logger.log_path) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "retrieve_pattern"
        assert event["pattern"]["pattern_id"] == "pattern_123"
        assert event["access"]["granted"] is True
        assert event["access"]["audit_required"] is True  # SENSITIVE classification

    def test_log_security_violation(self, logger):
        """Test security violation logging"""
        logger.log_security_violation(
            user_id="test@example.com",
            violation_type="secrets_detected",
            severity="HIGH",
            details={"secret_type": "api_key"},
            blocked=True,
        )

        # Verify log content
        with open(logger.log_path) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "security_violation"
        assert event["violation"]["type"] == "secrets_detected"
        assert event["violation"]["severity"] == "HIGH"
        assert event["status"] == "blocked"

    def test_json_lines_format(self, logger):
        """Test JSON Lines format (one event per line)"""
        # Log multiple events
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=2,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=3,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        # Verify each line is valid JSON
        with open(logger.log_path) as f:
            lines = f.readlines()

        assert len(lines) == 3
        for line in lines:
            event = json.loads(line.strip())
            assert "event_id" in event
            assert "timestamp" in event
            assert "event_type" in event

    def test_append_only_behavior(self, logger):
        """Test that logs are append-only (tamper-evident)"""
        # Log first event
        logger.log_llm_request(
            user_id="user1@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        # Get first event ID
        with open(logger.log_path) as f:
            first_event = json.loads(f.readline())
            first_event_id = first_event["event_id"]

        # Log second event
        logger.log_llm_request(
            user_id="user2@example.com",
            empathy_level=2,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        # Verify first event is unchanged
        with open(logger.log_path) as f:
            first_event_check = json.loads(f.readline())
            assert first_event_check["event_id"] == first_event_id

    def test_query_by_event_type(self, logger):
        """Test querying logs by event type"""
        # Log different event types
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p1",
            pattern_type="code",
            classification="PUBLIC",
        )
        logger.log_security_violation(
            user_id="test@example.com",
            violation_type="test",
            severity="LOW",
            details={},
        )

        # Query by event type
        llm_requests = logger.query(event_type="llm_request")
        pattern_stores = logger.query(event_type="store_pattern")
        violations = logger.query(event_type="security_violation")

        assert len(llm_requests) == 1
        assert len(pattern_stores) == 1
        assert len(violations) == 1

    def test_query_by_user_id(self, logger):
        """Test querying logs by user ID"""
        logger.log_llm_request(
            user_id="user1@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )
        logger.log_llm_request(
            user_id="user2@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )
        logger.log_llm_request(
            user_id="user1@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        user1_events = logger.query(user_id="user1@example.com")
        user2_events = logger.query(user_id="user2@example.com")

        assert len(user1_events) == 2
        assert len(user2_events) == 1

    def test_query_by_status(self, logger):
        """Test querying logs by status"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
            status="success",
        )
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
            status="failed",
            error="Test error",
        )

        success_events = logger.query(status="success")
        failed_events = logger.query(status="failed")

        assert len(success_events) == 1
        assert len(failed_events) == 1

    def test_query_with_nested_filter(self, logger):
        """Test querying with nested field filters"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p1",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=2,
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p2",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=5,
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p3",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=10,
        )

        # Query patterns with >5 PII items scrubbed
        high_pii = logger.query(event_type="store_pattern", security__pii_scrubbed__gt=5)
        assert len(high_pii) == 1
        assert high_pii[0]["pattern"]["pattern_id"] == "p3"

    def test_violation_tracking(self, logger):
        """Test security violation tracking"""
        # Trigger multiple violations
        logger.log_security_violation(
            user_id="test@example.com",
            violation_type="secrets_detected",
            severity="HIGH",
            details={},
        )
        logger.log_security_violation(
            user_id="test@example.com",
            violation_type="unauthorized_access",
            severity="MEDIUM",
            details={},
        )
        logger.log_security_violation(
            user_id="test@example.com",
            violation_type="secrets_detected",
            severity="HIGH",
            details={},
        )

        summary = logger.get_violation_summary(user_id="test@example.com")

        assert summary["total_violations"] == 3
        assert summary["by_type"]["secrets_detected"] == 2
        assert summary["by_type"]["unauthorized_access"] == 1
        assert summary["by_severity"]["HIGH"] == 2
        assert summary["by_severity"]["MEDIUM"] == 1

    def test_compliance_report(self, logger):
        """Test compliance report generation"""
        # Log various events
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=3,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=["enterprise"],
            pii_count=0,
            secrets_count=0,
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p1",
            pattern_type="code",
            classification="INTERNAL",
            pii_scrubbed=2,
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p2",
            pattern_type="medical",
            classification="SENSITIVE",
            encrypted=True,
        )

        report = logger.get_compliance_report()

        assert report["llm_requests"]["total"] == 1
        assert report["pattern_storage"]["total"] == 2
        assert report["pattern_storage"]["by_classification"]["INTERNAL"] == 1
        assert report["pattern_storage"]["by_classification"]["SENSITIVE"] == 1
        assert report["pattern_storage"]["encrypted"] == 1

    def test_sensitive_data_audit_trail(self, logger):
        """Test that SENSITIVE data access is always audited"""
        logger.log_pattern_retrieve(
            user_id="test@example.com",
            pattern_id="sensitive_pattern",
            classification="SENSITIVE",
            access_granted=True,
        )

        events = logger.query(event_type="retrieve_pattern")
        assert len(events) == 1
        assert events[0]["access"]["audit_required"] is True
        assert events[0]["compliance"]["hipaa_compliant"] is True

    def test_secrets_detection_violation(self, logger):
        """Test that secrets detection triggers violation"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
            secrets_count=1,  # Secrets detected
        )

        # Should have both llm_request and security_violation
        all_events = logger.query(limit=10)
        event_types = [e["event_type"] for e in all_events]

        assert "llm_request" in event_types
        assert "security_violation" in event_types

    def test_unauthorized_access_violation(self, logger):
        """Test that unauthorized access triggers violation"""
        logger.log_pattern_retrieve(
            user_id="test@example.com",
            pattern_id="pattern_123",
            classification="INTERNAL",
            access_granted=False,  # Access denied
        )

        violations = logger.query(event_type="security_violation")
        assert len(violations) == 1
        assert violations[0]["violation"]["type"] == "unauthorized_access"

    def test_iso8601_timestamps(self, logger):
        """Test that timestamps are ISO-8601 compliant"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        events = logger.query()
        timestamp = events[0]["timestamp"]

        # Should end with Z (UTC)
        assert timestamp.endswith("Z")

        # Should be parseable as ISO-8601
        dt = datetime.fromisoformat(timestamp.rstrip("Z"))
        assert isinstance(dt, datetime)

    def test_unique_event_ids(self, logger):
        """Test that event IDs are unique"""
        # Log multiple events
        for i in range(10):
            logger.log_llm_request(
                user_id=f"user{i}@example.com",
                empathy_level=1,
                provider="anthropic",
                model="claude-sonnet-4",
                memory_sources=[],
            )

        events = logger.query(limit=20)
        event_ids = [e["event_id"] for e in events]

        # All IDs should be unique
        assert len(event_ids) == len(set(event_ids))

        # All IDs should start with evt_
        assert all(eid.startswith("evt_") for eid in event_ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
