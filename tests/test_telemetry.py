"""Tests for Multi-Model Telemetry Module

Tests the telemetry storage and analytics functionality:
- LLMCallRecord and WorkflowRunRecord dataclasses
- TelemetryStore persistence
- TelemetryAnalytics queries and reports

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from empathy_os.models.telemetry import (
    LLMCallRecord,
    TelemetryAnalytics,
    TelemetryStore,
    WorkflowRunRecord,
    WorkflowStageRecord,
)


class TestLLMCallRecord:
    """Tests for LLMCallRecord dataclass."""

    def test_create_record(self):
        """Test creating an LLM call record."""
        record = LLMCallRecord(
            call_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            workflow_name="test_workflow",
            step_name="analysis",
            task_type="summarize",
            provider="anthropic",
            tier="cheap",
            model_id="claude-3-5-haiku-20241022",
            input_tokens=1000,
            output_tokens=200,
            estimated_cost=0.0012,
            latency_ms=500,
        )

        assert record.workflow_name == "test_workflow"
        assert record.tier == "cheap"
        assert record.estimated_cost == 0.0012

    def test_to_dict(self):
        """Test converting record to dictionary."""
        now = datetime.now().isoformat()
        record = LLMCallRecord(
            call_id="test-123",
            timestamp=now,
            workflow_name="test",
            step_name="step1",
            task_type="classify",
            provider="anthropic",
            tier="cheap",
            model_id="claude-3-5-haiku-20241022",
            input_tokens=500,
            output_tokens=100,
            estimated_cost=0.0006,
            latency_ms=300,
        )

        d = record.to_dict()
        assert d["workflow_name"] == "test"
        assert d["timestamp"] == now
        assert d["input_tokens"] == 500

    def test_from_dict(self):
        """Test creating record from dictionary."""
        data = {
            "call_id": "call-456",
            "timestamp": "2025-01-15T10:30:00",
            "workflow_name": "analysis",
            "step_name": "triage",
            "task_type": "triage",
            "provider": "openai",
            "tier": "cheap",
            "model_id": "gpt-4o-mini",
            "input_tokens": 800,
            "output_tokens": 150,
            "estimated_cost": 0.001,
            "latency_ms": 400,
        }

        record = LLMCallRecord.from_dict(data)
        assert record.workflow_name == "analysis"
        assert record.provider == "openai"
        assert record.input_tokens == 800

    def test_optional_metadata(self):
        """Test record with optional metadata."""
        record = LLMCallRecord(
            call_id="test-789",
            timestamp=datetime.now().isoformat(),
            workflow_name="test",
            step_name="step1",
            task_type="fix_bug",
            provider="anthropic",
            tier="capable",
            model_id="claude-sonnet-4-20250514",
            input_tokens=2000,
            output_tokens=500,
            estimated_cost=0.015,
            latency_ms=1500,
            fallback_used=True,
            original_provider="openai",
            error_message=None,
            metadata={"user_id": "test123"},
        )

        assert record.fallback_used is True
        assert record.original_provider == "openai"
        assert record.metadata["user_id"] == "test123"


class TestWorkflowRunRecord:
    """Tests for WorkflowRunRecord dataclass."""

    def test_create_workflow_record(self):
        """Test creating a workflow run record."""
        record = WorkflowRunRecord(
            run_id="run-001",
            workflow_name="code_review",
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            total_cost=0.05,
            total_input_tokens=5000,
            total_output_tokens=1500,
            success=True,
        )

        assert record.workflow_name == "code_review"
        assert record.total_cost == 0.05

    def test_workflow_with_error(self):
        """Test workflow record with error."""
        record = WorkflowRunRecord(
            run_id="run-002",
            workflow_name="deploy",
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            total_cost=0.02,
            total_input_tokens=2000,
            total_output_tokens=400,
            success=False,
            error="Rate limit exceeded",
        )

        assert record.success is False
        assert record.error == "Rate limit exceeded"

    def test_workflow_to_dict(self):
        """Test workflow record serialization."""
        now = datetime.now().isoformat()
        record = WorkflowRunRecord(
            run_id="run-003",
            workflow_name="test",
            started_at=now,
            completed_at=now,
            total_cost=0.01,
            total_input_tokens=1000,
            total_output_tokens=200,
            success=True,
        )

        d = record.to_dict()
        assert "workflow_name" in d
        assert "started_at" in d
        assert d["success"] is True

    def test_workflow_with_stages(self):
        """Test workflow with stage records."""
        stage = WorkflowStageRecord(
            stage_name="triage",
            tier="cheap",
            model_id="claude-3-5-haiku",
            input_tokens=500,
            output_tokens=100,
            cost=0.005,
        )

        record = WorkflowRunRecord(
            run_id="run-004",
            workflow_name="test",
            started_at=datetime.now().isoformat(),
            stages=[stage],
            total_cost=0.005,
        )

        assert len(record.stages) == 1
        assert record.stages[0].stage_name == "triage"


class TestTelemetryStore:
    """Tests for TelemetryStore persistence."""

    @pytest.fixture
    def temp_store(self):
        """Create a temporary telemetry store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = TelemetryStore(storage_dir=tmpdir)
            yield store

    def test_store_llm_call(self, temp_store):
        """Test storing an LLM call record."""
        record = LLMCallRecord(
            call_id="call-001",
            timestamp=datetime.now().isoformat(),
            workflow_name="test",
            step_name="step1",
            task_type="summarize",
            provider="anthropic",
            tier="cheap",
            model_id="claude-3-5-haiku-20241022",
            input_tokens=500,
            output_tokens=100,
            estimated_cost=0.0006,
            latency_ms=300,
        )

        temp_store.log_call(record)

        # Verify file was created
        calls_file = Path(temp_store.storage_dir) / "llm_calls.jsonl"
        assert calls_file.exists()

        # Verify content
        with open(calls_file) as f:
            line = f.readline()
            data = json.loads(line)
            assert data["workflow_name"] == "test"

    def test_store_workflow_run(self, temp_store):
        """Test storing a workflow run record."""
        record = WorkflowRunRecord(
            run_id="run-001",
            workflow_name="analysis",
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            total_cost=0.03,
            total_input_tokens=3000,
            total_output_tokens=600,
            success=True,
        )

        temp_store.log_workflow(record)

        # Verify file was created
        runs_file = Path(temp_store.storage_dir) / "workflow_runs.jsonl"
        assert runs_file.exists()

    def test_get_calls_by_workflow(self, temp_store):
        """Test retrieving calls filtered by workflow."""
        # Store multiple records
        for i, workflow in enumerate(["workflow_a", "workflow_b", "workflow_a"]):
            record = LLMCallRecord(
                call_id=f"call-{i}",
                timestamp=datetime.now().isoformat(),
                workflow_name=workflow,
                step_name=f"step{i}",
                task_type="summarize",
                provider="anthropic",
                tier="cheap",
                model_id="claude-3-5-haiku-20241022",
                input_tokens=500,
                output_tokens=100,
                estimated_cost=0.0006,
                latency_ms=300,
            )
            temp_store.log_call(record)

        # Query
        calls = temp_store.get_calls(workflow_name="workflow_a")
        assert len(calls) == 2

    def test_get_calls_by_time_range(self, temp_store):
        """Test retrieving calls within time range."""
        now = datetime.now()
        timestamps = [
            now - timedelta(hours=2),
            now - timedelta(hours=1),
            now,
        ]

        for i, ts in enumerate(timestamps):
            record = LLMCallRecord(
                call_id=f"call-{i}",
                timestamp=ts.isoformat(),
                workflow_name="test",
                step_name=f"step{i}",
                task_type="summarize",
                provider="anthropic",
                tier="cheap",
                model_id="test-model",
                input_tokens=500,
                output_tokens=100,
                estimated_cost=0.0006,
                latency_ms=300,
            )
            temp_store.log_call(record)

        # Get calls from last 90 minutes
        since = now - timedelta(minutes=90)
        calls = temp_store.get_calls(since=since)
        assert len(calls) == 2  # Last two records

    def test_get_workflow_runs(self, temp_store):
        """Test retrieving workflow runs."""
        for i in range(3):
            record = WorkflowRunRecord(
                run_id=f"run-{i}",
                workflow_name=f"workflow_{i}",
                started_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat(),
                total_cost=0.01 * (i + 1),
                total_input_tokens=1000,
                total_output_tokens=200,
                success=True,
            )
            temp_store.log_workflow(record)

        runs = temp_store.get_workflows()
        assert len(runs) == 3


