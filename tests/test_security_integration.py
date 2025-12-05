"""
Integration tests for Phase 2 Security Controls

Tests the complete security pipeline:
- PII scrubbing
- Secrets detection
- Audit logging
- Secure MemDocs integration
- Claude Memory + Security integration

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig
from empathy_llm_toolkit.security import (
    AuditLogger,
    PIIScrubber,
    SecretsDetector,
    SecureMemDocsIntegration,
)


class TestSecurityPipeline:
    """Test complete security pipeline integration"""

    def test_pii_scrubbing_pipeline(self):
        """Test PII scrubbing in complete pipeline"""
        scrubber = PIIScrubber()

        # Healthcare scenario (HIPAA)
        content = """
        Patient: John Smith
        Email: john.smith@hospital.com
        Phone: 555-123-4567
        MRN: 1234567
        """

        sanitized, detections = scrubber.scrub(content)

        assert "john.smith@hospital.com" not in sanitized
        assert "555-123-4567" not in sanitized
        assert "[EMAIL]" in sanitized
        assert "[PHONE]" in sanitized
        assert "[MRN]" in sanitized
        assert len(detections) == 3  # email, phone, mrn

    def test_secrets_detection_blocks_storage(self):
        """Test that secrets detection blocks pattern storage"""
        detector = SecretsDetector()

        # Content with secrets
        content = """
        api_key = "sk_live_abc123xyz789"
        password = "SuperSecret123"
        """

        detections = detector.detect(content)

        assert len(detections) >= 2
        assert any(d.secret_type.name == "GENERIC_API_KEY" for d in detections)
        assert any(d.secret_type.name == "PASSWORD" for d in detections)

        # Verify no actual secret values in detection
        for detection in detections:
            assert "sk_live" not in str(detection.to_dict())
            assert "SuperSecret" not in str(detection.to_dict())

    def test_audit_logging_compliance(self, tmp_path):
        """Test audit logging meets compliance requirements"""
        audit_log_dir = tmp_path / "audit"
        audit_log_dir.mkdir()

        logger = AuditLogger(log_dir=str(audit_log_dir))

        # Log various events
        logger.log_llm_request(
            user_id="test@company.com",
            empathy_level=3,
            provider="anthropic",
            model="claude-sonnet-4",
            memory_sources=["enterprise", "user"],
            pii_count=0,
            secrets_count=0,
        )

        logger.log_pattern_store(
            user_id="test@company.com",
            pattern_id="pat_123",
            pattern_type="test_pattern",
            classification="INTERNAL",
            pii_scrubbed=2,
            secrets_detected=0,
        )

        logger.log_security_violation(
            user_id="test@company.com",
            violation_type="secrets_detected",
            details={"secret_type": "api_key", "blocked": True},
            severity="HIGH",
        )

        # Verify audit log exists and is properly formatted
        audit_file = audit_log_dir / "audit.jsonl"
        assert audit_file.exists()

        # Query logs
        llm_requests = logger.query(event_type="llm_request")
        assert len(llm_requests) == 1

        violations = logger.query(event_type="security_violation")
        assert len(violations) == 1

        # Compliance report
        report = logger.get_compliance_report()
        assert "compliance_metrics" in report
        assert report["compliance_metrics"]["gdpr_compliant_rate"] == 1.0
        assert report["compliance_metrics"]["hipaa_compliant_rate"] == 1.0
        assert report["compliance_metrics"]["soc2_compliant_rate"] == 1.0

    def test_secure_memdocs_full_pipeline(self, tmp_path):
        """Test complete SecureMemDocs pipeline"""
        # Setup
        config = ClaudeMemoryConfig(enabled=False)  # Simplified for test
        integration = SecureMemDocsIntegration(config)
        integration.storage.storage_dir = tmp_path / "memdocs"

        # Test 1: Store PUBLIC pattern (no PII, no secrets)
        public_pattern = "Standard Python sorting algorithm using quicksort"
        result = integration.store_pattern(
            content=public_pattern,
            pattern_type="algorithm",
            user_id="dev@company.com",
            auto_classify=True,
        )

        assert result["pattern_id"]
        assert result["classification"] == "PUBLIC"
        assert result["sanitization_report"]["pii_count"] == 0
        assert result["sanitization_report"]["secrets_detected"] == 0

        # Test 2: Store INTERNAL pattern (proprietary, no PII/secrets)
        internal_pattern = """
        Our proprietary algorithm for Level 4 anticipatory predictions:
        1. Analyze trajectory using confidence scoring
        2. Identify leverage points
        3. Generate actionable alerts
        """
        result = integration.store_pattern(
            content=internal_pattern,
            pattern_type="algorithm",
            user_id="dev@company.com",
            auto_classify=True,
        )

        assert result["classification"] == "INTERNAL"

        # Test 3: Store SENSITIVE pattern (healthcare, with PII)
        sensitive_pattern = """
        Patient handoff protocol:
        Contact Dr. Smith at drsmith@hospital.com
        Patient MRN: 7654321
        """
        result = integration.store_pattern(
            content=sensitive_pattern,
            pattern_type="clinical_protocol",
            user_id="doctor@hospital.com",
            auto_classify=True,
        )

        assert result["classification"] == "SENSITIVE"
        assert result["sanitization_report"]["pii_count"] > 0

        # Verify PII was scrubbed
        retrieved = integration.retrieve_pattern(
            pattern_id=result["pattern_id"],
            user_id="doctor@hospital.com",
            check_permissions=True,
        )
        assert "drsmith@hospital.com" not in retrieved["content"]
        assert "[EMAIL]" in retrieved["content"]
        assert "[MRN]" in retrieved["content"]

        # Test 4: Secrets should block storage
        secret_pattern = "api_key = 'sk_live_abc123xyz789'"
        from empathy_llm_toolkit.security.secure_memdocs import SecurityError

        with pytest.raises(SecurityError, match="Secrets detected"):
            integration.store_pattern(
                content=secret_pattern,
                pattern_type="config",
                user_id="dev@company.com",
                auto_classify=True,
            )

    def test_classification_accuracy(self, tmp_path):
        """Test auto-classification accuracy"""
        config = ClaudeMemoryConfig(enabled=False)
        integration = SecureMemDocsIntegration(config)
        integration.storage.storage_dir = tmp_path / "memdocs"

        # Test healthcare classification
        healthcare = "Patient diagnosis: diabetes type 2"
        result = integration.store_pattern(
            healthcare, "medical", "doctor@hospital.com", auto_classify=True
        )
        assert result["classification"] == "SENSITIVE"

        # Test financial classification
        financial = "Credit card processing with PCI DSS compliance"
        result = integration.store_pattern(
            financial, "finance", "fin@company.com", auto_classify=True
        )
        assert result["classification"] == "SENSITIVE"

        # Test proprietary classification
        proprietary = "Our confidential trade secret algorithm"
        result = integration.store_pattern(
            proprietary, "algorithm", "dev@company.com", auto_classify=True
        )
        assert result["classification"] == "INTERNAL"

        # Test public classification
        public = "Standard Python best practices"
        result = integration.store_pattern(public, "guide", "dev@company.com", auto_classify=True)
        assert result["classification"] == "PUBLIC"

    def test_end_to_end_healthcare_workflow(self, tmp_path):
        """
        Test complete end-to-end workflow for healthcare scenario (HIPAA).

        This simulates a real-world healthcare use case with full security pipeline.
        """
        # Setup
        config = ClaudeMemoryConfig(enabled=False)
        integration = SecureMemDocsIntegration(config)
        integration.storage.storage_dir = tmp_path / "memdocs"

        # Healthcare pattern with PII
        pattern = """
        Clinical Protocol: Vital Signs Monitoring

        For patient John Doe (MRN: 1234567):
        - Blood pressure: 120/80 mmHg
        - Heart rate: 72 bpm
        - Temperature: 98.6°F

        Contact: nurse@hospital.com
        Phone: (555) 987-6543
        """

        # Store pattern (should scrub PII and classify as SENSITIVE)
        result = integration.store_pattern(
            content=pattern,
            pattern_type="clinical_protocol",
            user_id="nurse@hospital.com",
            auto_classify=True,
        )

        # Verify results
        assert result["classification"] == "SENSITIVE"
        assert result["sanitization_report"]["pii_count"] >= 3  # MRN, email, phone

        # Retrieve and verify PII was scrubbed
        retrieved = integration.retrieve_pattern(
            pattern_id=result["pattern_id"],
            user_id="nurse@hospital.com",
            check_permissions=True,
        )

        content = retrieved["content"]
        assert "nurse@hospital.com" not in content
        assert "555" not in content
        assert "[EMAIL]" in content
        assert "[PHONE]" in content
        assert "[MRN]" in content

        # Verify metadata
        assert retrieved["metadata"]["classification"] == "SENSITIVE"
        assert retrieved["metadata"]["sanitization_applied"] is True
        assert retrieved["metadata"]["retention_days"] == 90  # HIPAA minimum

    def test_performance_large_scale(self, tmp_path):
        """Test performance with many patterns"""
        config = ClaudeMemoryConfig(enabled=False)
        integration = SecureMemDocsIntegration(config)
        integration.storage.storage_dir = tmp_path / "memdocs"

        # Store 100 patterns
        pattern_ids = []
        for i in range(100):
            pattern = f"Test pattern #{i} with some content"
            result = integration.store_pattern(
                pattern, "test", "dev@company.com", auto_classify=True
            )
            pattern_ids.append(result["pattern_id"])

        # Verify all stored
        assert len(pattern_ids) == 100

        # Retrieve all
        for pattern_id in pattern_ids:
            retrieved = integration.retrieve_pattern(
                pattern_id, "dev@company.com", check_permissions=True
            )
            assert retrieved["content"]

    def test_error_handling(self, tmp_path):
        """Test error handling in security pipeline"""
        config = ClaudeMemoryConfig(enabled=False)
        integration = SecureMemDocsIntegration(config)
        integration.storage.storage_dir = tmp_path / "memdocs"

        # Test 1: Empty content
        with pytest.raises(ValueError, match="Content cannot be empty"):
            integration.store_pattern("", "test", "user@company.com", auto_classify=True)

        # Test 2: Invalid pattern type
        # Should still work but classify as PUBLIC
        result = integration.store_pattern(
            "Content", "invalid_type", "user@company.com", auto_classify=True
        )
        assert result["classification"] == "PUBLIC"

        # Test 3: Retrieve non-existent pattern
        with pytest.raises(ValueError):
            integration.retrieve_pattern("nonexistent", "user@company.com", check_permissions=True)


class TestIntegrationWithClaudeMemory:
    """Test integration of security controls with Claude Memory"""

    def test_security_policies_from_claude_memory(self, tmp_path):
        """Test loading security policies from CLAUDE.md"""
        # Create test CLAUDE.md with security policies
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text(
            """
