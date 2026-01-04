"""Manage_Documentation - Multi-Agent Workflow

Makes sure that new program files are fully documented and existing documents
are updated when associate program files are changed.

Pattern: Crew
- Multiple specialized AI agents collaborate on the task
- Process Type: sequential
- Agents: 4

Generated with: empathy workflow new Manage_Documentation
See: docs/guides/WORKFLOW_PATTERNS.md

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Try to import the LLM executor for actual AI calls
EmpathyLLMExecutor = None
ExecutionContext = None
HAS_EXECUTOR = False

try:
    from empathy_os.models import ExecutionContext as _ExecutionContext
    from empathy_os.models.empathy_executor import EmpathyLLMExecutor as _EmpathyLLMExecutor

    EmpathyLLMExecutor = _EmpathyLLMExecutor
    ExecutionContext = _ExecutionContext
    HAS_EXECUTOR = True
except ImportError:
    pass

# Try to import the ProjectIndex for file tracking
ProjectIndex = None
HAS_PROJECT_INDEX = False

try:
    from empathy_os.project_index import ProjectIndex as _ProjectIndex

    ProjectIndex = _ProjectIndex
    HAS_PROJECT_INDEX = True
except ImportError:
    pass


@dataclass
class ManageDocumentationCrewResult:
    """Result from ManageDocumentationCrew execution."""

    success: bool
    findings: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    files_analyzed: int = 0
    docs_needing_update: int = 0
    new_docs_needed: int = 0
    confidence: float = 0.0
    cost: float = 0.0
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "files_analyzed": self.files_analyzed,
            "docs_needing_update": self.docs_needing_update,
            "new_docs_needed": self.new_docs_needed,
            "confidence": self.confidence,
            "cost": self.cost,
            "duration_ms": self.duration_ms,
        }


@dataclass
class Agent:
    """Agent configuration for the crew."""

    role: str
    goal: str
    backstory: str
    expertise_level: str = "expert"

    def get_system_prompt(self) -> str:
        """Generate system prompt for this agent."""
        return f"""You are a {self.role} with {self.expertise_level}-level expertise.

Goal: {self.goal}

Background: {self.backstory}

Provide thorough, actionable analysis. Be specific and cite file paths when relevant."""


@dataclass
class Task:
    """Task configuration for the crew."""

    description: str
    expected_output: str
    agent: Agent

    def get_user_prompt(self, context: dict) -> str:
        """Generate user prompt for this task with context."""
        context_str = "\n".join(f"- {k}: {v}" for k, v in context.items() if v)
        return f"""{self.description}

Context:
{context_str}

