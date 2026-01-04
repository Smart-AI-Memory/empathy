"""Dependency Check Workflow

Audits dependencies for vulnerabilities, updates, and licensing issues.
Parses lockfiles and checks against known vulnerability patterns.

Stages:
1. inventory (CHEAP) - Parse requirements.txt, package.json, etc.
2. assess (CAPABLE) - Check for known vulnerabilities and updates
3. report (CAPABLE) - Generate risk assessment and recommendations

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import re
from pathlib import Path
from typing import Any

from .base import BaseWorkflow, ModelTier
from .step_config import WorkflowStepConfig

# Define step configurations for executor-based execution
DEPENDENCY_CHECK_STEPS = {
    "report": WorkflowStepConfig(
        name="report",
        task_type="analyze",  # Capable tier task
        tier_hint="capable",
        description="Generate dependency security report with remediation steps",
        max_tokens=3000,
    ),
}

# Known vulnerable package patterns (simulated CVE database)
KNOWN_VULNERABILITIES = {
    "requests": {"affected_versions": ["<2.25.0"], "severity": "medium", "cve": "CVE-2021-XXXX"},
    "urllib3": {"affected_versions": ["<1.26.5"], "severity": "high", "cve": "CVE-2021-XXXX"},
    "pyyaml": {"affected_versions": ["<5.4"], "severity": "critical", "cve": "CVE-2020-XXXX"},
    "django": {"affected_versions": ["<3.2.4"], "severity": "high", "cve": "CVE-2021-XXXX"},
    "flask": {"affected_versions": ["<2.0.0"], "severity": "medium", "cve": "CVE-2021-XXXX"},
    "lodash": {"affected_versions": ["<4.17.21"], "severity": "high", "cve": "CVE-2021-XXXX"},
    "axios": {"affected_versions": ["<0.21.1"], "severity": "medium", "cve": "CVE-2021-XXXX"},
}


class DependencyCheckWorkflow(BaseWorkflow):
    """Audit dependencies for security and updates.

    Scans dependency files to identify vulnerable, outdated,
    or potentially problematic packages.
    """

    name = "dependency-check"
    description = "Audit dependencies for vulnerabilities and updates"
    stages = ["inventory", "assess", "report"]
    tier_map = {
        "inventory": ModelTier.CHEAP,
        "assess": ModelTier.CAPABLE,
        "report": ModelTier.CAPABLE,
    }

    def __init__(self, **kwargs: Any):
        """Initialize dependency check workflow.

        Args:
            **kwargs: Additional arguments passed to BaseWorkflow

        """
        super().__init__(**kwargs)

    async def run_stage(
        self,
        stage_name: str,
        tier: ModelTier,
        input_data: Any,
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "inventory":
            return await self._inventory(input_data, tier)
        if stage_name == "assess":
            return await self._assess(input_data, tier)
        if stage_name == "report":
            return await self._report(input_data, tier)
        raise ValueError(f"Unknown stage: {stage_name}")

    async def _inventory(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Parse dependency files to build inventory.

        Supports requirements.txt, pyproject.toml, package.json,
        and their lockfiles.
        """
        target_path = input_data.get("path", ".")
        target = Path(target_path)

        dependencies: dict[str, list[dict]] = {
            "python": [],
            "node": [],
        }
        files_found: list[str] = []

        # Parse Python dependencies
        req_files = ["requirements.txt", "requirements-dev.txt", "requirements-test.txt"]
        for req_file in req_files:
            req_path = target / req_file
            if req_path.exists():
                files_found.append(str(req_path))
                deps = self._parse_requirements(req_path)
                dependencies["python"].extend(deps)

        # Parse pyproject.toml
        pyproject_path = target / "pyproject.toml"
        if pyproject_path.exists():
            files_found.append(str(pyproject_path))
            deps = self._parse_pyproject(pyproject_path)
            dependencies["python"].extend(deps)

        # Parse package.json
        package_json = target / "package.json"
        if package_json.exists():
            files_found.append(str(package_json))
            deps = self._parse_package_json(package_json)
            dependencies["node"].extend(deps)

        # Deduplicate
        for ecosystem in dependencies:
            seen = set()
            unique = []
            for dep in dependencies[ecosystem]:
                name = dep["name"].lower()
                if name not in seen:
                    seen.add(name)
                    unique.append(dep)
            dependencies[ecosystem] = unique

        total_count = sum(len(deps) for deps in dependencies.values())

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(dependencies)) // 4

        return (
            {
                "dependencies": dependencies,
                "files_found": files_found,
                "total_dependencies": total_count,
                "python_count": len(dependencies["python"]),
                "node_count": len(dependencies["node"]),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _parse_requirements(self, path: Path) -> list[dict]:
        """Parse requirements.txt format."""
        deps = []
        try:
            content = path.read_text()
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue

                # Parse version specifiers
                match = re.match(r"^([a-zA-Z0-9_-]+)\s*([<>=!~]+\s*[\d.]+)?", line)
                if match:
                    name = match.group(1)
                    version = match.group(2).strip() if match.group(2) else "any"
                    deps.append(
                        {
                            "name": name,
                            "version": version,
                            "source": str(path),
                            "ecosystem": "python",
                        },
                    )
        except OSError:
            pass
        return deps

    def _parse_pyproject(self, path: Path) -> list[dict]:
        """Parse pyproject.toml for dependencies."""
        deps = []
        try:
            content = path.read_text()
            # Simple TOML parsing for dependencies
            in_deps = False
            for line in content.splitlines():
                if "dependencies" in line and "=" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("]"):
                        in_deps = False
                        continue
                    match = re.search(r'"([a-zA-Z0-9_-]+)([<>=!~]+[\d.]+)?"', line)
                    if match:
                        name = match.group(1)
                        version = match.group(2) if match.group(2) else "any"
                        deps.append(
                            {
                                "name": name,
                                "version": version,
                                "source": str(path),
                                "ecosystem": "python",
                            },
                        )
        except OSError:
            pass
        return deps

    def _parse_package_json(self, path: Path) -> list[dict]:
        """Parse package.json for dependencies."""
        deps = []
        try:
            with open(path) as f:
                data = json.load(f)

            for dep_type in ["dependencies", "devDependencies"]:
                for name, version in data.get(dep_type, {}).items():
                    deps.append(
                        {
                            "name": name,
                            "version": version,
                            "source": str(path),
                            "ecosystem": "node",
                            "dev": dep_type == "devDependencies",
                        },
                    )
        except (OSError, json.JSONDecodeError):
            pass
        return deps

    async def _assess(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Check dependencies for vulnerabilities.

        Compares against known vulnerability database and
        identifies outdated packages.
        """
        dependencies = input_data.get("dependencies", {})

        vulnerabilities: list[dict] = []
        outdated: list[dict] = []

        for ecosystem, deps in dependencies.items():
            for dep in deps:
                name = dep["name"].lower()

                # Check known vulnerabilities
                if name in KNOWN_VULNERABILITIES:
                    vuln_info = KNOWN_VULNERABILITIES[name]
                    vulnerabilities.append(
                        {
                            "package": dep["name"],
                            "current_version": dep["version"],
                            "affected_versions": vuln_info["affected_versions"],
                            "severity": vuln_info["severity"],
                            "cve": vuln_info["cve"],
                            "ecosystem": ecosystem,
                        },
                    )

                # Check for outdated (simulate version check)
                if dep["version"].startswith("<") or dep["version"].startswith("^0."):
                    outdated.append(
                        {
                            "package": dep["name"],
                            "current_version": dep["version"],
                            "status": "potentially_outdated",
                            "ecosystem": ecosystem,
                        },
                    )

        # Categorize by severity
        critical = [v for v in vulnerabilities if v["severity"] == "critical"]
        high = [v for v in vulnerabilities if v["severity"] == "high"]
        medium = [v for v in vulnerabilities if v["severity"] == "medium"]

        assessment = {
            "vulnerabilities": vulnerabilities,
            "outdated": outdated,
            "vulnerability_count": len(vulnerabilities),
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
            "outdated_count": len(outdated),
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

    async def _report(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Generate risk assessment and recommendations using LLM.

        Creates actionable report with remediation steps.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        assessment = input_data.get("assessment", {})
        vulnerabilities = assessment.get("vulnerabilities", [])
        outdated = assessment.get("outdated", [])
        target = input_data.get("path", "")

        # Calculate risk score
        risk_score = (
            assessment.get("critical_count", 0) * 25
            + assessment.get("high_count", 0) * 10
            + assessment.get("medium_count", 0) * 3
            + assessment.get("outdated_count", 0) * 1
        )
        risk_score = min(100, risk_score)

        risk_level = (
            "critical"
            if risk_score >= 75
            else "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low"
        )

        # Build vulnerability summary for LLM
        vuln_summary = []
        for v in vulnerabilities[:15]:
            vuln_summary.append(
                f"- {v.get('package')}@{v.get('current_version')}: "
                f"{v.get('cve')} ({v.get('severity')})",
            )

        # Build input payload for prompt
        input_payload = f"""Target: {target or "codebase"}

Total Dependencies: {input_data.get("total_dependencies", 0)}
Risk Score: {risk_score}/100
Risk Level: {risk_level}

Vulnerabilities ({len(vulnerabilities)}):
{chr(10).join(vuln_summary) if vuln_summary else "None found"}

Outdated Packages: {len(outdated)}

Severity Summary:
- Critical: {assessment.get("critical_count", 0)}
- High: {assessment.get("high_count", 0)}
- Medium: {assessment.get("medium_count", 0)}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="security engineer specializing in dependency management",
                goal="Generate a comprehensive dependency security report with remediation steps",
                instructions=[
                    "Analyze the vulnerability findings and their severity",
                    "Prioritize remediation actions by risk level",
                    "Provide specific upgrade recommendations",
                    "Identify potential breaking changes from upgrades",
                    "Suggest a remediation timeline",
                ],
                constraints=[
                    "Focus on actionable recommendations",
                    "Prioritize critical and high severity issues",
                    "Include version upgrade targets where possible",
                ],
                input_type="dependency_vulnerabilities",
                input_payload=input_payload,
                extra={
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a security engineer specializing in dependency management.
Analyze the vulnerability findings and generate a comprehensive remediation report.

Focus on:
1. Prioritizing by severity
2. Specific upgrade recommendations
3. Potential breaking changes
4. Remediation timeline"""

            user_message = f"""Generate a dependency security report:

{input_payload}

Provide actionable remediation recommendations."""

        # Try executor-based execution first (Phase 3 pattern)
        if self._executor is not None or self._api_key:
            try:
                step = DEPENDENCY_CHECK_STEPS["report"]
                response, input_tokens, output_tokens, cost = await self.run_step_with_executor(
                    step=step,
                    prompt=user_message,
                    system=system,
                )
            except Exception:
                # Fall back to legacy _call_llm if executor fails
                response, input_tokens, output_tokens = await self._call_llm(
                    tier,
                    system or "",
                    user_message,
                    max_tokens=3000,
                )
        else:
            # Legacy path for backward compatibility
            response, input_tokens, output_tokens = await self._call_llm(
                tier,
                system or "",
                user_message,
                max_tokens=3000,
            )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        # Generate basic recommendations for backwards compatibility
        recommendations: list[dict] = []

        for vuln in vulnerabilities:
            recommendations.append(
                {
                    "priority": 1 if vuln["severity"] == "critical" else 2,
                    "action": "upgrade",
                    "package": vuln["package"],
                    "reason": f"Fix {vuln['cve']} ({vuln['severity']} severity)",
                    "suggestion": f"Upgrade {vuln['package']} to latest version",
                },
            )

        for dep in outdated[:10]:  # Top 10 outdated
            recommendations.append(
                {
                    "priority": 3,
                    "action": "review",
                    "package": dep["package"],
                    "reason": "Potentially outdated version",
                    "suggestion": f"Review and update {dep['package']}",
                },
            )

        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])

        result = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_dependencies": input_data.get("total_dependencies", 0),
            "vulnerability_count": len(vulnerabilities),
            "outdated_count": len(outdated),
            "recommendations": recommendations[:20],
            "security_report": response,
            "summary": {
                "critical": assessment.get("critical_count", 0),
                "high": assessment.get("high_count", 0),
                "medium": assessment.get("medium_count", 0),
            },
            "model_tier_used": tier.value,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            result.update(
                {
                    "xml_parsed": True,
                    "report_summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                },
            )

        # Add formatted report for human readability
        result["formatted_report"] = format_dependency_check_report(result, input_data)

        return (result, input_tokens, output_tokens)


def format_dependency_check_report(result: dict, input_data: dict) -> str:
    """Format dependency check output as a human-readable report.

    Args:
        result: The report stage result
        input_data: Input data from previous stages

    Returns:
        Formatted report string

    """
    lines = []

    # Header with risk level
    risk_score = result.get("risk_score", 0)

    if risk_score >= 75:
        risk_icon = "🔴"
        risk_text = "CRITICAL"
    elif risk_score >= 50:
        risk_icon = "🟠"
        risk_text = "HIGH RISK"
    elif risk_score >= 25:
        risk_icon = "🟡"
        risk_text = "MEDIUM RISK"
    else:
        risk_icon = "🟢"
        risk_text = "LOW RISK"

    lines.append("=" * 60)
    lines.append("DEPENDENCY SECURITY REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Risk Level: {risk_icon} {risk_text}")
    lines.append(f"Risk Score: {risk_score}/100")
    lines.append("")

    # Inventory summary
    total_deps = result.get("total_dependencies", 0)
    python_count = input_data.get("python_count", 0)
    node_count = input_data.get("node_count", 0)
    files_found = input_data.get("files_found", [])

    lines.append("-" * 60)
    lines.append("DEPENDENCY INVENTORY")
    lines.append("-" * 60)
    lines.append(f"Total Dependencies: {total_deps}")
    if python_count:
        lines.append(f"  Python: {python_count}")
    if node_count:
        lines.append(f"  Node.js: {node_count}")
    if files_found:
        lines.append(f"Files Scanned: {len(files_found)}")
        for f in files_found[:5]:
            lines.append(f"  • {f}")
    lines.append("")

    # Vulnerability summary
    summary = result.get("summary", {})
    vuln_count = result.get("vulnerability_count", 0)
    outdated_count = result.get("outdated_count", 0)

    lines.append("-" * 60)
    lines.append("SECURITY FINDINGS")
    lines.append("-" * 60)
    lines.append(f"Vulnerabilities: {vuln_count}")
    lines.append(f"  🔴 Critical: {summary.get('critical', 0)}")
    lines.append(f"  🟠 High: {summary.get('high', 0)}")
    lines.append(f"  🟡 Medium: {summary.get('medium', 0)}")
    lines.append(f"Outdated Packages: {outdated_count}")
    lines.append("")

    # Vulnerabilities detail
    assessment = input_data.get("assessment", {})
    vulnerabilities = assessment.get("vulnerabilities", [])
    if vulnerabilities:
        lines.append("-" * 60)
        lines.append("VULNERABLE PACKAGES")
        lines.append("-" * 60)
        for vuln in vulnerabilities[:10]:
            severity = vuln.get("severity", "unknown").upper()
            pkg = vuln.get("package", "unknown")
            version = vuln.get("current_version", "?")
            cve = vuln.get("cve", "N/A")
            sev_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(severity, "⚪")
            lines.append(f"  {sev_icon} {pkg}@{version}")
            lines.append(f"      CVE: {cve} | Severity: {severity}")
        if len(vulnerabilities) > 10:
            lines.append(f"  ... and {len(vulnerabilities) - 10} more")
        lines.append("")

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("-" * 60)
        lines.append("REMEDIATION ACTIONS")
        lines.append("-" * 60)
        priority_labels = {1: "🔴 URGENT", 2: "🟠 HIGH", 3: "🟡 REVIEW"}
        for rec in recommendations[:10]:
            priority = rec.get("priority", 3)
            pkg = rec.get("package", "unknown")
            suggestion = rec.get("suggestion", "")
            label = priority_labels.get(priority, "⚪ LOW")
            lines.append(f"  {label}: {pkg}")
            lines.append(f"      {suggestion}")
        lines.append("")

    # Security report from LLM (if available)
    security_report = result.get("security_report", "")
    if security_report and not security_report.startswith("[Simulated"):
        lines.append("-" * 60)
        lines.append("DETAILED ANALYSIS")
        lines.append("-" * 60)
        # Truncate if very long
        if len(security_report) > 1500:
            lines.append(security_report[:1500] + "...")
        else:
            lines.append(security_report)
        lines.append("")

    # Footer
    lines.append("=" * 60)
    model_tier = result.get("model_tier_used", "unknown")
    lines.append(f"Scanned {total_deps} dependencies using {model_tier} tier model")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """CLI entry point for dependency check workflow."""
    import asyncio

    async def run():
        workflow = DependencyCheckWorkflow()
        result = await workflow.execute(path=".")

        print("\nDependency Check Results")
        print("=" * 50)
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")

        report = result.final_output.get("report", {})
        print(f"Risk Level: {report.get('risk_level', 'N/A')}")
        print(f"Risk Score: {report.get('risk_score', 0)}/100")
        print(f"Total Dependencies: {report.get('total_dependencies', 0)}")
        print(f"Vulnerabilities: {report.get('vulnerability_count', 0)}")
        print(f"Outdated: {report.get('outdated_count', 0)}")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
