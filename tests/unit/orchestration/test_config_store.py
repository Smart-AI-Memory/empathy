"""Comprehensive tests for Agent Configuration Store

Tests cover:
- AgentConfiguration dataclass functionality
- ConfigurationStore CRUD operations
- Search and filtering
- Performance metric tracking
- Pattern library integration
- File I/O error handling
- Security (path validation)

Target: 90%+ test coverage
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from empathy_os.orchestration.config_store import AgentConfiguration, ConfigurationStore
from empathy_os.pattern_library import PatternLibrary


class TestAgentConfiguration:
    """Test AgentConfiguration dataclass"""

    def test_create_minimal_config(self):
        """Test creating configuration with minimal required fields."""
        config = AgentConfiguration(
            id="test_001",
            task_pattern="test_task",
            agents=[{"role": "tester", "tier": "CHEAP"}],
            strategy="sequential",
            quality_gates={"min_score": 80},
        )

        assert config.id == "test_001"
        assert config.task_pattern == "test_task"
        assert len(config.agents) == 1
        assert config.strategy == "sequential"
        assert config.success_rate == 0.0
        assert config.usage_count == 0

    def test_create_full_config(self):
        """Test creating configuration with all fields."""
        created = datetime(2025, 1, 1, 12, 0, 0)
        last_used = datetime(2025, 1, 10, 14, 30, 0)

        config = AgentConfiguration(
            id="test_002",
            task_pattern="release_prep",
            agents=[
                {"role": "security_auditor", "tier": "PREMIUM"},
                {"role": "test_analyzer", "tier": "CAPABLE"},
            ],
            strategy="parallel",
            quality_gates={"min_coverage": 80, "max_critical_issues": 0},
            success_rate=0.95,
            avg_quality_score=87.5,
            usage_count=20,
            success_count=19,
            failure_count=1,
            created_at=created,
            last_used=last_used,
            tags=["release", "production"],
        )

        assert config.id == "test_002"
        assert config.task_pattern == "release_prep"
        assert len(config.agents) == 2
        assert config.strategy == "parallel"
        assert config.success_rate == 0.95
        assert config.avg_quality_score == 87.5
        assert config.usage_count == 20
        assert config.created_at == created
        assert config.last_used == last_used
        assert "release" in config.tags

    def test_record_outcome_success(self):
        """Test recording successful outcome."""
        config = AgentConfiguration(
            id="test_003",
            task_pattern="test_task",
            agents=[],
            strategy="sequential",
            quality_gates={},
        )

        # Record first success
        config.record_outcome(success=True, quality_score=85.0)

        assert config.usage_count == 1
        assert config.success_count == 1
        assert config.failure_count == 0
        assert config.success_rate == 1.0
        assert config.avg_quality_score == 85.0
        assert config.last_used is not None

        # Record second success
        config.record_outcome(success=True, quality_score=90.0)

        assert config.usage_count == 2
        assert config.success_count == 2
        assert config.success_rate == 1.0
        # Weighted average: 0.7 * 90 + 0.3 * 85 = 88.5
        assert 88.0 <= config.avg_quality_score <= 89.0

    def test_record_outcome_failure(self):
        """Test recording failed outcome."""
        config = AgentConfiguration(
            id="test_004",
            task_pattern="test_task",
            agents=[],
            strategy="sequential",
            quality_gates={},
        )

        # Record first failure
        config.record_outcome(success=False, quality_score=45.0)

        assert config.usage_count == 1
        assert config.success_count == 0
        assert config.failure_count == 1
        assert config.success_rate == 0.0
        assert config.avg_quality_score == 45.0

        # Record success after failure
        config.record_outcome(success=True, quality_score=85.0)

        assert config.usage_count == 2
        assert config.success_count == 1
        assert config.failure_count == 1
        assert config.success_rate == 0.5

    def test_record_outcome_invalid_quality_score(self):
        """Test that invalid quality scores raise ValueError."""
        config = AgentConfiguration(
            id="test_005",
            task_pattern="test_task",
            agents=[],
            strategy="sequential",
            quality_gates={},
        )

        # Too low
        with pytest.raises(ValueError, match="quality_score must be 0-100"):
            config.record_outcome(success=True, quality_score=-1.0)

        # Too high
        with pytest.raises(ValueError, match="quality_score must be 0-100"):
            config.record_outcome(success=True, quality_score=101.0)

    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        created = datetime(2025, 1, 1, 12, 0, 0)
        config = AgentConfiguration(
            id="test_006",
            task_pattern="test_task",
            agents=[{"role": "tester"}],
            strategy="sequential",
            quality_gates={"min": 80},
            created_at=created,
        )

        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["id"] == "test_006"
        assert data["task_pattern"] == "test_task"
        assert data["created_at"] == created.isoformat()
        assert data["last_used"] is None

    def test_from_dict_deserialization(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "test_007",
            "task_pattern": "test_task",
            "agents": [{"role": "tester"}],
            "strategy": "sequential",
            "quality_gates": {"min": 80},
            "success_rate": 0.8,
            "avg_quality_score": 75.0,
            "usage_count": 10,
            "success_count": 8,
            "failure_count": 2,
            "created_at": "2025-01-01T12:00:00",
            "last_used": "2025-01-10T14:30:00",
            "tags": ["test"],
        }

        config = AgentConfiguration.from_dict(data)

        assert config.id == "test_007"
        assert config.task_pattern == "test_task"
        assert config.success_rate == 0.8
        assert isinstance(config.created_at, datetime)
        assert isinstance(config.last_used, datetime)

    def test_round_trip_serialization(self):
        """Test that serialization -> deserialization preserves data."""
        original = AgentConfiguration(
            id="test_008",
            task_pattern="test_task",
            agents=[{"role": "tester", "tier": "CAPABLE"}],
            strategy="parallel",
            quality_gates={"min_coverage": 80},
            success_rate=0.9,
            avg_quality_score=85.0,
            tags=["test", "production"],
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = AgentConfiguration.from_dict(data)

        assert restored.id == original.id
        assert restored.task_pattern == original.task_pattern
        assert restored.agents == original.agents
        assert restored.strategy == original.strategy
        assert restored.success_rate == original.success_rate
        assert restored.tags == original.tags


class TestConfigurationStore:
    """Test ConfigurationStore class"""

    @pytest.fixture
    def temp_store(self, tmp_path):
        """Create temporary configuration store."""
        storage_dir = tmp_path / "orchestration" / "compositions"
        return ConfigurationStore(storage_dir=str(storage_dir))

    @pytest.fixture
    def temp_store_with_pattern_library(self, tmp_path):
        """Create store with pattern library integration."""
        storage_dir = tmp_path / "orchestration" / "compositions"
        pattern_lib = PatternLibrary()
        return ConfigurationStore(storage_dir=str(storage_dir), pattern_library=pattern_lib)

    @pytest.fixture
    def sample_config(self):
        """Create sample configuration for testing."""
        return AgentConfiguration(
            id="sample_001",
            task_pattern="test_task",
            agents=[{"role": "tester", "tier": "CHEAP"}],
            strategy="sequential",
            quality_gates={"min_score": 80},
        )

    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates storage directory."""
        storage_dir = tmp_path / "new_dir" / "compositions"
        store = ConfigurationStore(storage_dir=str(storage_dir))

        assert storage_dir.exists()
        assert storage_dir.is_dir()
        assert store.storage_dir == storage_dir

    def test_init_with_existing_directory(self, tmp_path):
        """Test initialization with pre-existing directory."""
        storage_dir = tmp_path / "existing"
        storage_dir.mkdir(parents=True)

        store = ConfigurationStore(storage_dir=str(storage_dir))

        assert store.storage_dir == storage_dir

    def test_init_default_directory(self, monkeypatch, tmp_path):
        """Test that default directory is used when none provided."""
        # Change to temp directory for test
        monkeypatch.chdir(tmp_path)

        store = ConfigurationStore()

        expected = Path(".empathy/orchestration/compositions")
        assert store.storage_dir == expected
        assert expected.exists()

    def test_save_configuration(self, temp_store, sample_config):
        """Test saving configuration to disk."""
        file_path = temp_store.save(sample_config)

        assert file_path.exists()
        assert file_path.name == "sample_001.json"

        # Verify file contents
        with file_path.open("r") as f:
            data = json.load(f)
            assert data["id"] == "sample_001"
            assert data["task_pattern"] == "test_task"

    def test_save_updates_cache(self, temp_store, sample_config):
        """Test that save updates in-memory cache."""
        temp_store.save(sample_config)

        # Should be in cache
        assert "sample_001" in temp_store._cache
        assert temp_store._cache["sample_001"].id == "sample_001"

    def test_save_invalid_id(self, temp_store):
        """Test that save with invalid ID raises ValueError."""
        config = AgentConfiguration(
            id="",  # Empty ID
            task_pattern="test",
            agents=[],
            strategy="sequential",
            quality_gates={},
        )

        with pytest.raises(ValueError, match="config.id must be a non-empty string"):
            temp_store.save(config)

    def test_save_path_traversal_protection(self, temp_store):
        """Test that path traversal attempts are blocked."""
        # Try to save outside storage directory
        config = AgentConfiguration(
            id="../../../etc/passwd",
            task_pattern="malicious",
            agents=[],
            strategy="sequential",
            quality_gates={},
        )

        with pytest.raises(ValueError):
            temp_store.save(config)

    def test_load_existing_configuration(self, temp_store, sample_config):
        """Test loading configuration from disk."""
        # Save first
        temp_store.save(sample_config)

        # Load
        loaded = temp_store.load("sample_001")

        assert loaded is not None
        assert loaded.id == "sample_001"
        assert loaded.task_pattern == "test_task"
        assert loaded.strategy == "sequential"

    def test_load_nonexistent_configuration(self, temp_store):
        """Test loading non-existent configuration returns None."""
        loaded = temp_store.load("nonexistent")

        assert loaded is None

    def test_load_invalid_id(self, temp_store):
        """Test that load with invalid ID raises ValueError."""
        with pytest.raises(ValueError, match="config_id must be a non-empty string"):
            temp_store.load("")

    def test_load_lazy_initialization(self, temp_store, sample_config):
        """Test that configurations are loaded lazily from disk."""
        # Save config
        temp_store.save(sample_config)

        # Create new store instance (fresh cache)
        new_store = ConfigurationStore(storage_dir=str(temp_store.storage_dir))

        # Cache should be empty initially
        assert not new_store._loaded

        # Load should trigger lazy load
        loaded = new_store.load("sample_001")

        assert new_store._loaded
        assert loaded is not None
        assert loaded.id == "sample_001"

    def test_search_by_task_pattern(self, temp_store):
        """Test searching configurations by task pattern."""
        # Save multiple configs with different patterns
        configs = [
            AgentConfiguration(
                id="config_1",
                task_pattern="release_prep",
                agents=[],
                strategy="parallel",
                quality_gates={},
            ),
            AgentConfiguration(
                id="config_2",
                task_pattern="release_prep",
                agents=[],
                strategy="sequential",
                quality_gates={},
            ),
            AgentConfiguration(
                id="config_3",
                task_pattern="test_coverage",
                agents=[],
                strategy="sequential",
                quality_gates={},
            ),
        ]

        for config in configs:
            temp_store.save(config)

        # Search for release_prep
        results = temp_store.search(task_pattern="release_prep")

        assert len(results) == 2
        assert all(c.task_pattern == "release_prep" for c in results)

    def test_search_by_success_rate(self, temp_store):
        """Test searching by minimum success rate."""
        configs = [
            AgentConfiguration(
                id="config_1",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.5,
            ),
            AgentConfiguration(
                id="config_2",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.8,
            ),
            AgentConfiguration(
                id="config_3",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.95,
            ),
        ]

        for config in configs:
            temp_store.save(config)

        # Search for success rate >= 0.8
        results = temp_store.search(min_success_rate=0.8)

        assert len(results) == 2
        assert all(c.success_rate >= 0.8 for c in results)

    def test_search_by_quality_score(self, temp_store):
        """Test searching by minimum quality score."""
        configs = [
            AgentConfiguration(
                id="config_1",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                avg_quality_score=60.0,
            ),
            AgentConfiguration(
                id="config_2",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                avg_quality_score=75.0,
            ),
            AgentConfiguration(
                id="config_3",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                avg_quality_score=90.0,
            ),
        ]

        for config in configs:
            temp_store.save(config)

        # Search for quality score >= 75
        results = temp_store.search(min_quality_score=75.0)

        assert len(results) == 2
        assert all(c.avg_quality_score >= 75.0 for c in results)

    def test_search_combined_filters(self, temp_store):
        """Test searching with multiple filters combined."""
        configs = [
            AgentConfiguration(
                id="config_1",
                task_pattern="release_prep",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.9,
                avg_quality_score=85.0,
            ),
            AgentConfiguration(
                id="config_2",
                task_pattern="release_prep",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.7,  # Below threshold
                avg_quality_score=85.0,
            ),
            AgentConfiguration(
                id="config_3",
                task_pattern="test_coverage",  # Different pattern
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.9,
                avg_quality_score=85.0,
            ),
        ]

        for config in configs:
            temp_store.save(config)

        # Search for release_prep with success rate >= 0.8
        results = temp_store.search(
            task_pattern="release_prep", min_success_rate=0.8, min_quality_score=80.0
        )

        assert len(results) == 1
        assert results[0].id == "config_1"

    def test_search_sorting(self, temp_store):
        """Test that search results are sorted by success rate and quality."""
        configs = [
            AgentConfiguration(
                id="config_1",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.8,
                avg_quality_score=70.0,
            ),
            AgentConfiguration(
                id="config_2",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.9,  # Higher success rate
                avg_quality_score=85.0,
            ),
            AgentConfiguration(
                id="config_3",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.9,  # Same success rate
                avg_quality_score=90.0,  # Higher quality
            ),
        ]

        for config in configs:
            temp_store.save(config)

        results = temp_store.search()

        # Should be sorted: config_3, config_2, config_1
        assert results[0].id == "config_3"
        assert results[1].id == "config_2"
        assert results[2].id == "config_1"

    def test_search_limit(self, temp_store):
        """Test that search respects limit parameter."""
        # Create 10 configs
        for i in range(10):
            config = AgentConfiguration(
                id=f"config_{i}",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
            )
            temp_store.save(config)

        # Search with limit
        results = temp_store.search(limit=5)

        assert len(results) == 5

    def test_search_invalid_parameters(self, temp_store):
        """Test that search validates parameters."""
        # Invalid success rate
        with pytest.raises(ValueError, match="min_success_rate must be 0-1"):
            temp_store.search(min_success_rate=1.5)

        # Invalid quality score
        with pytest.raises(ValueError, match="min_quality_score must be 0-100"):
            temp_store.search(min_quality_score=150.0)

        # Invalid limit
        with pytest.raises(ValueError, match="limit must be positive"):
            temp_store.search(limit=0)

    def test_get_best_for_task(self, temp_store):
        """Test getting best configuration for a task pattern."""
        configs = [
            AgentConfiguration(
                id="config_1",
                task_pattern="release_prep",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.7,
            ),
            AgentConfiguration(
                id="config_2",
                task_pattern="release_prep",
                agents=[],
                strategy="parallel",
                quality_gates={},
                success_rate=0.95,  # Best
            ),
            AgentConfiguration(
                id="config_3",
                task_pattern="test_coverage",
                agents=[],
                strategy="sequential",
                quality_gates={},
                success_rate=0.9,
            ),
        ]

        for config in configs:
            temp_store.save(config)

        best = temp_store.get_best_for_task("release_prep")

        assert best is not None
        assert best.id == "config_2"
        assert best.success_rate == 0.95

    def test_get_best_for_task_not_found(self, temp_store):
        """Test getting best for non-existent task pattern."""
        best = temp_store.get_best_for_task("nonexistent")

        assert best is None

    def test_delete_existing_configuration(self, temp_store, sample_config):
        """Test deleting configuration."""
        # Save and verify exists
        file_path = temp_store.save(sample_config)
        assert file_path.exists()

        # Delete
        deleted = temp_store.delete("sample_001")

        assert deleted is True
        assert not file_path.exists()
        assert "sample_001" not in temp_store._cache

    def test_delete_nonexistent_configuration(self, temp_store):
        """Test deleting non-existent configuration."""
        deleted = temp_store.delete("nonexistent")

        assert deleted is False

    def test_delete_invalid_id(self, temp_store):
        """Test that delete with invalid ID raises ValueError."""
        with pytest.raises(ValueError, match="config_id must be a non-empty string"):
            temp_store.delete("")

    def test_list_all_configurations(self, temp_store):
        """Test listing all configurations."""
        configs = [
            AgentConfiguration(
                id=f"config_{i}",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
            )
            for i in range(5)
        ]

        for config in configs:
            temp_store.save(config)

        all_configs = temp_store.list_all()

        assert len(all_configs) == 5
        assert all(isinstance(c, AgentConfiguration) for c in all_configs)

    def test_list_all_sorted_by_last_used(self, temp_store):
        """Test that list_all sorts by last_used."""
        # Create configs with different last_used times
        configs = [
            AgentConfiguration(
                id="config_1",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                last_used=datetime(2025, 1, 1),  # Oldest
            ),
            AgentConfiguration(
                id="config_2",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                last_used=datetime(2025, 1, 10),  # Most recent
            ),
            AgentConfiguration(
                id="config_3",
                task_pattern="test",
                agents=[],
                strategy="sequential",
                quality_gates={},
                last_used=None,  # Never used
            ),
        ]

        for config in configs:
            temp_store.save(config)

        all_configs = temp_store.list_all()

        # Should be sorted: config_2, config_1, config_3
        assert all_configs[0].id == "config_2"
        assert all_configs[1].id == "config_1"
        assert all_configs[2].id == "config_3"

    def test_pattern_library_integration_saves_pattern(self, temp_store_with_pattern_library):
        """Test that successful configs are saved to pattern library."""
        store = temp_store_with_pattern_library

        # Create proven configuration (high usage, high success)
        config = AgentConfiguration(
            id="proven_001",
            task_pattern="release_prep",
            agents=[{"role": "security_auditor"}],
            strategy="parallel",
            quality_gates={},
            usage_count=5,
            success_count=4,
            failure_count=1,
            success_rate=0.8,
        )

        # Save should trigger pattern library contribution
        store.save(config)

        # Check pattern library has the pattern
        patterns = store.pattern_library.patterns
        pattern_id = f"orchestration_{config.id}"

        # Pattern should exist
        assert pattern_id in patterns
        pattern = patterns[pattern_id]
        assert pattern.name == "release_prep"
        assert pattern.pattern_type == "agent_composition"
        assert pattern.confidence == 0.8

    def test_pattern_library_integration_waits_for_proof(self, temp_store_with_pattern_library):
        """Test that unproven configs are NOT saved to pattern library."""
        store = temp_store_with_pattern_library

        # Create unproven configuration (low usage)
        config = AgentConfiguration(
            id="unproven_001",
            task_pattern="test_task",
            agents=[],
            strategy="sequential",
            quality_gates={},
            usage_count=1,  # Too few uses
            success_rate=0.5,
        )

        store.save(config)

        # Pattern should NOT be contributed yet
        pattern_id = f"orchestration_{config.id}"
        assert pattern_id not in store.pattern_library.patterns

    def test_handles_corrupted_config_file(self, temp_store):
        """Test that corrupted JSON files are handled gracefully."""
        # Create corrupted file
        bad_file = temp_store.storage_dir / "corrupted.json"
        bad_file.write_text("{ this is not valid json }")

        # Should load without crashing
        temp_store.list_all()

        # Corrupted file should be skipped
        assert "corrupted" not in temp_store._cache

    def test_handles_missing_directory_on_load(self, tmp_path):
        """Test that missing directory is handled on load."""
        nonexistent_dir = tmp_path / "does_not_exist"
        store = ConfigurationStore(storage_dir=str(nonexistent_dir))

        # Should create directory
        assert nonexistent_dir.exists()

        # Load should work with empty directory
        result = store.load("anything")
        assert result is None


