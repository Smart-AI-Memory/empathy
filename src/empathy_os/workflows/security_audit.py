"""
Security Audit Workflow

OWASP-focused security scan with intelligent vulnerability assessment.
Integrates with team security decisions to filter known false positives.

Stages:
1. triage (CHEAP) - Quick scan for common vulnerability patterns
2. analyze (CAPABLE) - Deep analysis of flagged areas
3. assess (CAPABLE) - Risk scoring and severity classification
4. remediate (PREMIUM) - Generate remediation plan (conditional)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier

# Common security vulnerability patterns (OWASP Top 10 inspired)
SECURITY_PATTERNS = {
    "sql_injection": {
        "patterns": [
            r'execute\s*\(\s*["\'].*%s',
            r'cursor\.execute\s*\(\s*f["\']',
            r"\.format\s*\(.*\).*execute",
        ],
        "severity": "critical",
        "owasp": "A03:2021 Injection",
    },
    "xss": {
        "patterns": [
            r"innerHTML\s*=",
            r"dangerouslySetInnerHTML",
            r"document\.write\s*\(",
        ],
        "severity": "high",
        "owasp": "A03:2021 Injection",
    },
    "hardcoded_secret": {
        "patterns": [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
        ],
        "severity": "critical",
        "owasp": "A02:2021 Cryptographic Failures",
    },
    "insecure_random": {
        "patterns": [
            r"random\.\w+\s*\(",
            r"Math\.random\s*\(",
        ],
        "severity": "medium",
        "owasp": "A02:2021 Cryptographic Failures",
    },
    "path_traversal": {
        "patterns": [
            r"open\s*\([^)]*\+[^)]*\)",
            r"readFile\s*\([^)]*\+[^)]*\)",
        ],
        "severity": "high",
        "owasp": "A01:2021 Broken Access Control",
    },
    "command_injection": {
        "patterns": [
            r"subprocess\.\w+\s*\([^)]*shell\s*=\s*True",
            r"os\.system\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
        ],
        "severity": "critical",
        "owasp": "A03:2021 Injection",
    },
}


class SecurityAuditWorkflow(BaseWorkflow):
    """
    OWASP-focused security audit with team decision integration.

    Scans code for security vulnerabilities while respecting
    team decisions about false positives and accepted risks.
    """

    name = "security-audit"
    description = "OWASP-focused security scan with vulnerability assessment"
    stages = ["triage", "analyze", "assess", "remediate"]
    tier_map = {
        "triage": ModelTier.CHEAP,
        "analyze": ModelTier.CAPABLE,
        "assess": ModelTier.CAPABLE,
        "remediate": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        patterns_dir: str = "./patterns",
        skip_remediate_if_clean: bool = True,
        use_crew_for_remediation: bool = False,
        crew_config: dict | None = None,
        **kwargs: Any,
    ):
        """
        Initialize security audit workflow.

        Args:
            patterns_dir: Directory containing security decisions
            skip_remediate_if_clean: Skip remediation if no high/critical findings
            use_crew_for_remediation: Use SecurityAuditCrew for enhanced remediation
            crew_config: Configuration dict for SecurityAuditCrew
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.patterns_dir = patterns_dir
        self.skip_remediate_if_clean = skip_remediate_if_clean
        self.use_crew_for_remediation = use_crew_for_remediation
        self.crew_config = crew_config or {}
        self._has_critical: bool = False
        self._team_decisions: dict[str, dict] = {}
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")
        self._load_team_decisions()

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
                "[Simulated - set ANTHROPIC_API_KEY for real results]",
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

    def _load_team_decisions(self) -> None:
        """Load team security decisions for false positive filtering."""
        decisions_file = Path(self.patterns_dir) / "security" / "team_decisions.json"
        if decisions_file.exists():
            try:
                with open(decisions_file) as f:
                    data = json.load(f)
                    for decision in data.get("decisions", []):
                        key = decision.get("finding_hash", "")
                        self._team_decisions[key] = decision
            except (json.JSONDecodeError, OSError):
                pass

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Skip remediation stage if no critical/high findings.

        Args:
            stage_name: Name of the stage to check
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        if stage_name == "remediate" and self.skip_remediate_if_clean:
            if not self._has_critical:
                return True, "No high/critical findings requiring remediation"
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "triage":
            return await self._triage(input_data, tier)
        elif stage_name == "analyze":
            return await self._analyze(input_data, tier)
        elif stage_name == "assess":
            return await self._assess(input_data, tier)
        elif stage_name == "remediate":
            return await self._remediate(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _triage(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Quick scan for common vulnerability patterns.

        Uses regex patterns to identify potential security issues
        across the codebase for further analysis.
        """
        target_path = input_data.get("path", ".")
        file_types = input_data.get("file_types", [".py", ".ts", ".tsx", ".js", ".jsx"])

        findings: list[dict] = []
        files_scanned = 0

        target = Path(target_path)
        if target.exists():
            for ext in file_types:
                for file_path in target.rglob(f"*{ext}"):
                    if any(
                        skip in str(file_path)
                        for skip in [".git", "node_modules", "__pycache__", "venv"]
                    ):
                        continue

                    try:
                        content = file_path.read_text(errors="ignore")
                        files_scanned += 1

                        for vuln_type, vuln_info in SECURITY_PATTERNS.items():
                            for pattern in vuln_info["patterns"]:
                                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                                for match in matches:
                                    # Find line number
                                    line_num = content[: match.start()].count("\n") + 1
                                    findings.append(
                                        {
                                            "type": vuln_type,
                                            "file": str(file_path),
                                            "line": line_num,
                                            "match": match.group()[:100],
                                            "severity": vuln_info["severity"],
                                            "owasp": vuln_info["owasp"],
                                        }
                                    )
                    except OSError:
                        continue

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(findings)) // 4

        return (
            {
                "findings": findings,
                "files_scanned": files_scanned,
                "finding_count": len(findings),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _analyze(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Deep analysis of flagged areas.

        Filters findings against team decisions and performs
        deeper analysis of genuine security concerns.
        """
        findings = input_data.get("findings", [])
        analyzed: list[dict] = []

        for finding in findings:
            finding_key = finding.get("type", "")

            # Check team decisions
            decision = self._team_decisions.get(finding_key)
            if decision:
                if decision.get("decision") == "false_positive":
                    finding["status"] = "false_positive"
                    finding["decision_reason"] = decision.get("reason", "")
                    finding["decided_by"] = decision.get("decided_by", "")
                elif decision.get("decision") == "accepted":
                    finding["status"] = "accepted_risk"
                    finding["decision_reason"] = decision.get("reason", "")
                elif decision.get("decision") == "deferred":
                    finding["status"] = "deferred"
                    finding["decision_reason"] = decision.get("reason", "")
                else:
                    finding["status"] = "needs_review"
            else:
                finding["status"] = "needs_review"

            # Add context analysis
            if finding["status"] == "needs_review":
                finding["analysis"] = self._analyze_finding(finding)

            analyzed.append(finding)

        # Separate by status
        needs_review = [f for f in analyzed if f["status"] == "needs_review"]
        false_positives = [f for f in analyzed if f["status"] == "false_positive"]
        accepted = [f for f in analyzed if f["status"] == "accepted_risk"]

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(analyzed)) // 4

        return (
            {
                "analyzed_findings": analyzed,
                "needs_review": needs_review,
                "false_positives": false_positives,
                "accepted_risks": accepted,
                "review_count": len(needs_review),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _analyze_finding(self, finding: dict) -> str:
        """Generate analysis context for a finding."""
        vuln_type = finding.get("type", "")
        analyses = {
            "sql_injection": "Potential SQL injection. Verify parameterized input.",
            "xss": "Potential XSS vulnerability. Check output escaping.",
            "hardcoded_secret": "Hardcoded credential. Use env vars or secrets manager.",
            "insecure_random": "Insecure random. Use secrets module instead.",
            "path_traversal": "Potential path traversal. Validate file paths.",
            "command_injection": "Potential command injection. Avoid shell=True.",
        }
        return analyses.get(vuln_type, "Review for security implications.")

    async def _assess(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Risk scoring and severity classification.

        Calculates overall security risk score and identifies
        critical issues requiring immediate attention.
        """
        needs_review = input_data.get("needs_review", [])

        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in needs_review:
            sev = finding.get("severity", "low")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # Calculate risk score (0-100)
        risk_score = (
            severity_counts["critical"] * 25
            + severity_counts["high"] * 10
            + severity_counts["medium"] * 3
            + severity_counts["low"] * 1
        )
        risk_score = min(100, risk_score)

        # Set flag for skip logic
        self._has_critical = severity_counts["critical"] > 0 or severity_counts["high"] > 0

        # Group findings by OWASP category
        by_owasp: dict[str, list] = {}
        for finding in needs_review:
            owasp = finding.get("owasp", "Unknown")
            if owasp not in by_owasp:
                by_owasp[owasp] = []
            by_owasp[owasp].append(finding)

        assessment = {
            "risk_score": risk_score,
            "risk_level": (
                "critical"
                if risk_score >= 75
                else "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low"
            ),
            "severity_breakdown": severity_counts,
            "by_owasp_category": {k: len(v) for k, v in by_owasp.items()},
            "critical_findings": [f for f in needs_review if f.get("severity") == "critical"],
            "high_findings": [f for f in needs_review if f.get("severity") == "high"],
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(assessment)) // 4

        return (
            {
                "assessment": assessment,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _remediate(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Generate remediation plan for security issues.

        Creates actionable remediation steps prioritized by
        severity and grouped by OWASP category.

        When use_crew_for_remediation=True, uses SecurityAuditCrew's
        Remediation Expert agent for enhanced recommendations.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        from .security_adapters import (
            _check_crew_available,
        )

        assessment = input_data.get("assessment", {})
        critical = assessment.get("critical_findings", [])
        high = assessment.get("high_findings", [])
        target = input_data.get("target", input_data.get("path", ""))

        crew_remediation = None
        crew_enhanced = False

        # Try crew-based remediation first if enabled
        if self.use_crew_for_remediation and _check_crew_available():
            crew_remediation = await self._get_crew_remediation(target, critical + high, assessment)
            if crew_remediation:
                crew_enhanced = True

        # Build findings summary for LLM
        findings_summary = []
        for f in critical:
            findings_summary.append(
                f"CRITICAL: {f.get('type')} in {f.get('file')}:{f.get('line')} - {f.get('owasp')}"
            )
        for f in high:
            findings_summary.append(
                f"HIGH: {f.get('type')} in {f.get('file')}:{f.get('line')} - {f.get('owasp')}"
            )

        # Build input payload for prompt
        input_payload = f"""Target: {target or 'codebase'}

Findings:
{chr(10).join(findings_summary) if findings_summary else 'No critical or high findings'}

Risk Score: {assessment.get('risk_score', 0)}/100
Risk Level: {assessment.get('risk_level', 'unknown')}

Severity Breakdown: {json.dumps(assessment.get('severity_breakdown', {}), indent=2)}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="application security engineer",
                goal="Generate a comprehensive remediation plan for security vulnerabilities",
                instructions=[
                    "Explain each vulnerability and its potential impact",
                    "Provide specific remediation steps with code examples",
                    "Suggest preventive measures to avoid similar issues",
                    "Reference relevant OWASP guidelines",
                    "Prioritize by severity (critical first, then high)",
                ],
                constraints=[
                    "Be specific and actionable",
                    "Include code examples where helpful",
                    "Group fixes by severity",
                ],
                input_type="security_findings",
                input_payload=input_payload,
                extra={
                    "risk_score": assessment.get("risk_score", 0),
                    "risk_level": assessment.get("risk_level", "unknown"),
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a security expert in application security and OWASP.
Generate a comprehensive remediation plan for the security findings.

For each finding:
1. Explain the vulnerability and its potential impact
2. Provide specific remediation steps with code examples
3. Suggest preventive measures to avoid similar issues
4. Reference relevant OWASP guidelines

Prioritize by severity (critical first, then high).
Be specific and actionable."""

            user_message = f"""Generate a remediation plan for these security findings:

{input_payload}

Provide a detailed remediation plan with specific fixes."""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system or "", user_message, max_tokens=3000
        )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        # Merge crew remediation if available
        if crew_enhanced and crew_remediation:
            response = self._merge_crew_remediation(response, crew_remediation)

        result = {
            "remediation_plan": response,
            "remediation_count": len(critical) + len(high),
            "risk_score": assessment.get("risk_score", 0),
            "risk_level": assessment.get("risk_level", "unknown"),
            "model_tier_used": tier.value,
            "crew_enhanced": crew_enhanced,
        }

        # Add crew-specific fields if enhanced
        if crew_enhanced and crew_remediation:
            result["crew_findings"] = crew_remediation.get("findings", [])
            result["crew_agents_used"] = crew_remediation.get("agents_used", [])

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

    async def _get_crew_remediation(
        self, target: str, findings: list, assessment: dict
    ) -> dict | None:
        """
        Get remediation recommendations from SecurityAuditCrew.

        Args:
            target: Path to codebase
            findings: List of findings needing remediation
            assessment: Current assessment dict

        Returns:
            Crew results dict or None if failed
        """
        try:
            from empathy_llm_toolkit.agent_factory.crews import (
                SecurityAuditConfig,
                SecurityAuditCrew,
            )

            from .security_adapters import (
                crew_report_to_workflow_format,
                workflow_findings_to_crew_format,
            )

            # Configure crew for focused remediation
            config = SecurityAuditConfig(
                scan_depth="quick",  # Skip deep scan, focus on remediation
                **self.crew_config,
            )
            crew = SecurityAuditCrew(config=config)

            # Convert findings to crew format for context
            crew_findings = workflow_findings_to_crew_format(findings)

            # Run audit with remediation focus
            context = {
                "focus_areas": ["remediation"],
                "existing_findings": crew_findings,
                "skip_detection": True,  # We already have findings
                "risk_score": assessment.get("risk_score", 0),
            }

            report = await crew.audit(target, context=context)

            if report:
                return crew_report_to_workflow_format(report)
            return None

        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(f"Crew remediation failed: {e}")
            return None

    def _merge_crew_remediation(self, llm_response: str, crew_remediation: dict) -> str:
        """
        Merge crew remediation recommendations with LLM response.

        Args:
            llm_response: LLM-generated remediation plan
            crew_remediation: Crew results in workflow format

        Returns:
            Merged response with crew enhancements
        """
        crew_findings = crew_remediation.get("findings", [])

        if not crew_findings:
            return llm_response

        crew_section = "\n\n## Enhanced Remediation (SecurityAuditCrew)\n\n"
        crew_section += f"**Agents Used**: {', '.join(crew_remediation.get('agents_used', []))}\n\n"

        for finding in crew_findings:
            if finding.get("remediation"):
                crew_section += f"### {finding.get('title', 'Finding')}\n"
                crew_section += f"**Severity**: {finding.get('severity', 'unknown').upper()}\n"
                if finding.get("cwe_id"):
                    crew_section += f"**CWE**: {finding.get('cwe_id')}\n"
                if finding.get("cvss_score"):
                    crew_section += f"**CVSS Score**: {finding.get('cvss_score')}\n"
                crew_section += f"\n**Remediation**:\n{finding.get('remediation')}\n\n"

        return llm_response + crew_section

    def _get_remediation_action(self, finding: dict) -> str:
        """Generate specific remediation action for a finding."""
        actions = {
            "sql_injection": "Use parameterized queries or ORM. Never interpolate user input.",
            "xss": "Use framework's auto-escaping. Sanitize user input.",
            "hardcoded_secret": "Move to env vars or use a secrets manager.",
            "insecure_random": "Use secrets.token_hex() or secrets.randbelow().",
            "path_traversal": "Use os.path.realpath() and validate paths.",
            "command_injection": "Use subprocess with shell=False and argument lists.",
        }
        return actions.get(finding.get("type", ""), "Apply security best practices.")


def main():
    """CLI entry point for security audit workflow."""
    import asyncio

    async def run():
        workflow = SecurityAuditWorkflow()
        result = await workflow.execute(path=".", file_types=[".py"])

        print("\nSecurity Audit Results")
        print("=" * 50)
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")

        assessment = result.final_output.get("assessment", {})
        print(f"Risk Level: {assessment.get('risk_level', 'N/A')}")
        print(f"Risk Score: {assessment.get('risk_score', 0)}/100")
        print("\nSeverity Breakdown:")
        for sev, count in assessment.get("severity_breakdown", {}).items():
            print(f"  {sev}: {count}")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
