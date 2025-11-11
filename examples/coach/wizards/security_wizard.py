"""
Security Wizard

Conducts security reviews, identifies vulnerabilities, and creates security checklists.
Uses Empathy Framework Level 4 (Anticipatory) to prevent future security incidents
and Level 3 (Proactive) to identify security patterns.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from .base_wizard import (
    BaseWizard,
    EmpathyChecks,
    WizardArtifact,
    WizardHandoff,
    WizardOutput,
    WizardRisk,
    WizardTask,
)


class SecurityWizard(BaseWizard):
    """
    Wizard for security analysis and vulnerability assessment

    Uses:
    - Level 3: Proactively identify security patterns and anti-patterns
    - Level 4: Anticipate attack vectors and security incidents
    - Level 5: Systems thinking for defense-in-depth
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a security task"""
        # High-priority security phrases (should match strongly)
        security_phrases = [
            "penetration test",
            "penetration testing",
            "pentest",
            "security audit",
            "security review",
            "vulnerability scan",
            "threat model",
            "sql injection",
            "xss",
            "csrf",
            "owasp",
        ]

        security_keywords = [
            "security",
            "vulnerability",
            "vuln",
            "exploit",
            "attack",
            "breach",
            "penetration",
            "threat",
            "risk assessment",
            "compliance",
            "authentication",
            "authorization",
            "encryption",
        ]

        task_lower = (task.task + " " + task.context).lower()

        # Check for high-priority security phrases first (worth 2 points each)
        phrase_matches = sum(2 for phrase in security_phrases if phrase in task_lower)

        # Check for individual keywords (worth 1 point each)
        keyword_matches = sum(1 for keyword in security_keywords if keyword in task_lower)

        total_score = phrase_matches + keyword_matches

        # Score capped at 1.0, but phrase matches ensure higher priority than generic "testing" keyword
        # For "penetration testing": phrase_matches=2*2=4, keyword_matches=2 ("penetration", "security"), total=6/2=3.0 -> 1.0
        # This ensures security-specific phrases score max even with higher threshold
        return min(total_score / 2.0, 1.0)  # 2+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute security review workflow"""

        # Step 1: Assess context
        constraints = self._extract_constraints(task)
        emotional_state = self._assess_emotional_state(task)

        # Step 2: Identify security scope
        security_scope = self._identify_security_scope(task)

        # Step 3: Conduct threat modeling (Level 4: Anticipatory)
        threat_model = self._conduct_threat_modeling(task, security_scope)

        # Step 4: Identify vulnerabilities (Level 3: Proactive)
        vulnerabilities = self._identify_vulnerabilities(task, security_scope)

        # Step 5: Assess compliance requirements
        compliance = self._assess_compliance(task, security_scope)

        # Step 6: Generate security checklist
        security_checklist = self._generate_security_checklist(
            security_scope, vulnerabilities, compliance
        )

        # Step 7: Create diagnosis
        diagnosis = self._create_diagnosis(security_scope, vulnerabilities, threat_model)

        # Step 8: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc", title="Threat Model", content=self._format_threat_model(threat_model)
            ),
            WizardArtifact(
                type="doc",
                title="Vulnerability Assessment",
                content=self._format_vulnerabilities(vulnerabilities),
            ),
            WizardArtifact(
                type="checklist", title="Security Checklist", content=security_checklist
            ),
            WizardArtifact(
                type="doc",
                title="Security Recommendations",
                content=self._generate_recommendations(vulnerabilities, threat_model),
            ),
        ]

        # Step 9: Create plan
        plan = [
            "Conduct threat modeling workshop",
            f"Address {len(vulnerabilities)} identified vulnerabilities",
            "Implement security controls",
            "Set up security monitoring",
            "Document security procedures",
            "Schedule regular security reviews",
        ]

        # Step 10: Generate next actions
        next_actions = [
            "Fix critical vulnerabilities immediately",
            "Implement automated security scanning",
            "Add security tests to CI/CD",
            "Update security documentation",
            "Train team on secure coding practices",
        ]

        # Add anticipatory actions
        anticipatory_actions = self._generate_anticipatory_actions(task)
        next_actions.extend(anticipatory_actions)

        # Step 11: Create handoffs
        handoffs = []
        if vulnerabilities:
            handoffs.append(
                WizardHandoff(
                    owner="security_team",
                    what="Review and validate security fixes",
                    when="Before deployment",
                )
            )
        if compliance:
            handoffs.append(
                WizardHandoff(
                    owner="compliance_officer",
                    what="Verify compliance requirements met",
                    when="Before go-live",
                )
            )

        # Step 12: Assess risks
        risks = self._assess_security_risks(task, vulnerabilities, threat_model)

        # Step 13: Empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role} security knowledge level and {security_scope['system_type']} system constraints",
            emotional=f"Acknowledged {'high stress' if len(vulnerabilities) > 3 else 'normal concern'} around security issues",
            anticipatory=f"Identified {len(threat_model['threats'])} potential threats and {len(anticipatory_actions)} preventive measures",
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=plan,
            artifacts=artifacts,
            risks=risks,
            handoffs=handoffs,
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _identify_security_scope(self, task: WizardTask) -> dict[str, Any]:
        """Identify security review scope"""
        context_lower = task.context.lower()

        # Identify system type
        system_type = "web_application"
        if "api" in context_lower:
            system_type = "api"
        elif "mobile" in context_lower:
            system_type = "mobile_app"
        elif "cloud" in context_lower or "aws" in context_lower or "azure" in context_lower:
            system_type = "cloud_infrastructure"

        # Identify assets
        assets = []
        if "user data" in context_lower or "pii" in context_lower:
            assets.append("User personal data")
        if "payment" in context_lower or "credit card" in context_lower:
            assets.append("Payment information")
        if "health" in context_lower or "medical" in context_lower:
            assets.append("Health records")
        if "database" in context_lower:
            assets.append("Database")

        # Identify attack surface
        attack_surface = []
        if "public" in context_lower or "internet" in context_lower:
            attack_surface.append("Public internet")
        if "auth" in context_lower:
            attack_surface.append("Authentication system")
        if "api" in context_lower:
            attack_surface.append("API endpoints")
        if "upload" in context_lower:
            attack_surface.append("File uploads")

        return {
            "system_type": system_type,
            "assets": assets if assets else ["Application data"],
            "attack_surface": attack_surface if attack_surface else ["Web interface"],
        }

    def _conduct_threat_modeling(self, task: WizardTask, scope: dict) -> dict[str, Any]:
        """Conduct threat modeling using STRIDE"""
        threats = []

        # STRIDE methodology
        stride_threats = {
            "Spoofing": "Attacker impersonates legitimate user",
            "Tampering": "Attacker modifies data in transit or at rest",
            "Repudiation": "User denies performing an action",
            "Information Disclosure": "Unauthorized access to sensitive data",
            "Denial of Service": "System availability disrupted",
            "Elevation of Privilege": "Attacker gains unauthorized permissions",
        }

        # Map threats to attack surface
        for attack_surface_item in scope["attack_surface"]:
            if "Authentication" in attack_surface_item:
                threats.append(
                    {
                        "category": "Spoofing",
                        "threat": "Credential theft or session hijacking",
                        "likelihood": "medium",
                        "impact": "high",
                    }
                )
                threats.append(
                    {
                        "category": "Elevation of Privilege",
                        "threat": "Authentication bypass",
                        "likelihood": "low",
                        "impact": "critical",
                    }
                )

            if "API" in attack_surface_item:
                threats.append(
                    {
                        "category": "Information Disclosure",
                        "threat": "API exposes sensitive data without authorization",
                        "likelihood": "medium",
                        "impact": "high",
                    }
                )
                threats.append(
                    {
                        "category": "Denial of Service",
                        "threat": "API rate limiting bypass or resource exhaustion",
                        "likelihood": "medium",
                        "impact": "medium",
                    }
                )

            if "File upload" in attack_surface_item:
                threats.append(
                    {
                        "category": "Tampering",
                        "threat": "Malicious file upload (malware, scripts)",
                        "likelihood": "high",
                        "impact": "high",
                    }
                )

        # Generic threats
        if not threats:
            threats = [
                {
                    "category": "Information Disclosure",
                    "threat": "Unauthorized data access",
                    "likelihood": "medium",
                    "impact": "high",
                },
                {
                    "category": "Spoofing",
                    "threat": "Identity theft",
                    "likelihood": "medium",
                    "impact": "high",
                },
            ]

        return {"methodology": "STRIDE", "threats": threats, "assets_at_risk": scope["assets"]}

    def _identify_vulnerabilities(self, task: WizardTask, scope: dict) -> list[dict[str, str]]:
        """Identify potential vulnerabilities (OWASP Top 10 based)"""
        vulns = []

        context_lower = task.context.lower()

        # Check for common vulnerabilities
        if "sql" in context_lower or "database" in context_lower:
            vulns.append(
                {
                    "name": "SQL Injection",
                    "severity": "critical",
                    "description": "User input may not be properly sanitized before database queries",
                    "remediation": "Use parameterized queries/prepared statements, ORM, input validation",
                }
            )

        if "auth" in context_lower:
            vulns.append(
                {
                    "name": "Broken Authentication",
                    "severity": "critical",
                    "description": "Weak password policies, session management issues, or missing MFA",
                    "remediation": "Implement strong password policies, secure session management, MFA",
                }
            )

        if "api" in context_lower:
            vulns.append(
                {
                    "name": "Broken Access Control",
                    "severity": "high",
                    "description": "Users may access resources they shouldn't have permission for",
                    "remediation": "Implement proper authorization checks, principle of least privilege",
                }
            )

        if "encrypt" not in context_lower and (
            "data" in context_lower or "password" in context_lower
        ):
            vulns.append(
                {
                    "name": "Sensitive Data Exposure",
                    "severity": "high",
                    "description": "Sensitive data may be transmitted or stored without encryption",
                    "remediation": "Use TLS for transport, encrypt data at rest, proper key management",
                }
            )

        if "xml" in context_lower or "deserialize" in context_lower:
            vulns.append(
                {
                    "name": "XXE / Insecure Deserialization",
                    "severity": "high",
                    "description": "Unsafe parsing of XML or deserialization of untrusted data",
                    "remediation": "Disable XML external entities, validate deserialization input",
                }
            )

        if "log" in context_lower:
            vulns.append(
                {
                    "name": "Insufficient Logging & Monitoring",
                    "severity": "medium",
                    "description": "Security events may not be logged or monitored",
                    "remediation": "Implement comprehensive logging, set up alerts, log retention",
                }
            )

        # Generic vulnerabilities if none found
        if not vulns:
            vulns = [
                {
                    "name": "Security Best Practices",
                    "severity": "medium",
                    "description": "General security hardening needed",
                    "remediation": "Follow OWASP guidelines, security code review, penetration testing",
                }
            ]

        return vulns[:6]  # Top 6 vulnerabilities

    def _assess_compliance(self, task: WizardTask, scope: dict) -> list[str]:
        """Assess compliance requirements"""
        compliance_reqs = []

        assets = scope.get("assets", [])

        if any("payment" in asset.lower() or "credit" in asset.lower() for asset in assets):
            compliance_reqs.append("PCI DSS (Payment Card Industry Data Security Standard)")

        if any("health" in asset.lower() or "medical" in asset.lower() for asset in assets):
            compliance_reqs.append("HIPAA (Health Insurance Portability and Accountability Act)")

        if any("personal" in asset.lower() for asset in assets):
            compliance_reqs.append("GDPR (General Data Protection Regulation)")
            compliance_reqs.append("CCPA (California Consumer Privacy Act)")

        return compliance_reqs

    def _assess_security_risks(
        self, task: WizardTask, vulnerabilities: list[dict], threat_model: dict
    ) -> list[WizardRisk]:
        """Assess security risks"""
        risks = []

        # Critical vulnerabilities = high risk
        critical_vulns = [v for v in vulnerabilities if v["severity"] == "critical"]
        if critical_vulns:
            risks.append(
                WizardRisk(
                    risk=f"{len(critical_vulns)} critical vulnerabilities could lead to data breach",
                    mitigation="Immediate remediation of critical issues, security code review, penetration testing",
                    severity="critical",
                )
            )

        # Check for high-impact threats
        high_impact_threats = [
            t for t in threat_model["threats"] if t["impact"] in ["high", "critical"]
        ]
        if high_impact_threats:
            risks.append(
                WizardRisk(
                    risk=f"{len(high_impact_threats)} high-impact threats identified",
                    mitigation="Implement security controls, monitoring, and incident response plan",
                    severity="high",
                )
            )

        risks.append(
            WizardRisk(
                risk="Security debt accumulation over time",
                mitigation="Regular security reviews, automated scanning, security training",
                severity="medium",
            )
        )

        risks.append(
            WizardRisk(
                risk="Insider threats or compromised credentials",
                mitigation="Principle of least privilege, audit logging, MFA, background checks",
                severity="medium",
            )
        )

        return risks[:5]

    def _create_diagnosis(
        self, scope: dict, vulnerabilities: list[dict], threat_model: dict
    ) -> str:
        """Create security diagnosis"""
        critical_count = len([v for v in vulnerabilities if v["severity"] == "critical"])
        return f"{scope['system_type']} security review: {len(vulnerabilities)} vulnerabilities ({critical_count} critical), {len(threat_model['threats'])} threats identified"

    def _format_threat_model(self, threat_model: dict) -> str:
        """Format threat model as documentation"""
        content = f"# Threat Model ({threat_model['methodology']})\n\n"

        content += "## Assets at Risk\n"
        for asset in threat_model["assets_at_risk"]:
            content += f"- {asset}\n"
        content += "\n"

        content += "## Identified Threats\n\n"
        for i, threat in enumerate(threat_model["threats"], 1):
            content += f"### Threat {i}: {threat['category']}\n\n"
            content += f"**Description**: {threat['threat']}\n\n"
            content += f"**Likelihood**: {threat['likelihood'].upper()}\n\n"
            content += f"**Impact**: {threat['impact'].upper()}\n\n"
            content += f"**Risk Score**: {self._calculate_risk_score(threat['likelihood'], threat['impact'])}\n\n"
            content += "---\n\n"

        return content

    def _calculate_risk_score(self, likelihood: str, impact: str) -> str:
        """Calculate risk score"""
        scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        score = scores.get(likelihood, 2) * scores.get(impact, 2)

        if score >= 9:
            return "CRITICAL"
        elif score >= 6:
            return "HIGH"
        elif score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _format_vulnerabilities(self, vulnerabilities: list[dict]) -> str:
        """Format vulnerabilities as documentation"""
        content = "# Vulnerability Assessment\n\n"

        # Group by severity
        for severity in ["critical", "high", "medium", "low"]:
            vulns_by_severity = [v for v in vulnerabilities if v["severity"] == severity]
            if vulns_by_severity:
                content += f"## {severity.upper()} Severity ({len(vulns_by_severity)})\n\n"
                for vuln in vulns_by_severity:
                    content += f"### {vuln['name']}\n\n"
                    content += f"**Description**: {vuln['description']}\n\n"
                    content += f"**Remediation**: {vuln['remediation']}\n\n"
                    content += "---\n\n"

        return content

    def _generate_security_checklist(
        self, scope: dict, vulnerabilities: list[dict], compliance: list[str]
    ) -> str:
        """Generate security checklist"""
        compliance_str = ", ".join(compliance) if compliance else "N/A"
        return f"""# Security Review Checklist

## Authentication & Authorization
- [ ] Strong password policy enforced (min 12 chars, complexity)
- [ ] Multi-factor authentication (MFA) implemented
- [ ] Session management secure (secure cookies, timeout)
- [ ] Authorization checks on all protected resources
- [ ] Principle of least privilege applied

## Data Protection
- [ ] TLS/HTTPS for all data in transit
- [ ] Sensitive data encrypted at rest
- [ ] Secure key management (no hardcoded keys)
- [ ] PII handling compliant with regulations
- [ ] Data retention and deletion policies

## Input Validation
- [ ] All user input validated and sanitized
- [ ] Parameterized queries (no SQL injection)
- [ ] XSS protection (output encoding)
- [ ] CSRF tokens on state-changing operations
- [ ] File upload validation (type, size, content)

## API Security
- [ ] API authentication required
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] Proper error handling (no info leakage)
- [ ] API versioning strategy

## Infrastructure
- [ ] Security patches up to date
- [ ] Unused services disabled
- [ ] Firewalls configured
- [ ] Network segmentation
- [ ] Backup and disaster recovery plan

## Logging & Monitoring
- [ ] Security events logged
- [ ] Log aggregation and analysis
- [ ] Alerting for suspicious activity
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled

## Code Security
- [ ] Security code review completed
- [ ] Static analysis tools integrated
- [ ] Dependency vulnerability scanning
- [ ] Security testing in CI/CD
- [ ] Secret management (no secrets in code)

## Compliance ({compliance_str})
- [ ] Compliance requirements identified
- [ ] Controls implemented
- [ ] Documentation maintained
- [ ] Regular compliance audits

## Identified Vulnerabilities
{chr(10).join(f"- [ ] {vuln['name']}: {vuln['remediation'][:80]}..." for vuln in vulnerabilities)}

---
*Security Review Date*: [Date]
*Next Review*: [Date + 3 months]
"""

    def _generate_recommendations(self, vulnerabilities: list[dict], threat_model: dict) -> str:
        """Generate security recommendations"""
        return f"""# Security Recommendations

## Immediate Actions (Critical)
{chr(10).join(f"1. {vuln['name']}: {vuln['remediation']}" for vuln in vulnerabilities if vuln['severity'] == 'critical')}

## Short-term (Within 1 Month)
{chr(10).join(f"- {vuln['name']}: {vuln['remediation']}" for vuln in vulnerabilities if vuln['severity'] == 'high')}

## Long-term (Ongoing)
- Implement security training for development team
- Set up automated security scanning in CI/CD
- Conduct regular penetration testing (quarterly)
- Establish bug bounty program
- Create security champions program

## Security Tools Recommended
- **SAST**: SonarQube, Checkmarx, or Semgrep
- **DAST**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: Snyk, Dependabot
- **Secrets Detection**: GitLeaks, TruffleHog
- **Infrastructure**: AWS Security Hub, Azure Security Center

## Defense in Depth
Apply security at multiple layers:
1. **Perimeter**: Firewalls, DDoS protection
2. **Network**: VPNs, network segmentation
3. **Application**: Input validation, authentication
4. **Data**: Encryption at rest and in transit
5. **Monitoring**: SIEM, intrusion detection

## Incident Response
1. Prepare incident response plan
2. Define roles and responsibilities
3. Set up communication channels
4. Practice incident scenarios (tabletop exercises)
5. Document lessons learned

---
*Remember*: Security is not a one-time effort but an ongoing process.
"""
