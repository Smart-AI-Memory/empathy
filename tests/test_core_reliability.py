"""Reliable Core Tests for Empathy Framework

These tests focus on core functionality with high reliability:
- No external API calls
- No network dependencies
- Fast execution
- Deterministic results

Copyright 2025 Smart AI Memory
"""

import os

import pytest

# ============================================================================
# EmpathyConfig Tests
# ============================================================================


class TestEmpathyConfig:
    """Test EmpathyConfig dataclass and methods."""

    def test_config_defaults(self):
        """Test default configuration values."""
        from empathy_os.config import EmpathyConfig

        config = EmpathyConfig()

        assert config.user_id == "default_user"
        assert config.target_level == 3
        assert config.confidence_threshold == 0.75
        assert config.persistence_enabled is True
        assert config.persistence_backend == "sqlite"

    def test_config_custom_values(self):
        """Test custom configuration values."""
        from empathy_os.config import EmpathyConfig

        config = EmpathyConfig(
            user_id="test_user",
            target_level=5,
            confidence_threshold=0.9,
        )

        assert config.user_id == "test_user"
        assert config.target_level == 5
        assert config.confidence_threshold == 0.9

    def test_config_from_env_filters_unknown_fields(self):
        """Test from_env filters out unknown environment variables."""
        from empathy_os.config import EmpathyConfig

        # Set a valid and an invalid env var
        os.environ["EMPATHY_USER_ID"] = "env_user"
        os.environ["EMPATHY_UNKNOWN_FIELD"] = "should_be_ignored"
        os.environ["EMPATHY_MASTER_KEY"] = "should_also_be_ignored"

        try:
            config = EmpathyConfig.from_env()
            assert config.user_id == "env_user"
            # Should not raise an error for unknown fields
            assert not hasattr(config, "unknown_field")
            assert not hasattr(config, "master_key")
        finally:
            # Cleanup
            del os.environ["EMPATHY_USER_ID"]
            del os.environ["EMPATHY_UNKNOWN_FIELD"]
            del os.environ["EMPATHY_MASTER_KEY"]

    def test_config_from_env_type_conversion(self):
        """Test from_env correctly converts types."""
        from empathy_os.config import EmpathyConfig

        os.environ["EMPATHY_TARGET_LEVEL"] = "4"
        os.environ["EMPATHY_CONFIDENCE_THRESHOLD"] = "0.85"
        os.environ["EMPATHY_PERSISTENCE_ENABLED"] = "false"

        try:
            config = EmpathyConfig.from_env()
            assert config.target_level == 4
            assert config.confidence_threshold == 0.85
            assert config.persistence_enabled is False
        finally:
            del os.environ["EMPATHY_TARGET_LEVEL"]
            del os.environ["EMPATHY_CONFIDENCE_THRESHOLD"]
            del os.environ["EMPATHY_PERSISTENCE_ENABLED"]

    def test_config_validate_valid(self):
        """Test validation passes for valid config."""
        from empathy_os.config import EmpathyConfig

        config = EmpathyConfig(target_level=3, confidence_threshold=0.8)
        assert config.validate() is True

    def test_config_validate_invalid_level(self):
        """Test validation fails for invalid target level."""
        from empathy_os.config import EmpathyConfig

        config = EmpathyConfig(target_level=10)
        with pytest.raises(ValueError, match="target_level must be 1-5"):
            config.validate()

    def test_config_validate_invalid_confidence(self):
        """Test validation fails for invalid confidence threshold."""
        from empathy_os.config import EmpathyConfig

        config = EmpathyConfig(confidence_threshold=1.5)
        with pytest.raises(ValueError, match="confidence_threshold must be 0.0-1.0"):
            config.validate()

    def test_config_to_dict(self):
        """Test conversion to dictionary."""
        from empathy_os.config import EmpathyConfig

        config = EmpathyConfig(user_id="dict_test")
        d = config.to_dict()

        assert isinstance(d, dict)
        assert d["user_id"] == "dict_test"
        assert "target_level" in d
        assert "confidence_threshold" in d

    def test_config_merge(self):
        """Test merging two configurations."""
        from empathy_os.config import EmpathyConfig

        base = EmpathyConfig(user_id="base", target_level=2)
        override = EmpathyConfig(target_level=4)

        merged = base.merge(override)

        assert merged.user_id == "base"  # Kept from base
        assert merged.target_level == 4  # Overridden


