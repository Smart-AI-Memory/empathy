"""Educational Tests for PII Scrubber (Phase 3 - Security Testing)

Learning Objectives:
- Multi-pattern detection (emails, phones, SSNs)
- Confidence scoring
- Custom pattern registration
- Redaction strategies

Key Patterns:
- Security testing patterns
- Regex pattern testing
- Multi-pattern detection
"""

import pytest

from empathy_os.memory.security.pii_scrubber import PIIScrubber


@pytest.mark.unit
class TestPIIDetection:
    """Educational tests for PII pattern detection."""

    @pytest.fixture
    def scrubber(self):
        """Fixture for PII scrubber."""
        return PIIScrubber()

    def test_scrub_email_address(self, scrubber):
        """Teaching Pattern: Testing email scrubbing.

        Common PII type that must be detected and scrubbed.
        """
        text = "Contact me at user@example.com for details"
        scrubbed, detections = scrubber.scrub(text)

        assert len(detections) >= 1
        assert "user@example.com" in text
        # Scrubbed should redact email
        assert "user@example.com" not in scrubbed or "[EMAIL" in scrubbed

    def test_scrub_returns_tuple(self, scrubber):
        """Teaching Pattern: Testing API return types.

        scrub() returns (scrubbed_text, detections_list)
        """
        text = "Call me at 555-123-4567"
        result = scrubber.scrub(text)

        assert isinstance(result, tuple)
        assert len(result) == 2
        scrubbed, detections = result
        assert isinstance(scrubbed, str)
        assert isinstance(detections, list)

    def test_empty_text_handling(self, scrubber):
        """Teaching Pattern: Testing edge cases.

        Empty input should not crash.
        """
        scrubbed, detections = scrubber.scrub("")

        assert scrubbed == ""
        assert isinstance(detections, list)

    @pytest.mark.parametrize(
        "text,pii_type,expected_replacement",
        [
            ("Email: user@example.com", "email", "[EMAIL]"),
            ("SSN: 123-45-6789", "ssn", "[SSN]"),
            ("Call: 555-123-4567", "phone", "[PHONE]"),
            ("CC: 4532-1234-5678-9010", "credit_card", "[CC]"),
            ("IP: 192.168.1.1", "ipv4", "[IP]"),
            ("MRN-1234567", "mrn", "[MRN]"),
            ("Patient ID: 123456", "patient_id", "[PATIENT_ID]"),
        ],
    )
    def test_multi_pattern_detection(self, scrubber, text, pii_type, expected_replacement):
        """Teaching Pattern: Parametrized testing for multiple PII types.

        Tests each PII pattern individually with expected replacement.
        """
        scrubbed, detections = scrubber.scrub(text)

        assert len(detections) >= 1
        assert expected_replacement in scrubbed
        assert any(d.pii_type == pii_type for d in detections)

    def test_multiple_pii_in_single_text(self, scrubber):
        """Teaching Pattern: Testing multi-pattern detection.

        Real-world text often contains multiple PII types.
        """
        text = "Contact John at john@test.com or 555-1234, SSN: 123-45-6789"
        scrubbed, detections = scrubber.scrub(text)

        # Should detect email, phone, and SSN
        pii_types = {d.pii_type for d in detections}
        assert "email" in pii_types
        assert "phone" in pii_types or "ssn" in pii_types  # At least one of these

        # Original PII should be removed
        assert "john@test.com" not in scrubbed or "[EMAIL]" in scrubbed

    def test_pii_detection_includes_position(self, scrubber):
        """Teaching Pattern: Testing detection metadata.

        Detection objects should include position information.
        """
        text = "Email me at user@example.com for details"
        scrubbed, detections = scrubber.scrub(text)

        assert len(detections) >= 1
        detection = detections[0]

        # Position should be valid
        assert detection.start_pos >= 0
        assert detection.end_pos > detection.start_pos
        assert detection.matched_text == text[detection.start_pos : detection.end_pos]

    def test_confidence_scoring(self, scrubber):
        """Teaching Pattern: Testing confidence values.

        Different patterns have different confidence levels.
        """
        text = "Email: user@example.com"
        scrubbed, detections = scrubber.scrub(text)

        assert len(detections) >= 1
        detection = detections[0]

        # Email pattern has high confidence (1.0)
        assert 0.0 <= detection.confidence <= 1.0
        assert detection.confidence > 0.5  # At least moderate confidence

    def test_detection_to_dict(self, scrubber):
        """Teaching Pattern: Testing serialization methods.

        PIIDetection can be converted to dictionary for logging.
        """
        text = "Contact: user@example.com"
        scrubbed, detections = scrubber.scrub(text)

        assert len(detections) >= 1
        detection = detections[0]

        # to_dict should include all fields
        detection_dict = detection.to_dict()
        assert "pii_type" in detection_dict
        assert "matched_text" in detection_dict
        assert "start_pos" in detection_dict
        assert "confidence" in detection_dict

    def test_detection_to_audit_safe_dict(self, scrubber):
        """Teaching Pattern: Testing audit-safe serialization.

        Audit logs should not contain actual PII values.
        """
        text = "Email: user@example.com"
        scrubbed, detections = scrubber.scrub(text)

        assert len(detections) >= 1
        detection = detections[0]

        # Audit-safe version should NOT include matched_text
        audit_dict = detection.to_audit_safe_dict()
        assert "matched_text" not in audit_dict
        assert "pii_type" in audit_dict
        assert "position" in audit_dict
        assert "length" in audit_dict


