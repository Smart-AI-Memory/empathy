#!/usr/bin/env python3
"""Document Generation Workflow Example

Demonstrates cost-optimized documentation generation using the 3-tier model system:
1. Haiku (cheap): Generate outline from code/specs
2. Sonnet (capable): Write each section content
3. Opus (premium): Final review and consistency polish

The premium polish stage is conditionally skipped for shorter documents.

Run:
    python examples/workflows/doc_gen_example.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio

from empathy_os.workflows import DocumentGenerationWorkflow


async def generate_api_docs():
    """Generate API reference documentation."""
    print("\n" + "-" * 50)
    print("  SCENARIO 1: API Reference Documentation")
    print("-" * 50 + "\n")

    workflow = DocumentGenerationWorkflow(
        skip_polish_threshold=1000,
        max_sections=10,  # Skip premium for short docs
    )

    source_code = '''
class EmpathyOS:
    """Main entry point for the Empathy Framework."""

    def __init__(self, user_id: str, target_level: int = 4):
        """Initialize the Empathy OS.

        Args:
            user_id: Unique identifier for the user
            target_level: Target empathy level (1-5)
        """
        self.user_id = user_id
        self.target_level = target_level

    async def collaborate(self, prompt: str, context: dict = None):
        """Process a collaboration request.

        Args:
            prompt: The user's input
            context: Additional context for the interaction

        Returns:
            CollaborationResult with response and predictions
        """
        pass

    def record_success(self, success: bool):
        """Record feedback about an interaction."""
        pass
'''

    result = await workflow.execute(
        source_code=source_code,
        doc_type="api_reference",
        audience="developers",
    )

    _print_result(result, "API Reference")


async def generate_tutorial():
    """Generate a tutorial document."""
    print("\n" + "-" * 50)
    print("  SCENARIO 2: Tutorial Documentation")
    print("-" * 50 + "\n")

    workflow = DocumentGenerationWorkflow(max_sections=7)

    source_code = """
# Getting started with Empathy Framework

from empathy_os import EmpathyOS

# Initialize
os = EmpathyOS(user_id="demo_user")

# Basic interaction
result = await os.collaborate("Help me debug this code")
print(result.response)
print(result.predictions)

# Record feedback
os.record_success(True)
"""

    result = await workflow.execute(
        source_code=source_code,
        doc_type="tutorial",
        audience="beginners",
    )

    _print_result(result, "Tutorial")


async def generate_architecture_doc():
    """Generate architecture documentation."""
    print("\n" + "-" * 50)
    print("  SCENARIO 3: Architecture Documentation")
    print("-" * 50 + "\n")

    workflow = DocumentGenerationWorkflow(max_sections=6)

    source_code = """
# System Architecture Overview

## Components
- EmpathyOS: Main orchestration layer
- Memory System: Redis (short-term) + Pattern Storage (long-term)
- Model Router: 3-tier cost optimization
- Agent Factory: Multi-framework agent creation

## Data Flow
User Request → EmpathyOS → Model Router → LLM
                ↓
            Memory System
                ↓
            Response + Predictions
"""

    result = await workflow.execute(
        source_code=source_code,
        doc_type="architecture",
        audience="architects",
    )

    _print_result(result, "Architecture")


def _print_result(result, doc_name):
    """Print workflow results."""
    if result.success:
        print(f"✓ Documentation generated: {doc_name}\n")

        # Stage summary
        print("Stages:")
        for stage in result.stages:
            tier_display = stage.tier.value
            if stage.skipped:
                print(f"  {stage.name:15} [SKIPPED]")
            else:
                print(f"  {stage.name:15} [{tier_display:8}] ${stage.cost:.6f}")
        print()

        # Document info
        output = result.final_output or {}
        sections = output.get("sections", [])
        if sections:
            print(f"Generated {len(sections)} sections:")
            for section in sections[:5]:
                tokens = section.get("tokens", 0)
                print(f"  • {section.get('title', 'Untitled')} ({tokens} tokens)")
            if len(sections) > 5:
                print(f"  ... and {len(sections) - 5} more sections")
            print()

        # Improvements applied
        improvements = output.get("improvements", [])
        if improvements:
            print("Polish improvements:")
            for imp in improvements:
                print(f"  ✓ {imp}")
            print()

        # Cost summary
        report = result.cost_report
        print("Cost Analysis:")
        print(f"  Total:    ${report.total_cost:.6f}")
        print(f"  Baseline: ${report.baseline_cost:.6f}")
        print(f"  Saved:    {report.savings_percent:.1f}%")
        print()

        # Show a preview of the document
        document = output.get("document", "")
        if document:
            preview_lines = document.split("\n")[:10]
            print("Document Preview:")
            print("-" * 40)
            for line in preview_lines:
                print(f"  {line[:60]}")
            if len(document.split("\n")) > 10:
                print("  ...")
            print()

    else:
        print(f"✗ Generation failed: {result.error}")


async def main():
    """Run all documentation generation scenarios."""
    print("\n" + "=" * 60)
    print("  DOCUMENT GENERATION WORKFLOW DEMO")
    print("=" * 60)

    # Run different scenarios
    await generate_api_docs()
    await generate_tutorial()
    await generate_architecture_doc()

    print("\n" + "=" * 60)
    print("  Demo complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
