"""Extended tests for Audit Logger Module

Coverage boost tests targeting untested code paths:
- Log rotation functionality
- Cleanup old logs
- Date range queries
- Custom filter operators (gte, lt, lte, ne)
- Error handling
- Compliance report edge cases

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from empathy_llm_toolkit.security.audit_logger import AuditEvent, AuditLogger, SecurityViolation


class TestAuditEventExtended:
    """Extended tests for AuditEvent"""

    def test_audit_event_defaults(self):
        """Test audit event default values"""
        event = AuditEvent()

        assert event.event_id.startswith("evt_")
        assert event.timestamp.endswith("Z")
        assert event.version == "1.0"
        assert event.event_type == ""
        assert event.user_id == ""
        assert event.session_id == ""
        assert event.status == "success"
        assert event.error == ""
        assert event.data == {}

    def test_audit_event_with_error(self):
        """Test audit event with error status"""
        event = AuditEvent(
            event_type="llm_request",
            user_id="test@example.com",
            status="failed",
            error="Connection timeout",
        )

        assert event.status == "failed"
        assert event.error == "Connection timeout"

    def test_audit_event_to_dict_flattens_data(self):
        """Test that to_dict flattens nested data"""
        event = AuditEvent(
            event_type="test",
            data={
                "nested": {"key": "value"},
                "flat_key": "flat_value",
            },
        )

        result = event.to_dict()
        assert "nested" in result
        assert result["flat_key"] == "flat_value"
        assert "data" not in result  # data dict is removed after flattening


class TestSecurityViolationExtended:
    """Extended tests for SecurityViolation"""

    def test_security_violation_with_notifications(self):
        """Test security violation with notification flags"""
        violation = SecurityViolation(
            violation_type="unauthorized_access",
            severity="CRITICAL",
            details={"pattern_id": "pat_123"},
            user_notified=True,
            manager_notified=True,
            security_team_notified=True,
        )

        assert violation.user_notified is True
        assert violation.manager_notified is True
        assert violation.security_team_notified is True

    def test_security_violation_default_notifications(self):
        """Test security violation default notification flags are False"""
        violation = SecurityViolation(
            violation_type="test",
            severity="LOW",
            details={},
        )

        assert violation.user_notified is False
        assert violation.manager_notified is False
        assert violation.security_team_notified is False


class TestAuditLoggerRotation:
    """Tests for log rotation functionality"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for test logs"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_log_rotation_triggers_on_size(self, temp_log_dir):
        """Test log rotation triggers when file exceeds max size"""
        # Create logger with very small max size
        logger = AuditLogger(
            log_dir=temp_log_dir,
            max_file_size_mb=0.0001,  # ~100 bytes
            enable_rotation=True,
            enable_console_logging=False,
        )

        # Write multiple events to trigger rotation
        for i in range(10):
            logger.log_llm_request(
                user_id=f"user{i}@example.com",
                empathy_level=1,
                provider="anthropic",
                model="claude-sonnet-4",
                memory_sources=["test"],
            )

        # Check that rotated files exist
        log_files = list(Path(temp_log_dir).glob("audit.jsonl.*"))
        assert len(log_files) >= 1  # At least one rotated file

    def test_cleanup_old_logs(self, temp_log_dir):
        """Test cleanup removes logs older than retention period"""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            retention_days=30,
            enable_rotation=True,
            enable_console_logging=False,
        )

        # Create old rotated log file
        old_timestamp = (datetime.utcnow() - timedelta(days=60)).strftime("%Y%m%d_%H%M%S")
        old_log_file = Path(temp_log_dir) / f"audit.jsonl.{old_timestamp}"
        old_log_file.write_text('{"old": "log"}')

        # Create recent rotated log file
        recent_timestamp = (datetime.utcnow() - timedelta(days=10)).strftime("%Y%m%d_%H%M%S")
        recent_log_file = Path(temp_log_dir) / f"audit.jsonl.{recent_timestamp}"
        recent_log_file.write_text('{"recent": "log"}')

        # Trigger cleanup
        logger._cleanup_old_logs()

        # Old file should be removed, recent should remain
        assert not old_log_file.exists()
        assert recent_log_file.exists()

    def test_cleanup_handles_malformed_timestamps(self, temp_log_dir):
        """Test cleanup skips files with invalid timestamp format"""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            retention_days=30,
            enable_rotation=True,
            enable_console_logging=False,
        )

        # Create file with malformed timestamp suffix
        malformed_file = Path(temp_log_dir) / "audit.jsonl.invalid-timestamp"
        malformed_file.write_text('{"malformed": "log"}')

        # Cleanup should not crash
        logger._cleanup_old_logs()

        # Malformed file should still exist (not deleted)
        assert malformed_file.exists()

    def test_rotation_error_handling(self, temp_log_dir):
        """Test rotation handles errors gracefully"""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=True,
            enable_console_logging=False,
        )

        # Mock rename to fail
        with patch.object(Path, "rename", side_effect=OSError("Permission denied")):
            # Should not crash, just log error
            logger._rotate_log()


