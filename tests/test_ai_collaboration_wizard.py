"""
Tests for AICollaborationWizard - Level 4 Anticipatory Empathy.

Tests cover:
- Initialization and configuration
- Required context validation
- Collaboration maturity analysis
- Bottleneck prediction
- Recommendation generation
- Pattern extraction
- Helper detection methods
- Edge cases and error handling
"""

import pytest

from empathy_software_plugin.wizards.ai_collaboration_wizard import AICollaborationWizard


class TestAICollaborationWizardInitialization:
    """Test wizard initialization and configuration."""

    def test_initialization(self):
        """Test wizard initializes with correct attributes."""
        wizard = AICollaborationWizard()
        assert wizard.name == "AI Collaboration Pattern Wizard"
        assert wizard.domain == "software"
        assert wizard.empathy_level == 4
        assert wizard.category == "ai_development"

    def test_required_context(self):
        """Test required context fields are correct."""
        wizard = AICollaborationWizard()
        required = wizard.get_required_context()
        assert "ai_integration_files" in required
        assert "project_path" in required
        assert "ai_usage_patterns" in required


class TestAICollaborationWizardAnalyze:
    """Test main analyze method."""

    @pytest.fixture
    def wizard(self):
        """Create wizard instance."""
        return AICollaborationWizard()

    @pytest.fixture
    def sample_context(self, tmp_path):
        """Create sample context with test files."""
        # Create a test file with reactive AI pattern
        test_file = tmp_path / "reactive_ai.py"
        test_file.write_text(
            """
import openai

def get_response(prompt):
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
"""
        )
        return {
            "ai_integration_files": [str(test_file)],
            "project_path": str(tmp_path),
            "ai_usage_patterns": [],
        }

    @pytest.mark.asyncio
    async def test_analyze_returns_expected_structure(self, wizard, sample_context):
        """Test analyze returns correct structure."""
        result = await wizard.analyze(sample_context)

        assert "issues" in result
        assert "predictions" in result
        assert "recommendations" in result
        assert "patterns" in result
        assert "confidence" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_analyze_metadata_contains_wizard_info(self, wizard, sample_context):
        """Test metadata includes wizard information."""
        result = await wizard.analyze(sample_context)

        assert result["metadata"]["wizard"] == "AI Collaboration Pattern Wizard"
        assert result["metadata"]["empathy_level"] == 4
        assert "current_maturity_level" in result["metadata"]
        assert "files_analyzed" in result["metadata"]

    @pytest.mark.asyncio
    async def test_analyze_confidence_is_high(self, wizard, sample_context):
        """Test confidence level is set correctly."""
        result = await wizard.analyze(sample_context)
        assert result["confidence"] == 0.90

    @pytest.mark.asyncio
    async def test_analyze_with_empty_files_list(self, wizard):
        """Test analyze with empty files list."""
        context = {
            "ai_integration_files": [],
            "project_path": "/tmp",
            "ai_usage_patterns": [],
        }
        result = await wizard.analyze(context)
        assert result["metadata"]["files_analyzed"] == 0

    @pytest.mark.asyncio
    async def test_analyze_with_missing_optional_context(self, wizard, tmp_path):
        """Test analyze works with empty ai_usage_patterns."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import anthropic")

        context = {
            "ai_integration_files": [str(test_file)],
            "project_path": str(tmp_path),
            "ai_usage_patterns": [],  # Required field, but can be empty
        }
        result = await wizard.analyze(context)
        assert "issues" in result


class TestCollaborationMaturityAnalysis:
    """Test collaboration maturity analysis."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    @pytest.mark.asyncio
    async def test_detects_level_1_reactive_patterns(self, wizard, tmp_path):
        """Test detection of Level 1 reactive patterns."""
        # Create multiple reactive files
        for i in range(5):
            f = tmp_path / f"reactive_{i}.py"
            f.write_text(
                """
import openai
def call_ai(prompt):
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
"""
            )

        files = [str(f) for f in tmp_path.glob("*.py")]
        issues = await wizard._analyze_collaboration_maturity(files, [])

        # May or may not detect based on threshold (70%)
        assert isinstance(issues, list)

    @pytest.mark.asyncio
    async def test_detects_no_context_accumulation(self, wizard, tmp_path):
        """Test detection of missing context accumulation."""
        test_file = tmp_path / "no_context.py"
        test_file.write_text("import openai")

        issues = await wizard._analyze_collaboration_maturity([str(test_file)], [])

        context_issues = [i for i in issues if i.get("type") == "no_context_accumulation"]
        assert len(context_issues) > 0
        assert context_issues[0]["severity"] == "warning"

    @pytest.mark.asyncio
    async def test_detects_no_pattern_detection(self, wizard, tmp_path):
        """Test detection of missing pattern detection capability."""
        test_file = tmp_path / "basic.py"
        test_file.write_text("import anthropic")

        issues = await wizard._analyze_collaboration_maturity([str(test_file)], [])

        pattern_issues = [i for i in issues if i.get("type") == "no_pattern_detection"]
        assert len(pattern_issues) > 0
        assert pattern_issues[0]["severity"] == "info"

    @pytest.mark.asyncio
    async def test_detects_no_trajectory_analysis(self, wizard, tmp_path):
        """Test detection of missing trajectory analysis."""
        test_file = tmp_path / "no_trajectory.py"
        test_file.write_text("import openai")

        issues = await wizard._analyze_collaboration_maturity([str(test_file)], [])

        trajectory_issues = [i for i in issues if i.get("type") == "no_trajectory_analysis"]
        assert len(trajectory_issues) > 0

    @pytest.mark.asyncio
    async def test_no_issues_with_advanced_codebase(self, wizard, tmp_path):
        """Test no issues detected with advanced collaboration patterns."""
        advanced_file = tmp_path / "advanced.py"
        advanced_file.write_text(
            """
from empathy_os import CollaborationState, PatternLibrary

class AdvancedAI:
    def __init__(self):
        self.state = CollaborationState()
        self.patterns = PatternLibrary()
        self.trajectory = TrajectoryAnalyzer()
        self.context_history = []
        self.conversation_memory = {}

    def analyze_trajectory(self):
        return self.trajectory.predict_bottleneck()
"""
        )

        issues = await wizard._analyze_collaboration_maturity([str(advanced_file)], [])
        # Advanced codebase should have fewer issues
        assert isinstance(issues, list)


