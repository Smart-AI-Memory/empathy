#!/usr/bin/env python3
"""
Research Synthesis Workflow Example

Demonstrates cost-optimized multi-source research using the 3-tier model system:
1. Haiku (cheap): Summarize each source document
2. Sonnet (capable): Identify patterns across summaries
3. Opus (premium): Synthesize final insights (conditional on complexity)

Run:
    python examples/workflows/research_example.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio

from empathy_os.workflows import ResearchSynthesisWorkflow


async def main():
    """Run research synthesis workflow demonstration."""
    print("\n" + "=" * 60)
    print("  RESEARCH SYNTHESIS WORKFLOW DEMO")
    print("=" * 60 + "\n")

    # Example research sources
    sources = [
        "research_paper_1.pdf",
        "research_paper_2.pdf",
        "industry_report.md",
        "expert_interview.txt",
        "blog_analysis.md",
    ]

    # Create workflow with custom complexity threshold
    # Premium synthesis only used if complexity > 70%
    workflow = ResearchSynthesisWorkflow(complexity_threshold=0.7)

    print("Workflow Description:")
    print("-" * 40)
    print(workflow.describe())
    print()

    # Execute the workflow
    print("Executing workflow...")
    print("-" * 40)

    result = await workflow.execute(
        sources=sources, question="What are the emerging trends in AI safety and alignment?"
    )

    # Display results
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60 + "\n")

    if result.success:
        print("✓ Workflow completed successfully\n")

        # Show stage execution
        print("Stage Execution:")
        print("-" * 40)
        for stage in result.stages:
            status = "SKIPPED" if stage.skipped else stage.tier.value
            cost = f"${stage.cost:.6f}" if not stage.skipped else "-"
            time = f"{stage.duration_ms}ms" if not stage.skipped else "-"
            print(f"  {stage.name:15} [{status:8}] {cost:12} {time}")
            if stage.skipped:
                print(f"    Reason: {stage.skip_reason}")
        print()

        # Show cost report
        print("Cost Analysis:")
        print("-" * 40)
        report = result.cost_report
        print(f"  Total Cost:      ${report.total_cost:.6f}")
        print(f"  Baseline Cost:   ${report.baseline_cost:.6f} (if all premium)")
        print(f"  Savings:         ${report.savings:.6f}")
        print(f"  Savings %:       {report.savings_percent:.1f}%")
        print()

        # Show breakdown by tier
        if report.by_tier:
            print("Cost by Tier:")
            for tier, cost in report.by_tier.items():
                print(f"    {tier:10} ${cost:.6f}")
            print()

        # Show final output
        print("Final Output:")
        print("-" * 40)
        output = result.final_output
        if output:
            print(f"  Answer: {output.get('answer', 'N/A')}")
            print(f"  Confidence: {output.get('confidence', 0):.0%}")
            print(f"  Model Tier Used: {output.get('model_tier_used', 'N/A')}")
            print(f"  Complexity Score: {output.get('complexity_score', 0):.2f}")
            print("\n  Key Insights:")
            for i, insight in enumerate(output.get("key_insights", [])[:5], 1):
                print(f"    {i}. {insight}")

    else:
        print(f"✗ Workflow failed: {result.error}")

    print("\n" + "=" * 60)
    print(f"  Total Duration: {result.total_duration_ms}ms")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
