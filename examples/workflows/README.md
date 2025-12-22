# Multi-Model Workflow Examples

Examples demonstrating cost-optimized multi-model workflows.

## Overview

These examples show how to use the 3-tier model routing system:

| Tier | Models | Cost | Use Case |
|------|--------|------|----------|
| Cheap | Haiku | $0.25-1.25/M | Summarization, classification |
| Capable | Sonnet | $3-15/M | Analysis, code generation |
| Premium | Opus | $15-75/M | Synthesis, architecture |

## Examples

### Research Synthesis (`research_example.py`)

Multi-source research pipeline that:
1. Summarizes each source with cheap models
2. Identifies patterns with capable models
3. Synthesizes insights with premium models (conditional)

```bash
python examples/workflows/research_example.py
```

### Code Review (`code_review_example.py`)

Tiered code analysis that:
1. Classifies changes (bug fix, feature, refactor)
2. Scans for security issues and bug patterns
3. Performs architectural review for large/critical changes

```bash
python examples/workflows/code_review_example.py
```

### Document Generation (`doc_gen_example.py`)

Cost-optimized documentation that:
1. Generates outline from code/specs
2. Writes each section
3. Polishes for consistency (conditional)

```bash
python examples/workflows/doc_gen_example.py
```

## Creating Custom Workflows

```python
from empathy_os.workflows import BaseWorkflow, ModelTier

class MyWorkflow(BaseWorkflow):
    name = "my-workflow"
    stages = ["prepare", "process", "finalize"]
    tier_map = {
        "prepare": ModelTier.CHEAP,
        "process": ModelTier.CAPABLE,
        "finalize": ModelTier.PREMIUM,
    }

    async def run_stage(self, stage_name, tier, input_data):
        # Your implementation
        return output, input_tokens, output_tokens
```

## CLI Usage

```bash
# List workflows
empathy workflow list

# Describe a workflow
empathy workflow describe research

# Run a workflow
empathy workflow run research --input '{"sources": ["doc.md"]}'
```

## See Also

- [Multi-Model Workflows Guide](../../docs/guides/multi-model-workflows.md)
- [Cost Tracking](../../docs/guides/cost-tracking.md)