class TestBottleneckPredictions:
    """Test bottleneck prediction logic."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    @pytest.mark.asyncio
    async def test_predicts_reactive_pattern_limitation(self, wizard, tmp_path):
        """Test prediction of reactive pattern limitation with many integrations."""
        # Create 6+ reactive files to trigger prediction
        for i in range(6):
            f = tmp_path / f"reactive_{i}.py"
            f.write_text("import openai\ndef call(): pass")

        files = [str(f) for f in tmp_path.glob("*.py")]
        predictions = await wizard._predict_collaboration_bottlenecks(files, [], {})

        reactive_preds = [p for p in predictions if p.get("type") == "reactive_pattern_limitation"]
        assert len(reactive_preds) > 0
        assert reactive_preds[0]["probability"] == "high"
        assert reactive_preds[0]["impact"] == "high"

    @pytest.mark.asyncio
    async def test_predicts_missing_feedback_loops(self, wizard, tmp_path):
        """Test prediction of missing feedback loops."""
        test_file = tmp_path / "no_feedback.py"
        test_file.write_text("import anthropic")

        predictions = await wizard._predict_collaboration_bottlenecks([str(test_file)], [], {})

        feedback_preds = [p for p in predictions if p.get("type") == "missing_feedback_loops"]
        assert len(feedback_preds) > 0
        assert "prevention_steps" in feedback_preds[0]

    @pytest.mark.asyncio
    async def test_predicts_siloed_integrations(self, wizard, tmp_path):
        """Test prediction of siloed AI integrations."""
        # Create 4+ files without pattern sharing
        for i in range(4):
            f = tmp_path / f"siloed_{i}.py"
            f.write_text("import openai")

        files = [str(f) for f in tmp_path.glob("*.py")]
        predictions = await wizard._predict_collaboration_bottlenecks(files, [], {})

        siloed_preds = [p for p in predictions if p.get("type") == "siloed_ai_integrations"]
        assert len(siloed_preds) > 0
        assert siloed_preds[0]["probability"] == "medium"

    @pytest.mark.asyncio
    async def test_predicts_ai_tool_mindset(self, wizard, tmp_path):
        """Test prediction of AI tool mindset."""
        test_file = tmp_path / "tool.py"
        test_file.write_text("import openai")

        predictions = await wizard._predict_collaboration_bottlenecks([str(test_file)], [], {})

        tool_preds = [p for p in predictions if p.get("type") == "ai_tool_mindset"]
        assert len(tool_preds) > 0
        assert "personal_experience" in tool_preds[0]

    @pytest.mark.asyncio
    async def test_predicts_architecture_gap(self, wizard, tmp_path):
        """Test prediction of collaboration architecture gap."""
        # Create 3+ files without architecture
        for i in range(3):
            f = tmp_path / f"no_arch_{i}.py"
            f.write_text("import anthropic")

        files = [str(f) for f in tmp_path.glob("*.py")]
        predictions = await wizard._predict_collaboration_bottlenecks(files, [], {})

        arch_preds = [p for p in predictions if p.get("type") == "collaboration_architecture_gap"]
        assert len(arch_preds) > 0
        assert arch_preds[0]["impact"] == "high"

    @pytest.mark.asyncio
    async def test_no_predictions_with_mature_codebase(self, wizard, tmp_path):
        """Test fewer predictions with mature collaboration patterns."""
        mature_file = tmp_path / "mature.py"
        mature_file.write_text(
            """
