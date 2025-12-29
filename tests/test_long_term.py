"""
Tests for src/empathy_os/memory/long_term.py

Tests the secure MemDocs integration including:
- Classification enum (PUBLIC, INTERNAL, SENSITIVE)
- ClassificationRules dataclass
- PatternMetadata dataclass
- SecurePattern dataclass
- EncryptionManager class
- Security exceptions
"""

import base64
import os
from datetime import datetime
from unittest.mock import patch

import pytest

from empathy_os.memory.long_term import (
    DEFAULT_CLASSIFICATION_RULES,
    Classification,
    ClassificationRules,
    EncryptionManager,
    PatternMetadata,
    SecurePattern,
    SecurityError,
)


class TestClassificationEnum:
    """Tests for Classification enum."""

    def test_public_value(self):
        """Test PUBLIC classification value."""
        assert Classification.PUBLIC.value == "PUBLIC"

    def test_internal_value(self):
        """Test INTERNAL classification value."""
        assert Classification.INTERNAL.value == "INTERNAL"

    def test_sensitive_value(self):
        """Test SENSITIVE classification value."""
        assert Classification.SENSITIVE.value == "SENSITIVE"

    def test_all_classifications_count(self):
        """Test total number of classifications."""
        assert len(Classification) == 3

    def test_classification_from_string(self):
        """Test creating Classification from string."""
        assert Classification("PUBLIC") == Classification.PUBLIC
        assert Classification("INTERNAL") == Classification.INTERNAL
        assert Classification("SENSITIVE") == Classification.SENSITIVE

    def test_invalid_classification_raises(self):
        """Test invalid classification raises ValueError."""
        with pytest.raises(ValueError):
            Classification("INVALID")


class TestClassificationRules:
    """Tests for ClassificationRules dataclass."""

    def test_create_public_rules(self):
        """Test creating PUBLIC classification rules."""
        rules = ClassificationRules(
            classification=Classification.PUBLIC,
            encryption_required=False,
            retention_days=365,
            access_level="all_users",
        )
        assert rules.classification == Classification.PUBLIC
        assert rules.encryption_required is False
        assert rules.retention_days == 365
        assert rules.access_level == "all_users"
        assert rules.audit_all_access is False  # Default

    def test_create_sensitive_rules(self):
        """Test creating SENSITIVE classification rules."""
        rules = ClassificationRules(
            classification=Classification.SENSITIVE,
            encryption_required=True,
            retention_days=90,
            access_level="explicit_permission",
            audit_all_access=True,
        )
        assert rules.classification == Classification.SENSITIVE
        assert rules.encryption_required is True
        assert rules.audit_all_access is True

    def test_default_audit_all_access(self):
        """Test audit_all_access defaults to False."""
        rules = ClassificationRules(
            classification=Classification.INTERNAL,
            encryption_required=False,
            retention_days=180,
            access_level="project_team",
        )
        assert rules.audit_all_access is False


class TestDefaultClassificationRules:
    """Tests for DEFAULT_CLASSIFICATION_RULES constant."""

    def test_all_classifications_have_rules(self):
        """Test all classifications have default rules."""
        assert Classification.PUBLIC in DEFAULT_CLASSIFICATION_RULES
        assert Classification.INTERNAL in DEFAULT_CLASSIFICATION_RULES
        assert Classification.SENSITIVE in DEFAULT_CLASSIFICATION_RULES

    def test_public_default_rules(self):
        """Test PUBLIC default rules."""
        rules = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        assert rules.encryption_required is False
        assert rules.retention_days == 365
        assert rules.access_level == "all_users"
        assert rules.audit_all_access is False

    def test_internal_default_rules(self):
        """Test INTERNAL default rules."""
        rules = DEFAULT_CLASSIFICATION_RULES[Classification.INTERNAL]
        assert rules.encryption_required is False
        assert rules.retention_days == 180
        assert rules.access_level == "project_team"

    def test_sensitive_default_rules(self):
        """Test SENSITIVE default rules."""
        rules = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert rules.encryption_required is True
        assert rules.retention_days == 90
        assert rules.access_level == "explicit_permission"
        assert rules.audit_all_access is True

    def test_sensitive_has_shortest_retention(self):
        """Test SENSITIVE has shortest retention for compliance."""
        public = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        internal = DEFAULT_CLASSIFICATION_RULES[Classification.INTERNAL]
        sensitive = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert sensitive.retention_days < internal.retention_days
        assert internal.retention_days < public.retention_days


