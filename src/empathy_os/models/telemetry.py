"""
Structured Telemetry for Multi-Model Workflows

Provides normalized schemas for tracking LLM calls and workflow runs:
- LLMCallRecord: Per-call metrics (model, tokens, cost, latency)
- WorkflowRunRecord: Per-workflow metrics (stages, total cost, duration)
- TelemetryBackend: Abstract interface for telemetry storage
- TelemetryStore: JSONL file-based backend (default)
- Analytics helpers for cost analysis and optimization

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class LLMCallRecord:
    """
    Record of a single LLM API call.

    Captures all relevant metrics for cost tracking, performance analysis,
    and debugging.
    """

    # Identification
    call_id: str
    timestamp: str  # ISO format

    # Context
    workflow_name: str | None = None
    step_name: str | None = None
    user_id: str | None = None
    session_id: str | None = None

    # Task routing
    task_type: str = "unknown"
    provider: str = "anthropic"
    tier: str = "capable"
    model_id: str = ""

    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0

    # Cost (in USD)
    estimated_cost: float = 0.0
    actual_cost: float | None = None

    # Performance
    latency_ms: int = 0

    # Fallback and resilience tracking
    fallback_used: bool = False
    fallback_chain: list[str] = field(default_factory=list)
    original_provider: str | None = None
    original_model: str | None = None
    retry_count: int = 0  # Number of retries before success
    circuit_breaker_state: str | None = None  # "closed", "open", "half-open"

    # Error tracking
    success: bool = True
    error_type: str | None = None
    error_message: str | None = None

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMCallRecord":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WorkflowStageRecord:
    """Record of a single workflow stage execution."""

    stage_name: str
    tier: str
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    latency_ms: int = 0
    success: bool = True
    skipped: bool = False
    skip_reason: str | None = None
    error: str | None = None


@dataclass
class WorkflowRunRecord:
    """
    Record of a complete workflow execution.

    Aggregates stage-level metrics and provides workflow-level analytics.
    """

    # Identification
    run_id: str
    workflow_name: str
    started_at: str  # ISO format
    completed_at: str | None = None

    # Context
    user_id: str | None = None
    session_id: str | None = None

    # Stages
    stages: list[WorkflowStageRecord] = field(default_factory=list)

    # Aggregated metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    baseline_cost: float = 0.0  # If all stages used premium
    savings: float = 0.0
    savings_percent: float = 0.0

    # Performance
    total_duration_ms: int = 0

    # Status
    success: bool = True
    error: str | None = None

    # Provider usage
    providers_used: list[str] = field(default_factory=list)
    tiers_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["stages"] = [asdict(s) for s in self.stages]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowRunRecord":
        """Create from dictionary."""
        stages = [WorkflowStageRecord(**s) for s in data.pop("stages", [])]
        return cls(stages=stages, **data)


@runtime_checkable
class TelemetryBackend(Protocol):
    """
    Protocol for telemetry storage backends.

    Implementations can store telemetry data in different backends:
    - JSONL files (default, via TelemetryStore)
    - Database (PostgreSQL, SQLite, etc.)
    - Cloud services (DataDog, New Relic, etc.)
    - Custom backends

    Example implementing a custom backend:
        >>> class DatabaseBackend:
        ...     def log_call(self, record: LLMCallRecord) -> None:
        ...         # Insert into database
        ...         pass
        ...
        ...     def log_workflow(self, record: WorkflowRunRecord) -> None:
        ...         # Insert into database
        ...         pass
        ...
        ...     def get_calls(self, since=None, workflow_name=None, limit=1000):
        ...         # Query database
        ...         return []
        ...
        ...     def get_workflows(self, since=None, workflow_name=None, limit=100):
        ...         # Query database
        ...         return []
    """

    def log_call(self, record: LLMCallRecord) -> None:
        """Log an LLM call record."""
        ...

    def log_workflow(self, record: WorkflowRunRecord) -> None:
        """Log a workflow run record."""
        ...

    def get_calls(
        self,
        since: datetime | None = None,
        workflow_name: str | None = None,
        limit: int = 1000,
    ) -> list[LLMCallRecord]:
        """Get LLM call records with optional filters."""
        ...

    def get_workflows(
        self,
        since: datetime | None = None,
        workflow_name: str | None = None,
        limit: int = 100,
    ) -> list[WorkflowRunRecord]:
        """Get workflow run records with optional filters."""
        ...


class TelemetryStore:
    """
    JSONL file-based telemetry backend (default implementation).

    Stores records in JSONL format for easy streaming and analysis.
    Implements the TelemetryBackend protocol.
    """

    def __init__(self, storage_dir: str = ".empathy"):
        """
        Initialize telemetry store.

        Args:
            storage_dir: Directory for telemetry files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.calls_file = self.storage_dir / "llm_calls.jsonl"
        self.workflows_file = self.storage_dir / "workflow_runs.jsonl"

    def log_call(self, record: LLMCallRecord) -> None:
        """Log an LLM call record."""
        with open(self.calls_file, "a") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def log_workflow(self, record: WorkflowRunRecord) -> None:
        """Log a workflow run record."""
        with open(self.workflows_file, "a") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def get_calls(
        self,
        since: datetime | None = None,
        workflow_name: str | None = None,
        limit: int = 1000,
    ) -> list[LLMCallRecord]:
        """
        Get LLM call records.

        Args:
            since: Only return records after this time
            workflow_name: Filter by workflow name
            limit: Maximum records to return

        Returns:
            List of LLMCallRecord
        """
        records: list[LLMCallRecord] = []
        if not self.calls_file.exists():
            return records

        with open(self.calls_file) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    record = LLMCallRecord.from_dict(data)

                    # Apply filters
                    if since:
                        record_time = datetime.fromisoformat(record.timestamp)
                        if record_time < since:
                            continue

                    if workflow_name and record.workflow_name != workflow_name:
                        continue

                    records.append(record)

                    if len(records) >= limit:
                        break
                except (json.JSONDecodeError, KeyError):
                    continue

        return records

    def get_workflows(
        self,
        since: datetime | None = None,
        workflow_name: str | None = None,
        limit: int = 100,
    ) -> list[WorkflowRunRecord]:
        """
        Get workflow run records.

        Args:
            since: Only return records after this time
            workflow_name: Filter by workflow name
            limit: Maximum records to return

        Returns:
            List of WorkflowRunRecord
        """
        records: list[WorkflowRunRecord] = []
        if not self.workflows_file.exists():
            return records

        with open(self.workflows_file) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    record = WorkflowRunRecord.from_dict(data)

                    # Apply filters
                    if since:
                        record_time = datetime.fromisoformat(record.started_at)
                        if record_time < since:
                            continue

                    if workflow_name and record.workflow_name != workflow_name:
                        continue

                    records.append(record)

                    if len(records) >= limit:
                        break
                except (json.JSONDecodeError, KeyError):
                    continue

        return records


