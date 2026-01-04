"""Tests for Refactoring Crew

Tests the 2-agent refactoring crew that performs interactive code
refactoring with session memory, rollback, and user preference learning.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path

import pytest


class TestRefactoringFinding:
    """Test RefactoringFinding data structure."""

    def test_finding_creation(self):
        """Test creating a refactoring finding."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        finding = RefactoringFinding(
            id="test-001",
            title="Extract complex validation logic",
            description="The validation logic in process_order is too complex",
            category=RefactoringCategory.EXTRACT_METHOD,
            severity=Severity.MEDIUM,
            file_path="src/orders/processor.py",
            start_line=42,
            end_line=85,
            before_code="def process_order(order):\n    # 40 lines of validation...",
            confidence=0.9,
            estimated_impact=Impact.HIGH,
            rationale="Improves testability and reduces cognitive load",
        )

        assert finding.id == "test-001"
        assert finding.title == "Extract complex validation logic"
        assert finding.category == RefactoringCategory.EXTRACT_METHOD
        assert finding.severity == Severity.MEDIUM
        assert finding.estimated_impact == Impact.HIGH
        assert finding.confidence == 0.9

    def test_finding_to_dict(self):
        """Test converting finding to dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        finding = RefactoringFinding(
            id="test-002",
            title="Rename unclear variable",
            description="Variable 'x' should be renamed to 'user_count'",
            category=RefactoringCategory.RENAME,
            severity=Severity.LOW,
            file_path="src/analytics.py",
            start_line=10,
            end_line=10,
            before_code="x = len(users)",
            after_code="user_count = len(users)",
            confidence=0.95,
            estimated_impact=Impact.LOW,
        )

        data = finding.to_dict()

        assert data["id"] == "test-002"
        assert data["title"] == "Rename unclear variable"
        assert data["category"] == "rename"
        assert data["severity"] == "low"
        assert data["estimated_impact"] == "low"
        assert data["before_code"] == "x = len(users)"
        assert data["after_code"] == "user_count = len(users)"

    def test_finding_from_dict(self):
        """Test creating finding from dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        data = {
            "id": "test-003",
            "title": "Remove dead code",
            "description": "Unused function detected",
            "category": "dead_code",
            "severity": "info",
            "file_path": "src/utils.py",
            "start_line": 100,
            "end_line": 120,
            "before_code": "def unused_function(): pass",
            "confidence": 1.0,
            "estimated_impact": "low",
        }

        finding = RefactoringFinding.from_dict(data)

        assert finding.id == "test-003"
        assert finding.category == RefactoringCategory.DEAD_CODE
        assert finding.severity == Severity.INFO
        assert finding.estimated_impact == Impact.LOW

    def test_finding_defaults(self):
        """Test finding default values."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        finding = RefactoringFinding(
            id="test-004",
            title="Test",
            description="Test finding",
            category=RefactoringCategory.OTHER,
            severity=Severity.INFO,
            file_path="test.py",
            start_line=1,
            end_line=1,
        )

        assert finding.before_code == ""
        assert finding.after_code is None
        assert finding.confidence == 1.0
        assert finding.estimated_impact == Impact.MEDIUM
        assert finding.rationale == ""
        assert finding.metadata == {}


class TestCodeCheckpoint:
    """Test CodeCheckpoint data structure."""

    def test_checkpoint_creation(self):
        """Test creating a checkpoint."""
        from empathy_llm_toolkit.agent_factory.crews import CodeCheckpoint

        checkpoint = CodeCheckpoint(
            id="cp-001",
            file_path="src/api.py",
            original_content="def old_function(): pass",
            timestamp="2025-12-27T10:00:00",
            finding_id="finding-001",
        )

        assert checkpoint.id == "cp-001"
        assert checkpoint.file_path == "src/api.py"
        assert checkpoint.original_content == "def old_function(): pass"
        assert checkpoint.finding_id == "finding-001"

    def test_checkpoint_to_dict(self):
        """Test converting checkpoint to dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import CodeCheckpoint

        checkpoint = CodeCheckpoint(
            id="cp-002",
            file_path="src/utils.py",
            original_content="x = 1",
            timestamp="2025-12-27T10:00:00",
            finding_id="finding-002",
        )

        data = checkpoint.to_dict()

        assert data["id"] == "cp-002"
        assert data["file_path"] == "src/utils.py"
        assert data["original_content"] == "x = 1"

    def test_checkpoint_from_dict(self):
        """Test creating checkpoint from dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import CodeCheckpoint

        data = {
            "id": "cp-003",
            "file_path": "src/models.py",
            "original_content": "class User: pass",
            "timestamp": "2025-12-27T11:00:00",
            "finding_id": "finding-003",
        }

        checkpoint = CodeCheckpoint.from_dict(data)

        assert checkpoint.id == "cp-003"
        assert checkpoint.file_path == "src/models.py"


class TestRefactoringReport:
    """Test RefactoringReport data structure."""

    def test_report_creation(self):
        """Test creating a refactoring report."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding, RefactoringReport
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        findings = [
            RefactoringFinding(
                id="f1",
                title="High impact extraction",
                description="...",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="src/api.py",
                start_line=10,
                end_line=50,
                estimated_impact=Impact.HIGH,
            ),
            RefactoringFinding(
                id="f2",
                title="Low impact rename",
                description="...",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="src/api.py",
                start_line=5,
                end_line=5,
                estimated_impact=Impact.LOW,
            ),
        ]

        report = RefactoringReport(
            target="src/api.py",
            findings=findings,
            summary="Found 2 refactoring opportunities",
            duration_seconds=5.5,
            agents_used=["analyzer", "writer"],
        )

        assert report.target == "src/api.py"
        assert len(report.findings) == 2
        assert len(report.high_impact_findings) == 1
        assert report.duration_seconds == 5.5

    def test_report_findings_by_category(self):
        """Test grouping findings by category."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding, RefactoringReport
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            RefactoringCategory,
            Severity,
        )

        findings = [
            RefactoringFinding(
                id="f1",
                title="Extract 1",
                description="...",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=1,
                end_line=10,
            ),
            RefactoringFinding(
                id="f2",
                title="Extract 2",
                description="...",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=20,
                end_line=30,
            ),
            RefactoringFinding(
                id="f3",
                title="Rename",
                description="...",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="test.py",
                start_line=5,
                end_line=5,
            ),
        ]

        report = RefactoringReport(target="test.py", findings=findings)
        by_cat = report.findings_by_category

        assert len(by_cat["extract_method"]) == 2
        assert len(by_cat["rename"]) == 1

    def test_report_total_lines_affected(self):
        """Test calculating total lines affected."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding, RefactoringReport
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            RefactoringCategory,
            Severity,
        )

        findings = [
            RefactoringFinding(
                id="f1",
                title="Test 1",
                description="...",
                category=RefactoringCategory.SIMPLIFY,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=10,
                end_line=20,  # 11 lines
            ),
            RefactoringFinding(
                id="f2",
                title="Test 2",
                description="...",
                category=RefactoringCategory.SIMPLIFY,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=30,
                end_line=35,  # 6 lines
            ),
        ]

        report = RefactoringReport(target="test.py", findings=findings)

        assert report.total_lines_affected == 17  # 11 + 6

    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding, RefactoringReport
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        findings = [
            RefactoringFinding(
                id="f1",
                title="Test",
                description="...",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=1,
                end_line=10,
                estimated_impact=Impact.HIGH,
            ),
        ]

        report = RefactoringReport(
            target="test.py",
            findings=findings,
            summary="Found 1 issue",
            duration_seconds=3.0,
            agents_used=["analyzer"],
        )

        data = report.to_dict()

        assert data["target"] == "test.py"
        assert data["high_impact_count"] == 1
        assert data["total_lines_affected"] == 10
        assert len(data["agents_used"]) == 1


