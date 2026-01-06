#!/usr/bin/env python3
"""Generate XML Enhancement Implementation Specification

Uses our own XMLAgent/XMLTask to generate a detailed specification
for implementing all 6 XML enhancement options.

This is a meta-application of XML-enhanced prompting - using the system
to design itself!
"""

import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from empathy_os.workflows.xml_enhanced_crew import XMLAgent, XMLTask, parse_xml_response


def main():
    """Generate the implementation specification using Claude API."""

    # Create the Technical Architect agent
    agent = XMLAgent(
        role="Senior Technical Architect",
        goal="Design comprehensive implementation plan for XML enhancement options 1-6",
        backstory=(
            "Expert in software architecture, AI systems, and prompt engineering. "
            "Experienced in Python, multi-agent systems, and large-scale refactoring. "
            "Deep knowledge of Anthropic's XML prompting best practices and CrewAI framework. "
            "Skilled at breaking down complex projects into actionable implementation plans."
        ),
        expertise_level="world-class",
        custom_instructions=[
            "Consider backward compatibility at every step",
            "Prioritize maintainability and testability",
            "Provide specific file paths and code examples",
            "Identify risks and mitigation strategies",
            "Estimate effort for each component",
        ],
    )

    # Create the specification task
    task = XMLTask(
        description=(
            "Generate a detailed technical specification and implementation plan for "
            "all 6 XML enhancement options, including file-by-file changes, test strategy, "
            "and phased rollout plan."
        ),
        expected_output=(
            "A comprehensive markdown document with:\n"
            "1. Executive summary\n"
            "2. Technical architecture for each option (1-6)\n"
            "3. File-by-file implementation plan\n"
            "4. Class/function signatures for new components\n"
            "5. Migration strategy for existing workflows\n"
            "6. Test strategy and coverage targets\n"
            "7. Risk assessment and mitigation\n"
            "8. Phased rollout plan\n"
            "9. Success metrics and validation criteria"
        ),
        agent=agent,
        examples=[
            {
                "input": "Design a new feature",
                "output": (
                    "## Technical Architecture\n"
                    "### Component Design\n"
                    "- Class: `FeatureName`\n"
                    "- Methods: `execute()`, `validate()`\n"
                    "### Files to Create\n"
                    "- `src/module/feature.py`\n"
                    "### Files to Modify\n"
                    "- `src/module/__init__.py` (add import)\n"
                    "### Tests\n"
                    "- `tests/test_feature.py` (unit tests)\n"
                    "### Risks\n"
                    "- Performance impact → Mitigation: Add caching"
                ),
            }
        ],
    )

    # Prepare context with user requirements
    context = {
        "user_requirements": json.dumps(
            {
                "implementation_approach": "All 6 options in parallel",
                "timeline": "Today (4-6 hours)",
                "migration_strategy": "Migrate all workflows, use_xml_structure=True by default, allow opt-out",
                "workflow_priority": "All equally important",
                "metrics_storage": ".empathy/prompt_metrics.json (local file)",
                "metrics_tracked": ["token_usage", "retry_rates", "parsing_success"],
                "optimization_level": "Balance readability and efficiency (moderate compression)",
                "task_complexity_scoring": "Simple heuristic (token count, LOC)",
                "languages": ["Spanish", "French", "German"],
                "i18n_approach": "User preference setting, default English tags with translated content",
            },
            indent=2,
        ),
        "options_to_implement": """
Option 1: Comprehensive Workflow Migration
- Migrate all LLM-using workflows to xml_enhanced_crew.py
- Target: code_review.py, bug_predict.py, test_gen.py, refactor_plan.py,
  security_audit.py, document_gen.py, research_synthesis.py, perf_audit.py,
  pr_review.py, release_prep.py
- Method: Replace ad-hoc prompts with XMLAgent/XMLTask

Option 2: XML Schema Validation
- Add XSD schemas for response validation
- Schemas: agent_response.xsd, thinking_answer.xsd
- Add validation to parse_xml_response()
- Graceful fallback on validation errors

Option 3: Prompt Performance Tracking
- Add PromptMetrics dataclass
- Log to .empathy/prompt_metrics.json
- Dashboard integration
- A/B testing framework

Option 4: Context Window Optimization
- Implement configurable short-form XML tags
- Whitespace compression
- System prompt caching

Option 5: Dynamic Prompt Adaptation
- AdaptiveXMLAgent class
- Task complexity scoring (token count, LOC heuristic)
- Model tier mapping (cheap/capable/premium)
- Auto-select prompt verbosity

Option 6: Multi-Language XML Templates
- Support Spanish, French, German
- Locale-aware tag names (optional)
- MultilingualXMLAgent class
- Translation dictionaries (English tags, translated content by default)
        """,
        "current_codebase_state": """
- xml_enhanced_crew.py: Already created with XMLAgent, XMLTask, parse_xml_response()
- manage_documentation.py: Already migrated to XML-enhanced prompting (Phase 1)
- Other workflows: Use various prompting approaches (ad-hoc, CrewAI native, etc.)
- Testing: pytest with 5,941 passing tests, coverage target 64%
- Empathy Framework v3.6.0 - production ready
        """,
        "architecture_constraints": """
- Must maintain backward compatibility
- Feature flags for gradual rollout
- Tests alongside implementation (hybrid TDD)
- Documentation updated during implementation
- Python 3.10+ type hints required
- Follow existing code patterns and style
        """,
        "phased_approach": """
Phase 1: Core Infrastructure (60-90 min)
- PromptMetrics and tracking system
- AdaptiveXMLAgent class
- Configuration with feature flags

Phase 2: Sample Workflow Migration (45-60 min)
- Migrate 3 workflows to prove pattern
- Write tests

Phase 3: Advanced Features (60-90 min)
- XML validation
- Context optimization
- Multi-language support

Phase 4: Complete Migration (45-60 min)
- Migrate remaining workflows
- Comprehensive testing
- Documentation
        """,
    }

    # Generate prompts
    system_prompt = agent.get_system_prompt()
    user_prompt = task.get_user_prompt(context)

    print("=" * 80)
    print("GENERATING XML ENHANCEMENT SPECIFICATION")
    print("=" * 80)
    print()
    print("Using XMLAgent/XMLTask to generate detailed implementation plan...")
    print()

    # Call Claude API
    try:
        import anthropic

        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")  # pragma: allowlist secret
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY not found in environment")
            print(
                "Please set it with: export ANTHROPIC_API_KEY='your-key-here'"  # pragma: allowlist secret
            )
            return 1

        client = anthropic.Anthropic(api_key=api_key)

        print("Calling Claude API (claude-sonnet-4-5-20250929)...")
        print()

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,
            temperature=0,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )

        # Extract response text
        response_text = response.content[0].text

        # Parse XML response
        parsed = parse_xml_response(response_text)

        # Save full response
        with open("XML_ENHANCEMENT_SPEC_RAW.md", "w") as f:
            f.write("# XML Enhancement Specification - Raw Response\n\n")
            f.write(response_text)

        print("✅ Response received!")
        print()
        print(f"Has XML structure: {parsed['has_structure']}")
        print(f"Thinking length: {len(parsed['thinking'])} chars")
        print(f"Answer length: {len(parsed['answer'])} chars")
        print()

        # Save parsed response
        spec_content = f"""# XML Enhancement Implementation Specification

**Generated by:** XMLAgent (Senior Technical Architect)
**Date:** 2026-01-05
**Model:** claude-sonnet-4-5-20250929
**Method:** Meta-application of XML-enhanced prompting

---

## Agent Thinking Process

<details>
<summary>View Agent's Reasoning (Click to expand)</summary>

{parsed["thinking"]}

</details>

---

## Implementation Specification

{parsed["answer"]}

---

## Metadata

- **Input tokens:** {response.usage.input_tokens}
- **Output tokens:** {response.usage.output_tokens}
- **Total tokens:** {response.usage.input_tokens + response.usage.output_tokens}
- **Cost estimate:** ${(response.usage.input_tokens * 0.003 / 1000) + (response.usage.output_tokens * 0.015 / 1000):.4f}
- **Has XML structure:** {parsed["has_structure"]}
"""

        with open("XML_ENHANCEMENT_SPEC.md", "w") as f:
            f.write(spec_content)

        print("✅ Specification saved to XML_ENHANCEMENT_SPEC.md")
        print("✅ Raw response saved to XML_ENHANCEMENT_SPEC_RAW.md")
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Input tokens:  {response.usage.input_tokens:,}")
        print(f"Output tokens: {response.usage.output_tokens:,}")
        print(
            f"Total cost:    ${(response.usage.input_tokens * 0.003 / 1000) + (response.usage.output_tokens * 0.015 / 1000):.4f}"
        )
        print()

        if parsed["has_structure"]:
            print("✅ Agent used proper <thinking> and <answer> structure!")
            print()
            print("Next step: Review XML_ENHANCEMENT_SPEC.md and proceed with implementation")
        else:
            print("⚠️  Response did not use XML structure (unexpected)")
            print()
            print("Next step: Review XML_ENHANCEMENT_SPEC_RAW.md and adapt approach")

        return 0

    except ImportError:
        print("ERROR: anthropic package not installed")
        print("Install with: pip install anthropic")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