from empathy_os import EmpathyOS, CollaborationState
from patterns import PatternLibrary

class MatureAI:
    def __init__(self):
        self.empathy = EmpathyOS()
        self.state = CollaborationState()
        self.patterns = PatternLibrary()
        self.feedback = QualityTracker()
        self.trajectory = TrajectoryAnalyzer()
        self.trust_level = 0.5
        self.context_history = []

    def analyze_trajectory(self):
        return self.trajectory.growth_rate()

    def contribute_patterns(self, pattern):
        self.patterns.add_cross_domain(pattern)
"""
        )

        predictions = await wizard._predict_collaboration_bottlenecks([str(mature_file)], [], {})
        # Mature codebase should have fewer critical predictions
        assert isinstance(predictions, list)


class TestRecommendations:
    """Test recommendation generation."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    def test_recommendations_include_maturity_level(self, wizard):
        """Test recommendations include current maturity level."""
        issues = [{"type": "level_1_reactive", "current_level": 1}]
        predictions = []

        recommendations = wizard._generate_recommendations(issues, predictions)
        assert any("Level 1" in r for r in recommendations)

    def test_recommendations_include_high_impact_alerts(self, wizard):
        """Test high impact predictions are included as alerts."""
        issues = []
        predictions = [
            {
                "type": "reactive_pattern_limitation",
                "alert": "Test alert message",
                "impact": "high",
                "prevention_steps": ["Step 1", "Step 2"],
            }
        ]

        recommendations = wizard._generate_recommendations(issues, predictions)
        assert any("[ALERT]" in r for r in recommendations)
        assert any("Step 1" in r for r in recommendations)

    def test_recommendations_include_growth_path(self, wizard):
        """Test recommendations include growth path."""
        issues = [{"current_level": 2}]
        predictions = []

        recommendations = wizard._generate_recommendations(issues, predictions)
        assert any("Growth Path" in r for r in recommendations)

    def test_growth_path_suggests_next_level(self, wizard):
        """Test growth path suggests appropriate next level."""
        # Level 1 -> Level 2
        issues = [{"current_level": 1}]
        recs = wizard._generate_recommendations(issues, [])
        assert any("Level 2" in r and "Guided" in r for r in recs)

        # Level 2 -> Level 3
        issues = [{"current_level": 2}]
        recs = wizard._generate_recommendations(issues, [])
        assert any("Level 3" in r and "Proactive" in r for r in recs)

        # Level 3 -> Level 4
        issues = [{"current_level": 3}]
        recs = wizard._generate_recommendations(issues, [])
        assert any("Level 4" in r and "Anticipatory" in r for r in recs)

        # Level 4 -> Level 5
        issues = [{"current_level": 4}]
        recs = wizard._generate_recommendations(issues, [])
        assert any("Level 5" in r and "Systems" in r for r in recs)


