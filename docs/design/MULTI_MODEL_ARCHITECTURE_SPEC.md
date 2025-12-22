# Multi-Model Architecture Design Specification

**Version:** 1.0
**Date:** 2025-12-22
**Status:** Draft for Review

---

## Executive Summary

This specification defines the architecture for multi-model support in the Empathy Framework. It consolidates the unified model registry, task-type routing, LLM execution, workflow orchestration, resilience patterns, and telemetry into a cohesive design.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User / Application                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Workflow Layer                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Research   │  │ Code Review │  │ Bug Predict │  ...            │
│  │  Workflow   │  │  Workflow   │  │  Workflow   │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                         │
│         └────────────────┼────────────────┘                         │
│                          ▼                                          │
│              ┌─────────────────────┐                                │
│              │  WorkflowStepConfig │                                │
│              │  (task_type, hints) │                                │
│              └──────────┬──────────┘                                │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Executor Layer                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   ResilientExecutor                          │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐  │   │
│  │  │ RetryPolicy   │  │ FallbackPolicy│  │ CircuitBreaker  │  │   │
│  │  └───────────────┘  └───────────────┘  └─────────────────┘  │   │
│  └────────────────────────────┬────────────────────────────────┘   │
│                               ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │               EmpathyLLMExecutor                             │   │
│  │  - Wraps EmpathyLLM.interact()                              │   │
│  │  - Applies task_type routing                                │   │
│  │  - Emits telemetry                                          │   │
│  └────────────────────────────┬────────────────────────────────┘   │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Routing Layer                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    ModelRouter                               │   │
│  │  - route(task_type) → model_id                              │   │
│  │  - estimate_cost()                                          │   │
│  │  - calculate_savings()                                      │   │
│  └────────────────────────────┬────────────────────────────────┘   │
│                               │                                     │
│  ┌────────────────────────────┼────────────────────────────────┐   │
│  │                     TASK_TIER_MAP                            │   │
│  │  summarize → cheap  │  generate_code → capable  │ ...       │   │
│  └────────────────────────────┼────────────────────────────────┘   │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Model Registry (Single Source of Truth)          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    MODEL_REGISTRY                            │   │
│  │  anthropic:                                                  │   │
│  │    cheap: haiku ($0.25/$1.25 per 1M)                        │   │
│  │    capable: sonnet ($3.00/$15.00 per 1M)                    │   │
│  │    premium: opus ($15.00/$75.00 per 1M)                     │   │
│  │  openai:                                                     │   │
│  │    cheap: gpt-4o-mini ($0.15/$0.60 per 1M)                  │   │
│  │    capable: gpt-4o ($2.50/$10.00 per 1M)                    │   │
│  │    premium: o1 ($15.00/$60.00 per 1M)                       │   │
│  │  ollama: (local, $0.00)                                     │   │
│  │  hybrid: (best-of across providers)                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Telemetry Layer                                  │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  LLMCallRecord  │  │WorkflowRunRecord │  │ TelemetryStore   │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 Model Registry (`empathy_os.models.registry`)

**Purpose:** Single source of truth for all model definitions, pricing, and capabilities.

#### Data Structures

```python
class ModelProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    HYBRID = "hybrid"

class ModelTier(str, Enum):
    CHEAP = "cheap"
    CAPABLE = "capable"
    PREMIUM = "premium"

@dataclass(frozen=True)
class ModelInfo:
    id: str                          # e.g., "claude-3-5-haiku-20241022"
    provider: str                    # lowercase provider key
    tier: str                        # "cheap" | "capable" | "premium"
    input_cost_per_million: float    # USD per 1M input tokens
    output_cost_per_million: float   # USD per 1M output tokens
    max_tokens: int                  # context window
    supports_vision: bool = False
    supports_tools: bool = True

    # Compatibility methods
    def to_router_config(self) -> "ModelConfig": ...
    def to_workflow_config(self) -> "WorkflowModelConfig": ...
    def to_cost_tracker_pricing(self) -> dict[str, float]: ...
```

#### Registry Structure

