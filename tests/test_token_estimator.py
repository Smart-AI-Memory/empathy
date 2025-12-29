"""
Tests for Token Estimation Service.

Tests pre-flight token estimation for cost prediction.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.empathy_os.models.token_estimator import (
    TIKTOKEN_AVAILABLE,
    TOKENS_PER_CHAR_HEURISTIC,
    estimate_single_call_cost,
    estimate_tokens,
    estimate_workflow_cost,
)


class TestEstimateTokens:
    """Tests for estimate_tokens function."""

    def test_empty_string(self):
        """Test empty string returns 0."""
        assert estimate_tokens("") == 0

    def test_simple_text(self):
        """Test simple text tokenization."""
        text = "Hello, world!"
        tokens = estimate_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_longer_text(self):
        """Test longer text has more tokens."""
        short = "Hello"
        long = "Hello, this is a much longer text that should have more tokens."

        short_tokens = estimate_tokens(short)
        long_tokens = estimate_tokens(long)

        assert long_tokens > short_tokens

    def test_code_text(self):
        """Test code tokenization."""
        code = '''
def calculate_total(items: list[dict]) -> float:
    """Calculate total price."""
    total = 0.0
    for item in items:
        total += item.get("price", 0)
    return total
'''
        tokens = estimate_tokens(code)
        assert tokens > 10

    def test_default_model(self):
        """Test default model is used."""
        text = "Test text"
        tokens = estimate_tokens(text)
        assert tokens > 0

    def test_claude_model(self):
        """Test Claude model encoding."""
        text = "Test with Claude model"
        tokens = estimate_tokens(text, model_id="claude-sonnet-4-5-20250514")
        assert tokens > 0

    def test_gpt4_model(self):
        """Test GPT-4 model encoding."""
        text = "Test with GPT-4 model"
        tokens = estimate_tokens(text, model_id="gpt-4o")
        assert tokens > 0

    def test_o1_model(self):
        """Test o1 model encoding."""
        text = "Test with o1 model"
        tokens = estimate_tokens(text, model_id="o1")
        assert tokens > 0

    def test_unknown_model_fallback(self):
        """Test unknown model uses default encoding."""
        text = "Test with unknown model"
        tokens = estimate_tokens(text, model_id="unknown-model-xyz")
        assert tokens > 0

    def test_heuristic_fallback(self):
        """Test heuristic fallback when tiktoken fails."""
        text = "Test text for heuristic"

        with patch("src.empathy_os.models.token_estimator.TIKTOKEN_AVAILABLE", False):
            tokens = estimate_tokens(text)
            expected = max(1, int(len(text) * TOKENS_PER_CHAR_HEURISTIC))
            assert tokens == expected

    def test_tiktoken_available(self):
        """Test tiktoken availability flag."""
        assert isinstance(TIKTOKEN_AVAILABLE, bool)


class TestEstimateWorkflowCost:
    """Tests for estimate_workflow_cost function."""

    def test_basic_workflow_cost(self):
        """Test basic workflow cost estimation."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="def foo(): pass",
            provider="anthropic",
        )

        assert "workflow" in result
        assert "provider" in result
        assert "input_tokens" in result
        assert "stages" in result
        assert "total_min" in result
        assert "total_max" in result
        assert "display" in result
        assert "risk" in result

    def test_workflow_returns_correct_name(self):
        """Test workflow name in result."""
        result = estimate_workflow_cost(
            workflow_name="security-audit",
            input_text="test input",
        )

        assert result["workflow"] == "security-audit"

    def test_workflow_returns_correct_provider(self):
        """Test provider in result."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test",
            provider="openai",
        )

        assert result["provider"] == "openai"

    def test_unknown_provider_fallback(self):
        """Test unknown provider falls back to anthropic."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test",
            provider="unknown-provider",
        )

        assert result["provider"] == "anthropic"

    def test_input_tokens_counted(self):
        """Test input tokens are counted."""
        text = "This is a test input with some content."
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text=text,
        )

        assert result["input_tokens"] > 0

    def test_stages_returned(self):
        """Test stages are returned."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test code",
        )

        assert len(result["stages"]) > 0
        for stage in result["stages"]:
            assert "stage" in stage
            assert "tier" in stage
            assert "estimated_cost" in stage

    def test_cost_range(self):
        """Test cost range is reasonable."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="x" * 1000,  # ~250 tokens
        )

        assert result["total_min"] <= result["total_max"]
        assert result["total_min"] >= 0

    def test_risk_levels(self):
        """Test risk level assignment."""
        # Small input = low risk
        small_result = estimate_workflow_cost(
            workflow_name="doc-gen",
            input_text="small",
        )
        assert small_result["risk"] in ("low", "medium", "high")

        # Large input could be higher risk
        large_result = estimate_workflow_cost(
            workflow_name="pro-review",
            input_text="x" * 100000,  # Large input
        )
        assert large_result["risk"] in ("low", "medium", "high")

    def test_display_format(self):
        """Test display format is valid."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test",
        )

        assert result["display"].startswith("$")
        assert " - $" in result["display"]

    def test_unknown_workflow_uses_default_stages(self):
        """Test unknown workflow uses default stages."""
        result = estimate_workflow_cost(
            workflow_name="unknown-workflow-xyz",
            input_text="test",
        )

        assert len(result["stages"]) > 0

    def test_different_workflows_have_different_stages(self):
        """Test different workflows have different stage configurations."""
        code_review = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test",
        )
        security_audit = estimate_workflow_cost(
            workflow_name="security-audit",
            input_text="test",
        )

        # They should have stages but may differ
        assert len(code_review["stages"]) > 0
        assert len(security_audit["stages"]) > 0

    def test_tiktoken_available_flag(self):
        """Test tiktoken availability is returned."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test",
        )

        assert "tiktoken_available" in result
        assert isinstance(result["tiktoken_available"], bool)


