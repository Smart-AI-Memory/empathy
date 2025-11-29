"""
Tests for Secure MemDocs Integration Module

Tests for the enterprise security pipeline including PII scrubbing,
secrets detection, classification, and encryption.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from empathy_llm_toolkit.security.secure_memdocs import (
    DEFAULT_CLASSIFICATION_RULES,
    Classification,
    ClassificationRules,
    MemDocsStorage,
    PatternMetadata,
    SecureMemDocsIntegration,
    SecurityError,
)


class TestClassification:
    """Tests for Classification enum"""

    def test_classification_values(self):
        """Test classification enum values"""
        assert Classification.PUBLIC.value == "PUBLIC"
        assert Classification.INTERNAL.value == "INTERNAL"
        assert Classification.SENSITIVE.value == "SENSITIVE"

    def test_classification_from_string(self):
        """Test creating classification from string"""
        assert Classification("PUBLIC") == Classification.PUBLIC
        assert Classification("INTERNAL") == Classification.INTERNAL
        assert Classification("SENSITIVE") == Classification.SENSITIVE

    def test_classification_ordering(self):
        """Test classifications can be compared by name"""
        classifications = [Classification.SENSITIVE, Classification.PUBLIC, Classification.INTERNAL]
        sorted_names = sorted([c.value for c in classifications])
        assert sorted_names == ["INTERNAL", "PUBLIC", "SENSITIVE"]


class TestClassificationRules:
    """Tests for ClassificationRules dataclass"""

    def test_rules_creation(self):
        """Test creating classification rules"""
        rules = ClassificationRules(
            classification=Classification.SENSITIVE,
            encryption_required=True,
            retention_days=90,
            access_level="explicit_permission",
            audit_all_access=True,
        )
        assert rules.classification == Classification.SENSITIVE
        assert rules.encryption_required is True
        assert rules.retention_days == 90
        assert rules.access_level == "explicit_permission"
        assert rules.audit_all_access is True

    def test_default_rules_exist(self):
        """Test default classification rules are defined"""
        assert Classification.PUBLIC in DEFAULT_CLASSIFICATION_RULES
        assert Classification.INTERNAL in DEFAULT_CLASSIFICATION_RULES
        assert Classification.SENSITIVE in DEFAULT_CLASSIFICATION_RULES

    def test_sensitive_requires_encryption(self):
        """Test SENSITIVE classification requires encryption"""
        sensitive_rules = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]
        assert sensitive_rules.encryption_required is True

    def test_public_no_encryption(self):
        """Test PUBLIC classification doesn't require encryption"""
        public_rules = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        assert public_rules.encryption_required is False

    def test_internal_rules(self):
        """Test INTERNAL classification rules"""
        internal_rules = DEFAULT_CLASSIFICATION_RULES[Classification.INTERNAL]
        assert internal_rules.encryption_required is False
        assert internal_rules.access_level == "project_team"
        assert internal_rules.retention_days == 180


class TestPatternMetadata:
    """Tests for PatternMetadata dataclass"""

    def test_metadata_creation(self):
        """Test creating pattern metadata"""
        metadata = PatternMetadata(
            pattern_id="test_123",
            created_by="test_user",
            created_at="2025-01-01T00:00:00Z",
            classification="INTERNAL",
            retention_days=180,
            encrypted=False,
            pattern_type="test",
            sanitization_applied=True,
            pii_removed=2,
            secrets_detected=0,
        )
        assert metadata.pattern_id == "test_123"
        assert metadata.created_by == "test_user"
        assert metadata.classification == "INTERNAL"
        assert metadata.pii_removed == 2

    def test_metadata_with_custom_fields(self):
        """Test metadata with custom metadata fields"""
        metadata = PatternMetadata(
            pattern_id="test_456",
            created_by="test_user",
            created_at="2025-01-01T00:00:00Z",
            classification="PUBLIC",
            retention_days=365,
            encrypted=False,
            pattern_type="code",
            sanitization_applied=True,
            pii_removed=0,
            secrets_detected=0,
            custom_metadata={"source": "github", "language": "python"},
        )
        assert metadata.custom_metadata["source"] == "github"
        assert metadata.custom_metadata["language"] == "python"