class TestPathValidation:
    """Test _validate_file_path security function"""

    def test_validate_file_path_normal_path(self, tmp_path):
        """Test validation of normal file path."""
        from empathy_os.orchestration.config_store import _validate_file_path

        test_file = tmp_path / "test.json"
        result = _validate_file_path(str(test_file))

        assert result.resolve() == test_file.resolve()

    def test_validate_file_path_null_bytes(self):
        """Test that null bytes in path are rejected."""
        from empathy_os.orchestration.config_store import _validate_file_path

        with pytest.raises(ValueError, match="contains null bytes"):
            _validate_file_path("test\x00file.json")

    def test_validate_file_path_empty_string(self):
        """Test that empty path is rejected."""
        from empathy_os.orchestration.config_store import _validate_file_path

        with pytest.raises(ValueError, match="path must be a non-empty string"):
            _validate_file_path("")

    def test_validate_file_path_non_string(self):
        """Test that non-string path is rejected."""
        from empathy_os.orchestration.config_store import _validate_file_path

        with pytest.raises(ValueError, match="path must be a non-empty string"):
            _validate_file_path(None)

    def test_validate_file_path_outside_allowed_dir(self, tmp_path):
        """Test that paths outside allowed directory are rejected."""
        from empathy_os.orchestration.config_store import _validate_file_path

        allowed_dir = tmp_path / "allowed"
        allowed_dir.mkdir()

        # Try to access parent directory
        outside_path = tmp_path / "outside.json"

        with pytest.raises(ValueError, match="path must be within"):
            _validate_file_path(str(outside_path), allowed_dir=str(allowed_dir))

    @pytest.mark.skipif(not Path("/proc").exists(), reason="Test requires Linux /proc filesystem")
    def test_validate_file_path_system_directory(self):
        """Test that system directories are blocked (Linux only)."""
        from empathy_os.orchestration.config_store import _validate_file_path

        # Test paths that exist on Linux and should be blocked
        # Note: On macOS, /etc is a symlink to /private/etc which complicates testing
        system_paths = ["/proc/test", "/sys/test.json"]

        for path in system_paths:
            with pytest.raises(ValueError, match="Cannot write to system directory"):
                _validate_file_path(path)

    def test_validate_file_path_within_allowed_dir(self, tmp_path):
        """Test that paths within allowed directory are accepted."""
        from empathy_os.orchestration.config_store import _validate_file_path

        allowed_dir = tmp_path / "allowed"
        allowed_dir.mkdir()

        test_file = allowed_dir / "test.json"

        result = _validate_file_path(str(test_file), allowed_dir=str(allowed_dir))

        assert result.resolve() == test_file.resolve()
