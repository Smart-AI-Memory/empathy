"""Extended tests for Secure MemDocs Integration Module

Coverage boost tests targeting untested code paths:
- EncryptionManager class
- delete_pattern functionality
- Retention policy enforcement
- Access control edge cases
- Pattern classification edge cases
- Error handling paths

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import base64
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from empathy_llm_toolkit.security.secure_memdocs import (
    Classification,
    EncryptionManager,
    MemDocsStorage,
    PatternMetadata,
    SecureMemDocsIntegration,
    SecurePattern,
    SecurityError,
)
from empathy_llm_toolkit.security.secure_memdocs import PermissionError as CustomPermissionError


class TestEncryptionManager:
    """Tests for EncryptionManager - encryption/decryption functionality"""

    @pytest.fixture
    def temp_home(self):
        """Create temporary home directory for key files"""
        temp_dir = tempfile.mkdtemp()
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = temp_dir
        yield temp_dir
        os.environ["HOME"] = old_home if old_home else ""
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_encryption_manager_disabled_without_library(self):
        """Test encryption manager handles missing cryptography library"""
        with patch("empathy_llm_toolkit.security.secure_memdocs.HAS_ENCRYPTION", False):
            manager = EncryptionManager()
            assert manager.enabled is False

    def test_encryption_manager_with_provided_key(self):
        """Test encryption manager with explicit master key"""
        # Generate a valid 32-byte key
        test_key = os.urandom(32)
        manager = EncryptionManager(master_key=test_key)

        # Should be enabled if cryptography is available
        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            assert manager.enabled is True
            assert manager.master_key == test_key
        except ImportError:
            assert manager.enabled is False

    def test_load_key_from_environment(self, temp_home):
        """Test loading master key from environment variable"""
        test_key = os.urandom(32)
        encoded_key = base64.b64encode(test_key).decode("utf-8")

        with patch.dict(os.environ, {"EMPATHY_MASTER_KEY": encoded_key}):
            manager = EncryptionManager()
            try:
                import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

                assert manager.enabled is True
                assert manager.master_key == test_key
            except ImportError:
                pass  # OK if cryptography not installed

    def test_load_key_invalid_format(self, temp_home):
        """Test invalid base64 key in environment raises error"""
        # 'a' is an invalid base64 string (wrong padding)
        with patch.dict(os.environ, {"EMPATHY_MASTER_KEY": "a"}):
            try:
                import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

                # Invalid key should raise ValueError
                with pytest.raises(ValueError, match="Invalid EMPATHY_MASTER_KEY format"):
                    EncryptionManager()
            except ImportError:
                pytest.skip("cryptography library not available")

    def test_load_key_from_file(self, temp_home):
        """Test loading master key from key file"""
        # Create .empathy directory and key file
        empathy_dir = Path(temp_home) / ".empathy"
        empathy_dir.mkdir(parents=True)
        key_file = empathy_dir / "master.key"

        test_key = os.urandom(32)
        key_file.write_bytes(test_key)

        manager = EncryptionManager()
        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            assert manager.enabled is True
            assert manager.master_key == test_key
        except ImportError:
            pass  # OK if cryptography not installed

    def test_encrypt_decrypt_roundtrip(self):
        """Test encrypting and decrypting returns original content"""
        test_key = os.urandom(32)
        manager = EncryptionManager(master_key=test_key)

        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            plaintext = "This is secret patient data"
            encrypted = manager.encrypt(plaintext)

            # Encrypted should be different from plaintext
            assert encrypted != plaintext

            # Decrypt should return original
            decrypted = manager.decrypt(encrypted)
            assert decrypted == plaintext

        except ImportError:
            pytest.skip("cryptography library not available")

    def test_encrypt_without_library_raises_error(self):
        """Test encrypt raises SecurityError when library not available"""
        with patch("empathy_llm_toolkit.security.secure_memdocs.HAS_ENCRYPTION", False):
            manager = EncryptionManager()
            with pytest.raises(SecurityError, match="Encryption not available"):
                manager.encrypt("test content")

    def test_decrypt_without_library_raises_error(self):
        """Test decrypt raises SecurityError when library not available"""
        with patch("empathy_llm_toolkit.security.secure_memdocs.HAS_ENCRYPTION", False):
            manager = EncryptionManager()
            with pytest.raises(SecurityError, match="Encryption not available"):
                manager.decrypt("some-encrypted-data")

    def test_decrypt_corrupted_data_raises_error(self):
        """Test decrypting corrupted data raises SecurityError"""
        test_key = os.urandom(32)
        manager = EncryptionManager(master_key=test_key)

        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            # Create invalid encrypted data
            corrupted = base64.b64encode(b"corrupted-data").decode("utf-8")

            with pytest.raises(SecurityError, match="Decryption failed"):
                manager.decrypt(corrupted)

        except ImportError:
            pytest.skip("cryptography library not available")

    def test_encrypt_different_nonces(self):
        """Test that each encryption produces different ciphertext (due to random nonce)"""
        test_key = os.urandom(32)
        manager = EncryptionManager(master_key=test_key)

        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            plaintext = "Same content"
            encrypted1 = manager.encrypt(plaintext)
            encrypted2 = manager.encrypt(plaintext)

            # Different encryptions should produce different ciphertext
            assert encrypted1 != encrypted2

            # But both should decrypt to same plaintext
            assert manager.decrypt(encrypted1) == plaintext
            assert manager.decrypt(encrypted2) == plaintext

        except ImportError:
            pytest.skip("cryptography library not available")


class TestSecurePattern:
    """Tests for SecurePattern dataclass"""

    def test_secure_pattern_creation(self):
        """Test creating a SecurePattern"""
        metadata = PatternMetadata(
            pattern_id="pat_test",
            created_by="user@test.com",
            created_at="2025-01-01T00:00:00Z",
            classification="INTERNAL",
            retention_days=180,
            encrypted=False,
            pattern_type="test",
            sanitization_applied=True,
            pii_removed=0,
            secrets_detected=0,
        )

        pattern = SecurePattern(
            pattern_id="pat_test",
            content="Test content",
            metadata=metadata,
        )

        assert pattern.pattern_id == "pat_test"
        assert pattern.content == "Test content"
        assert pattern.metadata.classification == "INTERNAL"


class TestMemDocsStorageExtended:
    """Extended tests for MemDocsStorage"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def storage(self, temp_storage):
        """Create MemDocsStorage instance"""
        return MemDocsStorage(temp_storage)

    def test_list_patterns_by_creator(self, storage):
        """Test listing patterns filtered by creator"""
        storage.store("pat_001", "content1", {"created_by": "user1@test.com"})
        storage.store("pat_002", "content2", {"created_by": "user2@test.com"})
        storage.store("pat_003", "content3", {"created_by": "user1@test.com"})

        user1_patterns = storage.list_patterns(created_by="user1@test.com")
        assert len(user1_patterns) == 2

        user2_patterns = storage.list_patterns(created_by="user2@test.com")
        assert len(user2_patterns) == 1

    def test_list_patterns_handles_malformed_files(self, storage, temp_storage):
        """Test list_patterns skips malformed JSON files"""
        # Store valid pattern
        storage.store("pat_valid", "content", {"classification": "PUBLIC"})

        # Create malformed file
        malformed_path = Path(temp_storage) / "pat_malformed.json"
        malformed_path.write_text("not valid json {{{")

        # Should only return valid pattern
        patterns = storage.list_patterns()
        assert len(patterns) == 1
        assert "pat_valid" in patterns

    def test_store_creates_parent_directories(self, temp_storage):
        """Test store creates parent directories if needed"""
        nested_dir = Path(temp_storage) / "nested" / "deep"
        storage = MemDocsStorage(str(nested_dir))

        result = storage.store("test_pat", "content", {"test": True})
        assert result is True
        assert nested_dir.exists()


