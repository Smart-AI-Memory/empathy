"""
Tests for empathy_llm_toolkit/agent_factory/crews/refactoring.py

Tests the RefactoringCrew and its supporting dataclasses and enums.
"""

from unittest.mock import patch

from empathy_llm_toolkit.agent_factory.crews.refactoring import (
    XML_PROMPT_TEMPLATES,
    CodeCheckpoint,
    Impact,
    RefactoringCategory,
    RefactoringConfig,
    RefactoringCrew,
    RefactoringFinding,
    RefactoringReport,
    Severity,
    UserProfile,
)


class TestRefactoringCategoryEnum:
    """Tests for RefactoringCategory enum."""

    def test_extract_method_value(self):
        """Test EXTRACT_METHOD value."""
        assert RefactoringCategory.EXTRACT_METHOD.value == "extract_method"

    def test_extract_variable_value(self):
        """Test EXTRACT_VARIABLE value."""
        assert RefactoringCategory.EXTRACT_VARIABLE.value == "extract_variable"

    def test_rename_value(self):
        """Test RENAME value."""
        assert RefactoringCategory.RENAME.value == "rename"

    def test_simplify_value(self):
        """Test SIMPLIFY value."""
        assert RefactoringCategory.SIMPLIFY.value == "simplify"

    def test_remove_duplication_value(self):
        """Test REMOVE_DUPLICATION value."""
        assert RefactoringCategory.REMOVE_DUPLICATION.value == "remove_duplication"

    def test_restructure_value(self):
        """Test RESTRUCTURE value."""
        assert RefactoringCategory.RESTRUCTURE.value == "restructure"

    def test_dead_code_value(self):
        """Test DEAD_CODE value."""
        assert RefactoringCategory.DEAD_CODE.value == "dead_code"

    def test_type_safety_value(self):
        """Test TYPE_SAFETY value."""
        assert RefactoringCategory.TYPE_SAFETY.value == "type_safety"

    def test_inline_value(self):
        """Test INLINE value."""
        assert RefactoringCategory.INLINE.value == "inline"

    def test_consolidate_conditional_value(self):
        """Test CONSOLIDATE_CONDITIONAL value."""
        assert RefactoringCategory.CONSOLIDATE_CONDITIONAL.value == "consolidate_conditional"

    def test_other_value(self):
        """Test OTHER value."""
        assert RefactoringCategory.OTHER.value == "other"

    def test_all_categories_count(self):
        """Test total number of categories."""
        assert len(RefactoringCategory) == 11

    def test_category_from_string(self):
        """Test creating category from string."""
        assert RefactoringCategory("extract_method") == RefactoringCategory.EXTRACT_METHOD
        assert RefactoringCategory("rename") == RefactoringCategory.RENAME


class TestSeverityEnum:
    """Tests for Severity enum."""

    def test_critical_value(self):
        """Test CRITICAL value."""
        assert Severity.CRITICAL.value == "critical"

    def test_high_value(self):
        """Test HIGH value."""
        assert Severity.HIGH.value == "high"

    def test_medium_value(self):
        """Test MEDIUM value."""
        assert Severity.MEDIUM.value == "medium"

    def test_low_value(self):
        """Test LOW value."""
        assert Severity.LOW.value == "low"

    def test_info_value(self):
        """Test INFO value."""
        assert Severity.INFO.value == "info"

    def test_all_severities_count(self):
        """Test total number of severities."""
        assert len(Severity) == 5


class TestImpactEnum:
    """Tests for Impact enum."""

    def test_high_value(self):
        """Test HIGH value."""
        assert Impact.HIGH.value == "high"

    def test_medium_value(self):
        """Test MEDIUM value."""
        assert Impact.MEDIUM.value == "medium"

    def test_low_value(self):
        """Test LOW value."""
        assert Impact.LOW.value == "low"

    def test_all_impacts_count(self):
        """Test total number of impact levels."""
        assert len(Impact) == 3


