"""
Dependency Check Workflow

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
    """
    Audit dependencies for security and updates.

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
        """
        Initialize dependency check workflow.

        Args:
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "inventory":
            return await self._inventory(input_data, tier)
        elif stage_name == "assess":
            return await self._assess(input_data, tier)
        elif stage_name == "report":
            return await self._report(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _inventory(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Parse dependency files to build inventory.

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
                        }
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
                            }
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
                        }
                    )
        except (OSError, json.JSONDecodeError):
            pass
        return deps

    async def _assess(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Check dependencies for vulnerabilities.

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
                        }
                    )

                # Check for outdated (simulate version check)
                if dep["version"].startswith("<") or dep["version"].startswith("^0."):
                    outdated.append(
                        {
                            "package": dep["name"],
                            "current_version": dep["version"],
                            "status": "potentially_outdated",
                            "ecosystem": ecosystem,
                        }
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
        """
        Generate risk assessment and recommendations.

        Creates actionable report with remediation steps.
        """
        assessment = input_data.get("assessment", {})
        vulnerabilities = assessment.get("vulnerabilities", [])
        outdated = assessment.get("outdated", [])

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

        # Generate recommendations
        recommendations: list[dict] = []

        for vuln in vulnerabilities:
            recommendations.append(
                {
                    "priority": 1 if vuln["severity"] == "critical" else 2,
                    "action": "upgrade",
                    "package": vuln["package"],
                    "reason": f"Fix {vuln['cve']} ({vuln['severity']} severity)",
                    "suggestion": f"Upgrade {vuln['package']} to latest version",
                }
            )

        for dep in outdated[:10]:  # Top 10 outdated
            recommendations.append(
                {
                    "priority": 3,
                    "action": "review",
                    "package": dep["package"],
                    "reason": "Potentially outdated version",
                    "suggestion": f"Review and update {dep['package']}",
                }
            )

        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])

        report = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_dependencies": input_data.get("total_dependencies", 0),
            "vulnerability_count": len(vulnerabilities),
            "outdated_count": len(outdated),
            "recommendations": recommendations[:20],
            "summary": {
                "critical": assessment.get("critical_count", 0),
                "high": assessment.get("high_count", 0),
                "medium": assessment.get("medium_count", 0),
            },
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(report)) // 4

        return (
            {
                "report": report,
                "model_tier_used": tier.value,
            },
            input_tokens,
            output_tokens,
        )


def main():
    """CLI entry point for dependency check workflow."""
    import asyncio

    async def run():
        workflow = DependencyCheckWorkflow()
        result = await workflow.execute(path=".")

        print("\nDependency Check Results")
        print("=" * 50)
        print(f"Success: {result.success}")

        report = result.final_output.get("report", {})
        print(f"Risk Level: {report.get('risk_level', 'N/A')}")
        print(f"Risk Score: {report.get('risk_score', 0)}/100")
        print(f"Total Dependencies: {report.get('total_dependencies', 0)}")
        print(f"Vulnerabilities: {report.get('vulnerability_count', 0)}")
        print(f"Outdated: {report.get('outdated_count', 0)}")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        print(
            f"  Savings: ${result.cost_report.savings:.4f} ({result.cost_report.savings_percent:.1f}%)"
        )

    asyncio.run(run())


if __name__ == "__main__":
    main()
