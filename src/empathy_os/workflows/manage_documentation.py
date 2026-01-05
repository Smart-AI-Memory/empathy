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
    formatted_report: str = ""

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
            "formatted_report": self.formatted_report,
        }


@dataclass
class Agent:
    """Agent configuration for the crew with XML-enhanced prompting."""

    role: str
    goal: str
    backstory: str
    expertise_level: str = "expert"
    use_xml_structure: bool = True  # Enable XML-enhanced prompting by default

    def get_system_prompt(self) -> str:
        """Generate XML-enhanced system prompt for this agent."""
        if not self.use_xml_structure:
            # Legacy format for backward compatibility
            return f"""You are a {self.role} with {self.expertise_level}-level expertise.

Goal: {self.goal}

Background: {self.backstory}

Provide thorough, actionable analysis. Be specific and cite file paths when relevant."""

        # XML-enhanced format (Anthropic best practice)
        return f"""<agent_role>
You are a {self.role} with {self.expertise_level}-level expertise.
</agent_role>

<agent_goal>
{self.goal}
</agent_goal>

<agent_backstory>
{self.backstory}
</agent_backstory>

<instructions>
1. Carefully review all provided context data
2. Think through your analysis step-by-step
3. Provide thorough, actionable analysis
4. Be specific and cite file paths when relevant
5. Structure your output according to the requested format
</instructions>

<output_structure>
Always structure your response as:

<thinking>
[Your step-by-step reasoning process]
- What you observe in the context
- How you analyze the situation
- What conclusions you draw
</thinking>

<answer>
[Your final output in the requested format]
</answer>
</output_structure>"""


@dataclass
class Task:
    """Task configuration for the crew with XML-enhanced prompting."""

    description: str
    expected_output: str
    agent: Agent

    def get_user_prompt(self, context: dict) -> str:
        """Generate XML-enhanced user prompt for this task with context."""
        if not self.agent.use_xml_structure:
            # Legacy format for backward compatibility
            context_str = "\n".join(f"- {k}: {v}" for k, v in context.items() if v)
            return f"""{self.description}

Context:
{context_str}

Expected output format: {self.expected_output}"""

        # XML-enhanced format (Anthropic best practice)
        # Build structured context with proper XML tags
        context_sections = []
        for key, value in context.items():
            if value:
                # Use underscores for tag names
                tag_name = key.replace(" ", "_").replace("-", "_").lower()
                # Wrap in appropriate tags
                context_sections.append(f"<{tag_name}>\n{value}\n</{tag_name}>")

        context_xml = "\n".join(context_sections)

        return f"""<task_description>
{self.description}
</task_description>

<context>
{context_xml}
</context>

<expected_output>
{self.expected_output}
</expected_output>

<instructions>
1. Review all context data in the <context> tags above
2. Structure your response using <thinking> and <answer> tags as defined in your system prompt
3. Match the expected output format exactly
4. Be thorough and specific in your analysis
</instructions>"""


def parse_xml_response(response: str) -> dict:
    """Parse XML-structured agent response.

    Args:
        response: Raw agent response potentially containing XML tags

    Returns:
        Dictionary with 'thinking', 'answer', and 'raw' keys
    """
    import re

    thinking_match = re.search(r"<thinking>(.*?)</thinking>", response, re.DOTALL)
    answer_match = re.search(r"<answer>(.*?)</answer>", response, re.DOTALL)

    return {
        "thinking": thinking_match.group(1).strip() if thinking_match else "",
        "answer": answer_match.group(1).strip() if answer_match else response.strip(),
        "raw": response,
        "has_structure": bool(thinking_match and answer_match),
    }