class TestRefactoringFinding:
    """Tests for RefactoringFinding dataclass."""

    def test_basic_creation(self):
        """Test basic finding creation."""
        finding = RefactoringFinding(
            id="ref_001",
            title="Extract Method",
            description="Long method should be broken down",
            category=RefactoringCategory.EXTRACT_METHOD,
            severity=Severity.MEDIUM,
            file_path="src/api.py",
            start_line=10,
            end_line=50,
        )
        assert finding.id == "ref_001"
        assert finding.title == "Extract Method"
        assert finding.category == RefactoringCategory.EXTRACT_METHOD
        assert finding.severity == Severity.MEDIUM
        assert finding.start_line == 10
        assert finding.end_line == 50

    def test_default_values(self):
        """Test default values."""
        finding = RefactoringFinding(
            id="ref_002",
            title="Test",
            description="Test desc",
            category=RefactoringCategory.OTHER,
            severity=Severity.LOW,
            file_path="test.py",
            start_line=1,
            end_line=5,
        )
        assert finding.before_code == ""
        assert finding.after_code is None
        assert finding.confidence == 1.0
        assert finding.estimated_impact == Impact.MEDIUM
        assert finding.rationale == ""
        assert finding.metadata == {}

    def test_full_finding_creation(self):
        """Test finding with all fields populated."""
        finding = RefactoringFinding(
            id="ref_003",
            title="Rename Variable",
            description="Variable name is unclear",
            category=RefactoringCategory.RENAME,
            severity=Severity.LOW,
            file_path="src/utils.py",
            start_line=25,
            end_line=25,
            before_code="x = calculate_value()",
            after_code="total_amount = calculate_value()",
            confidence=0.95,
            estimated_impact=Impact.LOW,
            rationale="More descriptive name improves readability",
            metadata={"old_name": "x", "new_name": "total_amount"},
        )
        assert finding.before_code == "x = calculate_value()"
        assert finding.after_code == "total_amount = calculate_value()"
        assert finding.confidence == 0.95
        assert finding.metadata["old_name"] == "x"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        finding = RefactoringFinding(
            id="ref_004",
            title="Dead Code",
            description="Unused function",
            category=RefactoringCategory.DEAD_CODE,
            severity=Severity.INFO,
            file_path="src/legacy.py",
            start_line=100,
            end_line=120,
        )
        data = finding.to_dict()
        assert data["id"] == "ref_004"
        assert data["title"] == "Dead Code"
        assert data["category"] == "dead_code"
        assert data["severity"] == "info"
        assert data["file_path"] == "src/legacy.py"
        assert data["start_line"] == 100
        assert data["end_line"] == 120

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "ref_005",
            "title": "Simplify Logic",
            "description": "Complex conditional can be simplified",
            "category": "simplify",
            "severity": "medium",
            "file_path": "src/core.py",
            "start_line": 50,
            "end_line": 65,
            "confidence": 0.85,
            "estimated_impact": "high",
        }
        finding = RefactoringFinding.from_dict(data)
        assert finding.id == "ref_005"
        assert finding.category == RefactoringCategory.SIMPLIFY
        assert finding.severity == Severity.MEDIUM
        assert finding.confidence == 0.85
        assert finding.estimated_impact == Impact.HIGH

    def test_from_dict_defaults(self):
        """Test from_dict with minimal data uses defaults."""
        data = {}
        finding = RefactoringFinding.from_dict(data)
        assert finding.title == "Untitled"
        assert finding.category == RefactoringCategory.OTHER
        assert finding.severity == Severity.MEDIUM


