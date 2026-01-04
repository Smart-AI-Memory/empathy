"""Security Learning Wizard (Level 4)

Security analysis wizard that learns from team decisions.
Demonstrates what's possible with persistent memory: AI that remembers
which warnings are false positives and team security policies.

"Suppressing 8 warnings you've previously marked as acceptable."

Key capabilities enabled by persistent memory:
- False positive learning
- Team security policy accumulation
- Context-aware severity adjustment
- Historical vulnerability tracking

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_wizard import BaseWizard

logger = logging.getLogger(__name__)


@dataclass
class SecurityFinding:
    """A security finding from scanning"""

    finding_id: str
    file_path: str
    line_number: int
    vulnerability_type: str
    severity: str  # critical, high, medium, low, info
    description: str
    code_snippet: str
    owasp_category: str | None = None


@dataclass
class TeamDecision:
    """A team's decision about a security finding"""

    finding_hash: str  # Hash of the finding pattern
    decision: str  # accepted, false_positive, deferred, fixed
    reason: str
    decided_by: str
    decided_at: str
    applies_to: str  # "all", "file", "pattern"
    expiration: str | None = None  # Optional expiration date


@dataclass
class LearningResult:
    """Result of applying learned patterns to findings"""

    total_findings: int
    suppressed_count: int
    adjusted_count: int
    new_findings: int
    suppression_details: list[dict[str, Any]] = field(default_factory=list)


