"""Smart Router

Intelligent dispatcher that analyzes developer input and routes
to the appropriate wizard(s) using LLM classification.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from typing import Any

from .classifier import ClassificationResult, HaikuClassifier
from .wizard_registry import WizardInfo, WizardRegistry


@dataclass
class RoutingDecision:
    """Decision from the smart router."""

    primary_wizard: str
    secondary_wizards: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    suggested_chain: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    # Metadata
    classification_method: str = "llm"  # llm, keyword, manual
    request_summary: str = ""


class SmartRouter:
    """Routes developer requests to appropriate wizard(s).

    Uses LLM classification (Haiku) to understand natural language
    requests and route them to the best wizard(s).

    Usage:
        router = SmartRouter()

        # Async routing (preferred - uses LLM)
        decision = await router.route("Fix the security issue in auth.py")
        print(f"Primary: {decision.primary_wizard}")
        print(f"Confidence: {decision.confidence}")

        # Sync routing (keyword fallback)
        decision = router.route_sync("Optimize database queries")
    """

    def __init__(self, api_key: str | None = None):
        """Initialize the smart router.

        Args:
            api_key: Optional Anthropic API key for LLM classification

        """
        self._registry = WizardRegistry()
        self._classifier = HaikuClassifier(api_key=api_key)

    async def route(
        self,
        request: str,
        context: dict[str, Any] | None = None,
    ) -> RoutingDecision:
        """Route a request to the appropriate wizard(s).

        Uses LLM classification for accurate natural language understanding.

        Args:
            request: Developer's natural language request
            context: Optional context (current file, project info, etc.)

        Returns:
            RoutingDecision with wizard recommendations

        """
        # Classify the request
        classification = await self._classifier.classify(
            request=request,
            context=context,
        )

        # Build suggested chain based on wizard triggers
        suggested_chain = self._build_chain(classification)

        # Merge extracted context
        merged_context = {**(context or {}), **classification.extracted_context}

        return RoutingDecision(
            primary_wizard=classification.primary_wizard,
            secondary_wizards=classification.secondary_wizards,
            confidence=classification.confidence,
            reasoning=classification.reasoning,
            suggested_chain=suggested_chain,
            context=merged_context,
            classification_method="llm",
            request_summary=request[:100],
        )

    def route_sync(
        self,
        request: str,
        context: dict[str, Any] | None = None,
    ) -> RoutingDecision:
        """Synchronous routing using keyword matching.

        Faster but less accurate than LLM classification.

        Args:
            request: Developer's request
            context: Optional context

        Returns:
            RoutingDecision with wizard recommendations

        """
        classification = self._classifier.classify_sync(
            request=request,
            context=context,
        )

        suggested_chain = self._build_chain(classification)

        return RoutingDecision(
            primary_wizard=classification.primary_wizard,
            secondary_wizards=classification.secondary_wizards,
            confidence=classification.confidence,
            reasoning=classification.reasoning,
            suggested_chain=suggested_chain,
            context=context or {},
            classification_method="keyword",
            request_summary=request[:100],
        )

    def _build_chain(self, classification: ClassificationResult) -> list[str]:
        """Build suggested wizard chain based on triggers."""
        chain = [classification.primary_wizard]

        # Add secondary wizards to chain
        for secondary in classification.secondary_wizards:
            if secondary not in chain:
                chain.append(secondary)

        # Check for auto-chain triggers from primary wizard
        triggers = self._registry.get_chain_triggers(classification.primary_wizard)
        for trigger in triggers:
            next_wizard = trigger.get("next")
            if next_wizard and next_wizard not in chain:
                chain.append(next_wizard)

        return chain

    def get_wizard_info(self, name: str) -> WizardInfo | None:
        """Get information about a specific wizard."""
        return self._registry.get(name)

    def list_wizards(self) -> list[WizardInfo]:
        """List all available wizards."""
        return self._registry.list_all()

    def suggest_for_file(self, file_path: str) -> list[str]:
        """Suggest wizards based on file type.

        Args:
            file_path: Path to the file

        Returns:
            List of suggested wizard names

        """
        suggestions = []

        # Get file extension
        ext = "." + file_path.rsplit(".", 1)[-1] if "." in file_path else ""
        filename = file_path.rsplit("/", 1)[-1]

        for wizard in self._registry.list_all():
            if ext in wizard.handles_file_types or filename in wizard.handles_file_types:
                suggestions.append(wizard.name)

        # Default suggestions if no matches
        if not suggestions:
            suggestions = ["code-review", "security-audit"]

        return suggestions

    def suggest_for_error(self, error_type: str) -> list[str]:
        """Suggest wizards based on error type.

        Args:
            error_type: Type of error (e.g., "TypeError", "SecurityError")

        Returns:
            List of suggested wizard names

        """
        error_lower = error_type.lower()

        # Map error types to wizards
        error_wizard_map = {
            "security": ["security-audit", "code-review"],
            "type": ["code-review", "bug-predict"],
            "null": ["bug-predict", "test-gen"],
            "undefined": ["bug-predict", "test-gen"],
            "timeout": ["perf-audit", "bug-predict"],
            "memory": ["perf-audit", "code-review"],
            "import": ["dependency-check", "code-review"],
            "permission": ["security-audit", "code-review"],
            "syntax": ["code-review"],
            "test": ["test-gen", "bug-predict"],
        }

        for keyword, wizards in error_wizard_map.items():
            if keyword in error_lower:
                return wizards

        return ["bug-predict", "code-review"]


# Convenience function for quick routing
async def quick_route(request: str, context: dict | None = None) -> RoutingDecision:
    """Quick routing helper.

    Args:
        request: Developer request
        context: Optional context

    Returns:
        RoutingDecision

    """
    router = SmartRouter()
    return await router.route(request, context)
