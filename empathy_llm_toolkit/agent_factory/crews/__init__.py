"""
Empathy Framework - Pre-built Crews

Ready-to-use multi-agent crews for common tasks.
Each crew leverages CrewAI's hierarchical collaboration patterns
with XML-enhanced prompts for structured output.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_llm_toolkit.agent_factory.crews.code_review import (
    CodeReviewConfig,
    CodeReviewCrew,
    CodeReviewReport,
    ReviewFinding,
    Verdict,
)
from empathy_llm_toolkit.agent_factory.crews.health_check import (
    HealthCheckConfig,
    HealthCheckCrew,
    HealthCheckReport,
    HealthFix,
    HealthIssue,
)
from empathy_llm_toolkit.agent_factory.crews.refactoring import (
    CodeCheckpoint,
    RefactoringCategory,
    RefactoringConfig,
    RefactoringCrew,
    RefactoringFinding,
    RefactoringReport,
    UserProfile,
)
from empathy_llm_toolkit.agent_factory.crews.security_audit import (
    SecurityAuditConfig,
    SecurityAuditCrew,
    SecurityFinding,
    SecurityReport,
)

__all__ = [
    # Security Audit Crew
    "SecurityAuditCrew",
    "SecurityAuditConfig",
    "SecurityFinding",
    "SecurityReport",
    # Code Review Crew
    "CodeReviewCrew",
    "CodeReviewConfig",
    "CodeReviewReport",
    "ReviewFinding",
    "Verdict",
    # Health Check Crew
    "HealthCheckCrew",
    "HealthCheckConfig",
    "HealthCheckReport",
    "HealthIssue",
    "HealthFix",
    # Refactoring Crew
    "RefactoringCrew",
    "RefactoringConfig",
    "RefactoringReport",
    "RefactoringFinding",
    "RefactoringCategory",
    "CodeCheckpoint",
    "UserProfile",
]