```python
MODEL_REGISTRY: dict[str, dict[str, ModelInfo]] = {
    "anthropic": {
        "cheap": ModelInfo(id="claude-3-5-haiku-20241022", ...),
        "capable": ModelInfo(id="claude-sonnet-4-20250514", ...),
        "premium": ModelInfo(id="claude-opus-4-20250514", ...),
    },
    "openai": {
        "cheap": ModelInfo(id="gpt-4o-mini", ...),
        "capable": ModelInfo(id="gpt-4o", ...),
        "premium": ModelInfo(id="o1", ...),
    },
    "ollama": {
        "cheap": ModelInfo(id="llama3.2:3b", ...),
        "capable": ModelInfo(id="llama3.2:latest", ...),
        "premium": ModelInfo(id="llama3.1:70b", ...),
    },
    "hybrid": {
        # Best-of across providers
        "cheap": ModelInfo(id="gpt-4o-mini", provider="openai", ...),
        "capable": ModelInfo(id="claude-sonnet-4-20250514", provider="anthropic", ...),
        "premium": ModelInfo(id="claude-opus-4-20250514", provider="anthropic", ...),
    },
}
```

#### Helper APIs

```python
def get_model(provider: str, tier: str) -> ModelInfo | None
def get_all_models() -> dict[str, dict[str, ModelInfo]]
def get_pricing_for_model(model_id: str) -> dict[str, float] | None
def get_supported_providers() -> list[str]
def get_tiers() -> list[str]
```

---

### 2.2 Task Types (`empathy_os.models.tasks`)

**Purpose:** Centralized task-to-tier mapping for consistent routing.

#### Task Categories

| Tier | Tasks | Rationale |
|------|-------|-----------|
| **Cheap** | summarize, classify, extract, format, validate | Simple, high-volume operations |
| **Capable** | generate_code, fix_bug, refactor, analyze, review | Standard development tasks |
| **Premium** | coordinate, architect, security_audit, complex_reasoning | High-stakes, complex decisions |

#### Data Structures

```python
class TaskType(str, Enum):
    # Cheap tasks
    SUMMARIZE = "summarize"
    CLASSIFY = "classify"
    EXTRACT = "extract"
    FORMAT = "format"
    VALIDATE = "validate"

    # Capable tasks
    GENERATE_CODE = "generate_code"
    FIX_BUG = "fix_bug"
    REFACTOR = "refactor"
    ANALYZE = "analyze"
    REVIEW = "review"

    # Premium tasks
    COORDINATE = "coordinate"
    ARCHITECT = "architect"
    SECURITY_AUDIT = "security_audit"
    COMPLEX_REASONING = "complex_reasoning"

TASK_TIER_MAP: dict[str, str] = {
    "summarize": "cheap",
    "classify": "cheap",
    "generate_code": "capable",
    "fix_bug": "capable",
    "coordinate": "premium",
    "architect": "premium",
    # ... etc
}
```

#### Helper APIs

```python
def normalize_task_type(task_type: str) -> str
def get_tier_for_task(task_type: str) -> str  # defaults to "capable"
def get_tasks_for_tier(tier: str) -> list[str]
def is_known_task(task_type: str) -> bool
```

---

### 2.3 LLM Executor (`empathy_os.models.executor`)

**Purpose:** Unified interface for all LLM calls with consistent context and response handling.

#### Core Interfaces

```python
@dataclass
class ExecutionContext:
    user_id: str | None = None
    workflow_name: str | None = None
    step_name: str | None = None
    task_type: str | None = None
    provider_hint: str | None = None
    tier_hint: str | None = None
    timeout_seconds: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    content: str
    model_id: str
    provider: str
    tier: str
    tokens_input: int | None = None
    tokens_output: int | None = None
    cost_estimate: float | None = None
    latency_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

class LLMExecutor(Protocol):
    async def run(self, prompt: str, context: ExecutionContext) -> LLMResponse: ...
```

#### EmpathyLLMExecutor

```python
class EmpathyLLMExecutor(LLMExecutor):
    """Wraps EmpathyLLM with unified routing and telemetry."""

    def __init__(
        self,
        llm: EmpathyLLM,
        telemetry_store: TelemetryStore | None = None,
    ): ...

    async def run(self, prompt: str, context: ExecutionContext) -> LLMResponse:
        # 1. Determine task_type (from context or default)
        # 2. Use ModelRouter to select model
        # 3. Call EmpathyLLM.interact()
        # 4. Emit LLMCallRecord to telemetry
        # 5. Return normalized LLMResponse
        ...
```