class TestAuditLoggerQueries:
    """Extended tests for query functionality"""

    @pytest.fixture
    def temp_log_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def logger(self, temp_log_dir):
        return AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=False,
        )

    def test_query_with_date_range(self, logger):
        """Test querying logs with date range filter"""
        # Log events
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        # Query with date range
        start = datetime.utcnow() - timedelta(hours=1)
        end = datetime.utcnow() + timedelta(hours=1)

        events = logger.query(start_date=start, end_date=end)
        assert len(events) == 1

        # Query outside date range
        old_start = datetime.utcnow() - timedelta(days=30)
        old_end = datetime.utcnow() - timedelta(days=29)

        events = logger.query(start_date=old_start, end_date=old_end)
        assert len(events) == 0

    def test_query_start_date_only(self, logger):
        """Test query with only start_date filter"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        start = datetime.utcnow() - timedelta(hours=1)
        events = logger.query(start_date=start)
        assert len(events) == 1

    def test_query_end_date_only(self, logger):
        """Test query with only end_date filter"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        end = datetime.utcnow() + timedelta(hours=1)
        events = logger.query(end_date=end)
        assert len(events) == 1

    def test_query_custom_filter_gte(self, logger):
        """Test query with gte (greater than or equal) filter"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p1",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=5,
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p2",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=10,
        )

        events = logger.query(
            event_type="store_pattern",
            security__pii_scrubbed__gte=5,
        )
        assert len(events) == 2

    def test_query_custom_filter_lt(self, logger):
        """Test query with lt (less than) filter"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p1",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=5,
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p2",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=10,
        )

        events = logger.query(
            event_type="store_pattern",
            security__pii_scrubbed__lt=10,
        )
        assert len(events) == 1
        assert events[0]["pattern"]["pattern_id"] == "p1"

    def test_query_custom_filter_lte(self, logger):
        """Test query with lte (less than or equal) filter"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p1",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=5,
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p2",
            pattern_type="code",
            classification="PUBLIC",
            pii_scrubbed=10,
        )

        events = logger.query(
            event_type="store_pattern",
            security__pii_scrubbed__lte=5,
        )
        assert len(events) == 1

    def test_query_custom_filter_ne(self, logger):
        """Test query with ne (not equal) filter"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p1",
            pattern_type="code",
            classification="PUBLIC",
        )
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="p2",
            pattern_type="architecture",
            classification="INTERNAL",
        )

        events = logger.query(
            event_type="store_pattern",
            pattern__classification__ne="PUBLIC",
        )
        assert len(events) == 1
        assert events[0]["pattern"]["classification"] == "INTERNAL"

    def test_query_nested_key_not_found(self, logger):
        """Test query with non-existent nested key returns no results"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        events = logger.query(nonexistent__nested__key="value")
        assert len(events) == 0

    def test_query_limit(self, logger):
        """Test query respects limit parameter"""
        for i in range(10):
            logger.log_llm_request(
                user_id=f"user{i}@example.com",
                empathy_level=1,
                provider="anthropic",
                model="claude-sonnet-4",
                memory_sources=[],
            )

        events = logger.query(limit=5)
        assert len(events) == 5

    def test_query_empty_log(self, logger):
        """Test query on empty log returns empty list"""
        events = logger.query()
        assert events == []

    def test_query_nonexistent_log_file(self, temp_log_dir):
        """Test query when log file doesn't exist"""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=False,
        )
        # Don't write any events - file won't exist

        events = logger.query()
        assert events == []

    def test_query_handles_malformed_json(self, temp_log_dir):
        """Test query skips malformed JSON lines"""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=False,
        )

        # Write valid event
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        # Append malformed line
        with open(logger.log_path, "a") as f:
            f.write("not valid json {{{}\n")

        # Query should return only valid events
        events = logger.query()
        assert len(events) == 1


