"""
Code Review Workflow

A tiered code analysis pipeline:
1. Haiku: Classify change type (cheap, fast)
2. Sonnet: Security scan + bug pattern matching
3. Opus: Architectural review (conditional on complexity)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier


class CodeReviewWorkflow(BaseWorkflow):
    """
    Multi-tier code review workflow.

    Uses cheap models for classification, capable models for security
    and bug scanning, and premium models only for complex architectural
    reviews (10+ files or core module changes).

    Usage:
        workflow = CodeReviewWorkflow()
        result = await workflow.execute(
            diff="...",
            files_changed=["src/main.py", "tests/test_main.py"],
            is_core_module=False
        )
    """

    name = "code-review"
    description = "Tiered code analysis with conditional premium review"
    stages = ["classify", "scan", "architect_review"]
    tier_map = {
        "classify": ModelTier.CHEAP,
        "scan": ModelTier.CAPABLE,
        "architect_review": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        file_threshold: int = 10,
        core_modules: list[str] | None = None,
        use_crew: bool = False,
        crew_config: dict | None = None,
        **kwargs: Any,
    ):
        """
        Initialize workflow.

        Args:
            file_threshold: Number of files above which premium review is used.
            core_modules: List of module paths considered "core" (trigger premium).
            use_crew: Enable CodeReviewCrew for comprehensive 5-agent analysis.
            crew_config: Configuration dict for CodeReviewCrew.
        """
        super().__init__(**kwargs)
        self.file_threshold = file_threshold
        self.core_modules = core_modules or [
            "src/core/",
            "src/security/",
            "src/auth/",
            "empathy_os/core.py",
            "empathy_os/security/",
        ]
        self.use_crew = use_crew
        self.crew_config = crew_config or {}
        self._needs_architect_review: bool = False
        self._change_type: str = "unknown"
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")

        # Dynamically configure stages based on crew setting
        if use_crew:
            self.stages = ["classify", "crew_review", "scan", "architect_review"]
            self.tier_map = {
                "classify": ModelTier.CHEAP,
                "crew_review": ModelTier.PREMIUM,
                "scan": ModelTier.CAPABLE,
                "architect_review": ModelTier.PREMIUM,
            }

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None and self._api_key:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                pass
        return self._client

    def _get_model_for_tier(self, tier: ModelTier) -> str:
        """Get the model name for a given tier."""
        provider = ModelProvider.ANTHROPIC
        return PROVIDER_MODELS.get(provider, {}).get(tier, "claude-sonnet-4-20250514")

    async def _call_llm(
        self, tier: ModelTier, system: str, user_message: str, max_tokens: int = 4096
    ) -> tuple[str, int, int]:
        """Make an actual LLM call using the Anthropic API."""
        client = self._get_client()
        if not client:
            return (
                f"[Simulated - set ANTHROPIC_API_KEY for real results]\n\n{user_message[:200]}...",
                len(user_message) // 4,
                100,
            )

        model = self._get_model_for_tier(tier)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return content, input_tokens, output_tokens

        except Exception as e:
            return f"Error calling LLM: {e}", 0, 0

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """Skip architectural review if change is simple."""
        if stage_name == "architect_review" and not self._needs_architect_review:
            return True, "Simple change - architectural review not needed"
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Execute a code review stage."""
        if stage_name == "classify":
            return await self._classify(input_data, tier)
        elif stage_name == "crew_review":
            return await self._crew_review(input_data, tier)
        elif stage_name == "scan":
            return await self._scan(input_data, tier)
        elif stage_name == "architect_review":
            return await self._architect_review(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _classify(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Classify the type of change."""
        diff = input_data.get("diff", "")
        target = input_data.get("target", "")
        files_changed = input_data.get("files_changed", [])

        # If target provided instead of diff, use it as the code to review
        code_to_review = diff or target

        system = """You are a code review classifier. Analyze the code and classify:
1. Change type: bug_fix, feature, refactor, docs, test, config, or security
2. Complexity: low, medium, high
3. Risk level: low, medium, high

Respond with a brief classification summary."""

        user_message = f"""Classify this code change:

Files: {", ".join(files_changed) if files_changed else "Not specified"}

Code:
{code_to_review[:4000]}"""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system, user_message, max_tokens=500
        )

        # Parse response to determine if architect review needed
        is_high_complexity = "high" in response.lower() and (
            "complexity" in response.lower() or "risk" in response.lower()
        )
        is_core = (
            any(any(core in f for core in self.core_modules) for f in files_changed)
            if files_changed
            else False
        )

        self._needs_architect_review = (
            len(files_changed) >= self.file_threshold
            or is_core
            or is_high_complexity
            or input_data.get("is_core_module", False)
        )

        return (
            {
                "classification": response,
                "change_type": "feature",  # Will be refined by LLM
                "files_changed": files_changed,
                "file_count": len(files_changed),
                "needs_architect_review": self._needs_architect_review,
                "is_core_module": is_core,
                "code_to_review": code_to_review,
            },
            input_tokens,
            output_tokens,
        )

    async def _crew_review(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Run CodeReviewCrew for comprehensive 5-agent analysis.

        This stage uses the CodeReviewCrew (Review Lead, Security Analyst,
        Architecture Reviewer, Quality Analyst, Performance Reviewer) for
        deep code analysis with memory graph integration.

        Falls back gracefully if CodeReviewCrew is not available.
        """
        from .code_review_adapters import (
            _check_crew_available,
            _get_crew_review,
            crew_report_to_workflow_format,
        )

        # Get code to review
        diff = input_data.get("diff", "") or input_data.get("code_to_review", "")
        files_changed = input_data.get("files_changed", [])

        # Check if crew is available
        if not _check_crew_available():
            return (
                {
                    "crew_review": {
                        "available": False,
                        "fallback": True,
                        "reason": "CodeReviewCrew not installed",
                    },
                    **input_data,
                },
                0,
                0,
            )

        # Run CodeReviewCrew
        report = await _get_crew_review(
            diff=diff,
            files_changed=files_changed,
            config=self.crew_config,
        )

        if report is None:
            return (
                {
                    "crew_review": {
                        "available": True,
                        "fallback": True,
                        "reason": "CodeReviewCrew review failed or timed out",
                    },
                    **input_data,
                },
                0,
                0,
            )

        # Convert crew report to workflow format
        crew_results = crew_report_to_workflow_format(report)

        # Update needs_architect_review based on crew findings
        has_blocking = crew_results.get("has_blocking_issues", False)
        critical_count = len(crew_results.get("assessment", {}).get("critical_findings", []))
        high_count = len(crew_results.get("assessment", {}).get("high_findings", []))

        if has_blocking or critical_count > 0 or high_count > 2:
            self._needs_architect_review = True

        crew_review_result = {
            "available": True,
            "fallback": False,
            "findings": crew_results.get("findings", []),
            "finding_count": crew_results.get("finding_count", 0),
            "verdict": crew_results.get("verdict", "approve"),
            "quality_score": crew_results.get("quality_score", 100),
            "has_blocking_issues": has_blocking,
            "critical_count": critical_count,
            "high_count": high_count,
            "summary": crew_results.get("summary", ""),
            "agents_used": crew_results.get("agents_used", []),
            "memory_graph_hits": crew_results.get("memory_graph_hits", 0),
            "review_duration_seconds": crew_results.get("review_duration_seconds", 0),
        }

        # Estimate tokens (crew uses internal LLM calls)
        input_tokens = len(diff) // 4
        output_tokens = len(str(crew_review_result)) // 4

        return (
            {
                "crew_review": crew_review_result,
                "needs_architect_review": self._needs_architect_review,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _scan(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Security scan and bug pattern matching.

        When external_audit_results is provided in input_data (e.g., from
        SecurityAuditCrew), these findings are merged with the LLM analysis
        and can trigger architect_review if critical issues are found.
        """
        code_to_review = input_data.get("code_to_review", input_data.get("diff", ""))
        classification = input_data.get("classification", "")

        # Check for external audit results (e.g., from SecurityAuditCrew)
        external_audit = input_data.get("external_audit_results")

        system = """You are a security and code quality expert. Analyze the code for:

1. SECURITY ISSUES (OWASP Top 10):
   - SQL Injection, XSS, Command Injection
   - Hardcoded secrets, API keys, passwords
   - Insecure deserialization
   - Authentication/authorization flaws

2. BUG PATTERNS:
   - Null/undefined references
   - Resource leaks
   - Race conditions
   - Error handling issues

3. CODE QUALITY:
   - Code smells
   - Maintainability issues
   - Performance concerns

For each issue found, provide:
- Severity (critical/high/medium/low)
- Location (if identifiable)
- Description
- Recommendation

Be thorough but focused on actionable findings."""

        # If external audit provided, include it in the prompt for context
        external_context = ""
        if external_audit:
            external_summary = external_audit.get("summary", "")
            external_findings = external_audit.get("findings", [])
            if external_summary or external_findings:
                # Build findings list efficiently (avoid O(n²) string concat)
                finding_lines = []
                for finding in external_findings[:10]:  # Top 10
                    sev = finding.get("severity", "unknown").upper()
                    title = finding.get("title", "N/A")
                    desc = finding.get("description", "")[:100]
                    finding_lines.append(f"- [{sev}] {title}: {desc}")

                external_context = f"""

## External Security Audit Results
Summary: {external_summary}

Findings ({len(external_findings)} total):
{chr(10).join(finding_lines)}

Verify these findings and identify additional issues."""

        user_message = f"""Review this code for security and quality issues:

Previous classification: {classification}
{external_context}
Code to review:
{code_to_review[:6000]}"""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system, user_message, max_tokens=2048
        )

        # Check if critical issues found in LLM response
        has_critical = "critical" in response.lower() or "high" in response.lower()

        # Merge external audit findings if provided
        security_findings: list[dict] = []
        external_has_critical = False

        if external_audit:
            merged_response, security_findings, external_has_critical = self._merge_external_audit(
                response, external_audit
            )
            response = merged_response
            has_critical = has_critical or external_has_critical

        return (
            {
                "scan_results": response,
                "security_findings": security_findings,
                "bug_patterns": [],
                "quality_issues": [],
                "has_critical_issues": has_critical,
                "security_score": 70 if has_critical else 90,
                "needs_architect_review": input_data.get("needs_architect_review", False)
                or has_critical,
                "code_to_review": code_to_review,
                "classification": classification,
                "external_audit_included": external_audit is not None,
                "external_audit_risk_score": (
                    external_audit.get("risk_score", 0) if external_audit else 0
                ),
            },
            input_tokens,
            output_tokens,
        )

    def _merge_external_audit(
        self, llm_response: str, external_audit: dict
    ) -> tuple[str, list, bool]:
        """
        Merge external SecurityAuditCrew results into scan output.

        Args:
            llm_response: Response from LLM security scan
            external_audit: External audit dict (from SecurityAuditCrew.to_dict())

        Returns:
            Tuple of (merged_response, security_findings, has_critical)
        """
        findings = external_audit.get("findings", [])
        summary = external_audit.get("summary", "")
        risk_score = external_audit.get("risk_score", 0)

        # Check for critical/high findings
        has_critical = any(f.get("severity") in ("critical", "high") for f in findings)

        # Build merged response
        merged_sections = [llm_response]

        if summary or findings:
            # Build crew section efficiently (avoid O(n²) string concat)
            parts = ["\n\n## SecurityAuditCrew Analysis\n"]
            if summary:
                parts.append(f"\n{summary}\n")

            parts.append(f"\n**Risk Score**: {risk_score}/100\n")

            if findings:
                critical = [f for f in findings if f.get("severity") == "critical"]
                high = [f for f in findings if f.get("severity") == "high"]

                if critical:
                    parts.append("\n### Critical Findings\n")
                    for f in critical:
                        title = f"- **{f.get('title', 'N/A')}**"
                        if f.get("file"):
                            title += f" ({f.get('file')}:{f.get('line', '?')})"
                        parts.append(title)
                        parts.append(f"\n  {f.get('description', '')[:200]}\n")
                        if f.get("remediation"):
                            parts.append(f"  *Fix*: {f.get('remediation')[:150]}\n")

                if high:
                    parts.append("\n### High Severity Findings\n")
                    for f in high[:5]:  # Top 5
                        title = f"- **{f.get('title', 'N/A')}**"
                        if f.get("file"):
                            title += f" ({f.get('file')}:{f.get('line', '?')})"
                        parts.append(title)
                        parts.append(f"\n  {f.get('description', '')[:150]}\n")

            merged_sections.append("".join(parts))

        return "\n".join(merged_sections), findings, has_critical

    async def _architect_review(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Deep architectural review.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        code_to_review = input_data.get("code_to_review", "")
        scan_results = input_data.get("scan_results", "")
        classification = input_data.get("classification", "")

        # Build input payload
        input_payload = f"""Classification: {classification}

Security Scan Results:
{scan_results[:2000]}

Code:
{code_to_review[:4000]}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            user_message = self._render_xml_prompt(
                role="senior software architect",
                goal="Perform comprehensive code review with architectural assessment",
                instructions=[
                    "Assess design patterns used (or missing)",
                    "Evaluate SOLID principles compliance",
                    "Check separation of concerns",
                    "Analyze coupling and cohesion",
                    "Provide specific improvement recommendations with examples",
                    "Suggest refactoring and testing improvements",
                    "Provide verdict: approve, approve_with_suggestions, or reject",
                ],
                constraints=[
                    "Be specific and actionable",
                    "Reference file locations where possible",
                    "Prioritize issues by impact",
                ],
                input_type="code",
                input_payload=input_payload,
            )
            system = None
        else:
            system = """You are a senior software architect. Provide a comprehensive review:

1. ARCHITECTURAL ASSESSMENT:
   - Design patterns used (or missing)
   - SOLID principles compliance
   - Separation of concerns
   - Coupling and cohesion

2. RECOMMENDATIONS:
   - Specific improvements with examples
   - Refactoring suggestions
   - Testing recommendations

3. VERDICT:
   - APPROVE: Code is production-ready
   - APPROVE_WITH_SUGGESTIONS: Minor improvements recommended
   - REQUEST_CHANGES: Issues must be addressed
   - REJECT: Fundamental problems

Provide actionable, specific feedback."""

            user_message = f"""Perform an architectural review:

{input_payload}"""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system or "", user_message, max_tokens=3000
        )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        # Determine verdict from response or parsed data
        verdict = "approve_with_suggestions"
        if parsed_data.get("xml_parsed"):
            extra = parsed_data.get("_parsed_response")
            if extra and hasattr(extra, "extra"):
                parsed_verdict = extra.extra.get("verdict", "").lower()
                if parsed_verdict in [
                    "approve",
                    "approve_with_suggestions",
                    "request_changes",
                    "reject",
                ]:
                    verdict = parsed_verdict

        if verdict == "approve_with_suggestions":
            # Fall back to text parsing
            if "REQUEST_CHANGES" in response.upper() or "REJECT" in response.upper():
                verdict = "request_changes"
            elif "APPROVE" in response.upper() and "SUGGESTIONS" not in response.upper():
                verdict = "approve"

        result: dict = {
            "architectural_review": response,
            "verdict": verdict,
            "recommendations": [],
            "model_tier_used": tier.value,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            result.update(
                {
                    "xml_parsed": True,
                    "summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                }
            )

        return (result, input_tokens, output_tokens)