class TestCodeCheckpoint:
    """Tests for CodeCheckpoint dataclass."""

    def test_basic_creation(self):
        """Test basic checkpoint creation."""
        checkpoint = CodeCheckpoint(
            id="ckpt_001",
            file_path="src/api.py",
            original_content="def old_function(): pass",
            timestamp="2025-01-15T10:30:00Z",
            finding_id="ref_001",
        )
        assert checkpoint.id == "ckpt_001"
        assert checkpoint.file_path == "src/api.py"
        assert checkpoint.original_content == "def old_function(): pass"
        assert checkpoint.finding_id == "ref_001"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        checkpoint = CodeCheckpoint(
            id="ckpt_002",
            file_path="src/utils.py",
            original_content="x = 1",
            timestamp="2025-01-15T11:00:00Z",
            finding_id="ref_002",
        )
        data = checkpoint.to_dict()
        assert data["id"] == "ckpt_002"
        assert data["file_path"] == "src/utils.py"
        assert data["original_content"] == "x = 1"
        assert data["timestamp"] == "2025-01-15T11:00:00Z"
        assert data["finding_id"] == "ref_002"

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "ckpt_003",
            "file_path": "src/core.py",
            "original_content": "def func(): pass",
            "timestamp": "2025-01-15T12:00:00Z",
            "finding_id": "ref_003",
        }
        checkpoint = CodeCheckpoint.from_dict(data)
        assert checkpoint.id == "ckpt_003"
        assert checkpoint.file_path == "src/core.py"
        assert checkpoint.original_content == "def func(): pass"


class TestRefactoringReport:
    """Tests for RefactoringReport dataclass."""

    def test_basic_creation(self):
        """Test basic report creation."""
        report = RefactoringReport(
            target="src/api.py",
            findings=[],
        )
        assert report.target == "src/api.py"
        assert report.findings == []

    def test_default_values(self):
        """Test default values."""
        report = RefactoringReport(target="test.py", findings=[])
        assert report.summary == ""
        assert report.duration_seconds == 0.0
        assert report.agents_used == []
        assert report.checkpoints == []
        assert report.memory_graph_hits == 0
        assert report.metadata == {}

    def test_high_impact_findings_property(self):
        """Test high_impact_findings property filters correctly."""
        findings = [
            RefactoringFinding(
                id="1",
                title="High",
                description="Desc",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.HIGH,
                file_path="a.py",
                start_line=1,
                end_line=10,
                estimated_impact=Impact.HIGH,
            ),
            RefactoringFinding(
                id="2",
                title="Medium",
                description="Desc",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="b.py",
                start_line=1,
                end_line=5,
                estimated_impact=Impact.MEDIUM,
            ),
            RefactoringFinding(
                id="3",
                title="High2",
                description="Desc",
                category=RefactoringCategory.SIMPLIFY,
                severity=Severity.MEDIUM,
                file_path="c.py",
                start_line=1,
                end_line=20,
                estimated_impact=Impact.HIGH,
            ),
        ]
        report = RefactoringReport(target="test", findings=findings)
        high_impact = report.high_impact_findings
        assert len(high_impact) == 2
        assert all(f.estimated_impact == Impact.HIGH for f in high_impact)

    def test_findings_by_category_property(self):
        """Test findings_by_category groups correctly."""
        findings = [
            RefactoringFinding(
                id="1",
                title="Extract1",
                description="Desc",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="a.py",
                start_line=1,
                end_line=10,
            ),
            RefactoringFinding(
                id="2",
                title="Extract2",
                description="Desc",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.LOW,
                file_path="b.py",
                start_line=1,
                end_line=5,
            ),
            RefactoringFinding(
                id="3",
                title="Rename1",
                description="Desc",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="c.py",
                start_line=1,
                end_line=1,
            ),
        ]
        report = RefactoringReport(target="test", findings=findings)
        by_cat = report.findings_by_category
        assert len(by_cat["extract_method"]) == 2
        assert len(by_cat["rename"]) == 1

    def test_total_lines_affected_property(self):
        """Test total_lines_affected calculation."""
        findings = [
            RefactoringFinding(
                id="1",
                title="F1",
                description="Desc",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="a.py",
                start_line=10,
                end_line=20,  # 11 lines
            ),
            RefactoringFinding(
                id="2",
                title="F2",
                description="Desc",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="b.py",
                start_line=5,
                end_line=5,  # 1 line
            ),
        ]
        report = RefactoringReport(target="test", findings=findings)
        assert report.total_lines_affected == 12  # 11 + 1

    def test_to_dict(self):
        """Test serialization to dictionary."""
        findings = [
            RefactoringFinding(
                id="1",
                title="Test",
                description="Desc",
                category=RefactoringCategory.OTHER,
                severity=Severity.INFO,
                file_path="test.py",
                start_line=1,
                end_line=5,
            ),
        ]
        report = RefactoringReport(
            target="src/api.py",
            findings=findings,
            summary="Found 1 opportunity",
            duration_seconds=5.5,
            agents_used=["analyzer", "writer"],
        )
        data = report.to_dict()
        assert data["target"] == "src/api.py"
        assert len(data["findings"]) == 1
        assert data["summary"] == "Found 1 opportunity"
        assert data["duration_seconds"] == 5.5
        assert "analyzer" in data["agents_used"]


