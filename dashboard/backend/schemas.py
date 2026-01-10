"""Pydantic schemas for request/response validation.

All API endpoints use these schemas for type-safe validation and
automatic OpenAPI documentation generation.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# Enums
# ============================================================================


class ClassificationEnum(str, Enum):
    """Pattern classification levels."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    SENSITIVE = "SENSITIVE"


class RedisStatusEnum(str, Enum):
    """Redis status states."""

    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    ERROR = "error"


class HealthStatusEnum(str, Enum):
    """Overall health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class CheckStatusEnum(str, Enum):
    """Individual check status."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    INFO = "info"


# ============================================================================
# Status Responses
# ============================================================================


class RedisStatusResponse(BaseModel):
    """Redis status information."""

    status: RedisStatusEnum
    host: str
    port: int
    method: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "running",
                "host": "localhost",
                "port": 6379,
                "method": "already_running",
            },
        }


class LongTermStatusResponse(BaseModel):
    """Long-term storage status."""

    status: str
    storage_dir: str
    pattern_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "status": "available",
                "storage_dir": "./memdocs_storage",
                "pattern_count": 42,
            },
        }


class ConfigStatusResponse(BaseModel):
    """Configuration status."""

    auto_start_redis: bool
    audit_dir: str

    class Config:
        json_schema_extra = {"example": {"auto_start_redis": True, "audit_dir": "./logs"}}


class SystemStatusResponse(BaseModel):
    """Complete system status."""

    timestamp: str
    redis: RedisStatusResponse
    long_term: LongTermStatusResponse
    config: ConfigStatusResponse

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-01-15T12:34:56.789Z",
                "redis": {
                    "status": "running",
                    "host": "localhost",
                    "port": 6379,
                    "method": "already_running",
                },
                "long_term": {
                    "status": "available",
                    "storage_dir": "./memdocs_storage",
                    "pattern_count": 42,
                },
                "config": {"auto_start_redis": True, "audit_dir": "./logs"},
            },
        }


# ============================================================================
# Statistics
# ============================================================================


class MemoryStatsResponse(BaseModel):
    """Comprehensive memory statistics."""

    # Redis stats
    redis_available: bool
    redis_method: str
    redis_keys_total: int
    redis_keys_working: int
    redis_keys_staged: int
    redis_memory_used: str

    # Long-term stats
    long_term_available: bool
    patterns_total: int
    patterns_public: int
    patterns_internal: int
    patterns_sensitive: int
    patterns_encrypted: int

    # Timestamp
    collected_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "redis_available": True,
                "redis_method": "homebrew",
                "redis_keys_total": 150,
                "redis_keys_working": 100,
                "redis_keys_staged": 5,
                "redis_memory_used": "2.5M",
                "long_term_available": True,
                "patterns_total": 42,
                "patterns_public": 30,
                "patterns_internal": 10,
                "patterns_sensitive": 2,
                "patterns_encrypted": 2,
                "collected_at": "2025-01-15T12:34:56.789Z",
            },
        }


# ============================================================================
# Health Check
# ============================================================================


class HealthCheckItem(BaseModel):
    """Individual health check result."""

    name: str
    status: CheckStatusEnum
    message: str

    class Config:
        json_schema_extra = {
            "example": {"name": "redis", "status": "pass", "message": "Redis is running"},
        }


class HealthCheckResponse(BaseModel):
    """Complete health check results."""

    overall: HealthStatusEnum
    checks: list[HealthCheckItem]
    recommendations: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "overall": "healthy",
                "checks": [
                    {"name": "redis", "status": "pass", "message": "Redis is running"},
                    {"name": "long_term", "status": "pass", "message": "Storage available"},
                ],
                "recommendations": [],
            },
        }


# ============================================================================
# Patterns
# ============================================================================


class PatternSummary(BaseModel):
    """Summary information for a pattern."""

    pattern_id: str
    pattern_type: str
    classification: ClassificationEnum
    created_at: str | None = None
    user_id: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "pattern_id": "pat_abc123",
                "pattern_type": "algorithm",
                "classification": "INTERNAL",
                "created_at": "2025-01-15T12:34:56.789Z",
                "user_id": "dev@company.com",
            },
        }


class PatternListResponse(BaseModel):
    """List of patterns with pagination info."""

    total: int
    patterns: list[PatternSummary]
    classification_filter: ClassificationEnum | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "total": 42,
                "patterns": [
                    {
                        "pattern_id": "pat_abc123",
                        "pattern_type": "algorithm",
                        "classification": "INTERNAL",
                        "created_at": "2025-01-15T12:34:56.789Z",
                        "user_id": "dev@company.com",
                    },
                ],
                "classification_filter": None,
            },
        }


class ExportPatternsRequest(BaseModel):
    """Request to export patterns."""

    classification: ClassificationEnum | None = Field(
        None,
        description="Filter patterns by classification",
    )
    output_filename: str | None = Field(None, description="Custom output filename (optional)")


class ExportPatternsResponse(BaseModel):
    """Response from pattern export."""

    success: bool
    pattern_count: int
    output_path: str
    exported_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "pattern_count": 42,
                "output_path": "/tmp/patterns_export_20250115.json",
                "exported_at": "2025-01-15T12:34:56.789Z",
            },
        }


# ============================================================================
# Redis Operations
# ============================================================================


class RedisStartRequest(BaseModel):
    """Request to start Redis."""

    verbose: bool = Field(True, description="Enable verbose logging during startup")


