"""Agent Configuration Store - Learning and Memory System for Agent Compositions

Saves and retrieves successful agent team configurations, enabling the meta-orchestrator
to learn from outcomes and reuse proven compositions.

This is the "memory" component of the meta-orchestration system - it learns which
agent teams work best for specific task types and progressively improves.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from empathy_os.pattern_library import Pattern, PatternLibrary

logger = logging.getLogger(__name__)


def _validate_file_path(path: str, allowed_dir: str | None = None) -> Path:
    """Validate file path to prevent path traversal and arbitrary writes.

    Args:
        path: File path to validate
        allowed_dir: Optional directory to restrict writes to

    Returns:
        Validated Path object

    Raises:
        ValueError: If path is invalid or unsafe
    """
    if not path or not isinstance(path, str):
        raise ValueError("path must be a non-empty string")

    # Check for null bytes
    if "\x00" in path:
        raise ValueError("path contains null bytes")

    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}")

    # Check if within allowed directory
    if allowed_dir:
        try:
            allowed = Path(allowed_dir).resolve()
            resolved.relative_to(allowed)
        except ValueError:
            raise ValueError(f"path must be within {allowed_dir}")

    # Check for dangerous system paths
    dangerous_paths = ["/etc", "/sys", "/proc", "/dev"]
    for dangerous in dangerous_paths:
        if str(resolved).startswith(dangerous):
            raise ValueError(f"Cannot write to system directory: {dangerous}")

    return resolved


@dataclass
class AgentConfiguration:
    """Saved configuration for a successful agent team composition.

    Represents a proven solution: the team composition, execution strategy,
    and performance metrics for a specific task pattern.

    This is what gets saved when an orchestration succeeds, and what gets
    retrieved when the system recognizes a similar task in the future.

    Example:
        >>> config = AgentConfiguration(
        ...     id="comp_release_prep_001",
        ...     task_pattern="release_preparation",
        ...     agents=[
        ...         {"role": "security_auditor", "tier": "PREMIUM"},
        ...         {"role": "test_analyzer", "tier": "CAPABLE"},
        ...     ],
        ...     strategy="parallel",
        ...     quality_gates={"min_coverage": 80},
        ...     success_rate=0.95,
        ...     avg_quality_score=87.5,
        ... )
    """

    # Identity
    id: str
    task_pattern: str  # "release_prep", "test_coverage_boost", etc.

    # Team Composition
    agents: list[dict[str, Any]]  # List of agent configs (role, tier, tools, etc.)
    strategy: str  # "sequential", "parallel", "debate", etc.

    # Quality Criteria
    quality_gates: dict[str, Any]  # Min thresholds (coverage, security score, etc.)

    # Performance Metrics
    success_rate: float = 0.0  # 0.0-1.0
    avg_quality_score: float = 0.0  # 0-100
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime | None = None
    tags: list[str] = field(default_factory=list)

    def record_outcome(self, success: bool, quality_score: float) -> None:
        """Record an execution outcome and update metrics.

        Args:
            success: Whether the orchestration succeeded (met quality gates)
            quality_score: Quality score from 0-100

        Raises:
            ValueError: If quality_score is out of range
        """
        if not 0.0 <= quality_score <= 100.0:
            raise ValueError(f"quality_score must be 0-100, got {quality_score}")

        self.usage_count += 1
        self.last_used = datetime.now()

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        # Update success rate
        if self.usage_count > 0:
            self.success_rate = self.success_count / self.usage_count

        # Update rolling average quality score
        if self.usage_count == 1:
            self.avg_quality_score = quality_score
        else:
            # Weighted average: recent scores matter more
            weight = 0.7  # 70% weight on new score
            self.avg_quality_score = weight * quality_score + (1 - weight) * self.avg_quality_score

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data["created_at"] = self.created_at.isoformat()
        data["last_used"] = self.last_used.isoformat() if self.last_used else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentConfiguration":
        """Deserialize from dictionary.

        Args:
            data: Dictionary from JSON

        Returns:
            AgentConfiguration instance
        """
        # Convert ISO format strings back to datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "last_used" in data and data["last_used"]:
            data["last_used"] = datetime.fromisoformat(data["last_used"])

        return cls(**data)


class ConfigurationStore:
    """Persistent storage for successful agent team compositions.

    This is the learning/memory system for the meta-orchestrator. It:
    1. Saves successful compositions to disk
    2. Retrieves proven solutions for similar tasks
    3. Tracks performance metrics over time
    4. Integrates with pattern library for cross-task learning

    File structure:
        .empathy/orchestration/compositions/
        ├── release_prep_001.json
        ├── test_coverage_boost_001.json
        └── security_deep_dive_001.json

    Example:
        >>> store = ConfigurationStore()
        >>>
        >>> # Save successful composition
        >>> config = AgentConfiguration(
        ...     id="comp_001",
        ...     task_pattern="release_prep",
        ...     agents=[...],
        ...     strategy="parallel",
        ... )
        >>> store.save(config)
        >>>
        >>> # Load for reuse
        >>> loaded = store.load("comp_001")
        >>>
        >>> # Search for similar tasks
        >>> matches = store.search(task_pattern="release_prep", min_success_rate=0.8)
    """

    def __init__(
        self,
        storage_dir: str | None = None,
        pattern_library: PatternLibrary | None = None,
    ):
        """Initialize configuration store.

        Args:
            storage_dir: Directory for storing configurations
                        (default: .empathy/orchestration/compositions/)
            pattern_library: Optional pattern library for integration
        """
        # Set default storage directory
        if storage_dir is None:
            storage_dir = ".empathy/orchestration/compositions"

        self.storage_dir = Path(storage_dir)
        self.pattern_library = pattern_library

        # Create storage directory if it doesn't exist
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create storage directory {self.storage_dir}: {e}")
            raise ValueError(f"Cannot create storage directory: {e}") from e

        # In-memory cache for fast lookups
        self._cache: dict[str, AgentConfiguration] = {}
        self._loaded = False

    def _load_all_from_disk(self) -> None:
        """Load all configurations from disk into cache.

        This is called lazily on first access to avoid startup overhead.
        """
        if self._loaded:
            return

        try:
            for config_file in self.storage_dir.glob("*.json"):
                try:
                    with config_file.open("r") as f:
                        data = json.load(f)
                        config = AgentConfiguration.from_dict(data)
                        self._cache[config.id] = config
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.warning(f"Failed to load {config_file}: {e}")
                    continue

            logger.info(f"Loaded {len(self._cache)} configurations from disk")
            self._loaded = True

        except OSError as e:
            logger.error(f"Error reading from {self.storage_dir}: {e}")
            # Don't raise - start with empty cache

    def save(self, config: AgentConfiguration) -> Path:
        """Save agent configuration to disk and update pattern library.

        Args:
            config: Configuration to save

        Returns:
            Path to saved file

        Raises:
            ValueError: If config.id is invalid or file path is unsafe
            OSError: If file write fails
        """
        if not config.id or not isinstance(config.id, str):
            raise ValueError("config.id must be a non-empty string")

        # Validate filename (prevent path traversal)
        filename = f"{config.id}.json"
        file_path = self.storage_dir / filename

        # Security: validate path is within storage_dir
        validated_path = _validate_file_path(str(file_path), allowed_dir=str(self.storage_dir))

        # Save to disk
        try:
            with validated_path.open("w") as f:
                json.dump(config.to_dict(), f, indent=2)

            logger.info(f"Saved configuration {config.id} to {validated_path}")

        except OSError as e:
            logger.error(f"Failed to save configuration {config.id}: {e}")
            raise

        # Update in-memory cache
        self._cache[config.id] = config

        # Integrate with pattern library
        if self.pattern_library:
            self._contribute_to_pattern_library(config)

        return validated_path

    def load(self, config_id: str) -> AgentConfiguration | None:
        """Load configuration by ID.

        Args:
            config_id: Configuration ID to load

        Returns:
            Configuration if found, None otherwise

        Raises:
            ValueError: If config_id is invalid
        """
        if not config_id or not isinstance(config_id, str):
            raise ValueError("config_id must be a non-empty string")

        # Load all configs if not already loaded
        self._load_all_from_disk()

        # Return from cache
        return self._cache.get(config_id)

    def search(
        self,
        task_pattern: str | None = None,
        min_success_rate: float = 0.0,
        min_quality_score: float = 0.0,
        limit: int = 10,
    ) -> list[AgentConfiguration]:
        """Search for configurations matching criteria.

        Args:
            task_pattern: Filter by task pattern (e.g., "release_prep")
            min_success_rate: Minimum success rate (0.0-1.0)
            min_quality_score: Minimum average quality score (0-100)
            limit: Maximum results to return

        Returns:
            List of matching configurations, sorted by success rate descending

        Raises:
            ValueError: If parameters are out of range
        """
        if not 0.0 <= min_success_rate <= 1.0:
            raise ValueError(f"min_success_rate must be 0-1, got {min_success_rate}")

        if not 0.0 <= min_quality_score <= 100.0:
            raise ValueError(f"min_quality_score must be 0-100, got {min_quality_score}")

        if limit < 1:
            raise ValueError(f"limit must be positive, got {limit}")

        # Load all configs if not already loaded
        self._load_all_from_disk()

        # Filter by criteria
        matches: list[AgentConfiguration] = []

        for config in self._cache.values():
            # Filter by task pattern
            if task_pattern and config.task_pattern != task_pattern:
                continue

            # Filter by success rate
            if config.success_rate < min_success_rate:
                continue

            # Filter by quality score
            if config.avg_quality_score < min_quality_score:
                continue

            matches.append(config)

        # Sort by success rate (descending), then quality score (descending)
        matches.sort(key=lambda c: (c.success_rate, c.avg_quality_score), reverse=True)

        # Apply limit
        return matches[:limit]

    def get_best_for_task(self, task_pattern: str) -> AgentConfiguration | None:
        """Get the best-performing configuration for a specific task pattern.

        Args:
            task_pattern: Task pattern to find configuration for

        Returns:
            Best configuration if found, None otherwise
        """
        results = self.search(task_pattern=task_pattern, limit=1)
        return results[0] if results else None

    def delete(self, config_id: str) -> bool:
        """Delete a configuration.

        Args:
            config_id: Configuration ID to delete

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If config_id is invalid
            OSError: If file deletion fails
        """
        if not config_id or not isinstance(config_id, str):
            raise ValueError("config_id must be a non-empty string")

        # Load all configs if not already loaded
        self._load_all_from_disk()

        # Check if exists in cache
        if config_id not in self._cache:
            return False

        # Delete from disk
        file_path = self.storage_dir / f"{config_id}.json"
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Deleted configuration {config_id}")
            except OSError as e:
                logger.error(f"Failed to delete {file_path}: {e}")
                raise

        # Delete from cache
        del self._cache[config_id]

        return True

    def list_all(self) -> list[AgentConfiguration]:
        """List all configurations.

        Returns:
            List of all configurations, sorted by last_used descending
        """
        self._load_all_from_disk()

        configs = list(self._cache.values())

        # Sort by last_used (most recent first), with never-used at end
        configs.sort(
            key=lambda c: c.last_used or datetime.min,
            reverse=True,
        )

        return configs

    def _contribute_to_pattern_library(self, config: AgentConfiguration) -> None:
        """Contribute successful configuration as a pattern to pattern library.

        This enables cross-task learning - patterns learned from one type of
        orchestration can inform decisions on other tasks.

        Args:
            config: Configuration to contribute as pattern
        """
        if not self.pattern_library:
            return

        # Only contribute configurations with proven success
        if config.usage_count < 3 or config.success_rate < 0.7:
            logger.debug(
                f"Configuration {config.id} not yet proven "
                f"(uses={config.usage_count}, rate={config.success_rate:.2f})"
            )
            return

        pattern = Pattern(
            id=f"orchestration_{config.id}",
            agent_id="meta_orchestrator",
            pattern_type="agent_composition",
            name=config.task_pattern,
            description=f"Successful agent composition for {config.task_pattern}",
            context={
                "agents": config.agents,
                "strategy": config.strategy,
                "quality_gates": config.quality_gates,
                "success_rate": config.success_rate,
                "avg_quality_score": config.avg_quality_score,
            },
            confidence=config.success_rate,
            usage_count=config.usage_count,
            success_count=config.success_count,
            failure_count=config.failure_count,
            tags=config.tags,
        )

        try:
            self.pattern_library.contribute_pattern("meta_orchestrator", pattern)
            logger.info(f"Contributed pattern for {config.task_pattern} to pattern library")
        except ValueError as e:
            # Pattern might already exist - that's okay
            logger.debug(f"Pattern already exists in library: {e}")
