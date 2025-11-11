"""
Empathy Framework - Plugin System Base Classes

This module provides the core abstractions for creating domain-specific plugins
that extend the Empathy Framework.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata about a plugin"""

    name: str
    version: str
    domain: str
    description: str
    author: str
    license: str
    requires_core_version: str  # Minimum core framework version
    dependencies: list[str] = None  # Additional package dependencies


class BaseWizard(ABC):
    """
    Universal base class for all wizards across all domains.

    This replaces domain-specific base classes (BaseCoachWizard, etc.)
    to provide a unified interface.

    Design Philosophy:
    - Domain-agnostic: Works for software, healthcare, finance, etc.
    - Level-aware: Each wizard declares its empathy level
    - Pattern-contributing: Wizards share learnings via pattern library
    """

    def __init__(self, name: str, domain: str, empathy_level: int, category: str | None = None):
        """
        Initialize a wizard

        Args:
            name: Human-readable wizard name
            domain: Domain this wizard belongs to (e.g., 'software', 'healthcare')
            empathy_level: Which empathy level this wizard operates at (1-5)
            category: Optional category within domain
        """
        self.name = name
        self.domain = domain
        self.empathy_level = empathy_level
        self.category = category
        self.logger = logging.getLogger(f"wizard.{domain}.{name}")

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze the given context and return results.

        This is the main entry point for all wizards. The context structure
        is domain-specific but the return format should follow a standard pattern.

        Args:
            context: Domain-specific context (code, patient data, financial records, etc.)

        Returns:
            Dictionary containing:
                - issues: List of current issues found (Levels 1-3)
                - predictions: List of future issues (Level 4)
                - recommendations: Actionable next steps
                - patterns: Patterns detected (for pattern library)
                - confidence: Confidence score (0.0 to 1.0)
        """
        pass

    @abstractmethod
    def get_required_context(self) -> list[str]:
        """
        Declare what context fields this wizard needs.

        Returns:
            List of required context keys

        Example:
            ['code', 'file_path', 'language'] for software wizard
            ['patient_id', 'vitals', 'medications'] for healthcare wizard
        """
        pass

    def validate_context(self, context: dict[str, Any]) -> bool:
        """
        Validate that context contains required fields.

        Args:
            context: Context to validate

        Returns:
            True if valid, raises ValueError if invalid
        """
        required = self.get_required_context()
        missing = [key for key in required if key not in context]

        if missing:
            raise ValueError(f"Wizard '{self.name}' missing required context: {missing}")

        return True

    def get_empathy_level(self) -> int:
        """Get the empathy level this wizard operates at"""
        return self.empathy_level

    def contribute_patterns(self, analysis_result: dict[str, Any]) -> dict[str, Any]:
        """
        Extract patterns from analysis for the shared pattern library.

        This enables cross-domain learning (Level 5 Systems Empathy).

        Args:
            analysis_result: Result from analyze()

        Returns:
            Dictionary of patterns in standard format
        """
        # Default implementation - override for custom pattern extraction
        return {
            "wizard": self.name,
            "domain": self.domain,
            "timestamp": datetime.now().isoformat(),
            "patterns": analysis_result.get("patterns", []),
        }


class BasePlugin(ABC):
    """
    Base class for domain plugins.

    A plugin is a collection of wizards and patterns for a specific domain.

    Example:
        - SoftwarePlugin: 16+ coach wizards for code analysis
        - HealthcarePlugin: Clinical and compliance wizards
        - FinancePlugin: Fraud detection, compliance wizards
    """

    def __init__(self):
        self.logger = logging.getLogger(f"plugin.{self.get_metadata().domain}")
        self._wizards: dict[str, type[BaseWizard]] = {}
        self._initialized = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return metadata about this plugin.

        Returns:
            PluginMetadata instance
        """
        pass

    @abstractmethod
    def register_wizards(self) -> dict[str, type[BaseWizard]]:
        """
        Register all wizards provided by this plugin.

        Returns:
            Dictionary mapping wizard_id -> Wizard class

        Example:
            {
                'security': SecurityWizard,
                'performance': PerformanceWizard,
            }
        """
        pass

    def register_patterns(self) -> dict[str, Any]:
        """
        Register domain-specific patterns for the pattern library.

        Returns:
            Dictionary of patterns in standard format
        """
        # Optional - override if plugin provides pre-built patterns
        return {}

    def initialize(self) -> None:
        """
        Initialize the plugin (lazy initialization).

        Called once before first use. Override to perform setup:
        - Load configuration
        - Initialize domain-specific services
        - Validate dependencies
        """
        if self._initialized:
            return

        self.logger.info(f"Initializing plugin: {self.get_metadata().name}")

        # Register wizards
        self._wizards = self.register_wizards()

        self.logger.info(
            f"Plugin '{self.get_metadata().name}' initialized with " f"{len(self._wizards)} wizards"
        )

        self._initialized = True

    def get_wizard(self, wizard_id: str) -> type[BaseWizard] | None:
        """
        Get a wizard by ID.

        Args:
            wizard_id: Wizard identifier

        Returns:
            Wizard class or None if not found
        """
        if not self._initialized:
            self.initialize()

        return self._wizards.get(wizard_id)

    def list_wizards(self) -> list[str]:
        """
        List all wizard IDs provided by this plugin.

        Returns:
            List of wizard identifiers
        """
        if not self._initialized:
            self.initialize()

        return list(self._wizards.keys())

    def get_wizard_info(self, wizard_id: str) -> dict[str, Any] | None:
        """
        Get information about a wizard without instantiating it.

        Args:
            wizard_id: Wizard identifier

        Returns:
            Dictionary with wizard metadata
        """
        wizard_class = self.get_wizard(wizard_id)
        if not wizard_class:
            return None

        # Create temporary instance to get metadata
        # (wizards should be lightweight to construct)
        temp_instance = wizard_class()

        return {
            "id": wizard_id,
            "name": temp_instance.name,
            "domain": temp_instance.domain,
            "empathy_level": temp_instance.empathy_level,
            "category": temp_instance.category,
            "required_context": temp_instance.get_required_context(),
        }


class PluginError(Exception):
    """Base exception for plugin-related errors"""

    pass


class PluginLoadError(PluginError):
    """Raised when plugin fails to load"""

    pass


class PluginValidationError(PluginError):
    """Raised when plugin fails validation"""

    pass