---

### 2.4 Resilience Layer (`empathy_os.models.fallback`)

**Purpose:** Automatic retry, fallback, and circuit-breaking for LLM calls.

#### Policies

```python
@dataclass
class RetryPolicy:
    max_retries: int = 3
    initial_delay_ms: int = 1000
    max_delay_ms: int = 30000
    exponential_base: float = 2.0
    retryable_errors: set[type] = field(default_factory=lambda: {
        RateLimitError, TimeoutError, ServiceUnavailableError
    })

@dataclass
class FallbackStep:
    provider: str
    tier: str

@dataclass
class FallbackPolicy:
    steps: list[FallbackStep]

    # Example: Primary Anthropic capable → OpenAI capable → Ollama capable
    @classmethod
    def default(cls) -> "FallbackPolicy":
        return cls(steps=[
            FallbackStep("anthropic", "capable"),
            FallbackStep("openai", "capable"),
            FallbackStep("ollama", "capable"),
        ])

class CircuitBreaker:
    """Per-provider circuit breaker to avoid hammering failing services."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
    ): ...

    def record_success(self, provider: str): ...
    def record_failure(self, provider: str): ...
    def is_open(self, provider: str) -> bool: ...
```

#### ResilientExecutor

```python
class ResilientExecutor(LLMExecutor):
    """Wraps an executor with retry, fallback, and circuit-breaking."""

    def __init__(
        self,
        executor: LLMExecutor,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        fallback_policy: FallbackPolicy = DEFAULT_FALLBACK_POLICY,
        circuit_breaker: CircuitBreaker | None = None,
    ): ...

    async def run(self, prompt: str, context: ExecutionContext) -> LLMResponse:
        # 1. Check circuit breaker for primary provider
        # 2. Attempt call with retry policy
        # 3. On persistent failure, iterate through fallback chain
        # 4. Record attempts in response metadata
        # 5. Update circuit breaker state
        ...
```

---

### 2.5 Workflow Layer (`empathy_os.workflows`)

**Purpose:** Multi-step orchestration with consistent model selection and telemetry.

#### Step Configuration

```python
@dataclass
class WorkflowStepConfig:
    name: str
    task_type: str
    description: str = ""
    tier_hint: str | None = None      # Override tier selection
    provider_hint: str | None = None  # Override provider selection
    fallback_policy: FallbackPolicy | None = None
    retry_policy: RetryPolicy | None = None
    timeout_seconds: int | None = None

    def to_execution_context(self, workflow_name: str) -> ExecutionContext:
        return ExecutionContext(
            workflow_name=workflow_name,
            step_name=self.name,
            task_type=self.task_type,
            provider_hint=self.provider_hint,
            tier_hint=self.tier_hint,
            timeout_seconds=self.timeout_seconds,
        )
```

#### Base Workflow

```python
class BaseWorkflow(ABC):
    name: str
    description: str
    steps: list[WorkflowStepConfig]

    def __init__(
        self,
        executor: LLMExecutor | None = None,
        config: WorkflowConfig | None = None,
        telemetry_store: TelemetryStore | None = None,
    ):
        self.executor = executor or self._create_default_executor()
        self.config = config or WorkflowConfig.load()
        self.telemetry = telemetry_store

    async def run(self, input_data: dict[str, Any]) -> WorkflowResult:
        """Execute all steps in sequence."""
        run_record = WorkflowRunRecord(
            workflow_name=self.name,
            start_time=datetime.now(),
        )

        try:
            for step in self.steps:
                context = step.to_execution_context(self.name)
                prompt = self._build_prompt(step, input_data)
                response = await self.executor.run(prompt, context)
                run_record.add_step_result(step.name, response)
                input_data = self._process_step_output(step, response, input_data)

            run_record.status = "success"
        except Exception as e:
            run_record.status = "failed"
            run_record.error = str(e)
            raise
        finally:
            run_record.end_time = datetime.now()
            if self.telemetry:
                self.telemetry.record_workflow_run(run_record)

        return WorkflowResult(output=input_data, record=run_record)

    @abstractmethod
    def _build_prompt(self, step: WorkflowStepConfig, data: dict) -> str: ...

    @abstractmethod
    def _process_step_output(self, step: WorkflowStepConfig, response: LLMResponse, data: dict) -> dict: ...
```

