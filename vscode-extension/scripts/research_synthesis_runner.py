#!/usr/bin/env python
"""Research Synthesis Runner for VSCode Extension

Simple CLI wrapper to run ResearchSynthesisWorkflow from the VSCode panel.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


async def run_synthesis(sources: list[str], question: str) -> dict:
    """Run the research synthesis workflow."""
    from empathy_os.workflows.research_synthesis import ResearchSynthesisWorkflow

    workflow = ResearchSynthesisWorkflow()

    try:
        result = await workflow.execute(sources=sources, question=question)

        return {
            "success": True,
            "answer": (
                result.final_output.get("answer", "")
                if isinstance(result.final_output, dict)
                else str(result.final_output)
            ),
            "key_insights": (
                result.final_output.get("key_insights", [])
                if isinstance(result.final_output, dict)
                else []
            ),
            "confidence": (
                result.final_output.get("confidence", 0.0)
                if isinstance(result.final_output, dict)
                else 0.0
            ),
            "model_tier_used": (
                result.final_output.get("model_tier_used", "unknown")
                if isinstance(result.final_output, dict)
                else "unknown"
            ),
            "complexity_score": (
                result.final_output.get("complexity_score", 0.0)
                if isinstance(result.final_output, dict)
                else 0.0
            ),
            "source_count": len(sources),
            "cost": result.cost_report.total_cost if result.cost_report else 0.0,
            "savings_percent": result.cost_report.savings_percent if result.cost_report else 0.0,
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "validation",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "runtime",
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No input data provided"}))
        sys.exit(1)

    try:
        input_data = json.loads(sys.argv[1])
        sources = input_data.get("sources", [])
        question = input_data.get("question", "")

        result = asyncio.run(run_synthesis(sources, question))
        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
