"""
Test suite for secrets detector module

Tests comprehensive secrets detection functionality including:
- Pattern-based detection for various secret types
- Entropy analysis for unknown secrets
- Custom pattern support
- Proper redaction of secret values
- Performance with large files

Author: Empathy Framework Team
Version: 1.8.0-beta
"""

import pytest

from empathy_llm_toolkit.security.secrets_detector import (
    SecretDetection,
    SecretsDetector,
    SecretType,
    Severity,
    detect_secrets,
)


class TestSecretsDetector:
    """Test suite for SecretsDetector class"""

    def test_initialization(self):
        """Test detector initialization"""
        detector = SecretsDetector()
        assert detector is not None
        stats = detector.get_statistics()
        assert stats["builtin_patterns"] > 0
        assert stats["custom_patterns"] == 0

    def test_anthropic_api_key_detection(self):
        """Test Anthropic API key detection"""
        detector = SecretsDetector()
        content = 'ANTHROPIC_API_KEY = "sk-ant-api03-abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012pqr"'
        detections = detector.detect(content)

        assert len(detections) > 0
        assert any(d.secret_type == SecretType.ANTHROPIC_API_KEY for d in detections)
        assert detections[0].severity == Severity.HIGH

    def test_openai_api_key_detection(self):
        """Test OpenAI API key detection"""
        detector = SecretsDetector()
        content = 'OPENAI_API_KEY = "sk-proj-abc123xyz789def456ghi789"'
        detections = detector.detect(content)

        assert len(detections) > 0
        # Should match either specific OpenAI pattern or generic API key
        assert any(
            d.secret_type in [SecretType.OPENAI_API_KEY, SecretType.GENERIC_API_KEY]
            for d in detections
        )

    def test_aws_credentials_detection(self):
        """Test AWS credentials detection"""
        detector = SecretsDetector()
        content = """
        AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
        AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        """
        detections = detector.detect(content)

        assert len(detections) >= 2
        assert any(d.secret_type == SecretType.AWS_ACCESS_KEY for d in detections)
        assert any(d.severity == Severity.CRITICAL for d in detections)

    def test_github_token_detection(self):
        """Test GitHub token detection"""
        detector = SecretsDetector()
        test_tokens = [
            "ghp_1234567890abcdefghijklmnopqrstuvwxyz",  # Personal access token
            "gho_1234567890abcdefghijklmnopqrstuvwxyz",  # OAuth token
            "ghs_1234567890abcdefghijklmnopqrstuvwxyz",  # Server-to-server token
        ]

        for token in test_tokens:
            content = f'GITHUB_TOKEN = "{token}"'
            detections = detector.detect(content)
            assert len(detections) > 0
            assert any(d.secret_type == SecretType.GITHUB_TOKEN for d in detections)

    def test_slack_token_detection(self):
        """Test Slack token detection"""
        detector = SecretsDetector()
        content = 'SLACK_TOKEN = "xoxb-FAKE-TEST-TOKEN-NOT-REAL-EXAMPLE"'
        detections = detector.detect(content)

        assert len(detections) > 0
        assert any(d.secret_type == SecretType.SLACK_TOKEN for d in detections)

    def test_stripe_key_detection(self):
        """Test Stripe key detection"""
        detector = SecretsDetector()
        test_keys = [
            "sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "sk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        ]

        for key in test_keys:
            content = f'STRIPE_KEY = "{key}"'
            detections = detector.detect(content)
            assert len(detections) > 0
            assert any(d.secret_type == SecretType.STRIPE_KEY for d in detections)

    def test_password_detection(self):
        """Test password detection"""
        detector = SecretsDetector()
        test_passwords = [
            'password = "my_secret_password123"',
            'PASSWORD = "SuperSecret!@#"',
            "pwd = 'admin123'",
            'passwd = "p@ssw0rd"',
        ]

        for content in test_passwords:
            detections = detector.detect(content)
            assert len(detections) > 0
            assert any(d.secret_type == SecretType.PASSWORD for d in detections)

    def test_private_key_detection(self):
        """Test private key detection"""
        detector = SecretsDetector()
        test_keys = [
            "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...",
            "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXkt...",
            "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIIGlh...",
            "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBg...",
            "-----BEGIN PGP PRIVATE KEY BLOCK-----\nVersion: GnuPG...",
        ]

        for content in test_keys:
            detections = detector.detect(content)
            assert len(detections) > 0
            assert any(d.severity == Severity.CRITICAL for d in detections)

    def test_jwt_token_detection(self):
        """Test JWT token detection"""
        detector = SecretsDetector()
        content = 'token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"'
        detections = detector.detect(content)

        assert len(detections) > 0
        assert any(d.secret_type == SecretType.JWT_TOKEN for d in detections)
        assert any(d.severity == Severity.MEDIUM for d in detections)

    def test_database_url_detection(self):
        """Test database URL detection"""
        detector = SecretsDetector()
        test_urls = [
            "postgres://user:password@localhost:5432/mydb",
            "mysql://admin:pass123@db.example.com:3306/database",
            "mongodb://user:pass@mongo.example.com:27017/db",
            "redis://default:secret@redis.example.com:6379",
        ]

        for url in test_urls:
            content = f'DATABASE_URL = "{url}"'
            detections = detector.detect(content)
            assert len(detections) > 0
            assert any(d.secret_type == SecretType.DATABASE_URL for d in detections)

    def test_high_entropy_detection(self):
        """Test high entropy string detection"""
        detector = SecretsDetector(enable_entropy_analysis=True)

        # High entropy string (should be detected)
        high_entropy = '"aB3xK9mQ7pL2wE5rT8uY1iO4sD6fG0hJ2kL5mN8pQ"'
        detections = detector.detect(high_entropy)
        assert len(detections) > 0
        assert any(d.secret_type == SecretType.HIGH_ENTROPY_STRING for d in detections)

        # Low entropy string (should not be detected)
        low_entropy = '"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"'
        detections = detector.detect(low_entropy)
        # Should not detect low entropy
        entropy_detections = [
            d for d in detections if d.secret_type == SecretType.HIGH_ENTROPY_STRING
        ]
        assert len(entropy_detections) == 0

    def test_entropy_disabled(self):
        """Test that entropy detection can be disabled"""
        detector = SecretsDetector(enable_entropy_analysis=False)
        high_entropy = '"aB3xK9mQ7pL2wE5rT8uY1iO4sD6fG0hJ2kL5mN8pQ"'
        detections = detector.detect(high_entropy)

        # Should not detect high entropy when disabled
        entropy_detections = [
            d for d in detections if d.secret_type == SecretType.HIGH_ENTROPY_STRING
        ]
        assert len(entropy_detections) == 0

    def test_custom_pattern(self):
        """Test custom pattern addition"""
        detector = SecretsDetector()
        detector.add_custom_pattern(
            name="acme_api_key", pattern=r"ACME_[A-Z0-9]{32}", severity="high"
        )

        # Exactly 32 characters after ACME_ prefix (37 total)
        content = "ACME_" + "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"
        detections = detector.detect(content)

        assert len(detections) > 0
        assert any(d.metadata.get("custom_pattern") == "acme_api_key" for d in detections)

    def test_custom_pattern_removal(self):
        """Test custom pattern removal"""
        detector = SecretsDetector()
        detector.add_custom_pattern(name="test_pattern", pattern=r"TEST_[0-9]{10}", severity="low")

        assert detector.remove_custom_pattern("test_pattern")
        assert not detector.remove_custom_pattern("nonexistent_pattern")

    def test_invalid_custom_pattern(self):
        """Test that invalid regex patterns are rejected"""
        detector = SecretsDetector()

        with pytest.raises(ValueError):
            detector.add_custom_pattern(
                name="bad_pattern", pattern=r"[invalid(regex", severity="high"
            )

    def test_invalid_severity(self):
        """Test that invalid severity levels are rejected"""
        detector = SecretsDetector()

        with pytest.raises(ValueError):
            detector.add_custom_pattern(
                name="test_pattern", pattern=r"TEST_\d+", severity="invalid_severity"
            )

    def test_secret_redaction(self):
        """Test that actual secret values are never exposed"""
        detector = SecretsDetector()
        secret_value = "sk-ant-super-secret-key-12345678901234567890123456789012345678901234567890123456789012345678901234567890"
        content = f'api_key = "{secret_value}"'

        detections = detector.detect(content)

        assert len(detections) > 0

        for detection in detections:
            # Secret value should never appear in any field
            assert secret_value not in detection.context_snippet
            assert secret_value not in str(detection.metadata)

            # Should have [REDACTED] instead
            assert "[REDACTED]" in detection.context_snippet

    def test_line_number_accuracy(self):
        """Test that line numbers are correctly reported"""
        detector = SecretsDetector()
        content = """Line 1
Line 2
Line 3 with api_key = "sk-ant-api03-abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012pqr"
Line 4
Line 5"""

        detections = detector.detect(content)

        assert len(detections) > 0
        # Secret is on line 3
        assert any(d.line_number == 3 for d in detections)

    def test_multiple_secrets_same_line(self):
        """Test detection of multiple secrets on the same line"""
        detector = SecretsDetector()
        content = 'aws_key = "AKIAIOSFODNN7EXAMPLE" and password = "secret123"'

        detections = detector.detect(content)

        # Should detect both secrets
        assert len(detections) >= 2

    def test_empty_content(self):
        """Test handling of empty content"""
        detector = SecretsDetector()
        detections = detector.detect("")

        assert len(detections) == 0

    def test_no_secrets(self):
        """Test that clean code produces no detections"""
        detector = SecretsDetector()
        clean_code = """
        def calculate_sum(a, b):
            return a + b

        result = calculate_sum(10, 20)
        print(result)
        """

        detections = detector.detect(clean_code)

        assert len(detections) == 0

    def test_statistics(self):
        """Test statistics reporting"""
        detector = SecretsDetector()
        stats = detector.get_statistics()

        assert "builtin_patterns" in stats
        assert "custom_patterns" in stats
        assert "total_patterns" in stats
        assert "entropy_analysis_enabled" in stats
        assert stats["builtin_patterns"] > 0
        assert stats["total_patterns"] >= stats["builtin_patterns"]

    def test_detection_to_dict(self):
        """Test SecretDetection serialization"""
        detection = SecretDetection(
            secret_type=SecretType.GENERIC_API_KEY,
            severity=Severity.HIGH,
            line_number=1,
            column_start=0,
            column_end=10,
            context_snippet="api_key = [REDACTED]",
            confidence=1.0,
            metadata={"test": "value"},
        )

        result = detection.to_dict()

        assert result["secret_type"] == "generic_api_key"
        assert result["severity"] == "high"
        assert result["line_number"] == 1
        assert result["confidence"] == 1.0
        assert result["metadata"]["test"] == "value"

    def test_convenience_function(self):
        """Test the convenience detect_secrets function"""
        content = 'api_key = "sk-test-abc123xyz789def456ghi789jkl012"'
        detections = detect_secrets(content)

        assert len(detections) > 0
        assert isinstance(detections[0], SecretDetection)

    def test_performance_large_file(self):
        """Test performance with large files"""
        import time

        detector = SecretsDetector()

        # Create a large file (10,000 lines)
        large_content = "\n".join([f"line {i}: some code here" for i in range(10000)])
        # Add a secret in the middle
        lines = large_content.split("\n")
        lines[5000] = (
            'api_key = "sk-ant-api03-abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012pqr"'
        )
        large_content = "\n".join(lines)

        start_time = time.time()
        detections = detector.detect(large_content)
        elapsed_time = time.time() - start_time

        assert len(detections) > 0
        assert elapsed_time < 5.0  # Should complete in less than 5 seconds