class TestMemDocsStorage:
    """Tests for MemDocsStorage backend"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def storage(self, temp_storage):
        """Create MemDocsStorage instance"""
        return MemDocsStorage(temp_storage)

    def test_storage_initialization(self, storage, temp_storage):
        """Test storage creates directory"""
        assert Path(temp_storage).exists()

    def test_store_and_retrieve(self, storage):
        """Test storing and retrieving a pattern"""
        pattern_id = "test_pat_001"
        content = "Test pattern content"
        metadata = {"classification": "PUBLIC", "created_by": "test_user"}

        result = storage.store(pattern_id, content, metadata)
        assert result is True

        retrieved = storage.retrieve(pattern_id)
        assert retrieved is not None
        assert retrieved["content"] == content
        assert retrieved["metadata"]["classification"] == "PUBLIC"

    def test_retrieve_nonexistent(self, storage):
        """Test retrieving non-existent pattern returns None"""
        result = storage.retrieve("nonexistent_pattern")
        assert result is None

    def test_delete_pattern(self, storage):
        """Test deleting a pattern"""
        pattern_id = "test_delete_001"
        storage.store(pattern_id, "content", {"test": True})

        # Pattern exists
        assert storage.retrieve(pattern_id) is not None

        # Delete it
        result = storage.delete(pattern_id)
        assert result is True

        # Pattern no longer exists
        assert storage.retrieve(pattern_id) is None

    def test_delete_nonexistent(self, storage):
        """Test deleting non-existent pattern returns False"""
        result = storage.delete("nonexistent_pattern")
        assert result is False

    def test_list_patterns(self, storage):
        """Test listing patterns"""
        storage.store("pat_001", "content1", {"classification": "PUBLIC"})
        storage.store("pat_002", "content2", {"classification": "INTERNAL"})
        storage.store("pat_003", "content3", {"classification": "PUBLIC"})

        all_patterns = storage.list_patterns()
        assert len(all_patterns) == 3

        public_patterns = storage.list_patterns(classification="PUBLIC")
        assert len(public_patterns) == 2


class TestSecureMemDocsIntegration:
    """Tests for SecureMemDocsIntegration"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def integration(self, temp_storage):
        """Create SecureMemDocsIntegration instance"""
        return SecureMemDocsIntegration(
            storage_dir=temp_storage,
            audit_log_dir=temp_storage,
            enable_encryption=False,  # Disable for testing without cryptography
        )

    def test_integration_initialization(self, integration):
        """Test integration initializes correctly"""
        assert integration.pii_scrubber is not None
        assert integration.secrets_detector is not None
        assert integration.storage is not None

    def test_store_public_pattern(self, integration):
        """Test storing a PUBLIC pattern"""
        result = integration.store_pattern(
            content="This is a test pattern",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        assert result is not None
        assert "pattern_id" in result
        assert result["classification"] == "PUBLIC"

    def test_store_pattern_with_email_pii(self, integration):
        """Test storing pattern with email gets scrubbed"""
        result = integration.store_pattern(
            content="Contact us at test@example.com for help",
            pattern_type="contact",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        assert result is not None
        assert result["sanitization_report"]["pii_count"] > 0

    def test_store_and_retrieve_pattern(self, integration):
        """Test storing and retrieving a pattern"""
        # Store a pattern
        store_result = integration.store_pattern(
            content="Test pattern for retrieval",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )

        assert store_result is not None
        pattern_id = store_result["pattern_id"]

        # Retrieve it
        retrieved = integration.retrieve_pattern(
            pattern_id=pattern_id,
            user_id="test_user",
        )

        assert retrieved is not None
        assert "content" in retrieved
        assert "Test pattern for retrieval" in retrieved["content"]

    def test_auto_classification_healthcare(self, integration):
        """Test automatic classification for healthcare content"""
        result = integration.store_pattern(
            content="Patient diagnosis includes important medical information",
            pattern_type="medical",
            user_id="test_user",
            auto_classify=True,
        )
        assert result is not None
        # Healthcare content should be SENSITIVE
        assert result["classification"] == "SENSITIVE"

    def test_auto_classification_proprietary(self, integration):
        """Test automatic classification for proprietary content"""
        result = integration.store_pattern(
            content="This is confidential internal company information",
            pattern_type="business",
            user_id="test_user",
            auto_classify=True,
        )
        assert result is not None
        # Proprietary content should be INTERNAL
        assert result["classification"] == "INTERNAL"

    def test_auto_classification_public(self, integration):
        """Test automatic classification for general content"""
        result = integration.store_pattern(
            content="A generic software pattern for handling loops",
            pattern_type="code",
            user_id="test_user",
            auto_classify=True,
        )
        assert result is not None
        # General content should be PUBLIC
        assert result["classification"] == "PUBLIC"

    def test_secrets_detection_blocks_storage(self, integration):
        """Test that secrets are detected and block storage"""
        content = """
        API_KEY = 'sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890ab'
        This looks like an OpenAI API key
        """

        with pytest.raises(SecurityError):
            integration.store_pattern(
                content=content,
                pattern_type="config",
                user_id="test_user",
                explicit_classification=Classification.PUBLIC,
            )


class TestSecurityPipeline:
    """Tests for the complete security pipeline"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def integration(self, temp_storage):
        """Create integration with full security enabled"""
        return SecureMemDocsIntegration(
            storage_dir=temp_storage,
            audit_log_dir=temp_storage,
            enable_encryption=False,
        )

    def test_pipeline_scrubs_multiple_pii(self, integration):
        """Test pipeline handles multiple PII types"""
        content = """
        User: John Doe
        Email: john.doe@company.com
        Phone: 555-123-4567
        Pattern: Error handling for API calls
        """

        result = integration.store_pattern(
            content=content,
            pattern_type="mixed",
            user_id="test_user",
            explicit_classification=Classification.INTERNAL,
        )

        assert result is not None
        # Should have scrubbed some PII
        assert result["sanitization_report"]["pii_count"] > 0

    def test_retention_days_by_classification(self):
        """Test retention policies differ by classification"""
        public_rules = DEFAULT_CLASSIFICATION_RULES[Classification.PUBLIC]
        internal_rules = DEFAULT_CLASSIFICATION_RULES[Classification.INTERNAL]
        sensitive_rules = DEFAULT_CLASSIFICATION_RULES[Classification.SENSITIVE]

        # PUBLIC has longest retention (365 days)
        assert public_rules.retention_days == 365
        # INTERNAL has medium retention (180 days)
        assert internal_rules.retention_days == 180
        # SENSITIVE has shortest retention (90 days - regulatory minimum)
        assert sensitive_rules.retention_days == 90

    def test_pattern_statistics(self, integration):
        """Test getting pattern statistics"""
        # Store some patterns
        integration.store_pattern(
            content="Public pattern 1",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        integration.store_pattern(
            content="Internal pattern with confidential info",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.INTERNAL,
        )

        stats = integration.get_statistics()
        assert stats["total_patterns"] == 2
        assert stats["by_classification"]["PUBLIC"] == 1
        assert stats["by_classification"]["INTERNAL"] == 1

    def test_list_patterns_by_user(self, integration):
        """Test listing patterns accessible to user"""
        # Store patterns
        integration.store_pattern(
            content="Pattern 1",
            pattern_type="test",
            user_id="user1",
            explicit_classification=Classification.PUBLIC,
        )
        integration.store_pattern(
            content="Pattern 2",
            pattern_type="test",
            user_id="user2",
            explicit_classification=Classification.PUBLIC,
        )

        # Both users should see PUBLIC patterns
        patterns = integration.list_patterns(user_id="user1")
        assert len(patterns) == 2
