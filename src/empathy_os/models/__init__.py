"""Unified Model Registry for Empathy Framework

Single source of truth for model configurations across:
- empathy_llm_toolkit.routing.ModelRouter
- src/empathy_os/workflows.WorkflowConfig
- src/empathy_os.cost_tracker

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from .empathy_executor import EmpathyLLMExecutor
from .executor import ExecutionContext, LLMExecutor, LLMResponse, MockLLMExecutor
from .fallback import (
                       DEFAULT_FALLBACK_POLICY,
                       DEFAULT_RETRY_POLICY,
                       CircuitBreaker,
                       CircuitBreakerState,
                       FallbackPolicy,
                       FallbackStep,
                       FallbackStrategy,
                       ResilientExecutor,
                       RetryPolicy,
)
from .provider_config import (
                       ProviderConfig,
                       ProviderMode,
                       configure_provider_cli,
                       configure_provider_interactive,
                       get_provider_config,
                       reset_provider_config,
                       set_provider_config,
)
from .registry import (
                       MODEL_REGISTRY,
                       ModelInfo,
                       ModelProvider,
                       ModelTier,
                       get_all_models,
                       get_model,
                       get_pricing_for_model,
)
from .tasks import (
                       CAPABLE_TASKS,
                       CHEAP_TASKS,
                       PREMIUM_TASKS,
                       TASK_TIER_MAP,
                       TaskInfo,
                       TaskType,
                       get_all_tasks,
                       get_tasks_for_tier,
                       get_tier_for_task,
                       is_known_task,
                       normalize_task_type,
)
from .telemetry import (
                       LLMCallRecord,
                       TelemetryAnalytics,
                       TelemetryBackend,
                       TelemetryStore,
                       WorkflowRunRecord,
                       WorkflowStageRecord,
                       get_telemetry_store,
                       log_llm_call,
                       log_workflow_run,
)
from .validation import (
                       ConfigValidator,
                       ValidationError,
                       ValidationResult,
                       validate_config,
                       validate_yaml_file,
)

__all__ = [
    "CAPABLE_TASKS",
    "CHEAP_TASKS",
    "DEFAULT_FALLBACK_POLICY",
    "DEFAULT_RETRY_POLICY",
    "MODEL_REGISTRY",
    "PREMIUM_TASKS",
    "TASK_TIER_MAP",
    "CircuitBreaker",
    "CircuitBreakerState",
    "ConfigValidator",
    "EmpathyLLMExecutor",
    "ExecutionContext",
    "FallbackPolicy",
    "FallbackStep",
    # Fallback exports
    "FallbackStrategy",
    # Telemetry exports
    "LLMCallRecord",
    # Executor exports
    "LLMExecutor",
    "LLMResponse",
    "MockLLMExecutor",
    "ModelInfo",
    "ModelProvider",
    # Registry exports
    "ModelTier",
    "ProviderConfig",
    # Provider config exports
    "ProviderMode",
    "ResilientExecutor",
    "RetryPolicy",
    "TaskInfo",
    # Task exports
    "TaskType",
    "TelemetryAnalytics",
    "TelemetryBackend",
    "TelemetryStore",
    # Validation exports
    "ValidationError",
    "ValidationResult",
    "WorkflowRunRecord",
    "WorkflowStageRecord",
    "configure_provider_cli",
    "configure_provider_interactive",
    "get_all_models",
    "get_all_tasks",
    "get_model",
    "get_pricing_for_model",
    "get_provider_config",
    "get_tasks_for_tier",
    "get_telemetry_store",
    "get_tier_for_task",
    "is_known_task",
    "log_llm_call",
    "log_workflow_run",
    "normalize_task_type",
    "reset_provider_config",
    "set_provider_config",
    "validate_config",
    "validate_yaml_file",
]
