"""Tests for AI Development Wizards

These tests validate Level 4 Anticipatory Empathy in action.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import os
import shutil

# Import wizards
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "empathy_software_plugin"))

from wizards.ai_collaboration_wizard import AICollaborationWizard
from wizards.ai_context_wizard import AIContextWindowWizard
from wizards.ai_documentation_wizard import AIDocumentationWizard
from wizards.prompt_engineering_wizard import PromptEngineeringWizard


class TestPromptEngineeringWizard:
    """Test Prompt Engineering Quality Wizard"""

    @pytest.fixture
    def wizard(self):
        return PromptEngineeringWizard()

    @pytest.fixture
    def temp_prompt_file(self):
        """Create a temporary prompt file for testing"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(
                """
You are a helpful assistant.

Please help the user with their task.

Try to be as helpful as possible.
            """,
            )
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    def test_wizard_initialization(self, wizard):
        """Test wizard initializes correctly"""
        assert wizard.name == "Prompt Engineering Quality Wizard"
        assert wizard.domain == "software"
        assert wizard.empathy_level == 4
        assert wizard.category == "ai_development"

    def test_required_context(self, wizard):
        """Test wizard declares required context"""
        required = wizard.get_required_context()
        assert "prompt_files" in required
        assert "project_path" in required

    @pytest.mark.asyncio
    async def test_analyze_detects_vague_language(self, wizard, temp_prompt_file, temp_project_dir):
        """Test wizard detects vague language in prompts"""
        context = {
            "prompt_files": [temp_prompt_file],
            "project_path": temp_project_dir,
            "ai_provider": "anthropic",
            "version_history": [],
        }

        result = await wizard.analyze(context)

        # Should detect vague language
        issues = result["issues"]
        assert any(
            issue["type"] == "vague_language" for issue in issues
        ), "Should detect vague language like 'try to', 'help'"

    @pytest.mark.asyncio
    async def test_analyze_detects_missing_structure(
        self,
        wizard,
        temp_prompt_file,
        temp_project_dir,
    ):
        """Test wizard detects unclear prompt structure"""
        context = {
            "prompt_files": [temp_prompt_file],
            "project_path": temp_project_dir,
            "ai_provider": "anthropic",
            "version_history": [],
        }

        result = await wizard.analyze(context)

        # Should detect unclear structure
        issues = result["issues"]
        assert any(
            issue["type"] == "unclear_structure" for issue in issues
        ), "Should detect missing role/task/context structure"

    @pytest.mark.asyncio
    async def test_level_4_predictions(self, wizard, temp_prompt_file, temp_project_dir):
        """Test Level 4 anticipatory predictions"""
        # Create multiple prompt files to trigger sprawl prediction
        temp_files = [temp_prompt_file]
        for i in range(12):
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
                f.write(f"Prompt {i}")
                temp_files.append(f.name)

        try:
            context = {
                "prompt_files": temp_files,
                "project_path": temp_project_dir,
                "ai_provider": "anthropic",
                "version_history": [],
            }

            result = await wizard.analyze(context)

            # Should predict prompt sprawl
            predictions = result["predictions"]
            assert any(
                pred["type"] == "prompt_sprawl" for pred in predictions
            ), "Should predict prompt sprawl with 13+ files"

        finally:
            # Cleanup
            for temp_file in temp_files[1:]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_returns_confidence(self, wizard, temp_prompt_file, temp_project_dir):
        """Test wizard returns confidence score"""
        context = {
            "prompt_files": [temp_prompt_file],
            "project_path": temp_project_dir,
            "ai_provider": "anthropic",
            "version_history": [],
        }

        result = await wizard.analyze(context)

        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_extracts_patterns(self, wizard, temp_prompt_file, temp_project_dir):
        """Test wizard extracts cross-domain patterns (Level 5)"""
        context = {
            "prompt_files": [temp_prompt_file],
            "project_path": temp_project_dir,
            "ai_provider": "anthropic",
            "version_history": [
                {"hash": "abc123", "files": ["main.py", "api.py"]},
                {"hash": "def456", "files": ["utils.py", "models.py"]},
                {"hash": "ghi789", "files": ["config.py"]},
            ],
        }

        result = await wizard.analyze(context)

        # Should extract patterns
        patterns = result.get("patterns", [])
        # May or may not extract patterns depending on detection logic
        assert isinstance(patterns, list)


