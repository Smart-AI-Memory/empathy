"""
Empathy LLM - Core Wrapper

Main class that wraps any LLM provider with Empathy Framework levels.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
from typing import Any

from .levels import EmpathyLevel
from .providers import AnthropicProvider, BaseLLMProvider, LocalProvider, OpenAIProvider
from .state import CollaborationState, UserPattern

logger = logging.getLogger(__name__)


class EmpathyLLM:
    """
    Wraps any LLM provider with Empathy Framework levels.

    Automatically progresses from Level 1 (reactive) to Level 4 (anticipatory)
    based on user collaboration state.

    Example:
        >>> llm = EmpathyLLM(provider="anthropic", target_level=4)
        >>> response = await llm.interact(
        ...     user_id="developer_123",
        ...     user_input="Help me optimize my code",
        ...     context={"code_snippet": "..."}
        ... )
        >>> print(response["content"])
    """

    def __init__(
        self,
        provider: str = "anthropic",
        target_level: int = 3,
        api_key: str | None = None,
        model: str | None = None,
        pattern_library: dict | None = None,
        **kwargs,
    ):
        """
        Initialize EmpathyLLM.

        Args:
            provider: "anthropic", "openai", or "local"
            target_level: Target empathy level (1-5)
            api_key: API key for provider (if needed)
            model: Specific model to use
            pattern_library: Shared pattern library (Level 5)
            **kwargs: Provider-specific options
        """
        self.target_level = target_level
        self.pattern_library = pattern_library or {}

        # Initialize provider
        self.provider = self._create_provider(provider, api_key, model, **kwargs)

        # Track collaboration states for different users
        self.states: dict[str, CollaborationState] = {}

        logger.info(f"EmpathyLLM initialized: provider={provider}, target_level={target_level}")

    def _create_provider(
        self, provider: str, api_key: str | None, model: str | None, **kwargs
    ) -> BaseLLMProvider:
        """Create appropriate provider instance"""

        if provider == "anthropic":
            return AnthropicProvider(
                api_key=api_key, model=model or "claude-sonnet-4-5-20250929", **kwargs
            )
        elif provider == "openai":
            return OpenAIProvider(api_key=api_key, model=model or "gpt-4-turbo-preview", **kwargs)
        elif provider == "local":
            return LocalProvider(
                endpoint=kwargs.get("endpoint", "http://localhost:11434"),
                model=model or "llama2",
                **kwargs,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _get_or_create_state(self, user_id: str) -> CollaborationState:
        """Get or create collaboration state for user"""
        if user_id not in self.states:
            self.states[user_id] = CollaborationState(user_id=user_id)
        return self.states[user_id]

    def _determine_level(self, state: CollaborationState) -> int:
        """
        Determine which empathy level to use.

        Progresses automatically based on state, up to target_level.
        """
        # Start at Level 1
        level = 1

        # Progress through levels if state allows
        for candidate_level in range(2, self.target_level + 1):
            if state.should_progress_to_level(candidate_level):
                level = candidate_level
            else:
                break

        return level

    async def interact(
        self,
        user_id: str,
        user_input: str,
        context: dict[str, Any] | None = None,
        force_level: int | None = None,
    ) -> dict[str, Any]:
        """
        Main interaction method.

        Automatically selects appropriate empathy level and responds.

        Args:
            user_id: Unique user identifier
            user_input: User's input/question
            context: Optional context dictionary
            force_level: Force specific level (for testing/demos)

        Returns:
            Dictionary with:
                - content: LLM response
                - level_used: Which empathy level was used
                - proactive: Whether action was proactive
                - metadata: Additional information
        """
        state = self._get_or_create_state(user_id)
        context = context or {}

        # Determine level to use
        level = force_level if force_level is not None else self._determine_level(state)

        logger.info(f"User {user_id}: Level {level} interaction")

        # Record user input
        state.add_interaction("user", user_input, level)

        # Route to appropriate level handler
        if level == 1:
            result = await self._level_1_reactive(user_input, state, context)
        elif level == 2:
            result = await self._level_2_guided(user_input, state, context)
        elif level == 3:
            result = await self._level_3_proactive(user_input, state, context)
        elif level == 4:
            result = await self._level_4_anticipatory(user_input, state, context)
        elif level == 5:
            result = await self._level_5_systems(user_input, state, context)
        else:
            raise ValueError(f"Invalid level: {level}")

        # Record assistant response
        state.add_interaction("assistant", result["content"], level, result.get("metadata"))

        # Add level info to result
        result["level_used"] = level
        result["level_description"] = EmpathyLevel.get_description(level)

        return result

    async def _level_1_reactive(
        self, user_input: str, state: CollaborationState, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Level 1: Reactive - Simple Q&A

        No memory, no patterns, just respond to question.
        """
        response = await self.provider.generate(
            messages=[{"role": "user", "content": user_input}],
            system_prompt=EmpathyLevel.get_system_prompt(1),
            temperature=EmpathyLevel.get_temperature_recommendation(1),
            max_tokens=EmpathyLevel.get_max_tokens_recommendation(1),
        )

        return {
            "content": response.content,
            "proactive": False,
            "metadata": {"tokens_used": response.tokens_used, "model": response.model},
        }

    async def _level_2_guided(
        self, user_input: str, state: CollaborationState, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Level 2: Guided - Ask clarifying questions

        Uses conversation history for context.
        """
        # Include conversation history
        messages = state.get_conversation_history(max_turns=5)
        messages.append({"role": "user", "content": user_input})

        response = await self.provider.generate(
            messages=messages,
            system_prompt=EmpathyLevel.get_system_prompt(2),
            temperature=EmpathyLevel.get_temperature_recommendation(2),
            max_tokens=EmpathyLevel.get_max_tokens_recommendation(2),
        )

        return {
            "content": response.content,
            "proactive": False,
            "metadata": {
                "tokens_used": response.tokens_used,
                "model": response.model,
                "history_turns": len(messages) - 1,
            },
        }

    async def _level_3_proactive(
        self, user_input: str, state: CollaborationState, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Level 3: Proactive - Act on detected patterns

        Checks for matching patterns and acts proactively.
        """
        # Check for matching pattern
        matching_pattern = state.find_matching_pattern(user_input)

        if matching_pattern:
            # Proactive action based on pattern
            prompt = f"""
User said: "{user_input}"

I've detected a pattern: When you {matching_pattern.trigger}, you typically {matching_pattern.action}.

Based on this pattern (confidence: {matching_pattern.confidence:.0%}), I'm proactively {matching_pattern.action}.

[Provide the expected result/action]

Was this helpful? If not, I can adjust my pattern detection.
"""

            messages = [{"role": "user", "content": prompt}]
            proactive = True
            pattern_info = {
                "pattern_type": matching_pattern.pattern_type.value,
                "trigger": matching_pattern.trigger,
                "confidence": matching_pattern.confidence,
            }

        else:
            # Standard response + pattern detection
            messages = state.get_conversation_history(max_turns=10)
            messages.append({"role": "user", "content": user_input})
            proactive = False
            pattern_info = None

            # TODO: Run pattern detection in background
            # await self._detect_patterns_async(state)

        response = await self.provider.generate(
            messages=messages,
            system_prompt=EmpathyLevel.get_system_prompt(3),
            temperature=EmpathyLevel.get_temperature_recommendation(3),
            max_tokens=EmpathyLevel.get_max_tokens_recommendation(3),
        )

        return {
            "content": response.content,
            "proactive": proactive,
            "metadata": {
                "tokens_used": response.tokens_used,
                "model": response.model,
                "pattern": pattern_info,
            },
        }

    async def _level_4_anticipatory(
        self, user_input: str, state: CollaborationState, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Level 4: Anticipatory - Predict future needs

        Analyzes trajectory and alerts to future bottlenecks.
        """
        # Build prompt with trajectory analysis context
        trajectory_prompt = f"""
User request: "{user_input}"

COLLABORATION CONTEXT:
- Total interactions: {len(state.interactions)}
- Trust level: {state.trust_level:.2f}
- Detected patterns: {len(state.detected_patterns)}
- Success rate: {state.successful_actions / (state.successful_actions + state.failed_actions) if (state.successful_actions + state.failed_actions) > 0 else 0:.0%}

TASK:
1. Respond to immediate request
2. Analyze trajectory (where is this headed?)
3. Predict future bottlenecks (if any)
4. Alert with prevention steps (if needed)

Use anticipatory format:
- Current state analysis
- Trajectory prediction
- Alert (if bottleneck predicted)
- Prevention steps (actionable)
- Reasoning (based on experience)
"""

        messages = state.get_conversation_history(max_turns=15)
        messages.append({"role": "user", "content": trajectory_prompt})

        response = await self.provider.generate(
            messages=messages,
            system_prompt=EmpathyLevel.get_system_prompt(4),
            temperature=EmpathyLevel.get_temperature_recommendation(4),
            max_tokens=EmpathyLevel.get_max_tokens_recommendation(4),
        )

        return {
            "content": response.content,
            "proactive": True,  # Level 4 is inherently proactive
            "metadata": {
                "tokens_used": response.tokens_used,
                "model": response.model,
                "trajectory_analyzed": True,
                "trust_level": state.trust_level,
            },
        }

    async def _level_5_systems(
        self, user_input: str, state: CollaborationState, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Level 5: Systems - Cross-domain pattern learning

        Leverages shared pattern library across domains.
        """
        # Include pattern library context
        pattern_context = ""
        if self.pattern_library:
            pattern_context = f"\n\nSHARED PATTERN LIBRARY:\n{self.pattern_library}"

        prompt = f"""
User request: "{user_input}"

{pattern_context}

TASK:
1. Respond to request
2. Check if relevant cross-domain patterns apply
3. Contribute new patterns if discovered
4. Show how principle generalizes across domains
"""

        messages = state.get_conversation_history(max_turns=20)
        messages.append({"role": "user", "content": prompt})

        response = await self.provider.generate(
            messages=messages,
            system_prompt=EmpathyLevel.get_system_prompt(5),
            temperature=EmpathyLevel.get_temperature_recommendation(5),
            max_tokens=EmpathyLevel.get_max_tokens_recommendation(5),
        )

        return {
            "content": response.content,
            "proactive": True,
            "metadata": {
                "tokens_used": response.tokens_used,
                "model": response.model,
                "pattern_library_size": len(self.pattern_library),
                "systems_level": True,
            },
        }

    def update_trust(self, user_id: str, outcome: str, magnitude: float = 1.0):
        """
        Update trust level based on interaction outcome.

        Args:
            user_id: User identifier
            outcome: "success" or "failure"
            magnitude: How much to adjust (0.0 to 1.0)
        """
        state = self._get_or_create_state(user_id)
        state.update_trust(outcome, magnitude)

        logger.info(f"Trust updated for {user_id}: {outcome} -> {state.trust_level:.2f}")

    def add_pattern(self, user_id: str, pattern: UserPattern):
        """
        Manually add a detected pattern.

        Args:
            user_id: User identifier
            pattern: UserPattern instance
        """
        state = self._get_or_create_state(user_id)
        state.add_pattern(pattern)

        logger.info(f"Pattern added for {user_id}: {pattern.pattern_type.value}")

    def get_statistics(self, user_id: str) -> dict[str, Any]:
        """
        Get collaboration statistics for user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with stats
        """
        state = self._get_or_create_state(user_id)
        return state.get_statistics()

    def reset_state(self, user_id: str):
        """Reset collaboration state for user"""
        if user_id in self.states:
            del self.states[user_id]
            logger.info(f"State reset for {user_id}")