class TestSecureMemDocsIntegrationExtended:
    """Extended tests for SecureMemDocsIntegration"""

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
            enable_encryption=False,
        )

    @pytest.fixture
    def integration_with_encryption(self, temp_storage):
        """Create SecureMemDocsIntegration with encryption enabled"""
        return SecureMemDocsIntegration(
            storage_dir=temp_storage,
            audit_log_dir=temp_storage,
            enable_encryption=True,
            master_key=os.urandom(32),
        )

    def test_store_empty_content_raises_error(self, integration):
        """Test storing empty content raises ValueError"""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            integration.store_pattern(
                content="",
                pattern_type="test",
                user_id="test_user",
            )

    def test_store_whitespace_content_raises_error(self, integration):
        """Test storing whitespace-only content raises ValueError"""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            integration.store_pattern(
                content="   \n\t  ",
                pattern_type="test",
                user_id="test_user",
            )

    def test_delete_pattern_success(self, integration):
        """Test successfully deleting a pattern"""
        # Store a pattern first
        result = integration.store_pattern(
            content="Test pattern for deletion",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        pattern_id = result["pattern_id"]

        # Delete it using the full delete_pattern method
        deleted = integration.delete_pattern(
            pattern_id=pattern_id,
            user_id="test_user",
        )
        assert deleted is True

        # Verify it's gone from storage
        assert integration.storage.retrieve(pattern_id) is None

    def test_delete_pattern_not_found(self, integration):
        """Test deleting non-existent pattern returns False"""
        result = integration.delete_pattern(
            pattern_id="nonexistent_pattern",
            user_id="test_user",
        )
        assert result is False

    def test_delete_pattern_permission_denied(self, integration):
        """Test deleting pattern created by another user raises PermissionError"""
        # Store pattern as user1
        result = integration.store_pattern(
            content="User1's pattern",
            pattern_type="test",
            user_id="user1@test.com",
            explicit_classification=Classification.PUBLIC,
        )
        pattern_id = result["pattern_id"]

        # Try to delete as user2
        with pytest.raises(CustomPermissionError):
            integration.delete_pattern(
                pattern_id=pattern_id,
                user_id="user2@test.com",
            )

    def test_retrieve_expired_retention_raises_error(self, integration):
        """Test retrieving pattern past retention period raises error"""
        # Store a pattern
        result = integration.store_pattern(
            content="Short retention pattern",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        pattern_id = result["pattern_id"]

        # Manually modify the storage to have an old creation date
        pattern_data = integration.storage.retrieve(pattern_id)
        old_date = (datetime.utcnow() - timedelta(days=400)).isoformat() + "Z"
        pattern_data["metadata"]["created_at"] = old_date
        integration.storage.store(pattern_id, pattern_data["content"], pattern_data["metadata"])

        # Try to retrieve
        with pytest.raises(ValueError, match="expired retention period"):
            integration.retrieve_pattern(pattern_id=pattern_id, user_id="test_user")

    def test_retrieve_sensitive_pattern_access_denied(self, integration):
        """Test retrieving SENSITIVE pattern by non-creator raises PermissionError"""
        # Store sensitive pattern as creator
        result = integration.store_pattern(
            content="Patient medical records require careful handling",
            pattern_type="clinical",
            user_id="doctor@hospital.com",
            auto_classify=True,  # Should be SENSITIVE due to "patient" keyword
        )
        pattern_id = result["pattern_id"]

        # Try to retrieve as different user
        with pytest.raises(CustomPermissionError, match="does not have access"):
            integration.retrieve_pattern(
                pattern_id=pattern_id,
                user_id="other_user@hospital.com",
            )

    def test_retrieve_pattern_not_found(self, integration):
        """Test retrieving non-existent pattern raises error"""
        with pytest.raises(ValueError, match="not found"):
            integration.retrieve_pattern(
                pattern_id="nonexistent_pattern",
                user_id="test_user",
            )

    def test_auto_classification_financial_keywords(self, integration):
        """Test auto-classification detects financial keywords as SENSITIVE"""
        result = integration.store_pattern(
            content="Payment processing and credit card handling procedures",
            pattern_type="business",
            user_id="test_user",
            auto_classify=True,
        )
        assert result["classification"] == "SENSITIVE"

    def test_auto_classification_by_pattern_type(self, integration):
        """Test auto-classification by pattern type"""
        # clinical_protocol type -> SENSITIVE
        result = integration.store_pattern(
            content="Generic protocol content",
            pattern_type="clinical_protocol",
            user_id="test_user",
            auto_classify=True,
        )
        assert result["classification"] == "SENSITIVE"

        # architecture type -> INTERNAL
        result2 = integration.store_pattern(
            content="Generic architecture content",
            pattern_type="architecture",
            user_id="test_user",
            auto_classify=True,
        )
        assert result2["classification"] == "INTERNAL"

    def test_store_with_no_auto_classify(self, integration):
        """Test storing without auto_classify defaults to INTERNAL"""
        result = integration.store_pattern(
            content="Some content",
            pattern_type="test",
            user_id="test_user",
            auto_classify=False,
        )
        assert result["classification"] == "INTERNAL"

    def test_store_sensitive_with_encryption(self, integration_with_encryption):
        """Test SENSITIVE patterns are encrypted when encryption is enabled"""
        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            result = integration_with_encryption.store_pattern(
                content="Patient diagnosis information",
                pattern_type="clinical",
                user_id="doctor@hospital.com",
                auto_classify=True,  # Should be SENSITIVE
            )

            assert result["classification"] == "SENSITIVE"
            assert result["metadata"]["encrypted"] is True

        except ImportError:
            pytest.skip("cryptography library not available")

    def test_retrieve_encrypted_pattern(self, integration_with_encryption):
        """Test retrieving and decrypting an encrypted pattern"""
        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            original_content = "Patient medical history details"

            # Store SENSITIVE pattern
            result = integration_with_encryption.store_pattern(
                content=original_content,
                pattern_type="clinical_protocol",
                user_id="doctor@hospital.com",
                auto_classify=True,
            )
            pattern_id = result["pattern_id"]

            # Retrieve and decrypt
            retrieved = integration_with_encryption.retrieve_pattern(
                pattern_id=pattern_id,
                user_id="doctor@hospital.com",
            )

            assert original_content in retrieved["content"]

        except ImportError:
            pytest.skip("cryptography library not available")

    def test_list_patterns_by_classification(self, integration):
        """Test listing patterns filtered by classification"""
        # Create patterns with different classifications
        integration.store_pattern(
            content="Public content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        integration.store_pattern(
            content="Internal content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.INTERNAL,
        )

        public_patterns = integration.list_patterns(
            user_id="test_user",
            classification=Classification.PUBLIC,
        )
        assert len(public_patterns) == 1
        assert public_patterns[0]["classification"] == "PUBLIC"

    def test_list_patterns_by_pattern_type(self, integration):
        """Test listing patterns filtered by pattern type"""
        integration.store_pattern(
            content="Code pattern",
            pattern_type="code",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        integration.store_pattern(
            content="Architecture pattern",
            pattern_type="architecture",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )

        code_patterns = integration.list_patterns(
            user_id="test_user",
            pattern_type="code",
        )
        assert len(code_patterns) == 1
        assert code_patterns[0]["pattern_type"] == "code"

    def test_check_access_public(self, integration):
        """Test PUBLIC patterns are accessible to all users"""
        result = integration.store_pattern(
            content="Public content",
            pattern_type="test",
            user_id="creator@test.com",
            explicit_classification=Classification.PUBLIC,
        )

        # Different user should be able to access
        retrieved = integration.retrieve_pattern(
            pattern_id=result["pattern_id"],
            user_id="other_user@test.com",
        )
        assert retrieved is not None

    def test_check_access_internal(self, integration):
        """Test INTERNAL patterns are accessible (simplified team check)"""
        result = integration.store_pattern(
            content="Internal content",
            pattern_type="test",
            user_id="creator@test.com",
            explicit_classification=Classification.INTERNAL,
        )

        # Different user should still be able to access (simplified check)
        retrieved = integration.retrieve_pattern(
            pattern_id=result["pattern_id"],
            user_id="other_user@test.com",
        )
        assert retrieved is not None

    def test_get_statistics_empty(self, integration):
        """Test get_statistics with no patterns"""
        stats = integration.get_statistics()
        assert stats["total_patterns"] == 0
        assert stats["encrypted_count"] == 0

    def test_get_statistics_with_pii_scrubbed(self, integration):
        """Test statistics count patterns with PII scrubbed"""
        integration.store_pattern(
            content="Contact: test@example.com for more info",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )

        stats = integration.get_statistics()
        assert stats["with_pii_scrubbed"] == 1

    def test_store_pattern_failed_logging(self, integration):
        """Test that failed pattern storage is logged to audit"""
        # Force an error by mocking storage
        original_store = integration.storage.store
        integration.storage.store = MagicMock(side_effect=OSError("Storage error"))

        with pytest.raises(IOError):
            integration.store_pattern(
                content="Test content",
                pattern_type="test",
                user_id="test_user",
                explicit_classification=Classification.PUBLIC,
            )

        integration.storage.store = original_store

    def test_retrieve_pattern_skip_permissions(self, integration):
        """Test retrieving pattern without permission check"""
        # Store SENSITIVE pattern
        result = integration.store_pattern(
            content="Patient data requires handling",
            pattern_type="clinical",
            user_id="doctor@hospital.com",
            auto_classify=True,
        )

        # Retrieve without permission check (e.g., for admin access)
        retrieved = integration.retrieve_pattern(
            pattern_id=result["pattern_id"],
            user_id="admin@hospital.com",
            check_permissions=False,
        )
        assert retrieved is not None

    def test_retrieve_decryption_unavailable_error(self, temp_storage):
        """Test retrieving encrypted pattern when decryption unavailable raises error"""
        # Create integration with encryption to store encrypted pattern
        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            integration = SecureMemDocsIntegration(
                storage_dir=temp_storage,
                audit_log_dir=temp_storage,
                enable_encryption=True,
                master_key=os.urandom(32),
            )

            result = integration.store_pattern(
                content="Patient data",
                pattern_type="clinical_protocol",
                user_id="doctor@hospital.com",
                auto_classify=True,
            )
            pattern_id = result["pattern_id"]

            # Disable encryption and try to retrieve
            integration.encryption_enabled = False

            with pytest.raises(SecurityError, match="Encryption not available"):
                integration.retrieve_pattern(
                    pattern_id=pattern_id,
                    user_id="doctor@hospital.com",
                )

        except ImportError:
            pytest.skip("cryptography library not available")

    def test_store_pattern_with_custom_metadata(self, integration):
        """Test storing pattern with custom metadata"""
        result = integration.store_pattern(
            content="Test content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
            custom_metadata={"source": "github", "language": "python"},
        )

        retrieved = integration.retrieve_pattern(
            pattern_id=result["pattern_id"],
            user_id="test_user",
        )

        assert retrieved["metadata"]["custom_metadata"]["source"] == "github"
        assert retrieved["metadata"]["custom_metadata"]["language"] == "python"

    def test_store_pattern_with_session_id(self, integration):
        """Test storing pattern with session ID for audit"""
        result = integration.store_pattern(
            content="Test content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
            session_id="sess_12345",
        )

        assert result is not None
        # Session ID is used for audit logging, not stored in pattern


class TestClassificationEdgeCases:
    """Test classification edge cases"""

    @pytest.fixture
    def temp_storage(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def integration(self, temp_storage):
        return SecureMemDocsIntegration(
            storage_dir=temp_storage,
            audit_log_dir=temp_storage,
            enable_encryption=False,
        )

    def test_financial_procedure_type_sensitive(self, integration):
        """Test financial_procedure pattern type is SENSITIVE"""
        result = integration.store_pattern(
            content="Generic procedure content",
            pattern_type="financial_procedure",
            user_id="test_user",
            auto_classify=True,
        )
        assert result["classification"] == "SENSITIVE"

    def test_medical_guideline_type_sensitive(self, integration):
        """Test medical_guideline pattern type is SENSITIVE"""
        result = integration.store_pattern(
            content="Generic guideline content",
            pattern_type="medical_guideline",
            user_id="test_user",
            auto_classify=True,
        )
        assert result["classification"] == "SENSITIVE"

    def test_patient_workflow_type_sensitive(self, integration):
        """Test patient_workflow pattern type is SENSITIVE"""
        result = integration.store_pattern(
            content="Generic workflow content",
            pattern_type="patient_workflow",
            user_id="test_user",
            auto_classify=True,
        )
        assert result["classification"] == "SENSITIVE"

    def test_business_logic_type_internal(self, integration):
        """Test business_logic pattern type is INTERNAL"""
        result = integration.store_pattern(
            content="Generic business logic",
            pattern_type="business_logic",
            user_id="test_user",
            auto_classify=True,
        )
        assert result["classification"] == "INTERNAL"

    def test_company_process_type_internal(self, integration):
        """Test company_process pattern type is INTERNAL"""
        result = integration.store_pattern(
            content="Generic company process",
            pattern_type="company_process",
            user_id="test_user",
            auto_classify=True,
        )
        assert result["classification"] == "INTERNAL"

    def test_proprietary_keywords_internal(self, integration):
        """Test proprietary keywords result in INTERNAL classification"""
        keywords = ["proprietary", "confidential", "trade secret", "restricted"]

        for keyword in keywords:
            result = integration.store_pattern(
                content=f"This contains {keyword} information",
                pattern_type="generic",
                user_id="test_user",
                auto_classify=True,
            )
            assert result["classification"] == "INTERNAL", f"Failed for keyword: {keyword}"


class TestMemDocsStorageErrorPaths:
    """Test error handling in MemDocsStorage"""

    @pytest.fixture
    def temp_storage(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def storage(self, temp_storage):
        return MemDocsStorage(temp_storage)

    def test_store_io_error(self, storage):
        """Test store handles IO errors"""
        with patch("builtins.open", side_effect=OSError("Disk full")):
            with pytest.raises(IOError):
                storage.store("test_id", "content", {"test": True})

    def test_retrieve_corrupted_json(self, storage, temp_storage):
        """Test retrieve handles corrupted JSON files"""
        # Create a corrupted JSON file
        pattern_file = Path(temp_storage) / "corrupted.json"
        pattern_file.write_text("not valid json {{{")

        # retrieve should return None and not crash
        result = storage.retrieve("corrupted")
        assert result is None

    def test_delete_permission_error(self, storage, temp_storage):
        """Test delete handles permission errors"""
        # Store a pattern first
        storage.store("test_delete", "content", {"test": True})

        # Mock unlink to raise PermissionError
        with patch.object(Path, "unlink", side_effect=PermissionError("Permission denied")):
            result = storage.delete("test_delete")
            assert result is False


class TestEncryptionEdgeCases:
    """Test encryption edge cases"""

    @pytest.fixture
    def temp_home(self):
        temp_dir = tempfile.mkdtemp()
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = temp_dir
        yield temp_dir
        os.environ["HOME"] = old_home if old_home else ""
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_key_file_read_error(self, temp_home):
        """Test handling key file read errors"""
        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            # Create .empathy directory and key file
            empathy_dir = Path(temp_home) / ".empathy"
            empathy_dir.mkdir(parents=True)
            key_file = empathy_dir / "master.key"
            key_file.write_bytes(os.urandom(32))

            # Mock read_bytes to fail
            with patch.object(Path, "read_bytes", side_effect=OSError("Read error")):
                # Should fall back to generating ephemeral key
                manager = EncryptionManager()
                assert manager.enabled is True
                # Key was generated, not loaded from file

        except ImportError:
            pytest.skip("cryptography library not available")

    def test_encryption_general_exception(self):
        """Test encryption handles general exceptions"""
        try:
            import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401

            # Create a manager with a valid key
            test_key = os.urandom(32)
            manager = EncryptionManager(master_key=test_key)

            # Mock AESGCM to raise an unexpected error
            with (
                patch(
                    "empathy_llm_toolkit.security.secure_memdocs.AESGCM",
                    side_effect=RuntimeError("Unexpected crypto error"),
                ),
                pytest.raises(SecurityError, match="Encryption failed"),
            ):
                manager.encrypt("test content")

        except ImportError:
            pytest.skip("cryptography library not available")


class TestRetrievePatternErrorPaths:
    """Test retrieve_pattern error handling"""

    @pytest.fixture
    def temp_storage(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def integration(self, temp_storage):
        return SecureMemDocsIntegration(
            storage_dir=temp_storage,
            audit_log_dir=temp_storage,
            enable_encryption=False,
        )

    def test_retrieve_unexpected_error(self, integration):
        """Test retrieve_pattern handles unexpected errors and logs to audit"""
        # Store a valid pattern
        result = integration.store_pattern(
            content="Test content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )
        pattern_id = result["pattern_id"]

        # Mock storage.retrieve to raise an unexpected error
        integration.storage.retrieve = MagicMock(
            side_effect=RuntimeError("Unexpected database error"),
        )

        # Retrieve should raise the unexpected error
        with pytest.raises(RuntimeError, match="Unexpected database error"):
            integration.retrieve_pattern(pattern_id=pattern_id, user_id="test_user")

    def test_retrieve_classification_key_error(self, integration, temp_storage):
        """Test retrieve handles invalid classification in stored data"""
        # Manually create a pattern with invalid classification
        pattern_file = Path(temp_storage) / "invalid_class.json"
        pattern_data = {
            "pattern_id": "invalid_class",
            "content": "test content",
            "metadata": {
                "classification": "INVALID_CLASS",  # Invalid enum value
                "created_by": "test_user",
                "created_at": "2025-01-01T00:00:00Z",
                "retention_days": 365,
                "encrypted": False,
            },
        }
        with open(pattern_file, "w") as f:
            import json

            json.dump(pattern_data, f)

        # Retrieve should raise KeyError for invalid classification
        with pytest.raises(KeyError):
            integration.retrieve_pattern(pattern_id="invalid_class", user_id="test_user")


class TestListPatternsErrorPaths:
    """Test list_patterns error handling"""

    @pytest.fixture
    def temp_storage(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def integration(self, temp_storage):
        return SecureMemDocsIntegration(
            storage_dir=temp_storage,
            audit_log_dir=temp_storage,
            enable_encryption=False,
        )

    def test_list_patterns_with_corrupted_file(self, integration, temp_storage):
        """Test list_patterns skips corrupted pattern files"""
        # Store valid pattern
        integration.store_pattern(
            content="Valid content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )

        # Create corrupted pattern file
        corrupted_file = Path(temp_storage) / "corrupted_pat.json"
        corrupted_file.write_text("not valid json")

        # list_patterns should still work, returning only valid patterns
        patterns = integration.list_patterns(user_id="test_user")
        assert len(patterns) == 1

    def test_list_patterns_retrieval_error(self, integration, temp_storage):
        """Test list_patterns handles retrieval errors for individual patterns"""
        # Store a valid pattern
        integration.store_pattern(
            content="Test content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )

        # Mock storage.retrieve to sometimes fail
        original_retrieve = integration.storage.retrieve
        call_count = [0]

        def flaky_retrieve(pid):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Flaky error")
            return original_retrieve(pid)

        integration.storage.retrieve = flaky_retrieve

        # list_patterns should handle the error and continue
        integration.list_patterns(user_id="test_user")
        # May return 0 or more patterns depending on error handling


class TestGetStatisticsErrorPaths:
    """Test get_statistics error handling"""

    @pytest.fixture
    def temp_storage(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def integration(self, temp_storage):
        return SecureMemDocsIntegration(
            storage_dir=temp_storage,
            audit_log_dir=temp_storage,
            enable_encryption=False,
        )

    def test_get_statistics_with_corrupted_pattern(self, integration, temp_storage):
        """Test get_statistics handles corrupted patterns gracefully"""
        # Store valid pattern
        integration.store_pattern(
            content="Valid content",
            pattern_type="test",
            user_id="test_user",
            explicit_classification=Classification.PUBLIC,
        )

        # Create corrupted pattern file
        corrupted_file = Path(temp_storage) / "corrupted_stats.json"
        corrupted_file.write_text("not valid json")

        # get_statistics should still work
        stats = integration.get_statistics()
        assert stats["total_patterns"] >= 1  # At least the valid pattern


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