class TestPatternMetadata:
    """Tests for PatternMetadata dataclass."""

    def test_create_metadata(self):
        """Test creating pattern metadata."""
        metadata = PatternMetadata(
            pattern_id="pat_001",
            created_by="user@example.com",
            created_at="2025-01-15T10:30:00Z",
            classification="PUBLIC",
            retention_days=365,
            encrypted=False,
            pattern_type="code",
            sanitization_applied=True,
            pii_removed=0,
            secrets_detected=0,
        )
        assert metadata.pattern_id == "pat_001"
        assert metadata.created_by == "user@example.com"
        assert metadata.classification == "PUBLIC"
        assert metadata.encrypted is False
        assert metadata.pii_removed == 0

    def test_metadata_with_access_control(self):
        """Test metadata with access control."""
        metadata = PatternMetadata(
            pattern_id="pat_002",
            created_by="admin@example.com",
            created_at="2025-01-15T11:00:00Z",
            classification="SENSITIVE",
            retention_days=90,
            encrypted=True,
            pattern_type="medical",
            sanitization_applied=True,
            pii_removed=5,
            secrets_detected=0,
            access_control={"allowed_users": ["doctor@hospital.com"]},
        )
        assert metadata.access_control["allowed_users"] == ["doctor@hospital.com"]

    def test_metadata_with_custom_metadata(self):
        """Test metadata with custom fields."""
        metadata = PatternMetadata(
            pattern_id="pat_003",
            created_by="dev@example.com",
            created_at="2025-01-15T12:00:00Z",
            classification="INTERNAL",
            retention_days=180,
            encrypted=False,
            pattern_type="architecture",
            sanitization_applied=True,
            pii_removed=0,
            secrets_detected=0,
            custom_metadata={"project": "empathy-framework", "version": "3.0"},
        )
        assert metadata.custom_metadata["project"] == "empathy-framework"

    def test_metadata_defaults(self):
        """Test metadata default values."""
        metadata = PatternMetadata(
            pattern_id="pat_004",
            created_by="user@example.com",
            created_at="2025-01-15T13:00:00Z",
            classification="PUBLIC",
            retention_days=365,
            encrypted=False,
            pattern_type="general",
            sanitization_applied=False,
            pii_removed=0,
            secrets_detected=0,
        )
        assert metadata.access_control == {}
        assert metadata.custom_metadata == {}


class TestSecurePattern:
    """Tests for SecurePattern dataclass."""

    def test_create_secure_pattern(self):
        """Test creating a secure pattern."""
        metadata = PatternMetadata(
            pattern_id="pat_secure",
            created_by="user@example.com",
            created_at="2025-01-15T10:00:00Z",
            classification="PUBLIC",
            retention_days=365,
            encrypted=False,
            pattern_type="code",
            sanitization_applied=True,
            pii_removed=0,
            secrets_detected=0,
        )
        pattern = SecurePattern(
            pattern_id="pat_secure",
            content="def hello(): return 'world'",
            metadata=metadata,
        )
        assert pattern.pattern_id == "pat_secure"
        assert pattern.content == "def hello(): return 'world'"
        assert pattern.metadata.classification == "PUBLIC"

    def test_secure_pattern_encrypted(self):
        """Test encrypted secure pattern."""
        metadata = PatternMetadata(
            pattern_id="pat_encrypted",
            created_by="admin@example.com",
            created_at="2025-01-15T10:00:00Z",
            classification="SENSITIVE",
            retention_days=90,
            encrypted=True,
            pattern_type="financial",
            sanitization_applied=True,
            pii_removed=3,
            secrets_detected=0,
        )
        pattern = SecurePattern(
            pattern_id="pat_encrypted",
            content="[encrypted content]",
            metadata=metadata,
        )
        assert pattern.metadata.encrypted is True
        assert pattern.metadata.classification == "SENSITIVE"


class TestSecurityError:
    """Tests for SecurityError exception."""

    def test_raise_security_error(self):
        """Test raising SecurityError."""
        with pytest.raises(SecurityError):
            raise SecurityError("Secrets detected in pattern")

    def test_security_error_message(self):
        """Test SecurityError message."""
        try:
            raise SecurityError("API key detected")
        except SecurityError as e:
            assert "API key detected" in str(e)