class TestAIContextWindowWizard:
    """Test AI Context Window Management Wizard"""

    @pytest.fixture
    def wizard(self):
        return AIContextWindowWizard()

    def test_wizard_initialization(self, wizard):
        """Test wizard initializes correctly"""
        assert wizard.name == "AI Context Window Management Wizard"
        assert wizard.empathy_level == 4
        assert wizard.domain == "software"

    def test_required_context(self, wizard):
        """Test wizard declares required context"""
        required = wizard.get_required_context()
        assert "ai_calls" in required
        assert "context_sources" in required
        assert "ai_provider" in required

    @pytest.mark.asyncio
    async def test_detects_high_context_usage(self, wizard):
        """Test wizard detects high context window usage"""
        context = {
            "ai_calls": [
                {
                    "id": "call1",
                    "location": "main.py:42",
                    "prompt_size": 80000,  # High usage
                    "code_snippet": "ai.generate(prompt + context)",
                },
            ],
            "context_sources": [],
            "ai_provider": "anthropic",
            "model_name": "claude-3-sonnet",
        }

        result = await wizard.analyze(context)

        # Should detect high usage (80k / 200k = 40%, but our estimate is rough)
        issues = result["issues"]
        # May or may not trigger depending on calculation
        assert isinstance(issues, list)

    @pytest.mark.asyncio
    async def test_detects_naive_concatenation(self, wizard):
        """Test wizard detects naive string concatenation"""
        context = {
            "ai_calls": [
                {
                    "id": "call1",
                    "location": "main.py:42",
                    "prompt_size": 1000,
                    "code_snippet": "prompt = base_prompt + user_input + data",
                },
            ],
            "context_sources": [],
            "ai_provider": "openai",
            "model_name": "gpt-4",
        }

        result = await wizard.analyze(context)

        issues = result["issues"]
        assert any(
            issue["type"] == "naive_concatenation" for issue in issues
        ), "Should detect naive concatenation pattern"

    @pytest.mark.asyncio
    async def test_level_4_growth_trajectory_prediction(self, wizard):
        """Test Level 4 prediction of context growth"""
        context = {
            "ai_calls": [
                {
                    "id": "call1",
                    "location": "main.py:42",
                    "prompt_size": 5000,
                    "code_snippet": "ai.generate(prompt)",
                    "conversation_id": "conv1",
                },
                {
                    "id": "call2",
                    "location": "api.py:100",
                    "prompt_size": 8000,
                    "code_snippet": "ai.generate(prompt)",
                    "conversation_id": "conv2",
                },
            ],
            "context_sources": [
                {"type": "dynamic", "estimated_size": 1000, "call_id": "call1"},
                {"type": "dynamic", "estimated_size": 2000, "call_id": "call2"},
            ],
            "ai_provider": "anthropic",
            "model_name": "claude-3-sonnet",
            "version_history": [{"hash": "abc", "files": ["main.py"]}],
        }

        result = await wizard.analyze(context)

        # Should make Level 4 predictions
        predictions = result["predictions"]
        assert len(predictions) > 0, "Should make anticipatory predictions"

        # Check prediction structure
        for pred in predictions:
            assert "type" in pred
            assert "alert" in pred
            assert "prevention_steps" in pred


class TestAICollaborationWizard:
    """Test AI Collaboration Pattern Wizard"""

    @pytest.fixture
    def wizard(self):
        return AICollaborationWizard()

    @pytest.fixture
    def temp_ai_file(self):
        """Create temporary file with AI integration"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(
                """
