"""
Code Review Crew

A multi-agent crew that performs comprehensive code reviews.
Demonstrates CrewAI's hierarchical collaboration patterns with:
- 5 specialized agents with distinct roles
- Hierarchical task delegation from Review Lead
- Memory Graph integration for cross-review learning
- Structured output with verdict and recommendations

Usage:
    from empathy_llm_toolkit.agent_factory.crews import CodeReviewCrew

    crew = CodeReviewCrew(api_key="...")
    report = await crew.review(diff="...", files_changed=["src/api.py"])

    print(f"Verdict: {report.verdict}")
    for finding in report.critical_findings:
        print(f"  - {finding.title}: {finding.suggestion}")

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Review finding severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(Enum):
    """Code review finding categories."""

    SECURITY = "security"
    ARCHITECTURE = "architecture"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    STYLE = "style"
    BUG = "bug"
    OTHER = "other"


class Verdict(Enum):
    """Code review verdict."""

    APPROVE = "approve"
    APPROVE_WITH_SUGGESTIONS = "approve_with_suggestions"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"


@dataclass
class ReviewFinding:
    """A single finding from the code review."""

    title: str
    description: str
    severity: Severity
    category: FindingCategory
    file_path: str | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    suggestion: str | None = None
    before_code: str | None = None
    after_code: str | None = None
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert finding to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
            "before_code": self.before_code,
            "after_code": self.after_code,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class CodeReviewReport:
    """Complete code review report."""

    target: str
    findings: list[ReviewFinding]
    verdict: Verdict
    summary: str = ""
    review_duration_seconds: float = 0.0
    agents_used: list[str] = field(default_factory=list)
    memory_graph_hits: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def critical_findings(self) -> list[ReviewFinding]:
        """Get critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    @property
    def high_findings(self) -> list[ReviewFinding]:
        """Get high severity findings."""
        return [f for f in self.findings if f.severity == Severity.HIGH]

    @property
    def findings_by_category(self) -> dict[str, list[ReviewFinding]]:
        """Group findings by category."""
        result: dict[str, list[ReviewFinding]] = {}
        for finding in self.findings:
            cat = finding.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(finding)
        return result

    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100, higher is better)."""
        if not self.findings:
            return 100.0

        # Start with 100 and deduct based on severity
        deductions = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 0.5,
        }

        total_deduction = sum(deductions[f.severity] * f.confidence for f in self.findings)
        return max(0.0, 100.0 - total_deduction)

    @property
    def has_blocking_issues(self) -> bool:
        """Check if there are issues that should block merge."""
        return len(self.critical_findings) > 0 or len(self.high_findings) > 3

    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            "target": self.target,
            "findings": [f.to_dict() for f in self.findings],
            "verdict": self.verdict.value,
            "summary": self.summary,
            "review_duration_seconds": self.review_duration_seconds,
            "agents_used": self.agents_used,
            "memory_graph_hits": self.memory_graph_hits,
            "quality_score": self.quality_score,
            "has_blocking_issues": self.has_blocking_issues,
            "finding_counts": {
                "critical": len(self.critical_findings),
                "high": len(self.high_findings),
                "total": len(self.findings),
            },
            "metadata": self.metadata,
        }


@dataclass
class CodeReviewConfig:
    """Configuration for code review crew."""

    # API Configuration
    provider: str = "anthropic"
    api_key: str | None = None

    # Review Configuration
    review_depth: str = "standard"  # "quick", "standard", "thorough"
    focus_areas: list[str] = field(
        default_factory=lambda: ["security", "architecture", "quality", "performance"]
    )
    check_tests: bool = True
    check_docs: bool = False

    # Memory Graph
    memory_graph_enabled: bool = True
    memory_graph_path: str = "patterns/code_review_memory.json"

    # Agent Tiers
    lead_tier: str = "premium"
    security_tier: str = "capable"
    architecture_tier: str = "premium"
    quality_tier: str = "capable"
    performance_tier: str = "capable"

    # Resilience
    resilience_enabled: bool = True
    timeout_seconds: float = 300.0


class CodeReviewCrew:
    """
    Multi-agent crew for comprehensive code reviews.

    The crew consists of 5 specialized agents:

    1. **Review Lead** (Coordinator)
       - Orchestrates the review team
       - Synthesizes findings from all agents
       - Makes final verdict decision
       - Generates executive summary
       - Model: Premium tier

    2. **Security Analyst** (Security Expert)
       - Reviews for security vulnerabilities
       - OWASP Top 10 focus
       - Checks for hardcoded secrets
       - Model: Capable tier

    3. **Architecture Reviewer** (Architect)
       - Evaluates design patterns
       - Checks SOLID principles
       - Assesses coupling and cohesion
       - Model: Premium tier

    4. **Quality Analyst** (Quality Engineer)
       - Identifies code smells
       - Checks maintainability
       - Reviews test coverage
       - Model: Capable tier

    5. **Performance Reviewer** (Performance Engineer)
       - Identifies performance issues
       - Suggests optimizations
       - Checks for anti-patterns
       - Model: Capable tier

    Example:
        crew = CodeReviewCrew(api_key="...")
        report = await crew.review(
            diff="...",
            files_changed=["src/api.py"],
        )

        # Access verdict
        if report.verdict == Verdict.APPROVE:
            print("Code is ready to merge!")

        # Get quality score
        print(f"Quality Score: {report.quality_score}/100")
    """

    def __init__(self, config: CodeReviewConfig | None = None, **kwargs: Any):
        """
        Initialize the Code Review Crew.

        Args:
            config: CodeReviewConfig or pass individual params as kwargs
            **kwargs: Individual config parameters (api_key, provider, etc.)
        """
        if config:
            self.config = config
        else:
            self.config = CodeReviewConfig(**kwargs)

        self._factory = None
        self._agents: dict[str, Any] = {}
        self._workflow = None
        self._graph = None
        self._initialized = False

    async def _initialize(self) -> None:
        """Lazy initialization of agents and workflow."""
        if self._initialized:
            return

        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        # Check if CrewAI is available
        try:
            from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import (
                _check_crewai,
            )

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

        # Create the 5 specialized agents
        await self._create_agents()

        # Create hierarchical workflow
        await self._create_workflow()

        self._initialized = True

    async def _create_agents(self) -> None:
        """Create the 5 specialized code review agents."""
        # 1. Review Lead (Coordinator)
        self._agents["lead"] = self._factory.create_agent(
            name="review_lead",
            role="coordinator",
            description="Senior engineer who orchestrates the code review team",
            system_prompt="""You are the Review Lead, a senior engineer with 15+ years.

