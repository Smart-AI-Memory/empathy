"""
Coach Wizards Package

Specialized wizards for different types of software tasks.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from .base_wizard import (
    BaseWizard,
    WizardTask,
    WizardOutput,
    WizardArtifact,
    WizardRisk,
    WizardHandoff,
    EmpathyChecks,
)
# Original 6 wizards
from .debugging_wizard import DebuggingWizard
from .documentation_wizard import DocumentationWizard
from .design_review_wizard import DesignReviewWizard
from .testing_wizard import TestingWizard
from .retrospective_wizard import RetrospectiveWizard
from .security_wizard import SecurityWizard
# New 10 wizards
from .performance_wizard import PerformanceWizard
from .refactoring_wizard import RefactoringWizard
from .api_wizard import APIWizard
from .database_wizard import DatabaseWizard
from .devops_wizard import DevOpsWizard
from .onboarding_wizard import OnboardingWizard
from .accessibility_wizard import AccessibilityWizard
from .localization_wizard import LocalizationWizard
from .compliance_wizard import ComplianceWizard
from .monitoring_wizard import MonitoringWizard

__all__ = [
    "BaseWizard",
    "WizardTask",
    "WizardOutput",
    "WizardArtifact",
    "WizardRisk",
    "WizardHandoff",
    "EmpathyChecks",
    # Original 6 wizards
    "DebuggingWizard",
    "DocumentationWizard",
    "DesignReviewWizard",
    "TestingWizard",
    "RetrospectiveWizard",
    "SecurityWizard",
    # New 10 wizards
    "PerformanceWizard",
    "RefactoringWizard",
    "APIWizard",
    "DatabaseWizard",
    "DevOpsWizard",
    "OnboardingWizard",
    "AccessibilityWizard",
    "LocalizationWizard",
    "ComplianceWizard",
    "MonitoringWizard",
]
