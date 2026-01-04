"""Unified Agent Configuration

Single source of truth for all agent, wizard, and workflow configuration.
Uses Pydantic for validation and type safety.

This resolves the AgentConfig duplication between:
- empathy_llm_toolkit/agent_factory/base.py
- agents/book_production/base.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ModelTier(str, Enum):
    """Model tier for cost optimization."""

    CHEAP = "cheap"  # Haiku - fast, low cost
    CAPABLE = "capable"  # Sonnet - balanced
    PREMIUM = "premium"  # Opus - highest quality


class Provider(str, Enum):
    """LLM provider options."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LOCAL = "local"


class WorkflowMode(str, Enum):
    """Workflow execution modes."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    GRAPH = "graph"
    CONVERSATION = "conversation"


class AgentOperationError(Exception):
    """Error during agent operation with context."""

    def __init__(self, operation: str, cause: Exception):
        self.operation = operation
        self.cause = cause
        super().__init__(f"Agent operation '{operation}' failed: {cause}")


class UnifiedAgentConfig(BaseModel):
    """Unified configuration model for all agents.

    This is the single source of truth for agent configuration,
    replacing duplicate definitions across the codebase.

    Example:
        config = UnifiedAgentConfig(
            name="researcher",
            role="researcher",
            model_tier=ModelTier.CAPABLE,
            empathy_level=4
        )

    """

    # Identity
    name: str = Field(..., min_length=1, description="Unique agent name")
    role: str = Field(default="custom", description="Agent role (researcher, writer, etc.)")
    description: str = Field(default="", description="Agent description")

    # Model selection
    model_tier: ModelTier = Field(
        default=ModelTier.CAPABLE,
        description="Model tier for cost optimization",
    )
    model_override: str | None = Field(
        default=None,
        description="Specific model ID to use (overrides tier)",
    )
    provider: Provider = Field(default=Provider.ANTHROPIC, description="LLM provider")

    # Empathy Framework features
    empathy_level: int = Field(
        default=4,
        ge=1,
        le=5,
        description="Empathy level (1=Basic, 4=Anticipatory, 5=Transformative)",
    )

    # Feature flags
    memory_enabled: bool = Field(default=True, description="Enable conversation memory")
    pattern_learning: bool = Field(default=True, description="Enable pattern learning")
    cost_tracking: bool = Field(default=True, description="Track API costs")
    use_patterns: bool = Field(default=True, description="Use learned patterns")

    # LLM parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=200000)
    timeout: int = Field(default=120, ge=1, description="Timeout in seconds")

    # Retry configuration
    retry_attempts: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)

    # System prompt
    system_prompt: str | None = Field(default=None, description="Custom system prompt")

    # Tools and capabilities
    tools: list[Any] = Field(default_factory=list, description="Agent tools")
    capabilities: list[str] = Field(default_factory=list, description="Agent capabilities")

    # Framework-specific options
    framework_options: dict[str, Any] = Field(
        default_factory=dict,
        description="Framework-specific configuration",
    )

    # Extensions
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom configuration",
    )

    @field_validator("role")
    @classmethod
    def normalize_role(cls, v: str) -> str:
        """Normalize role to lowercase."""
        return v.lower().strip()

    def get_model_id(self) -> str:
        """Get the actual model ID based on tier and provider.

        Returns:
            Model identifier string

        """
        if self.model_override:
            return self.model_override

        # Model mapping by provider and tier
        models = {
            Provider.ANTHROPIC: {
                ModelTier.CHEAP: "claude-3-haiku-20240307",
                ModelTier.CAPABLE: "claude-sonnet-4-20250514",
                ModelTier.PREMIUM: "claude-opus-4-20250514",
            },
            Provider.OPENAI: {
                ModelTier.CHEAP: "gpt-4o-mini",
                ModelTier.CAPABLE: "gpt-4o",
                ModelTier.PREMIUM: "gpt-4o",
            },
            Provider.LOCAL: {
                ModelTier.CHEAP: "llama3.2:3b",
                ModelTier.CAPABLE: "llama3.1:8b",
                ModelTier.PREMIUM: "llama3.1:70b",
            },
        }

        return models.get(self.provider, {}).get(
            self.model_tier,
            "claude-sonnet-4-20250514",  # Fallback
        )

    def for_book_production(self) -> "BookProductionConfig":
        """Convert to BookProductionConfig for backward compatibility.

        Returns:
            BookProductionConfig instance

        """
        return BookProductionConfig(
            agent_config=self,
            memdocs_config=MemDocsConfig(),
            redis_config=RedisConfig(),
        )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class MemDocsConfig(BaseModel):
    """Configuration for MemDocs pattern storage integration."""

    enabled: bool = Field(default=True, description="Enable MemDocs integration")
    project: str = Field(default="empathy-framework", description="Project identifier")

    collections: dict[str, str] = Field(
        default_factory=lambda: {
            "patterns": "learned_patterns",
            "exemplars": "exemplar_examples",
            "transformations": "transformation_examples",
            "feedback": "quality_feedback",
        },
        description="Collection name mappings",
    )

    # Storage settings
    storage_path: str = Field(default="./patterns", description="Local storage path")
    encryption_enabled: bool = Field(default=False, description="Enable encryption")


class RedisConfig(BaseModel):
    """Configuration for Redis state management."""

    enabled: bool = Field(default=True, description="Enable Redis")
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535)
    db: int = Field(default=0, ge=0, le=15)
    password: str | None = Field(default=None, description="Redis password")

    prefix: str = Field(default="empathy", description="Key prefix")
    ttl: int = Field(default=86400, ge=0, description="Default TTL in seconds")

    # Connection pool settings
    max_connections: int = Field(default=10, ge=1)
    socket_timeout: float = Field(default=5.0, ge=0.1)


class BookProductionConfig(BaseModel):
    """Unified configuration for book production agents.

    Combines UnifiedAgentConfig with production-specific settings.
    This replaces the duplicate AgentConfig in agents/book_production/base.py.
    """

    agent_config: UnifiedAgentConfig
    memdocs_config: MemDocsConfig = Field(default_factory=MemDocsConfig)
    redis_config: RedisConfig = Field(default_factory=RedisConfig)

    # Book production specific
    chapter_max_words: int = Field(default=5000, ge=100)
    include_code_examples: bool = Field(default=True)
    target_reading_level: Literal["beginner", "intermediate", "advanced"] = "intermediate"

    @property
    def model(self) -> str:
        """Get model ID for backward compatibility."""
        return self.agent_config.get_model_id()

    @property
    def max_tokens(self) -> int:
        """Get max tokens for backward compatibility."""
        return self.agent_config.max_tokens

    @property
    def temperature(self) -> float:
        """Get temperature for backward compatibility."""
        return self.agent_config.temperature

    @property
    def timeout(self) -> int:
        """Get timeout for backward compatibility."""
        return self.agent_config.timeout

    @property
    def retry_attempts(self) -> int:
        """Get retry attempts for backward compatibility."""
        return self.agent_config.retry_attempts

    @property
    def retry_delay(self) -> float:
        """Get retry delay for backward compatibility."""
        return self.agent_config.retry_delay


class WorkflowConfig(BaseModel):
    """Configuration for agent workflows."""

    name: str = Field(..., min_length=1)
    description: str = Field(default="")
    mode: WorkflowMode = Field(default=WorkflowMode.SEQUENTIAL)

    # Execution settings
    max_iterations: int = Field(default=10, ge=1, le=100)
    timeout_seconds: int = Field(default=300, ge=1)

    # State management
    state_schema: dict[str, Any] | None = Field(default=None)
    checkpointing: bool = Field(default=True)

    # Error handling
    retry_on_error: bool = Field(default=True)
    max_retries: int = Field(default=3, ge=0)

    # Framework options
    framework_options: dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True