Your responsibilities:
1. Coordinate the code review team
2. Synthesize findings from all reviewers
3. Prioritize issues by impact
4. Make final verdict decision (approve, request_changes, reject)
5. Generate actionable summary

You delegate to your team:
- Security Analyst: Security vulnerabilities and risks
- Architecture Reviewer: Design patterns and structure
- Quality Analyst: Code quality and maintainability
- Performance Reviewer: Performance issues and optimizations

For verdict decisions:
- APPROVE: No issues or only minor suggestions
- APPROVE_WITH_SUGGESTIONS: Good overall, some improvements recommended
- REQUEST_CHANGES: Issues that must be addressed before merge
- REJECT: Fundamental problems requiring significant rework

Be constructive and specific in feedback.""",
            model_tier=self.config.lead_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
            resilience_enabled=self.config.resilience_enabled,
        )

        # 2. Security Analyst
        self._agents["security"] = self._factory.create_agent(
            name="security_analyst",
            role="security",
            description="Expert at identifying security vulnerabilities",
            system_prompt="""You are the Security Analyst, a security-focused reviewer.

Your focus areas:
1. OWASP Top 10 vulnerabilities
2. SQL Injection, XSS, Command Injection
3. Hardcoded secrets, API keys, passwords
4. Authentication and authorization flaws
5. Input validation issues
6. Insecure dependencies
7. Cryptographic weaknesses

For each finding, provide:
- Clear description of the security risk
- File and line number
- Severity (critical/high/medium/low)
- Specific remediation with code example

Be thorough but minimize false positives. Focus on exploitable issues.""",
            model_tier=self.config.security_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

        # 3. Architecture Reviewer
        self._agents["architecture"] = self._factory.create_agent(
            name="architecture_reviewer",
            role="architect",
            description="Evaluates code design and architecture",
            system_prompt="""You are the Architecture Reviewer, a software architect.

Your evaluation criteria:
1. SOLID Principles
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

2. Design Patterns
   - Appropriate pattern usage
   - Anti-patterns to avoid
   - Missing patterns where beneficial

3. Code Structure
   - Module boundaries
   - Coupling and cohesion
   - Dependency direction
   - Layering violations

