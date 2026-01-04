"""Cost Tracking for Empathy Framework

Tracks API costs across model tiers and calculates savings from
smart model routing (Haiku/Sonnet/Opus selection).

Features:
- Log each API request with model, tokens, and task type
- Calculate actual cost vs baseline (if all requests used premium model)
- Generate weekly/monthly reports
- Integrate with `empathy costs` and `empathy morning` commands

Model pricing is sourced from empathy_os.models.MODEL_REGISTRY.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Import pricing from unified registry
from empathy_os.models import MODEL_REGISTRY
from empathy_os.models.registry import TIER_PRICING


def _build_model_pricing() -> dict[str, dict[str, float]]:
    """Build MODEL_PRICING from unified registry."""
    pricing: dict[str, dict[str, float]] = {}

    # Add all models from registry
    for provider_models in MODEL_REGISTRY.values():
        for model_info in provider_models.values():
            pricing[model_info.id] = {
                "input": model_info.input_cost_per_million,
                "output": model_info.output_cost_per_million,
            }

    # Add tier aliases from registry
    pricing.update(TIER_PRICING)

    # Add legacy model names for backward compatibility
    legacy_models = {
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }
    pricing.update(legacy_models)

    return pricing


# Pricing per million tokens - sourced from unified registry
MODEL_PRICING = _build_model_pricing()

# Default premium model for baseline comparison
BASELINE_MODEL = "claude-opus-4-5-20251101"


class CostTracker:
    """Tracks API costs and calculates savings from model routing.

    Usage:
        tracker = CostTracker()
        tracker.log_request("claude-3-haiku-20240307", 1000, 500, "summarize")
        report = tracker.get_report()
    """

    def __init__(self, storage_dir: str = ".empathy"):
        """Initialize cost tracker.

        Args:
            storage_dir: Directory for cost data storage

        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.costs_file = self.storage_dir / "costs.json"
        self._load()

    def _load(self) -> None:
        """Load cost data from storage."""
        if self.costs_file.exists():
            try:
                with open(self.costs_file) as f:
                    self.data = json.load(f)
            except (OSError, json.JSONDecodeError):
                self.data = self._default_data()
        else:
            self.data = self._default_data()

    def _default_data(self) -> dict:
        """Return default data structure."""
        return {
            "requests": [],
            "daily_totals": {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

    def _save(self) -> None:
        """Save cost data to storage."""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.costs_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request.

        Args:
            model: Model name or tier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD

        """
        pricing = MODEL_PRICING.get(model) or MODEL_PRICING["capable"]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def log_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_type: str = "unknown",
        tier: str | None = None,
    ) -> dict:
        """Log an API request with cost tracking.

        Args:
            model: Model name used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            task_type: Type of task (summarize, generate_code, etc.)
            tier: Optional tier override (cheap, capable, premium)

        Returns:
            Request record with cost information

        """
        actual_cost = self._calculate_cost(model, input_tokens, output_tokens)
        baseline_cost = self._calculate_cost(BASELINE_MODEL, input_tokens, output_tokens)
        savings = baseline_cost - actual_cost

        request = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tier": tier or self._get_tier(model),
            "task_type": task_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "actual_cost": round(actual_cost, 6),
            "baseline_cost": round(baseline_cost, 6),
            "savings": round(savings, 6),
        }

        self.data["requests"].append(request)

        # Update daily totals
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.data["daily_totals"]:
            self.data["daily_totals"][today] = {
                "requests": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "actual_cost": 0,
                "baseline_cost": 0,
                "savings": 0,
            }

        daily = self.data["daily_totals"][today]
        daily["requests"] += 1
        daily["input_tokens"] += input_tokens
        daily["output_tokens"] += output_tokens
        daily["actual_cost"] = round(daily["actual_cost"] + actual_cost, 6)
        daily["baseline_cost"] = round(daily["baseline_cost"] + baseline_cost, 6)
        daily["savings"] = round(daily["savings"] + savings, 6)

        # Keep only last 1000 requests in detail
        if len(self.data["requests"]) > 1000:
            self.data["requests"] = self.data["requests"][-1000:]

        self._save()
        return request

    def _get_tier(self, model: str) -> str:
        """Determine tier from model name."""
        if "haiku" in model.lower():
            return "cheap"
        if "opus" in model.lower():
            return "premium"
        return "capable"

    def get_summary(self, days: int = 7) -> dict:
        """Get cost summary for recent period.

        Args:
            days: Number of days to include

        Returns:
            Summary with totals and savings percentage

        """
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        totals: dict[str, Any] = {
            "days": days,
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "actual_cost": 0,
            "baseline_cost": 0,
            "savings": 0,
            "by_tier": {"cheap": 0, "capable": 0, "premium": 0},
            "by_task": {},
        }

        for date, daily in self.data.get("daily_totals", {}).items():
            if date >= cutoff_str:
                totals["requests"] += daily["requests"]
                totals["input_tokens"] += daily["input_tokens"]
                totals["output_tokens"] += daily["output_tokens"]
                totals["actual_cost"] += daily["actual_cost"]
                totals["baseline_cost"] += daily["baseline_cost"]
                totals["savings"] += daily["savings"]

        # Count by tier and task from recent requests
        cutoff_iso = cutoff.isoformat()
        for req in self.data.get("requests", []):
            if req["timestamp"] >= cutoff_iso:
                tier = req.get("tier", "capable")
                task = req.get("task_type", "unknown")
                totals["by_tier"][tier] = totals["by_tier"].get(tier, 0) + 1
                totals["by_task"][task] = totals["by_task"].get(task, 0) + 1

        # Calculate savings percentage
        if totals["baseline_cost"] > 0:
            totals["savings_percent"] = round(
                (totals["savings"] / totals["baseline_cost"]) * 100,
                1,
            )
        else:
            totals["savings_percent"] = 0

        return totals

    def get_report(self, days: int = 7) -> str:
        """Generate a formatted cost report.

        Args:
            days: Number of days to include

        Returns:
            Formatted report string

        """
        summary = self.get_summary(days)

        lines = [
            "",
            "=" * 60,
            "  COST TRACKING REPORT",
            f"  Last {days} days",
            "=" * 60,
            "",
            "SUMMARY",
            "-" * 40,
            f"  Total requests:      {summary['requests']:,}",
            f"  Input tokens:        {summary['input_tokens']:,}",
            f"  Output tokens:       {summary['output_tokens']:,}",
            "",
            "COSTS",
            "-" * 40,
            f"  Actual cost:         ${summary['actual_cost']:.4f}",
            f"  Baseline (Opus):     ${summary['baseline_cost']:.4f}",
            f"  You saved:           ${summary['savings']:.4f} ({summary['savings_percent']}%)",
            "",
        ]

        # Tier breakdown
        if sum(summary["by_tier"].values()) > 0:
            lines.extend(
                [
                    "BY MODEL TIER",
                    "-" * 40,
                ],
            )
            for tier, count in sorted(summary["by_tier"].items(), key=lambda x: -x[1]):
                if count > 0:
                    pct = (count / summary["requests"]) * 100 if summary["requests"] else 0
                    lines.append(f"  {tier:12} {count:6,} requests ({pct:.1f}%)")
            lines.append("")

        # Task breakdown (top 5)
        if summary["by_task"]:
            lines.extend(
                [
                    "BY TASK TYPE (Top 5)",
                    "-" * 40,
                ],
            )
            sorted_tasks = sorted(summary["by_task"].items(), key=lambda x: -x[1])[:5]
            for task, count in sorted_tasks:
                lines.append(f"  {task:20} {count:,}")
            lines.append("")

        lines.extend(
            [
                "=" * 60,
                "  Model routing saves money by using cheaper models",
                "  for simple tasks and Opus only when needed.",
                "=" * 60,
                "",
            ],
        )

        return "\n".join(lines)

    def get_today(self) -> dict[str, int | float]:
        """Get today's cost summary."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_totals = self.data.get("daily_totals", {})
        default: dict[str, int | float] = {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "actual_cost": 0,
            "baseline_cost": 0,
            "savings": 0,
        }
        if isinstance(daily_totals, dict) and today in daily_totals:
            result = daily_totals[today]
            return result if isinstance(result, dict) else default
        return default


def cmd_costs(args):
    """CLI command handler for costs."""
    tracker = CostTracker(storage_dir=getattr(args, "empathy_dir", ".empathy"))
    days = getattr(args, "days", 7)

    if getattr(args, "json", False):
        import json as json_mod

        print(json_mod.dumps(tracker.get_summary(days), indent=2))
    else:
        print(tracker.get_report(days))

    return 0


# Singleton for global tracking
_tracker: CostTracker | None = None


def get_tracker(storage_dir: str = ".empathy") -> CostTracker:
    """Get or create the global cost tracker."""
    global _tracker
    if _tracker is None:
        _tracker = CostTracker(storage_dir)
    return _tracker


def log_request(
    model: str,
    input_tokens: int,
    output_tokens: int,
    task_type: str = "unknown",
    tier: str | None = None,
) -> dict:
    """Convenience function to log a request to the global tracker.

    Usage:
        from empathy_os.cost_tracker import log_request
        log_request("claude-3-haiku-20240307", 1000, 500, "summarize")
    """
    return get_tracker().log_request(model, input_tokens, output_tokens, task_type, tier)