class RedisStartResponse(BaseModel):
    """Response from Redis start operation."""

    success: bool
    available: bool
    method: str
    message: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "available": True,
                "method": "homebrew",
                "message": "Redis started via homebrew",
            },
        }


class RedisStopResponse(BaseModel):
    """Response from Redis stop operation."""

    success: bool
    message: str

    class Config:
        json_schema_extra = {"example": {"success": True, "message": "Redis stopped successfully"}}


# ============================================================================
# WebSocket Messages
# ============================================================================


class WebSocketMessage(BaseModel):
    """Base WebSocket message."""

    type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    data: dict[str, Any] | None = None


class MetricsUpdate(BaseModel):
    """Real-time metrics update."""

    redis_keys_total: int
    redis_keys_working: int
    redis_keys_staged: int
    redis_memory_used: str
    patterns_total: int
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "redis_keys_total": 150,
                "redis_keys_working": 100,
                "redis_keys_staged": 5,
                "redis_memory_used": "2.5M",
                "patterns_total": 42,
                "timestamp": "2025-01-15T12:34:56.789Z",
            },
        }


# ============================================================================
# Tier 1 Automation Monitoring Responses
# ============================================================================


class TaskRoutingStatsResponse(BaseModel):
    """Task routing statistics response."""

    total_tasks: int
    successful_routing: int
    accuracy_rate: float
    avg_confidence: float
    by_task_type: dict[str, dict]
    by_strategy: dict[str, dict]
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "total_tasks": 150,
                "successful_routing": 142,
                "accuracy_rate": 0.947,
                "avg_confidence": 0.92,
                "by_task_type": {
                    "code_review": {"total": 50, "success": 48, "rate": 0.96},
                    "test_gen": {"total": 45, "success": 43, "rate": 0.956},
                },
                "by_strategy": {
                    "rule_based": {"total": 100, "success": 95},
                    "ml_predicted": {"total": 50, "success": 47},
                },
                "timestamp": "2025-01-15T12:34:56.789Z",
            },
        }


class TestExecutionStatsResponse(BaseModel):
    """Test execution statistics response."""

    total_executions: int
    success_rate: float
    avg_duration_seconds: float
    total_tests_run: int
    total_failures: int
    coverage_trend: str
    most_failing_tests: list[dict]
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "total_executions": 25,
                "success_rate": 0.88,
                "avg_duration_seconds": 45.2,
                "total_tests_run": 2500,
                "total_failures": 15,
                "coverage_trend": "improving",
                "most_failing_tests": [
                    {"name": "test_authentication", "failures": 5},
                    {"name": "test_database_connection", "failures": 3},
                ],
                "timestamp": "2025-01-15T12:34:56.789Z",
            },
        }


class CoverageStatsResponse(BaseModel):
    """Test coverage statistics response."""

    current_coverage: float
    previous_coverage: float
    change: float
    trend: str
    coverage_history: list[dict]
    files_improved: int
    files_declined: int
    critical_gaps_count: int
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "current_coverage": 85.3,
                "previous_coverage": 82.1,
                "change": 3.2,
                "trend": "improving",
                "coverage_history": [
                    {"timestamp": "2025-01-08T12:00:00Z", "coverage": 82.1, "trend": "stable"},
                    {"timestamp": "2025-01-15T12:00:00Z", "coverage": 85.3, "trend": "improving"},
                ],
                "files_improved": 12,
                "files_declined": 2,
                "critical_gaps_count": 5,
                "timestamp": "2025-01-15T12:34:56.789Z",
            },
        }


class AgentPerformanceResponse(BaseModel):
    """Agent performance metrics response."""

    total_assignments: int
    by_agent: dict[str, dict]
    automation_rate: float
    human_review_rate: float
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "total_assignments": 80,
                "by_agent": {
                    "test_gen_workflow": {
                        "assignments": 50,
                        "completed": 47,
                        "success_rate": 0.94,
                        "avg_duration_hours": 0.5,
                        "quality_score_avg": 0.88,
                    },
                    "code_review_workflow": {
                        "assignments": 30,
                        "completed": 28,
                        "success_rate": 0.933,
                        "avg_duration_hours": 0.3,
                        "quality_score_avg": 0.92,
                    },
                },
                "automation_rate": 0.75,
                "human_review_rate": 0.10,
                "timestamp": "2025-01-15T12:34:56.789Z",
            },
        }


class Tier1SummaryResponse(BaseModel):
    """Comprehensive Tier 1 summary response."""

    task_routing: TaskRoutingStatsResponse
    test_execution: TestExecutionStatsResponse
    coverage: CoverageStatsResponse
    agent_performance: AgentPerformanceResponse
    cost_savings: dict
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "task_routing": {
                    "total_tasks": 150,
                    "successful_routing": 142,
                    "accuracy_rate": 0.947,
                },
                "test_execution": {"total_executions": 25, "success_rate": 0.88},
                "coverage": {"current_coverage": 85.3, "trend": "improving"},
                "agent_performance": {"automation_rate": 0.75},
                "cost_savings": {"total_savings": 125.50, "savings_percent": 42.3},
                "timestamp": "2025-01-15T12:34:56.789Z",
            },
        }


# ============================================================================
# Error Responses
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    error_code: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Resource not found",
                "error_code": "NOT_FOUND",
                "timestamp": "2025-01-15T12:34:56.789Z",
            },
        }


# ============================================================================
# API Response Wrapper
# ============================================================================


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool
    data: Any | None = None
    error: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