# ============================================================================
# Model Registry Tests
# ============================================================================


class TestModelRegistry:
    """Test model registry functionality."""

    def test_get_all_models(self):
        """Test getting all registered models."""
        from empathy_os.models import get_all_models

        models = get_all_models()

        assert isinstance(models, dict)
        assert "anthropic" in models
        assert "openai" in models

    def test_anthropic_models_have_tiers(self):
        """Test Anthropic provider has all required tiers."""
        from empathy_os.models import get_all_models

        models = get_all_models()
        anthropic = models.get("anthropic", {})

        assert "cheap" in anthropic
        assert "capable" in anthropic
        assert "premium" in anthropic

    def test_model_info_has_required_fields(self):
        """Test model info has all required fields."""
        from empathy_os.models import get_all_models

        models = get_all_models()

        for provider, tiers in models.items():
            for tier, info in tiers.items():
                assert hasattr(info, "id"), f"{provider}/{tier} missing id"
                assert hasattr(info, "input_cost_per_million")
                assert hasattr(info, "output_cost_per_million")
                assert hasattr(info, "max_tokens")


# ============================================================================
# Workflow Registry Tests
# ============================================================================


class TestWorkflowRegistry:
    """Test workflow registry."""

    def test_workflow_registry_exists(self):
        """Test workflow registry is populated."""
        from empathy_os.workflows import WORKFLOW_REGISTRY

        assert isinstance(WORKFLOW_REGISTRY, dict)
        assert len(WORKFLOW_REGISTRY) > 0

    def test_key_workflows_registered(self):
        """Test key workflows are registered."""
        from empathy_os.workflows import WORKFLOW_REGISTRY

        expected = [
            "code-review",
            "security-audit",
            "health-check",
            "test-gen",
            "doc-gen",
        ]

        for workflow in expected:
            assert workflow in WORKFLOW_REGISTRY, f"{workflow} not registered"

    def test_workflow_entries_are_valid(self):
        """Test workflow entries are valid workflow classes or dicts."""
        from empathy_os.workflows import WORKFLOW_REGISTRY

        for name, entry in WORKFLOW_REGISTRY.items():
            # Entry can be a class or a dict with 'class' key
            if isinstance(entry, dict):
                assert "class" in entry, f"{name} missing 'class'"
            else:
                # It's a class directly
                assert callable(entry), f"{name} is not callable"


# ============================================================================
# Cost Tracker Tests
# ============================================================================


class TestCostTracker:
    """Test cost tracking functionality."""

    def test_model_pricing_exists(self):
        """Test MODEL_PRICING dictionary is populated."""
        from empathy_os.cost_tracker import MODEL_PRICING

        assert isinstance(MODEL_PRICING, dict)
        assert len(MODEL_PRICING) > 0

    def test_tier_pricing_exists(self):
        """Test tier pricing aliases exist."""
        from empathy_os.cost_tracker import MODEL_PRICING

        assert "cheap" in MODEL_PRICING
        assert "capable" in MODEL_PRICING
        assert "premium" in MODEL_PRICING

    def test_tier_pricing_has_input_output(self):
        """Test tier pricing has input and output costs."""
        from empathy_os.cost_tracker import MODEL_PRICING

        for tier in ["cheap", "capable", "premium"]:
            assert "input" in MODEL_PRICING[tier]
            assert "output" in MODEL_PRICING[tier]
            assert MODEL_PRICING[tier]["input"] >= 0
            assert MODEL_PRICING[tier]["output"] >= 0

    def test_premium_costs_more_than_cheap(self):
        """Test pricing tiers are ordered correctly."""
        from empathy_os.cost_tracker import MODEL_PRICING

        assert MODEL_PRICING["premium"]["input"] > MODEL_PRICING["cheap"]["input"]
        assert MODEL_PRICING["premium"]["output"] > MODEL_PRICING["cheap"]["output"]


