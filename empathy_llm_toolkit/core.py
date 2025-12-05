"""
Empathy LLM - Core Wrapper

Main class that wraps any LLM provider with Empathy Framework levels.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
import time
from typing import Any

from .claude_memory import ClaudeMemoryConfig, ClaudeMemoryLoader
from .levels import EmpathyLevel
from .providers import AnthropicProvider, BaseLLMProvider, LocalProvider, OpenAIProvider
from .security import AuditLogger, PIIScrubber, SecretsDetector, SecurityError
from .state import CollaborationState, UserPattern

logger = logging.getLogger(__name__)


class EmpathyLLM:
    """
    Wraps any LLM provider with Empathy Framework levels.

    Automatically progresses from Level 1 (reactive) to Level 4 (anticipatory)
    based on user collaboration state.

    Security Features (Phase 3):
        - PII Scrubbing: Automatically detect and redact PII from user inputs
        - Secrets Detection: Block requests containing API keys, passwords, etc.
        - Audit Logging: Comprehensive compliance logging (SOC2, HIPAA, GDPR)
        - Backward Compatible: Security disabled by default

    Example:
        >>> llm = EmpathyLLM(provider="anthropic", target_level=4)
        >>> response = await llm.interact(
        ...     user_id="developer_123",
        ...     user_input="Help me optimize my code",
        ...     context={"code_snippet": "..."}
        ... )
        >>> print(response["content"])

    Example with Security:
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     target_level=4,
        ...     enable_security=True,
        ...     security_config={
        ...         "audit_log_dir": "/var/log/empathy",
        ...         "block_on_secrets": True,
        ...         "enable_pii_scrubbing": True
        ...     }
        ... )
        >>> response = await llm.interact(
        ...     user_id="user@company.com",
        ...     user_input="My email is john@example.com"
        ... )
        >>> # PII automatically scrubbed, request logged
    """

    def __init__(
        self,
        provider: str = "anthropic",
        target_level: int = 3,
        api_key: str | None = None,
        model: str | None = None,
        pattern_library: dict | None = None,
        claude_memory_config: ClaudeMemoryConfig | None = None,
        project_root: str | None = None,
        enable_security: bool = False,
        security_config: dict | None = None,
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
            claude_memory_config: Configuration for Claude memory integration (v1.8.0+)
            project_root: Project root directory for loading .claude/CLAUDE.md
            enable_security: Enable Phase 2 security controls (default: False)
            security_config: Security configuration dictionary with options:
                - audit_log_dir: Directory for audit logs (default: "./logs")
                - block_on_secrets: Block requests with detected secrets (default: True)
                - enable_pii_scrubbing: Enable PII detection/scrubbing (default: True)
                - enable_name_detection: Enable name PII detection (default: False)
                - enable_audit_logging: Enable audit logging (default: True)
                - enable_console_logging: Log to console for debugging (default: False)
            **kwargs: Provider-specific options
        """
        self.target_level = target_level
        self.pattern_library = pattern_library or {}
        self.project_root = project_root

        # Initialize provider
        self.provider = self._create_provider(provider, api_key, model, **kwargs)

        # Track collaboration states for different users
        self.states: dict[str, CollaborationState] = {}

        # Initialize Claude memory integration (v1.8.0+)
        self.claude_memory_config = claude_memory_config
        self.claude_memory_loader = None
        self._cached_memory = None

        if claude_memory_config and claude_memory_config.enabled:
            self.claude_memory_loader = ClaudeMemoryLoader(claude_memory_config)
            # Load memory once at initialization
            self._cached_memory = self.claude_memory_loader.load_all_memory(project_root)
            logger.info(
                f"EmpathyLLM initialized with Claude memory: "
                f"{len(self._cached_memory)} chars loaded"
            )

        # Initialize Phase 3 security controls (v1.8.0+)
        self.enable_security = enable_security
        self.security_config = security_config or {}
        self.pii_scrubber = None
        self.secrets_detector = None
        self.audit_logger = None

        if enable_security:
            self._initialize_security()

        logger.info(
            f"EmpathyLLM initialized: provider={provider}, target_level={target_level}, "
            f"security={'enabled' if enable_security else 'disabled'}"
        )

    def _initialize_security(self):
        """Initialize Phase 3 security modules based on configuration"""
        # Extract security config options
        enable_pii_scrubbing = self.security_config.get("enable_pii_scrubbing", True)
        enable_name_detection = self.security_config.get("enable_name_detection", False)
        enable_audit_logging = self.security_config.get("enable_audit_logging", True)
        audit_log_dir = self.security_config.get("audit_log_dir", "./logs")
        enable_console_logging = self.security_config.get("enable_console_logging", False)

        # Initialize PII Scrubber
        if enable_pii_scrubbing:
            self.pii_scrubber = PIIScrubber(enable_name_detection=enable_name_detection)
            logger.info("PII Scrubber initialized")

        # Initialize Secrets Detector
        self.secrets_detector = SecretsDetector(
            enable_entropy_analysis=True,
            entropy_threshold=4.5,
            min_entropy_length=20,
        )
        logger.info("Secrets Detector initialized")

        # Initialize Audit Logger
        if enable_audit_logging:
            self.audit_logger = AuditLogger(
                log_dir=audit_log_dir,
                enable_console_logging=enable_console_logging,
            )
            logger.info(f"Audit Logger initialized: {audit_log_dir}")

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

    def _build_system_prompt(self, level: int) -> str:
        """
        Build system prompt including Claude memory (if enabled).

        Claude memory is prepended to the level-specific prompt,
        so instructions from CLAUDE.md files affect all interactions.

        Args:
            level: Empathy level (1-5)

        Returns:
            Complete system prompt
        """
        level_prompt = EmpathyLevel.get_system_prompt(level)

        # If Claude memory is enabled and loaded, prepend it
        if self._cached_memory:
            return f"""{self._cached_memory}

---
# Empathy Framework Instructions
{level_prompt}

Follow the instructions from CLAUDE.md files above, then apply the Empathy Framework guidelines below.
"""
        else:
            return level_prompt

    def reload_memory(self):
        """
        Reload Claude memory files.

        Useful if CLAUDE.md files have been updated during runtime.
        Call this to pick up changes without restarting.
        """
        if self.claude_memory_loader:
            # Clear cache before reloading to pick up file changes
            self.claude_memory_loader.clear_cache()
            self._cached_memory = self.claude_memory_loader.load_all_memory(self.project_root)
            logger.info(f"Claude memory reloaded: {len(self._cached_memory)} chars")
        else:
            logger.warning("Claude memory not enabled, cannot reload")

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

        Phase 3 Security Pipeline (if enabled):
            1. PII Scrubbing: Detect and redact PII from user input
            2. Secrets Detection: Block requests containing secrets
            3. LLM Interaction: Process sanitized input
            4. Audit Logging: Log request details for compliance

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
                - security: Security details (if enabled)

        Raises:
            SecurityError: If secrets detected and block_on_secrets=True
        """
        start_time = time.time()
        state = self._get_or_create_state(user_id)
        context = context or {}

        # Initialize security tracking
        pii_detections = []
        secrets_detections = []
        sanitized_input = user_input
        security_metadata = {}

        # Phase 3: Security Pipeline (Step 1 - PII Scrubbing)
        if self.enable_security and self.pii_scrubber:
            sanitized_input, pii_detections = self.pii_scrubber.scrub(user_input)
            security_metadata["pii_detected"] = len(pii_detections)
            security_metadata["pii_scrubbed"] = len(pii_detections) > 0
            if pii_detections:
                logger.info(
                    f"PII detected for user {user_id}: {len(pii_detections)} items scrubbed"
                )

        # Phase 3: Security Pipeline (Step 2 - Secrets Detection)
        if self.enable_security and self.secrets_detector:
            secrets_detections = self.secrets_detector.detect(sanitized_input)
            security_metadata["secrets_detected"] = len(secrets_detections)

            if secrets_detections:
                block_on_secrets = self.security_config.get("block_on_secrets", True)
                logger.warning(
                    f"Secrets detected for user {user_id}: {len(secrets_detections)} secrets, "
                    f"blocking={block_on_secrets}"
                )

                # Log security violation
                if self.audit_logger:
                    self.audit_logger.log_security_violation(
                        user_id=user_id,
                        violation_type="secrets_detected",
                        severity="HIGH",
                        details={
                            "secret_count": len(secrets_detections),
                            "secret_types": [s.secret_type.value for s in secrets_detections],
                            "event_type": "llm_request",
                        },
                        blocked=block_on_secrets,
                    )

                if block_on_secrets:
                    raise SecurityError(
                        f"Request blocked: {len(secrets_detections)} secret(s) detected in input. "
                        f"Please remove sensitive credentials before submitting."
                    )

        # Determine level to use
        level = force_level if force_level is not None else self._determine_level(state)

        logger.info(f"User {user_id}: Level {level} interaction")

        # Record user input (sanitized version if security enabled)
        state.add_interaction("user", sanitized_input, level)

        # Phase 3: Security Pipeline (Step 3 - LLM Interaction with sanitized input)
        # Route to appropriate level handler using sanitized input
        if level == 1:
            result = await self._level_1_reactive(sanitized_input, state, context)
        elif level == 2:
            result = await self._level_2_guided(sanitized_input, state, context)
        elif level == 3:
            result = await self._level_3_proactive(sanitized_input, state, context)
        elif level == 4:
            result = await self._level_4_anticipatory(sanitized_input, state, context)
        elif level == 5:
            result = await self._level_5_systems(sanitized_input, state, context)
        else:
            raise ValueError(f"Invalid level: {level}")

        # Record assistant response
        state.add_interaction("assistant", result["content"], level, result.get("metadata"))

        # Add level info to result
        result["level_used"] = level
        result["level_description"] = EmpathyLevel.get_description(level)

        # Add security metadata to result
        if self.enable_security:
            result["security"] = security_metadata

        # Phase 3: Security Pipeline (Step 4 - Audit Logging)
        if self.enable_security and self.audit_logger:
            duration_ms = int((time.time() - start_time) * 1000)

            # Calculate approximate sizes
            request_size_bytes = len(user_input.encode("utf-8"))
            response_size_bytes = len(result["content"].encode("utf-8"))

            # Extract memory sources if Claude Memory is enabled
            memory_sources = []
            if self._cached_memory:
                memory_sources = ["claude_memory"]

            self.audit_logger.log_llm_request(
                user_id=user_id,
                empathy_level=level,
                provider=self.provider.__class__.__name__.replace("Provider", "").lower(),
                model=result.get("metadata", {}).get("model", "unknown"),
                memory_sources=memory_sources,
                pii_count=len(pii_detections),
                secrets_count=len(secrets_detections),
                request_size_bytes=request_size_bytes,
                response_size_bytes=response_size_bytes,
                duration_ms=duration_ms,
                sanitization_applied=len(pii_detections) > 0,
                classification_verified=True,
                status="success",
            )

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
            system_prompt=self._build_system_prompt(1),
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
            system_prompt=self._build_system_prompt(2),
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
            system_prompt=self._build_system_prompt(3),
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
            system_prompt=self._build_system_prompt(4),
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
            system_prompt=self._build_system_prompt(5),
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
