"""Software Development Plugin for Empathy Framework

This plugin provides 16+ Coach wizards for code analysis,
demonstrating Level 4 Anticipatory Empathy in software development.

Based on real-world experience developing AI systems where the framework
transformed productivity with higher quality code developed many times faster.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
import os

# Import from core framework
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from empathy_os.plugins import BasePlugin, BaseWizard, PluginMetadata

logger = logging.getLogger(__name__)


class SoftwarePlugin(BasePlugin):
    """Software Development Domain Plugin

    Provides wizards for:
    - Security analysis
    - Performance optimization
    - Architecture review
    - Testing strategy
    - Code quality assessment
    - And more...

    All wizards operate at Level 3 (Proactive) or Level 4 (Anticipatory)
    empathy levels.
    """

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="Empathy Framework - Software Development",
            version="1.0.0",
            domain="software",
            description=(
                "16+ Coach wizards for code analysis and anticipatory "
                "software development. Alerts you to bottlenecks, security "
                "vulnerabilities, and architectural issues before they "
                "become critical."
            ),
            author="Smart AI Memory, LLC",
            license="Apache-2.0",
            requires_core_version="1.0.0",
            dependencies=[],  # Add any domain-specific deps
        )

    def register_wizards(self) -> dict[str, type[BaseWizard]]:
        """Register all software development wizards.

        In our experience building these wizards, we found that the framework
        enables a fundamental shift: instead of reactive debugging, the system
        alerts you to emerging issues that would surface weeks later.
        """
        wizards = {}

        # Import wizards with graceful degradation
        # (some wizards may have optional dependencies)

        try:
            from .wizards.security_wizard import SecurityWizard

            wizards["security"] = SecurityWizard
        except ImportError as e:
            logger.warning(f"SecurityWizard not available: {e}")

        try:
            from .wizards.performance_wizard import PerformanceWizard

            wizards["performance"] = PerformanceWizard
        except ImportError as e:
            logger.warning(f"PerformanceWizard not available: {e}")

        try:
            from .wizards.testing_wizard import TestingWizard

            wizards["testing"] = TestingWizard
        except ImportError as e:
            logger.warning(f"TestingWizard not available: {e}")

        try:
            from .wizards.architecture_wizard import ArchitectureWizard

            wizards["architecture"] = ArchitectureWizard
        except ImportError as e:
            logger.warning(f"ArchitectureWizard not available: {e}")

        # AI Development Wizards (Level 4 Anticipatory)
        try:
            from .wizards.prompt_engineering_wizard import PromptEngineeringWizard

            wizards["prompt_engineering"] = PromptEngineeringWizard
        except ImportError as e:
            logger.warning(f"PromptEngineeringWizard not available: {e}")

        try:
            from .wizards.ai_context_wizard import AIContextWindowWizard

            wizards["context_window"] = AIContextWindowWizard
        except ImportError as e:
            logger.warning(f"AIContextWindowWizard not available: {e}")

        try:
            from .wizards.ai_collaboration_wizard import AICollaborationWizard

            wizards["collaboration_pattern"] = AICollaborationWizard
        except ImportError as e:
            logger.warning(f"AICollaborationWizard not available: {e}")

        try:
            from .wizards.ai_documentation_wizard import AIDocumentationWizard

            wizards["ai_documentation"] = AIDocumentationWizard
        except ImportError as e:
            logger.warning(f"AIDocumentationWizard not available: {e}")

        try:
            from .wizards.agent_orchestration_wizard import AgentOrchestrationWizard

            wizards["agent_orchestration"] = AgentOrchestrationWizard
        except ImportError as e:
            logger.warning(f"AgentOrchestrationWizard not available: {e}")

        try:
            from .wizards.rag_pattern_wizard import RAGPatternWizard

            wizards["rag_pattern"] = RAGPatternWizard
        except ImportError as e:
            logger.warning(f"RAGPatternWizard not available: {e}")

        try:
            from .wizards.multi_model_wizard import MultiModelWizard

            wizards["multi_model"] = MultiModelWizard
        except ImportError as e:
            logger.warning(f"MultiModelWizard not available: {e}")

        # Add remaining wizards...
        # In production, you'd import all 16+ wizards

        logger.info(f"Software plugin registered {len(wizards)} wizards")

        return wizards

    def register_patterns(self) -> dict:
        """Register software development patterns.

        These patterns were learned from real-world usage and enable
        cross-domain learning (Level 5 Systems Empathy).
        """
        return {
            "domain": "software",
            "patterns": {
                "testing_bottleneck": {
                    "description": (
                        "Manual testing burden grows faster than team size. "
                        "Alert: When test count > 25 or test time > 15min, "
                        "recommend automation framework."
                    ),
                    "indicators": ["test_count_growth_rate", "manual_test_time", "wizard_count"],
                    "threshold": "test_time > 900 seconds",
                    "recommendation": "Implement test automation framework",
                },
                "security_drift": {
                    "description": (
                        "Security practices degrade over time without active "
                        "monitoring. Alert: When new code bypasses security "
                        "patterns established in existing code."
                    ),
                    "indicators": [
                        "input_validation_coverage",
                        "authentication_consistency",
                        "data_sanitization_patterns",
                    ],
                },
            },
        }
