# Meta-Orchestration User Guide

**Version:** 3.12.0
**Last Updated:** January 10, 2026
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [CLI Reference](#cli-reference)
4. [Python API](#python-api)
5. [Agent Templates](#agent-templates)
6. [Composition Patterns](#composition-patterns)
7. [Configuration Store](#configuration-store)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Meta-Orchestration?

**Meta-orchestration is intelligent agent team composition.** Instead of manually coordinating multiple AI agents, the meta-orchestrator:

1. **Analyzes your task** to understand complexity and requirements
2. **Selects appropriate agents** from a library of expert templates
3. **Chooses composition patterns** (sequential, parallel, debate, etc.)
4. **Executes the team** with quality gates and monitoring
5. **Learns from outcomes** to improve future compositions

Think of it as a **conductor for AI agents** - it knows which agents to use, in what order, and how to coordinate them for optimal results.

### Why Use Meta-Orchestration?

**Manual agent coordination is complex:**
```python
# Manual approach - 50+ lines of coordination code
analyzer = SecurityAnalyzer()
tester = TestAnalyzer()
reviewer = CodeReviewer()
docs = DocWriter()

# Run in parallel
results = await asyncio.gather(
    analyzer.run(), tester.run(), reviewer.run(), docs.run()
)

# Aggregate results
if all(r.passed for r in results):
    # Check quality gates
    if results[0].critical_issues == 0 and results[1].coverage >= 80:
        # Generate report...
        pass
```

**Meta-orchestration simplifies this:**
```python
# Meta-orchestration approach - 3 lines
workflow = OrchestratedReleasePrepWorkflow()
report = await workflow.execute(path=".")
print(report.format_console_output())  # Done!
```

### Key Benefits

- ✅ **Faster development** - Pre-built workflows eliminate boilerplate
- ✅ **Better outcomes** - Proven compositions backed by quality gates
- ✅ **Cost optimization** - Right-sized agent tiers (CHEAP → CAPABLE → PREMIUM)
- ✅ **Learning system** - Configurations improve over time through feedback
- ✅ **Production-ready** - Comprehensive testing, security validation, monitoring

---

## Getting Started

### Installation

Meta-orchestration is included in Empathy Framework v3.12.0+:

```bash
pip install empathy-framework[developer]>=3.12.0
```

### Quick Start: Release Preparation

**Run release readiness validation with 4 parallel agents:**

```bash
empathy orchestrate release-prep
```

This executes:
- **Security Auditor** (vulnerability scan)
- **Test Coverage Analyzer** (gap analysis)
- **Code Quality Reviewer** (best practices)
- **Documentation Writer** (completeness check)

**Output:**
```
======================================================================
RELEASE READINESS REPORT (Meta-Orchestrated)
======================================================================

Status: ✅ READY FOR RELEASE
Confidence: HIGH
Generated: 2026-01-10T14:32:15
Duration: 12.45s

----------------------------------------------------------------------
QUALITY GATES
----------------------------------------------------------------------
✅ Security: PASS (actual: 0.0, threshold: 0.0)
✅ Test Coverage: PASS (actual: 85.2, threshold: 80.0)
✅ Code Quality: PASS (actual: 8.5, threshold: 7.0)
⚠️  Documentation: below threshold (actual: 95.0, threshold: 100.0)

----------------------------------------------------------------------
AGENTS EXECUTED (4)
----------------------------------------------------------------------
✅ security_auditor: 3.21s
✅ test_coverage_analyzer: 4.55s
✅ code_reviewer: 2.98s
✅ documentation_writer: 1.71s
```

### Quick Start: Test Coverage Boost

**Boost test coverage to 90% using sequential workflow:**

```bash
empathy orchestrate test-coverage --target 90
```

This executes:
1. **Coverage Analyzer** → Identify gaps
2. **Test Generator** → Create tests for gaps
3. **Test Validator** → Verify tests pass

---

## CLI Reference

### `empathy orchestrate`

Run meta-orchestration workflows from the command line.

```bash
empathy orchestrate <workflow> [options]
```

---

### Release Preparation Workflow

**Command:**
```bash
empathy orchestrate release-prep [options]
```

**Description:**
Validates release readiness by running 4 parallel validation agents with quality gates.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--path <path>` | Path to codebase to analyze | `.` (current dir) |
| `--min-coverage <float>` | Minimum test coverage required (0-100) | `80.0` |
| `--min-quality <float>` | Minimum code quality score (0-10) | `7.0` |
| `--max-critical <int>` | Maximum critical security issues | `0` |
| `--json` | Output results as JSON | `false` |

**Examples:**

```bash
# Basic usage (current directory, default gates)
empathy orchestrate release-prep

# Custom path with strict quality gates
empathy orchestrate release-prep \
  --path ./my-project \
  --min-coverage 90 \
  --min-quality 8.5 \
  --max-critical 0

# JSON output for CI integration
empathy orchestrate release-prep --json > report.json
```

**Exit Codes:**
- `0` - Release approved (all quality gates passed)
- `1` - Release blocked (quality gates failed or errors)

---

### Test Coverage Boost Workflow

**Command:**
```bash
empathy orchestrate test-coverage [options]
```

**Description:**
Sequentially analyzes gaps, generates tests, and validates coverage improvement.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--target <float>` | Target coverage percentage (0-100) | `80.0` |
| `--project-root <path>` | Project root directory | `.` |
| `--current-coverage <float>` | Current coverage (for context) | Auto-detected |

**Examples:**

```bash
# Boost to 90% coverage
empathy orchestrate test-coverage --target 90

# Specify project root
empathy orchestrate test-coverage \
  --target 85 \
  --project-root ./src

# Provide current coverage hint
empathy orchestrate test-coverage \
  --target 90 \
  --current-coverage 75
```

**Exit Codes:**
- `0` - Target coverage achieved
- `1` - Failed to reach target or errors

---

## Python API

### Basic Usage

```python
import asyncio
from empathy_os.workflows.orchestrated_release_prep import (
    OrchestratedReleasePrepWorkflow
)

async def main():
    # Create workflow with default quality gates
    workflow = OrchestratedReleasePrepWorkflow()

    # Execute on current directory
    report = await workflow.execute(path=".")

    # Check results
    if report.approved:
        print("✅ Release approved!")
        print(f"Confidence: {report.confidence}")
    else:
        print("❌ Release blocked")
        for blocker in report.blockers:
            print(f"  • {blocker}")

asyncio.run(main())
```

### Custom Quality Gates

```python
from empathy_os.workflows.orchestrated_release_prep import (
    OrchestratedReleasePrepWorkflow
)

# Define custom quality gates
quality_gates = {
    "min_coverage": 90.0,           # 90% test coverage
    "min_quality_score": 8.5,       # High code quality
    "max_critical_issues": 0,       # Zero critical vulns
    "min_doc_coverage": 100.0,      # Full API documentation
}

workflow = OrchestratedReleasePrepWorkflow(quality_gates=quality_gates)
report = await workflow.execute(path="./my-project")
```

### Using Specific Agents

```python
# Override default agents with custom selection
workflow = OrchestratedReleasePrepWorkflow(
    agent_ids=[
        "security_auditor",
        "test_coverage_analyzer",
        "performance_optimizer",  # Add performance check
    ]
)

report = await workflow.execute(path=".")
```

### Test Coverage Boost

```python
from empathy_os.workflows.test_coverage_boost import (
    TestCoverageBoostWorkflow
)

# Create workflow
workflow = TestCoverageBoostWorkflow(
    target_coverage=90.0,
    project_root="./src",
    save_patterns=True,  # Save successful compositions
)

# Execute with context
result = await workflow.execute({
    "current_coverage": 75.0,
    "priority_modules": ["auth", "payment"],
})

print(f"Coverage improved by {result['coverage_improvement']}%")
print(f"New tests: {result['tests_generated']}")
```

### Direct Meta-Orchestrator Usage

**For custom workflows:**

```python
from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator
from empathy_os.orchestration.execution_strategies import get_strategy

# Create orchestrator
orchestrator = MetaOrchestrator()

# Analyze task and create execution plan
plan = orchestrator.analyze_and_compose(
    task="Improve code quality and performance",
    context={
        "current_quality_score": 6.5,
        "performance_baseline": "10s",
    }
)

print(f"Selected agents: {[a.id for a in plan.agents]}")
print(f"Strategy: {plan.strategy.value}")
print(f"Estimated cost: {plan.estimated_cost}")

# Execute plan
strategy = get_strategy(plan.strategy.value)
result = await strategy.execute(plan.agents, context)

print(f"Success: {result.success}")
print(f"Duration: {result.total_duration:.2f}s")
```

---

## Agent Templates

### Overview

Agent templates are **reusable agent archetypes** with pre-defined capabilities, tools, and quality gates.

**7 pre-built templates:**

1. **Test Coverage Analyzer** - Gap analysis and test suggestions
2. **Security Auditor** - Vulnerability scanning and compliance
3. **Code Reviewer** - Quality assessment and best practices
4. **Documentation Writer** - API docs and examples
5. **Performance Optimizer** - Profiling and optimization
6. **Architecture Analyst** - Design patterns and dependencies
7. **Refactoring Specialist** - Code smells and improvements

### Template Structure

```python
@dataclass
class AgentTemplate:
    id: str                              # Unique identifier
    role: str                            # Human-readable role
    capabilities: list[str]              # What agent can do
    tier_preference: str                 # "CHEAP", "CAPABLE", "PREMIUM"
    tools: list[str]                     # Required tools
    default_instructions: str            # Agent prompt
    quality_gates: dict[str, Any]        # Quality thresholds
    resource_requirements: ResourceRequirements  # Limits
```

### Retrieving Templates

```python
from empathy_os.orchestration.agent_templates import (
    get_template,
    get_all_templates,
    get_templates_by_capability,
    get_templates_by_tier,
)

# Get specific template
template = get_template("test_coverage_analyzer")
print(template.role)  # "Test Coverage Expert"

# Get all templates
all_templates = get_all_templates()
print(f"Available: {len(all_templates)} templates")

# Find by capability
security_templates = get_templates_by_capability("vulnerability_scan")

# Find by tier (cost optimization)
cheap_templates = get_templates_by_tier("CHEAP")
```

### Template Capabilities Reference

| Template | Capabilities | Tier | Use Cases |
|----------|-------------|------|-----------|
| **test_coverage_analyzer** | analyze_gaps, suggest_tests, validate_coverage | CAPABLE | Gap analysis, coverage improvement |
| **security_auditor** | vulnerability_scan, threat_modeling, compliance_check | PREMIUM | Security audits, compliance validation |
| **code_reviewer** | code_review, quality_assessment, best_practices_check | CAPABLE | Code reviews, quality checks |
| **documentation_writer** | generate_docs, check_completeness, update_examples | CHEAP | API docs, tutorials, examples |
| **performance_optimizer** | profile_code, identify_bottlenecks, suggest_optimizations | CAPABLE | Performance analysis, optimization |
| **architecture_analyst** | analyze_architecture, identify_patterns, suggest_improvements | PREMIUM | Architecture review, refactoring |
| **refactoring_specialist** | identify_code_smells, suggest_refactorings, validate_changes | CAPABLE | Refactoring, technical debt |

---

## Composition Patterns

### Overview

**Composition patterns define HOW agents work together.** The meta-orchestrator automatically selects the best pattern based on task characteristics.

**6 composition patterns (grammar rules):**

1. **Sequential** (A → B → C) - Pipeline processing
2. **Parallel** (A ‖ B ‖ C) - Independent validation
3. **Debate** (A ⇄ B ⇄ C → Synthesis) - Consensus building
4. **Teaching** (Junior → Expert validation) - Cost optimization
5. **Refinement** (Draft → Review → Polish) - Iterative improvement
6. **Adaptive** (Classifier → Specialist) - Right-sizing

---

### 1. Sequential Strategy

**Pattern:** A → B → C
**Use when:** Tasks must be done in order, each step depends on previous results

```python
from empathy_os.orchestration.execution_strategies import SequentialStrategy

strategy = SequentialStrategy()

# Execute agents in order
# Agent B receives Agent A's output in context
# Agent C receives Agent A + B outputs
result = await strategy.execute(agents, context)
```

**Example:**
Coverage Analyzer → Test Generator → Test Validator

**When selected:**
- Task is sequential (contains "generate", "create", "refactor")
- Testing domain with multiple agents
- Default for most multi-agent tasks

---

### 2. Parallel Strategy

**Pattern:** A ‖ B ‖ C
**Use when:** Independent validations needed, time optimization important

```python
from empathy_os.orchestration.execution_strategies import ParallelStrategy

strategy = ParallelStrategy()

# Execute all agents simultaneously
# Each receives same initial context
# Results aggregated at end
result = await strategy.execute(agents, context)
```

**Example:**
Security Audit ‖ Performance Check ‖ Code Quality ‖ Docs Check

**When selected:**
- Task contains "release", "audit", "check", "validate", "review"
- Security or architecture domain
- Task marked as parallelizable

**Benefits:**
- Fastest execution (bounded by slowest agent)
- Multiple perspectives on same problem
- Independent quality checks

---

### 3. Debate Strategy

**Pattern:** A ⇄ B ⇄ C → Synthesis
**Use when:** Multiple expert opinions needed, tradeoff analysis required

```python
from empathy_os.orchestration.execution_strategies import DebateStrategy

strategy = DebateStrategy()

# Phase 1: Agents provide independent opinions (parallel)
# Phase 2: Synthesizer aggregates and resolves conflicts
result = await strategy.execute(agents, context)

# Access synthesis
consensus = result.aggregated_output["consensus"]
```

**Example:**
Architect(scale) ‖ Architect(cost) ‖ Architect(simplicity) → Synthesizer

**When selected:**
- Multiple agents with same capability detected
- Architecture decisions requiring debate
- Complex tasks needing multi-perspective analysis

**Output structure:**
```python
{
    "debate_participants": ["agent1", "agent2", "agent3"],
    "opinions": [...],  # Individual agent outputs
    "consensus": {
        "consensus_reached": True,
        "success_votes": 3,
        "total_votes": 3,
        "avg_confidence": 0.87
    }
}
```

---

### 4. Teaching Strategy

**Pattern:** Junior → Expert validation
**Use when:** Cost-effective generation desired, quality assurance critical

```python
from empathy_os.orchestration.execution_strategies import TeachingStrategy

# Configure quality threshold
strategy = TeachingStrategy(quality_threshold=0.7)

# Junior attempts task (CHEAP tier)
# If confidence >= 0.7: done
# If confidence < 0.7: expert takes over (CAPABLE/PREMIUM)
result = await strategy.execute([junior, expert], context)

outcome = result.aggregated_output["outcome"]
# "junior_success" or "expert_takeover"
```

**Example:**
Junior Writer(CHEAP) → Quality Gate → (pass ? done : Expert Review(CAPABLE))

**When selected:**
- Documentation domain
- Simple tasks with review needed
- Cost optimization desired

**Cost savings:**
- Junior success: ~70% cost reduction
- Expert takeover: Same cost as direct expert use
- Average savings: 40-50% (assuming 60% junior success rate)

---

### 5. Refinement Strategy

**Pattern:** Draft → Review → Polish
**Use when:** Iterative improvement needed, quality ladder desired

```python
from empathy_os.orchestration.execution_strategies import RefinementStrategy

strategy = RefinementStrategy()

# Stage 1: Drafter creates initial version (CHEAP)
# Stage 2: Reviewer improves (CAPABLE)
# Stage 3: Polisher finalizes (PREMIUM)
result = await strategy.execute([drafter, reviewer, polisher], context)

final_output = result.aggregated_output["final_output"]
```

**Example:**
Drafter(CHEAP) → Reviewer(CAPABLE) → Polisher(PREMIUM)

**When selected:**
- Refactoring domain
- Multi-stage refinement beneficial
- Quality progression desired

**Benefits:**
- Progressive quality improvement
- Each stage builds on previous
- Final output is highest quality

---

### 6. Adaptive Strategy

**Pattern:** Classifier → Specialist
**Use when:** Variable task complexity, cost optimization desired

```python
from empathy_os.orchestration.execution_strategies import AdaptiveStrategy

strategy = AdaptiveStrategy()

# Phase 1: Classifier assesses complexity (CHEAP)
# Phase 2: Route to appropriate specialist tier
result = await strategy.execute([classifier, *specialists], context)

selected = result.aggregated_output["selected_specialist"]
```

**Example:**
Classifier(CHEAP) → route(simple|moderate|complex) → Specialist(tier)

**When selected:**
- Complex tasks (contains "architecture", "migrate", "redesign")
- Variable task complexity
- Right-sizing important

**Routing logic:**
- High confidence (>0.8) → Simple task → CHEAP specialist
- Low confidence (<0.8) → Complex task → PREMIUM specialist

**Cost savings:**
- Simple tasks: ~70% cost reduction (CHEAP instead of PREMIUM)
- Complex tasks: Same cost (PREMIUM when needed)
- Average savings: 30-40% (assuming task distribution)

---

### Pattern Selection Rules

**How the meta-orchestrator chooses:**

```python
# Priority order (first match wins):

1. If task is parallelizable → PARALLEL
2. If security/architecture domain → PARALLEL (even 1 agent)
3. If documentation domain → TEACHING
4. If refactoring domain → REFINEMENT
5. If single agent → SEQUENTIAL
6. If duplicate capabilities → DEBATE
7. If testing domain → SEQUENTIAL
8. If complex task → ADAPTIVE
9. Default → SEQUENTIAL
```

**Override pattern:**

```python
from empathy_os.orchestration.execution_strategies import get_strategy

# Force specific pattern
strategy = get_strategy("parallel")
result = await strategy.execute(agents, context)
```

---

## Configuration Store

### Overview

The **Configuration Store** is the learning/memory system for meta-orchestration. It:
- Saves successful agent compositions
- Tracks performance metrics over time
- Retrieves proven solutions for similar tasks
- Learns from outcomes to improve future decisions

**Think of it as:** A database of "what worked" that grows smarter over time.

### Architecture

```
.empathy/orchestration/compositions/
├── release_prep_001.json
├── test_coverage_boost_001.json
└── security_deep_dive_001.json
```

Each configuration stores:
- Agent team composition
- Execution strategy used
- Quality gates enforced
- Performance metrics (success rate, quality score)
- Usage statistics

---

### Basic Usage

```python
from empathy_os.orchestration.config_store import (
    ConfigurationStore,
    AgentConfiguration,
)

# Initialize store
store = ConfigurationStore()

# Save successful composition
config = AgentConfiguration(
    id="comp_release_001",
    task_pattern="release_preparation",
    agents=[
        {"role": "security_auditor", "tier": "PREMIUM"},
        {"role": "test_analyzer", "tier": "CAPABLE"},
    ],
    strategy="parallel",
    quality_gates={"min_coverage": 80},
)

store.save(config)

# Load for reuse
loaded = store.load("comp_release_001")

# Search for similar tasks
matches = store.search(
    task_pattern="release_preparation",
    min_success_rate=0.8,
)

for match in matches:
    print(f"{match.id}: {match.success_rate:.1%} success")
```

---

### Recording Outcomes

```python
# After execution, record outcome
config = store.load("comp_release_001")

# Record successful execution
config.record_outcome(
    success=True,
    quality_score=87.5,  # 0-100
)

# Save updated metrics
store.save(config)

# Metrics are automatically updated:
# - usage_count: 1 → 2
# - success_count: 1 → 2
# - success_rate: recalculated
# - avg_quality_score: weighted average
# - last_used: updated to now
```

---

### Searching Configurations

```python
# Find best for specific task
best = store.get_best_for_task("release_preparation")
print(f"Best: {best.id} ({best.success_rate:.1%})")

# Search with filters
matches = store.search(
    task_pattern="test_coverage",
    min_success_rate=0.75,      # 75%+ success
    min_quality_score=80.0,     # Score >= 80
    limit=5,                     # Top 5 results
)

# List all configurations
all_configs = store.list_all()  # Sorted by last_used
```

---

### Integration with Workflows

**Workflows automatically use the configuration store:**

```python
workflow = OrchestratedReleasePrepWorkflow()

# On first run:
# 1. Executes with default agents
# 2. Records outcome in store
# 3. Saves successful composition

# On subsequent runs:
# 1. Checks store for proven composition
# 2. Reuses if found (faster, more reliable)
# 3. Falls back to meta-orchestrator if needed
```

**Manual integration:**

```python
from empathy_os.orchestration.config_store import ConfigurationStore
from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator

store = ConfigurationStore()
orchestrator = MetaOrchestrator()

# Try to load proven composition
best = store.get_best_for_task("release_prep")

if best and best.success_rate >= 0.8:
    # Reuse proven composition
    agents = [get_template(a["role"]) for a in best.agents]
    strategy = get_strategy(best.strategy)
else:
    # Use meta-orchestrator to create new composition
    plan = orchestrator.analyze_and_compose(task, context)
    agents = plan.agents
    strategy = get_strategy(plan.strategy.value)

# Execute...
```

---

### Pattern Library Integration

**Successful compositions contribute to the pattern library:**

```python
from empathy_os.pattern_library import PatternLibrary

store = ConfigurationStore(
    pattern_library=PatternLibrary()
)

# Save configuration
store.save(config)

# After 3+ successful uses with 70%+ success rate:
# → Automatically contributes pattern to library
# → Pattern becomes available for cross-task learning
```

**Benefits:**
- Patterns learned from release prep can inform security audits
- Cross-workflow knowledge sharing
- Framework-wide learning loop

---

## Advanced Usage

### Custom Workflows

**Create your own meta-orchestrated workflows:**

```python
import asyncio
from dataclasses import dataclass
from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator
from empathy_os.orchestration.execution_strategies import get_strategy
from empathy_os.orchestration.config_store import (
    ConfigurationStore,
    AgentConfiguration,
)

@dataclass
class CustomWorkflowResult:
    success: bool
    quality_score: float
    outputs: dict

class CustomWorkflow:
    """Custom workflow using meta-orchestration."""

    def __init__(self):
        self.orchestrator = MetaOrchestrator()
        self.config_store = ConfigurationStore()

    async def execute(self, context: dict) -> CustomWorkflowResult:
        # Step 1: Check for proven composition
        task_pattern = "custom_workflow"
        best = self.config_store.get_best_for_task(task_pattern)

        if best and best.success_rate >= 0.8:
            # Reuse proven composition
            agents = [get_template(a["role"]) for a in best.agents]
            strategy = get_strategy(best.strategy)
        else:
            # Create new composition
            plan = self.orchestrator.analyze_and_compose(
                task="Your task description",
                context=context,
            )
            agents = plan.agents
            strategy = get_strategy(plan.strategy.value)

        # Step 2: Execute
        result = await strategy.execute(agents, context)

        # Step 3: Evaluate quality
        quality_score = self._calculate_quality(result)
        success = quality_score >= 70.0

        # Step 4: Save/update configuration
        if not best:
            best = AgentConfiguration(
                id=f"comp_{task_pattern}_{self._generate_id()}",
                task_pattern=task_pattern,
                agents=[{
                    "role": a.id,
                    "tier": a.tier_preference,
                } for a in agents],
                strategy=strategy.__class__.__name__.replace("Strategy", "").lower(),
                quality_gates={"min_quality": 70.0},
            )

        best.record_outcome(success, quality_score)
        self.config_store.save(best)

        return CustomWorkflowResult(
            success=success,
            quality_score=quality_score,
            outputs={r.agent_id: r.output for r in result.outputs},
        )

    def _calculate_quality(self, result) -> float:
        # Your quality calculation logic
        return 85.0

    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())[:8]

# Usage
workflow = CustomWorkflow()
result = await workflow.execute({"param": "value"})
```

---

### Custom Agent Templates

**Define your own agent templates:**

```python
from empathy_os.orchestration.agent_templates import (
    AgentTemplate,
    ResourceRequirements,
)

# Create custom template
custom_template = AgentTemplate(
    id="data_pipeline_expert",
    role="Data Pipeline Specialist",
    capabilities=[
        "pipeline_design",
        "data_validation",
        "performance_tuning",
    ],
    tier_preference="CAPABLE",
    tools=["spark", "airflow", "dbt"],
    default_instructions="""
You are a data pipeline expert. Your tasks:
1. Design scalable data pipelines
2. Validate data quality and integrity
3. Optimize pipeline performance
4. Ensure fault tolerance and monitoring

Focus on production-ready, maintainable solutions.
    """.strip(),
    quality_gates={
        "min_data_quality": 99.0,
        "max_pipeline_latency": 60,  # seconds
    },
    resource_requirements=ResourceRequirements(
        min_tokens=3000,
        max_tokens=20000,
        timeout_seconds=900,
        memory_mb=2048,
    ),
)

# Use in custom workflow
from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator

orchestrator = MetaOrchestrator()
plan = orchestrator.analyze_and_compose(
    task="Build ETL pipeline for customer data",
    context={"data_sources": ["postgres", "s3"]}
)

# Manually add custom agent
plan.agents.append(custom_template)
```

---

### Multi-Stage Workflows

**Combine multiple orchestration patterns:**

```python
async def multi_stage_workflow(context: dict):
    """Complex workflow with multiple orchestration stages."""

    # Stage 1: Parallel analysis
    analysis_plan = orchestrator.analyze_and_compose(
        task="Analyze codebase for issues",
        context=context,
    )
    analysis_strategy = get_strategy("parallel")
    analysis_result = await analysis_strategy.execute(
        analysis_plan.agents,
        context,
    )

    # Stage 2: Sequential fixes (based on analysis)
    fix_context = {
        **context,
        "analysis": analysis_result.aggregated_output,
    }
    fix_plan = orchestrator.analyze_and_compose(
        task="Fix identified issues",
        context=fix_context,
    )
    fix_strategy = get_strategy("sequential")
    fix_result = await fix_strategy.execute(
        fix_plan.agents,
        fix_context,
    )

    # Stage 3: Validation (parallel)
    validation_plan = orchestrator.analyze_and_compose(
        task="Validate all fixes",
        context={**fix_context, "fixes": fix_result.aggregated_output},
    )
    validation_strategy = get_strategy("parallel")
    validation_result = await validation_strategy.execute(
        validation_plan.agents,
        fix_context,
    )

    return {
        "analysis": analysis_result,
        "fixes": fix_result,
        "validation": validation_result,
    }
```

---

## Troubleshooting

### Common Issues

#### 1. "No agents available for domain"

**Problem:** Meta-orchestrator can't find agents for your task.

**Solution:**
```python
# Check available templates
from empathy_os.orchestration.agent_templates import get_all_templates

templates = get_all_templates()
print(f"Available: {[t.id for t in templates]}")

# Explicitly provide agents
workflow = OrchestratedReleasePrepWorkflow(
    agent_ids=["security_auditor", "code_reviewer"]
)
```

#### 2. Quality gates always failing

**Problem:** Default quality gates too strict for your project.

**Solution:**
```python
# Relax quality gates
quality_gates = {
    "min_coverage": 60.0,        # Lower from 80
    "min_quality_score": 6.0,    # Lower from 7
    "max_critical_issues": 2,    # Allow 2 instead of 0
}

workflow = OrchestratedReleasePrepWorkflow(quality_gates=quality_gates)
```

#### 3. Execution timeout

**Problem:** Agents taking too long to execute.

**Solution:**
```python
# Increase agent timeout
from empathy_os.orchestration.agent_templates import (
    AgentTemplate,
    ResourceRequirements,
)

custom_template = AgentTemplate(
    # ...
    resource_requirements=ResourceRequirements(
        timeout_seconds=1800,  # 30 minutes instead of 5
    )
)
```

#### 4. Configuration store not saving

**Problem:** Permissions issue or invalid path.

**Solution:**
```python
# Use custom storage directory with write permissions
store = ConfigurationStore(
    storage_dir="/tmp/orchestration_configs"
)

# Or check current directory
import os
print(f"Current dir: {os.getcwd()}")
print(f"Writable: {os.access('.empathy', os.W_OK)}")
```

---

### Debugging Tips

**Enable debug logging:**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("empathy_os.orchestration")
logger.setLevel(logging.DEBUG)

# Now see detailed orchestration decisions
workflow = OrchestratedReleasePrepWorkflow()
report = await workflow.execute(path=".")
```

**Inspect execution plan:**

```python
orchestrator = MetaOrchestrator()
plan = orchestrator.analyze_and_compose(task, context)

print(f"Task complexity: {plan.complexity}")
print(f"Task domain: {plan.domain}")
print(f"Selected agents: {[a.id for a in plan.agents]}")
print(f"Strategy: {plan.strategy.value}")
print(f"Estimated cost: {plan.estimated_cost}")
print(f"Estimated duration: {plan.estimated_duration}s")
```

**Validate agent results:**

```python
result = await strategy.execute(agents, context)

for agent_result in result.outputs:
    print(f"\nAgent: {agent_result.agent_id}")
    print(f"Success: {agent_result.success}")
    print(f"Confidence: {agent_result.confidence}")
    print(f"Duration: {agent_result.duration_seconds:.2f}s")

    if not agent_result.success:
        print(f"Error: {agent_result.error}")
    else:
        print(f"Output keys: {list(agent_result.output.keys())}")
```

---

### Performance Optimization

**Reduce execution time:**

```python
# 1. Use parallel strategy when possible
strategy = get_strategy("parallel")

# 2. Use cheaper tiers for non-critical tasks
from empathy_os.orchestration.agent_templates import get_templates_by_tier

cheap_agents = get_templates_by_tier("CHEAP")

# 3. Limit number of agents
workflow = OrchestratedReleasePrepWorkflow(
    agent_ids=["security_auditor", "test_coverage_analyzer"]  # Only 2
)

# 4. Reuse proven configurations (automatic)
store = ConfigurationStore()
best = store.get_best_for_task("release_prep")
# Uses cached composition instead of re-analyzing
```

---

### Getting Help

**Resources:**
- [API Documentation](ORCHESTRATION_API.md)
- [GitHub Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
- [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions)
- [Example Code](../examples/orchestration/)

**Report bugs:**
```bash
empathy orchestrate release-prep --json > debug.json

# Then attach debug.json to your issue
```

---

## Next Steps

1. **Try the built-in workflows:**
   ```bash
   empathy orchestrate release-prep
   empathy orchestrate test-coverage --target 90
   ```

2. **Read the API documentation:** [ORCHESTRATION_API.md](ORCHESTRATION_API.md)

3. **Explore examples:** [examples/orchestration/](../examples/orchestration/)

4. **Build custom workflows:** See [Advanced Usage](#advanced-usage)

5. **Contribute patterns:** Successful compositions automatically improve the system!

---

**Questions or feedback?** Open an issue or discussion on GitHub!