4. Scalability
   - Extensibility points
   - Future maintenance burden
   - Breaking changes

Provide specific refactoring suggestions with before/after examples.""",
            model_tier=self.config.architecture_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

        # 4. Quality Analyst
        self._agents["quality"] = self._factory.create_agent(
            name="quality_analyst",
            role="analyst",
            description="Identifies code quality and maintainability issues",
            system_prompt="""You are the Quality Analyst, a code quality expert.

Your focus areas:
1. Code Smells
   - Long methods/functions
   - Large classes
   - Duplicate code
   - Dead code
   - Magic numbers/strings

2. Maintainability
   - Clear naming
   - Appropriate comments
   - Consistent formatting
   - Error handling
   - Logging

3. Testing
   - Test coverage gaps
   - Edge cases
   - Error scenarios
   - Integration points

4. Complexity
   - Cyclomatic complexity
   - Nesting depth
   - Parameter counts
   - Cognitive load

Prioritize issues that affect long-term maintainability.""",
            model_tier=self.config.quality_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

        # 5. Performance Reviewer
        self._agents["performance"] = self._factory.create_agent(
            name="performance_reviewer",
            role="analyst",
            description="Identifies performance issues and optimizations",
            system_prompt="""You are the Performance Reviewer, a performance engineer.

Your focus areas:
1. Algorithm Efficiency
   - Time complexity (Big O)
   - Space complexity
   - Unnecessary iterations
   - Inefficient data structures

2. Resource Usage
   - Memory leaks
   - Connection leaks
   - File handle management
   - Cache misuse

3. Common Anti-patterns
   - N+1 queries
   - Sync operations in async code
   - Blocking main thread
   - Unoptimized regex
   - String concatenation in loops

4. Database Performance
   - Missing indexes
   - Expensive queries
   - Over-fetching
   - Transaction scope

Provide optimization suggestions with expected impact.""",
            model_tier=self.config.performance_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

    async def _create_workflow(self) -> None:
        """Create hierarchical workflow with Review Lead as manager."""
        agents = list(self._agents.values())

        self._workflow = self._factory.create_workflow(
            name="code_review_workflow",
            agents=agents,
            mode="hierarchical",  # Review Lead delegates to others
            description="Comprehensive code review with coordinated analysis",
        )

    async def review(
        self,
        diff: str = "",
        files_changed: list[str] | None = None,
        target: str = "",
        context: dict | None = None,
    ) -> CodeReviewReport:
        """
        Perform a comprehensive code review.

        Args:
            diff: Git diff or code changes to review
            files_changed: List of changed file paths
            target: Description of review target
            context: Optional context (previous findings, focus areas, etc.)

        Returns:
            CodeReviewReport with findings and verdict
        """
        import time

        start_time = time.time()

        # Initialize if needed
        await self._initialize()

        context = context or {}
        files_changed = files_changed or []
        findings: list[ReviewFinding] = []
        memory_hits = 0

        # Build target description
        if not target:
            target = f"Review of {len(files_changed)} files"

        # Check Memory Graph for similar past reviews
        if self._graph and self.config.memory_graph_enabled:
            try:
                similar = self._graph.find_similar(
                    {"name": f"code_review:{target}", "description": target},
                    threshold=0.4,
                    limit=10,
                )
                if similar:
                    memory_hits = len(similar)
                    context["similar_reviews"] = [
                        {
                            "name": node.name,
                            "verdict": node.metadata.get("verdict", "unknown"),
                            "quality_score": node.metadata.get("quality_score", 0),
                        }
                        for node, score in similar
                    ]
                    logger.info(f"Found {memory_hits} similar past reviews")
            except Exception as e:
                logger.warning(f"Error querying Memory Graph: {e}")

        # Build review task for the crew
        review_task = self._build_review_task(diff, files_changed, context)

        # Execute the workflow
        verdict = Verdict.APPROVE
        try:
            result = await self._workflow.run(review_task, initial_state=context)

            # Parse findings from result
            findings = self._parse_findings(result)

            # Determine verdict
            verdict = self._determine_verdict(findings)

        except Exception as e:
            logger.error(f"Code review failed: {e}")
            # Return partial report with error
            return CodeReviewReport(
                target=target,
                findings=findings,
                verdict=Verdict.REQUEST_CHANGES,
                summary=f"Review failed with error: {e}",
                review_duration_seconds=time.time() - start_time,
                agents_used=list(self._agents.keys()),
                memory_graph_hits=memory_hits,
                metadata={"error": str(e)},
            )

        # Build the report
        duration = time.time() - start_time
        report = CodeReviewReport(
            target=target,
            findings=findings,
            verdict=verdict,
            summary=self._generate_summary(findings, verdict),
            review_duration_seconds=duration,
            agents_used=list(self._agents.keys()),
            memory_graph_hits=memory_hits,
            metadata={
                "review_depth": self.config.review_depth,
                "framework": str(self._factory.framework.value),
                "files_changed": files_changed,
            },
        )

        # Store review in Memory Graph
        if self._graph and self.config.memory_graph_enabled:
            try:
                self._graph.add_finding(
                    "code_review_crew",
                    {
                        "type": "code_review",
                        "name": f"review:{target}",
                        "description": report.summary,
                        "verdict": verdict.value,
                        "quality_score": report.quality_score,
                        "findings_count": len(findings),
                    },
                )
                self._graph._save()
            except Exception as e:
                logger.warning(f"Error storing review in Memory Graph: {e}")

        return report

    def _build_review_task(self, diff: str, files_changed: list[str], context: dict) -> str:
        """Build the review task description for the crew."""
        depth_instructions = {
            "quick": "Focus on critical issues only. Skip style and minor issues.",
            "standard": "Cover security, architecture, quality, and performance.",
            "thorough": "Deep review including edge cases, testing, and docs.",
        }

        focus_list = ", ".join(self.config.focus_areas)

        task = f"""Perform a comprehensive code review.

