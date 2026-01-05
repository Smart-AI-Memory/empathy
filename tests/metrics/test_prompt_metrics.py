"""Tests for prompt metrics tracking.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime
from pathlib import Path

import pytest

from empathy_os.metrics.prompt_metrics import MetricsTracker, PromptMetrics


@pytest.fixture
def temp_metrics_file(tmp_path):
    """Create temporary metrics file."""
    return str(tmp_path / "test_metrics.json")


def test_prompt_metrics_creation():
    """Test PromptMetrics dataclass creation."""
    metric = PromptMetrics(
        timestamp=datetime.now().isoformat(),
        workflow="test_workflow",
        agent_role="Test Agent",
        task_description="Test task",
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        latency_ms=1000.0,
        retry_count=0,
        parsing_success=True,
        validation_success=True,
        error_message=None,
        xml_structure_used=True,
    )

    assert metric.workflow == "test_workflow"
    assert metric.total_tokens == 150
    assert metric.xml_structure_used is True


def test_prompt_metrics_to_dict():
    """Test conversion to dictionary."""
    metric = PromptMetrics(
        timestamp=datetime.now().isoformat(),
        workflow="test_workflow",
        agent_role="Test Agent",
        task_description="Test task",
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        latency_ms=1000.0,
        retry_count=0,
        parsing_success=True,
        validation_success=True,
        error_message=None,
        xml_structure_used=True,
    )

    data = metric.to_dict()
    assert data["workflow"] == "test_workflow"
    assert data["total_tokens"] == 150


def test_prompt_metrics_from_dict():
    """Test creation from dictionary."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "workflow": "test_workflow",
        "agent_role": "Test Agent",
        "task_description": "Test task",
        "model": "gpt-4",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "latency_ms": 1000.0,
        "retry_count": 0,
        "parsing_success": True,
        "validation_success": True,
        "error_message": None,
        "xml_structure_used": True,
    }

    metric = PromptMetrics.from_dict(data)
    assert metric.workflow == "test_workflow"
    assert metric.total_tokens == 150


def test_metrics_tracker_initialization(temp_metrics_file):
    """Test MetricsTracker initialization."""
    tracker = MetricsTracker(temp_metrics_file)

    assert tracker.metrics_file.exists()
    assert tracker.metrics_file.read_text() == ""


def test_metrics_tracker_log(temp_metrics_file):
    """Test logging metrics to file."""
    tracker = MetricsTracker(temp_metrics_file)

    metric = PromptMetrics(
        timestamp=datetime.now().isoformat(),
        workflow="test_workflow",
        agent_role="Test Agent",
        task_description="Test task",
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        latency_ms=1000.0,
        retry_count=0,
        parsing_success=True,
        validation_success=True,
        error_message=None,
        xml_structure_used=True,
    )

    tracker.log_metric(metric)

    # Verify file was created and contains data
    assert Path(temp_metrics_file).exists()
    metrics = tracker.get_metrics()
    assert len(metrics) == 1
    assert metrics[0].workflow == "test_workflow"


def test_metrics_tracker_multiple_metrics(temp_metrics_file):
    """Test logging multiple metrics."""
    tracker = MetricsTracker(temp_metrics_file)

    for i in range(5):
        metric = PromptMetrics(
            timestamp=datetime.now().isoformat(),
            workflow=f"workflow_{i}",
            agent_role="Test Agent",
            task_description=f"Test task {i}",
            model="gpt-4",
            prompt_tokens=100 + i,
            completion_tokens=50 + i,
            total_tokens=150 + i,
            latency_ms=1000.0 + i,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=True,
        )
        tracker.log_metric(metric)

    metrics = tracker.get_metrics()
    assert len(metrics) == 5


def test_metrics_tracker_filter_by_workflow(temp_metrics_file):
    """Test filtering metrics by workflow."""
    tracker = MetricsTracker(temp_metrics_file)

    # Log metrics for different workflows
    for workflow in ["code_review", "bug_predict", "code_review"]:
        metric = PromptMetrics(
            timestamp=datetime.now().isoformat(),
            workflow=workflow,
            agent_role="Test Agent",
            task_description="Test task",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1000.0,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=True,
        )
        tracker.log_metric(metric)

    # Filter by workflow
    code_review_metrics = tracker.get_metrics(workflow="code_review")
    assert len(code_review_metrics) == 2

    bug_predict_metrics = tracker.get_metrics(workflow="bug_predict")
    assert len(bug_predict_metrics) == 1


def test_metrics_tracker_summary(temp_metrics_file):
    """Test metrics summary calculation."""
    tracker = MetricsTracker(temp_metrics_file)

    # Log multiple metrics
    for i in range(5):
        metric = PromptMetrics(
            timestamp=datetime.now().isoformat(),
            workflow="test_workflow",
            agent_role="Test Agent",
            task_description=f"Test task {i}",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1000.0,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=True,
        )
        tracker.log_metric(metric)

    summary = tracker.get_summary()
    assert summary["total_prompts"] == 5
    assert summary["avg_tokens"] == 150
    assert summary["avg_latency_ms"] == 1000.0
    assert summary["success_rate"] == 1.0
    assert summary["retry_rate"] == 0.0


def test_metrics_tracker_summary_with_failures(temp_metrics_file):
    """Test summary with some failed parses."""
    tracker = MetricsTracker(temp_metrics_file)

    # Log 3 successful and 2 failed
    for i in range(5):
        metric = PromptMetrics(
            timestamp=datetime.now().isoformat(),
            workflow="test_workflow",
            agent_role="Test Agent",
            task_description=f"Test task {i}",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1000.0,
            retry_count=0 if i < 3 else 1,
            parsing_success=i < 3,  # First 3 succeed
            validation_success=True if i < 3 else False,
            error_message=None if i < 3 else "Parse error",
            xml_structure_used=True,
        )
        tracker.log_metric(metric)

    summary = tracker.get_summary()
    assert summary["total_prompts"] == 5
    assert summary["success_rate"] == 0.6  # 3/5
    assert summary["retry_rate"] == 0.4  # 2/5


def test_metrics_tracker_empty_summary(temp_metrics_file):
    """Test summary with no metrics."""
    tracker = MetricsTracker(temp_metrics_file)

    summary = tracker.get_summary()
    assert summary["total_prompts"] == 0
    assert summary["avg_tokens"] == 0
    assert summary["success_rate"] == 0