def format_manage_docs_report(result: ManageDocumentationCrewResult, path: str) -> str:
    """Format documentation management output as a human-readable report.

    Args:
        result: The ManageDocumentationCrewResult
        path: The path that was analyzed

    Returns:
        Formatted report string
    """
    lines = []

    # Header with confidence
    confidence = result.confidence
    if confidence >= 0.8:
        confidence_icon = "🟢"
        confidence_text = "HIGH CONFIDENCE"
    elif confidence >= 0.5:
        confidence_icon = "🟡"
        confidence_text = "MODERATE CONFIDENCE"
    else:
        confidence_icon = "🔴"
        confidence_text = "LOW CONFIDENCE (Mock Mode)"

    lines.append("=" * 60)
    lines.append("DOCUMENTATION SYNC REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Path Analyzed: {path}")
    lines.append(f"Confidence: {confidence_icon} {confidence_text} ({confidence:.0%})")
    lines.append("")

    # Summary
    lines.append("-" * 60)
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Files Analyzed: {result.files_analyzed}")
    lines.append(f"Docs Needing Update: {result.docs_needing_update}")
    lines.append(f"New Docs Needed: {result.new_docs_needed}")
    lines.append(f"Duration: {result.duration_ms}ms ({result.duration_ms / 1000:.1f}s)")
    lines.append(f"Cost: ${result.cost:.4f}")
    lines.append("")

    # Agent Findings
    if result.findings:
        lines.append("-" * 60)
        lines.append("AGENT FINDINGS")
        lines.append("-" * 60)
        for i, finding in enumerate(result.findings, 1):
            agent = finding.get("agent", f"Agent {i}")
            response = finding.get("response", "")
            thinking = finding.get("thinking", "")
            answer = finding.get("answer", "")
            has_xml = finding.get("has_xml_structure", False)
            cost = finding.get("cost", 0.0)

            lines.append(
                f"\n{i}. {agent} (Cost: ${cost:.4f}) {'🔬 XML-Structured' if has_xml else ''}"
            )
            lines.append("   " + "-" * 54)

            # Show thinking and answer separately if available
            if has_xml and thinking:
                lines.append("   💭 Thinking:")
                if len(thinking) > 300:
                    lines.append(f"   {thinking[:300]}...")
                else:
                    lines.append(f"   {thinking}")
                lines.append("")
                lines.append("   ✅ Answer:")
                if len(answer) > 300:
                    lines.append(f"   {answer[:300]}...")
                else:
                    lines.append(f"   {answer}")
            else:
                # Fallback to original response
                if len(response) > 500:
                    lines.append(f"   {response[:500]}...")
                    lines.append(f"   [Truncated - {len(response)} chars total]")
                else:
                    lines.append(f"   {response}")
            lines.append("")

    # Recommendations
    if result.recommendations:
        lines.append("-" * 60)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 60)
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    # Next Steps
    lines.append("-" * 60)
    lines.append("NEXT STEPS")
    lines.append("-" * 60)
    lines.append("1. Review agent findings above for specific files")
    lines.append("2. Prioritize documentation updates based on impact")
    lines.append("3. Use 'Generate Docs' workflow for auto-generation")
    lines.append("4. Run this workflow periodically to keep docs in sync")
    lines.append("")

    # Footer
    lines.append("=" * 60)
    if result.success:
        lines.append("✅ Documentation sync analysis complete")
    else:
        lines.append("❌ Documentation sync analysis failed")
    lines.append("=" * 60)

    return "\n".join(lines)


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

            # Parse XML-structured response if available
            parsed = parse_xml_response(response)

            # Store full response for next agent's context
            all_responses.append(response)

            # Store findings with parsed structure
            all_findings.append(
                {
                    "agent": task.agent.role,
                    "task": task.description[:100],
                    "response": response[:1000],  # Truncate for result
                    "thinking": parsed["thinking"][:500] if parsed["thinking"] else "",
                    "answer": parsed["answer"][:500] if parsed["answer"] else response[:500],
                    "has_xml_structure": parsed["has_structure"],
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

        # Create result
        result = ManageDocumentationCrewResult(
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

        # Generate formatted report
        result.formatted_report = format_manage_docs_report(result, path)

        return result


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

        # Print formatted report
        print("\n" + result.formatted_report)

    asyncio.run(main())
