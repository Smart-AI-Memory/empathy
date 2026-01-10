"""Tier 1 Automation Monitoring API endpoints.

Provides REST API for:
- Task routing statistics
- Test execution metrics
- Coverage trends
- Agent performance
- Comprehensive Tier 1 summary
"""

from datetime import datetime, timedelta

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from empathy_os.models.telemetry import TelemetryAnalytics, get_telemetry_store

from ..schemas import (
    AgentPerformanceResponse,
    CoverageStatsResponse,
    TaskRoutingStatsResponse,
    TestExecutionStatsResponse,
    Tier1SummaryResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "/monitoring/task-routing",
    response_model=TaskRoutingStatsResponse,
    summary="Get task routing statistics",
    description="Get routing accuracy, confidence scores, and breakdown by task type and strategy.",
)
async def get_task_routing_stats(
    hours: int = Query(24, ge=1, le=720, description="Hours to look back"),
) -> TaskRoutingStatsResponse:
    """Get task routing statistics.

    Returns routing accuracy, confidence scores, and breakdown by task type
    and routing strategy (rule-based, ML, manual override).

    Args:
        hours: Number of hours to analyze (default: 24, max: 720 / 30 days)

    Returns:
        TaskRoutingStatsResponse with routing metrics
    """
    try:
        store = get_telemetry_store()
        analytics = TelemetryAnalytics(store)
        since = datetime.utcnow() - timedelta(hours=hours)

        stats = analytics.task_routing_accuracy(since=since)
        stats["timestamp"] = datetime.utcnow().isoformat() + "Z"

        logger.info(
            "task_routing_stats_retrieved",
            hours=hours,
            total_tasks=stats["total_tasks"],
            accuracy_rate=stats["accuracy_rate"],
        )
        return TaskRoutingStatsResponse(**stats)
    except Exception as e:
        logger.error("task_routing_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task routing stats: {e!s}",
        )


@router.get(
    "/monitoring/test-execution",
    response_model=TestExecutionStatsResponse,
    summary="Get test execution statistics",
    description="Get test success rates, duration trends, and failure analysis.",
)
async def get_test_execution_stats(
    hours: int = Query(24, ge=1, le=720, description="Hours to look back"),
) -> TestExecutionStatsResponse:
    """Get test execution statistics.

    Returns test execution success rates, average duration,
    total tests run, and most frequently failing tests.

    Args:
        hours: Number of hours to analyze (default: 24, max: 720 / 30 days)

    Returns:
        TestExecutionStatsResponse with test metrics
    """
    try:
        store = get_telemetry_store()
        analytics = TelemetryAnalytics(store)
        since = datetime.utcnow() - timedelta(hours=hours)

        stats = analytics.test_execution_trends(since=since)
        stats["timestamp"] = datetime.utcnow().isoformat() + "Z"

        logger.info(
            "test_execution_stats_retrieved",
            hours=hours,
            total_executions=stats["total_executions"],
            success_rate=stats["success_rate"],
        )
        return TestExecutionStatsResponse(**stats)
    except Exception as e:
        logger.error("test_execution_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve test execution stats: {e!s}",
        )


@router.get(
    "/monitoring/coverage",
    response_model=CoverageStatsResponse,
    summary="Get test coverage statistics",
    description="Get current coverage, trends, and critical gaps.",
)
async def get_coverage_stats(
    hours: int = Query(168, ge=1, le=720, description="Hours to look back (default: 7 days)"),
) -> CoverageStatsResponse:
    """Get test coverage statistics and trends.

    Returns current coverage percentage, trend (improving/declining/stable),
    and count of critical gaps requiring attention.

    Args:
        hours: Number of hours to analyze (default: 168 / 7 days, max: 720 / 30 days)

    Returns:
        CoverageStatsResponse with coverage metrics
    """
    try:
        store = get_telemetry_store()
        analytics = TelemetryAnalytics(store)
        since = datetime.utcnow() - timedelta(hours=hours)

        stats = analytics.coverage_progress(since=since)
        stats["timestamp"] = datetime.utcnow().isoformat() + "Z"

        logger.info(
            "coverage_stats_retrieved",
            hours=hours,
            current_coverage=stats["current_coverage"],
            trend=stats["trend"],
        )
        return CoverageStatsResponse(**stats)
    except Exception as e:
        logger.error("coverage_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve coverage stats: {e!s}",
        )


