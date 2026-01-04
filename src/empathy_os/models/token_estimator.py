"""Token Estimation Service

Pre-flight token estimation for cost prediction using tiktoken.
Provides accurate token counts before workflow execution.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from __future__ import annotations

import functools
from typing import Any

# Try to import tiktoken, fall back to heuristic if not available
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


# Heuristic fallback: ~4 tokens per word, ~0.25 tokens per character
TOKENS_PER_CHAR_HEURISTIC = 0.25


@functools.lru_cache(maxsize=4)
def _get_encoding(model_id: str) -> Any:
    """Get tiktoken encoding for a model, with caching."""
    if not TIKTOKEN_AVAILABLE:
        return None

    # Map model IDs to encoding names
    if "claude" in model_id.lower() or "anthropic" in model_id.lower():
        # Claude uses cl100k_base-like encoding
        return tiktoken.get_encoding("cl100k_base")
    if "gpt-4" in model_id.lower() or "gpt-3.5" in model_id.lower() or "o1" in model_id.lower():
        return tiktoken.encoding_for_model("gpt-4")
    # Default to cl100k_base for unknown models
    return tiktoken.get_encoding("cl100k_base")


def estimate_tokens(text: str, model_id: str = "claude-sonnet-4-5-20250514") -> int:
    """Estimate token count for text.

    Uses tiktoken for accurate counting, falls back to heuristic if unavailable.

    Args:
        text: The text to count tokens for
        model_id: The model ID to use for encoding selection

    Returns:
        Estimated token count

    """
    if not text:
        return 0

    if TIKTOKEN_AVAILABLE:
        try:
            encoding = _get_encoding(model_id)
            if encoding:
                return len(encoding.encode(text))
        except Exception:
            pass  # Fall through to heuristic

    # Heuristic fallback
    return max(1, int(len(text) * TOKENS_PER_CHAR_HEURISTIC))


def estimate_workflow_cost(
    workflow_name: str,
    input_text: str,
    provider: str = "anthropic",
    target_path: str | None = None,
) -> dict[str, Any]:
    """Estimate total workflow cost before execution.

    Analyzes workflow stages and estimates token usage and cost for each,
    providing a cost range for the full workflow.

    Args:
        workflow_name: Name of the workflow (e.g., "security-audit", "test-gen")
        input_text: The input text/code to be processed
        provider: LLM provider (anthropic, openai, ollama, hybrid)
        target_path: Optional path for file-based workflows

    Returns:
        Dictionary with cost estimates:
        {
            "workflow": str,
            "provider": str,
            "input_tokens": int,
            "stages": [...],
            "total_min": float,
            "total_max": float,
            "display": str,
            "risk": "low" | "medium" | "high"
        }

    """
    from .registry import get_model, get_supported_providers

    # Validate provider
    if provider not in get_supported_providers():
        provider = "anthropic"  # Default fallback

    # Workflow stage configurations by workflow name
    # Based on actual workflow implementations
    WORKFLOW_STAGES = {
        "security-audit": [
            {"name": "identify_vulnerabilities", "tier": "capable"},
            {"name": "analyze_risk", "tier": "capable"},
            {"name": "generate_report", "tier": "cheap"},
        ],
        "code-review": [
            {"name": "analyze_code", "tier": "capable"},
            {"name": "generate_feedback", "tier": "capable"},
            {"name": "summarize", "tier": "cheap"},
        ],
        "test-gen": [
            {"name": "analyze_code", "tier": "capable"},
            {"name": "generate_tests", "tier": "capable"},
            {"name": "review_tests", "tier": "cheap"},
        ],
        "doc-gen": [
            {"name": "analyze_structure", "tier": "cheap"},
            {"name": "generate_documentation", "tier": "capable"},
        ],
        "bug-predict": [
            {"name": "analyze_patterns", "tier": "capable"},
            {"name": "predict_risks", "tier": "capable"},
        ],
        "refactor-plan": [
            {"name": "identify_issues", "tier": "capable"},
            {"name": "plan_refactoring", "tier": "capable"},
            {"name": "review_plan", "tier": "cheap"},
        ],
        "perf-audit": [
            {"name": "analyze_performance", "tier": "capable"},
            {"name": "identify_bottlenecks", "tier": "capable"},
            {"name": "generate_recommendations", "tier": "cheap"},
        ],
        "health-check": [
            {"name": "scan_codebase", "tier": "cheap"},
            {"name": "analyze_health", "tier": "capable"},
            {"name": "generate_report", "tier": "cheap"},
        ],
        "pr-review": [
            {"name": "analyze_diff", "tier": "capable"},
            {"name": "check_quality", "tier": "capable"},
            {"name": "generate_review", "tier": "capable"},
        ],
        "pro-review": [
            {"name": "deep_analysis", "tier": "premium"},
            {"name": "generate_insights", "tier": "capable"},
        ],
    }

    # Get stage configuration for this workflow
    stages_config = WORKFLOW_STAGES.get(
        workflow_name,
        [
            {"name": "analyze", "tier": "capable"},
            {"name": "generate", "tier": "capable"},
            {"name": "review", "tier": "cheap"},
        ],
    )

    # Estimate input tokens
    input_tokens = estimate_tokens(input_text)

    # If we have a target path, estimate additional content
    if target_path:
        try:
            import os

            if os.path.isfile(target_path):
                with open(target_path, encoding="utf-8", errors="ignore") as f:
                    file_content = f.read()
                input_tokens += estimate_tokens(file_content)
            elif os.path.isdir(target_path):
                # Estimate based on directory size (rough heuristic)
                total_chars = 0
                for root, _, files in os.walk(target_path):
                    for file in files[:50]:  # Limit to first 50 files
                        if file.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
                            try:
                                filepath = os.path.join(root, file)
                                with open(filepath, encoding="utf-8", errors="ignore") as f:
                                    total_chars += len(f.read())
                            except Exception:
                                pass
                input_tokens += int(total_chars * TOKENS_PER_CHAR_HEURISTIC)
        except Exception:
            pass  # Keep original estimate

    # Output multipliers by stage type
    output_multipliers = {
        "identify": 0.3,
        "analyze": 0.8,
        "generate": 2.0,
        "review": 0.5,
        "summarize": 0.3,
        "fix": 1.5,
        "test": 1.5,
        "document": 1.0,
    }

    estimates = []
    total_min = 0.0
    total_max = 0.0

    for stage in stages_config:
        stage_name = stage.get("name", "unknown")
        tier = stage.get("tier", "capable")

        # Get model for this tier
        try:
            model_info = get_model(provider, tier)
        except Exception:
            # Fallback to capable tier
            model_info = get_model(provider, "capable")

        if model_info is None:
            # Skip stage if no model available
            continue

        # Estimate output tokens based on stage type
        multiplier = 1.0
        for stage_type, mult in output_multipliers.items():
            if stage_type in stage_name.lower():
                multiplier = mult
                break

        est_output = int(input_tokens * multiplier)

        # Calculate cost
        cost = (input_tokens / 1_000_000) * model_info.input_cost_per_million + (
            est_output / 1_000_000
        ) * model_info.output_cost_per_million

        estimates.append(
            {
                "stage": stage_name,
                "tier": tier,
                "model": model_info.id,
                "estimated_input_tokens": input_tokens,
                "estimated_output_tokens": est_output,
                "estimated_cost": round(cost, 6),
            },
        )

        # Accumulate with variance (80% - 120%)
        total_min += cost * 0.8
        total_max += cost * 1.2

    # Determine risk level
    if total_max > 1.0:
        risk = "high"
    elif total_max > 0.10:
        risk = "medium"
    else:
        risk = "low"

    return {
        "workflow": workflow_name,
        "provider": provider,
        "input_tokens": input_tokens,
        "stages": estimates,
        "total_min": round(total_min, 4),
        "total_max": round(total_max, 4),
        "display": f"${total_min:.3f} - ${total_max:.3f}",
        "risk": risk,
        "tiktoken_available": TIKTOKEN_AVAILABLE,
    }


def estimate_single_call_cost(
    text: str,
    task_type: str,
    provider: str = "anthropic",
) -> dict[str, Any]:
    """Estimate cost for a single LLM call.

    Args:
        text: Input text
        task_type: Type of task (e.g., "summarize", "generate_code")
        provider: LLM provider

    Returns:
        Cost estimate dictionary

    """
    from .registry import get_model
    from .tasks import get_tier_for_task

    input_tokens = estimate_tokens(text)

    # Get tier for task
    tier = get_tier_for_task(task_type)
    model_info = get_model(provider, tier.value)

    if model_info is None:
        # Return a fallback estimate if no model available
        return {
            "task_type": task_type,
            "tier": tier.value,
            "model": "unknown",
            "provider": provider,
            "input_tokens": input_tokens,
            "estimated_output_tokens": input_tokens,
            "estimated_cost": 0.0,
            "display": "$0.0000",
        }

    # Estimate output based on task type
    output_multipliers = {
        "summarize": 0.3,
        "classify": 0.1,
        "generate_code": 1.5,
        "fix_bug": 1.2,
        "review": 0.5,
        "document": 0.8,
    }

    multiplier = output_multipliers.get(task_type, 1.0)
    est_output = int(input_tokens * multiplier)

    cost = (input_tokens / 1_000_000) * model_info.input_cost_per_million + (
        est_output / 1_000_000
    ) * model_info.output_cost_per_million

    return {
        "task_type": task_type,
        "tier": tier.value,
        "model": model_info.id,
        "provider": provider,
        "input_tokens": input_tokens,
        "estimated_output_tokens": est_output,
        "estimated_cost": round(cost, 6),
        "display": f"${cost:.4f}",
    }


# CLI support
if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Estimate workflow costs")
    parser.add_argument("workflow", help="Workflow name (e.g., security-audit)")
    parser.add_argument("--input", "-i", help="Input text or file path")
    parser.add_argument("--provider", "-p", default="anthropic", help="LLM provider")
    parser.add_argument("--target", "-t", help="Target path for file-based workflows")

    args = parser.parse_args()

    # Read input
    input_text = ""
    if args.input:
        try:
            with open(args.input) as f:
                input_text = f.read()
        except FileNotFoundError:
            input_text = args.input

    result = estimate_workflow_cost(
        workflow_name=args.workflow,
        input_text=input_text,
        provider=args.provider,
        target_path=args.target,
    )

    print(json.dumps(result, indent=2))
    sys.exit(0)
