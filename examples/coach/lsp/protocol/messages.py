"""
Custom LSP Messages for Coach
Defines custom request/response types
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class WizardTaskRequest:
    """Request to run a specific wizard"""

    wizard_name: str
    task: str
    role: str = "developer"
    context: str = ""
    preferences: str = ""
    risk_tolerance: str = "medium"


@dataclass
class WizardResponse:
    """Response from wizard execution"""

    wizard_name: str
    diagnosis: str
    artifacts: list[dict[str, str]]
    confidence: float
    empathy_level: int


@dataclass
class MultiWizardRequest:
    """Request for multi-wizard collaboration"""

    scenario: str
    file_uris: list[str]
    context: str | None = None


@dataclass
class HealthCheckResponse:
    """Health check response"""

    status: str
    version: str
    wizards: int
    wizard_names: list[str]
    uptime_seconds: int


@dataclass
class PredictionRequest:
    """Request for Level 4 prediction"""

    context_type: str
    current_value: Any
    additional_context: str | None = None


# LSP Custom Method Names
COACH_RUN_WIZARD = "coach/runWizard"
COACH_MULTI_WIZARD_REVIEW = "coach/multiWizardReview"
COACH_PREDICT = "coach/predict"
COACH_HEALTH_CHECK = "coach/healthCheck"
COACH_CLEAR_CACHE = "coach/clearCache"
COACH_GET_PATTERNS = "coach/getPatterns"