class TelemetryAnalytics:
    """
    Analytics helpers for telemetry data.

    Provides insights into cost optimization, provider usage, and performance.
    """

    def __init__(self, store: TelemetryStore | None = None):
        """
        Initialize analytics.

        Args:
            store: TelemetryStore to analyze (creates default if None)
        """
        self.store = store or TelemetryStore()

    def top_expensive_workflows(
        self,
        n: int = 10,
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get the most expensive workflows.

        Args:
            n: Number of workflows to return
            since: Only consider workflows after this time

        Returns:
            List of dicts with workflow_name, total_cost, run_count
        """
        workflows = self.store.get_workflows(since=since, limit=10000)

        # Aggregate by workflow name
        costs: dict[str, dict[str, Any]] = {}
        for wf in workflows:
            if wf.workflow_name not in costs:
                costs[wf.workflow_name] = {
                    "workflow_name": wf.workflow_name,
                    "total_cost": 0.0,
                    "run_count": 0,
                    "total_savings": 0.0,
                    "avg_duration_ms": 0,
                }
            costs[wf.workflow_name]["total_cost"] += wf.total_cost
            costs[wf.workflow_name]["run_count"] += 1
            costs[wf.workflow_name]["total_savings"] += wf.savings

        # Calculate averages and sort
        result = list(costs.values())
        for item in result:
            if item["run_count"] > 0:
                item["avg_cost"] = item["total_cost"] / item["run_count"]

        result.sort(key=lambda x: x["total_cost"], reverse=True)
        return result[:n]

    def provider_usage_summary(
        self,
        since: datetime | None = None,
    ) -> dict[str, dict[str, Any]]:
        """
        Get usage summary by provider.

        Args:
            since: Only consider calls after this time

        Returns:
            Dict mapping provider to usage stats
        """
        calls = self.store.get_calls(since=since, limit=100000)

        summary: dict[str, dict[str, Any]] = {}
        for call in calls:
            if call.provider not in summary:
                summary[call.provider] = {
                    "call_count": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "error_count": 0,
                    "avg_latency_ms": 0,
                    "by_tier": {"cheap": 0, "capable": 0, "premium": 0},
                }

            s = summary[call.provider]
            s["call_count"] += 1
            s["total_tokens"] += call.input_tokens + call.output_tokens
            s["total_cost"] += call.estimated_cost
            if not call.success:
                s["error_count"] += 1
            if call.tier in s["by_tier"]:
                s["by_tier"][call.tier] += 1

        # Calculate averages
        for _provider, stats in summary.items():
            if stats["call_count"] > 0:
                stats["avg_cost"] = stats["total_cost"] / stats["call_count"]

        return summary

    def tier_distribution(
        self,
        since: datetime | None = None,
    ) -> dict[str, dict[str, Any]]:
        """
        Get call distribution by tier.

        Args:
            since: Only consider calls after this time

        Returns:
            Dict mapping tier to stats
        """
        calls = self.store.get_calls(since=since, limit=100000)

        dist: dict[str, dict[str, Any]] = {
            "cheap": {"count": 0, "cost": 0.0, "tokens": 0},
            "capable": {"count": 0, "cost": 0.0, "tokens": 0},
            "premium": {"count": 0, "cost": 0.0, "tokens": 0},
        }

        for call in calls:
            if call.tier in dist:
                dist[call.tier]["count"] += 1
                dist[call.tier]["cost"] += call.estimated_cost
                dist[call.tier]["tokens"] += call.input_tokens + call.output_tokens

        total_calls = sum(d["count"] for d in dist.values())
        for _tier, stats in dist.items():
            stats["percent"] = (stats["count"] / total_calls * 100) if total_calls > 0 else 0

        return dist

    def fallback_stats(
        self,
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get fallback usage statistics.

        Args:
            since: Only consider calls after this time

        Returns:
            Dict with fallback stats
        """
        calls = self.store.get_calls(since=since, limit=100000)

        total = len(calls)
        fallback_count = sum(1 for c in calls if c.fallback_used)
        error_count = sum(1 for c in calls if not c.success)

        # Count by original provider
        by_provider: dict[str, int] = {}
        for call in calls:
            if call.fallback_used and call.original_provider:
                by_provider[call.original_provider] = by_provider.get(call.original_provider, 0) + 1

        return {
            "total_calls": total,
            "fallback_count": fallback_count,
            "fallback_percent": (fallback_count / total * 100) if total > 0 else 0,
            "error_count": error_count,
            "error_rate": (error_count / total * 100) if total > 0 else 0,
            "by_original_provider": by_provider,
        }

    def cost_savings_report(
        self,
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Generate cost savings report.

        Args:
            since: Only consider workflows after this time

        Returns:
            Dict with savings analysis
        """
        workflows = self.store.get_workflows(since=since, limit=10000)

        total_cost = sum(wf.total_cost for wf in workflows)
        total_baseline = sum(wf.baseline_cost for wf in workflows)
        total_savings = sum(wf.savings for wf in workflows)

        return {
            "workflow_count": len(workflows),
            "total_actual_cost": total_cost,
            "total_baseline_cost": total_baseline,
            "total_savings": total_savings,
            "savings_percent": (
                (total_savings / total_baseline * 100) if total_baseline > 0 else 0
            ),
            "avg_cost_per_workflow": total_cost / len(workflows) if workflows else 0,
        }


# Singleton for global telemetry
_telemetry_store: TelemetryStore | None = None


def get_telemetry_store(storage_dir: str = ".empathy") -> TelemetryStore:
    """Get or create the global telemetry store."""
    global _telemetry_store
    if _telemetry_store is None:
        _telemetry_store = TelemetryStore(storage_dir)
    return _telemetry_store


def log_llm_call(record: LLMCallRecord) -> None:
    """Convenience function to log an LLM call."""
    get_telemetry_store().log_call(record)


def log_workflow_run(record: WorkflowRunRecord) -> None:
    """Convenience function to log a workflow run."""
    get_telemetry_store().log_workflow(record)