#### Example Workflow

```python
class ResearchSynthesisWorkflow(BaseWorkflow):
    name = "research"
    description = "Multi-source research and synthesis"
    steps = [
        WorkflowStepConfig(
            name="gather",
            task_type="extract",
            description="Gather information from sources",
            tier_hint="cheap",
        ),
        WorkflowStepConfig(
            name="analyze",
            task_type="analyze",
            description="Analyze gathered information",
            # Uses default tier (capable)
        ),
        WorkflowStepConfig(
            name="synthesize",
            task_type="generate_code",  # Or custom "synthesize" task
            description="Synthesize findings into report",
        ),
    ]
```

---

### 2.6 Telemetry (`empathy_os.models.telemetry`)

**Purpose:** Structured logging for analysis, debugging, and cost tracking.

#### Records

```python
@dataclass
class LLMCallRecord:
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # Context
    workflow_name: str | None = None
    step_name: str | None = None
    user_id: str | None = None

    # Routing
    task_type: str | None = None
    provider: str = ""
    tier: str = ""
    model_id: str = ""

    # Metrics
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: int = 0
    estimated_cost: float = 0.0

    # Resilience
    fallback_used: bool = False
    attempts: list[dict] = field(default_factory=list)
    error: str | None = None

@dataclass
class WorkflowRunRecord:
    id: str = field(default_factory=lambda: str(uuid4()))
    workflow_name: str = ""
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str = "pending"  # pending | running | success | failed

    # Aggregated metrics
    steps: list[dict] = field(default_factory=list)
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_cost: float = 0.0
    total_savings: float = 0.0

    error: str | None = None
```

#### Store and Analytics

```python
class TelemetryStore:
    """Persistent storage for telemetry records."""

    def __init__(self, path: Path = Path(".empathy/telemetry.jsonl")): ...

    def record_call(self, record: LLMCallRecord): ...
    def record_workflow_run(self, record: WorkflowRunRecord): ...
    def query_calls(self, filters: dict) -> list[LLMCallRecord]: ...
    def query_runs(self, filters: dict) -> list[WorkflowRunRecord]: ...

class TelemetryAnalytics:
    """Analysis utilities over telemetry data."""

    def __init__(self, store: TelemetryStore): ...

    def top_expensive_workflows(self, n: int = 10) -> list[dict]: ...
    def provider_usage_summary(self) -> dict[str, dict]: ...
    def fallback_stats(self) -> dict[str, float]: ...
    def cost_by_task_type(self) -> dict[str, float]: ...
    def savings_vs_premium(self) -> dict[str, float]: ...
```

---

## 3. Integration Points

### 3.1 ModelRouter Integration

```python
class ModelRouter:
    """Routes tasks to appropriate models using the unified registry."""

    MODELS: dict[str, dict[str, ModelConfig]] = {}

    @classmethod
    def _ensure_models_loaded(cls):
        if not cls.MODELS:
            for provider, tiers in MODEL_REGISTRY.items():
                cls.MODELS[provider] = {}
                for tier, info in tiers.items():
                    cls.MODELS[provider][tier] = info.to_router_config()

    def route(self, task_type: str, provider: str | None = None) -> str:
        self._ensure_models_loaded()
        tier = get_tier_for_task(task_type)
        provider = provider or self.default_provider
        return self.MODELS[provider][tier].model_id
```

### 3.2 EmpathyLLM Integration

```python
class EmpathyLLM:
    def __init__(
        self,
        provider: str = "anthropic",
        enable_model_routing: bool = False,
        ...
    ):
        if enable_model_routing:
            self._router = ModelRouter(default_provider=provider)

    async def interact(
        self,
        user_id: str,
        user_input: str,
        task_type: str = "generate_code",
        ...
    ) -> dict:
        if self._router and not self._explicit_model:
            model_id = self._router.route(task_type)
            # Use routed model
        ...
```