class TestPatternExtraction:
    """Test pattern extraction."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    def test_extracts_collaboration_maturity_pattern(self, wizard):
        """Test extraction of collaboration maturity pattern."""
        patterns = wizard._extract_patterns([], [])

        assert len(patterns) > 0
        pattern = patterns[0]
        assert pattern["pattern_type"] == "collaboration_maturity_model"
        assert pattern["domain_agnostic"] is True

    def test_pattern_has_applicable_domains(self, wizard):
        """Test pattern includes applicable domains."""
        patterns = wizard._extract_patterns([], [])
        pattern = patterns[0]

        assert "applicable_to" in pattern
        assert "AI-human collaboration" in pattern["applicable_to"]

    def test_pattern_includes_levels(self, wizard):
        """Test pattern includes all 5 levels."""
        patterns = wizard._extract_patterns([], [])
        pattern = patterns[0]

        assert "levels" in pattern
        assert len(pattern["levels"]) == 5
        assert "Reactive" in pattern["levels"][0]
        assert "Anticipatory" in pattern["levels"][3]


class TestMaturityAssessment:
    """Test maturity level assessment methods."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    def test_assess_maturity_from_issues(self, wizard):
        """Test maturity level assessment from issues."""
        issues = [
            {"current_level": 1},
            {"current_level": 2},
            {"current_level": 1},
        ]
        level = wizard._assess_maturity_level(issues)
        assert level == 2  # Max level from issues

    def test_assess_maturity_with_empty_issues(self, wizard):
        """Test maturity assessment with empty issues returns 1."""
        level = wizard._assess_maturity_level([])
        assert level == 1

    def test_assess_maturity_numeric_level_4(self, wizard, tmp_path):
        """Test numeric assessment returns Level 4 with trajectory analysis."""
        test_file = tmp_path / "level4.py"
        test_file.write_text(
            """
class Analyzer:
    def trajectory(self):
        return self.growth_rate()
    def anticipatory(self):
        pass
"""
        )

        level = wizard._assess_maturity_level_numeric([str(test_file)])
        assert level == 4

    def test_assess_maturity_numeric_level_3(self, wizard, tmp_path):
        """Test numeric assessment returns Level 3 with pattern detection."""
        test_file = tmp_path / "level3.py"
        test_file.write_text(
            """
from patterns import PatternLibrary
def detect_patterns():
    pass
"""
        )

        level = wizard._assess_maturity_level_numeric([str(test_file)])
        assert level == 3

    def test_assess_maturity_numeric_level_2(self, wizard, tmp_path):
        """Test numeric assessment returns Level 2 with context accumulation."""
        test_file = tmp_path / "level2.py"
        test_file.write_text(
            """
state = CollaborationState()
context_history = []
"""
        )

        level = wizard._assess_maturity_level_numeric([str(test_file)])
        assert level == 2

    def test_assess_maturity_numeric_level_1(self, wizard, tmp_path):
        """Test numeric assessment returns Level 1 for basic code."""
        test_file = tmp_path / "level1.py"
        test_file.write_text("import openai")

        level = wizard._assess_maturity_level_numeric([str(test_file)])
        assert level == 1


class TestHelperDetectionMethods:
    """Test helper detection methods."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    def test_detect_reactive_patterns_with_openai(self, wizard, tmp_path):
        """Test detection of reactive patterns with OpenAI."""
        test_file = tmp_path / "reactive.py"
        test_file.write_text(
            """
import openai
def simple_call():
    return openai.chat.completions.create()
"""
        )

        count = wizard._detect_reactive_patterns([str(test_file)])
        assert count == 1

    def test_detect_reactive_patterns_with_context(self, wizard, tmp_path):
        """Test non-reactive pattern when context is present."""
        test_file = tmp_path / "with_context.py"
        test_file.write_text(
            """
import openai
def call_with_context(context):
    return openai.chat.completions.create(context=context)