class TestAuditLoggerErrorHandling:
    """Tests for error handling in AuditLogger"""

    @pytest.fixture
    def temp_log_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_init_fallback_directory(self):
        """Test logger falls back to local directory on permission error"""
        with patch("os.chmod", side_effect=PermissionError("Permission denied")):
            logger = AuditLogger(
                log_dir="/nonexistent/restricted/path",
                enable_console_logging=False,
            )

            # Should fall back to ./logs
            assert "logs" in str(logger.log_dir)

    def test_write_event_error_handling(self, temp_log_dir):
        """Test write event handles IO errors gracefully"""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=True,  # Enable to test console fallback
        )

        event = AuditEvent(event_type="test")

        # Mock open to fail
        with patch("builtins.open", side_effect=OSError("Disk full")):
            # Should not crash
            logger._write_event(event)

    def test_query_error_handling(self, temp_log_dir):
        """Test query handles file read errors gracefully"""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=False,
        )

        # Create log file
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        # Verify normal query works
        events = logger.query()
        assert len(events) == 1

        # Test that malformed content in middle of file is handled
        # Append malformed JSON to test error handling mid-stream
        with open(logger.log_path, "a") as f:
            f.write("malformed json line without proper format\n")

        # Query should still work, skipping malformed lines
        events = logger.query()
        assert len(events) == 1  # Only valid event returned


class TestAuditLoggerCompliance:
    """Extended compliance tests"""

    @pytest.fixture
    def temp_log_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def logger(self, temp_log_dir):
        return AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=False,
        )

    def test_compliance_report_empty(self, logger):
        """Test compliance report with no events"""
        report = logger.get_compliance_report()

        assert report["llm_requests"]["total"] == 0
        assert report["pattern_storage"]["total"] == 0
        assert report["security_violations"]["total"] == 0
        assert report["compliance_metrics"]["gdpr_compliant_rate"] == 0.0

    def test_compliance_report_with_dates(self, logger):
        """Test compliance report with date range"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
        )

        start = datetime.utcnow() - timedelta(hours=1)
        end = datetime.utcnow() + timedelta(hours=1)

        report = logger.get_compliance_report(start_date=start, end_date=end)
        assert report["llm_requests"]["total"] == 1

    def test_compliance_report_pii_tracking(self, logger):
        """Test compliance report tracks PII detection"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
            pii_count=5,
        )

        report = logger.get_compliance_report()
        assert report["llm_requests"]["with_pii_detected"] == 1

    def test_compliance_report_secrets_tracking(self, logger):
        """Test compliance report tracks secrets detection"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
            secrets_count=1,
        )

        report = logger.get_compliance_report()
        assert report["llm_requests"]["with_secrets_detected"] == 1

    def test_compliance_report_sanitization(self, logger):
        """Test compliance report tracks sanitization"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
            sanitization_applied=True,
        )

        report = logger.get_compliance_report()
        assert report["llm_requests"]["sanitization_applied"] == 1

    def test_compliance_report_pattern_retrieval(self, logger):
        """Test compliance report tracks pattern retrieval"""
        logger.log_pattern_retrieve(
            user_id="test@example.com",
            pattern_id="pat_123",
            classification="SENSITIVE",
            access_granted=True,
        )
        logger.log_pattern_retrieve(
            user_id="test@example.com",
            pattern_id="pat_456",
            classification="INTERNAL",
            access_granted=False,
        )

        report = logger.get_compliance_report()
        assert report["pattern_retrieval"]["total"] == 2
        assert report["pattern_retrieval"]["access_denied"] == 1
        assert report["pattern_retrieval"]["by_classification"]["SENSITIVE"] == 1

    def test_get_violation_summary_all_users(self, logger):
        """Test violation summary without user filter"""
        logger.log_security_violation(
            user_id="user1@example.com",
            violation_type="secrets_detected",
            severity="HIGH",
            details={},
        )
        logger.log_security_violation(
            user_id="user2@example.com",
            violation_type="unauthorized_access",
            severity="MEDIUM",
            details={},
        )

        summary = logger.get_violation_summary()  # No user filter

        assert summary["total_violations"] == 2
        assert summary["by_user"]["user1@example.com"] == 1
        assert summary["by_user"]["user2@example.com"] == 1


