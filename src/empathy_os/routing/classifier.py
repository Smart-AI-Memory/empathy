"""LLM-based Request Classifier

Uses a cheap model (Haiku) to classify developer requests
and route them to appropriate wizard(s).

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any

from .wizard_registry import WizardRegistry


@dataclass
class ClassificationResult:
    """Result of classifying a developer request."""

    primary_wizard: str
    secondary_wizards: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    suggested_chain: list[str] = field(default_factory=list)
    extracted_context: dict[str, Any] = field(default_factory=dict)


class HaikuClassifier:
    """Uses Claude Haiku to classify requests to wizards.

    Why Haiku:
    - Cheapest tier model
    - Fast response times
    - Sufficient for classification tasks
    - Cost-effective for high-volume routing
    """

    def __init__(self, api_key: str | None = None):
        """Initialize the classifier.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)

        """
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client = None
        self._registry = WizardRegistry()

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None and self._api_key:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                pass
        return self._client

    async def classify(
        self,
        request: str,
        context: dict[str, Any] | None = None,
        available_wizards: dict[str, str] | None = None,
    ) -> ClassificationResult:
        """Classify a developer request and determine which wizard(s) to invoke.

        Args:
            request: The developer's natural language request
            context: Optional context (current file, project type, etc.)
            available_wizards: Override for available wizard descriptions

        Returns:
            ClassificationResult with primary and secondary wizard recommendations

        """
        if available_wizards is None:
            available_wizards = self._registry.get_descriptions_for_classification()

        # Build classification prompt
        wizard_list = "\n".join(f"- {name}: {desc}" for name, desc in available_wizards.items())

        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}"

        system_prompt = """You are a request router that classifies requests to the appropriate wizard.

Analyze the request and determine:
1. The PRIMARY wizard that best handles this request
2. Any SECONDARY wizards that could provide additional value
3. Your confidence level (0.0 - 1.0)
4. Brief reasoning for your choice

Respond in JSON format:
{
    "primary_wizard": "wizard-name",
    "secondary_wizards": ["wizard-name-2"],
    "confidence": 0.85,
    "reasoning": "Brief explanation",
    "extracted_context": {
        "file_mentioned": "auth.py",
        "issue_type": "performance"
    }
}"""

        user_prompt = f"""Available wizards:
{wizard_list}

Developer request: "{request}"{context_str}

Classify this request."""

        # Try LLM classification
        client = self._get_client()
        if client:
            try:
                response = client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )

                content = response.content[0].text if response.content else "{}"

                # Parse JSON response
                try:
                    # Extract JSON from response (handle markdown code blocks)
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0]
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0]

                    data = json.loads(content.strip())
                    return ClassificationResult(
                        primary_wizard=data.get("primary_wizard", "code-review"),
                        secondary_wizards=data.get("secondary_wizards", []),
                        confidence=data.get("confidence", 0.5),
                        reasoning=data.get("reasoning", ""),
                        extracted_context=data.get("extracted_context", {}),
                    )
                except json.JSONDecodeError:
                    pass

            except Exception as e:
                print(f"LLM classification error: {e}")

        # Fallback to keyword-based classification
        return self._keyword_classify(request, available_wizards)

    def _keyword_classify(
        self,
        request: str,
        available_wizards: dict[str, str],
    ) -> ClassificationResult:
        """Fallback keyword-based classification."""
        request_lower = request.lower()

        # Score each wizard based on keyword matches
        scores: dict[str, float] = {}

        for wizard in self._registry.list_all():
            score = 0.0
            for keyword in wizard.keywords:
                if keyword in request_lower:
                    score += 1.0
                    # Exact word match bonus
                    if f" {keyword} " in f" {request_lower} ":
                        score += 0.5

            if score > 0:
                scores[wizard.name] = score

        if not scores:
            # Default to code-review
            return ClassificationResult(
                primary_wizard="code-review",
                confidence=0.3,
                reasoning="No keyword matches, defaulting to code-review",
            )

        # Sort by score
        sorted_wizards = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_wizards[0][0]
        primary_score = sorted_wizards[0][1]

        # Get secondary if significantly different
        secondary = []
        if len(sorted_wizards) > 1:
            for name, score in sorted_wizards[1:3]:
                if score >= primary_score * 0.5:
                    secondary.append(name)

        # Normalize confidence
        max_possible = max(len(w.keywords) for w in self._registry.list_all())
        confidence = min(primary_score / max_possible, 1.0)

        return ClassificationResult(
            primary_wizard=primary,
            secondary_wizards=secondary,
            confidence=confidence,
            reasoning=f"Keyword match score: {primary_score}",
        )

    def classify_sync(
        self,
        request: str,
        context: dict[str, Any] | None = None,
    ) -> ClassificationResult:
        """Synchronous classification using keyword matching only."""
        return self._keyword_classify(
            request,
            self._registry.get_descriptions_for_classification(),
        )