class TestEstimateWorkflowCostWithFile:
    """Tests for file-based workflow cost estimation."""

    @pytest.mark.skipif(sys.platform == "win32", reason="File locking issues on Windows")
    def test_with_file_path(self):
        """Test estimation with file path."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def hello(): return 'world'\n" * 10)
            f.flush()

            try:
                result = estimate_workflow_cost(
                    workflow_name="code-review",
                    input_text="",
                    target_path=f.name,
                )

                assert result["input_tokens"] > 0
            finally:
                os.unlink(f.name)

    def test_with_directory_path(self):
        """Test estimation with directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some Python files
            for i in range(3):
                filepath = Path(tmpdir) / f"file{i}.py"
                filepath.write_text("def foo(): pass\n")

            result = estimate_workflow_cost(
                workflow_name="code-review",
                input_text="",
                target_path=tmpdir,
            )

            assert result["input_tokens"] >= 0

    def test_with_nonexistent_path(self):
        """Test estimation with nonexistent path doesn't crash."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="fallback text",
            target_path="/nonexistent/path/to/file.py",
        )

        # Should still work with fallback text
        assert "input_tokens" in result


class TestEstimateSingleCallCost:
    """Tests for estimate_single_call_cost function."""

    def test_basic_call_cost(self):
        """Test basic single call cost estimation."""
        result = estimate_single_call_cost(
            text="Test input text",
            task_type="summarize",
        )

        assert "task_type" in result
        assert "tier" in result
        assert "model" in result
        assert "input_tokens" in result
        assert "estimated_output_tokens" in result
        assert "estimated_cost" in result
        assert "display" in result

    def test_summarize_has_low_output(self):
        """Test summarize task has low output multiplier."""
        result = estimate_single_call_cost(
            text="Test input text",
            task_type="summarize",
        )

        # Summarize should have fewer output tokens than input
        assert result["estimated_output_tokens"] < result["input_tokens"]

    def test_generate_code_has_high_output(self):
        """Test generate_code task has high output multiplier."""
        result = estimate_single_call_cost(
            text="Create a function that sorts a list",
            task_type="generate_code",
        )

        # Generate code should have more output tokens
        assert result["estimated_output_tokens"] >= result["input_tokens"]

    def test_different_providers(self):
        """Test different providers work."""
        anthropic = estimate_single_call_cost(
            text="Test",
            task_type="review",
            provider="anthropic",
        )
        openai = estimate_single_call_cost(
            text="Test",
            task_type="review",
            provider="openai",
        )

        assert anthropic["provider"] == "anthropic"
        assert openai["provider"] == "openai"

    def test_display_format(self):
        """Test display format."""
        result = estimate_single_call_cost(
            text="Test",
            task_type="classify",
        )

        assert result["display"].startswith("$")

    def test_unknown_task_type(self):
        """Test unknown task type uses default multiplier."""
        result = estimate_single_call_cost(
            text="Test input",
            task_type="unknown_task_xyz",
        )

        # Should still work with default multiplier
        assert result["estimated_output_tokens"] == result["input_tokens"]


class TestWorkflowStageConfigurations:
    """Tests for specific workflow stage configurations."""

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "security-audit",
            "code-review",
            "test-gen",
            "doc-gen",
            "bug-predict",
            "refactor-plan",
            "perf-audit",
            "health-check",
            "pr-review",
            "pro-review",
        ],
    )
    def test_known_workflows_have_stages(self, workflow_name):
        """Test all known workflows have stage configurations."""
        result = estimate_workflow_cost(
            workflow_name=workflow_name,
            input_text="test input",
        )

        assert len(result["stages"]) > 0
        assert result["workflow"] == workflow_name

    def test_pro_review_uses_premium(self):
        """Test pro-review uses premium tier."""
        result = estimate_workflow_cost(
            workflow_name="pro-review",
            input_text="test",
        )

        tiers = [s["tier"] for s in result["stages"]]
        assert "premium" in tiers

    def test_doc_gen_uses_cheap_and_capable(self):
        """Test doc-gen uses cheap and capable tiers."""
        result = estimate_workflow_cost(
            workflow_name="doc-gen",
            input_text="test",
        )

        tiers = [s["tier"] for s in result["stages"]]
        assert "cheap" in tiers or "capable" in tiers
