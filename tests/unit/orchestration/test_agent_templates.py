"""Tests for agent template system.

Test coverage:
    - AgentCapability creation and validation
    - ResourceRequirements creation and validation
    - AgentTemplate creation and validation
    - Template registry operations
    - Pre-built template validation
"""

import pytest

from empathy_os.orchestration.agent_templates import (
    AgentCapability,
    AgentTemplate,
    ResourceRequirements,
    get_all_templates,
    get_template,
    get_templates_by_capability,
    get_templates_by_tier,
)


class TestAgentCapability:
    """Test AgentCapability dataclass."""

    def test_create_valid_capability(self):
        """Test creating a valid capability."""
        cap = AgentCapability(
            name="analyze_gaps",
            description="Identify test coverage gaps",
            required_tools=["coverage_analyzer"],
        )

        assert cap.name == "analyze_gaps"
        assert cap.description == "Identify test coverage gaps"
        assert cap.required_tools == ["coverage_analyzer"]

    def test_create_capability_without_tools(self):
        """Test creating capability without required tools."""
        cap = AgentCapability(
            name="simple_task",
            description="A simple task",
        )

        assert cap.name == "simple_task"
        assert cap.required_tools == []

    def test_capability_is_frozen(self):
        """Test that capability is immutable."""
        cap = AgentCapability(
            name="analyze_gaps",
            description="Identify test coverage gaps",
        )

        with pytest.raises(AttributeError):
            cap.name = "new_name"

    def test_create_capability_with_empty_name(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            AgentCapability(
                name="",
                description="Test description",
            )

    def test_create_capability_with_invalid_name_type(self):
        """Test that non-string name raises ValueError."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            AgentCapability(
                name=123,  # type: ignore
                description="Test description",
            )

    def test_create_capability_with_empty_description(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="description must be a non-empty string"):
            AgentCapability(
                name="test",
                description="",
            )

    def test_create_capability_with_invalid_tools_type(self):
        """Test that non-list tools raises ValueError."""
        with pytest.raises(ValueError, match="required_tools must be a list"):
            AgentCapability(
                name="test",
                description="Test description",
                required_tools="not_a_list",  # type: ignore
            )


class TestResourceRequirements:
    """Test ResourceRequirements dataclass."""

    def test_create_valid_requirements(self):
        """Test creating valid resource requirements."""
        req = ResourceRequirements(
            min_tokens=1000,
            max_tokens=10000,
            timeout_seconds=300,
            memory_mb=512,
        )

        assert req.min_tokens == 1000
        assert req.max_tokens == 10000
        assert req.timeout_seconds == 300
        assert req.memory_mb == 512

    def test_create_requirements_with_defaults(self):
        """Test creating requirements with default values."""
        req = ResourceRequirements()

        assert req.min_tokens == 1000
        assert req.max_tokens == 10000
        assert req.timeout_seconds == 300
        assert req.memory_mb == 512

    def test_requirements_is_frozen(self):
        """Test that requirements is immutable."""
        req = ResourceRequirements()

        with pytest.raises(AttributeError):
            req.min_tokens = 2000

    def test_create_requirements_with_negative_min_tokens(self):
        """Test that negative min_tokens raises ValueError."""
        with pytest.raises(ValueError, match="min_tokens must be non-negative"):
            ResourceRequirements(min_tokens=-100)

    def test_create_requirements_with_invalid_max_tokens(self):
        """Test that max_tokens < min_tokens raises ValueError."""
        with pytest.raises(ValueError, match="max_tokens must be >= min_tokens"):
            ResourceRequirements(min_tokens=1000, max_tokens=500)

    def test_create_requirements_with_zero_timeout(self):
        """Test that zero timeout raises ValueError."""
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            ResourceRequirements(timeout_seconds=0)

    def test_create_requirements_with_negative_timeout(self):
        """Test that negative timeout raises ValueError."""
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            ResourceRequirements(timeout_seconds=-100)

    def test_create_requirements_with_zero_memory(self):
        """Test that zero memory raises ValueError."""
        with pytest.raises(ValueError, match="memory_mb must be positive"):
            ResourceRequirements(memory_mb=0)


class TestAgentTemplate:
    """Test AgentTemplate dataclass."""

    def test_create_valid_template(self):
        """Test creating a valid agent template."""
        template = AgentTemplate(
            id="test_analyzer",
            role="Test Analyzer",
            capabilities=["analyze", "suggest"],
            tier_preference="CAPABLE",
            tools=["analyzer"],
            default_instructions="Analyze and suggest improvements",
            quality_gates={"min_quality": 7},
        )

        assert template.id == "test_analyzer"
        assert template.role == "Test Analyzer"
        assert template.capabilities == ["analyze", "suggest"]
        assert template.tier_preference == "CAPABLE"
        assert template.tools == ["analyzer"]
        assert template.default_instructions == "Analyze and suggest improvements"
        assert template.quality_gates == {"min_quality": 7}
        assert isinstance(template.resource_requirements, ResourceRequirements)

    def test_create_template_with_custom_resources(self):
        """Test creating template with custom resource requirements."""
        resources = ResourceRequirements(
            min_tokens=5000,
            max_tokens=20000,
            timeout_seconds=600,
            memory_mb=1024,
        )

        template = AgentTemplate(
            id="test_analyzer",
            role="Test Analyzer",
            capabilities=["analyze"],
            tier_preference="CAPABLE",
            tools=["analyzer"],
            default_instructions="Analyze code",
            quality_gates={},
            resource_requirements=resources,
        )

        assert template.resource_requirements == resources
        assert template.resource_requirements.min_tokens == 5000

    def test_template_is_frozen(self):
        """Test that template is immutable."""
        template = AgentTemplate(
            id="test_analyzer",
            role="Test Analyzer",
            capabilities=["analyze"],
            tier_preference="CAPABLE",
            tools=["analyzer"],
            default_instructions="Analyze code",
            quality_gates={},
        )

        with pytest.raises(AttributeError):
            template.id = "new_id"

    def test_create_template_with_empty_id(self):
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id must be a non-empty string"):
            AgentTemplate(
                id="",
                role="Test Analyzer",
                capabilities=["analyze"],
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_empty_role(self):
        """Test that empty role raises ValueError."""
        with pytest.raises(ValueError, match="role must be a non-empty string"):
            AgentTemplate(
                id="test_analyzer",
                role="",
                capabilities=["analyze"],
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_invalid_capabilities_type(self):
        """Test that non-list capabilities raises ValueError."""
        with pytest.raises(ValueError, match="capabilities must be a list"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities="not_a_list",  # type: ignore
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_empty_capabilities(self):
        """Test that empty capabilities raises ValueError."""
        with pytest.raises(ValueError, match="capabilities must not be empty"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=[],
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_invalid_capability_item(self):
        """Test that non-string capability raises ValueError."""
        with pytest.raises(ValueError, match="all capabilities must be non-empty strings"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=["analyze", 123],  # type: ignore
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_invalid_tier(self):
        """Test that invalid tier raises ValueError."""
        with pytest.raises(ValueError, match="tier_preference must be one of"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=["analyze"],
                tier_preference="INVALID",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_invalid_tools_type(self):
        """Test that non-list tools raises ValueError."""
        with pytest.raises(ValueError, match="tools must be a list"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=["analyze"],
                tier_preference="CAPABLE",
                tools="not_a_list",  # type: ignore
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_invalid_tool_item(self):
        """Test that non-string tool raises ValueError."""
        with pytest.raises(ValueError, match="all tools must be non-empty strings"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=["analyze"],
                tier_preference="CAPABLE",
                tools=["analyzer", 123],  # type: ignore
                default_instructions="Analyze code",
                quality_gates={},
            )

    def test_create_template_with_empty_instructions(self):
        """Test that empty instructions raises ValueError."""
        with pytest.raises(ValueError, match="default_instructions must be a non-empty string"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=["analyze"],
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="",
                quality_gates={},
            )

    def test_create_template_with_invalid_quality_gates_type(self):
        """Test that non-dict quality_gates raises ValueError."""
        with pytest.raises(ValueError, match="quality_gates must be a dict"):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=["analyze"],
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates="not_a_dict",  # type: ignore
            )

    def test_create_template_with_invalid_resource_requirements(self):
        """Test that invalid resource_requirements raises ValueError."""
        with pytest.raises(
            ValueError,
            match="resource_requirements must be a ResourceRequirements instance",
        ):
            AgentTemplate(
                id="test_analyzer",
                role="Test Analyzer",
                capabilities=["analyze"],
                tier_preference="CAPABLE",
                tools=["analyzer"],
                default_instructions="Analyze code",
                quality_gates={},
                resource_requirements="not_valid",  # type: ignore
            )


class TestTemplateRegistry:
    """Test template registry operations."""

    def test_get_template_by_id(self):
        """Test retrieving template by ID."""
        template = get_template("test_coverage_analyzer")

        assert template is not None
        assert template.id == "test_coverage_analyzer"
        assert template.role == "Test Coverage Expert"

    def test_get_nonexistent_template(self):
        """Test that nonexistent template returns None."""
        template = get_template("nonexistent_template")

        assert template is None

    def test_get_template_with_invalid_id_type(self):
        """Test that invalid ID type returns None."""
        template = get_template(123)  # type: ignore

        assert template is None

    def test_get_template_with_empty_id(self):
        """Test that empty ID returns None."""
        template = get_template("")

        assert template is None

    def test_get_all_templates(self):
        """Test retrieving all templates."""
        templates = get_all_templates()

        assert isinstance(templates, list)
        assert len(templates) >= 7  # At least 7 pre-built templates

        # Verify all expected templates are present
        template_ids = {t.id for t in templates}
        expected_ids = {
            "test_coverage_analyzer",
            "security_auditor",
            "code_reviewer",
            "documentation_writer",
            "performance_optimizer",
            "architecture_analyst",
            "refactoring_specialist",
        }
        assert expected_ids.issubset(template_ids)

    def test_get_templates_by_capability(self):
        """Test retrieving templates by capability."""
        templates = get_templates_by_capability("analyze_gaps")

        assert isinstance(templates, list)
        assert len(templates) >= 1

        # Verify test_coverage_analyzer is in results
        assert any(t.id == "test_coverage_analyzer" for t in templates)

        # Verify all returned templates have the capability
        for template in templates:
            assert "analyze_gaps" in template.capabilities

    def test_get_templates_by_nonexistent_capability(self):
        """Test that nonexistent capability returns empty list."""
        templates = get_templates_by_capability("nonexistent_capability")

        assert templates == []

    def test_get_templates_by_capability_with_invalid_type(self):
        """Test that invalid capability type returns empty list."""
        templates = get_templates_by_capability(123)  # type: ignore

        assert templates == []

    def test_get_templates_by_tier(self):
        """Test retrieving templates by tier."""
        capable_templates = get_templates_by_tier("CAPABLE")

        assert isinstance(capable_templates, list)
        assert len(capable_templates) > 0

        # Verify all returned templates prefer CAPABLE tier
        for template in capable_templates:
            assert template.tier_preference == "CAPABLE"

    def test_get_templates_by_invalid_tier(self):
        """Test that invalid tier returns empty list."""
        templates = get_templates_by_tier("INVALID_TIER")

        assert templates == []

    def test_templates_by_tier_coverage(self):
        """Test that all tiers have at least one template."""
        cheap_templates = get_templates_by_tier("CHEAP")
        capable_templates = get_templates_by_tier("CAPABLE")
        premium_templates = get_templates_by_tier("PREMIUM")

        assert len(cheap_templates) > 0
        assert len(capable_templates) > 0
        assert len(premium_templates) > 0


class TestPreBuiltTemplates:
    """Test all pre-built templates."""

    def test_test_coverage_analyzer(self):
        """Test test_coverage_analyzer template."""
        template = get_template("test_coverage_analyzer")

        assert template is not None
        assert template.id == "test_coverage_analyzer"
        assert template.role == "Test Coverage Expert"
        assert template.tier_preference == "CAPABLE"
        assert "analyze_gaps" in template.capabilities
        assert "suggest_tests" in template.capabilities
        assert "validate_coverage" in template.capabilities
        assert "coverage_analyzer" in template.tools
        assert "ast_parser" in template.tools
        assert template.quality_gates["min_coverage"] == 80
        assert template.resource_requirements.min_tokens == 2000

    def test_security_auditor(self):
        """Test security_auditor template."""
        template = get_template("security_auditor")

        assert template is not None
        assert template.id == "security_auditor"
        assert template.role == "Security Auditor"
        assert template.tier_preference == "PREMIUM"
        assert "vulnerability_scan" in template.capabilities
        assert "threat_modeling" in template.capabilities
        assert "compliance_check" in template.capabilities
        assert "security_scanner" in template.tools
        assert template.quality_gates["max_critical_issues"] == 0
        assert template.resource_requirements.min_tokens == 5000

    def test_code_reviewer(self):
        """Test code_reviewer template."""
        template = get_template("code_reviewer")

        assert template is not None
        assert template.id == "code_reviewer"
        assert template.role == "Code Quality Reviewer"
        assert template.tier_preference == "CAPABLE"
        assert "code_review" in template.capabilities
        assert "quality_assessment" in template.capabilities
        assert "best_practices_check" in template.capabilities
        assert "ast_parser" in template.tools
        assert template.quality_gates["min_quality_score"] == 7

    def test_documentation_writer(self):
        """Test documentation_writer template."""
        template = get_template("documentation_writer")

        assert template is not None
        assert template.id == "documentation_writer"
        assert template.role == "Documentation Writer"
        assert template.tier_preference == "CHEAP"
        assert "generate_docs" in template.capabilities
        assert "check_completeness" in template.capabilities
        assert "update_examples" in template.capabilities
        assert "doc_generator" in template.tools
        assert template.quality_gates["min_doc_coverage"] == 100

    def test_performance_optimizer(self):
        """Test performance_optimizer template."""
        template = get_template("performance_optimizer")

        assert template is not None
        assert template.id == "performance_optimizer"
        assert template.role == "Performance Optimizer"
        assert template.tier_preference == "CAPABLE"
        assert "profile_code" in template.capabilities
        assert "identify_bottlenecks" in template.capabilities
        assert "suggest_optimizations" in template.capabilities
        assert "profiler" in template.tools
        assert template.quality_gates["min_performance_improvement"] == 20

    def test_architecture_analyst(self):
        """Test architecture_analyst template."""
        template = get_template("architecture_analyst")

        assert template is not None
        assert template.id == "architecture_analyst"
        assert template.role == "Architecture Analyst"
        assert template.tier_preference == "PREMIUM"
        assert "analyze_architecture" in template.capabilities
        assert "identify_patterns" in template.capabilities
        assert "suggest_improvements" in template.capabilities
        assert "dependency_analyzer" in template.tools
        assert template.quality_gates["max_circular_dependencies"] == 0

    def test_refactoring_specialist(self):
        """Test refactoring_specialist template."""
        template = get_template("refactoring_specialist")

        assert template is not None
        assert template.id == "refactoring_specialist"
        assert template.role == "Refactoring Specialist"
        assert template.tier_preference == "CAPABLE"
        assert "identify_code_smells" in template.capabilities
        assert "suggest_refactorings" in template.capabilities
        assert "validate_changes" in template.capabilities
        assert "ast_parser" in template.tools
        assert template.quality_gates["max_duplication_percent"] == 5

    def test_all_templates_have_valid_structure(self):
        """Test that all pre-built templates have valid structure."""
        templates = get_all_templates()

        for template in templates:
            # Verify all required fields
            assert template.id
            assert template.role
            assert len(template.capabilities) > 0
            assert template.tier_preference in {"CHEAP", "CAPABLE", "PREMIUM"}
            assert isinstance(template.tools, list)
            assert template.default_instructions
            assert isinstance(template.quality_gates, dict)
            assert isinstance(template.resource_requirements, ResourceRequirements)

            # Verify resource requirements are sensible
            assert template.resource_requirements.min_tokens > 0
            assert template.resource_requirements.max_tokens > 0
            assert (
                template.resource_requirements.max_tokens
                >= template.resource_requirements.min_tokens
            )
            assert template.resource_requirements.timeout_seconds > 0
            assert template.resource_requirements.memory_mb > 0

    def test_template_ids_are_unique(self):
        """Test that all template IDs are unique."""
        templates = get_all_templates()
        template_ids = [t.id for t in templates]

        assert len(template_ids) == len(set(template_ids))