### 3.3 CLI Integration

```bash
# Registry inspection
empathy models registry --provider anthropic
empathy models registry --format json

# Task mapping
empathy models tasks --tier capable
empathy models tasks --task generate_code

# Cost estimation
empathy models costs --task generate_code --input-tokens 1000 --output-tokens 500

# Telemetry
empathy telemetry workflows --top 10
empathy telemetry providers --failures
empathy telemetry costs --by-task
```

---

## 4. Design Decisions

### 4.1 Enum Unification

**Decision:** Use `empathy_os.models.registry.ModelProvider` and `ModelTier` as canonical types everywhere.

**Rationale:** Prevents subtle type mismatches and simplifies cross-component refactors.

**Migration Path:**
1. Add deprecation warnings to local enums
2. Update imports in routing and workflows modules
3. Remove deprecated enums after transition period

### 4.2 Fallback Strategy

**Decision:** Default fallback crosses providers (Anthropic → OpenAI → Ollama).

**Rationale:** Maximizes availability. Provider-specific fallback (same provider, different tier) can be configured per-workflow.

**Configuration:**
```python
# Cross-provider (default)
DEFAULT_FALLBACK_POLICY = FallbackPolicy(steps=[
    FallbackStep("anthropic", "capable"),
    FallbackStep("openai", "capable"),
    FallbackStep("ollama", "capable"),
])

# Same-provider fallback
ANTHROPIC_ONLY_FALLBACK = FallbackPolicy(steps=[
    FallbackStep("anthropic", "capable"),
    FallbackStep("anthropic", "cheap"),
])
```

### 4.3 Telemetry Granularity

**Decision:** Record both per-call (`LLMCallRecord`) and per-workflow (`WorkflowRunRecord`).

**Rationale:** Per-call enables debugging and fine-grained cost attribution. Per-workflow enables business-level reporting.

**Storage:** JSONL files in `.empathy/` directory for simplicity. Can be upgraded to database later.

### 4.4 Workflow Step Definition

**Decision:** Workflows define steps declaratively via `WorkflowStepConfig`.

**Rationale:** Separates orchestration logic from model selection. Enables testing and visualization of workflow structure.

---

## 5. Implementation Priorities

### Phase 1: Foundation (Completed)
- [x] Unified MODEL_REGISTRY
- [x] Task-type schema (TASK_TIER_MAP)
- [x] ModelRouter integration with registry
- [x] Basic telemetry structures

### Phase 2: Execution Layer (Current)
- [ ] Formalize LLMExecutor interface
- [ ] Implement EmpathyLLMExecutor with telemetry
- [ ] Implement ResilientExecutor with fallback
- [ ] Wire into existing workflows

### Phase 3: Workflow Enhancement
- [ ] Migrate workflows to WorkflowStepConfig pattern
- [ ] Add per-step fallback configuration
- [ ] Integrate TelemetryStore into workflow runs
- [ ] CLI commands for telemetry analysis

### Phase 4: Operational Excellence
- [ ] Dashboard/UI integration
- [ ] Alerting on fallback spikes
- [ ] Cost budgeting per workflow
- [ ] A/B testing for routing strategies

---

## 6. Testing Strategy

### Unit Tests
- Registry: All providers/tiers present, pricing correct
- Tasks: Mapping completeness, normalization
- Router: Correct model selection per task/provider
- Executor: Mock-based tests for context handling

### Integration Tests
- Workflow end-to-end with mock executor
- Fallback behavior with simulated failures
- Telemetry recording and querying

### Performance Tests
- Router lookup latency (<1ms)
- Executor overhead (<10ms)
- Telemetry write throughput

---

## 7. Design Decisions (Resolved)

### 7.1 Circuit Breaker Scope

**Decision:** Per-provider-per-tier

**Rationale:** A failing premium tier (e.g., Opus rate-limited) shouldn't block cheap tier calls to the same provider. This provides finer-grained resilience.

