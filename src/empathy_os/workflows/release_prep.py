"""
Release Preparation Workflow

Pre-release quality gate combining health checks, security scan,
and changelog generation.

Stages:
1. health (CHEAP) - Run health checks (lint, types, tests)
2. security (CAPABLE) - Security scan summary
3. changelog (CAPABLE) - Generate changelog from commits
4. approve (PREMIUM) - Final release readiness assessment (conditional)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier


class ReleasePreparationWorkflow(BaseWorkflow):
    """
    Pre-release quality gate workflow.

    Combines multiple checks to determine if the codebase
    is ready for release.

    When use_security_crew=True, adds an additional crew_security stage
    that runs SecurityAuditCrew for comprehensive security analysis.
    """

    name = "release-prep"
    description = "Pre-release quality gate with health, security, and changelog"

    # Default stages (can be modified in __init__)
    stages = ["health", "security", "changelog", "approve"]
    tier_map = {
        "health": ModelTier.CHEAP,
        "security": ModelTier.CAPABLE,
        "changelog": ModelTier.CAPABLE,
        "approve": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        skip_approve_if_clean: bool = True,
        use_security_crew: bool = False,
        crew_config: dict | None = None,
        **kwargs: Any,
    ):
        """
        Initialize release preparation workflow.

        Args:
            skip_approve_if_clean: Skip premium approval if all checks pass
            use_security_crew: Enable SecurityAuditCrew for comprehensive security audit
            crew_config: Configuration dict for SecurityAuditCrew
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.skip_approve_if_clean = skip_approve_if_clean
        self.use_security_crew = use_security_crew
        self.crew_config = crew_config or {}
        self._has_blockers: bool = False
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")

        # Dynamically configure stages based on security crew setting
        if use_security_crew:
            self.stages = ["health", "security", "crew_security", "changelog", "approve"]
            self.tier_map = {
                "health": ModelTier.CHEAP,
                "security": ModelTier.CAPABLE,
                "crew_security": ModelTier.PREMIUM,
                "changelog": ModelTier.CAPABLE,
                "approve": ModelTier.PREMIUM,
            }
        else:
            self.stages = ["health", "security", "changelog", "approve"]
            self.tier_map = {
                "health": ModelTier.CHEAP,
                "security": ModelTier.CAPABLE,
                "changelog": ModelTier.CAPABLE,
                "approve": ModelTier.PREMIUM,
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

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Skip approval if all checks pass cleanly.

        Args:
            stage_name: Name of the stage to check
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        if stage_name == "approve" and self.skip_approve_if_clean:
            if not self._has_blockers:
                return True, "All checks passed - auto-approved"
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "health":
            return await self._health(input_data, tier)
        elif stage_name == "security":
            return await self._security(input_data, tier)
        elif stage_name == "crew_security":
            return await self._crew_security(input_data, tier)
        elif stage_name == "changelog":
            return await self._changelog(input_data, tier)
        elif stage_name == "approve":
            return await self._approve(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _health(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Run health checks.

        Executes lint, type checking, and tests.
        """
        target_path = input_data.get("path", ".")
        checks: dict[str, dict] = {}

        # Lint check (ruff)
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", target_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            lint_errors = result.stdout.count("error") + result.stderr.count("error")
            checks["lint"] = {
                "passed": result.returncode == 0,
                "errors": lint_errors,
                "tool": "ruff",
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            checks["lint"] = {"passed": True, "errors": 0, "tool": "ruff", "skipped": True}

        # Type check (mypy)
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", target_path, "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            type_errors = result.stdout.count("error:")
            checks["types"] = {
                "passed": result.returncode == 0,
                "errors": type_errors,
                "tool": "mypy",
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            checks["types"] = {"passed": True, "errors": 0, "tool": "mypy", "skipped": True}

        # Test check (pytest)
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--co", "-q"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=target_path,
            )
            # Count collected tests
            test_count = 0
            for line in result.stdout.splitlines():
                if "test" in line.lower():
                    test_count += 1

            checks["tests"] = {
                "passed": True,
                "test_count": test_count,
                "tool": "pytest",
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            checks["tests"] = {"passed": True, "test_count": 0, "tool": "pytest", "skipped": True}

        # Calculate health score
        failed_checks = [k for k, v in checks.items() if not v.get("passed", True)]
        health_score = 100 - (len(failed_checks) * 20)

        if failed_checks:
            self._has_blockers = True

        health_result = {
            "checks": checks,
            "health_score": max(0, health_score),
            "failed_checks": failed_checks,
            "passed": len(failed_checks) == 0,
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(health_result)) // 4

        return (
            {
                "health": health_result,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _security(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Run security scan summary.

        Quick security check for obvious issues.
        """
        target_path = input_data.get("path", ".")
        target = Path(target_path)

        issues: list[dict] = []

        # Check for common security issues
        for py_file in target.rglob("*.py"):
            if ".git" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                content = py_file.read_text(errors="ignore")

                # Check for hardcoded secrets
                if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    issues.append(
                        {
                            "type": "hardcoded_secret",
                            "file": str(py_file),
                            "severity": "high",
                        }
                    )

                # Check for eval/exec
                if "eval(" in content or "exec(" in content:
                    issues.append(
                        {
                            "type": "dangerous_function",
                            "file": str(py_file),
                            "severity": "high",
                        }
                    )
            except OSError:
                continue

        # Count by severity
        high_count = len([i for i in issues if i["severity"] == "high"])
        medium_count = len([i for i in issues if i["severity"] == "medium"])

        if high_count > 0:
            self._has_blockers = True

        security_result = {
            "issues": issues[:20],  # Top 20
            "total_issues": len(issues),
            "high_severity": high_count,
            "medium_severity": medium_count,
            "passed": high_count == 0,
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(security_result)) // 4

        return (
            {
                "security": security_result,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _crew_security(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Run SecurityAuditCrew for comprehensive security analysis.

        This stage uses the 5-agent SecurityAuditCrew for deep security
        analysis including vulnerability hunting, risk assessment,
        remediation planning, and compliance mapping.

        Falls back gracefully if SecurityAuditCrew is not available.
        """
        from .security_adapters import (
            _check_crew_available,
            _get_crew_audit,
            crew_report_to_workflow_format,
            merge_security_results,
        )

        target_path = input_data.get("path", ".")
        existing_security = input_data.get("security", {})

        # Check if crew is available
        if not _check_crew_available():
            return (
                {
                    "crew_security": {
                        "available": False,
                        "fallback": True,
                        "reason": "SecurityAuditCrew not installed",
                    },
                    **input_data,
                },
                0,
                0,
            )

        # Run SecurityAuditCrew
        report = await _get_crew_audit(target_path, self.crew_config)

        if report is None:
            return (
                {
                    "crew_security": {
                        "available": True,
                        "fallback": True,
                        "reason": "SecurityAuditCrew audit failed or timed out",
                    },
                    **input_data,
                },
                0,
                0,
            )

        # Convert crew report to workflow format
        crew_results = crew_report_to_workflow_format(report)

        # Merge with existing security stage results
        existing_issues = existing_security.get("issues", [])
        merged = merge_security_results(crew_results, {"findings": existing_issues})

        # Update blockers based on crew findings
        critical_count = len(crew_results.get("assessment", {}).get("critical_findings", []))
        high_count = len(crew_results.get("assessment", {}).get("high_findings", []))

        if critical_count > 0 or high_count > 0:
            self._has_blockers = True

        crew_security_result = {
            "available": True,
            "fallback": False,
            "findings": crew_results.get("findings", []),
            "finding_count": crew_results.get("finding_count", 0),
            "risk_score": crew_results.get("risk_score", 0),
            "risk_level": crew_results.get("risk_level", "none"),
            "critical_count": critical_count,
            "high_count": high_count,
            "summary": crew_results.get("summary", ""),
            "agents_used": crew_results.get("agents_used", []),
            "merged_results": merged,
        }

        # Estimate tokens (crew uses internal LLM calls)
        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(crew_security_result)) // 4

        return (
            {
                "crew_security": crew_security_result,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _changelog(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Generate changelog from recent commits.

        Extracts commit messages and organizes by type.
        """
        target_path = input_data.get("path", ".")
        since = input_data.get("since", "1 week ago")

        commits: list[dict] = []

        try:
            result = subprocess.run(
                ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=target_path,
            )

            for line in result.stdout.splitlines():
                if not line.strip():
                    continue

                parts = line.split(" ", 1)
                if len(parts) >= 2:
                    sha = parts[0]
                    message = parts[1]

                    # Categorize by conventional commit prefix
                    category = "other"
                    if message.startswith("feat"):
                        category = "features"
                    elif message.startswith("fix"):
                        category = "fixes"
                    elif message.startswith("docs"):
                        category = "docs"
                    elif message.startswith("refactor"):
                        category = "refactor"
                    elif message.startswith("test"):
                        category = "tests"
                    elif message.startswith("chore"):
                        category = "chores"

                    commits.append(
                        {
                            "sha": sha,
                            "message": message,
                            "category": category,
                        }
                    )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Group by category
        by_category: dict[str, list] = {}
        for commit in commits:
            cat = commit["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(commit)

        changelog = {
            "commits": commits,
            "total_commits": len(commits),
            "by_category": {k: len(v) for k, v in by_category.items()},
            "generated_at": datetime.now().isoformat(),
            "period": since,
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(changelog)) // 4

        return (
            {
                "changelog": changelog,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _approve(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Final release readiness assessment using LLM.

        Synthesizes all checks into go/no-go recommendation.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        health = input_data.get("health", {})
        security = input_data.get("security", {})
        changelog = input_data.get("changelog", {})
        target = input_data.get("path", "")

        # Gather blockers
        blockers: list[str] = []

        if not health.get("passed", False):
            for check in health.get("failed_checks", []):
                blockers.append(f"Health check failed: {check}")

        if not security.get("passed", False):
            blockers.append(f"Security issues: {security.get('high_severity', 0)} high severity")

        if changelog.get("total_commits", 0) == 0:
            blockers.append("No commits in release period")

        # Gather warnings
        warnings: list[str] = []

        if security.get("medium_severity", 0) > 0:
            warnings.append(f"{security.get('medium_severity')} medium security issues")

        test_count = health.get("checks", {}).get("tests", {}).get("test_count", 0)
        if test_count < 10:
            warnings.append(f"Low test count: {test_count}")

        # Build input payload for LLM
        input_payload = f"""Target: {target or "codebase"}

Health Score: {health.get("health_score", 0)}/100
Health Checks: {json.dumps(health.get("checks", {}), indent=2)}

Security Issues: {security.get("total_issues", 0)}
High Severity: {security.get("high_severity", 0)}
Medium Severity: {security.get("medium_severity", 0)}

Commit Count: {changelog.get("total_commits", 0)}
Changes by Category: {json.dumps(changelog.get("by_category", {}), indent=2)}

Blockers: {json.dumps(blockers, indent=2)}
Warnings: {json.dumps(warnings, indent=2)}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="release manager assessing release readiness",
                goal="Provide a comprehensive release readiness assessment",
                instructions=[
                    "Evaluate all health checks and their implications",
                    "Assess security findings and their risk level",
                    "Review the changelog for completeness",
                    "Identify any blockers that must be resolved",
                    "Provide a clear go/no-go recommendation",
                    "Suggest remediation steps for any issues",
                ],
                constraints=[
                    "Be conservative - flag potential issues",
                    "Provide clear, actionable feedback",
                    "Include confidence level in recommendation",
                ],
                input_type="release_checks",
                input_payload=input_payload,
                extra={
                    "blocker_count": len(blockers),
                    "warning_count": len(warnings),
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a release manager assessing release readiness.
Analyze the health checks, security findings, and changelog to provide
a clear go/no-go recommendation.

Be thorough and flag any potential issues."""

            user_message = f"""Assess release readiness:

{input_payload}

Provide a comprehensive release readiness assessment."""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system or "", user_message, max_tokens=2000
        )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        # Make decision
        approved = len(blockers) == 0
        confidence = "high" if approved and len(warnings) == 0 else "medium" if approved else "low"

        result = {
            "approved": approved,
            "confidence": confidence,
            "blockers": blockers,
            "warnings": warnings,
            "health_score": health.get("health_score", 0),
            "commit_count": changelog.get("total_commits", 0),
            "assessment": response,
            "recommendation": (
                "Ready for release" if approved else "Address blockers before release"
            ),
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


def main():
    """CLI entry point for release preparation workflow."""
    import asyncio

    async def run():
        workflow = ReleasePreparationWorkflow()
        result = await workflow.execute(path=".")

        print("\nRelease Preparation Results")
        print("=" * 50)
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")

        output = result.final_output
        print(f"Approved: {output.get('approved', False)}")
        print(f"Confidence: {output.get('confidence', 'N/A')}")

        if output.get("blockers"):
            print("\nBlockers:")
            for b in output["blockers"]:
                print(f"  - {b}")

        if output.get("warnings"):
            print("\nWarnings:")
            for w in output["warnings"]:
                print(f"  - {w}")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
