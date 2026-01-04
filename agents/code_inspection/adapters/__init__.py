"""Tool Adapters for Code Inspection Pipeline

Each adapter wraps an existing inspection tool and converts its output
to the unified ToolResult format for the pipeline.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .code_health_adapter import CodeHealthAdapter
from .code_review_adapter import CodeReviewAdapter
from .debugging_adapter import DebuggingAdapter
from .security_adapter import SecurityAdapter
from .tech_debt_adapter import TechDebtAdapter
from .test_quality_adapter import TestQualityAdapter

__all__ = [
    "CodeHealthAdapter",
    "CodeReviewAdapter",
    "DebuggingAdapter",
    "SecurityAdapter",
    "TechDebtAdapter",
    "TestQualityAdapter",
]