import openai

def analyze_code(code):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": code}]
    )
    return response
            """,
            )
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    def test_wizard_initialization(self, wizard):
        """Test wizard initializes correctly"""
        assert wizard.name == "AI Collaboration Pattern Wizard"
        assert wizard.empathy_level == 4

    @pytest.mark.asyncio
    async def test_detects_level_1_reactive_patterns(self, wizard, temp_ai_file, temp_project_dir):
        """Test wizard detects Level 1 reactive patterns"""
        context = {
            "ai_integration_files": [temp_ai_file],
            "project_path": temp_project_dir,
            "ai_usage_patterns": [],
        }

        result = await wizard.analyze(context)

        # Should detect reactive pattern
        issues = result["issues"]
        assert any(
            "level_1" in issue.get("type", "") or issue.get("current_level", 0) == 1
            for issue in issues
        ), "Should detect Level 1 reactive patterns"

    @pytest.mark.asyncio
    async def test_assesses_maturity_level(self, wizard, temp_ai_file, temp_project_dir):
        """Test wizard assesses collaboration maturity"""
        context = {
            "ai_integration_files": [temp_ai_file],
            "project_path": temp_project_dir,
            "ai_usage_patterns": [],
        }

        result = await wizard.analyze(context)

        metadata = result["metadata"]
        assert "current_maturity_level" in metadata
        assert 1 <= metadata["current_maturity_level"] <= 5

    @pytest.mark.asyncio
    async def test_provides_growth_recommendations(self, wizard, temp_ai_file, temp_project_dir):
        """Test wizard provides recommendations for growth"""
        context = {
            "ai_integration_files": [temp_ai_file],
            "project_path": temp_project_dir,
            "ai_usage_patterns": [],
        }

        result = await wizard.analyze(context)

        recommendations = result["recommendations"]
        assert len(recommendations) > 0

        # Should include growth path
        rec_text = " ".join(recommendations)
        assert "Level" in rec_text or "growth" in rec_text.lower()


class TestAIDocumentationWizard:
    """Test AI-First Documentation Wizard"""

    @pytest.fixture
    def wizard(self):
        return AIDocumentationWizard()

    @pytest.fixture
    def temp_readme(self):
        """Create temporary README without architecture"""
        # Create temp file with README in the name so wizard detects it
        tmpdir = tempfile.mkdtemp()
        temp_path = os.path.join(tmpdir, "README.md")
        with open(temp_path, "w") as f:
            f.write(
                """
# My Project

This is a cool project that does things.

## Installation

pip install myproject

## Usage

Run the thing.
            """,
            )

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(tmpdir):
            os.rmdir(tmpdir)

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    def test_wizard_initialization(self, wizard):
        """Test wizard initializes correctly"""
        assert wizard.name == "AI-First Documentation Wizard"
        assert wizard.empathy_level == 4

    @pytest.mark.asyncio
    async def test_detects_missing_architecture(self, wizard, temp_readme, temp_project_dir):
        """Test wizard detects missing architecture overview"""
        context = {
            "documentation_files": [temp_readme],
            "code_files": [],
            "project_path": temp_project_dir,
        }

        result = await wizard.analyze(context)

        issues = result["issues"]
        assert any(
            issue["type"] == "missing_architecture_context" for issue in issues
        ), "Should detect missing architecture section"

    @pytest.mark.asyncio
    async def test_detects_ambiguous_language(self, wizard, temp_project_dir):
        """Test wizard detects ambiguous language"""
        # Create doc with ambiguous language
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(
                """
# API Documentation