class SecurityLearningWizard(BaseWizard):
    """Security Learning Wizard - Level 4 with Team Knowledge

    What's now possible that wasn't before:

    WITHOUT PERSISTENT MEMORY (Before):
    - Same false positives flagged every scan
    - No learning from team decisions
    - Security fatigue from noise
    - Lost context about accepted risks

    WITH PERSISTENT MEMORY (After):
    - AI remembers team decisions
    - False positives automatically suppressed
    - Context preserved: "Accepted by @sarah on 2025-09-15 because..."
    - Security debt tracked over time

    Example:
        >>> wizard = SecurityLearningWizard()
        >>> result = await wizard.analyze({
        ...     "project_path": ".",
        ...     "apply_learned_patterns": True
        ... })
        >>> print(result["learning_applied"]["suppressed_count"])
        # Shows how many warnings were suppressed based on team decisions

    """

    @property
    def name(self) -> str:
        return "Security Learning Wizard"

    @property
    def level(self) -> int:
        return 4

    def __init__(self, pattern_storage_path: str = "./patterns/security"):
        """Initialize the security learning wizard.

        Args:
            pattern_storage_path: Path to git-based pattern storage

        """
        super().__init__()
        self.pattern_storage_path = Path(pattern_storage_path)
        self.pattern_storage_path.mkdir(parents=True, exist_ok=True)

        # Vulnerability detection patterns
        self.vulnerability_patterns = {
            "sql_injection": {
                "patterns": [
                    r"execute\s*\(\s*['\"].*%s.*['\"]",
                    r"cursor\.execute\s*\(\s*f['\"]",
                    r"\.query\s*\(\s*['\"].*\+",
                    r"SELECT.*\+.*WHERE",
                ],
                "owasp": "A03:2021",
                "severity": "high",
            },
            "xss": {
                "patterns": [
                    r"innerHTML\s*=",
                    r"document\.write\s*\(",
                    r"\.html\s*\(\s*[^)]*\$",
                    r"dangerouslySetInnerHTML",
                ],
                "owasp": "A03:2021",
                "severity": "high",
            },
            "hardcoded_secret": {
                "patterns": [
                    r"password\s*=\s*['\"][^'\"]+['\"]",
                    r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
                    r"secret\s*=\s*['\"][^'\"]+['\"]",
                    r"token\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]",
                ],
                "owasp": "A07:2021",
                "severity": "critical",
            },
            "insecure_random": {
                "patterns": [
                    r"Math\.random\s*\(",
                    r"random\.random\s*\(",
                    r"rand\s*\(",
                ],
                "owasp": "A02:2021",
                "severity": "medium",
            },
            "path_traversal": {
                "patterns": [
                    r"open\s*\([^)]*\+",
                    r"readFile\s*\([^)]*\+",
                    r"\.\.\/",
                ],
                "owasp": "A01:2021",
                "severity": "high",
            },
            "command_injection": {
                "patterns": [
                    r"exec\s*\([^)]*\+",
                    r"system\s*\([^)]*\+",
                    r"subprocess.*shell\s*=\s*True",
                    r"eval\s*\(",
                ],
                "owasp": "A03:2021",
                "severity": "critical",
            },
        }

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze project security with learned patterns.

        Context expects:
            - project_path: Path to the project
            - apply_learned_patterns: Apply team decisions (default True)
            - exclude_patterns: Patterns to exclude
            - scan_depth: "quick", "standard", "thorough" (default "standard")

        Returns:
            Analysis with:
            - findings: Security findings (after learning applied)
            - learning_applied: Summary of learned suppressions
            - raw_findings: All findings before learning
            - predictions: Level 4 predictions
            - recommendations: Actionable steps

        """
        project_path = Path(context.get("project_path", "."))
        apply_learning = context.get("apply_learned_patterns", True)
        exclude_patterns = context.get(
            "exclude_patterns",
            ["node_modules", "venv", ".git", "__pycache__", "test", "tests"],
        )
        scan_depth = context.get("scan_depth", "standard")

        # Step 1: Scan for vulnerabilities
        raw_findings = await self._scan_for_vulnerabilities(
            project_path,
            exclude_patterns,
            scan_depth,
        )

        # Step 2: Load team decisions
        team_decisions = self._load_team_decisions()

        # Step 3: Apply learned patterns
        learning_result = None
        filtered_findings = raw_findings

        if apply_learning:
            learning_result = self._apply_learned_patterns(raw_findings, team_decisions)
            filtered_findings = [
                f
                for f in raw_findings
                if f.finding_id
                not in [d["finding_id"] for d in learning_result.suppression_details]
            ]

        # Step 4: Group findings by severity
        by_severity = self._group_by_severity(filtered_findings)

        # Step 5: Generate predictions (Level 4)
        predictions = self._generate_predictions(filtered_findings, raw_findings, team_decisions)

        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(
            filtered_findings,
            learning_result,
            team_decisions,
        )

        return {
            "findings": [
                {
                    "id": f.finding_id,
                    "file": f.file_path,
                    "line": f.line_number,
                    "type": f.vulnerability_type,
                    "severity": f.severity,
                    "description": f.description,
                    "owasp": f.owasp_category,
                    "code_preview": f.code_snippet[:80],
                }
                for f in filtered_findings[:50]  # Top 50
            ],
            "summary": {
                "total_after_learning": len(filtered_findings),
                "by_severity": by_severity,
            },
            "learning_applied": (
                {
                    "enabled": True,
                    "total_raw_findings": learning_result.total_findings,
                    "suppressed_count": learning_result.suppressed_count,
                    "new_findings": learning_result.new_findings,
                    "noise_reduction_percent": (
                        round(
                            (learning_result.suppressed_count / learning_result.total_findings)
                            * 100,
                            1,
                        )
                        if learning_result.total_findings > 0
                        else 0
                    ),
                    "suppression_details": learning_result.suppression_details[:10],
                }
                if learning_result
                else {"enabled": False}
            ),
            "raw_findings_count": len(raw_findings),
            "team_decisions_count": len(team_decisions),
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": 0.85,
            "memory_benefit": self._calculate_memory_benefit(learning_result, team_decisions),
        }

    async def _scan_for_vulnerabilities(
        self,
        project_path: Path,
        exclude_patterns: list[str],
        scan_depth: str,
    ) -> list[SecurityFinding]:
        """Scan project for security vulnerabilities"""
        findings = []

        # File extensions to scan
        extensions = ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.java", "*.go", "*.rb"]

        # Adjust file limit based on scan depth
        file_limits = {"quick": 50, "standard": 200, "thorough": 1000}
        file_limit = file_limits.get(scan_depth, 200)

        files_scanned = 0
        for ext in extensions:
            for file_path in project_path.rglob(ext):
                if files_scanned >= file_limit:
                    break

                # Skip excluded patterns
                if any(exclude in str(file_path) for exclude in exclude_patterns):
                    continue

                try:
                    findings.extend(self._scan_file(file_path))
                    files_scanned += 1
                except (OSError, UnicodeDecodeError) as e:
                    logger.debug(f"Could not scan {file_path}: {e}")
                    continue

        return findings

    def _scan_file(self, file_path: Path) -> list[SecurityFinding]:
        """Scan a single file for vulnerabilities"""
        findings = []

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            for vuln_type, config in self.vulnerability_patterns.items():
                for pattern in config["patterns"]:
                    if re.search(pattern, line, re.IGNORECASE):
                        finding = SecurityFinding(
                            finding_id=self._generate_finding_id(file_path, line_num, vuln_type),
                            file_path=str(file_path),
                            line_number=line_num,
                            vulnerability_type=vuln_type,
                            severity=str(config["severity"]),
                            description=self._get_description(vuln_type),
                            code_snippet=line.strip(),
                            owasp_category=str(config["owasp"]) if config.get("owasp") else None,
                        )
                        findings.append(finding)
                        break  # One finding per line per type

        return findings

    def _generate_finding_id(self, file_path: Path, line_number: int, vuln_type: str) -> str:
        """Generate a stable finding ID"""
        content = f"{file_path}:{line_number}:{vuln_type}"
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:12]

    def _get_description(self, vuln_type: str) -> str:
        """Get description for vulnerability type"""
        descriptions = {
            "sql_injection": "Potential SQL injection - user input may reach query",
            "xss": "Potential XSS vulnerability - unsanitized content in DOM",
            "hardcoded_secret": "Hardcoded credential or secret detected",
            "insecure_random": "Cryptographically weak random number generator",
            "path_traversal": "Potential path traversal - file path from user input",
            "command_injection": "Potential command injection - shell execution with input",
        }
        return descriptions.get(vuln_type, f"Potential {vuln_type} vulnerability")

    def _load_team_decisions(self) -> list[TeamDecision]:
        """Load team decisions from pattern storage"""
        decisions = []
        decisions_file = self.pattern_storage_path / "team_decisions.json"

        if decisions_file.exists():
            try:
                with open(decisions_file, encoding="utf-8") as f:
                    data = json.load(f)

                for decision_data in data.get("decisions", []):
                    # Skip expired decisions
                    if decision_data.get("expiration"):
                        exp_date = datetime.fromisoformat(
                            decision_data["expiration"].replace("Z", ""),
                        )
                        if exp_date < datetime.now():
                            continue

                    decisions.append(
                        TeamDecision(
                            finding_hash=decision_data["finding_hash"],
                            decision=decision_data["decision"],
                            reason=decision_data["reason"],
                            decided_by=decision_data["decided_by"],
                            decided_at=decision_data["decided_at"],
                            applies_to=decision_data.get("applies_to", "pattern"),
                            expiration=decision_data.get("expiration"),
                        ),
                    )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not load team decisions: {e}")

        return decisions

    def _apply_learned_patterns(
        self,
        findings: list[SecurityFinding],
        decisions: list[TeamDecision],
    ) -> LearningResult:
        """Apply team decisions to filter findings"""
        suppression_details = []
        suppressed_ids = set()

        for finding in findings:
            # Check if there's a decision for this finding pattern
            finding_hash = self._hash_finding_pattern(finding)

            for decision in decisions:
                if self._decision_matches(finding, finding_hash, decision):
                    if decision.decision in ["accepted", "false_positive"]:
                        suppression_details.append(
                            {
                                "finding_id": finding.finding_id,
                                "type": finding.vulnerability_type,
                                "file": finding.file_path,
                                "decision": decision.decision,
                                "reason": decision.reason,
                                "decided_by": decision.decided_by,
                                "decided_at": decision.decided_at,
                            },
                        )
                        suppressed_ids.add(finding.finding_id)
                    break

        return LearningResult(
            total_findings=len(findings),
            suppressed_count=len(suppression_details),
            adjusted_count=0,
            new_findings=len(findings) - len(suppression_details),
            suppression_details=suppression_details,
        )

    def _hash_finding_pattern(self, finding: SecurityFinding) -> str:
        """Create a hash that identifies the pattern (not specific location)"""
        # Hash based on vulnerability type and code pattern (not line number)
        pattern_content = f"{finding.vulnerability_type}:{finding.code_snippet.strip()}"
        return hashlib.md5(pattern_content.encode(), usedforsecurity=False).hexdigest()[:16]

    def _decision_matches(
        self,
        finding: SecurityFinding,
        finding_hash: str,
        decision: TeamDecision,
    ) -> bool:
        """Check if a decision applies to a finding"""
        if decision.applies_to == "all":
            # Decision applies to all findings of this type
            return decision.finding_hash.startswith(finding.vulnerability_type)

        if decision.applies_to == "file":
            # Decision applies to all findings in a specific file
            return decision.finding_hash == finding.file_path

        # Default: pattern match
        return decision.finding_hash == finding_hash

    def _group_by_severity(self, findings: list[SecurityFinding]) -> dict[str, int]:
        """Group findings by severity"""
        by_severity: dict[str, int] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for finding in findings:
            if finding.severity in by_severity:
                by_severity[finding.severity] += 1

        return by_severity

    def _generate_predictions(
        self,
        filtered_findings: list[SecurityFinding],
        raw_findings: list[SecurityFinding],
        team_decisions: list[TeamDecision],
    ) -> list[dict[str, Any]]:
        """Generate Level 4 predictions"""
        predictions = []

        # Prediction 1: Critical vulnerability warning
        critical_count = sum(1 for f in filtered_findings if f.severity == "critical")
        if critical_count > 0:
            predictions.append(
                {
                    "type": "critical_vulnerabilities",
                    "severity": "critical",
                    "description": (
                        f"{critical_count} critical vulnerabilities detected. "
                        "In our experience, these are actively exploited in the wild."
                    ),
                    "prevention_steps": [
                        "Fix before deployment",
                        "Add to security review checklist",
                        "Consider automated blocking in CI/CD",
                    ],
                },
            )

        # Prediction 2: Pattern concentration
        vuln_types = [f.vulnerability_type for f in filtered_findings]
        if vuln_types:
            most_common = max(set(vuln_types), key=vuln_types.count)
            count = vuln_types.count(most_common)
            if count >= 3:
                predictions.append(
                    {
                        "type": "pattern_concentration",
                        "severity": "high",
                        "description": (
                            f"{count} instances of {most_common} detected. "
                            "Clustered vulnerabilities suggest systematic issue."
                        ),
                        "prevention_steps": [
                            f"Add linting rule for {most_common}",
                            "Review coding patterns team-wide",
                            "Consider security training",
                        ],
                    },
                )

        # Prediction 3: Learning effectiveness
        if len(raw_findings) > 0 and len(team_decisions) > 0:
            suppression_rate = (len(raw_findings) - len(filtered_findings)) / len(raw_findings)
            if suppression_rate > 0.3:
                predictions.append(
                    {
                        "type": "learning_effective",
                        "severity": "info",
                        "description": (
                            f"Team decisions reduced noise by {int(suppression_rate * 100)}%. "
                            "Persistent memory is working."
                        ),
                        "prevention_steps": ["Continue documenting decisions"],
                    },
                )

        # Prediction 4: Aging decisions warning
        old_decisions = [
            d
            for d in team_decisions
            if (datetime.now() - datetime.fromisoformat(d.decided_at.replace("Z", ""))).days > 180
        ]
        if old_decisions:
            predictions.append(
                {
                    "type": "aging_decisions",
                    "severity": "medium",
                    "description": (
                        f"{len(old_decisions)} security decisions are over 6 months old. "
                        "Consider reviewing if they're still valid."
                    ),
                    "prevention_steps": [
                        "Review accepted risks quarterly",
                        "Set expiration dates on decisions",
                        "Re-evaluate in context of new threats",
                    ],
                },
            )

        return predictions

    def _generate_recommendations(
        self,
        filtered_findings: list[SecurityFinding],
        learning_result: LearningResult | None,
        team_decisions: list[TeamDecision],
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Severity-based recommendations
        critical_count = sum(1 for f in filtered_findings if f.severity == "critical")
        high_count = sum(1 for f in filtered_findings if f.severity == "high")

        if critical_count > 0:
            recommendations.append(
                f"🚨 {critical_count} CRITICAL vulnerabilities - block deployment until fixed",
            )

        if high_count > 0:
            recommendations.append(
                f"⚠️  {high_count} HIGH severity findings - prioritize for next sprint",
            )

        # Learning-based recommendations
        if learning_result and learning_result.suppressed_count > 0:
            recommendations.append(
                f"✅ {learning_result.suppressed_count} findings suppressed by team decisions "
                f"(reducing noise by {int(learning_result.suppressed_count / learning_result.total_findings * 100)}%)",
            )

        # Help build knowledge base
        new_types = {f.vulnerability_type for f in filtered_findings}
        if new_types and len(team_decisions) < 10:
            recommendations.append(
                "💡 Tip: After reviewing, use record_decision() to teach the wizard",
            )

        # Memory benefit
        if team_decisions:
            recommendations.append(
                f"📚 Using {len(team_decisions)} team security decisions from memory",
            )
        else:
            recommendations.append(
                "💾 No team decisions recorded yet - start building security knowledge base",
            )

        return recommendations

    def _calculate_memory_benefit(
        self,
        learning_result: LearningResult | None,
        team_decisions: list[TeamDecision],
    ) -> dict[str, Any]:
        """Calculate the benefit provided by persistent memory"""
        if not team_decisions:
            return {
                "decisions_available": False,
                "value_statement": (
                    "No team decisions recorded yet. "
                    "Use record_decision() to start building your security knowledge base."
                ),
                "noise_reduction": "N/A",
            }

        suppressed = learning_result.suppressed_count if learning_result else 0
        total = learning_result.total_findings if learning_result else 0

        return {
            "decisions_available": True,
            "decisions_count": len(team_decisions),
            "findings_suppressed": suppressed,
            "noise_reduction_percent": (round((suppressed / total) * 100, 1) if total > 0 else 0),
            "value_statement": (
                f"Persistent memory applied {len(team_decisions)} team decisions, "
                f"suppressing {suppressed} warnings. "
                "Without memory, you'd review the same false positives every scan."
            ),
            "oldest_decision": min((d.decided_at for d in team_decisions), default="N/A"),
        }

    async def record_decision(
        self,
        finding: dict[str, Any],
        decision: str,
        reason: str,
        decided_by: str,
        applies_to: str = "pattern",
        expiration_days: int | None = None,
    ) -> bool:
        """Record a team decision about a security finding.

        Call this after reviewing a finding to teach the wizard.

        Args:
            finding: The finding dict from analyze results
            decision: "accepted", "false_positive", "deferred", "fixed"
            reason: Why this decision was made
            decided_by: Who made the decision (e.g., "@sarah")
            applies_to: "pattern" (this specific pattern), "file", or "all" (all of this type)
            expiration_days: Optional days until decision expires

        Returns:
            True if recorded successfully

        Example:
            >>> await wizard.record_decision(
            ...     finding=results["findings"][0],
            ...     decision="false_positive",
            ...     reason="ORM handles SQL escaping, not vulnerable",
            ...     decided_by="@sarah",
            ...     applies_to="pattern"
            ... )

        """
        decisions_file = self.pattern_storage_path / "team_decisions.json"

        # Load existing decisions
        decisions_data: dict[str, list[dict]] = {"decisions": []}
        if decisions_file.exists():
            try:
                with open(decisions_file, encoding="utf-8") as f:
                    decisions_data = json.load(f)
            except json.JSONDecodeError:
                pass

        # Create finding hash based on applies_to
        if applies_to == "all":
            finding_hash = finding.get("type", "unknown")
        elif applies_to == "file":
            finding_hash = finding.get("file", "unknown")
        else:
            # Pattern-based hash
            pattern_content = f"{finding.get('type')}:{finding.get('code_preview', '')}"
            finding_hash = hashlib.md5(pattern_content.encode(), usedforsecurity=False).hexdigest()[
                :16
            ]

        # Create decision record
        expiration = None
        if expiration_days:
            from datetime import timedelta

            expiration = (datetime.now() + timedelta(days=expiration_days)).isoformat()

        new_decision = {
            "finding_hash": finding_hash,
            "decision": decision,
            "reason": reason,
            "decided_by": decided_by,
            "decided_at": datetime.now().isoformat(),
            "applies_to": applies_to,
            "expiration": expiration,
            "original_finding": {
                "type": finding.get("type"),
                "file": finding.get("file"),
                "severity": finding.get("severity"),
            },
        }

        decisions_data["decisions"].append(new_decision)

        # Store
        try:
            with open(decisions_file, "w", encoding="utf-8") as f:
                json.dump(decisions_data, f, indent=2)
            logger.info(f"Recorded security decision: {decision} for {finding.get('type')}")
            return True
        except OSError as e:
            logger.error(f"Could not record decision: {e}")
            return False