class TestUserProfile:
    """Tests for UserProfile dataclass."""

    def test_default_values(self):
        """Test default values."""
        profile = UserProfile()
        assert profile.user_id == "default"
        assert profile.updated_at == ""
        assert profile.accepted_categories == {}
        assert profile.rejected_categories == {}
        assert profile.preferred_complexity == "medium"
        assert profile.history == []

    def test_custom_values(self):
        """Test creating profile with custom values."""
        profile = UserProfile(
            user_id="user123",
            updated_at="2025-01-15T10:00:00Z",
            accepted_categories={"extract_method": 5, "rename": 3},
            rejected_categories={"dead_code": 2},
            preferred_complexity="high",
            history=[{"session_id": "abc", "category": "rename", "accepted": True}],
        )
        assert profile.user_id == "user123"
        assert profile.accepted_categories["extract_method"] == 5
        assert profile.rejected_categories["dead_code"] == 2

    def test_get_category_score_neutral(self):
        """Test category score is neutral for unknown categories."""
        profile = UserProfile()
        score = profile.get_category_score(RefactoringCategory.RENAME)
        assert score == 0.5  # Neutral

    def test_get_category_score_all_accepted(self):
        """Test category score when all were accepted."""
        profile = UserProfile(
            accepted_categories={"rename": 10},
            rejected_categories={},
        )
        score = profile.get_category_score(RefactoringCategory.RENAME)
        assert score == 1.0  # All accepted

    def test_get_category_score_mixed(self):
        """Test category score with mixed acceptance."""
        profile = UserProfile(
            accepted_categories={"rename": 3},
            rejected_categories={"rename": 1},
        )
        score = profile.get_category_score(RefactoringCategory.RENAME)
        assert score == 0.75  # 3 / (3 + 1)

    def test_to_dict(self):
        """Test serialization to dictionary."""
        profile = UserProfile(
            user_id="user456",
            accepted_categories={"simplify": 5},
        )
        data = profile.to_dict()
        assert data["user_id"] == "user456"
        assert "preferences" in data
        assert data["preferences"]["accepted_categories"]["simplify"] == 5

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "user_id": "user789",
            "updated_at": "2025-01-15",
            "preferences": {
                "accepted_categories": {"rename": 2},
                "rejected_categories": {},
                "preferred_complexity": "low",
            },
            "history": [],
        }
        profile = UserProfile.from_dict(data)
        assert profile.user_id == "user789"
        assert profile.accepted_categories["rename"] == 2
        assert profile.preferred_complexity == "low"


class TestRefactoringConfig:
    """Tests for RefactoringConfig dataclass."""

    def test_default_values(self):
        """Test default values."""
        config = RefactoringConfig()
        assert config.provider == "anthropic"
        assert config.api_key is None
        assert config.depth == "standard"
        assert "extract_method" in config.focus_areas
        assert config.memory_graph_enabled is True
        assert config.user_profile_enabled is True
        assert config.resilience_enabled is True
        assert config.timeout_seconds == 300.0
        assert config.xml_prompts_enabled is True

    def test_custom_values(self):
        """Test creating config with custom values."""
        config = RefactoringConfig(
            provider="openai",
            api_key="sk-test",
            depth="thorough",
            focus_areas=["rename", "simplify"],
            memory_graph_enabled=False,
            timeout_seconds=600.0,
        )
        assert config.provider == "openai"
        assert config.api_key == "sk-test"
        assert config.depth == "thorough"
        assert config.focus_areas == ["rename", "simplify"]
        assert config.memory_graph_enabled is False
        assert config.timeout_seconds == 600.0

    def test_agent_tiers(self):
        """Test agent tier configuration."""
        config = RefactoringConfig(
            analyzer_tier="premium",
            writer_tier="capable",
        )
        assert config.analyzer_tier == "premium"
        assert config.writer_tier == "capable"


