"""
Base Wizard for Software Development Plugin

Foundation for all software development wizards.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseWizard(ABC):
    """
    Base class for all software development wizards.

    All wizards implement Level 4 Anticipatory Empathy:
    - Analyze current state
    - Predict future problems
    - Provide prevention steps
    """

    def __init__(self):
        self.logger = logger

    @property
    @abstractmethod
    def name(self) -> str:
        """Wizard name"""
        pass

    @property
    @abstractmethod
    def level(self) -> int:
        """Empathy level (1-5)"""
        pass

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze the given context and return results.

        Args:
            context: Dictionary with wizard-specific inputs

        Returns:
            Dictionary with:
            - predictions: List of Level 4 predictions
            - recommendations: List of actionable steps
            - confidence: Float 0.0-1.0
            - Additional wizard-specific data
        """
        pass