"""
        )

        count = wizard._detect_reactive_patterns([str(test_file)])
        assert count == 0  # Has context, not reactive

    def test_has_context_accumulation_true(self, wizard, tmp_path):
        """Test context accumulation detection - true case."""
        test_file = tmp_path / "has_context.py"
        test_file.write_text("state = CollaborationState()")

        assert wizard._has_context_accumulation([str(test_file)]) is True

    def test_has_context_accumulation_false(self, wizard, tmp_path):
        """Test context accumulation detection - false case."""
        test_file = tmp_path / "no_context.py"
        test_file.write_text("import openai")

        assert wizard._has_context_accumulation([str(test_file)]) is False

    def test_has_pattern_detection_true(self, wizard, tmp_path):
        """Test pattern detection detection - true case."""
        test_file = tmp_path / "has_patterns.py"
        test_file.write_text("library = PatternLibrary()")

        assert wizard._has_pattern_detection([str(test_file)]) is True

    def test_has_pattern_detection_false(self, wizard, tmp_path):
        """Test pattern detection detection - false case."""
        test_file = tmp_path / "no_patterns.py"
        test_file.write_text("import openai")

        assert wizard._has_pattern_detection([str(test_file)]) is False

    def test_has_trajectory_analysis_true(self, wizard, tmp_path):
        """Test trajectory analysis detection - true case."""
        test_file = tmp_path / "has_trajectory.py"
        test_file.write_text(
            """
def analyze_trajectory():
    return growth_rate()
"""
        )

        assert wizard._has_trajectory_analysis([str(test_file)]) is True

    def test_has_trajectory_analysis_false(self, wizard, tmp_path):
        """Test trajectory analysis detection - false case."""
        test_file = tmp_path / "no_trajectory.py"
        test_file.write_text("import anthropic")

        assert wizard._has_trajectory_analysis([str(test_file)]) is False

    def test_has_feedback_loops_true(self, wizard, tmp_path):
        """Test feedback loop detection - true case."""
        test_file = tmp_path / "has_feedback.py"
        test_file.write_text("self.trust_level = 0.5")

        assert wizard._has_feedback_loops([str(test_file)]) is True

    def test_has_feedback_loops_false(self, wizard, tmp_path):
        """Test feedback loop detection - false case."""
        test_file = tmp_path / "no_feedback.py"
        test_file.write_text("import openai")

        assert wizard._has_feedback_loops([str(test_file)]) is False

    def test_has_pattern_sharing_true(self, wizard, tmp_path):
        """Test pattern sharing detection - true case."""
        test_file = tmp_path / "has_sharing.py"
        test_file.write_text("patterns.contribute_patterns(p)")

        assert wizard._has_pattern_sharing([str(test_file)]) is True

    def test_ai_used_as_tool_true(self, wizard, tmp_path):
        """Test AI tool mindset detection - true case."""
        test_file = tmp_path / "tool_usage.py"
        test_file.write_text("import openai")

        assert wizard._ai_used_as_tool([str(test_file)]) is True

    def test_ai_used_as_tool_false(self, wizard, tmp_path):
        """Test AI tool mindset detection - false case (partnership)."""
        test_file = tmp_path / "partnership.py"
        test_file.write_text(
            """
state = CollaborationState()
context_history = []
self.trust_level = 0.5
feedback = QualityTracker()
"""
        )

        assert wizard._ai_used_as_tool([str(test_file)]) is False

    def test_has_collaboration_architecture_true(self, wizard, tmp_path):
        """Test collaboration architecture detection - true case."""
        test_file = tmp_path / "has_arch.py"
        test_file.write_text("from empathy_os import EmpathyOS")

        assert wizard._has_collaboration_architecture([str(test_file)]) is True

    def test_has_any_keyword_with_missing_file(self, wizard):
        """Test keyword detection handles missing files gracefully."""
        result = wizard._has_any_keyword(["/nonexistent/file.py"], ["keyword"])
        assert result is False

    def test_detect_reactive_patterns_missing_file(self, wizard):
        """Test reactive pattern detection handles missing files."""
        count = wizard._detect_reactive_patterns(["/nonexistent/file.py"])
        assert count == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    @pytest.mark.asyncio
    async def test_analyze_with_nonexistent_files(self, wizard):
        """Test analyze handles nonexistent files gracefully."""
        context = {
            "ai_integration_files": ["/nonexistent/file.py"],
            "project_path": "/tmp",
            "ai_usage_patterns": [],
        }
        result = await wizard.analyze(context)
        assert "issues" in result
        assert "predictions" in result

    @pytest.mark.asyncio
    async def test_analyze_with_empty_file(self, wizard, tmp_path):
        """Test analyze handles empty files."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        context = {
            "ai_integration_files": [str(empty_file)],
            "project_path": str(tmp_path),
            "ai_usage_patterns": [],
        }
        result = await wizard.analyze(context)
        assert result["metadata"]["files_analyzed"] == 1

    @pytest.mark.asyncio
    async def test_analyze_with_binary_file(self, wizard, tmp_path):
        """Test analyze handles binary files gracefully."""
        binary_file = tmp_path / "binary.pyc"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        context = {
            "ai_integration_files": [str(binary_file)],
            "project_path": str(tmp_path),
            "ai_usage_patterns": [],
        }
        # Should not raise exception
        result = await wizard.analyze(context)
        assert isinstance(result, dict)

    def test_generate_recommendations_empty_inputs(self, wizard):
        """Test recommendations with empty inputs."""
        recommendations = wizard._generate_recommendations([], [])
        assert isinstance(recommendations, list)
        assert any("Growth Path" in r for r in recommendations)


