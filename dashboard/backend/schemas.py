"""
Pydantic schemas for request/response validation.

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
            }
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
            }
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
            }
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
            }
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
            "example": {"name": "redis", "status": "pass", "message": "Redis is running"}
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
            }
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
            }
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
                    }
                ],
                "classification_filter": None,
            }
        }


class ExportPatternsRequest(BaseModel):
    """Request to export patterns."""

    classification: ClassificationEnum | None = Field(
        None, description="Filter patterns by classification"
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
            }
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
            }
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
            }
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
            }
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