**Implementation:**
```python
class CircuitBreaker:
    def __init__(self):
        # Key: "{provider}:{tier}" e.g., "anthropic:premium"
        self._states: dict[str, CircuitBreakerState] = {}

    def get_key(self, provider: str, tier: str) -> str:
        return f"{provider}:{tier}"

    def is_open(self, provider: str, tier: str) -> bool:
        key = self.get_key(provider, tier)
        state = self._states.get(key)
        return state and state.is_open()
```

---

### 7.2 Telemetry Retention (Enterprise Recommendations)

**Decision:** Tiered retention with configurable policies

| Tier | Retention | Use Case |
|------|-----------|----------|
| **Hot** | 7 days | Real-time dashboards, debugging |
| **Warm** | 90 days | Monthly reporting, trend analysis |
| **Cold** | 1 year | Compliance, audit trails |
| **Archive** | 7 years | HIPAA/SOC2 requirements |

**Implementation:**
```python
@dataclass
class TelemetryRetentionPolicy:
    hot_days: int = 7
    warm_days: int = 90
    cold_days: int = 365
    archive_days: int = 2555  # ~7 years

    # Auto-cleanup settings
    auto_cleanup_enabled: bool = True
    cleanup_interval_hours: int = 24

    # Storage locations
    hot_path: Path = Path(".empathy/telemetry/hot/")
    warm_path: Path = Path(".empathy/telemetry/warm/")
    cold_path: Path = Path(".empathy/telemetry/cold/")
    archive_path: Path | None = None  # External storage (S3, etc.)

    # Compression
    compress_after_days: int = 7
    compression_format: str = "gzip"  # gzip | zstd | none

# Enterprise configuration example
ENTERPRISE_RETENTION = TelemetryRetentionPolicy(
    hot_days=14,
    warm_days=180,
    cold_days=365,
    archive_days=2555,
    archive_path=Path("/mnt/compliance/empathy-telemetry/"),
)
```

**Enterprise Features:**
- **Encryption at rest** for HIPAA compliance
- **Export API** for SIEM integration (Splunk, DataDog)
- **PII scrubbing** before long-term storage
- **Audit log** for telemetry access

---

### 7.3 Cost Limits (Optional Feature)

**Decision:** Not required for MVP, but useful for enterprise guardrails

**Suggested Implementation (Future):**
```python
@dataclass
class CostLimits:
    # Per-run limits
    max_cost_per_run: float | None = None      # Abort if exceeded
    warn_cost_per_run: float | None = None     # Log warning

    # Per-step limits
    max_cost_per_step: float | None = None

    # Daily/monthly budgets (for dashboards/alerts, not hard limits)
    daily_budget: float | None = None
    monthly_budget: float | None = None

    # Action on limit
    on_limit: str = "warn"  # "warn" | "abort" | "fallback_to_cheaper"

# Usage in workflow
class BaseWorkflow:
    cost_limits: CostLimits | None = None

    async def _check_cost_limit(self, accumulated_cost: float):
        if self.cost_limits and self.cost_limits.max_cost_per_run:
            if accumulated_cost > self.cost_limits.max_cost_per_run:
                if self.cost_limits.on_limit == "abort":
                    raise CostLimitExceededError(f"Run cost ${accumulated_cost:.4f} exceeds limit")
                elif self.cost_limits.on_limit == "fallback_to_cheaper":
                    self._force_cheap_tier = True
```

**When This Becomes Useful:**
- Multi-tenant SaaS (per-customer budgets)
- Runaway loop prevention
- Cost attribution for chargebacks

---

### 7.4 Async vs Sync Execution

**Decision:** Async-first with sync compatibility wrapper