class TestTelemetryAnalytics:
    """Tests for TelemetryAnalytics queries."""

    @pytest.fixture
    def analytics_with_data(self):
        """Create analytics with sample data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = TelemetryStore(storage_dir=tmpdir)

            # Add sample LLM calls
            workflows = ["code_review", "code_review", "deploy", "analysis"]
            providers = ["anthropic", "openai", "anthropic", "anthropic"]
            costs = [0.05, 0.03, 0.02, 0.08]
            tiers = ["capable", "capable", "cheap", "premium"]

            for i, (wf, prov, cost, tier) in enumerate(
                zip(workflows, providers, costs, tiers, strict=False),
            ):
                record = LLMCallRecord(
                    call_id=f"call-{i}",
                    timestamp=datetime.now().isoformat(),
                    workflow_name=wf,
                    step_name=f"step{i}",
                    task_type="fix_bug" if tier == "capable" else "summarize",
                    provider=prov,
                    tier=tier,
                    model_id="test-model",
                    input_tokens=1000 * (i + 1),
                    output_tokens=200 * (i + 1),
                    estimated_cost=cost,
                    latency_ms=500 * (i + 1),
                    fallback_used=(i == 1),  # One fallback
                )
                store.log_call(record)

            # Add workflow runs
            for i, (wf, cost) in enumerate(
                [("code_review", 0.08), ("deploy", 0.02), ("analysis", 0.08)],
            ):
                run = WorkflowRunRecord(
                    run_id=f"run-{i}",
                    workflow_name=wf,
                    started_at=datetime.now().isoformat(),
                    completed_at=datetime.now().isoformat(),
                    total_cost=cost,
                    baseline_cost=cost * 2,  # Pretend premium would cost 2x
                    savings=cost,
                    total_input_tokens=3000,
                    total_output_tokens=600,
                    success=True,
                )
                store.log_workflow(run)

            analytics = TelemetryAnalytics(store)
            yield analytics

    def test_top_expensive_workflows(self, analytics_with_data):
        """Test getting most expensive workflows."""
        top = analytics_with_data.top_expensive_workflows(n=2)

        assert len(top) <= 2
        # code_review and analysis should be most expensive
        workflow_names = [w["workflow_name"] for w in top]
        assert "code_review" in workflow_names or "analysis" in workflow_names

    def test_provider_usage_summary(self, analytics_with_data):
        """Test provider usage summary."""
        summary = analytics_with_data.provider_usage_summary()

        assert "anthropic" in summary
        assert "openai" in summary
        assert summary["anthropic"]["call_count"] == 3
        assert summary["openai"]["call_count"] == 1

    def test_fallback_stats(self, analytics_with_data):
        """Test fallback statistics."""
        stats = analytics_with_data.fallback_stats()

        assert stats["total_calls"] == 4
        assert stats["fallback_count"] == 1
        assert stats["fallback_percent"] == 25.0  # 1/4 * 100

    def test_cost_savings_report(self, analytics_with_data):
        """Test cost savings report."""
        report = analytics_with_data.cost_savings_report()

        assert "total_actual_cost" in report
        assert "total_baseline_cost" in report
        assert "total_savings" in report
        assert report["total_actual_cost"] > 0

    def test_tier_distribution(self, analytics_with_data):
        """Test tier distribution analytics."""
        dist = analytics_with_data.tier_distribution()

        assert "cheap" in dist
        assert "capable" in dist
        assert "premium" in dist
        assert dist["capable"]["count"] == 2

    def test_empty_store_analytics(self):
        """Test analytics with empty store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = TelemetryStore(storage_dir=tmpdir)
            analytics = TelemetryAnalytics(store)

            # Should handle empty data gracefully
            top = analytics.top_expensive_workflows()
            assert top == []

            summary = analytics.provider_usage_summary()
            assert summary == {}

            stats = analytics.fallback_stats()
            assert stats["total_calls"] == 0
            assert stats["fallback_percent"] == 0