@router.get(
    "/monitoring/agents",
    response_model=AgentPerformanceResponse,
    summary="Get agent performance metrics",
    description="Get assignment counts, success rates, and quality scores per agent/workflow.",
)
async def get_agent_performance(
    hours: int = Query(168, ge=1, le=720, description="Hours to look back (default: 7 days)"),
) -> AgentPerformanceResponse:
    """Get agent/workflow performance metrics.

    Returns per-agent statistics including assignments, completions,
    success rates, average duration, and overall automation rates.

    Args:
        hours: Number of hours to analyze (default: 168 / 7 days, max: 720 / 30 days)

    Returns:
        AgentPerformanceResponse with agent metrics
    """
    try:
        store = get_telemetry_store()
        analytics = TelemetryAnalytics(store)
        since = datetime.utcnow() - timedelta(hours=hours)

        stats = analytics.agent_performance(since=since)
        stats["timestamp"] = datetime.utcnow().isoformat() + "Z"

        logger.info(
            "agent_performance_retrieved",
            hours=hours,
            agent_count=len(stats["by_agent"]),
            automation_rate=stats["automation_rate"],
        )
        return AgentPerformanceResponse(**stats)
    except Exception as e:
        logger.error("agent_performance_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent performance: {e!s}",
        )


@router.get(
    "/monitoring/summary",
    response_model=Tier1SummaryResponse,
    summary="Get comprehensive Tier 1 summary",
    description="Get all Tier 1 automation metrics in a single response.",
)
async def get_tier1_summary(
    hours: int = Query(24, ge=1, le=720, description="Hours to look back"),
) -> Tier1SummaryResponse:
    """Get comprehensive Tier 1 automation summary.

    Combines all Tier 1 metrics (task routing, test execution, coverage,
    agent performance, cost savings) into a single dashboard view.

    Args:
        hours: Number of hours to analyze (default: 24, max: 720 / 30 days)

    Returns:
        Tier1SummaryResponse with all metrics
    """
    try:
        store = get_telemetry_store()
        analytics = TelemetryAnalytics(store)
        since = datetime.utcnow() - timedelta(hours=hours)

        summary = analytics.tier1_summary(since=since)

        # Add timestamp to each sub-section
        timestamp = datetime.utcnow().isoformat() + "Z"
        summary["timestamp"] = timestamp
        summary["task_routing"]["timestamp"] = timestamp
        summary["test_execution"]["timestamp"] = timestamp
        summary["coverage"]["timestamp"] = timestamp
        summary["agent_performance"]["timestamp"] = timestamp

        logger.info("tier1_summary_retrieved", hours=hours)
        return Tier1SummaryResponse(**summary)
    except Exception as e:
        logger.error("tier1_summary_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Tier 1 summary: {e!s}",
        )


@router.get(
    "/monitoring/recent-tasks",
    summary="Get recent task routing decisions",
    description="Get the most recent task routing decisions for live monitoring.",
)
async def get_recent_tasks(
    limit: int = Query(20, ge=1, le=100, description="Maximum tasks to return"),
) -> dict:
    """Get recent task routing decisions for live monitoring.

    Args:
        limit: Maximum number of tasks to return (default: 20, max: 100)

    Returns:
        Dict with task routing records
    """
    try:
        store = get_telemetry_store()
        routings = store.get_task_routings(limit=limit)

        logger.info("recent_tasks_retrieved", count=len(routings))
        return {
            "total": len(routings),
            "tasks": [r.to_dict() for r in routings],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error("recent_tasks_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent tasks: {e!s}",
        )


@router.get(
    "/monitoring/recent-tests",
    summary="Get recent test executions",
    description="Get the most recent test execution results for live monitoring.",
)
async def get_recent_tests(
    limit: int = Query(10, ge=1, le=50, description="Maximum test runs to return"),
) -> dict:
    """Get recent test executions for live monitoring.

    Args:
        limit: Maximum number of test runs to return (default: 10, max: 50)

    Returns:
        Dict with test execution records
    """
    try:
        store = get_telemetry_store()
        executions = store.get_test_executions(limit=limit)

        logger.info("recent_tests_retrieved", count=len(executions))
        return {
            "total": len(executions),
            "executions": [e.to_dict() for e in executions],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error("recent_tests_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent tests: {e!s}",
        )
