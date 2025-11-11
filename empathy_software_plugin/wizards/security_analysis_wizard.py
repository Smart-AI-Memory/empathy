"""
Security Analysis Wizard (Level 4)

Predicts which security vulnerabilities are actually exploitable.

Level 4: Anticipatory - identifies real security risks, not just theoretical ones.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
from pathlib import Path
from typing import Any

from .base_wizard import BaseWizard
from .security.exploit_analyzer import ExploitabilityAssessment, ExploitAnalyzer
from .security.owasp_patterns import OWASPPatternDetector

logger = logging.getLogger(__name__)


class SecurityAnalysisWizard(BaseWizard):
    """
    Security Analysis Wizard - Level 4

    Beyond finding vulnerabilities:
    - Predicts which are actually exploitable
    - Assesses real-world attack likelihood
    - Prioritizes by actual risk (not just CVSS)
    - Experience-based recommendations
    """

    @property
    def name(self) -> str:
        return "Security Analysis Wizard"

    @property
    def level(self) -> int:
        return 4

    def __init__(self):
        super().__init__()

        self.pattern_detector = OWASPPatternDetector()
        self.exploit_analyzer = ExploitAnalyzer()

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze code for security vulnerabilities.

        Context expects:
            - source_files: List of source file paths to scan
            - project_path: Project root (optional)
            - endpoint_config: Endpoint exposure info (optional)
            - exclude_patterns: Patterns to exclude (optional)

        Returns:
            Analysis with vulnerabilities, exploitability, predictions
        """
        source_files = context.get("source_files", [])
        project_path = context.get("project_path", ".")
        endpoint_config = context.get("endpoint_config", {})
        exclude_patterns = context.get("exclude_patterns", [])

        if not source_files:
            source_files = self._discover_source_files(project_path, exclude_patterns)

        # Phase 1: Detect vulnerabilities
        all_vulnerabilities = []

        for source_file in source_files[:100]:  # Limit for performance
            try:
                with open(source_file) as f:
                    code = f.read()

                vulns = self.pattern_detector.detect_vulnerabilities(code, source_file)

                all_vulnerabilities.extend(vulns)

            except Exception as e:
                logger.warning(f"Could not scan {source_file}: {e}")

        # Phase 2: Assess exploitability (Level 4)
        exploitability_assessments = []

        for vuln in all_vulnerabilities:
            # Get endpoint context if available
            file_path = vuln.get("file_path", "")
            endpoint_context = endpoint_config.get(file_path, {})

            assessment = self.exploit_analyzer.assess_exploitability(vuln, endpoint_context)

            exploitability_assessments.append(assessment)

        # Sort by exploitability
        exploitability_assessments.sort(
            key=lambda a: (
                {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(a.exploitability, 4),
                -a.exploit_likelihood,
            )
        )

        # Phase 3: Generate insights
        insights = self._generate_insights(all_vulnerabilities, exploitability_assessments)

        # Phase 4: Predictions (Level 4)
        predictions = self._generate_predictions(exploitability_assessments, insights)

        # Phase 5: Recommendations
        recommendations = self._generate_recommendations(exploitability_assessments, insights)

        return {
            "vulnerabilities_found": len(all_vulnerabilities),
            "by_severity": self._group_by_severity(all_vulnerabilities),
            "by_category": self._group_by_category(all_vulnerabilities),
            "exploitability_assessments": [
                {
                    "vulnerability": a.vulnerability,
                    "exploitability": a.exploitability,
                    "accessibility": a.accessibility,
                    "attack_complexity": a.attack_complexity,
                    "exploit_likelihood": a.exploit_likelihood,
                    "reasoning": a.reasoning,
                    "mitigation_urgency": a.mitigation_urgency,
                }
                for a in exploitability_assessments
            ],
            "insights": insights,
            # Standard wizard outputs
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": 0.85,
        }

    def _discover_source_files(self, project_path: str, exclude_patterns: list[str]) -> list[str]:
        """Discover source files to scan"""
        source_files = []
        project = Path(project_path)

        # Common source file extensions
        extensions = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.go", "*.rb"]

        for ext in extensions:
            for file in project.rglob(ext):
                # Skip excluded patterns
                if any(pattern in str(file) for pattern in exclude_patterns):
                    continue

                # Skip test files and dependencies
                if any(
                    p in str(file) for p in ["/test/", "/tests/", "node_modules", "venv", ".git"]
                ):
                    continue

                source_files.append(str(file))

        return source_files[:200]  # Limit for performance

    def _group_by_severity(self, vulnerabilities: list[dict[str, Any]]) -> dict[str, int]:
        """Group vulnerabilities by severity"""
        by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "MEDIUM")
            if severity in by_severity:
                by_severity[severity] += 1

        return by_severity

    def _group_by_category(self, vulnerabilities: list[dict[str, Any]]) -> dict[str, int]:
        """Group vulnerabilities by OWASP category"""
        by_category = {}

        for vuln in vulnerabilities:
            category = vuln.get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1

        return by_category

    def _generate_insights(
        self, vulnerabilities: list[dict[str, Any]], assessments: list[ExploitabilityAssessment]
    ) -> dict[str, Any]:
        """Generate security insights"""

        # Most common vulnerability type
        by_category = self._group_by_category(vulnerabilities)
        most_common = max(by_category.items(), key=lambda x: x[1])[0] if by_category else "none"

        # Percentage actually exploitable
        critical_exploitable = sum(1 for a in assessments if a.exploitability == "CRITICAL")
        high_exploitable = sum(1 for a in assessments if a.exploitability == "HIGH")

        total = len(assessments)
        exploitable_percent = (
            ((critical_exploitable + high_exploitable) / total * 100) if total > 0 else 0
        )

        return {
            "most_common_category": most_common,
            "critical_exploitable": critical_exploitable,
            "high_exploitable": high_exploitable,
            "exploitable_percent": exploitable_percent,
            "public_exposure": sum(1 for a in assessments if a.accessibility == "public"),
            "immediate_action_required": sum(
                1 for a in assessments if "IMMEDIATE" in a.mitigation_urgency
            ),
        }

    def _generate_predictions(
        self, assessments: list[ExploitabilityAssessment], insights: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate Level 4 predictions"""

        predictions = []

        # Prediction 1: Imminent exploitation risk
        immediate_risks = [a for a in assessments if "IMMEDIATE" in a.mitigation_urgency]
        if immediate_risks:
            predictions.append(
                {
                    "type": "imminent_exploitation_risk",
                    "severity": "critical",
                    "description": (
                        f"{len(immediate_risks)} vulnerabilities have IMMEDIATE exploitation risk. "
                        f"In our experience, {immediate_risks[0].vulnerability['name']} "
                        f"is actively scanned by automated tools."
                    ),
                    "affected_files": [a.vulnerability["file_path"] for a in immediate_risks[:3]],
                    "prevention_steps": [
                        a.vulnerability.get("example_safe", "Fix vulnerability")
                        for a in immediate_risks[:3]
                    ],
                }
            )

        # Prediction 2: Public exposure risk
        public_critical = [
            a
            for a in assessments
            if a.accessibility == "public" and a.exploitability in ["CRITICAL", "HIGH"]
        ]
        if public_critical:
            predictions.append(
                {
                    "type": "public_exposure_risk",
                    "severity": "high",
                    "description": (
                        f"{len(public_critical)} publicly accessible vulnerabilities detected. "
                        "In our experience, public endpoints are scanned within hours of deployment."
                    ),
                    "prevention_steps": [
                        "Add authentication to sensitive endpoints",
                        "Implement rate limiting",
                        "Add input validation",
                    ],
                }
            )

        # Prediction 3: Attack pattern concentration
        if insights["most_common_category"] in ["injection", "broken_authentication"]:
            predictions.append(
                {
                    "type": "attack_pattern_concentration",
                    "severity": "high",
                    "description": (
                        f"Multiple {insights['most_common_category']} vulnerabilities detected. "
                        "In our experience, clustered vulnerabilities indicate systematic issues."
                    ),
                    "prevention_steps": [
                        "Review coding standards",
                        "Add automated security scanning to CI/CD",
                        "Conduct security training",
                    ],
                }
            )

        return predictions

    def _generate_recommendations(
        self, assessments: list[ExploitabilityAssessment], insights: dict[str, Any]
    ) -> list[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Immediate actions
        if insights["immediate_action_required"] > 0:
            recommendations.append(
                f"🚨 CRITICAL: Fix {insights['immediate_action_required']} "
                "vulnerabilities BEFORE next deployment"
            )

        # Category-specific recommendations
        if insights["most_common_category"] == "injection":
            recommendations.append("Use parameterized queries for ALL database operations")
            recommendations.append("Add input validation library (e.g., validator.js, bleach)")

        if insights["most_common_category"] == "cross_site_scripting":
            recommendations.append("Use textContent instead of innerHTML")
            recommendations.append("Implement Content Security Policy (CSP) headers")

        # Public exposure recommendations
        if insights["public_exposure"] > 0:
            recommendations.append(
                f"{insights['public_exposure']} publicly exposed endpoints - "
                "Add authentication and rate limiting"
            )

        # Top priority fixes
        for assessment in assessments[:3]:
            if assessment.exploitability in ["CRITICAL", "HIGH"]:
                vuln = assessment.vulnerability
                recommendations.append(
                    f"{assessment.exploitability}: {vuln['name']} in {Path(vuln['file_path']).name}:{vuln['line_number']}"
                )

        # General best practices
        recommendations.append("Add pre-commit security scanning (e.g., bandit, safety, npm audit)")

        return recommendations