class TestXMLPromptTemplates:
    """Tests for XML_PROMPT_TEMPLATES."""

    def test_analyzer_template_exists(self):
        """Test analyzer template exists."""
        assert "refactor_analyzer" in XML_PROMPT_TEMPLATES

    def test_writer_template_exists(self):
        """Test writer template exists."""
        assert "refactor_writer" in XML_PROMPT_TEMPLATES

    def test_analyzer_template_structure(self):
        """Test analyzer template has expected structure."""
        template = XML_PROMPT_TEMPLATES["refactor_analyzer"]
        assert '<agent role="refactor_analyzer"' in template
        assert "<identity>" in template
        assert "<goal>" in template
        assert "<instructions>" in template
        assert "<constraints>" in template
        assert "<output_format>" in template

    def test_writer_template_structure(self):
        """Test writer template has expected structure."""
        template = XML_PROMPT_TEMPLATES["refactor_writer"]
        assert '<agent role="refactor_writer"' in template
        assert "<identity>" in template
        assert "<goal>" in template
        assert "<instructions>" in template
        assert "<constraints>" in template

    def test_templates_have_schema_version_placeholder(self):
        """Test templates have schema version placeholder."""
        for template in XML_PROMPT_TEMPLATES.values():
            assert "{schema_version}" in template


class TestRefactoringCrewInit:
    """Tests for RefactoringCrew initialization."""

    def test_init_default(self):
        """Test initialization with defaults."""
        crew = RefactoringCrew()
        assert crew.config is not None
        assert crew.config.provider == "anthropic"
        assert crew._initialized is False

    def test_init_with_config(self):
        """Test initialization with config object."""
        config = RefactoringConfig(provider="openai", depth="thorough")
        crew = RefactoringCrew(config=config)
        assert crew.config.provider == "openai"
        assert crew.config.depth == "thorough"

    def test_init_with_kwargs(self):
        """Test initialization with keyword arguments."""
        crew = RefactoringCrew(provider="openai", api_key="sk-test")
        assert crew.config.provider == "openai"
        assert crew.config.api_key == "sk-test"

    def test_init_internal_state(self):
        """Test initialization sets internal state correctly."""
        crew = RefactoringCrew()
        assert crew._factory is None
        assert crew._agents == {}
        assert crew._workflow is None
        assert crew._graph is None
        assert crew._user_profile is None


class TestRefactoringCrewProperties:
    """Tests for RefactoringCrew properties."""

    def test_agents_property(self):
        """Test agents property returns dictionary."""
        crew = RefactoringCrew()
        assert isinstance(crew.agents, dict)

    def test_is_initialized_property(self):
        """Test is_initialized property."""
        crew = RefactoringCrew()
        assert crew.is_initialized is False

    def test_user_profile_property(self):
        """Test user_profile property returns None before init."""
        crew = RefactoringCrew()
        assert crew.user_profile is None


class TestRefactoringCrewXMLPrompts:
    """Tests for XML prompt rendering."""

    def test_render_xml_prompt(self):
        """Test _render_xml_prompt method."""
        crew = RefactoringCrew()
        prompt = crew._render_xml_prompt("refactor_analyzer")
        assert 'version="1.0"' in prompt
        assert "{schema_version}" not in prompt

    def test_render_xml_prompt_custom_version(self):
        """Test _render_xml_prompt with custom schema version."""
        config = RefactoringConfig(xml_schema_version="2.0")
        crew = RefactoringCrew(config=config)
        prompt = crew._render_xml_prompt("refactor_analyzer")
        assert 'version="2.0"' in prompt

    def test_get_system_prompt_xml_enabled(self):
        """Test _get_system_prompt when XML is enabled."""
        crew = RefactoringCrew()
        prompt = crew._get_system_prompt("refactor_analyzer", "fallback")
        assert "<agent" in prompt  # XML template

    def test_get_system_prompt_xml_disabled(self):
        """Test _get_system_prompt when XML is disabled."""
        config = RefactoringConfig(xml_prompts_enabled=False)
        crew = RefactoringCrew(config=config)
        prompt = crew._get_system_prompt("refactor_analyzer", "fallback")
        assert prompt == "fallback"