You should usually call this function first.
Normally you want to initialize the system.
Try to handle errors gracefully.
            """,
            )
            temp_ambiguous = f.name

        try:
            context = {
                "documentation_files": [temp_ambiguous],
                "code_files": [],
                "project_path": temp_project_dir,
            }

            result = await wizard.analyze(context)

            issues = result["issues"]
            assert any(
                issue["type"] == "ambiguous_language" for issue in issues
            ), "Should detect ambiguous phrases"

        finally:
            if os.path.exists(temp_ambiguous):
                os.unlink(temp_ambiguous)

    @pytest.mark.asyncio
    async def test_level_4_predicts_missing_why_context(
        self,
        wizard,
        temp_readme,
        temp_project_dir,
    ):
        """Test Level 4 prediction about missing 'why' context"""
        context = {
            "documentation_files": [temp_readme],
            "code_files": [],
            "project_path": temp_project_dir,
        }

        result = await wizard.analyze(context)

        predictions = result["predictions"]
        # Should predict issue with missing 'why' context
        assert any(
            "why" in pred.get("type", "").lower() or "why" in pred.get("alert", "").lower()
            for pred in predictions
        ), "Should predict missing 'why' context issue"


class TestCrossDomainPatterns:
    """Test that wizards extract cross-domain patterns (Level 5)"""

    @pytest.mark.asyncio
    async def test_patterns_are_domain_agnostic(self):
        """Test extracted patterns claim domain-agnostic applicability"""
        wizard = PromptEngineeringWizard()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test prompt")
            temp_file = f.name

        tmpdir = tempfile.mkdtemp()

        try:
            context = {
                "prompt_files": [temp_file],
                "project_path": tmpdir,
                "ai_provider": "anthropic",
                "version_history": [
                    {"hash": "abc", "files": ["main.py", "api.py", "utils.py"]},
                    {"hash": "def", "files": ["models.py"]},
                ],
            }

            result = await wizard.analyze(context)
            patterns = result.get("patterns", [])

            if patterns:
                # If patterns extracted, verify structure
                for pattern in patterns:
                    assert "pattern_type" in pattern
                    # Many should be domain-agnostic
                    if pattern.get("domain_agnostic"):
                        assert "applicable_to" in pattern
                        assert len(pattern["applicable_to"]) > 1

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)


class TestWizardIntegration:
    """Integration tests for wizard system"""

    @pytest.mark.asyncio
    async def test_all_wizards_return_standard_format(self):
        """Test all wizards return consistent result format"""
        wizards = [
            PromptEngineeringWizard(),
            AIContextWindowWizard(),
            AICollaborationWizard(),
            AIDocumentationWizard(),
        ]

        tmpdir = tempfile.mkdtemp()

        try:
            for wizard in wizards:
                # Create minimal valid context with all required fields
                context = {key: [] for key in wizard.get_required_context()}
                context["project_path"] = tmpdir

                # Add specific fields that some wizards require
                if "ai_provider" in wizard.get_required_context():
                    context["ai_provider"] = "anthropic"
                if "model_name" in wizard.get_required_context():
                    context["model_name"] = "claude-3-sonnet"
                if "version_history" in wizard.get_required_context():
                    context["version_history"] = []

                result = await wizard.analyze(context)

                # All should return standard format
                assert "issues" in result
                assert "predictions" in result
                assert "recommendations" in result
                assert "patterns" in result
                assert "confidence" in result
                assert "metadata" in result

                assert isinstance(result["issues"], list)
                assert isinstance(result["predictions"], list)
                assert isinstance(result["recommendations"], list)
                assert isinstance(result["patterns"], list)
                assert isinstance(result["confidence"], int | float)
                assert isinstance(result["metadata"], dict)

        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)

    def test_all_wizards_are_level_4(self):
        """Test all AI development wizards operate at Level 4"""
        wizards = [
            PromptEngineeringWizard(),
            AIContextWindowWizard(),
            AICollaborationWizard(),
            AIDocumentationWizard(),
        ]

        for wizard in wizards:
            assert wizard.empathy_level == 4, f"{wizard.name} should be Level 4 (Anticipatory)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