class TestUserProfile:
    """Test UserProfile data structure."""

    def test_profile_creation(self):
        """Test creating a user profile."""
        from empathy_llm_toolkit.agent_factory.crews import UserProfile

        profile = UserProfile(user_id="test-user")

        assert profile.user_id == "test-user"
        assert profile.accepted_categories == {}
        assert profile.rejected_categories == {}
        assert profile.preferred_complexity == "medium"

    def test_profile_category_score(self):
        """Test calculating category preference score."""
        from empathy_llm_toolkit.agent_factory.crews import UserProfile
        from empathy_llm_toolkit.agent_factory.crews.refactoring import RefactoringCategory

        profile = UserProfile(
            accepted_categories={"extract_method": 8, "rename": 4},
            rejected_categories={"extract_method": 2, "rename": 6},
        )

        # 8 / (8+2) = 0.8
        extract_score = profile.get_category_score(RefactoringCategory.EXTRACT_METHOD)
        assert extract_score == 0.8

        # 4 / (4+6) = 0.4
        rename_score = profile.get_category_score(RefactoringCategory.RENAME)
        assert rename_score == 0.4

        # Unknown category = 0.5 (neutral)
        simplify_score = profile.get_category_score(RefactoringCategory.SIMPLIFY)
        assert simplify_score == 0.5

    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import UserProfile

        profile = UserProfile(
            user_id="test-user",
            accepted_categories={"extract_method": 5},
            rejected_categories={"rename": 2},
        )

        data = profile.to_dict()

        assert data["user_id"] == "test-user"
        assert data["preferences"]["accepted_categories"]["extract_method"] == 5
        assert data["preferences"]["rejected_categories"]["rename"] == 2

    def test_profile_from_dict(self):
        """Test creating profile from dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import UserProfile

        data = {
            "user_id": "loaded-user",
            "preferences": {
                "accepted_categories": {"simplify": 10},
                "rejected_categories": {},
                "preferred_complexity": "high",
            },
            "history": [],
        }

        profile = UserProfile.from_dict(data)

        assert profile.user_id == "loaded-user"
        assert profile.accepted_categories["simplify"] == 10
        assert profile.preferred_complexity == "high"


class TestRefactoringConfig:
    """Test RefactoringConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringConfig

        config = RefactoringConfig()

        assert config.provider == "anthropic"
        assert config.depth == "standard"
        assert config.memory_graph_enabled is True
        assert config.user_profile_enabled is True
        assert config.analyzer_tier == "capable"
        assert config.writer_tier == "capable"
        assert "extract_method" in config.focus_areas

    def test_custom_config(self):
        """Test custom configuration."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringConfig

        config = RefactoringConfig(
            provider="openai",
            depth="thorough",
            memory_graph_enabled=False,
            analyzer_tier="premium",
        )

        assert config.provider == "openai"
        assert config.depth == "thorough"
        assert config.memory_graph_enabled is False
        assert config.analyzer_tier == "premium"


class TestRefactoringCrew:
    """Test RefactoringCrew creation and initialization."""

    def test_crew_creation_with_config(self):
        """Test creating crew with config object."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringConfig, RefactoringCrew

        config = RefactoringConfig(
            api_key="test-key",
            depth="quick",
        )

        crew = RefactoringCrew(config=config)

        assert crew.config.api_key == "test-key"
        assert crew.config.depth == "quick"
        assert crew.is_initialized is False

    def test_crew_creation_with_kwargs(self):
        """Test creating crew with keyword arguments."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew

        crew = RefactoringCrew(
            api_key="test-key",
            provider="openai",
            memory_graph_enabled=False,
        )

        assert crew.config.api_key == "test-key"
        assert crew.config.provider == "openai"
        assert crew.config.memory_graph_enabled is False

    @pytest.mark.asyncio
    async def test_crew_initialization(self):
        """Test lazy initialization of crew agents."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew

        with tempfile.TemporaryDirectory() as tmpdir:
            crew = RefactoringCrew(
                memory_graph_enabled=False,
                user_profile_enabled=False,
                memory_graph_path=str(Path(tmpdir) / "test.json"),
            )

            # Not initialized yet
            assert crew.is_initialized is False
            assert len(crew.agents) == 0

            # Initialize
            await crew._initialize()

            # Now initialized with 2 agents
            assert crew.is_initialized is True
            assert len(crew.agents) == 2
            assert "analyzer" in crew.agents
            assert "writer" in crew.agents