# ============================================================================
# Health Check Crew Tests
# ============================================================================


class TestHealthCheckCrewStructure:
    """Test HealthCheckCrew structure and types."""

    def test_health_category_enum(self):
        """Test HealthCategory enum values."""
        from empathy_llm_toolkit.agent_factory.crews.health_check import HealthCategory

        assert HealthCategory.LINT.value == "lint"
        assert HealthCategory.TYPES.value == "types"
        assert HealthCategory.TESTS.value == "tests"
        assert HealthCategory.SECURITY.value == "security"

    def test_issue_severity_enum(self):
        """Test IssueSeverity enum values."""
        from empathy_llm_toolkit.agent_factory.crews.health_check import IssueSeverity

        assert IssueSeverity.CRITICAL.value == "critical"
        assert IssueSeverity.HIGH.value == "high"
        assert IssueSeverity.MEDIUM.value == "medium"
        assert IssueSeverity.LOW.value == "low"
        assert IssueSeverity.INFO.value == "info"

    def test_health_issue_dataclass(self):
        """Test HealthIssue dataclass structure."""
        from empathy_llm_toolkit.agent_factory.crews.health_check import (
            HealthCategory,
            HealthIssue,
            IssueSeverity,
        )

        issue = HealthIssue(
            title="Test Issue",
            description="A test issue",
            category=HealthCategory.LINT,
            severity=IssueSeverity.MEDIUM,
        )

        assert issue.title == "Test Issue"
        assert issue.category == HealthCategory.LINT
        assert issue.severity == IssueSeverity.MEDIUM

        # Test to_dict
        d = issue.to_dict()
        assert d["title"] == "Test Issue"
        assert d["category"] == "lint"
        assert d["severity"] == "medium"

    def test_health_score_calculation(self):
        """Test health score calculation with category caps."""
        from empathy_llm_toolkit.agent_factory.crews.health_check import (
            HealthCategory,
            HealthCheckCrew,
            HealthIssue,
            IssueSeverity,
        )

        # Create many lint issues - should be capped
        issues = [
            HealthIssue(
                title=f"Lint issue {i}",
                description="Lint warning",
                category=HealthCategory.LINT,
                severity=IssueSeverity.MEDIUM,
            )
            for i in range(50)
        ]

        crew = HealthCheckCrew.__new__(HealthCheckCrew)
        score = crew._calculate_health_score(issues)

        # With cap of 15 for lint, score should be 85
        assert score >= 80, f"Score {score} too low - cap not working"
        assert score <= 100


# ============================================================================
# Import Smoke Tests
# ============================================================================


class TestImports:
    """Smoke tests for critical imports."""

    def test_empathy_os_imports(self):
        """Test main empathy_os imports work."""
        from empathy_os import EmpathyOS
        from empathy_os.config import EmpathyConfig
        from empathy_os.models import get_all_models

        assert EmpathyOS is not None
        assert EmpathyConfig is not None
        assert callable(get_all_models)

    def test_crew_imports(self):
        """Test crew imports work."""
        from empathy_llm_toolkit.agent_factory.crews import (
            CodeReviewCrew,
            HealthCheckCrew,
            SecurityAuditCrew,
        )

        assert HealthCheckCrew is not None
        assert CodeReviewCrew is not None
        assert SecurityAuditCrew is not None

    def test_workflow_imports(self):
        """Test workflow imports work."""
        from empathy_os.workflows import WORKFLOW_REGISTRY
        from empathy_os.workflows.base import BaseWorkflow

        assert WORKFLOW_REGISTRY is not None
        assert BaseWorkflow is not None
