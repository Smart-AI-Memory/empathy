# Multi-Model Workflows

Cost-optimized workflow pipelines that route tasks to appropriate model tiers.

## Overview

Multi-model workflows enable you to build sophisticated AI pipelines that automatically route different stages of work to the most cost-effective model. Instead of using the most expensive model for everything, workflows intelligently match task complexity to model capability.

### The 3-Tier Model System

| Tier | Models | Cost | Best For |
|------|--------|------|----------|
| **Cheap** | Haiku, GPT-4o-mini | $0.25-1.25/M tokens | Summarization, classification, triage |
| **Capable** | Sonnet, GPT-4o | $3-15/M tokens | Analysis, code generation, security review |
| **Premium** | Opus, o1 | $15-75/M tokens | Synthesis, architectural decisions, coordination |

### Typical Savings

Most workflows achieve **80-96% cost reduction** compared to using premium models for everything.

## Quick Start

```python
from empathy_os.workflows import ResearchSynthesisWorkflow

# Create and run a workflow
workflow = ResearchSynthesisWorkflow()
result = await workflow.execute(
    sources=["doc1.md", "doc2.md", "doc3.md"],
    question="What are the key patterns?"
)

# Check results
print(f"Cost: ${result.cost_report.total_cost:.4f}")
print(f"Savings: {result.cost_report.savings_percent:.1f}%")
print(f"Answer: {result.final_output}")
```

## CLI Usage

```bash
# List available workflows
empathy workflow list

# Describe a workflow's stages
empathy workflow describe research

# Run a workflow
empathy workflow run research --input '{"sources": ["doc1.md"], "question": "Summarize"}'

# Get JSON output
empathy workflow run code-review --input '{"diff": "..."}' --json
```

## Built-in Workflows

### Research Synthesis

**Stages:** summarize (cheap) → analyze (capable) → synthesize (premium)

Optimized for multi-source research tasks. Uses cheap models to summarize each source in parallel, capable models to identify patterns, and premium models only for final synthesis when complexity warrants it.

```python
from empathy_os.workflows import ResearchSynthesisWorkflow

workflow = ResearchSynthesisWorkflow(
    complexity_threshold=0.7  # Only use premium if complexity > 70%
)

result = await workflow.execute(
    sources=["paper1.pdf", "paper2.pdf", "notes.md"],
    question="What are the emerging trends in AI safety?"
)
```

### Code Review

**Stages:** classify (cheap) → scan (capable) → architect_review (premium, conditional)

Tiered code analysis that classifies changes cheaply, scans for security/bugs with capable models, and only invokes premium architectural review for large or critical changes.

```python
from empathy_os.workflows import CodeReviewWorkflow

workflow = CodeReviewWorkflow(
    file_threshold=10,  # Premium review if 10+ files changed
    core_modules=["src/core/", "src/security/"]  # Always review core modules
)

result = await workflow.execute(
    diff="...",
    files_changed=["src/utils.py", "tests/test_utils.py"],
    is_core_module=False
)

# Access findings
security_findings = result.final_output.get("security_findings", [])
```

### Document Generation

**Stages:** outline (cheap) → write (capable) → polish (premium)

Cost-optimized documentation generation. Creates outlines cheaply, writes content with capable models, and uses premium models for final polish only on longer documents.

```python
from empathy_os.workflows import DocumentGenerationWorkflow

workflow = DocumentGenerationWorkflow(
    skip_polish_threshold=1000,  # Skip premium for short docs
    max_sections=10
)

result = await workflow.execute(
    source_code="def my_function(): ...",
    doc_type="api_reference",  # or "tutorial", "architecture"
    audience="developers"
)
```

## Creating Custom Workflows

Extend `BaseWorkflow` to create your own multi-model pipelines:

```python
from empathy_os.workflows import BaseWorkflow, ModelTier

class MyCustomWorkflow(BaseWorkflow):
    """My custom 3-stage workflow."""

    name = "custom"
    description = "Custom workflow for specialized tasks"
    stages = ["prepare", "process", "finalize"]
    tier_map = {
        "prepare": ModelTier.CHEAP,
        "process": ModelTier.CAPABLE,
        "finalize": ModelTier.PREMIUM,
    }

    async def run_stage(self, stage_name, tier, input_data):
        """Execute a single stage."""
        if stage_name == "prepare":
            # Your preparation logic
            output = {"prepared_data": input_data}
            return output, 100, 50  # (output, input_tokens, output_tokens)

        elif stage_name == "process":
            # Your processing logic
            output = {"processed": True}
            return output, 200, 100

        elif stage_name == "finalize":
            # Your finalization logic
            output = {"result": "done"}
            return output, 150, 75

    def should_skip_stage(self, stage_name, input_data):
        """Optionally skip stages based on conditions."""
        if stage_name == "finalize" and input_data.get("simple_mode"):
            return True, "Simple mode - skipping finalization"
        return False, None
```

## Cost Tracking Integration

All workflows integrate with Empathy's cost tracking system:

```python
from empathy_os.cost_tracker import CostTracker

# Use shared cost tracker
tracker = CostTracker()
workflow = ResearchSynthesisWorkflow(cost_tracker=tracker)

await workflow.execute(sources=["doc.md"], question="Summary?")

# View costs
report = tracker.get_report()
print(f"Total session cost: ${report['total_cost']:.4f}")
```

View workflow costs in the CLI:

```bash
empathy costs --days 7
```

## Workflow Results

Every workflow execution returns a `WorkflowResult`:

```python
result = await workflow.execute(...)

# Check success
if result.success:
    print(result.final_output)
else:
    print(f"Error: {result.error}")

# Inspect stages
for stage in result.stages:
    print(f"{stage.name}: {stage.tier.value} - ${stage.cost:.6f}")
    if stage.skipped:
        print(f"  Skipped: {stage.skip_reason}")

# Cost analysis
report = result.cost_report
print(f"Total: ${report.total_cost:.4f}")
print(f"Baseline (all premium): ${report.baseline_cost:.4f}")
print(f"Saved: ${report.savings:.4f} ({report.savings_percent:.1f}%)")

# Timing
print(f"Duration: {result.total_duration_ms}ms")
```

## Best Practices

### 1. Match Complexity to Tier

- **Cheap tier**: Summarization, classification, extraction, formatting
- **Capable tier**: Analysis, code generation, pattern matching, security review
- **Premium tier**: Synthesis, reasoning, architectural decisions, complex judgment

### 2. Use Conditional Stages

Skip expensive stages when not needed:

```python
def should_skip_stage(self, stage_name, input_data):
    if stage_name == "premium_analysis":
        # Only run for complex inputs
        if input_data.get("complexity_score", 0) < 0.5:
            return True, "Low complexity - skipping premium analysis"
    return False, None
```

### 3. Parallelize When Possible

For independent tasks, consider running in parallel (implementation note: parallel execution is on the roadmap for future versions).

### 4. Track and Optimize

Monitor your workflow costs:

```bash
# View cost breakdown by workflow
empathy costs --days 30

# Compare workflows
empathy workflow run research --input '...' --json | jq .cost_report
```

## See Also

- [Cost Tracking Guide](cost-tracking.md)
- [Agent Factory](agent-factory.md)
- [Multi-Agent Coordination](multi-agent-coordination.md)