# Security Policies

## PII Protection
- Scrub all email addresses
- Scrub all phone numbers
- Scrub all SSNs

## Secrets Detection
- Block API keys
- Block passwords
- Block private keys

## Classification Rules
- Healthcare patterns: SENSITIVE
- Proprietary patterns: INTERNAL
- General patterns: PUBLIC
"""
        )

        # Load config with security policies
        config = ClaudeMemoryConfig(
            enabled=True, load_enterprise=False, load_user=False, load_project=True
        )

        from empathy_llm_toolkit.claude_memory import ClaudeMemoryLoader

        loader = ClaudeMemoryLoader(config)
        memory = loader.load_all_memory(str(tmp_path))

        # Verify security policies are loaded
        assert "PII Protection" in memory
        assert "Secrets Detection" in memory
        assert "Classification Rules" in memory

    def test_full_stack_integration(self, tmp_path):
        """Test complete integration of all Phase 2 components"""
        # This is the ultimate integration test showing everything working together

        # 1. Setup Claude Memory with security policies
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").write_text("# Security enabled\nPII scrubbing: ON")

        # 2. Setup security integration
        config = ClaudeMemoryConfig(
            enabled=True, load_enterprise=False, load_user=False, load_project=True
        )
        integration = SecureMemDocsIntegration(config)
        integration.storage.storage_dir = tmp_path / "memdocs"

        # 3. Store pattern with full security pipeline
        pattern = """
        Healthcare analysis for patient@hospital.com
        MRN: 9876543
        Diagnosis: Confidential medical information
        """

        result = integration.store_pattern(
            pattern, "clinical", "doctor@hospital.com", auto_classify=True
        )

        # 4. Verify everything worked
        assert result["classification"] == "SENSITIVE"
        assert result["sanitization_report"]["pii_count"] >= 2

        # 5. Verify audit trail was created
        from pathlib import Path

        audit_file = Path(integration.audit_logger.log_dir) / "audit.jsonl"
        assert audit_file.exists()

        # 6. Verify pattern can be retrieved with proper access
        retrieved = integration.retrieve_pattern(
            result["pattern_id"], "doctor@hospital.com", check_permissions=True
        )
        assert "[EMAIL]" in retrieved["content"]
        assert "[MRN]" in retrieved["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