class TestRefactoringCrewCheckpoint:
    """Tests for checkpoint/rollback functionality."""

    def test_create_checkpoint(self):
        """Test creating a checkpoint."""
        crew = RefactoringCrew()
        checkpoint = crew.create_checkpoint(
            file_path="src/api.py",
            content="def old(): pass",
            finding_id="ref_001",
        )
        assert checkpoint.file_path == "src/api.py"
        assert checkpoint.original_content == "def old(): pass"
        assert checkpoint.finding_id == "ref_001"
        assert checkpoint.id is not None
        assert checkpoint.timestamp is not None

    def test_rollback(self):
        """Test rollback returns original content."""
        crew = RefactoringCrew()
        checkpoint = crew.create_checkpoint(
            file_path="src/api.py",
            content="original content",
            finding_id="ref_001",
        )
        content = crew.rollback(checkpoint)
        assert content == "original content"


class TestRefactoringCrewRecordDecision:
    """Tests for recording user decisions."""

    def test_record_decision_accepted(self):
        """Test recording an accepted decision."""
        crew = RefactoringCrew()
        crew._user_profile = UserProfile()

        finding = RefactoringFinding(
            id="1",
            title="Rename",
            description="Desc",
            category=RefactoringCategory.RENAME,
            severity=Severity.LOW,
            file_path="test.py",
            start_line=1,
            end_line=1,
        )

        with patch.object(crew, "save_user_profile"):
            crew.record_decision(finding, accepted=True)

        assert crew._user_profile.accepted_categories["rename"] == 1
        assert len(crew._user_profile.history) == 1
        assert crew._user_profile.history[0]["accepted"] is True

    def test_record_decision_rejected(self):
        """Test recording a rejected decision."""
        crew = RefactoringCrew()
        crew._user_profile = UserProfile()

        finding = RefactoringFinding(
            id="1",
            title="Simplify",
            description="Desc",
            category=RefactoringCategory.SIMPLIFY,
            severity=Severity.MEDIUM,
            file_path="test.py",
            start_line=1,
            end_line=10,
        )

        with patch.object(crew, "save_user_profile"):
            crew.record_decision(finding, accepted=False)

        assert crew._user_profile.rejected_categories["simplify"] == 1
        assert len(crew._user_profile.history) == 1
        assert crew._user_profile.history[0]["accepted"] is False

    def test_record_decision_no_profile(self):
        """Test recording decision when no profile exists."""
        crew = RefactoringCrew()
        crew._user_profile = None

        finding = RefactoringFinding(
            id="1",
            title="Test",
            description="Desc",
            category=RefactoringCategory.OTHER,
            severity=Severity.INFO,
            file_path="test.py",
            start_line=1,
            end_line=1,
        )

        # Should not raise an error
        crew.record_decision(finding, accepted=True)


class TestRefactoringCrewSummaryGeneration:
    """Tests for summary generation."""

    def test_generate_summary_no_findings(self):
        """Test summary generation with no findings."""
        crew = RefactoringCrew()
        summary = crew._generate_summary([])
        assert "No refactoring opportunities" in summary

    def test_generate_summary_with_findings(self):
        """Test summary generation with findings."""
        crew = RefactoringCrew()
        findings = [
            RefactoringFinding(
                id="1",
                title="High",
                description="Desc",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.HIGH,
                file_path="a.py",
                start_line=1,
                end_line=20,
                estimated_impact=Impact.HIGH,
            ),
            RefactoringFinding(
                id="2",
                title="Medium",
                description="Desc",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="b.py",
                start_line=1,
                end_line=1,
                estimated_impact=Impact.MEDIUM,
            ),
        ]
        summary = crew._generate_summary(findings)
        assert "2 refactoring opportunities" in summary
        assert "high impact" in summary.lower()


