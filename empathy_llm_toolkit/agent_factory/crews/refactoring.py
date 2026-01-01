"""
Refactoring Crew

A 2-agent crew that performs interactive code refactoring analysis.
Designed for Level 4 Empathy with session memory, rollback capability,
and learning from user preferences over time.

Agents:
- RefactorAnalyzer: Identifies refactoring opportunities, prioritizes by impact
- RefactorWriter: Generates concrete code changes with before/after

Usage:
    from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew

    crew = RefactoringCrew(api_key="...")
    report = await crew.analyze(code="...", file_path="src/api.py")

    for finding in report.findings:
        print(f"  - {finding.title} ({finding.category.value})")

        # Generate the refactored code
        finding = await crew.generate_refactor(finding, code)
        print(f"    Before: {finding.before_code[:50]}...")
        print(f"    After: {finding.after_code[:50]}...")

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class RefactoringCategory(Enum):
    """Categories of refactoring opportunities."""

    EXTRACT_METHOD = "extract_method"
    EXTRACT_VARIABLE = "extract_variable"
    RENAME = "rename"
    SIMPLIFY = "simplify"
    REMOVE_DUPLICATION = "remove_duplication"
    RESTRUCTURE = "restructure"
    DEAD_CODE = "dead_code"
    TYPE_SAFETY = "type_safety"
    INLINE = "inline"
    CONSOLIDATE_CONDITIONAL = "consolidate_conditional"
    OTHER = "other"


class Severity(Enum):
    """Severity levels for refactoring findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Impact(Enum):
    """Estimated impact of applying a refactoring."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class RefactoringFinding:
    """A single refactoring opportunity identified by the analyzer."""

    id: str
    title: str
    description: str
    category: RefactoringCategory
    severity: Severity
    file_path: str
    start_line: int
    end_line: int
    before_code: str = ""
    after_code: str | None = None
    confidence: float = 1.0
    estimated_impact: Impact = Impact.MEDIUM
    rationale: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert finding to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "before_code": self.before_code,
            "after_code": self.after_code,
            "confidence": self.confidence,
            "estimated_impact": self.estimated_impact.value,
            "rationale": self.rationale,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RefactoringFinding":
        """Create finding from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", "Untitled"),
            description=data.get("description", ""),
            category=RefactoringCategory(data.get("category", "other")),
            severity=Severity(data.get("severity", "medium")),
            file_path=data.get("file_path", ""),
            start_line=data.get("start_line", 0),
            end_line=data.get("end_line", 0),
            before_code=data.get("before_code", ""),
            after_code=data.get("after_code"),
            confidence=data.get("confidence", 1.0),
            estimated_impact=Impact(data.get("estimated_impact", "medium")),
            rationale=data.get("rationale", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CodeCheckpoint:
    """Checkpoint for rollback capability."""

    id: str
    file_path: str
    original_content: str
    timestamp: str
    finding_id: str

    def to_dict(self) -> dict:
        """Convert checkpoint to dictionary."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "original_content": self.original_content,
            "timestamp": self.timestamp,
            "finding_id": self.finding_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CodeCheckpoint":
        """Create checkpoint from dictionary."""
        return cls(
            id=data["id"],
            file_path=data["file_path"],
            original_content=data["original_content"],
            timestamp=data["timestamp"],
            finding_id=data["finding_id"],
        )


@dataclass
class RefactoringReport:
    """Complete refactoring analysis report."""

    target: str
    findings: list[RefactoringFinding]
    summary: str = ""
    duration_seconds: float = 0.0
    agents_used: list[str] = field(default_factory=list)
    checkpoints: list[CodeCheckpoint] = field(default_factory=list)
    memory_graph_hits: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def high_impact_findings(self) -> list[RefactoringFinding]:
        """Get high impact findings."""
        return [f for f in self.findings if f.estimated_impact == Impact.HIGH]

    @property
    def findings_by_category(self) -> dict[str, list[RefactoringFinding]]:
        """Group findings by category."""
        result: dict[str, list[RefactoringFinding]] = {}
        for finding in self.findings:
            cat = finding.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(finding)
        return result

    @property
    def total_lines_affected(self) -> int:
        """Calculate total lines that would be affected."""
        return sum(f.end_line - f.start_line + 1 for f in self.findings)

    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            "target": self.target,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "duration_seconds": self.duration_seconds,
            "agents_used": self.agents_used,
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "memory_graph_hits": self.memory_graph_hits,
            "high_impact_count": len(self.high_impact_findings),
            "total_lines_affected": self.total_lines_affected,
            "metadata": self.metadata,
        }


@dataclass
class UserProfile:
    """User preferences learned over time."""

    user_id: str = "default"
    updated_at: str = ""
    accepted_categories: dict[str, int] = field(default_factory=dict)
    rejected_categories: dict[str, int] = field(default_factory=dict)
    preferred_complexity: str = "medium"
    history: list[dict] = field(default_factory=list)

    def get_category_score(self, category: RefactoringCategory) -> float:
        """Get score for a category based on user history (higher = more preferred)."""
        cat = category.value
        accepted = self.accepted_categories.get(cat, 0)
        rejected = self.rejected_categories.get(cat, 0)
        total = accepted + rejected
        if total == 0:
            return 0.5  # Neutral
        return accepted / total

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "updated_at": self.updated_at,
            "preferences": {
                "accepted_categories": self.accepted_categories,
                "rejected_categories": self.rejected_categories,
                "preferred_complexity": self.preferred_complexity,
            },
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create from dictionary."""
        prefs = data.get("preferences", {})
        return cls(
            user_id=data.get("user_id", "default"),
            updated_at=data.get("updated_at", ""),
            accepted_categories=prefs.get("accepted_categories", {}),
            rejected_categories=prefs.get("rejected_categories", {}),
            preferred_complexity=prefs.get("preferred_complexity", "medium"),
            history=data.get("history", []),
        )


@dataclass
class RefactoringConfig:
    """Configuration for the refactoring crew."""

    # API Configuration
    provider: str = "anthropic"
    api_key: str | None = None

    # Analysis Configuration
    depth: str = "standard"  # "quick", "standard", "thorough"
    focus_areas: list[str] = field(
        default_factory=lambda: [
            "extract_method",
            "simplify",
            "remove_duplication",
            "rename",
            "dead_code",
        ]
    )

    # Memory Graph
    memory_graph_enabled: bool = True
    memory_graph_path: str = "patterns/refactoring_memory.json"

    # User Profile
    user_profile_enabled: bool = True
    user_profile_path: str = ".empathy/refactor_profile.json"

    # Agent Tiers (cost optimization)
    analyzer_tier: str = "capable"  # GPT-4o / Claude Sonnet
    writer_tier: str = "capable"

    # Resilience
    resilience_enabled: bool = True
    timeout_seconds: float = 300.0

    # XML Prompts
    xml_prompts_enabled: bool = True
    xml_schema_version: str = "1.0"


# =============================================================================
# XML Prompt Templates
# =============================================================================

XML_PROMPT_TEMPLATES = {
    "refactor_analyzer": """<agent role="refactor_analyzer" version="{schema_version}">
  <identity>
    <role>Refactoring Analyst</role>
    <expertise>Code analysis, refactoring patterns, code smells detection</expertise>
  </identity>

  <goal>
    Analyze code to identify refactoring opportunities that improve maintainability,
    readability, and performance. Prioritize by impact and confidence.
  </goal>

  <instructions>
    <step>Analyze the code structure, complexity, and patterns</step>
    <step>Identify code smells: long methods, duplication, poor naming, dead code</step>
    <step>Detect opportunities for extraction, simplification, or restructuring</step>
    <step>Assess the impact and risk of each potential refactoring</step>
    <step>Prioritize findings by impact (high > medium > low) and confidence</step>
    <step>Provide clear rationale for each recommendation</step>
  </instructions>

  <constraints>
    <rule>Focus on actionable refactorings, not style preferences</rule>
    <rule>Consider the broader codebase context when suggesting changes</rule>
    <rule>Prioritize safety - prefer low-risk refactorings over high-risk ones</rule>
    <rule>Include exact line numbers for each finding</rule>
    <rule>Provide the before_code snippet for context</rule>
  </constraints>

  <refactoring_patterns>
    <pattern name="extract_method">Long or complex code blocks that can be extracted</pattern>
    <pattern name="extract_variable">Complex expressions that deserve a named variable</pattern>
    <pattern name="rename">Unclear or misleading names for variables, functions, or classes</pattern>
    <pattern name="simplify">Overly complex conditionals or logic that can be simplified</pattern>
    <pattern name="remove_duplication">Repeated code blocks that should be consolidated</pattern>
    <pattern name="dead_code">Unused variables, functions, or imports</pattern>
    <pattern name="inline">Over-abstracted code that should be inlined</pattern>
    <pattern name="consolidate_conditional">Multiple conditionals that can be merged</pattern>
  </refactoring_patterns>

  <output_format>
    Return a JSON array of findings, each with:
    - id: unique identifier
    - title: brief description
    - description: detailed explanation
    - category: one of the refactoring patterns
    - severity: critical/high/medium/low/info
    - file_path: path to the file
    - start_line: starting line number
    - end_line: ending line number
    - before_code: the current code snippet
    - confidence: 0.0 to 1.0
    - estimated_impact: high/medium/low
    - rationale: why this refactoring is recommended
  </output_format>
</agent>""",
    "refactor_writer": """<agent role="refactor_writer" version="{schema_version}">
  <identity>
    <role>Refactoring Engineer</role>
    <expertise>Code transformation, refactoring implementation, clean code</expertise>
  </identity>

  <goal>
    Generate the refactored code for a specific finding. Produce clean, correct,
    and idiomatic code that addresses the identified issue.
  </goal>

  <instructions>
    <step>Understand the original code and the refactoring goal</step>
    <step>Apply the appropriate refactoring pattern</step>
    <step>Ensure the refactored code is syntactically correct</step>
    <step>Maintain the original functionality - no behavior changes</step>
    <step>Follow the project's coding style and conventions</step>
    <step>Return the complete refactored code snippet</step>
  </instructions>

  <constraints>
    <rule>The refactored code MUST be syntactically valid</rule>
    <rule>Preserve all functionality - this is refactoring, not feature changes</rule>
    <rule>Match the indentation and style of surrounding code</rule>
    <rule>Include any necessary imports or helper functions</rule>
    <rule>Keep the refactoring minimal - only change what's needed</rule>
  </constraints>

  <output_format>
    Return a JSON object with:
    - after_code: the complete refactored code snippet
    - explanation: brief explanation of changes made
    - imports_needed: list of any new imports required (if any)
  </output_format>
</agent>""",
}


# =============================================================================
# RefactoringCrew Class
# =============================================================================


class RefactoringCrew:
    """
    2-agent crew for interactive code refactoring.

    The crew consists of:

    1. **RefactorAnalyzer** (Analysis Agent)
       - Analyzes code for refactoring opportunities
       - Identifies code smells and improvement areas
       - Prioritizes by impact and confidence
       - Model: Capable tier (cost-effective)

    2. **RefactorWriter** (Generation Agent)
       - Generates concrete refactored code
       - Produces before/after diffs
       - Ensures syntactic correctness
       - Model: Capable tier

    Features:
    - Checkpoint/rollback for safe refactoring
    - User profile learning for personalized recommendations
    - Memory Graph integration for cross-session learning

    Example:
        crew = RefactoringCrew(api_key="...")
        report = await crew.analyze(code="...", file_path="api.py")

        for finding in report.findings:
            # Generate refactored code on demand
            finding = await crew.generate_refactor(finding, full_code)
            print(f"After: {finding.after_code}")
    """

    def __init__(self, config: RefactoringConfig | None = None, **kwargs: Any):
        """
        Initialize the Refactoring Crew.

        Args:
            config: RefactoringConfig or pass individual params as kwargs
            **kwargs: Individual config parameters (api_key, provider, etc.)
        """
        if config:
            self.config = config
        else:
            self.config = RefactoringConfig(**kwargs)

        self._factory: Any = None
        self._agents: dict[str, Any] = {}
        self._workflow: Any = None
        self._graph: Any = None
        self._user_profile: UserProfile | None = None
        self._initialized = False

    def _render_xml_prompt(self, template_key: str) -> str:
        """Render XML prompt template with config values."""
        template = XML_PROMPT_TEMPLATES.get(template_key, "")
        return template.format(schema_version=self.config.xml_schema_version)

    def _get_system_prompt(self, agent_key: str, fallback: str) -> str:
        """Get system prompt - XML if enabled, fallback otherwise."""
        if self.config.xml_prompts_enabled:
            return self._render_xml_prompt(agent_key)
        return fallback

    async def _initialize(self) -> None:
        """Lazy initialization of agents and workflow."""
        if self._initialized:
            return

        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        # Check if CrewAI is available
        try:
            from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import _check_crewai

            use_crewai = _check_crewai()
        except ImportError:
            use_crewai = False

        # Use CrewAI if available, otherwise fall back to Native
        framework = Framework.CREWAI if use_crewai else Framework.NATIVE

        self._factory = AgentFactory(
            framework=framework,
            provider=self.config.provider,
            api_key=self.config.api_key,
        )

        # Initialize Memory Graph if enabled
        if self.config.memory_graph_enabled:
            try:
                from empathy_os.memory import MemoryGraph

                self._graph = MemoryGraph(path=self.config.memory_graph_path)
            except ImportError:
                logger.warning("Memory Graph not available, continuing without it")

        # Load user profile if enabled
        if self.config.user_profile_enabled:
            self._user_profile = self._load_user_profile()

        # Create the 2 specialized agents
        await self._create_agents()

        self._initialized = True

    async def _create_agents(self) -> None:
        """Create the 2 specialized refactoring agents."""

        # Fallback prompts
        analyzer_fallback = """You are a Refactoring Analyst.

Your job is to analyze code and identify refactoring opportunities:

1. Look for code smells:
   - Long methods (>20 lines)
   - Duplicate code blocks
   - Poor naming
   - Dead code (unused variables/functions)
   - Complex conditionals

2. For each finding, provide:
   - Title and description
   - Category (extract_method, rename, simplify, etc.)
   - Severity (critical/high/medium/low)
   - Line numbers (start_line, end_line)
   - The before_code snippet
   - Confidence score (0-1)
   - Estimated impact (high/medium/low)
   - Rationale for the recommendation

Focus on actionable, safe refactorings. Prioritize by impact."""

        writer_fallback = """You are a Refactoring Engineer.

Your job is to generate the refactored code for a specific finding.

Requirements:
1. The code MUST be syntactically valid
2. Preserve all functionality - no behavior changes
3. Match the project's coding style
4. Keep changes minimal - only change what's needed

Return the refactored code as after_code."""

        # 1. RefactorAnalyzer
        self._agents["analyzer"] = self._factory.create_agent(
            name="refactor_analyzer",
            role="analyst",
            description="Analyzes code for refactoring opportunities",
            system_prompt=self._get_system_prompt("refactor_analyzer", analyzer_fallback),
            model_tier=self.config.analyzer_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
            resilience_enabled=self.config.resilience_enabled,
        )

        # 2. RefactorWriter
        self._agents["writer"] = self._factory.create_agent(
            name="refactor_writer",
            role="engineer",
            description="Generates refactored code for specific findings",
            system_prompt=self._get_system_prompt("refactor_writer", writer_fallback),
            model_tier=self.config.writer_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
            resilience_enabled=self.config.resilience_enabled,
        )

    # =========================================================================
    # Public Methods
    # =========================================================================

    async def analyze(
        self,
        code: str,
        file_path: str,
        context: dict | None = None,
    ) -> RefactoringReport:
        """
        Analyze code for refactoring opportunities.

        Args:
            code: The source code to analyze
            file_path: Path to the file being analyzed
            context: Optional context (language, project conventions, etc.)

        Returns:
            RefactoringReport with prioritized findings
        """
        import time

        start_time = time.time()

        # Initialize if needed
        await self._initialize()

        context = context or {}
        findings: list[RefactoringFinding] = []
        memory_hits = 0

        # Query Memory Graph for similar past refactorings
        if self._graph and self.config.memory_graph_enabled:
            try:
                similar = self._graph.find_similar(
                    {"name": f"refactor:{file_path}", "description": file_path},
                    threshold=0.4,
                    limit=10,
                )
                if similar:
                    memory_hits = len(similar)
                    context["similar_refactorings"] = [
                        {
                            "name": node.name,
                            "category": node.metadata.get("category", "unknown"),
                        }
                        for node, score in similar
                    ]
                    logger.info(f"Found {memory_hits} similar past refactorings")
            except Exception as e:
                logger.warning(f"Error querying Memory Graph: {e}")

        # Build analysis task
        task = self._build_analysis_task(code, file_path, context)

        # Execute analysis
        try:
            result = await self._agents["analyzer"].invoke(task, context)
            findings = self._parse_findings(result)

            # Apply user preferences for prioritization
            if self._user_profile:
                findings = self._apply_user_preferences(findings)

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return RefactoringReport(
                target=file_path,
                findings=[],
                summary=f"Analysis failed: {e}",
                duration_seconds=time.time() - start_time,
                agents_used=["analyzer"],
                memory_graph_hits=memory_hits,
                metadata={"error": str(e)},
            )

        # Build report
        duration = time.time() - start_time
        report = RefactoringReport(
            target=file_path,
            findings=findings,
            summary=self._generate_summary(findings),
            duration_seconds=duration,
            agents_used=list(self._agents.keys()),
            memory_graph_hits=memory_hits,
            metadata={
                "depth": self.config.depth,
                "framework": str(self._factory.framework.value) if self._factory else "unknown",
            },
        )

        # Store in Memory Graph
        if self._graph and self.config.memory_graph_enabled:
            try:
                self._graph.add_finding(
                    "refactoring_crew",
                    {
                        "type": "refactoring_analysis",
                        "name": f"refactor:{file_path}",
                        "description": report.summary,
                        "findings_count": len(findings),
                    },
                )
                self._graph._save()
            except Exception as e:
                logger.warning(f"Error storing in Memory Graph: {e}")

        return report

    async def generate_refactor(
        self,
        finding: RefactoringFinding,
        full_code: str,
    ) -> RefactoringFinding:
        """
        Generate refactored code for a specific finding.

        Args:
            finding: The finding to generate refactored code for
            full_code: The complete source file content

        Returns:
            Updated finding with after_code populated
        """
        await self._initialize()

        task = self._build_refactor_task(finding, full_code)

        try:
            result = await self._agents["writer"].invoke(task)
            after_code = self._parse_refactor_result(result)
            finding.after_code = after_code
        except Exception as e:
            logger.error(f"Refactor generation failed: {e}")
            finding.metadata["generation_error"] = str(e)

        return finding

    # =========================================================================
    # Checkpoint & Rollback
    # =========================================================================

    def create_checkpoint(
        self,
        file_path: str,
        content: str,
        finding_id: str,
    ) -> CodeCheckpoint:
        """
        Create a checkpoint before applying a change.

        Args:
            file_path: Path to the file
            content: Current content of the file
            finding_id: ID of the finding being applied

        Returns:
            CodeCheckpoint that can be used for rollback
        """
        checkpoint = CodeCheckpoint(
            id=str(uuid.uuid4()),
            file_path=file_path,
            original_content=content,
            timestamp=datetime.now().isoformat(),
            finding_id=finding_id,
        )
        return checkpoint

    def rollback(self, checkpoint: CodeCheckpoint) -> str:
        """
        Get the original content from a checkpoint.

        Args:
            checkpoint: The checkpoint to rollback to

        Returns:
            The original file content
        """
        return checkpoint.original_content

    # =========================================================================
    # User Profile Management
    # =========================================================================

    def _load_user_profile(self) -> UserProfile:
        """Load user profile from disk."""
        profile_path = Path(self.config.user_profile_path)
        if profile_path.exists():
            try:
                with open(profile_path) as f:
                    data = json.load(f)
                return UserProfile.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load user profile: {e}")
        return UserProfile()

    def save_user_profile(self) -> None:
        """Save user profile to disk."""
        if not self._user_profile:
            return

        profile_path = Path(self.config.user_profile_path)
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        self._user_profile.updated_at = datetime.now().isoformat()

        try:
            with open(profile_path, "w") as f:
                json.dump(self._user_profile.to_dict(), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save user profile: {e}")

    def record_decision(self, finding: RefactoringFinding, accepted: bool) -> None:
        """
        Record user decision for learning.

        Args:
            finding: The finding that was accepted or rejected
            accepted: True if user accepted, False if rejected
        """
        if not self._user_profile:
            return

        cat = finding.category.value

        if accepted:
            self._user_profile.accepted_categories[cat] = (
                self._user_profile.accepted_categories.get(cat, 0) + 1
            )
        else:
            self._user_profile.rejected_categories[cat] = (
                self._user_profile.rejected_categories.get(cat, 0) + 1
            )

        # Add to history
        self._user_profile.history.append(
            {
                "session_id": str(uuid.uuid4())[:8],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "file": finding.file_path,
                "category": cat,
                "accepted": accepted,
            }
        )

        # Keep history bounded
        if len(self._user_profile.history) > 100:
            self._user_profile.history = self._user_profile.history[-100:]

        self.save_user_profile()

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _build_analysis_task(self, code: str, file_path: str, context: dict) -> str:
        """Build the analysis task for the analyzer agent."""
        depth_instructions = {
            "quick": "Focus on obvious issues only. Skip minor improvements.",
            "standard": "Balance thoroughness with practicality. Cover major patterns.",
            "thorough": "Deep analysis including subtle improvements and edge cases.",
        }

        focus_list = ", ".join(self.config.focus_areas)

        task = f"""Analyze the following code for refactoring opportunities.

File: {file_path}
Analysis Depth: {self.config.depth}
Instructions: {depth_instructions.get(self.config.depth, "standard")}
Focus Areas: {focus_list}

```
{code[:20000]}
```

Return a JSON array of findings. Each finding should have:
- id: unique identifier (use UUID format)
- title: brief description
- description: detailed explanation
- category: {focus_list}, or "other"
- severity: critical, high, medium, low, or info
- file_path: "{file_path}"
- start_line: starting line number
- end_line: ending line number
- before_code: the current code snippet
- confidence: 0.0 to 1.0
- estimated_impact: high, medium, or low
- rationale: why this refactoring is recommended

Prioritize by impact and confidence. Return at most 10 findings.
"""

        if context.get("similar_refactorings"):
            task += f"\n\nSimilar past refactorings found: {len(context['similar_refactorings'])}"

        return task

    def _build_refactor_task(self, finding: RefactoringFinding, full_code: str) -> str:
        """Build the refactoring task for the writer agent."""
        return f"""Generate refactored code for the following finding.

Finding: {finding.title}
Category: {finding.category.value}
Description: {finding.description}
Lines: {finding.start_line} to {finding.end_line}
Rationale: {finding.rationale}

Current code (before):
```
{finding.before_code}
```

Full file context:
```
{full_code[:15000]}
```

Return a JSON object with:
- after_code: the complete refactored code snippet (to replace before_code)
- explanation: brief explanation of changes made

The refactored code MUST be syntactically valid and preserve all functionality.
"""

    def _parse_findings(self, result: dict) -> list[RefactoringFinding]:
        """Parse findings from analyzer result."""
        findings = []

        output = result.get("output", "")
        metadata = result.get("metadata", {})

        # Try structured findings first
        if "findings" in metadata:
            for f in metadata["findings"]:
                findings.append(RefactoringFinding.from_dict(f))
            return findings

        # Try to parse JSON from output
        try:
            # Look for JSON array in output
            import re

            json_match = re.search(r"\[[\s\S]*\]", output)
            if json_match:
                data = json.loads(json_match.group())
                for f in data:
                    findings.append(RefactoringFinding.from_dict(f))
                return findings
        except json.JSONDecodeError:
            pass

        # Fallback: create a single finding from text
        if output.strip():
            findings.append(
                RefactoringFinding(
                    id=str(uuid.uuid4()),
                    title="Analysis Result",
                    description=output[:500],
                    category=RefactoringCategory.OTHER,
                    severity=Severity.INFO,
                    file_path="",
                    start_line=0,
                    end_line=0,
                    confidence=0.5,
                )
            )

        return findings

    def _parse_refactor_result(self, result: dict) -> str:
        """Parse refactored code from writer result."""
        output = result.get("output", "")
        metadata = result.get("metadata", {})

        # Check metadata first
        if "after_code" in metadata:
            return str(metadata["after_code"])

        # Try to parse JSON from output
        try:
            import re

            json_match = re.search(r"\{[\s\S]*\}", output)
            if json_match:
                data = json.loads(json_match.group())
                if "after_code" in data:
                    return str(data["after_code"])
        except json.JSONDecodeError:
            pass

        # Look for code blocks
        import re

        code_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", output)
        if code_match:
            return code_match.group(1).strip()

        # Return raw output as fallback
        return str(output).strip()

    def _apply_user_preferences(
        self, findings: list[RefactoringFinding]
    ) -> list[RefactoringFinding]:
        """Apply user preferences to prioritize findings."""
        if not self._user_profile:
            return findings

        user_profile = self._user_profile  # Capture for closure with non-None type

        def score(finding: RefactoringFinding) -> float:
            # Base score from impact
            impact_scores = {Impact.HIGH: 3.0, Impact.MEDIUM: 2.0, Impact.LOW: 1.0}
            base = impact_scores.get(finding.estimated_impact, 2.0)

            # Adjust by user preference
            pref = user_profile.get_category_score(finding.category)
            adjusted = base * (0.5 + pref)  # Range: 0.5x to 1.5x

            # Adjust by confidence
            return adjusted * finding.confidence

        return sorted(findings, key=score, reverse=True)

    def _generate_summary(self, findings: list[RefactoringFinding]) -> str:
        """Generate summary of analysis."""
        if not findings:
            return "No refactoring opportunities identified."

        by_impact = {
            Impact.HIGH: sum(1 for f in findings if f.estimated_impact == Impact.HIGH),
            Impact.MEDIUM: sum(1 for f in findings if f.estimated_impact == Impact.MEDIUM),
            Impact.LOW: sum(1 for f in findings if f.estimated_impact == Impact.LOW),
        }

        parts = [f"Found {len(findings)} refactoring opportunities:"]

        if by_impact[Impact.HIGH] > 0:
            parts.append(f"  - {by_impact[Impact.HIGH]} high impact")
        if by_impact[Impact.MEDIUM] > 0:
            parts.append(f"  - {by_impact[Impact.MEDIUM]} medium impact")
        if by_impact[Impact.LOW] > 0:
            parts.append(f"  - {by_impact[Impact.LOW]} low impact")

        # Top categories
        by_cat: dict[str, int] = {}
        for f in findings:
            cat = f.category.value
            by_cat[cat] = by_cat.get(cat, 0) + 1

        if by_cat:
            top = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)[:3]
            parts.append("\nTop categories:")
            for cat, count in top:
                parts.append(f"  - {cat}: {count}")

        return "\n".join(parts)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def agents(self) -> dict[str, Any]:
        """Get the crew's agents."""
        return self._agents

    @property
    def is_initialized(self) -> bool:
        """Check if crew is initialized."""
        return self._initialized

    @property
    def user_profile(self) -> UserProfile | None:
        """Get the current user profile."""
        return self._user_profile