class TestAuditLoggerViolationHandling:
    """Tests for internal violation handling"""

    @pytest.fixture
    def temp_log_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def logger(self, temp_log_dir):
        return AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=False,
        )

    def test_violation_count_tracking(self, logger):
        """Test that violations are counted per user/type"""
        # Log same violation type multiple times
        for _ in range(5):
            logger._handle_security_violation(
                user_id="test@example.com",
                violation_type="secrets_detected",
                severity="HIGH",
                details={},
            )

        # Check internal count
        key = "test@example.com:secrets_detected"
        assert logger._violation_counts[key] == 5

    def test_violation_threshold_alert(self, logger):
        """Test alert triggers at threshold"""
        # Log 3 violations (threshold for warning)
        with patch.object(logger, "_write_event"):  # Don't actually write
            for _ in range(3):
                logger._handle_security_violation(
                    user_id="test@example.com",
                    violation_type="test_violation",
                    severity="MEDIUM",
                    details={},
                )

        key = "test@example.com:test_violation"
        assert logger._violation_counts[key] >= 3

    def test_critical_violation_immediate_alert(self, logger):
        """Test CRITICAL severity triggers immediate alert"""
        with patch("empathy_llm_toolkit.security.audit_logger.logger.warning") as mock_warning:
            logger._handle_security_violation(
                user_id="test@example.com",
                violation_type="critical_issue",
                severity="CRITICAL",
                details={},
            )

            # Should trigger warning even on first occurrence
            mock_warning.assert_called()

    def test_sensitive_not_encrypted_violation(self, logger):
        """Test SENSITIVE pattern without encryption triggers violation"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="pat_123",
            pattern_type="clinical",
            classification="SENSITIVE",
            encrypted=False,  # Should trigger violation
        )

        violations = logger.query(event_type="security_violation")
        assert len(violations) == 1
        assert violations[0]["violation"]["type"] == "sensitive_not_encrypted"


class TestAuditLoggerAdditionalFields:
    """Tests for additional logging fields"""

    @pytest.fixture
    def temp_log_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def logger(self, temp_log_dir):
        return AuditLogger(
            log_dir=temp_log_dir,
            enable_rotation=False,
            enable_console_logging=False,
        )

    def test_llm_request_full_fields(self, logger):
        """Test LLM request with all fields"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=3,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=["enterprise", "user", "project"],
            pii_count=2,
            secrets_count=0,
            request_size_bytes=1000,
            response_size_bytes=5000,
            duration_ms=1500,
            memdocs_patterns_used=["pat_1", "pat_2"],
            sanitization_applied=True,
            classification_verified=True,
            session_id="sess_123",
            ip_address="192.168.1.x",
            temperature=0.5,
            status="success",
        )

        events = logger.query(event_type="llm_request")
        assert len(events) == 1

        event = events[0]
        assert event["llm"]["temperature"] == 0.5
        assert event["request"]["duration_ms"] == 1500
        assert event["request"]["ip_address"] == "192.168.1.x"
        assert len(event["memdocs"]["patterns_used"]) == 2

    def test_llm_request_kwargs(self, logger):
        """Test LLM request with additional kwargs"""
        logger.log_llm_request(
            user_id="test@example.com",
            empathy_level=1,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=[],
            custom_field="custom_value",
            another_field=123,
        )

        events = logger.query(event_type="llm_request")
        event = events[0]

        assert event["custom_field"] == "custom_value"
        assert event["another_field"] == 123

    def test_pattern_store_kwargs(self, logger):
        """Test pattern store with additional kwargs"""
        logger.log_pattern_store(
            user_id="test@example.com",
            pattern_id="pat_123",
            pattern_type="code",
            classification="PUBLIC",
            wizard_used="CodeAnalyzer",
            source="github",
        )

        events = logger.query(event_type="store_pattern")
        event = events[0]

        assert event["wizard_used"] == "CodeAnalyzer"
        assert event["source"] == "github"

    def test_pattern_retrieve_kwargs(self, logger):
        """Test pattern retrieve with additional kwargs"""
        logger.log_pattern_retrieve(
            user_id="test@example.com",
            pattern_id="pat_123",
            classification="INTERNAL",
            access_granted=True,
            purpose="code_review",
        )

        events = logger.query(event_type="retrieve_pattern")
        event = events[0]

        assert event["purpose"] == "code_review"

    def test_security_violation_kwargs(self, logger):
        """Test security violation with additional kwargs"""
        logger.log_security_violation(
            user_id="test@example.com",
            violation_type="secrets_detected",
            severity="HIGH",
            details={"secret_type": "api_key"},
            source_file="config.py",
            line_number=42,
        )

        events = logger.query(event_type="security_violation")
        event = events[0]

        assert event["source_file"] == "config.py"
        assert event["line_number"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
