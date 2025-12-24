"""
Empathy Framework - Plugin System Base Classes

This module provides the core abstractions for creating domain-specific plugins
that extend the Empathy Framework.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
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
    dependencies: list[str] | None = None  # Additional package dependencies


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
        Subclasses must implement domain-specific analysis logic that aligns with
        the wizard's empathy level.

        Args:
            context: dict[str, Any]
                Domain-specific context dictionary. Must contain all fields returned
                by get_required_context(). Examples:
                - Software: {'code': str, 'file_path': str, 'language': str}
                - Healthcare: {'patient_id': str, 'vitals': dict, 'medications': list}
                - Finance: {'transactions': list, 'account': dict, 'period': str}

        Returns:
            dict[str, Any]
                Analysis results dictionary containing:
                - 'issues': list[dict] - Current issues found (Levels 1-3 analysis)
                - 'predictions': list[dict] - Future issues predicted (Level 4 analysis)
                - 'recommendations': list[dict] - Actionable next steps
                - 'patterns': list[str] - Patterns detected for the pattern library
                - 'confidence': float - Confidence score between 0.0 and 1.0
                - 'wizard': str - Name of the wizard that performed analysis
                - 'empathy_level': int - Empathy level of this analysis (1-5)
                - 'timestamp': str - ISO format timestamp of analysis

        Raises:
            ValueError: If context is invalid or missing required fields
            RuntimeError: If analysis fails due to domain-specific errors
            TimeoutError: If analysis takes too long to complete

        Note:
            - Validate context using self.validate_context() at the beginning
            - Each issue/prediction should include 'severity', 'description', 'affected_component'
            - Use self.contribute_patterns() to extract learnings for the pattern library
            - Confidence scores should reflect uncertainty in the analysis
            - This method is async to support long-running analyses
        """
        pass

    @abstractmethod
    def get_required_context(self) -> list[str]:
        """
        Declare what context fields this wizard needs.

        This method defines the contract between the caller and the wizard.
        The caller must provide all declared fields before calling analyze().
        This enables validation via validate_context() and helps with introspection.

        Returns:
            list[str]
                List of required context field names (keys). Each string should be
                a simple identifier that matches the keys in context dictionaries
                passed to analyze().

        Examples:
            Software wizard returns: ['code', 'file_path', 'language']
            Healthcare wizard returns: ['patient_id', 'vitals', 'medications']
            Finance wizard returns: ['transactions', 'account_id', 'period']

        Note:
            - Must return at least one field (even if minimal)
            - Field names should match exactly what analyze() expects in context
            - Order is not significant but consistency helps with documentation
            - Consider validation requirements when declaring fields
            - Used by validate_context() to check required fields before analyze()
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

        This method provides essential information about the plugin that the
        framework uses for loading, validation, and discovery. It must return
        consistent metadata across multiple calls.

        Returns:
            PluginMetadata
                A PluginMetadata instance containing:
                - name: str - Human-readable plugin name (e.g., 'Software Plugin')
                - version: str - Semantic version string (e.g., '1.0.0')
                - domain: str - Domain this plugin serves (e.g., 'software', 'healthcare')
                - description: str - Brief description of plugin functionality
                - author: str - Plugin author or organization name
                - license: str - License identifier (e.g., 'Apache-2.0', 'MIT')
                - requires_core_version: str - Minimum core framework version (e.g., '1.0.0')
                - dependencies: list[str] - Optional list of required packages

        Note:
            - Called during plugin initialization to validate compatibility
            - Used for plugin discovery and listing
            - Should be immutable (return same values each call)
            - Version should follow semantic versioning
            - Domain names should be lowercase and consistent across plugins
            - Core version requirement ensures framework compatibility
        """
        pass

    @abstractmethod
    def register_wizards(self) -> dict[str, type[BaseWizard]]:
        """
        Register all wizards provided by this plugin.

        This method defines all analysis wizards available in this plugin.
        Wizards are lazy-instantiated by get_wizard() when first requested.
        This method is called during plugin initialization.

        Returns:
            dict[str, type[BaseWizard]]
                Dictionary mapping wizard identifiers to Wizard classes (not instances).
                Keys should be lowercase, snake_case identifiers. Values should be
                uninstantiated class references.

        Returns:
            dict[str, type[BaseWizard]]
                Mapping structure:
                {
                    'wizard_id': WizardClass,
                    'another_wizard': AnotherWizardClass,
                    ...
                }

        Example:
            Software plugin might return:
            {
                'security': SecurityWizard,
                'performance': PerformanceWizard,
                'maintainability': MaintainabilityWizard,
                'accessibility': AccessibilityWizard,
            }

        Note:
            - Return only the class, not instances (instantiation is lazy)
            - Use consistent, descriptive wizard IDs
            - All returned classes must be subclasses of BaseWizard
            - Can return empty dict {} if plugin provides no wizards initially
            - Called once during initialization via initialize()
            - Framework caches results in self._wizards
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
            f"Plugin '{self.get_metadata().name}' initialized with {len(self._wizards)} wizards"
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
        # Subclasses provide their own defaults for name, domain, empathy_level
        temp_instance = wizard_class()  # type: ignore[call-arg]

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
