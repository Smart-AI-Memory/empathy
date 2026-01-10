# Meta-Orchestration API Reference

**Version:** 3.12.0
**Last Updated:** January 10, 2026

---

## Table of Contents

1. [Core Components](#core-components)
2. [Agent Templates](#agent-templates)
3. [Meta-Orchestrator](#meta-orchestrator)
4. [Execution Strategies](#execution-strategies)
5. [Configuration Store](#configuration-store)
6. [Workflows](#workflows)

---

## Core Components

### Overview

The meta-orchestration system consists of 5 main modules:

```
empathy_os.orchestration/
├── agent_templates.py      # Agent archetypes and capabilities
├── meta_orchestrator.py    # Task analysis and agent selection
├── execution_strategies.py # 6 composition patterns
├── config_store.py         # Learning and memory system
└── __init__.py
```

---

## Agent Templates

**Module:** `empathy_os.orchestration.agent_templates`

### Classes

#### `AgentCapability`

**Dataclass representing a capability that an agent can perform.**

```python
@dataclass(frozen=True)
class AgentCapability:
    name: str
    description: str
    required_tools: list[str] = field(default_factory=list)
```

**Attributes:**
- `name` (str): Capability identifier (e.g., "analyze_gaps")
- `description` (str): Human-readable description
- `required_tools` (list[str]): List of tools needed for this capability

**Example:**
```python
cap = AgentCapability(
    name="analyze_gaps",
    description="Identify test coverage gaps",
    required_tools=["coverage_analyzer"]
)
```

---

#### `ResourceRequirements`

**Dataclass defining resource limits for agent execution.**

```python
@dataclass(frozen=True)
class ResourceRequirements:
    min_tokens: int = 1000
    max_tokens: int = 10000
    timeout_seconds: int = 300
    memory_mb: int = 512
```

**Attributes:**
- `min_tokens` (int): Minimum token budget required
- `max_tokens` (int): Maximum token budget allowed
- `timeout_seconds` (int): Maximum execution time in seconds
- `memory_mb` (int): Maximum memory usage in megabytes

**Validation:**
- `min_tokens` must be ≥ 0
- `max_tokens` must be ≥ `min_tokens`
- `timeout_seconds` must be > 0
- `memory_mb` must be > 0

**Example:**
```python
req = ResourceRequirements(
    min_tokens=2000,
    max_tokens=15000,
    timeout_seconds=600,
    memory_mb=1024
)
```

---

#### `AgentTemplate`

**Dataclass representing a reusable agent archetype.**

```python
@dataclass(frozen=True)
class AgentTemplate:
    id: str
    role: str
    capabilities: list[str]
    tier_preference: str
    tools: list[str]
    default_instructions: str
    quality_gates: dict[str, Any]
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)

    ALLOWED_TIERS = {"CHEAP", "CAPABLE", "PREMIUM"}
```

**Attributes:**
- `id` (str): Unique template identifier
- `role` (str): Human-readable agent role
- `capabilities` (list[str]): List of capability names
- `tier_preference` (str): Preferred tier ("CHEAP", "CAPABLE", "PREMIUM")
- `tools` (list[str]): List of tool identifiers
- `default_instructions` (str): Default instructions for the agent
- `quality_gates` (dict[str, Any]): Quality gate thresholds
- `resource_requirements` (ResourceRequirements): Resource limits

**Validation:**
- `id` and `role` must be non-empty strings
- `capabilities` must be non-empty list of strings
- `tier_preference` must be in `ALLOWED_TIERS`
- `tools` must be list (can be empty)
- `default_instructions` must be non-empty string
- `quality_gates` must be dict

**Example:**
```python
template = AgentTemplate(
    id="test_coverage_analyzer",
    role="Test Coverage Expert",
    capabilities=["analyze_gaps", "suggest_tests"],
    tier_preference="CAPABLE",
    tools=["coverage_analyzer", "ast_parser"],
    default_instructions="Analyze test coverage...",
    quality_gates={"min_coverage": 80}
)
```

---

### Functions

#### `get_template(template_id: str) -> AgentTemplate | None`

**Retrieve agent template by ID.**

**Parameters:**
- `template_id` (str): Template identifier

**Returns:**
- `AgentTemplate | None`: Template if found, None otherwise

**Example:**
```python
template = get_template("test_coverage_analyzer")
if template:
    print(template.role)  # "Test Coverage Expert"
```

---

#### `get_all_templates() -> list[AgentTemplate]`

**Retrieve all registered templates.**

**Returns:**
- `list[AgentTemplate]`: List of all available templates

**Example:**
```python
templates = get_all_templates()
print(f"Available: {len(templates)} templates")
for t in templates:
    print(f"  - {t.id}: {t.role}")
```

---

#### `get_templates_by_capability(capability: str) -> list[AgentTemplate]`

**Retrieve templates with a specific capability.**

**Parameters:**
- `capability` (str): Capability name to search for

**Returns:**
- `list[AgentTemplate]`: Templates with that capability

**Example:**
```python
templates = get_templates_by_capability("vulnerability_scan")
# Returns: [security_auditor]
```

---

#### `get_templates_by_tier(tier: str) -> list[AgentTemplate]`

**Retrieve templates preferring a specific tier.**

**Parameters:**
- `tier` (str): Tier name ("CHEAP", "CAPABLE", "PREMIUM")

**Returns:**
- `list[AgentTemplate]`: Templates preferring that tier

**Example:**
```python
cheap_templates = get_templates_by_tier("CHEAP")
# Returns: [documentation_writer]

capable_templates = get_templates_by_tier("CAPABLE")
# Returns: [test_coverage_analyzer, code_reviewer, performance_optimizer, refactoring_specialist]
```

---

### Pre-built Templates

**7 templates available:**

1. `test_coverage_analyzer` (CAPABLE)
2. `security_auditor` (PREMIUM)
3. `code_reviewer` (CAPABLE)
4. `documentation_writer` (CHEAP)
5. `performance_optimizer` (CAPABLE)
6. `architecture_analyst` (PREMIUM)
7. `refactoring_specialist` (CAPABLE)

---

## Meta-Orchestrator

**Module:** `empathy_os.orchestration.meta_orchestrator`

### Enums

#### `TaskComplexity`

**Task complexity classification.**

```python
class TaskComplexity(Enum):
    SIMPLE = "simple"      # Single agent, straightforward
    MODERATE = "moderate"  # 2-3 agents, some coordination
    COMPLEX = "complex"    # 4+ agents, multi-phase execution
```

---

#### `TaskDomain`

**Task domain classification.**

```python
class TaskDomain(Enum):
    TESTING = "testing"
    SECURITY = "security"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    REFACTORING = "refactoring"
    GENERAL = "general"
```

---

#### `CompositionPattern`

**Available composition patterns (grammar rules).**

```python
class CompositionPattern(Enum):
    SEQUENTIAL = "sequential"  # A → B → C
    PARALLEL = "parallel"      # A ‖ B ‖ C
    DEBATE = "debate"          # A ⇄ B ⇄ C → Synthesis
    TEACHING = "teaching"      # Junior → Expert validation
    REFINEMENT = "refinement"  # Draft → Review → Polish
    ADAPTIVE = "adaptive"      # Classifier → Specialist
```

---

### Dataclasses

#### `TaskRequirements`

**Extracted requirements from task analysis.**

```python
@dataclass
class TaskRequirements:
    complexity: TaskComplexity
    domain: TaskDomain
    capabilities_needed: list[str]
    parallelizable: bool = False
    quality_gates: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
```

**Attributes:**
- `complexity` (TaskComplexity): Task complexity level
- `domain` (TaskDomain): Primary task domain
- `capabilities_needed` (list[str]): Required capabilities
- `parallelizable` (bool): Whether task can be parallelized
- `quality_gates` (dict[str, Any]): Quality thresholds
- `context` (dict[str, Any]): Additional context

---

#### `ExecutionPlan`

**Plan for agent execution.**

```python
@dataclass
class ExecutionPlan:
    agents: list[AgentTemplate]
    strategy: CompositionPattern
    quality_gates: dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    estimated_duration: int = 0
```

**Attributes:**
- `agents` (list[AgentTemplate]): Agents to execute
- `strategy` (CompositionPattern): Composition pattern
- `quality_gates` (dict[str, Any]): Quality thresholds
- `estimated_cost` (float): Estimated execution cost (arbitrary units)
- `estimated_duration` (int): Estimated time in seconds

---

### Classes

#### `MetaOrchestrator`

**Intelligent task analyzer and agent composition engine.**

```python
class MetaOrchestrator:
    def __init__(self): ...

    def analyze_and_compose(
        self, task: str, context: dict[str, Any] | None = None
    ) -> ExecutionPlan: ...
```

**Methods:**

##### `__init__()`

**Initialize meta-orchestrator.**

**Example:**
```python
orchestrator = MetaOrchestrator()
```

---

##### `analyze_and_compose(task: str, context: dict[str, Any] | None = None) -> ExecutionPlan`

**Analyze task and create execution plan.**

This is the main entry point for meta-orchestration.

**Parameters:**
- `task` (str): Task description (e.g., "Boost test coverage to 90%")
- `context` (dict[str, Any] | None): Optional context dictionary

**Returns:**
- `ExecutionPlan`: Plan with agents and strategy

**Raises:**
- `ValueError`: If task is invalid (empty or not a string)

**Example:**
```python
orchestrator = MetaOrchestrator()

plan = orchestrator.analyze_and_compose(
    task="Prepare for v3.12.0 release",
    context={
        "version": "3.12.0",
        "current_coverage": 75.0,
    }
)

print(f"Complexity: {plan.complexity}")
print(f"Domain: {plan.domain}")
print(f"Agents: {[a.id for a in plan.agents]}")
print(f"Strategy: {plan.strategy.value}")
print(f"Cost: {plan.estimated_cost}")
print(f"Duration: {plan.estimated_duration}s")
```

**Algorithm:**
1. Classify task complexity (simple/moderate/complex)
2. Classify task domain (testing/security/etc.)
3. Extract required capabilities
4. Select appropriate agents
5. Choose composition pattern
6. Estimate cost and duration

---

## Execution Strategies

**Module:** `empathy_os.orchestration.execution_strategies`

### Dataclasses

#### `AgentResult`

**Result from agent execution.**

```python
@dataclass
class AgentResult:
    agent_id: str
    success: bool
    output: dict[str, Any]
    confidence: float = 0.0
    duration_seconds: float = 0.0
    error: str = ""
```

**Attributes:**
- `agent_id` (str): ID of agent that produced result
- `success` (bool): Whether execution succeeded
- `output` (dict[str, Any]): Agent output data
- `confidence` (float): Confidence score (0-1)
- `duration_seconds` (float): Execution time
- `error` (str): Error message if failed

---

#### `StrategyResult`

**Aggregated result from strategy execution.**

```python
@dataclass
class StrategyResult:
    success: bool
    outputs: list[AgentResult]
    aggregated_output: dict[str, Any]
    total_duration: float = 0.0
    errors: list[str] = None
```

**Attributes:**
- `success` (bool): Whether overall execution succeeded
- `outputs` (list[AgentResult]): Individual agent results
- `aggregated_output` (dict[str, Any]): Combined/synthesized output
- `total_duration` (float): Total execution time
- `errors` (list[str]): List of errors encountered

---

### Base Class

#### `ExecutionStrategy`

**Base class for agent composition strategies.**

```python
class ExecutionStrategy(ABC):
    @abstractmethod
    async def execute(
        self, agents: list[AgentTemplate], context: dict[str, Any]
    ) -> StrategyResult: ...
```

**Methods:**

##### `execute(agents: list[AgentTemplate], context: dict[str, Any]) -> StrategyResult`

**Execute agents using this strategy.**

**Parameters:**
- `agents` (list[AgentTemplate]): Agents to execute
- `context` (dict[str, Any]): Initial context

**Returns:**
- `StrategyResult`: Aggregated results

**Raises:**
- `ValueError`: If agents list is empty
- `TimeoutError`: If execution exceeds timeout

---

### Strategy Classes

#### `SequentialStrategy`

**Sequential composition (A → B → C).**

```python
class SequentialStrategy(ExecutionStrategy):
    async def execute(
        self, agents: list[AgentTemplate], context: dict[str, Any]
    ) -> StrategyResult: ...
```

**Behavior:**
- Executes agents one after another
- Each agent receives output from previous agent in context
- Total duration = sum of individual durations

**Example:**
```python
strategy = SequentialStrategy()
result = await strategy.execute(
    [analyzer, generator, validator],
    {"project_root": "./"}
)
```

---

#### `ParallelStrategy`

**Parallel composition (A ‖ B ‖ C).**

```python
class ParallelStrategy(ExecutionStrategy):
    async def execute(
        self, agents: list[AgentTemplate], context: dict[str, Any]
    ) -> StrategyResult: ...
```

**Behavior:**
- Executes all agents simultaneously using `asyncio.gather()`
- Each agent receives same initial context
- Total duration = max individual duration

**Example:**
```python
strategy = ParallelStrategy()
result = await strategy.execute(
    [security, coverage, quality, docs],
    {"path": "."}
)
```

---

#### `DebateStrategy`

**Debate/Consensus composition (A ⇄ B ⇄ C → Synthesis).**

```python
class DebateStrategy(ExecutionStrategy):
    async def execute(
        self, agents: list[AgentTemplate], context: dict[str, Any]
    ) -> StrategyResult: ...
```

**Behavior:**
- Phase 1: Agents provide independent opinions (parallel)
- Phase 2: Synthesizer aggregates and resolves conflicts
- Total duration ≈ 2x max individual duration

**Output structure:**
```python
{
    "debate_participants": ["agent1", "agent2"],
    "opinions": [output1, output2],
    "consensus": {
        "consensus_reached": True,
        "success_votes": 2,
        "total_votes": 2,
        "avg_confidence": 0.85
    }
}
```

**Example:**
```python
strategy = DebateStrategy()
result = await strategy.execute(
    [architect1, architect2, architect3],
    {"requirements": {...}}
)
```

---

#### `TeachingStrategy`

**Teaching/Validation (Junior → Expert Review).**

```python
class TeachingStrategy(ExecutionStrategy):
    def __init__(self, quality_threshold: float = 0.7): ...

    async def execute(
        self, agents: list[AgentTemplate], context: dict[str, Any]
    ) -> StrategyResult: ...
```

**Parameters:**
- `quality_threshold` (float): Minimum confidence for junior to pass (0-1), default 0.7

**Behavior:**
- Phase 1: Junior agent attempts task
- Phase 2: Quality gate checks confidence
- Phase 3: Expert takes over if junior fails

**Requirements:**
- Exactly 2 agents: `[junior, expert]`

**Output structure:**
```python
{
    "outcome": "junior_success",  # or "expert_takeover"
    "junior_output": {...},
    "expert_output": {...}  # only if expert took over
}
```

**Example:**
```python
strategy = TeachingStrategy(quality_threshold=0.7)
result = await strategy.execute(
    [junior_writer, expert_writer],
    {"topic": "API documentation"}
)
```

---

#### `RefinementStrategy`

**Progressive Refinement (Draft → Review → Polish).**

```python
class RefinementStrategy(ExecutionStrategy):
    async def execute(
        self, agents: list[AgentTemplate], context: dict[str, Any]
    ) -> StrategyResult: ...
```

**Behavior:**
- Each agent refines output from previous stage
- Sequential execution with progressive quality improvement
- Stops on first failure

**Requirements:**
- At least 2 agents (typically 3: drafter, reviewer, polisher)

**Output structure:**
```python
{
    "refinement_stages": 3,
    "final_output": {...},
    "stage_outputs": [draft, reviewed, polished]
}
```

**Example:**
```python
strategy = RefinementStrategy()
result = await strategy.execute(
    [drafter, reviewer, polisher],
    {"requirements": {...}}
)
```

---

#### `AdaptiveStrategy`

**Adaptive Routing (Classifier → Specialist).**

```python
class AdaptiveStrategy(ExecutionStrategy):
    async def execute(
        self, agents: list[AgentTemplate], context: dict[str, Any]
    ) -> StrategyResult: ...
```

**Behavior:**
- Phase 1: Classifier assesses task complexity
- Phase 2: Routes to appropriate specialist based on confidence
  - High confidence (>0.8) → CHEAP specialist
  - Low confidence (<0.8) → PREMIUM specialist

**Requirements:**
- At least 2 agents: `[classifier, specialist1, ...]`

**Output structure:**
```python
{
    "classification": {...},
    "selected_specialist": "specialist_id",
    "specialist_output": {...}
}
```

**Example:**
```python
strategy = AdaptiveStrategy()
result = await strategy.execute(
    [classifier, cheap_specialist, premium_specialist],
    {"task_description": "..."}
)
```

---

### Functions

#### `get_strategy(strategy_name: str) -> ExecutionStrategy`

**Get strategy instance by name.**

**Parameters:**
- `strategy_name` (str): Strategy name ("sequential", "parallel", "debate", "teaching", "refinement", "adaptive")

**Returns:**
- `ExecutionStrategy`: Strategy instance

**Raises:**
- `ValueError`: If strategy name is invalid

**Example:**
```python
strategy = get_strategy("parallel")
isinstance(strategy, ParallelStrategy)  # True

# Available strategies
STRATEGY_REGISTRY = {
    "sequential": SequentialStrategy,
    "parallel": ParallelStrategy,
    "debate": DebateStrategy,
    "teaching": TeachingStrategy,
    "refinement": RefinementStrategy,
    "adaptive": AdaptiveStrategy,
}
```

---

## Configuration Store

**Module:** `empathy_os.orchestration.config_store`

### Dataclasses

#### `AgentConfiguration`

**Saved configuration for a successful agent team composition.**

```python
@dataclass
class AgentConfiguration:
    # Identity
    id: str
    task_pattern: str

    # Team Composition
    agents: list[dict[str, Any]]
    strategy: str

    # Quality Criteria
    quality_gates: dict[str, Any]

    # Performance Metrics
    success_rate: float = 0.0
    avg_quality_score: float = 0.0
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime | None = None
    tags: list[str] = field(default_factory=list)
```

**Attributes:**
- `id` (str): Unique configuration identifier
- `task_pattern` (str): Task pattern (e.g., "release_prep")
- `agents` (list[dict[str, Any]]): Agent configurations
- `strategy` (str): Composition pattern used
- `quality_gates` (dict[str, Any]): Quality thresholds
- `success_rate` (float): Success rate (0.0-1.0)
- `avg_quality_score` (float): Average quality score (0-100)
- `usage_count` (int): Number of times used
- `success_count` (int): Number of successes
- `failure_count` (int): Number of failures
- `created_at` (datetime): Creation timestamp
- `last_used` (datetime | None): Last usage timestamp
- `tags` (list[str]): Organizational tags

**Methods:**

##### `record_outcome(success: bool, quality_score: float) -> None`

**Record an execution outcome and update metrics.**

**Parameters:**
- `success` (bool): Whether orchestration succeeded
- `quality_score` (float): Quality score (0-100)

**Raises:**
- `ValueError`: If quality_score is out of range

**Example:**
```python
config.record_outcome(success=True, quality_score=87.5)

# Updates:
# - usage_count += 1
# - success_count += 1 (if success)
# - success_rate recalculated
# - avg_quality_score updated (weighted average)
# - last_used = now
```

---

##### `to_dict() -> dict[str, Any]`

**Serialize to dictionary for JSON storage.**

**Returns:**
- `dict[str, Any]`: Dictionary representation

**Example:**
```python
data = config.to_dict()
# Datetime objects converted to ISO format strings
```

---

##### `from_dict(data: dict[str, Any]) -> AgentConfiguration`

**Deserialize from dictionary (class method).**

**Parameters:**
- `data` (dict[str, Any]): Dictionary from JSON

**Returns:**
- `AgentConfiguration`: Configuration instance

**Example:**
```python
config = AgentConfiguration.from_dict(data)
# ISO format strings converted back to datetime objects
```

---

### Classes

#### `ConfigurationStore`

**Persistent storage for successful agent team compositions.**

```python
class ConfigurationStore:
    def __init__(
        self,
        storage_dir: str | None = None,
        pattern_library: PatternLibrary | None = None,
    ): ...
```

**Parameters:**
- `storage_dir` (str | None): Directory for storing configurations (default: `.empathy/orchestration/compositions/`)
- `pattern_library` (PatternLibrary | None): Optional pattern library for integration

**Methods:**

##### `save(config: AgentConfiguration) -> Path`

**Save agent configuration to disk and update pattern library.**

**Parameters:**
- `config` (AgentConfiguration): Configuration to save

**Returns:**
- `Path`: Path to saved file

**Raises:**
- `ValueError`: If config.id is invalid or path is unsafe
- `OSError`: If file write fails

**Example:**
```python
store = ConfigurationStore()

config = AgentConfiguration(
    id="comp_001",
    task_pattern="release_prep",
    agents=[...],
    strategy="parallel",
    quality_gates={...}
)

path = store.save(config)
print(f"Saved to: {path}")
```

---

##### `load(config_id: str) -> AgentConfiguration | None`

**Load configuration by ID.**

**Parameters:**
- `config_id` (str): Configuration ID

**Returns:**
- `AgentConfiguration | None`: Configuration if found

**Raises:**
- `ValueError`: If config_id is invalid

**Example:**
```python
config = store.load("comp_001")
if config:
    print(f"Success rate: {config.success_rate:.1%}")
```

---

##### `search(...) -> list[AgentConfiguration]`

**Search for configurations matching criteria.**

```python
def search(
    self,
    task_pattern: str | None = None,
    min_success_rate: float = 0.0,
    min_quality_score: float = 0.0,
    limit: int = 10,
) -> list[AgentConfiguration]: ...
```

**Parameters:**
- `task_pattern` (str | None): Filter by task pattern
- `min_success_rate` (float): Minimum success rate (0.0-1.0)
- `min_quality_score` (float): Minimum quality score (0-100)
- `limit` (int): Maximum results

**Returns:**
- `list[AgentConfiguration]`: Matching configurations, sorted by success rate descending

**Raises:**
- `ValueError`: If parameters out of range

**Example:**
```python
matches = store.search(
    task_pattern="release_prep",
    min_success_rate=0.8,
    min_quality_score=80.0,
    limit=5
)

for config in matches:
    print(f"{config.id}: {config.success_rate:.1%}")
```

---

##### `get_best_for_task(task_pattern: str) -> AgentConfiguration | None`

**Get best-performing configuration for a task pattern.**

**Parameters:**
- `task_pattern` (str): Task pattern

**Returns:**
- `AgentConfiguration | None`: Best configuration if found

**Example:**
```python
best = store.get_best_for_task("release_prep")
if best:
    print(f"Best: {best.id} ({best.success_rate:.1%})")
```

---

##### `delete(config_id: str) -> bool`

**Delete a configuration.**

**Parameters:**
- `config_id` (str): Configuration ID

**Returns:**
- `bool`: True if deleted, False if not found

**Raises:**
- `ValueError`: If config_id is invalid
- `OSError`: If file deletion fails

**Example:**
```python
deleted = store.delete("comp_001")
print(f"Deleted: {deleted}")
```

---

##### `list_all() -> list[AgentConfiguration]`

**List all configurations.**

**Returns:**
- `list[AgentConfiguration]`: All configurations, sorted by last_used descending

**Example:**
```python
all_configs = store.list_all()
for config in all_configs:
    print(f"{config.id}: used {config.usage_count} times")
```

---

## Workflows

**Module:** `empathy_os.workflows`

### Release Preparation

#### `OrchestratedReleasePrepWorkflow`

**Release preparation workflow using meta-orchestration.**

```python
class OrchestratedReleasePrepWorkflow:
    DEFAULT_QUALITY_GATES = {
        "min_coverage": 80.0,
        "min_quality_score": 7.0,
        "max_critical_issues": 0.0,
        "min_doc_coverage": 100.0,
    }

    def __init__(
        self,
        quality_gates: dict[str, float] | None = None,
        agent_ids: list[str] | None = None,
    ): ...

    async def execute(
        self, path: str = ".", context: dict[str, Any] | None = None
    ) -> ReleaseReadinessReport: ...
```

**Parameters (\_\_init\_\_):**
- `quality_gates` (dict[str, float] | None): Custom quality gate thresholds
- `agent_ids` (list[str] | None): Specific agent IDs to use

**Parameters (execute):**
- `path` (str): Path to codebase (default: ".")
- `context` (dict[str, Any] | None): Additional context

**Returns:**
- `ReleaseReadinessReport`: Consolidated readiness assessment

**Raises:**
- `ValueError`: If path is invalid or quality gates are invalid

**Example:**
```python
workflow = OrchestratedReleasePrepWorkflow(
    quality_gates={
        "min_coverage": 90.0,
        "max_critical_issues": 0,
    }
)

report = await workflow.execute(path="./my-project")

if report.approved:
    print("✅ Release approved!")
else:
    for blocker in report.blockers:
        print(f"❌ {blocker}")
```

---

#### `ReleaseReadinessReport`

**Consolidated release readiness assessment.**

```python
@dataclass
class ReleaseReadinessReport:
    approved: bool
    confidence: str
    quality_gates: list[QualityGate] = field(default_factory=list)
    agent_results: dict[str, dict] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_duration: float = 0.0
```

**Attributes:**
- `approved` (bool): Overall release approval status
- `confidence` (str): Confidence level ("high", "medium", "low")
- `quality_gates` (list[QualityGate]): Quality gate results
- `agent_results` (dict[str, dict]): Individual agent outputs
- `blockers` (list[str]): Critical issues blocking release
- `warnings` (list[str]): Non-critical issues
- `summary` (str): Executive summary
- `timestamp` (str): Report generation time (ISO format)
- `total_duration` (float): Total execution time in seconds

**Methods:**

##### `to_dict() -> dict[str, Any]`

**Convert report to dictionary format.**

**Returns:**
- `dict[str, Any]`: JSON-serializable dictionary

---

##### `format_console_output() -> str`

**Format report for console display.**

**Returns:**
- `str`: Formatted report

**Example:**
```python
print(report.format_console_output())
```

---

### Test Coverage Boost

#### `TestCoverageBoostWorkflow`

**Test coverage boost workflow using meta-orchestration.**

```python
class TestCoverageBoostWorkflow:
    def __init__(
        self,
        target_coverage: float = 80.0,
        project_root: str = ".",
        save_patterns: bool = True,
    ): ...

    async def execute(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, Any]: ...
```

**Parameters (\_\_init\_\_):**
- `target_coverage` (float): Target coverage percentage (0-100)
- `project_root` (str): Project root directory
- `save_patterns` (bool): Whether to save successful patterns

**Parameters (execute):**
- `context` (dict[str, Any] | None): Execution context (e.g., current_coverage)

**Returns:**
- `dict[str, Any]`: Results with coverage improvement metrics

**Example:**
```python
workflow = TestCoverageBoostWorkflow(
    target_coverage=90.0,
    project_root="./src",
    save_patterns=True
)

result = await workflow.execute({
    "current_coverage": 75.0
})

print(f"Improvement: {result['coverage_improvement']}%")
print(f"New tests: {result['tests_generated']}")
```

---

## Complete Example

**Putting it all together:**

```python
import asyncio
from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator
from empathy_os.orchestration.execution_strategies import get_strategy
from empathy_os.orchestration.config_store import (
    ConfigurationStore,
    AgentConfiguration,
)
from empathy_os.workflows.orchestrated_release_prep import (
    OrchestratedReleasePrepWorkflow
)

async def main():
    # Option 1: Use pre-built workflow
    workflow = OrchestratedReleasePrepWorkflow()
    report = await workflow.execute(path=".")

    if report.approved:
        print("✅ Release approved!")
    else:
        print("❌ Release blocked:")
        for blocker in report.blockers:
            print(f"  • {blocker}")

    # Option 2: Manual orchestration
    orchestrator = MetaOrchestrator()
    store = ConfigurationStore()

    # Check for proven composition
    best = store.get_best_for_task("release_prep")

    if best and best.success_rate >= 0.8:
        # Reuse proven composition
        agents = [get_template(a["role"]) for a in best.agents]
        strategy = get_strategy(best.strategy)
    else:
        # Create new composition
        plan = orchestrator.analyze_and_compose(
            task="Prepare for release",
            context={"version": "3.12.0"}
        )
        agents = plan.agents
        strategy = get_strategy(plan.strategy.value)

    # Execute
    result = await strategy.execute(agents, {"path": "."})

    # Record outcome
    if best:
        quality_score = 85.0  # Calculate from result
        best.record_outcome(result.success, quality_score)
        store.save(best)

asyncio.run(main())
```

---

## Type Hints

**All public APIs have complete type hints:**

```python
from typing import Any, Dict, List, Optional

# Aliases for backward compatibility
Context = Dict[str, Any]
AgentList = List[AgentTemplate]
QualityGates = Dict[str, Any]

# Return types
async def execute(...) -> StrategyResult: ...
def search(...) -> list[AgentConfiguration]: ...
```

---

## Error Handling

**All functions validate inputs and raise appropriate exceptions:**

```python
try:
    template = get_template("invalid_id")
except ValueError as e:
    print(f"Invalid template ID: {e}")

try:
    plan = orchestrator.analyze_and_compose("", context)
except ValueError as e:
    print(f"Invalid task: {e}")

try:
    result = await strategy.execute([], context)
except ValueError as e:
    print(f"Empty agents list: {e}")
```

---

## Next Steps

- **User Guide:** [ORCHESTRATION_USER_GUIDE.md](ORCHESTRATION_USER_GUIDE.md)
- **Examples:** [examples/orchestration/](../examples/orchestration/)
- **Source Code:** [src/empathy_os/orchestration/](../src/empathy_os/orchestration/)

---

**Questions?** Open an issue on [GitHub](https://github.com/Smart-AI-Memory/empathy-framework/issues)