Review Depth: {self.config.review_depth}
Instructions: {depth_instructions.get(self.config.review_depth, 'standard')}
Focus Areas: {focus_list}

Files Changed ({len(files_changed)}):
{chr(10).join(f'  - {f}' for f in files_changed[:20])}

Diff/Code to Review:
```
{diff[:15000]}
```

Workflow:
1. Review Lead coordinates the overall review strategy
2. Security Analyst checks for security vulnerabilities
3. Architecture Reviewer evaluates design and structure
4. Quality Analyst identifies code quality issues
5. Performance Reviewer spots performance problems

For each finding, provide:
- Title and description
- Severity (critical/high/medium/low/info)
- Category (security/architecture/quality/performance/etc.)
- File path and line number
- Specific suggestion with code example if applicable

Final Verdict Options:
- APPROVE: No issues or only minor suggestions
- APPROVE_WITH_SUGGESTIONS: Good overall, improvements recommended
- REQUEST_CHANGES: Issues must be addressed before merge
- REJECT: Fundamental problems requiring rework

"""
        if context.get("similar_reviews"):
            task += f"""
Similar Past Reviews Found: {len(context['similar_reviews'])}
Consider patterns from past reviews.
"""

        return task

    def _parse_findings(self, result: dict) -> list[ReviewFinding]:
        """Parse findings from workflow result."""
        findings = []

        output = result.get("output", "")
        metadata = result.get("metadata", {})

        # Check for structured findings in metadata
        if "findings" in metadata:
            for f in metadata["findings"]:
                findings.append(self._dict_to_finding(f))
            return findings

        # Parse from text output (fallback)
        findings = self._parse_text_findings(output)

        return findings

    def _dict_to_finding(self, data: dict) -> ReviewFinding:
        """Convert dictionary to ReviewFinding."""
        return ReviewFinding(
            title=data.get("title", "Untitled Finding"),
            description=data.get("description", ""),
            severity=Severity(data.get("severity", "medium")),
            category=FindingCategory(data.get("category", "other")),
            file_path=data.get("file_path"),
            line_number=data.get("line_number"),
            code_snippet=data.get("code_snippet"),
            suggestion=data.get("suggestion"),
            before_code=data.get("before_code"),
            after_code=data.get("after_code"),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
        )

    def _parse_text_findings(self, text: str) -> list[ReviewFinding]:
        """Parse findings from unstructured text output."""
        findings = []

        severity_keywords = {
            Severity.CRITICAL: ["critical", "security", "vulnerability"],
            Severity.HIGH: ["high", "important", "must fix"],
            Severity.MEDIUM: ["medium", "should", "consider"],
            Severity.LOW: ["low", "minor", "nitpick"],
            Severity.INFO: ["info", "suggestion", "optional"],
        }

        category_keywords = {
            FindingCategory.SECURITY: ["security", "injection", "xss", "auth"],
            FindingCategory.ARCHITECTURE: ["architecture", "design", "solid"],
            FindingCategory.QUALITY: ["quality", "smell", "duplicate"],
            FindingCategory.PERFORMANCE: ["performance", "slow", "optimize"],
            FindingCategory.TESTING: ["test", "coverage", "assertion"],
            FindingCategory.DOCUMENTATION: ["doc", "comment", "readme"],
        }

        lines = text.split("\n")
        current_finding = None

        for line in lines:
            line_lower = line.lower().strip()

            # Detect severity
            detected_severity = Severity.MEDIUM
            for sev, keywords in severity_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    detected_severity = sev
                    break

            # Detect category
            detected_category = FindingCategory.OTHER
            for cat, keywords in category_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    detected_category = cat
                    break

            # Simple finding detection
            if any(
                indicator in line_lower
                for indicator in ["issue", "finding", "problem", "fix", "should"]
            ):
                if current_finding:
                    findings.append(current_finding)

                current_finding = ReviewFinding(
                    title=line[:100].strip(),
                    description=line,
                    severity=detected_severity,
                    category=detected_category,
                )

        if current_finding:
            findings.append(current_finding)

        return findings

    def _determine_verdict(self, findings: list[ReviewFinding]) -> Verdict:
        """Determine review verdict based on findings."""
        if not findings:
            return Verdict.APPROVE

        critical_count = len([f for f in findings if f.severity == Severity.CRITICAL])
        high_count = len([f for f in findings if f.severity == Severity.HIGH])
        medium_count = len([f for f in findings if f.severity == Severity.MEDIUM])

        # Reject if too many critical issues
        if critical_count >= 3:
            return Verdict.REJECT

        # Request changes for critical or many high issues
        if critical_count > 0 or high_count > 3:
            return Verdict.REQUEST_CHANGES

        # Approve with suggestions for medium/low issues
        if high_count > 0 or medium_count > 0:
            return Verdict.APPROVE_WITH_SUGGESTIONS

        return Verdict.APPROVE

    def _generate_summary(self, findings: list[ReviewFinding], verdict: Verdict) -> str:
        """Generate executive summary of review."""
        if not findings:
            return "Code review passed with no issues identified."

        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high = sum(1 for f in findings if f.severity == Severity.HIGH)
        medium = sum(1 for f in findings if f.severity == Severity.MEDIUM)
        low = sum(1 for f in findings if f.severity == Severity.LOW)

        verdict_text = {
            Verdict.APPROVE: "Approved - ready to merge",
            Verdict.APPROVE_WITH_SUGGESTIONS: "Approved with suggestions",
            Verdict.REQUEST_CHANGES: "Changes requested before merge",
            Verdict.REJECT: "Rejected - requires significant rework",
        }

        summary_parts = [
            f"Code review verdict: {verdict_text.get(verdict, verdict.value)}",
            f"Total findings: {len(findings)}",
        ]

        if critical > 0:
            summary_parts.append(f"  - {critical} CRITICAL (blocking)")
        if high > 0:
            summary_parts.append(f"  - {high} HIGH (should address)")
        if medium > 0:
            summary_parts.append(f"  - {medium} MEDIUM (recommended)")
        if low > 0:
            summary_parts.append(f"  - {low} LOW (nice to have)")

        # Add top categories
        by_category: dict[str, int] = {}
        for f in findings:
            cat = f.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        if by_category:
            top_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:3]
            summary_parts.append("\nTop issue categories:")
            for cat, count in top_cats:
                summary_parts.append(f"  - {cat}: {count}")

        return "\n".join(summary_parts)

    @property
    def agents(self) -> dict[str, Any]:
        """Get the crew's agents."""
        return self._agents

    @property
    def is_initialized(self) -> bool:
        """Check if crew is initialized."""
        return self._initialized

    async def get_agent_stats(self) -> dict:
        """Get statistics about crew agents."""
        await self._initialize()

        stats = {
            "agent_count": len(self._agents),
            "agents": {},
            "framework": self._factory.framework.value if self._factory else "unknown",
            "memory_graph_enabled": self.config.memory_graph_enabled,
        }

        for name, agent in self._agents.items():
            stats["agents"][name] = {
                "role": agent.config.role if hasattr(agent, "config") else "unknown",
                "model_tier": getattr(agent.config, "model_tier", "unknown"),
            }

        return stats