class TestSecretsDetectorIntegration:
    """Integration tests for real-world scenarios"""

    def test_config_file_scanning(self):
        """Test scanning a typical config file"""
        detector = SecretsDetector()
        config_file = """
        # Application Configuration
        APP_NAME = "MyApp"
        DEBUG = True

        # API Keys
        ANTHROPIC_API_KEY = "sk-ant-api03-abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012pqr"
        OPENAI_API_KEY = "sk-proj-abc123xyz789def456"

        # Database
        DATABASE_URL = "postgres://user:password@localhost:5432/mydb"

        # Feature Flags
        ENABLE_FEATURE_X = True
        """

        detections = detector.detect(config_file)

        # Should detect API keys and database URL
        assert len(detections) >= 3
        assert any(d.severity == Severity.HIGH for d in detections)

    def test_code_file_scanning(self):
        """Test scanning a Python code file"""
        detector = SecretsDetector()
        python_code = """
        import os
        from anthropic import Anthropic

        # BAD: Hardcoded API key
        client = Anthropic(api_key="sk-ant-api03-abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012pqr")

        # GOOD: From environment variable
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        def main():
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                messages=[{"role": "user", "content": "Hello"}]
            )
            print(response.content)
        """

        detections = detector.detect(python_code)

        # Should detect the hardcoded API key
        assert len(detections) > 0
        # Should NOT detect the os.getenv call as a secret
        assert all("os.getenv" not in d.context_snippet for d in detections)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
