"""
Tests for Prompt Engineering Wizard

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from coach_wizards import PromptEngineeringWizard
from coach_wizards.prompt_engineering_wizard import OptimizedPrompt, PromptAnalysis


@pytest.fixture
def wizard():
    """Create a Prompt Engineering Wizard instance."""
    return PromptEngineeringWizard()


class TestPromptAnalysis:
    """Tests for prompt analysis functionality."""

    def test_analyze_minimal_prompt(self, wizard):
        """Test analyzing a minimal prompt."""
        analysis = wizard.analyze_prompt("Fix this bug")

        assert isinstance(analysis, PromptAnalysis)
        assert analysis.overall_score < 0.5  # Poor prompt
        assert not analysis.has_role
        assert not analysis.has_output_format
        assert len(analysis.issues) > 0

    def test_analyze_good_prompt(self, wizard):
        """Test analyzing a well-structured prompt."""
        prompt = """You are a senior software engineer.

Context: The user is working on a Python web application.

Please analyze this code for bugs and provide your findings.

Format your response as JSON with severity and description fields.
"""
        analysis = wizard.analyze_prompt(prompt)

        assert analysis.has_role is True
        assert analysis.has_context is True
        assert analysis.has_output_format is True
        assert analysis.overall_score > 0.5

    def test_analyze_detects_role(self, wizard):
        """Test that role indicators are detected."""
        prompts_with_role = [
            "You are an expert in Python.",
            "Act as a security researcher.",
            "As a senior developer, help me...",
        ]

        for prompt in prompts_with_role:
            analysis = wizard.analyze_prompt(prompt)
            assert analysis.has_role is True, f"Failed for: {prompt}"

    def test_analyze_detects_examples(self, wizard):
        """Test that example indicators are detected."""
        prompt = """
        Help me format code.

        Example:
        Input: def foo():pass
        Output: def foo():\n    pass
        """
        analysis = wizard.analyze_prompt(prompt)
        assert analysis.has_examples is True

    def test_analyze_detects_constraints(self, wizard):
        """Test that constraint indicators are detected."""
        prompt = "Review this code. You must focus on security. Never suggest style changes."
        analysis = wizard.analyze_prompt(prompt)
        assert analysis.has_constraints is True

    def test_token_estimation(self, wizard):
        """Test token count estimation."""
        prompt = "A" * 100  # 100 characters
        analysis = wizard.analyze_prompt(prompt)

        # Should estimate ~25 tokens (100/4)
        assert 20 <= analysis.token_count <= 30


class TestPromptGeneration:
    """Tests for prompt generation functionality."""

    def test_generate_basic_prompt(self, wizard):
        """Test generating a basic prompt."""
        prompt = wizard.generate_prompt(task="Review this code for bugs")

        assert "You are" in prompt
        assert "Review this code for bugs" in prompt

    def test_generate_with_role(self, wizard):
        """Test generating a prompt with custom role."""
        prompt = wizard.generate_prompt(
            task="Analyze security",
            role="a senior security engineer",
        )

        assert "You are a senior security engineer" in prompt

    def test_generate_with_context(self, wizard):
        """Test generating a prompt with context."""
        prompt = wizard.generate_prompt(
            task="Review code",
            context="The user is building a healthcare application.",
        )

        assert "## Context" in prompt
        assert "healthcare application" in prompt

    def test_generate_with_constraints(self, wizard):
        """Test generating a prompt with constraints."""
        prompt = wizard.generate_prompt(
            task="Review code",
            constraints=["Focus on OWASP top 10", "Ignore style issues"],
        )

        assert "## Constraints" in prompt
        assert "OWASP top 10" in prompt
        assert "style issues" in prompt

    def test_generate_with_examples(self, wizard):
        """Test generating a prompt with examples."""
        prompt = wizard.generate_prompt(
            task="Format code",
            examples=[
                {"input": "def foo():pass", "output": "def foo():\n    pass"},
            ],
        )

        assert "## Examples" in prompt
        assert "Input:" in prompt
        assert "Output:" in prompt

    def test_generate_with_output_format(self, wizard):
        """Test generating a prompt with output format."""
        prompt = wizard.generate_prompt(
            task="Analyze code",
            output_format="JSON with severity and message fields",
        )

        assert "## Output Format" in prompt
        assert "JSON" in prompt


class TestFewShotExamples:
    """Tests for few-shot example functionality."""

    def test_add_examples_at_end(self, wizard):
        """Test adding examples at the end."""
        original = "Analyze this code."
        examples = [{"input": "x=1", "output": "Good"}]

        result = wizard.add_few_shot_examples(original, examples)

        assert "## Examples" in result
        assert result.index("Analyze") < result.index("Examples")

    def test_add_examples_at_start(self, wizard):
        """Test adding examples at the start."""
        original = "Analyze this code."
        examples = [{"input": "x=1", "output": "Good"}]

        result = wizard.add_few_shot_examples(original, examples, position="start")

        assert "## Examples" in result
        assert result.index("Examples") < result.index("Analyze")

    def test_multiple_examples(self, wizard):
        """Test adding multiple examples."""
        original = "Analyze this code."
        examples = [
            {"input": "x=1", "output": "Good"},
            {"input": "y=None", "output": "Warning: potential null"},
        ]

        result = wizard.add_few_shot_examples(original, examples)

        assert "Example 1" in result
        assert "Example 2" in result


class TestTokenOptimization:
    """Tests for token optimization functionality."""

    def test_optimize_removes_whitespace(self, wizard):
        """Test that optimization removes redundant whitespace."""
        prompt = "Hello\n\n\n\nWorld   test"
        result = wizard.optimize_tokens(prompt)

        assert isinstance(result, OptimizedPrompt)
        assert "\n\n\n\n" not in result.optimized_prompt
        assert "   " not in result.optimized_prompt

    def test_optimize_shortens_phrases(self, wizard):
        """Test that optimization shortens verbose phrases."""
        prompt = "In order to fix the bug, we need to..."
        result = wizard.optimize_tokens(prompt)

        assert "in order to" not in result.optimized_prompt.lower()
        assert "to fix" in result.optimized_prompt.lower()

    def test_optimize_removes_fillers(self, wizard):
        """Test that optimization removes filler words."""
        prompt = "We basically need to actually just fix this."
        result = wizard.optimize_tokens(prompt)

        # Should remove some filler words
        assert result.optimized_tokens <= result.original_tokens

    def test_optimize_tracks_changes(self, wizard):
        """Test that optimization tracks changes made."""
        prompt = "In order to fix   the bug basically..."
        result = wizard.optimize_tokens(prompt)

        assert len(result.changes_made) > 0

    def test_optimize_calculates_reduction(self, wizard):
        """Test that token reduction is calculated."""
        prompt = "This is a very very verbose prompt with lots of redundant     whitespace."
        result = wizard.optimize_tokens(prompt)

        assert result.token_reduction >= 0


class TestChainOfThought:
    """Tests for chain-of-thought scaffolding."""

    def test_add_cot_step_by_step(self, wizard):
        """Test adding step-by-step CoT."""
        prompt = "Solve this problem."
        result = wizard.add_chain_of_thought(prompt, "step_by_step")

        assert "## Reasoning Process" in result
        assert "step by step" in result.lower()

    def test_add_cot_pros_cons(self, wizard):
        """Test adding pros/cons CoT."""
        prompt = "Evaluate these options."
        result = wizard.add_chain_of_thought(prompt, "pros_cons")

        assert "pros" in result.lower()
        assert "cons" in result.lower()

    def test_add_cot_debug(self, wizard):
        """Test adding debugging CoT."""
        prompt = "Fix this bug."
        result = wizard.add_chain_of_thought(prompt, "debug")

        assert "expected behavior" in result.lower()
        assert "actual behavior" in result.lower()
        assert "root cause" in result.lower()

    def test_add_cot_analysis(self, wizard):
        """Test adding analysis CoT."""
        prompt = "Analyze this system."
        result = wizard.add_chain_of_thought(prompt, "analysis")

        assert "scope" in result.lower()
        assert "components" in result.lower()


class TestWizardInterface:
    """Tests for BaseCoachWizard interface compliance."""

    def test_wizard_properties(self, wizard):
        """Test wizard has required properties."""
        assert wizard.name == "prompt-engineering"
        assert wizard.category == "prompt_optimization"
        assert "natural_language" in wizard.languages

    def test_analyze_code_returns_issues(self, wizard):
        """Test analyze_code returns WizardIssues."""
        issues = wizard.analyze_code("Fix this", "prompt.txt", "text")

        assert isinstance(issues, list)
        if issues:
            from coach_wizards.base_wizard import WizardIssue

            assert all(isinstance(i, WizardIssue) for i in issues)

    def test_suggest_fixes(self, wizard):
        """Test suggest_fixes returns string."""
        from coach_wizards.base_wizard import WizardIssue

        issue = WizardIssue(
            severity="warning",
            message="Prompt lacks role",
            file_path="test.txt",
            line_number=None,
            code_snippet=None,
            fix_suggestion=None,
            category="prompt_structure",
            confidence=0.8,
        )

        fix = wizard.suggest_fixes(issue)

        assert isinstance(fix, str)
        assert len(fix) > 0

    def test_predict_future_issues(self, wizard):
        """Test predict_future_issues returns predictions."""
        # Low clarity prompt should predict issues
        predictions = wizard.predict_future_issues(
            code="Fix bug",
            file_path="prompt.txt",
            project_context={"team_size": 5},
        )

        assert isinstance(predictions, list)


class TestPromptAnalysisDataclass:
    """Tests for PromptAnalysis dataclass."""

    def test_prompt_analysis_defaults(self):
        """Test PromptAnalysis default values."""
        analysis = PromptAnalysis(
            overall_score=0.5,
            clarity_score=0.5,
            specificity_score=0.5,
            structure_score=0.5,
            token_count=100,
            estimated_cost=0.001,
        )

        assert analysis.issues == []
        assert analysis.suggestions == []
        assert analysis.has_role is False

    def test_prompt_analysis_with_all_fields(self):
        """Test PromptAnalysis with all fields."""
        analysis = PromptAnalysis(
            overall_score=0.9,
            clarity_score=0.8,
            specificity_score=0.9,
            structure_score=1.0,
            token_count=500,
            estimated_cost=0.005,
            issues=["Minor issue"],
            suggestions=["Consider X"],
            has_role=True,
            has_context=True,
            has_examples=True,
            has_constraints=True,
            has_output_format=True,
        )

        assert analysis.overall_score == 0.9
        assert analysis.has_role is True
        assert len(analysis.issues) == 1


class TestOptimizedPromptDataclass:
    """Tests for OptimizedPrompt dataclass."""

    def test_optimized_prompt_defaults(self):
        """Test OptimizedPrompt default values."""
        result = OptimizedPrompt(
            original_prompt="Hello",
            optimized_prompt="Hi",
            original_tokens=10,
            optimized_tokens=5,
            token_reduction=0.5,
            quality_preserved=True,
        )

        assert result.changes_made == []
        assert result.token_reduction == 0.5
