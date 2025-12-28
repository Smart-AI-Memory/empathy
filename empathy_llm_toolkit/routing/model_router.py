"""
Smart Model Router for Empathy Framework

Routes tasks to appropriate model tiers for optimal cost/quality tradeoff:

TIER 1 - CHEAP (Haiku / GPT-4o-mini / Local Ollama):
    Cost: ~$0.25/M input, $1.25/M output
    Use for: Triage, classification, summarization, simple analysis

TIER 2 - CAPABLE (Sonnet / GPT-4o):
    Cost: ~$3/M input, $15/M output
    Use for: Code generation, bug fixes, security review, sub-agent work

TIER 3 - PREMIUM (Opus / o1):
    Cost: ~$15/M input, $75/M output
    Use for: Coordination, synthesis, architectural decisions, critical work

Cost Savings Example:
    WITHOUT routing (all Opus): $4.05 per complex task
    WITH routing (tiered):      $0.83 per complex task
    SAVINGS: 80% reduction, ~$9,660/month at 100 tasks/day

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

# Import from unified registry
from empathy_os.models import MODEL_REGISTRY, ModelInfo
from empathy_os.models.tasks import CAPABLE_TASKS, CHEAP_TASKS, PREMIUM_TASKS, get_tier_for_task


class ModelTier(Enum):
    """
    Model tier classification for routing.

    CHEAP: Fast, low-cost models for simple tasks
    CAPABLE: Balanced models for most development work
    PREMIUM: Highest capability for complex reasoning
    """

    CHEAP = "cheap"
    CAPABLE = "capable"
    PREMIUM = "premium"


@dataclass
class ModelConfig:
    """
    Configuration for a model in a tier.

    Note: This class is kept for backward compatibility. New code should
    use empathy_os.models.ModelInfo from the unified registry.
    """

    model_id: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    max_tokens: int = 4096
    supports_tools: bool = True

    @classmethod
    def from_model_info(cls, info: ModelInfo) -> "ModelConfig":
        """Create ModelConfig from unified ModelInfo."""
        return cls(
            model_id=info.id,
            cost_per_1k_input=info.cost_per_1k_input,
            cost_per_1k_output=info.cost_per_1k_output,
            max_tokens=info.max_tokens,
            supports_tools=info.supports_tools,
        )


class TaskRouting:
    """
    Task type to model tier mappings.

    Maps task types to appropriate model tiers based on:
    - Complexity requirements
    - Cost sensitivity
    - Quality needs

    Note: Task definitions are sourced from empathy_os.models.tasks
    for consistency across the framework.
    """

    # Tasks imported from shared module
    CHEAP_TASKS = CHEAP_TASKS
    CAPABLE_TASKS = CAPABLE_TASKS
    PREMIUM_TASKS = PREMIUM_TASKS

    @classmethod
    def get_tier(cls, task_type: str) -> ModelTier:
        """
        Get the appropriate tier for a task type.

        Args:
            task_type: Type of task to route

        Returns:
            ModelTier for the task
        """
        # Delegate to shared module
        tier = get_tier_for_task(task_type)
        # Convert from registry ModelTier to local ModelTier
        return ModelTier(tier.value)


class ModelRouter:
    """
    Smart model router for cost-optimized task execution.

    Routes tasks to appropriate model tiers based on complexity and
    cost requirements. Supports Anthropic, OpenAI, and Ollama providers.

    Model configurations are sourced from the unified registry at
    empathy_os.models.MODEL_REGISTRY.

    Example:
        >>> router = ModelRouter()
        >>>
        >>> # Get model for task
        >>> model = router.route("summarize")  # Returns cheap model
        >>> model = router.route("fix_bug")    # Returns capable model
        >>> model = router.route("coordinate") # Returns premium model
        >>>
        >>> # Estimate costs
        >>> cost = router.estimate_cost("fix_bug", 5000, 1000)
        >>> print(f"Estimated: ${cost:.4f}")
        >>>
        >>> # Custom routing
        >>> router.add_task_routing("my_task", ModelTier.PREMIUM)
    """

    # MODELS is now sourced from the unified registry
    # This is built lazily and cached at the class level for backward compatibility
    MODELS: dict[str, dict[str, ModelConfig]] = {}  # Populated in _ensure_models_loaded

    @classmethod
    def _ensure_models_loaded(cls) -> None:
        """Ensure MODELS is populated from registry (called lazily)."""
        if not cls.MODELS:
            for provider, tiers in MODEL_REGISTRY.items():
                cls.MODELS[provider] = {}
                for tier, info in tiers.items():
                    cls.MODELS[provider][tier] = ModelConfig.from_model_info(info)

    def __init__(
        self,
        default_provider: str = "anthropic",
        custom_routing: dict[str, ModelTier] | None = None,
    ):
        """
        Initialize the model router.

        Args:
            default_provider: Default provider (anthropic, openai, ollama, hybrid)
            custom_routing: Custom task type to tier mappings
        """
        # Ensure class-level MODELS is populated from registry
        self._ensure_models_loaded()

        self._default_provider = default_provider
        self._custom_routing: dict[str, ModelTier] = custom_routing or {}

    def route(
        self,
        task_type: str,
        provider: str | None = None,
    ) -> str:
        """
        Route a task to the appropriate model.

        Args:
            task_type: Type of task (e.g., "summarize", "fix_bug", "coordinate")
            provider: Optional provider override

        Returns:
            Model ID string

        Example:
            >>> router.route("summarize")
            'claude-3-5-haiku-20241022'
            >>> router.route("fix_bug")
            'claude-sonnet-4-5-20250514'
            >>> router.route("coordinate")
            'claude-opus-4-5-20251101'
        """
        provider = provider or self._default_provider
        tier = self._get_tier(task_type)

        if provider not in self.MODELS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.MODELS.keys())}")

        config = self.MODELS[provider].get(tier.value)
        if not config:
            # Fallback to capable
            config = self.MODELS[provider]["capable"]

        return config.model_id

    def get_config(
        self,
        task_type: str,
        provider: str | None = None,
    ) -> ModelConfig:
        """
        Get full model configuration for a task.

        Args:
            task_type: Type of task
            provider: Optional provider override

        Returns:
            ModelConfig with model_id, costs, and limits
        """
        provider = provider or self._default_provider
        tier = self._get_tier(task_type)

        return self.MODELS[provider][tier.value]

    def estimate_cost(
        self,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
        provider: str | None = None,
    ) -> float:
        """
        Estimate cost for a task.

        Args:
            task_type: Type of task
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens
            provider: Optional provider override

        Returns:
            Estimated cost in dollars

        Example:
            >>> router.estimate_cost("fix_bug", 5000, 1000)
            0.03  # $0.03 for capable tier
        """
        config = self.get_config(task_type, provider)

        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output

        return input_cost + output_cost

    def compare_costs(
        self,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
    ) -> dict[str, float]:
        """
        Compare costs across all tiers for a task.

        Args:
            task_type: Type of task
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens

        Returns:
            Dict mapping tier to estimated cost
        """
        provider = self._default_provider
        costs = {}

        for tier_name in ["cheap", "capable", "premium"]:
            config = self.MODELS[provider][tier_name]
            input_cost = (input_tokens / 1000) * config.cost_per_1k_input
            output_cost = (output_tokens / 1000) * config.cost_per_1k_output
            costs[tier_name] = input_cost + output_cost

        return costs

    def add_task_routing(self, task_type: str, tier: ModelTier) -> None:
        """
        Add custom task routing.

        Args:
            task_type: Task type to route
            tier: Model tier to use
        """
        self._custom_routing[task_type.lower()] = tier

    def get_tier(self, task_type: str) -> ModelTier:
        """
        Get the tier for a task type.

        Args:
            task_type: Task type

        Returns:
            ModelTier for the task
        """
        return self._get_tier(task_type)

    def _get_tier(self, task_type: str) -> ModelTier:
        """Internal method to get tier with custom routing support."""
        task_lower = task_type.lower().replace("-", "_").replace(" ", "_")

        # Check custom routing first
        if task_lower in self._custom_routing:
            return self._custom_routing[task_lower]

        # Use default routing
        return TaskRouting.get_tier(task_type)

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported providers."""
        cls._ensure_models_loaded()
        return list(cls.MODELS.keys())

    @classmethod
    def get_all_tasks(cls) -> dict[str, list[str]]:
        """Get all known task types by tier."""
        return {
            "cheap": list(TaskRouting.CHEAP_TASKS),
            "capable": list(TaskRouting.CAPABLE_TASKS),
            "premium": list(TaskRouting.PREMIUM_TASKS),
        }

    def calculate_savings(
        self,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
    ) -> dict[str, Any]:
        """
        Calculate savings from smart routing vs always using premium.

        Args:
            task_type: Type of task
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens

        Returns:
            Dict with savings information
        """
        routed_cost = self.estimate_cost(task_type, input_tokens, output_tokens)

        # Calculate what premium would cost
        premium_config = self.MODELS[self._default_provider]["premium"]
        premium_cost = (input_tokens / 1000) * premium_config.cost_per_1k_input + (
            output_tokens / 1000
        ) * premium_config.cost_per_1k_output

        savings = premium_cost - routed_cost
        savings_percent = (savings / premium_cost * 100) if premium_cost > 0 else 0

        return {
            "task_type": task_type,
            "routed_tier": self._get_tier(task_type).value,
            "routed_cost": routed_cost,
            "premium_cost": premium_cost,
            "savings": savings,
            "savings_percent": savings_percent,
        }
