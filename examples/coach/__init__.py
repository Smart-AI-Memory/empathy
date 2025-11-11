"""
Coach - Empathy Framework Orchestration Agent

Coordinates task-specific wizards to provide empathetic, anticipatory
assistance for software development tasks.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from .coach import Coach, CoachOutput
from .wizards import DebuggingWizard, DocumentationWizard, WizardOutput, WizardTask

__all__ = [
    "Coach",
    "CoachOutput",
    "WizardTask",
    "WizardOutput",
    "DebuggingWizard",
    "DocumentationWizard",
]