**Implementation:**
```python
class LLMExecutor(Protocol):
    """Primary interface is async."""
    async def run(self, prompt: str, context: ExecutionContext) -> LLMResponse: ...

class SyncExecutorWrapper:
    """Wrapper for sync contexts (CLI, simple scripts)."""

    def __init__(self, executor: LLMExecutor):
        self._executor = executor

    def run(self, prompt: str, context: ExecutionContext) -> LLMResponse:
        """Sync wrapper - creates event loop if needed."""
        try:
            loop = asyncio.get_running_loop()
            # Already in async context - can't use sync wrapper
            raise RuntimeError("Use async executor.run() in async context")
        except RuntimeError:
            # No running loop - safe to create one
            return asyncio.run(self._executor.run(prompt, context))

# Convenience function
def run_sync(executor: LLMExecutor, prompt: str, context: ExecutionContext) -> LLMResponse:
    """Helper for one-off sync calls."""
    return asyncio.run(executor.run(prompt, context))

# Auto-detection in workflows
class BaseWorkflow:
    def run(self, input_data: dict) -> WorkflowResult:
        """Auto-detects sync/async context."""
        try:
            loop = asyncio.get_running_loop()
            # We're in async context - return coroutine
            return self._run_async(input_data)
        except RuntimeError:
            # Sync context - run with new loop
            return asyncio.run(self._run_async(input_data))

    async def _run_async(self, input_data: dict) -> WorkflowResult:
        # Actual implementation
        ...
```

---

### 7.5 Workflow Plugin Integration

**Decision:** Yes - workflows should be discoverable via the plugin system

**Recommended Options:**

#### Option A: Unified Plugin Type (Recommended)
Workflows register as plugins with `type="workflow"`:

```python
# In workflow module
from empathy_os.plugins import register_plugin

@register_plugin(
    name="research-synthesis",
    type="workflow",
    domain="research",
    description="Multi-source research and synthesis",
    version="1.0.0",
)
class ResearchSynthesisWorkflow(BaseWorkflow):
    ...

# Discovery
from empathy_os.plugins import get_global_registry

registry = get_global_registry()
workflows = registry.get_plugins(type="workflow")
research_workflows = registry.get_plugins(type="workflow", domain="research")
```

#### Option B: Separate Workflow Registry with Plugin Bridge
Keep `WORKFLOW_REGISTRY` but expose via plugin system:

```python
# In workflows/__init__.py
from empathy_os.plugins import PluginRegistry

def register_workflows_as_plugins(registry: PluginRegistry):
    """Bridge WORKFLOW_REGISTRY to plugin system."""
    for name, workflow_class in WORKFLOW_REGISTRY.items():
        registry.register(
            name=name,
            type="workflow",
            implementation=workflow_class,
            metadata={
                "description": workflow_class.description,
                "stages": workflow_class.stages,
                "tier_map": getattr(workflow_class, "tier_map", {}),
            }
        )

# Auto-register on import
register_workflows_as_plugins(get_global_registry())
```

#### Option C: Entry Points Discovery (Most Flexible)
Use setuptools entry points for external workflow packages:

```toml
# In pyproject.toml of an external package
[project.entry-points."empathy.workflows"]
my-custom-workflow = "my_package.workflows:CustomWorkflow"
```

```python
# Discovery in empathy_os
from importlib.metadata import entry_points

def discover_workflow_plugins():
    eps = entry_points(group="empathy.workflows")
    for ep in eps:
        workflow_class = ep.load()
        WORKFLOW_REGISTRY[ep.name] = workflow_class
```

**Recommendation:** Start with **Option A** for simplicity, with entry point support (Option C) as a future extension for third-party workflows.

**Benefits:**
- Single `registry.get_plugins()` API for wizards AND workflows
- Consistent metadata schema
- Dashboard can show all capabilities in one view
- Third-party extensibility via entry points

---

## 8. Appendix: Current File Locations

| Component | Location |
|-----------|----------|
| Model Registry | `src/empathy_os/models/registry.py` |
| Task Types | `src/empathy_os/models/tasks.py` |
| Executor | `src/empathy_os/models/executor.py` |
| EmpathyLLMExecutor | `src/empathy_os/models/empathy_executor.py` |
| Fallback/Resilience | `src/empathy_os/models/fallback.py` |
| Telemetry | `src/empathy_os/models/telemetry.py` |
| CLI | `src/empathy_os/models/cli.py` |
| ModelRouter | `empathy_llm_toolkit/routing/model_router.py` |
| Workflows | `src/empathy_os/workflows/` |
| Tests | `tests/test_model_registry.py`, `tests/test_model_router.py` |

---

*This specification is intended for review. Implementation should proceed incrementally with tests at each phase.*