@pytest.mark.unit
class TestCustomPatterns:
    """Educational tests for custom PII pattern registration."""

    @pytest.fixture
    def scrubber(self):
        """Fixture for PII scrubber."""
        return PIIScrubber()

    def test_add_custom_pattern(self, scrubber):
        """Teaching Pattern: Testing custom pattern registration.

        Organizations need domain-specific PII patterns.
        """
        scrubber.add_custom_pattern(
            name="employee_id",
            pattern=r"EMP-\d{6}",
            replacement="[EMPLOYEE_ID]",
            description="Company employee identifier",
        )

        text = "Employee EMP-123456 submitted report"
        scrubbed, detections = scrubber.scrub(text)

        assert "[EMPLOYEE_ID]" in scrubbed
        assert "EMP-123456" not in scrubbed
        assert any(d.pii_type == "employee_id" for d in detections)

    def test_custom_pattern_with_confidence(self, scrubber):
        """Teaching Pattern: Custom patterns can have custom confidence.

        Some patterns are less certain than others.
        """
        scrubber.add_custom_pattern(
            name="possible_id",
            pattern=r"ID-\d{4}",
            replacement="[ID]",
            confidence=0.7,  # Lower confidence
            description="Possible identifier",
        )

        text = "Reference ID-1234"
        scrubbed, detections = scrubber.scrub(text)

        assert len(detections) >= 1
        detection = detections[0]
        assert detection.confidence == 0.7

    def test_duplicate_pattern_name_raises_error(self, scrubber):
        """Teaching Pattern: Testing error conditions.

        Pattern names must be unique to avoid conflicts.
        """
        scrubber.add_custom_pattern(name="test_id", pattern=r"TEST-\d+", replacement="[TEST]")

        # Adding again should raise ValueError
        with pytest.raises(ValueError, match="already exists"):
            scrubber.add_custom_pattern(name="test_id", pattern=r"OTHER-\d+", replacement="[OTHER]")

    def test_invalid_regex_pattern_raises_error(self, scrubber):
        """Teaching Pattern: Testing regex validation.

        Invalid regex should be caught early.
        """
        with pytest.raises(ValueError, match="Invalid regex"):
            scrubber.add_custom_pattern(
                name="bad_pattern",
                pattern=r"[unclosed",
                replacement="[BAD]",  # Invalid regex
            )

    def test_remove_custom_pattern(self, scrubber):
        """Teaching Pattern: Testing pattern removal.

        Custom patterns can be added and removed dynamically.
        """
        scrubber.add_custom_pattern(name="temp_id", pattern=r"TEMP-\d+", replacement="[TEMP]")

        # Pattern should work
        text = "Reference TEMP-123"
        scrubbed, _ = scrubber.scrub(text)
        assert "[TEMP]" in scrubbed

        # Remove pattern
        scrubber.remove_custom_pattern("temp_id")

        # Pattern should no longer work
        scrubbed, _ = scrubber.scrub(text)
        assert "TEMP-123" in scrubbed  # Not scrubbed anymore

    def test_cannot_remove_default_pattern(self, scrubber):
        """Teaching Pattern: Testing protection of default patterns.

        Default patterns can be disabled but not removed.
        """
        with pytest.raises(ValueError, match="Cannot remove default pattern"):
            scrubber.remove_custom_pattern("email")


