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

    # XML-enhanced prompts (Phase 4)
    xml_prompts_enabled: bool = True  # Enable by default for better Claude API performance
    xml_schema_version: str = "1.0"
    enforce_xml_response: bool = False  # Require XML-structured responses


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

    # =========================================================================
    # XML-Enhanced Prompt Support (Phase 4)
    # =========================================================================

    def _is_xml_enabled(self) -> bool:
        """Check if XML prompts are enabled for this wizard."""
        return self.config.xml_prompts_enabled

    def _render_xml_prompt(
        self,
        role: str,
        goal: str,
        instructions: list[str],
        constraints: list[str],
        input_type: str,
        input_payload: str,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Render a wizard prompt using XML structure.

        This method follows Claude API best practices for XML-enhanced prompts,
        providing clearer structure and better performance.

        Args:
            role: The role/expertise for the AI (e.g., "registered nurse")
            goal: The primary objective of the task
            instructions: Step-by-step instructions list
            constraints: Guidelines and boundaries list
            input_type: Type of input data (e.g., "patient_data", "code", "document")
            input_payload: The actual input content
            extra: Additional context fields (optional)

        Returns:
            XML-formatted prompt string

        Example:
            prompt = self._render_xml_prompt(
                role="HIPAA compliance specialist",
                goal="Review patient handoff for completeness",
                instructions=[
                    "Check for required SBAR elements",
                    "Verify patient identifiers present",
                    "Confirm allergies documented",
                ],
                constraints=[
                    "Follow Joint Commission standards",
                    "Maintain professional medical terminology",
                ],
                input_type="shift_handoff",
                input_payload=json.dumps(handoff_data),
            )

        """
        if not self._is_xml_enabled():
            # Fallback to plain text if XML disabled
            return self._render_plain_prompt(
                role,
                goal,
                instructions,
                constraints,
                input_payload,
            )

        parts = [f'<task role="{role}" version="{self.config.xml_schema_version}">']
        parts.append(f"  <goal>{goal}</goal>")
        parts.append("")

        if instructions:
            parts.append("  <instructions>")
            for i, inst in enumerate(instructions, 1):
                parts.append(f"    {i}. {inst}")
            parts.append("  </instructions>")
            parts.append("")

        if constraints:
            parts.append("  <constraints>")
            for constraint in constraints:
                parts.append(f"    - {constraint}")
            parts.append("  </constraints>")
            parts.append("")

        # Add extra context if provided
        if extra:
            parts.append("  <context>")
            for key, value in extra.items():
                parts.append(f"    <{key}>{value}</{key}>")
            parts.append("  </context>")
            parts.append("")

        parts.append(f'  <input type="{input_type}">')
        parts.append(f"    {input_payload}")
        parts.append("  </input>")
        parts.append("</task>")

        return "\n".join(parts)

    def _render_plain_prompt(
        self,
        role: str,
        goal: str,
        instructions: list[str],
        constraints: list[str],
        input_payload: str,
    ) -> str:
        """Render plain text prompt (fallback for non-XML mode).

        Args:
            role: The role/expertise for the AI
            goal: The primary objective
            instructions: Step-by-step instructions
            constraints: Guidelines and boundaries
            input_payload: The input content

        Returns:
            Plain text formatted prompt

        """
        parts = [f"Role: {role}"]
        parts.append(f"Goal: {goal}")
        parts.append("")

        if instructions:
            parts.append("Instructions:")
            for i, inst in enumerate(instructions, 1):
                parts.append(f"{i}. {inst}")
            parts.append("")

        if constraints:
            parts.append("Guidelines:")
            for constraint in constraints:
                parts.append(f"- {constraint}")
            parts.append("")

        parts.append("Input:")
        parts.append(input_payload)

        return "\n".join(parts)

    def _parse_xml_response(self, response: str) -> dict[str, Any]:
        """Parse XML-structured response if enforcement is enabled.

        Args:
            response: The LLM response text

        Returns:
            Dictionary with parsed fields or raw response

        Note:
            This is a basic parser. For production use, consider
            using the full XmlResponseParser from empathy_os.prompts.

        """
        if not self.config.enforce_xml_response:
            return {"xml_parsed": False, "content": response}

        # Basic XML parsing - extract common tags
        import re

        result: dict[str, Any] = {"xml_parsed": True}

        # Extract <summary> tag
        summary_match = re.search(r"<summary>(.*?)</summary>", response, re.DOTALL)
        if summary_match:
            result["summary"] = summary_match.group(1).strip()

        # Extract <recommendation> tags
        recommendations = re.findall(r"<recommendation>(.*?)</recommendation>", response, re.DOTALL)
        if recommendations:
            result["recommendations"] = [r.strip() for r in recommendations]

        # Extract <finding> tags
        findings = re.findall(r"<finding>(.*?)</finding>", response, re.DOTALL)
        if findings:
            result["findings"] = [f.strip() for f in findings]

        # Always include raw content
        result["content"] = response

        return result

    def get_config(self) -> WizardConfig:
        """Get wizard configuration"""
        return self.config

    def get_name(self) -> str:
        """Get wizard name"""
        return self.config.name