Expected output format: {self.expected_output}"""


class ManageDocumentationCrew:
    """Manage_Documentation - Documentation management crew.

    Makes sure that new program files are fully documented and existing
    documents are updated when associated program files are changed.

    Process Type: sequential

    Agents:
    - Analyst: Scans codebase to identify documentation gaps
    - Reviewer: Cross-checks findings and validates accuracy
    - Synthesizer: Combines findings into actionable recommendations
    - Manager: Coordinates actions and prioritizes work

    Usage:
        crew = ManageDocumentationCrew()
        result = await crew.execute(path="./src", context={})
    """

    name = "Manage_Documentation"
    description = "Makes sure that new program files are fully documented and existing documents are updated when associated program files are changed."
    process_type = "sequential"

    def __init__(self, project_root: str = ".", **kwargs: Any):
        """Initialize the crew with configured agents."""
        self.config = kwargs
        self.project_root = project_root
        self._executor = None
        self._project_index = None
        self._total_cost = 0.0
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        # Initialize executor if available
        if HAS_EXECUTOR and EmpathyLLMExecutor is not None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                try:
                    self._executor = EmpathyLLMExecutor(
                        provider="anthropic",
                        api_key=api_key,
                    )
                except Exception:
                    pass

        # Initialize ProjectIndex if available
        if HAS_PROJECT_INDEX and ProjectIndex is not None:
            try:
                self._project_index = ProjectIndex(project_root)
                if not self._project_index.load():
                    # Index doesn't exist or is stale, refresh it
                    print("  [ProjectIndex] Building index (first run)...")
                    self._project_index.refresh()
            except Exception as e:
                print(f"  [ProjectIndex] Warning: Could not load index: {e}")

        # Define agents
        self.analyst = Agent(
            role="Documentation Analyst",
            goal="Scan the codebase to identify files lacking documentation and find stale docs",
            backstory="Expert analyst who understands code structure, docstrings, and documentation best practices. Skilled at identifying gaps between code and documentation.",
            expertise_level="expert",
        )

        self.reviewer = Agent(
            role="Documentation Reviewer",
            goal="Cross-check findings and validate accuracy of the analysis",
            backstory="Experienced technical writer and reviewer focused on quality, correctness, and ensuring documentation matches actual code behavior.",
            expertise_level="expert",
        )

        self.synthesizer = Agent(
            role="Documentation Synthesizer",
            goal="Combine findings into actionable, prioritized recommendations",
            backstory="Strategic thinker who excels at synthesis and prioritization. Creates clear action plans that developers can follow.",
            expertise_level="expert",
        )

        self.manager = Agent(
            role="Documentation Manager",
            goal="Coordinate actions of other agents and prioritize documentation work",
            backstory="Understands the documentation needs of the project and the capability of other agents. Makes decisions about what to document first based on impact and effort.",
            expertise_level="world-class",
        )

        # Store all agents
        self.agents = [self.analyst, self.reviewer, self.synthesizer, self.manager]

    def define_tasks(self) -> list[Task]:
        """Define the tasks for this crew."""
        return [
            Task(
                description="Analyze the codebase to identify: 1) Python files without docstrings, 2) Functions/classes missing documentation, 3) README files that may be outdated, 4) Missing API documentation",
                expected_output="JSON list of findings with: file_path, issue_type (missing_docstring|stale_doc|no_readme), severity (high|medium|low), details",
                agent=self.analyst,
            ),
            Task(
                description="Review and validate the analysis findings. Check if flagged files truly need documentation updates. Identify any false positives.",
                expected_output="Validated findings with confidence scores (0-1) and notes on any false positives removed",
                agent=self.reviewer,
            ),
            Task(
                description="Synthesize validated findings into a prioritized action plan. Group by module/area, estimate effort, and create clear next steps.",
                expected_output="Prioritized list of documentation tasks with: priority (1-5), task description, estimated effort (small|medium|large), files involved",
                agent=self.synthesizer,
            ),
        ]

    async def _call_llm(
        self,
        agent: Agent,
        task: Task,
        context: dict,
        task_type: str = "code_analysis",
    ) -> tuple[str, int, int, float]:
        """Call the LLM with agent/task configuration.

        Returns: (response_text, input_tokens, output_tokens, cost)
        """
        system_prompt = agent.get_system_prompt()
        user_prompt = task.get_user_prompt(context)

        if self._executor is not None and ExecutionContext is not None:
            try:
                exec_context = ExecutionContext(
                    workflow_name=self.name,
                    step_name=agent.role.lower().replace(" ", "_"),
                    task_type=task_type,
                )

                response = await self._executor.run(
                    task_type=task_type,
                    prompt=user_prompt,
                    system=system_prompt,
                    context=exec_context,
                )

                return (
                    response.content,
                    response.tokens_input,
                    response.tokens_output,
                    response.cost_estimate or 0.0,
                )
            except Exception as e:
                # Fallback to mock response on error
                return self._mock_response(agent, task, context, str(e))
        else:
            # No executor available - return mock response
            return self._mock_response(agent, task, context, "No LLM executor configured")

    def _mock_response(
        self,
        agent: Agent,
        task: Task,
        context: dict,
        reason: str,
    ) -> tuple[str, int, int, float]:
        """Generate a mock response when LLM is not available."""
        mock_findings = {
            "Documentation Analyst": f"""[Mock Analysis - {reason}]

Based on scanning the path: {context.get("path", ".")}

Findings:
1. {{
   "file_path": "src/example.py",
   "issue_type": "missing_docstring",
   "severity": "medium",
   "details": "Module lacks module-level docstring"
}}
2. {{
   "file_path": "README.md",
   "issue_type": "stale_doc",
   "severity": "low",
   "details": "README may not reflect recent changes"
}}

Note: This is a mock response. Configure ANTHROPIC_API_KEY for real analysis.""",
            "Documentation Reviewer": f"""[Mock Review - {reason}]

Validated Findings:
- Finding 1: VALID (confidence: 0.8) - Missing docstrings are a real issue
- Finding 2: NEEDS_VERIFICATION (confidence: 0.5) - Stale docs need manual check

False Positives Removed: 0

Note: This is a mock response. Configure ANTHROPIC_API_KEY for real analysis.""",
            "Documentation Synthesizer": f"""[Mock Synthesis - {reason}]

Prioritized Action Plan:

1. Priority 1 (High) - Add module docstrings
   - Effort: small
   - Files: src/example.py

2. Priority 3 (Medium) - Review README accuracy
   - Effort: medium
   - Files: README.md