@pytest.mark.unit
class TestPatternManagement:
    """Educational tests for pattern enable/disable functionality."""

    @pytest.fixture
    def scrubber(self):
        """Fixture for PII scrubber."""
        return PIIScrubber()

    def test_disable_pattern(self, scrubber):
        """Teaching Pattern: Testing pattern disabling.

        Patterns can be temporarily disabled without removal.
        """
        # Disable email pattern
        scrubber.disable_pattern("email")

        text = "Contact: user@example.com"
        scrubbed, detections = scrubber.scrub(text)

        # Email should NOT be detected
        assert "user@example.com" in scrubbed
        assert not any(d.pii_type == "email" for d in detections)

    def test_enable_pattern(self, scrubber):
        """Teaching Pattern: Testing pattern re-enabling.

        Disabled patterns can be re-enabled.
        """
        # Name detection is disabled by default
        scrubber.enable_pattern("name")

        text = "Patient: John Smith"
        scrubbed, detections = scrubber.scrub(text)

        # Name should now be detected
        assert "[NAME]" in scrubbed or "John Smith" not in scrubbed

    def test_get_statistics(self, scrubber):
        """Teaching Pattern: Testing statistics gathering.

        Scrubber can report configuration statistics.
        """
        stats = scrubber.get_statistics()

        assert "total_patterns" in stats
        assert "default_patterns" in stats
        assert "custom_patterns" in stats
        assert "enabled_default" in stats
        assert stats["default_patterns"] >= 10  # We have many default patterns

    def test_statistics_after_adding_custom(self, scrubber):
        """Teaching Pattern: Testing dynamic statistics.

        Statistics update as patterns are added.
        """
        initial_stats = scrubber.get_statistics()
        initial_total = initial_stats["total_patterns"]

        scrubber.add_custom_pattern(name="custom1", pattern=r"CUSTOM-\d+", replacement="[CUSTOM]")

        new_stats = scrubber.get_statistics()
        assert new_stats["total_patterns"] == initial_total + 1
        assert new_stats["custom_patterns"] == initial_stats["custom_patterns"] + 1

    def test_get_pattern_info(self, scrubber):
        """Teaching Pattern: Testing pattern introspection.

        Can query details about specific patterns.
        """
        info = scrubber.get_pattern_info("email")

        assert info["name"] == "email"
        assert info["replacement"] == "[EMAIL]"
        assert info["confidence"] == 1.0
        assert "description" in info
        assert info["is_custom"] is False

    def test_get_pattern_info_for_nonexistent(self, scrubber):
        """Teaching Pattern: Testing error handling.

        Querying non-existent pattern should raise error.
        """
        with pytest.raises(ValueError, match="not found"):
            scrubber.get_pattern_info("nonexistent_pattern")


@pytest.mark.unit
class TestEdgeCases:
    """Educational tests for edge cases and boundary conditions."""

    @pytest.fixture
    def scrubber(self):
        """Fixture for PII scrubber."""
        return PIIScrubber()

    def test_overlapping_patterns(self, scrubber):
        """Teaching Pattern: Testing overlap handling.

        When patterns overlap, first match wins.
        """
        # IPv4 address might overlap with other patterns
        text = "Server at 192.168.1.1 port 8080"
        scrubbed, detections = scrubber.scrub(text)

        # Should detect IP address
        assert "[IP]" in scrubbed
        assert "192.168.1.1" not in scrubbed

    def test_very_long_text(self, scrubber):
        """Teaching Pattern: Testing performance with large inputs.

        Scrubber should handle large text efficiently.
        """
        # Create large text with scattered PII
        large_text = "Normal text. " * 1000 + "Email: user@example.com. " + "More text. " * 1000

        scrubbed, detections = scrubber.scrub(large_text)

        # Should still detect the email
        assert len(detections) >= 1
        assert "[EMAIL]" in scrubbed

    def test_special_characters_in_text(self, scrubber):
        """Teaching Pattern: Testing special character handling.

        Text with ASCII-compatible email addresses work.
        The email pattern uses standard ASCII characters.
        """
        text = "Contact: user@example.com in café"
        scrubbed, detections = scrubber.scrub(text)

        # Email pattern should work with ASCII emails
        assert len(detections) >= 1
        assert "[EMAIL]" in scrubbed

    def test_text_with_no_pii(self, scrubber):
        """Teaching Pattern: Testing clean text.

        Text without PII should pass through unchanged.
        """
        text = "This is a normal sentence with no PII at all."
        scrubbed, detections = scrubber.scrub(text)

        assert scrubbed == text
        assert len(detections) == 0

    def test_validate_patterns(self, scrubber):
        """Teaching Pattern: Testing pattern validation.

        Scrubber can validate patterns with built-in test cases.
        """
        results = scrubber.validate_patterns()

        # Should validate multiple patterns
        assert len(results) > 0

        # Each result should have test statistics
        for result in results:
            assert "pattern" in result
            assert "total_tests" in result
            assert "passed" in result
            assert "success_rate" in result
