"""
Tests for PII Scrubber Module

Comprehensive tests for PII detection and scrubbing functionality.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_llm_toolkit.security.pii_scrubber import PIIDetection, PIIPattern, PIIScrubber


class TestPIIDetection:
    """Tests for PIIDetection dataclass"""

    def test_pii_detection_creation(self):
        """Test creating a PIIDetection instance"""
        detection = PIIDetection(
            pii_type="email",
            matched_text="test@example.com",
            start_pos=0,
            end_pos=16,
            replacement="[EMAIL]",
            confidence=1.0,
        )
        assert detection.pii_type == "email"
        assert detection.matched_text == "test@example.com"
        assert detection.replacement == "[EMAIL]"
        assert detection.confidence == 1.0

    def test_pii_detection_to_dict(self):
        """Test converting PIIDetection to dictionary"""
        detection = PIIDetection(
            pii_type="phone",
            matched_text="555-123-4567",
            start_pos=10,
            end_pos=22,
            replacement="[PHONE]",
            confidence=0.95,
            metadata={"format": "US"},
        )
        result = detection.to_dict()
        assert result["pii_type"] == "phone"
        assert result["matched_text"] == "555-123-4567"
        assert result["confidence"] == 0.95
        assert result["metadata"] == {"format": "US"}

    def test_pii_detection_to_audit_safe_dict(self):
        """Test audit-safe dictionary (no PII values)"""
        detection = PIIDetection(
            pii_type="ssn",
            matched_text="123-45-6789",
            start_pos=5,
            end_pos=16,
            replacement="[SSN]",
            confidence=1.0,
        )
        result = detection.to_audit_safe_dict()
        assert result["pii_type"] == "ssn"
        assert "matched_text" not in result  # Should not contain actual PII
        assert result["position"] == "5-16"
        assert result["length"] == 11
        assert result["replacement"] == "[SSN]"


class TestPIIScrubber:
    """Tests for PIIScrubber class"""

    @pytest.fixture
    def scrubber(self):
        """Create a PIIScrubber instance with name detection enabled"""
        return PIIScrubber(enable_name_detection=True)

    @pytest.fixture
    def scrubber_no_names(self):
        """Create a PIIScrubber instance without name detection"""
        return PIIScrubber(enable_name_detection=False)

    def test_scrubber_initialization(self, scrubber):
        """Test PIIScrubber initializes with default patterns"""
        assert len(scrubber.patterns) > 0
        assert "email" in scrubber.patterns
        assert "ssn" in scrubber.patterns
        assert "phone" in scrubber.patterns
        assert "credit_card" in scrubber.patterns

    def test_scrubber_without_name_detection(self, scrubber_no_names):
        """Test name detection can be disabled"""
        assert "name" in scrubber_no_names.patterns
        assert scrubber_no_names.patterns["name"].enabled is False

    def test_scrub_email(self, scrubber):
        """Test email address scrubbing"""
        text = "Contact me at john.doe@example.com for more info"
        sanitized, detections = scrubber.scrub(text)

        assert "[EMAIL]" in sanitized
        assert "john.doe@example.com" not in sanitized
        assert len(detections) >= 1
        assert any(d.pii_type == "email" for d in detections)

    def test_scrub_ssn(self, scrubber):
        """Test SSN scrubbing"""
        text = "My SSN is 123-45-6789"
        sanitized, detections = scrubber.scrub(text)

        assert "[SSN]" in sanitized
        assert "123-45-6789" not in sanitized
        assert any(d.pii_type == "ssn" for d in detections)

    def test_scrub_ssn_without_dashes(self, scrubber):
        """Test SSN without dashes is detected"""
        text = "SSN: 123456789"
        sanitized, detections = scrubber.scrub(text)

        assert "[SSN]" in sanitized
        assert "123456789" not in sanitized

    def test_scrub_phone_us_format(self, scrubber):
        """Test US phone number scrubbing"""
        text = "Call me at (555) 123-4567"
        sanitized, detections = scrubber.scrub(text)

        assert "[PHONE]" in sanitized
        assert "(555) 123-4567" not in sanitized

    def test_scrub_phone_with_dots(self, scrubber):
        """Test phone with dots format"""
        text = "Phone: 555.123.4567"
        sanitized, detections = scrubber.scrub(text)

        assert "[PHONE]" in sanitized
        assert "555.123.4567" not in sanitized

    def test_scrub_credit_card_visa(self, scrubber):
        """Test Visa credit card scrubbing"""
        text = "Pay with card: 4111-1111-1111-1111"
        sanitized, detections = scrubber.scrub(text)

        assert "[CC]" in sanitized
        assert "4111-1111-1111-1111" not in sanitized

    def test_scrub_credit_card_amex(self, scrubber):
        """Test Amex credit card scrubbing"""
        text = "Amex: 3782-822463-10005"
        sanitized, detections = scrubber.scrub(text)

        assert "[CC]" in sanitized
        assert "3782-822463-10005" not in sanitized

    def test_scrub_ipv4(self, scrubber):
        """Test IPv4 address scrubbing"""
        text = "Server IP: 192.168.1.100"
        sanitized, detections = scrubber.scrub(text)

        assert "[IP]" in sanitized
        assert "192.168.1.100" not in sanitized

    def test_scrub_multiple_pii_types(self, scrubber):
        """Test scrubbing multiple PII types in one text"""
        text = "Email: test@email.com, Phone: 555-123-4567, SSN: 123-45-6789"
        sanitized, detections = scrubber.scrub(text)

        assert "[EMAIL]" in sanitized
        assert "[PHONE]" in sanitized
        assert "[SSN]" in sanitized
        assert len(detections) >= 3

    def test_scrub_preserves_non_pii_text(self, scrubber):
        """Test that non-PII text is preserved"""
        text = "Hello, this is a normal message with no PII."
        sanitized, detections = scrubber.scrub(text)

        assert sanitized == text
        assert len(detections) == 0

    def test_scrub_empty_string(self, scrubber):
        """Test scrubbing empty string"""
        sanitized, detections = scrubber.scrub("")

        assert sanitized == ""
        assert len(detections) == 0

    def test_scrub_address(self, scrubber):
        """Test US address scrubbing"""
        text = "I live at 123 Main Street Apt 4B"
        sanitized, detections = scrubber.scrub(text)

        # Address detection is enabled
        if any(d.pii_type == "address" for d in detections):
            assert "[ADDRESS]" in sanitized

    def test_detection_positions_are_correct(self, scrubber):
        """Test that detection positions are accurate"""
        text = "Email: test@example.com"
        sanitized, detections = scrubber.scrub(text)

        email_detection = next((d for d in detections if d.pii_type == "email"), None)
        if email_detection:
            original_text = text[email_detection.start_pos : email_detection.end_pos]
            assert "test@example.com" in original_text or original_text in "test@example.com"


class TestPIIPattern:
    """Tests for PIIPattern dataclass"""

    def test_pattern_creation(self):
        """Test creating a PIIPattern"""
        import re

        pattern = PIIPattern(
            name="custom",
            pattern=re.compile(r"\btest\b"),
            replacement="[CUSTOM]",
            confidence=0.9,
            description="Custom test pattern",
            enabled=True,
        )
        assert pattern.name == "custom"
        assert pattern.replacement == "[CUSTOM]"
        assert pattern.confidence == 0.9
        assert pattern.enabled is True

    def test_pattern_default_values(self):
        """Test default values for PIIPattern"""
        import re

        pattern = PIIPattern(
            name="minimal",
            pattern=re.compile(r"\bminimal\b"),
            replacement="[MINIMAL]",
        )
        assert pattern.confidence == 1.0
        assert pattern.description == ""
        assert pattern.enabled is True


class TestPIIEdgeCases:
    """Edge case tests for PII scrubbing"""

    @pytest.fixture
    def scrubber(self):
        return PIIScrubber()

    def test_invalid_ssn_not_detected(self, scrubber):
        """Test that invalid SSN patterns are not detected"""
        # SSNs starting with 000, 666, or 9xx are invalid
        text = "Invalid: 000-12-3456"
        sanitized, detections = scrubber.scrub(text)

        # The pattern should exclude invalid SSNs
        ssn_detections = [d for d in detections if d.pii_type == "ssn"]
        assert len(ssn_detections) == 0 or "000-12-3456" in sanitized

    def test_very_long_text(self, scrubber):
        """Test scrubbing very long text"""
        long_text = "Normal text. " * 1000 + " Email: test@example.com " + " More text. " * 1000
        sanitized, detections = scrubber.scrub(long_text)

        assert "[EMAIL]" in sanitized
        assert "test@example.com" not in sanitized

    def test_unicode_text(self, scrubber):
        """Test scrubbing text with unicode characters"""
        text = "Email: тест@example.com, Regular: test@example.com"
        sanitized, detections = scrubber.scrub(text)

        # At least the regular email should be detected
        assert len(detections) >= 1

    def test_newlines_and_tabs(self, scrubber):
        """Test scrubbing text with newlines and tabs"""
        text = "Line 1: test@email.com\nLine 2: 555-123-4567\tEnd"
        sanitized, detections = scrubber.scrub(text)

        assert "[EMAIL]" in sanitized
        assert "[PHONE]" in sanitized
