"""Base Wizard - Foundation for all EmpathyLLM wizards

Provides common functionality for security-aware AI assistants with domain-specific
configurations and integrated privacy controls.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig

logger = logging.getLogger(__name__)


@dataclass
class WizardConfig:
    """Configuration for an Empathy wizard"""

    # Wizard identity
    name: str
    description: str
    domain: str  # healthcare, finance, legal, general, etc.

    # Empathy level (0-4)
    default_empathy_level: int = 2

    # Security configuration
    enable_security: bool = False
    pii_patterns: list[str] = field(default_factory=list)
    enable_secrets_detection: bool = False
    block_on_secrets: bool = True

    # Audit configuration
    audit_all_access: bool = False
    retention_days: int = 180

    # Classification
    default_classification: str = "INTERNAL"  # PUBLIC, INTERNAL, SENSITIVE
    auto_classify: bool = True

    # Memory configuration
    enable_memory: bool = False
    memory_config: ClaudeMemoryConfig | None = None


class BaseWizard:
    """Base class for all Empathy LLM wizards

    Provides:
    - Integration with EmpathyLLM
    - Security pipeline configuration
    - Domain-specific prompting
    - Audit logging
    - Session management
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        config: WizardConfig,
    ):
        """Initialize wizard with LLM and configuration

        Args:
            llm: EmpathyLLM instance (with or without security enabled)
            config: Wizard configuration

        """
        self.llm = llm
        self.config = config
        self.logger = logging.getLogger(f"wizard.{config.name}")

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate wizard configuration"""
        if not 0 <= self.config.default_empathy_level <= 4:
            raise ValueError(f"Empathy level must be 0-4, got {self.config.default_empathy_level}")

        if self.config.default_classification not in ["PUBLIC", "INTERNAL", "SENSITIVE"]:
            raise ValueError(f"Invalid classification: {self.config.default_classification}")

    async def process(
        self,
        user_input: str,
        user_id: str,
        empathy_level: int | None = None,
        session_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process user input through the wizard

        Args:
            user_input: User's message or request
            user_id: Identifier for the user
            empathy_level: Override default empathy level (optional)
            session_context: Additional context for the conversation

        Returns:
            Dictionary containing:
                - response: AI response
                - empathy_level: Level used
                - security_report: Security scan results (if enabled)
                - metadata: Additional wizard metadata

        """
        level = empathy_level if empathy_level is not None else self.config.default_empathy_level

        self.logger.info(
            "processing_request: wizard=%s user_id=%s empathy_level=%s",
            self.config.name,
            user_id,
            level,
        )

        # Build system prompt with domain knowledge
        system_prompt = self._build_system_prompt()

        # Add session context if provided
        if session_context:
            context_str = self._format_context(session_context)
            user_input = f"{context_str}\n\n{user_input}"

        # Process through EmpathyLLM (with security if enabled)
        # Note: EmpathyLLM uses 'force_level' and 'context' parameters
        context_dict = session_context.copy() if session_context else {}
        context_dict["system_prompt"] = system_prompt

        result = await self.llm.interact(
            user_id=user_id,
            user_input=user_input,
            force_level=level,
            context=context_dict,
        )

        # Enhance result with wizard metadata
        result["wizard"] = {
            "name": self.config.name,
            "domain": self.config.domain,
            "empathy_level": level,
        }

        return result

    def _build_system_prompt(self) -> str:
        """Build domain-specific system prompt

        Override in subclasses to add domain knowledge
        """
        return f"""You are an AI assistant specialized in {self.config.domain}.

Description: {self.config.description}

Guidelines:
- Provide accurate, helpful responses
- Be empathetic and understanding
- Follow domain best practices
- Maintain user privacy and confidentiality
"""

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format session context for inclusion in prompt"""
        lines = ["Context:"]
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def get_config(self) -> WizardConfig:
        """Get wizard configuration"""
        return self.config

    def get_name(self) -> str:
        """Get wizard name"""
        return self.config.name
