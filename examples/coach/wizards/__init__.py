"""Coach Wizards Package

Specialized wizards for different types of software tasks.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from .accessibility_wizard import AccessibilityWizard
from .api_wizard import APIWizard
from .base_wizard import (
    BaseWizard,
    EmpathyChecks,
    WizardArtifact,
    WizardHandoff,
    WizardOutput,
    WizardRisk,
    WizardTask,
)
from .compliance_wizard import ComplianceWizard
from .database_wizard import DatabaseWizard

# Original 6 wizards
from .debugging_wizard import DebuggingWizard
from .design_review_wizard import DesignReviewWizard
from .devops_wizard import DevOpsWizard
from .documentation_wizard import DocumentationWizard
from .localization_wizard import LocalizationWizard
from .monitoring_wizard import MonitoringWizard
from .onboarding_wizard import OnboardingWizard

# New 10 wizards
from .performance_wizard import PerformanceWizard
from .refactoring_wizard import RefactoringWizard
from .retrospective_wizard import RetrospectiveWizard
from .security_wizard import SecurityWizard
from .testing_wizard import TestingWizard

__all__ = [
    "APIWizard",
    "AccessibilityWizard",
    "BaseWizard",
    "ComplianceWizard",
    "DatabaseWizard",
    # Original 6 wizards
    "DebuggingWizard",
    "DesignReviewWizard",
    "DevOpsWizard",
    "DocumentationWizard",
    "EmpathyChecks",
    "LocalizationWizard",
    "MonitoringWizard",
    "OnboardingWizard",
    # New 10 wizards
    "PerformanceWizard",
    "RefactoringWizard",
    "RetrospectiveWizard",
    "SecurityWizard",
    "TestingWizard",
    "WizardArtifact",
    "WizardHandoff",
    "WizardOutput",
    "WizardRisk",
    "WizardTask",
]