class TestRefactoringCrewParseFindings:
    """Tests for parsing findings from agent results."""

    def test_parse_findings_from_metadata(self):
        """Test parsing findings from metadata."""
        crew = RefactoringCrew()
        result = {
            "output": "",
            "metadata": {
                "findings": [
                    {
                        "id": "1",
                        "title": "Test Finding",
                        "description": "Description",
                        "category": "rename",
                        "severity": "low",
                        "file_path": "test.py",
                        "start_line": 1,
                        "end_line": 5,
                    }
                ]
            },
        }
        findings = crew._parse_findings(result)
        assert len(findings) == 1
        assert findings[0].title == "Test Finding"

    def test_parse_findings_from_json_output(self):
        """Test parsing findings from JSON in output."""
        crew = RefactoringCrew()
        result = {
            "output": """Here are the findings:
[
    {
        "id": "1",
        "title": "Extract Method",
        "description": "Long method",
        "category": "extract_method",
        "severity": "medium",
        "file_path": "api.py",
        "start_line": 10,
        "end_line": 50
    }
]
""",
            "metadata": {},
        }
        findings = crew._parse_findings(result)
        assert len(findings) == 1
        assert findings[0].category == RefactoringCategory.EXTRACT_METHOD

    def test_parse_findings_fallback(self):
        """Test parsing findings with fallback for text output."""
        crew = RefactoringCrew()
        result = {
            "output": "Found some issues with the code structure.",
            "metadata": {},
        }
        findings = crew._parse_findings(result)
        assert len(findings) == 1
        assert findings[0].category == RefactoringCategory.OTHER


class TestRefactoringCrewParseRefactorResult:
    """Tests for parsing refactor results."""

    def test_parse_refactor_result_from_metadata(self):
        """Test parsing refactor result from metadata."""
        crew = RefactoringCrew()
        result = {
            "output": "",
            "metadata": {"after_code": "def new_function(): pass"},
        }
        after_code = crew._parse_refactor_result(result)
        assert after_code == "def new_function(): pass"

    def test_parse_refactor_result_from_json(self):
        """Test parsing refactor result from JSON output."""
        crew = RefactoringCrew()
        result = {
            "output": '{"after_code": "def refactored(): pass", "explanation": "Simplified"}',
            "metadata": {},
        }
        after_code = crew._parse_refactor_result(result)
        assert after_code == "def refactored(): pass"

    def test_parse_refactor_result_from_code_block(self):
        """Test parsing refactor result from code block."""
        crew = RefactoringCrew()
        result = {
            "output": """Here's the refactored code:

```python
def better_function():
    return True
```
""",
            "metadata": {},
        }
        after_code = crew._parse_refactor_result(result)
        assert "def better_function" in after_code


class TestRefactoringCrewUserPreferences:
    """Tests for applying user preferences."""

    def test_apply_user_preferences_sorting(self):
        """Test findings are sorted by user preferences."""
        crew = RefactoringCrew()
        crew._user_profile = UserProfile(
            accepted_categories={"rename": 10, "extract_method": 1},
            rejected_categories={"simplify": 5},
        )

        findings = [
            RefactoringFinding(
                id="1",
                title="Simplify",
                description="Desc",
                category=RefactoringCategory.SIMPLIFY,
                severity=Severity.MEDIUM,
                file_path="a.py",
                start_line=1,
                end_line=10,
                estimated_impact=Impact.MEDIUM,
                confidence=1.0,
            ),
            RefactoringFinding(
                id="2",
                title="Rename",
                description="Desc",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="b.py",
                start_line=1,
                end_line=1,
                estimated_impact=Impact.MEDIUM,
                confidence=1.0,
            ),
        ]

        sorted_findings = crew._apply_user_preferences(findings)
        # Rename should be first (higher acceptance rate)
        assert sorted_findings[0].category == RefactoringCategory.RENAME