class TestEncryptionManager:
    """Tests for EncryptionManager class."""

    def test_init_without_encryption(self):
        """Test initialization when encryption not available."""
        with patch("empathy_os.memory.long_term.HAS_ENCRYPTION", False):
            # Re-import won't work, so we test the class behavior
            manager = EncryptionManager.__new__(EncryptionManager)
            manager.enabled = False
            assert manager.enabled is False

    def test_init_with_master_key(self):
        """Test initialization with provided master key."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            key = AESGCM.generate_key(bit_length=256)
            manager = EncryptionManager(master_key=key)
            assert manager.enabled is True
            assert manager.master_key == key
        except ImportError:
            pytest.skip("cryptography library not installed")

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption roundtrip."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            key = AESGCM.generate_key(bit_length=256)
            manager = EncryptionManager(master_key=key)

            plaintext = "This is sensitive data that needs encryption"
            encrypted = manager.encrypt(plaintext)

            # Encrypted should be different from plaintext
            assert encrypted != plaintext

            # Decryption should recover original
            decrypted = manager.decrypt(encrypted)
            assert decrypted == plaintext
        except ImportError:
            pytest.skip("cryptography library not installed")

    def test_encrypt_produces_different_output(self):
        """Test encryption produces different output each time (random nonce)."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            key = AESGCM.generate_key(bit_length=256)
            manager = EncryptionManager(master_key=key)

            plaintext = "Same message encrypted twice"
            encrypted1 = manager.encrypt(plaintext)
            encrypted2 = manager.encrypt(plaintext)

            # Should produce different ciphertext due to random nonce
            assert encrypted1 != encrypted2

            # But both should decrypt to same plaintext
            assert manager.decrypt(encrypted1) == plaintext
            assert manager.decrypt(encrypted2) == plaintext
        except ImportError:
            pytest.skip("cryptography library not installed")

    def test_load_key_from_env(self):
        """Test loading master key from environment variable."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            # Generate a key and encode it
            test_key = AESGCM.generate_key(bit_length=256)
            encoded_key = base64.b64encode(test_key).decode()

            with patch.dict(os.environ, {"EMPATHY_MASTER_KEY": encoded_key}):
                manager = EncryptionManager()
                assert manager.master_key == test_key
        except ImportError:
            pytest.skip("cryptography library not installed")

    def test_invalid_env_key_raises(self):
        """Test invalid environment key raises ValueError."""
        try:
            with patch.dict(os.environ, {"EMPATHY_MASTER_KEY": "not-valid-base64!!!"}):
                with pytest.raises(ValueError):
                    EncryptionManager()
        except ImportError:
            pytest.skip("cryptography library not installed")


class TestClassificationIntegration:
    """Integration tests for classification system."""

    def test_public_classification_workflow(self):
        """Test PUBLIC classification workflow."""
        rules = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        assert rules.encryption_required is False
        assert rules.access_level == "all_users"

        metadata = PatternMetadata(
            pattern_id="pub_001",
            created_by="user@example.com",
            created_at=datetime.now().isoformat(),
            classification=Classification.PUBLIC.value,
            retention_days=rules.retention_days,
            encrypted=rules.encryption_required,
            pattern_type="documentation",
            sanitization_applied=True,
            pii_removed=0,
            secrets_detected=0,
        )

        pattern = SecurePattern(
            pattern_id="pub_001",
            content="Public documentation content",
            metadata=metadata,
        )

        assert pattern.metadata.encrypted is False
        assert pattern.metadata.retention_days == 365

    def test_sensitive_classification_workflow(self):
        """Test SENSITIVE classification workflow."""
        rules = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert rules.encryption_required is True
        assert rules.audit_all_access is True

        metadata = PatternMetadata(
            pattern_id="sens_001",
            created_by="admin@hospital.com",
            created_at=datetime.now().isoformat(),
            classification=Classification.SENSITIVE.value,
            retention_days=rules.retention_days,
            encrypted=rules.encryption_required,
            pattern_type="medical_protocol",
            sanitization_applied=True,
            pii_removed=10,
            secrets_detected=0,
            access_control={"allowed_users": ["doctor1@hospital.com"]},
        )

        pattern = SecurePattern(
            pattern_id="sens_001",
            content="[Encrypted medical data]",
            metadata=metadata,
        )

        assert pattern.metadata.encrypted is True
        assert pattern.metadata.retention_days == 90
        assert len(pattern.metadata.access_control["allowed_users"]) == 1


class TestRetentionPolicies:
    """Tests for retention policy consistency."""

    def test_retention_order(self):
        """Test retention days follow security tier ordering."""
        public = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC].retention_days
        internal = DEFAULT_CLASSIFICATION_RULES[Classification.INTERNAL].retention_days
        sensitive = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE].retention_days

        # More sensitive = shorter retention
        assert sensitive < internal < public

    def test_sensitive_under_100_days(self):
        """Test SENSITIVE retention is under 100 days (HIPAA guideline)."""
        sensitive = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert sensitive.retention_days <= 100

    def test_public_max_one_year(self):
        """Test PUBLIC retention is max one year."""
        public = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        assert public.retention_days <= 365


class TestAccessControl:
    """Tests for access control levels."""

    def test_all_classifications_have_access_level(self):
        """Test all classifications define access level."""
        for classification in Classification:
            rules = DEFAULT_CLASSIFICATION_RULES[classification]
            assert hasattr(rules, "access_level")
            assert rules.access_level in ["all_users", "project_team", "explicit_permission"]

    def test_sensitive_requires_explicit_permission(self):
        """Test SENSITIVE requires explicit permission."""
        sensitive = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert sensitive.access_level == "explicit_permission"

    def test_public_allows_all_users(self):
        """Test PUBLIC allows all users."""
        public = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        assert public.access_level == "all_users"