class TestRefactoringCrewCheckpoints:
    """Test RefactoringCrew checkpoint and rollback functionality."""

    def test_create_checkpoint(self):
        """Test creating a checkpoint."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew

        crew = RefactoringCrew(memory_graph_enabled=False)

        checkpoint = crew.create_checkpoint(
            file_path="src/api.py",
            content="original content here",
            finding_id="finding-001",
        )

        assert checkpoint.file_path == "src/api.py"
        assert checkpoint.original_content == "original content here"
        assert checkpoint.finding_id == "finding-001"
        assert checkpoint.id  # Should have auto-generated ID
        assert checkpoint.timestamp  # Should have timestamp

    def test_rollback(self):
        """Test rollback returns original content."""
        from empathy_llm_toolkit.agent_factory.crews import CodeCheckpoint, RefactoringCrew

        crew = RefactoringCrew(memory_graph_enabled=False)

        checkpoint = CodeCheckpoint(
            id="cp-001",
            file_path="src/api.py",
            original_content="def original(): pass",
            timestamp="2025-12-27T10:00:00",
            finding_id="finding-001",
        )

        content = crew.rollback(checkpoint)

        assert content == "def original(): pass"


class TestRefactoringCrewUserProfile:
    """Test RefactoringCrew user profile management."""

    def test_load_missing_profile(self):
        """Test loading when profile doesn't exist."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew

        with tempfile.TemporaryDirectory() as tmpdir:
            crew = RefactoringCrew(
                memory_graph_enabled=False,
                user_profile_path=str(Path(tmpdir) / "nonexistent.json"),
            )

            profile = crew._load_user_profile()

            assert profile.user_id == "default"
            assert profile.accepted_categories == {}

    def test_save_and_load_profile(self):
        """Test saving and loading user profile."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew, UserProfile

        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = str(Path(tmpdir) / "profile.json")

            crew = RefactoringCrew(
                memory_graph_enabled=False,
                user_profile_path=profile_path,
            )

            # Create and save profile
            crew._user_profile = UserProfile(
                user_id="test-user",
                accepted_categories={"extract_method": 5},
            )
            crew.save_user_profile()

            # Verify file exists
            assert Path(profile_path).exists()

            # Load profile
            loaded = crew._load_user_profile()
            assert loaded.user_id == "test-user"
            assert loaded.accepted_categories["extract_method"] == 5

    def test_record_decision(self):
        """Test recording user decisions."""
        from empathy_llm_toolkit.agent_factory.crews import (
            RefactoringCrew,
            RefactoringFinding,
            UserProfile,
        )
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            RefactoringCategory,
            Severity,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            crew = RefactoringCrew(
                memory_graph_enabled=False,
                user_profile_path=str(Path(tmpdir) / "profile.json"),
            )
            crew._user_profile = UserProfile()

            finding = RefactoringFinding(
                id="f1",
                title="Test",
                description="...",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=1,
                end_line=10,
            )

            # Accept the finding
            crew.record_decision(finding, accepted=True)

            assert crew._user_profile.accepted_categories["extract_method"] == 1
            assert len(crew._user_profile.history) == 1
            assert crew._user_profile.history[0]["accepted"] is True

            # Reject another finding
            crew.record_decision(finding, accepted=False)

            assert crew._user_profile.rejected_categories["extract_method"] == 1
            assert len(crew._user_profile.history) == 2


class TestRefactoringCrewParsing:
    """Test RefactoringCrew parsing logic."""

    def test_generate_summary_no_findings(self):
        """Test summary generation with no findings."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew

        crew = RefactoringCrew(memory_graph_enabled=False)
        summary = crew._generate_summary([])

        assert "No refactoring opportunities" in summary

    def test_generate_summary_with_findings(self):
        """Test summary generation with findings."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew, RefactoringFinding
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        crew = RefactoringCrew(memory_graph_enabled=False)

        findings = [
            RefactoringFinding(
                id="f1",
                title="High impact",
                description="...",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=1,
                end_line=10,
                estimated_impact=Impact.HIGH,
            ),
            RefactoringFinding(
                id="f2",
                title="Medium impact 1",
                description="...",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="test.py",
                start_line=20,
                end_line=20,
                estimated_impact=Impact.MEDIUM,
            ),
            RefactoringFinding(
                id="f3",
                title="Medium impact 2",
                description="...",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="test.py",
                start_line=30,
                end_line=30,
                estimated_impact=Impact.MEDIUM,
            ),
        ]

        summary = crew._generate_summary(findings)

        assert "3 refactoring opportunities" in summary
        assert "1 high impact" in summary
        assert "2 medium impact" in summary

    def test_apply_user_preferences(self):
        """Test applying user preferences to prioritize findings."""
        from empathy_llm_toolkit.agent_factory.crews import (
            RefactoringCrew,
            RefactoringFinding,
            UserProfile,
        )
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            Impact,
            RefactoringCategory,
            Severity,
        )

        crew = RefactoringCrew(memory_graph_enabled=False)
        crew._user_profile = UserProfile(
            accepted_categories={"extract_method": 10},  # High preference
            rejected_categories={"rename": 10},  # Low preference
        )

        findings = [
            RefactoringFinding(
                id="f1",
                title="Rename (low pref)",
                description="...",
                category=RefactoringCategory.RENAME,
                severity=Severity.LOW,
                file_path="test.py",
                start_line=1,
                end_line=1,
                estimated_impact=Impact.HIGH,
                confidence=1.0,
            ),
            RefactoringFinding(
                id="f2",
                title="Extract (high pref)",
                description="...",
                category=RefactoringCategory.EXTRACT_METHOD,
                severity=Severity.MEDIUM,
                file_path="test.py",
                start_line=10,
                end_line=20,
                estimated_impact=Impact.MEDIUM,
                confidence=1.0,
            ),
        ]

        prioritized = crew._apply_user_preferences(findings)

        # Extract method should come first due to user preference
        assert prioritized[0].category == RefactoringCategory.EXTRACT_METHOD


class TestRefactoringCrewWorkflow:
    """Test RefactoringCrew workflow execution."""

    def test_build_analysis_task(self):
        """Test building analysis task description."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew

        crew = RefactoringCrew(depth="standard", memory_graph_enabled=False)

        task = crew._build_analysis_task(
            code="def test(): pass",
            file_path="src/test.py",
            context={},
        )

        assert "src/test.py" in task
        assert "standard" in task.lower()
        assert "def test(): pass" in task

    def test_build_refactor_task(self):
        """Test building refactor task description."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew, RefactoringFinding
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            RefactoringCategory,
            Severity,
        )

        crew = RefactoringCrew(memory_graph_enabled=False)

        finding = RefactoringFinding(
            id="f1",
            title="Extract validation",
            description="Extract validation logic",
            category=RefactoringCategory.EXTRACT_METHOD,
            severity=Severity.MEDIUM,
            file_path="test.py",
            start_line=10,
            end_line=30,
            before_code="def process():\n    # validation code",
            rationale="Improves testability",
        )

        task = crew._build_refactor_task(finding, "full file content here")

        assert "Extract validation" in task
        assert "extract_method" in task
        assert "Improves testability" in task
        assert "before_code" in task.lower() or "before" in task.lower()

    @pytest.mark.asyncio
    async def test_analyze_with_mocked_workflow(self):
        """Test analyze execution with mocked agents."""
        from unittest.mock import AsyncMock, MagicMock

        from empathy_llm_toolkit.agent_factory.crews import RefactoringConfig, RefactoringCrew

        config = RefactoringConfig(
            memory_graph_enabled=False,
            user_profile_enabled=False,
        )
        crew = RefactoringCrew(config=config)

        # Mock initialization
        crew._initialized = True
        crew._factory = MagicMock()

        # Mock analyzer agent
        mock_analyzer = MagicMock()
        mock_analyzer.invoke = AsyncMock(
            return_value={
                "output": "[]",
                "metadata": {
                    "findings": [
                        {
                            "id": "f1",
                            "title": "Extract method",
                            "description": "Complex logic",
                            "category": "extract_method",
                            "severity": "medium",
                            "file_path": "test.py",
                            "start_line": 10,
                            "end_line": 30,
                            "before_code": "def old(): pass",
                            "confidence": 0.9,
                            "estimated_impact": "high",
                        },
                    ],
                },
            },
        )

        crew._agents = {"analyzer": mock_analyzer, "writer": MagicMock()}

        report = await crew.analyze("def test(): pass", "test.py")

        assert report.target == "test.py"
        assert len(report.findings) == 1
        assert report.findings[0].title == "Extract method"
        assert report.findings[0].category.value == "extract_method"


class TestRefactoringCategoryEnum:
    """Test RefactoringCategory enum."""

    def test_category_values(self):
        """Test refactoring category enum values."""
        from empathy_llm_toolkit.agent_factory.crews.refactoring import RefactoringCategory

        assert RefactoringCategory.EXTRACT_METHOD.value == "extract_method"
        assert RefactoringCategory.RENAME.value == "rename"
        assert RefactoringCategory.SIMPLIFY.value == "simplify"
        assert RefactoringCategory.DEAD_CODE.value == "dead_code"

    def test_all_categories_present(self):
        """Test all expected categories are present."""
        from empathy_llm_toolkit.agent_factory.crews.refactoring import RefactoringCategory

        # Should have at least these core categories
        expected = [
            "extract_method",
            "rename",
            "simplify",
            "remove_duplication",
            "dead_code",
        ]

        values = [c.value for c in RefactoringCategory]
        for exp in expected:
            assert exp in values


class TestCrewExports:
    """Test that crew module exports are correct."""

    def test_public_exports(self):
        """Test public exports from crews module."""
        from empathy_llm_toolkit.agent_factory.crews import (
            CodeCheckpoint,
            RefactoringCategory,
            RefactoringConfig,
            RefactoringCrew,
            RefactoringFinding,
            RefactoringReport,
            UserProfile,
        )

        assert RefactoringCrew is not None
        assert RefactoringConfig is not None
        assert RefactoringFinding is not None
        assert RefactoringReport is not None
        assert RefactoringCategory is not None
        assert CodeCheckpoint is not None
        assert UserProfile is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
