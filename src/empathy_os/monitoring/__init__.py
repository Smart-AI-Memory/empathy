"""LLM Telemetry Monitoring System

A zero-config monitoring system for LLM usage tracking with progressive enhancement:

**Tier 1 (Default - Zero Config):**
- JSONL telemetry (automatic logging to `.empathy/`)
- CLI dashboard (`empathy telemetry`)
- VSCode panel (real-time visualization)

**Tier 2 (Enterprise - Opt-in):**
- Alert system (threshold-based notifications)
- OpenTelemetry backend (export to SigNoz/Datadog)

This package provides the backend components for the monitoring system.
The frontend VSCode extension is in `website/components/telemetry/`.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

# Import agent monitoring classes from sibling module (backwards compatibility)
# The agent_monitoring.py module contains agent monitoring for multi-agent systems
# This package (monitoring/) contains LLM telemetry monitoring
from empathy_os.agent_monitoring import AgentMetrics, AgentMonitor, TeamMetrics

# Import telemetry classes
from empathy_os.models.telemetry import (
                                         LLMCallRecord,
                                         TelemetryAnalytics,
                                         TelemetryStore,
                                         WorkflowRunRecord,
                                         get_telemetry_store,
                                         log_llm_call,
                                         log_workflow_run,
)

__all__ = [
    # Agent monitoring (backwards compatibility)
    "AgentMetrics",
    "AgentMonitor",
    "TeamMetrics",
    # LLM telemetry
    "LLMCallRecord",
    "WorkflowRunRecord",
    "TelemetryStore",
    "TelemetryAnalytics",
    "get_telemetry_store",
    "log_llm_call",
    "log_workflow_run",
]

__version__ = "3.8.0-alpha"