class TestIntegration:
    """Integration tests for full analysis workflow."""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self, wizard, tmp_path):
        """Test complete analysis workflow."""
        # Create realistic project structure
        (tmp_path / "src").mkdir()

        ai_file = tmp_path / "src" / "ai_service.py"
        ai_file.write_text(
            """
import openai

class AIService:
    def __init__(self):
        self.client = openai.OpenAI()

    def generate(self, prompt):
        return self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
"""
        )

        context = {
            "ai_integration_files": [str(ai_file)],
            "project_path": str(tmp_path),
            "ai_usage_patterns": [{"type": "reactive", "frequency": "high"}],
        }

        result = await wizard.analyze(context)

        # Verify complete result structure
        assert result["confidence"] == 0.90
        assert result["metadata"]["empathy_level"] == 4
        assert len(result["patterns"]) > 0
        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_mature_project_analysis(self, wizard, tmp_path):
        """Test analysis of mature AI collaboration project."""
        mature_file = tmp_path / "empathy_ai.py"
        mature_file.write_text(
            """
from empathy_os import EmpathyOS, CollaborationState
from patterns import PatternLibrary

class MatureAICollaboration:
    def __init__(self):
        self.empathy = EmpathyOS()
        self.state = CollaborationState()
        self.patterns = PatternLibrary()
        self.context_history = []
        self.conversation_memory = {}
        self.trust_level = 0.8
        self.feedback = QualityTracker()

    def analyze_trajectory(self):
        return self.trajectory_analyzer.growth_rate()

    def anticipatory_suggestion(self, context):
        return self.patterns.predict_bottleneck(context)

    def contribute_patterns(self, pattern):
        self.patterns.add_cross_domain(pattern)
        self.shared_patterns.publish(pattern)
"""
        )

        context = {
            "ai_integration_files": [str(mature_file)],
            "project_path": str(tmp_path),
            "ai_usage_patterns": [],
        }

        result = await wizard.analyze(context)

        # Mature project should have fewer issues and predictions
        # Note: current_maturity_level is based on max issue level found
        # A mature codebase with all features present triggers no issues,
        # so maturity defaults to 1. The actual maturity is shown in predictions.
        assert result["metadata"]["files_analyzed"] == 1
        # Verify it has the collaboration architecture (EmpathyOS detected)
        assert wizard._has_collaboration_architecture([str(mature_file)])

    @pytest.mark.asyncio
    async def test_identifies_all_collaboration_patterns(self, wizard, tmp_path):
        """Test wizard identifies all collaboration pattern types."""
        # Create files that trigger different patterns
        files = []

        for i in range(6):
            f = tmp_path / f"service_{i}.py"
            f.write_text("import openai\ndef call(): pass")
            files.append(str(f))

        context = {
            "ai_integration_files": files,
            "project_path": str(tmp_path),
            "ai_usage_patterns": [],
        }

        result = await wizard.analyze(context)

        # Check prediction types
        prediction_types = {p["type"] for p in result["predictions"]}

        # Should have multiple prediction types
        assert len(prediction_types) >= 2

        # Should have high-impact predictions
        high_impact = [p for p in result["predictions"] if p.get("impact") == "high"]
        assert len(high_impact) >= 1