Note: This is a mock response. Configure ANTHROPIC_API_KEY for real analysis.""",
        }

        response = mock_findings.get(agent.role, f"Mock response for {agent.role}")
        return (response, 0, 0, 0.0)

    def _scan_directory(self, path: str) -> dict:
        """Scan directory for Python files and documentation."""
        path_obj = Path(path)
        if not path_obj.exists():
            return {"error": f"Path does not exist: {path}"}

        python_files = []
        doc_files = []

        # Find Python files
        for py_file in path_obj.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                python_files.append(str(py_file))

        # Find documentation files
        for pattern in ["*.md", "*.rst", "*.txt"]:
            for doc_file in path_obj.rglob(pattern):
                doc_files.append(str(doc_file))

        return {
            "python_files": python_files[:50],  # Limit for context
            "python_file_count": len(python_files),
            "doc_files": doc_files[:20],
            "doc_file_count": len(doc_files),
        }

    def _get_index_context(self) -> dict[str, Any]:
        """Get documentation context from ProjectIndex if available."""
        if self._project_index is None:
            return {}

        try:
            return self._project_index.get_context_for_workflow("documentation")
        except Exception as e:
            print(f"  [ProjectIndex] Warning: Could not get context: {e}")
            return {}

    async def execute(
        self,
        path: str = ".",
        context: dict | None = None,
        **kwargs: Any,
    ) -> ManageDocumentationCrewResult:
        """Execute the documentation management crew.

        Args:
            path: Path to analyze for documentation gaps
            context: Additional context for agents
            **kwargs: Additional arguments

        Returns:
            ManageDocumentationCrewResult with findings and recommendations

        """
        started_at = datetime.now()
        context = context or {}

        # Try to get rich context from ProjectIndex
        index_context = self._get_index_context()

        if index_context:
            print("  [ProjectIndex] Using indexed file data")
            doc_stats = index_context.get("documentation_stats", {})

            # Build context from index
            agent_context = {
                "path": path,
                "python_files": f"{doc_stats.get('total_python_files', 0)} Python files indexed",
                "files_with_docstrings": f"{doc_stats.get('files_with_docstrings', 0)} files ({doc_stats.get('docstring_coverage_pct', 0):.1f}% coverage)",
                "files_without_docstrings": f"{doc_stats.get('files_without_docstrings', 0)} files need docstrings",
                "type_hint_coverage": f"{doc_stats.get('type_hint_coverage_pct', 0):.1f}%",
                "high_impact_undocumented": doc_stats.get("priority_files", []),
                "doc_files": f"{doc_stats.get('doc_file_count', 0)} documentation files",
                "total_loc_undocumented": doc_stats.get("loc_undocumented", 0),
                # New: modification tracking
                "recently_modified_source_count": doc_stats.get(
                    "recently_modified_source_count",
                    0,
                ),
                "stale_docs_count": doc_stats.get("stale_docs_count", 0),
                **context,
            }

            # Add sample of files needing docs
            files_without_docs = index_context.get("files_without_docstrings", [])
            if files_without_docs:
                agent_context["sample_undocumented"] = [f["path"] for f in files_without_docs[:10]]

            # Add recently modified source files (last 7 days)
            recent_source = index_context.get("recently_modified_source", [])
            if recent_source:
                agent_context["recently_modified_source_files"] = [
                    {"path": f["path"], "modified": f.get("last_modified")}
                    for f in recent_source[:10]
                ]

            # Add docs that may need review (source changed after doc)
            docs_needing_review = index_context.get("docs_needing_review", [])
            if docs_needing_review:
                stale_docs = [d for d in docs_needing_review if d.get("source_modified_after_doc")]
                agent_context["stale_docs"] = [
                    {
                        "doc": d["doc_file"],
                        "related_source": d["related_source_files"][:3],
                        "days_since_update": d["days_since_doc_update"],
                    }
                    for d in stale_docs[:5]
                ]

            scan_results = {
                "python_file_count": doc_stats.get("total_python_files", 0),
                "doc_file_count": doc_stats.get("doc_file_count", 0),
                "python_files": [f["path"] for f in files_without_docs[:50]],
                "doc_files": [f["path"] for f in index_context.get("doc_files", [])[:20]],
                "recently_modified_count": doc_stats.get("recently_modified_source_count", 0),
                "stale_docs_count": doc_stats.get("stale_docs_count", 0),
            }
        else:
            # Fallback to directory scanning
            print("  [Fallback] Scanning directory manually")
            scan_results = self._scan_directory(path)
            if "error" in scan_results:
                return ManageDocumentationCrewResult(
                    success=False,
                    findings=[{"error": scan_results["error"]}],
                    recommendations=["Fix the path and try again"],
                )

            # Build context for agents
            agent_context = {
                "path": path,
                "python_files": f"{scan_results['python_file_count']} files found",
                "sample_files": ", ".join(scan_results["python_files"][:10]),
                "doc_files": f"{scan_results['doc_file_count']} doc files found",
                **context,
            }

        # Get tasks
        tasks = self.define_tasks()

        # Execute tasks sequentially (crew pattern)
        all_findings: list[dict] = []
        all_responses: list[str] = []

        for i, task in enumerate(tasks):
            print(f"  [{i + 1}/{len(tasks)}] {task.agent.role}: {task.description[:50]}...")

            # Add previous task output to context
            if all_responses:
                agent_context["previous_analysis"] = all_responses[-1][:2000]

            # Determine task type for routing
            task_type = "code_analysis"
            if "review" in task.agent.role.lower():
                task_type = "code_analysis"  # Could be "review" if defined
            elif "synth" in task.agent.role.lower():
                task_type = "summarize"

            # Call LLM
            response, in_tokens, out_tokens, cost = await self._call_llm(
                agent=task.agent,
                task=task,
                context=agent_context,
                task_type=task_type,
            )

            # Track metrics
            self._total_input_tokens += in_tokens
            self._total_output_tokens += out_tokens
            self._total_cost += cost

            all_responses.append(response)
            all_findings.append(
                {
                    "agent": task.agent.role,
                    "task": task.description[:100],
                    "response": response[:1000],  # Truncate for result
                    "tokens": {"input": in_tokens, "output": out_tokens},
                    "cost": cost,
                },
            )

        # Manager coordination (final synthesis)
        manager_context = {
            "path": path,
            "analyst_findings": all_responses[0][:1500] if len(all_responses) > 0 else "",
            "reviewer_validation": all_responses[1][:1500] if len(all_responses) > 1 else "",
            "synthesizer_plan": all_responses[2][:1500] if len(all_responses) > 2 else "",
        }

        print(f"  [Final] {self.manager.role}: Coordinating final output...")

        manager_task = Task(
            description="Review all agent outputs and create a final executive summary with the top 3-5 prioritized actions for improving documentation.",
            expected_output="Executive summary with: 1) Overall documentation health score (0-100), 2) Top priorities, 3) Quick wins, 4) Estimated total effort",
            agent=self.manager,
        )

        final_response, in_tokens, out_tokens, cost = await self._call_llm(
            agent=self.manager,
            task=manager_task,
            context=manager_context,
            task_type="summarize",
        )

        self._total_input_tokens += in_tokens
        self._total_output_tokens += out_tokens
        self._total_cost += cost

        # Calculate duration
        duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)

        # Build recommendations from final response
        recommendations = [
            f"Documentation analysis complete for {path}",
            f"Analyzed {scan_results['python_file_count']} Python files",
            f"Found {scan_results['doc_file_count']} documentation files",
        ]

        # Add synthesized recommendations if available
        if len(all_responses) > 2:
            recommendations.append("See synthesizer output for prioritized action plan")

        return ManageDocumentationCrewResult(
            success=True,
            findings=all_findings,
            recommendations=recommendations,
            files_analyzed=scan_results["python_file_count"],
            docs_needing_update=0,  # Would be parsed from actual LLM response
            new_docs_needed=0,  # Would be parsed from actual LLM response
            confidence=0.75 if self._executor else 0.3,
            cost=self._total_cost,
            duration_ms=duration_ms,
        )


# CLI entry point for testing
if __name__ == "__main__":
    import sys

    async def main():
        path = sys.argv[1] if len(sys.argv) > 1 else "."
        print(f"ManageDocumentationCrew - Analyzing: {path}\n")

        crew = ManageDocumentationCrew()
        print(f"Crew: {crew.name}")
        print(f"Agents: {len(crew.agents)}")
        print(f"LLM Executor: {'Available' if crew._executor else 'Not configured (using mocks)'}")
        print()

        result = await crew.execute(path=path)

        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Success: {result.success}")
        print(f"Files Analyzed: {result.files_analyzed}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Cost: ${result.cost:.4f}")
        print(f"Confidence: {result.confidence:.0%}")
        print()
        print("Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")
        print()
        print("Agent Outputs:")
        for finding in result.findings:
            print(f"\n[{finding['agent']}]")
            print(finding["response"][:500])

    asyncio.run(main())
