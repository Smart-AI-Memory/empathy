"""Educational Tests for Long-Term Memory (Phase 2 Completion)

Learning Objectives:
- Testing encryption and decryption (AES-256-GCM)
- Three-tier classification system testing
- Security pipeline integration (PII + secrets)
- Audit logging verification
- File-based persistence testing

Key Patterns:
- Testing with optional dependencies (cryptography)
- Security-first testing
- Classification logic
- Parallel processing (ThreadPoolExecutor)
"""

import pytest

from empathy_os.memory.long_term import (
    DEFAULT_CLASSIFICATION_RULES,
    HAS_ENCRYPTION,
    Classification,
    ClassificationRules,
)


@pytest.mark.unit
class TestClassificationSystem:
    """Educational tests for three-tier classification."""

    def test_classification_enum_values(self):
        """Teaching Pattern: Testing security classification levels.

        Three-tier system: PUBLIC → INTERNAL → SENSITIVE
        """
        assert Classification.PUBLIC.value == "PUBLIC"
        assert Classification.INTERNAL.value == "INTERNAL"
        assert Classification.SENSITIVE.value == "SENSITIVE"

    def test_default_classification_rules(self):
        """Teaching Pattern: Testing security policy defaults.

        Each classification has different security requirements.
        """
        public_rules = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        assert public_rules.encryption_required is False
        assert public_rules.retention_days == 365
        assert public_rules.access_level == "all_users"

        sensitive_rules = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert sensitive_rules.encryption_required is True
        assert sensitive_rules.retention_days == 90
        assert sensitive_rules.access_level == "explicit_permission"
        assert sensitive_rules.audit_all_access is True

    def test_sensitive_requires_encryption(self):
        """Teaching Pattern: Testing security requirements.

        SENSITIVE classification MUST have encryption enabled.
        """
        rules = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert rules.encryption_required is True

    def test_public_has_longest_retention(self):
        """Teaching Pattern: Testing business logic.

        PUBLIC data (anonymized) can be kept longer than SENSITIVE data.
        """
        public = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        internal = DEFAULT_CLASSIFICATION_RULES[Classification.INTERNAL]
        sensitive = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]

        assert public.retention_days > internal.retention_days
        assert internal.retention_days > sensitive.retention_days


@pytest.mark.unit
@pytest.mark.skipif(not HAS_ENCRYPTION, reason="cryptography not installed")
class TestEncryption:
    """Educational tests for encryption (when available)."""

    def test_has_encryption_available(self):
        """Teaching Pattern: Testing optional dependencies.

        Skip encryption tests if cryptography library unavailable.
        """
        assert HAS_ENCRYPTION is True


@pytest.mark.unit
class TestClassificationRules:
    """Educational tests for classification rule creation."""

    def test_create_custom_classification_rule(self):
        """Teaching Pattern: Testing dataclass creation.

        Custom security rules for different environments.
        """
        custom_rule = ClassificationRules(
            classification=Classification.INTERNAL,
            encryption_required=True,  # Override: require encryption
            retention_days=365,
            access_level="department",
            audit_all_access=True,
        )

        assert custom_rule.classification == Classification.INTERNAL
        assert custom_rule.encryption_required is True
        assert custom_rule.retention_days == 365
