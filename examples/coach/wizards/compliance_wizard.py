"""
Compliance Wizard

SOC 2, HIPAA, GDPR, ISO 27001 compliance audit and preparation.
Uses Empathy Framework Level 3 (Proactive) for compliance gap analysis and Level 4
(Anticipatory) for predicting audit failures and regulatory risks.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import re
from typing import List, Dict, Any

from .base_wizard import (
    BaseWizard,
    WizardTask,
    WizardOutput,
    WizardArtifact,
    WizardRisk,
    WizardHandoff,
    EmpathyChecks,
)


class ComplianceWizard(BaseWizard):
    """
    Wizard for compliance audits and regulatory preparation

    Uses:
    - Level 2: Guide user through compliance requirements
    - Level 3: Proactively identify compliance gaps
    - Level 4: Anticipate audit failures and regulatory changes
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a compliance task"""
        # High-priority compliance phrases (worth 2 points each)
        compliance_phrases = [
            "compliance", "audit", "soc 2", "hipaa", "gdpr", "iso 27001"
        ]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "pentest", "penetration test", "security audit", "pci dss",
            "pii", "phi", "data protection", "privacy", "certification",
            "regulatory", "sox", "ccpa", "regulation"
        ]

        task_lower = (task.task + " " + task.context).lower()

        primary_matches = sum(2 for phrase in compliance_phrases if phrase in task_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute compliance audit workflow"""

        emotional_state = self._assess_emotional_state(task)
        constraints = self._extract_constraints(task)

        diagnosis = self._analyze_compliance_requirements(task)
        gap_analysis = self._perform_gap_analysis(task)
        remediation_plan = self._create_remediation_plan(task, gap_analysis)
        policy_documents = self._generate_policy_documents(task)
        audit_evidence = self._create_audit_evidence(task)
        compliance_forecast = self._predict_compliance_risks(task, gap_analysis)

        artifacts = [
            WizardArtifact(
                type="doc",
                title="Compliance Gap Analysis",
                content=self._generate_gap_analysis_report(diagnosis, gap_analysis)
            ),
            WizardArtifact(
                type="doc",
                title="Remediation Plan",
                content="\n".join(remediation_plan)
            ),
            WizardArtifact(
                type="doc",
                title="Policy Documents",
                content=policy_documents
            ),
            WizardArtifact(
                type="doc",
                title="Audit Evidence Collection",
                content=audit_evidence
            ),
            WizardArtifact(
                type="checklist",
                title="Pre-Audit Checklist",
                content=self._create_pre_audit_checklist(task)
            ),
            WizardArtifact(
                type="doc",
                title="Compliance Risk Forecast",
                content=compliance_forecast
            )
        ]

        plan = remediation_plan[:7]

        empathy_checks = EmpathyChecks(
            cognitive=f"Considered stakeholders: legal, security, auditors, customers, executives",
            emotional=f"Acknowledged: Audits are stressful and high-stakes, {emotional_state['urgency']} urgency",
            anticipatory=compliance_forecast[:200] + "..." if len(compliance_forecast) > 200 else compliance_forecast
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=plan,
            artifacts=artifacts,
            risks=self._identify_risks(task, gap_analysis),
            handoffs=self._create_handoffs(task),
            next_actions=plan[:5] + self._generate_anticipatory_actions(task),
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task)
        )

    def _analyze_compliance_requirements(self, task: WizardTask) -> str:
        """Analyze compliance requirements"""
        analysis = "# Compliance Requirements Analysis\n\n"
        analysis += f"**Objective**: {task.task}\n\n"

        task_lower = (task.task + " " + task.context).lower()

        # Detect compliance frameworks
        frameworks = []
        if "soc 2" in task_lower or "soc2" in task_lower:
            frameworks.append("SOC 2 Type II")
        if "hipaa" in task_lower:
            frameworks.append("HIPAA")
        if "gdpr" in task_lower:
            frameworks.append("GDPR")
        if "iso 27001" in task_lower or "iso27001" in task_lower:
            frameworks.append("ISO 27001")
        if "pci" in task_lower or "pci dss" in task_lower:
            frameworks.append("PCI DSS")

        if not frameworks:
            frameworks.append("SOC 2 Type II (assumed)")

        analysis += f"**Target Compliance**: {', '.join(frameworks)}\n"
        analysis += f"**Timeline**: Pre-audit preparation\n"
        analysis += f"**Context**: {task.context[:300]}...\n" if len(task.context) > 300 else f"**Context**: {task.context}\n"

        return analysis

    def _perform_gap_analysis(self, task: WizardTask) -> List[Dict[str, Any]]:
        """Perform compliance gap analysis"""
        gaps = []

        # SOC 2 Trust Service Criteria
        gaps.append({
            "framework": "SOC 2",
            "criterion": "CC6.1 - Logical and Physical Access Controls",
            "requirement": "Implement MFA for all system access",
            "current_state": "Password-only authentication",
            "gap": "Missing multi-factor authentication",
            "severity": "critical",
            "remediation": [
                "Implement MFA for all users (Google Authenticator, Duo, etc.)",
                "Enforce MFA for privileged accounts (admins, developers)",
                "Document MFA policy and user onboarding process"
            ]
        })

        gaps.append({
            "framework": "SOC 2",
            "criterion": "CC7.2 - System Monitoring",
            "requirement": "Monitor system components and detect anomalies",
            "current_state": "Basic logging, no alerting",
            "gap": "Insufficient monitoring and alerting",
            "severity": "high",
            "remediation": [
                "Implement centralized logging (ELK, Splunk, Datadog)",
                "Set up alerts for security events (failed logins, privilege escalation)",
                "Create incident response runbooks"
            ]
        })

        gaps.append({
            "framework": "SOC 2 / GDPR",
            "criterion": "Data Encryption",
            "requirement": "Encrypt data at rest and in transit",
            "current_state": "HTTPS only, database not encrypted",
            "gap": "Data at rest not encrypted",
            "severity": "critical",
            "remediation": [
                "Enable database encryption (PostgreSQL: pgcrypto, MySQL: TDE)",
                "Encrypt backups",
                "Implement key management (AWS KMS, HashiCorp Vault)"
            ]
        })

        gaps.append({
            "framework": "GDPR",
            "criterion": "Article 17 - Right to Erasure",
            "requirement": "Users can request data deletion",
            "current_state": "Manual process, no automation",
            "gap": "No automated data deletion workflow",
            "severity": "high",
            "remediation": [
                "Implement data deletion API endpoint",
                "Create user-facing data export/deletion UI",
                "Document data retention policy (30-day deletion SLA)"
            ]
        })

        gaps.append({
            "framework": "SOC 2 / ISO 27001",
            "criterion": "Vendor Risk Management",
            "requirement": "Assess third-party vendor security",
            "current_state": "No vendor security reviews",
            "gap": "Missing vendor risk assessment process",
            "severity": "medium",
            "remediation": [
                "Create vendor security questionnaire",
                "Review SOC 2 reports for critical vendors",
                "Maintain vendor risk register"
            ]
        })

        gaps.append({
            "framework": "SOC 2",
            "criterion": "CC2.1 - Risk Assessment",
            "requirement": "Annual risk assessment process",
            "current_state": "No formal risk assessment",
            "gap": "Missing risk assessment documentation",
            "severity": "high",
            "remediation": [
                "Conduct annual risk assessment",
                "Document threats, vulnerabilities, mitigations",
                "Executive sign-off on risk acceptance"
            ]
        })

        return gaps

    def _create_remediation_plan(self, task: WizardTask, gaps: List[Dict]) -> List[str]:
        """Create compliance remediation plan"""
        plan = ["## Compliance Remediation Plan (Priority Ordered)\n"]

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_gaps = sorted(gaps, key=lambda g: severity_order.get(g["severity"], 3))

        for i, gap in enumerate(sorted_gaps, 1):
            plan.append(f"\n### Step {i}: {gap['criterion']} ({gap['severity'].upper()})")
            plan.append(f"**Framework**: {gap['framework']}")
            plan.append(f"**Gap**: {gap['gap']}")
            plan.append(f"**Current**: {gap['current_state']}")
            plan.append("\n**Remediation**:")
            for j, step in enumerate(gap['remediation'], 1):
                plan.append(f"  {j}. {step}")

        plan.append(f"\n### Step {len(sorted_gaps)+1}: Pre-Audit Validation")
        plan.append("  1. Self-assessment against all controls")
        plan.append("  2. Collect audit evidence (screenshots, logs, policies)")
        plan.append("  3. Conduct internal mock audit")
        plan.append("  4. Schedule external audit")

        return plan

    def _generate_policy_documents(self, task: WizardTask) -> str:
        """Generate compliance policy documents"""
        policies = "# Compliance Policy Documents\n\n"

        policies += "## 1. Information Security Policy\n\n"
        policies += "**Purpose**: Define security standards and responsibilities\n\n"
        policies += "**Scope**: All employees, contractors, systems, and data\n\n"
        policies += "**Key Requirements**:\n"
        policies += "- All systems must use multi-factor authentication\n"
        policies += "- Data must be encrypted at rest and in transit\n"
        policies += "- Annual security training required for all employees\n"
        policies += "- Incident response plan must be followed\n"
        policies += "- Third-party vendors must be security-reviewed\n\n"

        policies += "**Review**: Annually or when significant changes occur\n\n"
        policies += "---\n\n"

        policies += "## 2. Data Retention and Deletion Policy\n\n"
        policies += "**Purpose**: Define how long data is retained and deletion procedures\n\n"
        policies += "**Data Retention Periods**:\n"
        policies += "- Active user data: Retained while account active\n"
        policies += "- Inactive accounts: 2 years, then deleted\n"
        policies += "- Audit logs: 7 years (regulatory requirement)\n"
        policies += "- Backups: 30 days\n\n"

        policies += "**Deletion Process**:\n"
        policies += "1. User requests deletion via in-app UI or email\n"
        policies += "2. 30-day grace period (can cancel deletion)\n"
        policies += "3. Automated deletion of all user data\n"
        policies += "4. Confirmation email sent\n"
        policies += "5. Audit trail maintained (metadata only, not PII)\n\n"

        policies += "---\n\n"

        policies += "## 3. Incident Response Policy\n\n"
        policies += "**Purpose**: Define response procedures for security incidents\n\n"
        policies += "**Incident Classification**:\n"
        policies += "- **P0 (Critical)**: Data breach, system compromise\n"
        policies += "- **P1 (High)**: Unauthorized access attempt, malware\n"
        policies += "- **P2 (Medium)**: Policy violation, minor vulnerability\n"
        policies += "- **P3 (Low)**: Suspicious activity, false alarm\n\n"

        policies += "**Response Steps**:\n"
        policies += "1. **Detect**: Automated alerts or manual report\n"
        policies += "2. **Contain**: Isolate affected systems\n"
        policies += "3. **Investigate**: Root cause analysis\n"
        policies += "4. **Remediate**: Fix vulnerability, restore service\n"
        policies += "5. **Report**: Notify stakeholders (legal, customers if breach)\n"
        policies += "6. **Post-Mortem**: Document lessons learned\n\n"

        policies += "**Notification Requirements**:\n"
        policies += "- GDPR: 72 hours to notify authorities of breach\n"
        policies += "- HIPAA: 60 days to notify affected individuals\n"
        policies += "- SOC 2: Notify customers per contract terms\n\n"

        policies += "---\n\n"

        policies += "## 4. Access Control Policy\n\n"
        policies += "**Purpose**: Define who can access what, and how\n\n"
        policies += "**Principles**:\n"
        policies += "- **Least Privilege**: Users get minimum access needed\n"
        policies += "- **Role-Based Access**: Access based on job function\n"
        policies += "- **Regular Review**: Quarterly access reviews\n"
        policies += "- **Immediate Revocation**: Access removed upon termination\n\n"

        policies += "**Access Tiers**:\n"
        policies += "- **Admin**: Full system access (CTO, Lead Engineer)\n"
        policies += "- **Developer**: Code + staging environments\n"
        policies += "- **Support**: Customer data (read-only)\n"
        policies += "- **Contractor**: Scoped access, time-limited\n\n"

        policies += "**MFA Requirements**:\n"
        policies += "- All production system access: Required\n"
        policies += "- Code repositories: Required\n"
        policies += "- Cloud consoles (AWS, GCP): Required\n"
        policies += "- Email: Strongly recommended\n\n"

        return policies

    def _create_audit_evidence(self, task: WizardTask) -> str:
        """Create audit evidence collection guide"""
        evidence = "# Audit Evidence Collection\n\n"

        evidence += "## What Auditors Will Request\n\n"
        evidence += "### 1. Access Controls\n"
        evidence += "- [ ] Screenshot of MFA enforcement settings\n"
        evidence += "- [ ] List of all users with admin access\n"
        evidence += "- [ ] Access review logs (quarterly reviews)\n"
        evidence += "- [ ] Terminated user access revocation proof\n\n"

        evidence += "### 2. Encryption\n"
        evidence += "- [ ] Database encryption settings (screenshot)\n"
        evidence += "- [ ] SSL/TLS certificate (valid, not expired)\n"
        evidence += "- [ ] Backup encryption verification\n"
        evidence += "- [ ] Key management procedures (documented)\n\n"

        evidence += "### 3. Monitoring & Logging\n"
        evidence += "- [ ] Centralized logging setup (screenshot)\n"
        evidence += "- [ ] Security alert configurations\n"
        evidence += "- [ ] Sample security event log (redacted)\n"
        evidence += "- [ ] Log retention policy (7 years)\n\n"

        evidence += "### 4. Incident Response\n"
        evidence += "- [ ] Incident response plan (documented)\n"
        evidence += "- [ ] Incident response test results\n"
        evidence += "- [ ] Sample incident report (if any incidents)\n"
        evidence += "- [ ] Post-mortem documents\n\n"

        evidence += "### 5. Vendor Management\n"
        evidence += "- [ ] Vendor risk register (all third-party services)\n"
        evidence += "- [ ] Vendor SOC 2 reports (AWS, Stripe, etc.)\n"
        evidence += "- [ ] Data processing agreements (DPAs)\n\n"

        evidence += "### 6. Change Management\n"
        evidence += "- [ ] Git commit history (shows review process)\n"
        evidence += "- [ ] CI/CD pipeline configuration\n"
        evidence += "- [ ] Production deployment approvals\n"
        evidence += "- [ ] Rollback procedures\n\n"

        evidence += "### 7. Data Protection (GDPR)\n"
        evidence += "- [ ] Privacy policy (published on website)\n"
        evidence += "- [ ] Data processing register\n"
        evidence += "- [ ] User data export/deletion workflow\n"
        evidence += "- [ ] Cookie consent implementation\n\n"

        evidence += "## Evidence Organization\n\n"
        evidence += "```\n"
        evidence += "audit-evidence/\n"
        evidence += "├── 01-access-controls/\n"
        evidence += "│   ├── mfa-settings.png\n"
        evidence += "│   ├── admin-users-list.pdf\n"
        evidence += "│   └── access-review-2025-Q1.xlsx\n"
        evidence += "├── 02-encryption/\n"
        evidence += "│   ├── database-encryption.png\n"
        evidence += "│   └── ssl-certificate.pdf\n"
        evidence += "├── 03-monitoring/\n"
        evidence += "│   ├── logging-setup.png\n"
        evidence += "│   └── alert-rules.json\n"
        evidence += "├── 04-policies/\n"
        evidence += "│   ├── information-security-policy.pdf\n"
        evidence += "│   ├── incident-response-policy.pdf\n"
        evidence += "│   └── data-retention-policy.pdf\n"
        evidence += "└── 05-vendor-management/\n"
        evidence += "    ├── vendor-register.xlsx\n"
        evidence += "    └── aws-soc2-report.pdf\n"
        evidence += "```\n\n"

        evidence += "## Tips for Audit Success\n\n"
        evidence += "1. **Be proactive**: Collect evidence as you go, not scrambling before audit\n"
        evidence += "2. **Be honest**: If something isn't implemented, say so (don't hide gaps)\n"
        evidence += "3. **Be organized**: Well-organized evidence saves time and shows maturity\n"
        evidence += "4. **Be responsive**: Answer auditor questions quickly\n"
        evidence += "5. **Be collaborative**: Treat auditors as partners, not adversaries\n"

        return evidence

    def _create_pre_audit_checklist(self, task: WizardTask) -> str:
        """Create pre-audit checklist"""
        checklist = "# Pre-Audit Checklist\n\n"

        checklist += "## 3 Months Before Audit\n\n"
        checklist += "- [ ] Schedule audit with external auditor\n"
        checklist += "- [ ] Conduct gap analysis against SOC 2/GDPR/HIPAA\n"
        checklist += "- [ ] Create remediation plan for gaps\n"
        checklist += "- [ ] Assign remediation tasks to team\n\n"

        checklist += "## 2 Months Before Audit\n\n"
        checklist += "- [ ] Implement critical controls (MFA, encryption)\n"
        checklist += "- [ ] Document all policies (security, privacy, incident response)\n"
        checklist += "- [ ] Executive review and sign-off on policies\n"
        checklist += "- [ ] Begin evidence collection\n\n"

        checklist += "## 1 Month Before Audit\n\n"
        checklist += "- [ ] Complete all remediation tasks\n"
        checklist += "- [ ] Conduct internal mock audit\n"
        checklist += "- [ ] Organize evidence in shared folder\n"
        checklist += "- [ ] Train team on audit procedures\n"
        checklist += "- [ ] Identify audit point of contact\n\n"

        checklist += "## 1 Week Before Audit\n\n"
        checklist += "- [ ] Final evidence review (ensure nothing missing)\n"
        checklist += "- [ ] Test all controls (MFA, monitoring, backups)\n"
        checklist += "- [ ] Confirm audit logistics (dates, participants)\n"
        checklist += "- [ ] Prepare audit kick-off presentation\n\n"

        checklist += "## During Audit\n\n"
        checklist += "- [ ] Daily standup with auditor\n"
        checklist += "- [ ] Respond to information requests within 24 hours\n"
        checklist += "- [ ] Document any new gaps identified\n"
        checklist += "- [ ] Maintain professional, collaborative tone\n\n"

        checklist += "## Post-Audit\n\n"
        checklist += "- [ ] Review draft audit report\n"
        checklist += "- [ ] Address any findings/exceptions\n"
        checklist += "- [ ] Receive final SOC 2 report\n"
        checklist += "- [ ] Share report with customers (if requested)\n"
        checklist += "- [ ] Plan for next year's audit\n"

        return checklist

    def _predict_compliance_risks(self, task: WizardTask, gaps: List[Dict]) -> str:
        """Level 4: Predict compliance risks"""
        forecast = "# Compliance Risk Forecast (Level 4: Anticipatory)\n\n"

        critical_gaps = [g for g in gaps if g['severity'] == 'critical']

        forecast += "## Current State\n"
        forecast += f"- Critical gaps: {len(critical_gaps)}\n"
        forecast += f"- Total gaps: {len(gaps)}\n"
        forecast += "- Audit readiness: Not ready (gaps present)\n\n"

        forecast += "## Projected Risks (Next 30-90 Days)\n\n"

        forecast += "### ⚠️ Audit Failure (30 days)\n"
        forecast += "**Prediction**: Critical gaps will cause SOC 2 audit failure\n"
        forecast += "**Impact**: No SOC 2 report = lost enterprise customers, deal blockers\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Fix ALL critical gaps before audit starts\n"
        forecast += "- Conduct mock audit to validate readiness\n"
        forecast += "- Consider delaying audit if not ready (better than failing)\n\n"

        forecast += "### ⚠️ Data Breach Due to Weak Controls (45 days)\n"
        forecast += "**Prediction**: Missing MFA and encryption increase breach risk\n"
        forecast += "**Impact**: GDPR fines (up to 4% revenue), customer trust loss, legal action\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Implement MFA NOW (highest priority)\n"
        forecast += "- Enable database encryption immediately\n"
        forecast += "- Conduct penetration test to find vulnerabilities\n\n"

        forecast += "### ⚠️ GDPR Complaint (60 days)\n"
        forecast += "**Prediction**: User requests data deletion, we can't comply within 30 days\n"
        forecast += "**Impact**: GDPR violation, fines, bad PR\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Implement automated data deletion workflow\n"
        forecast += "- Test deletion process end-to-end\n"
        forecast += "- Document data retention policy\n\n"

        forecast += "### ⚠️ Vendor Breach Cascades to Us (90 days)\n"
        forecast += "**Prediction**: Third-party vendor suffers breach, exposes our data\n"
        forecast += "**Impact**: We're liable, even though vendor was breached\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Review vendor security (SOC 2 reports)\n"
        forecast += "- Ensure data processing agreements (DPAs) in place\n"
        forecast += "- Minimize data shared with vendors\n\n"

        forecast += "## Compliance Debt Trajectory\n\n"
        forecast += "**If gaps not addressed**:\n"
        forecast += "- Month 1: Audit failure, delayed customer deals\n"
        forecast += "- Month 3: Increased breach risk as attack surface grows\n"
        forecast += "- Month 6: Major incident triggers regulatory investigation\n"
        forecast += "- Month 12: Fines, lawsuits, reputation damage\n\n"

        forecast += "**If addressed now**:\n"
        forecast += "- Month 1: Pass SOC 2 audit, unlock enterprise deals\n"
        forecast += "- Month 3: Reduced breach risk, compliance becomes routine\n"
        forecast += "- Month 6: Compliance as competitive advantage\n"
        forecast += "- Month 12: Trusted brand, minimal regulatory risk\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Week 1-2**: Fix critical gaps (MFA, encryption)\n"
        forecast += "- **Week 3-4**: Document policies, collect evidence\n"
        forecast += "- **Week 5-6**: Mock audit, address findings\n"
        forecast += "- **Week 7+**: Official audit, certification\n"

        return forecast

    def _generate_gap_analysis_report(self, diagnosis: str, gaps: List[Dict]) -> str:
        """Generate gap analysis report"""
        report = f"{diagnosis}\n\n"

        report += "## Gap Analysis Summary\n\n"

        critical = len([g for g in gaps if g['severity'] == 'critical'])
        high = len([g for g in gaps if g['severity'] == 'high'])
        medium = len([g for g in gaps if g['severity'] == 'medium'])

        report += f"- **Critical**: {critical} gaps (MUST fix before audit)\n"
        report += f"- **High**: {high} gaps (Should fix before audit)\n"
        report += f"- **Medium**: {medium} gaps (Fix when possible)\n\n"

        report += "**Audit Readiness**: ❌ Not ready (critical gaps present)\n\n"

        report += "## Detailed Gaps\n\n"

        for i, gap in enumerate(gaps, 1):
            report += f"### {i}. {gap['criterion']} ({gap['severity'].upper()})\n"
            report += f"**Framework**: {gap['framework']}\n"
            report += f"**Requirement**: {gap['requirement']}\n"
            report += f"**Current State**: {gap['current_state']}\n"
            report += f"**Gap**: {gap['gap']}\n\n"
            report += "**Remediation**:\n"
            for step in gap['remediation']:
                report += f"- {step}\n"
            report += "\n"

        return report

    def _identify_risks(self, task: WizardTask, gaps: List[Dict]) -> List[WizardRisk]:
        """Identify compliance risks"""
        risks = []

        risks.append(WizardRisk(
            risk="Audit failure blocks enterprise customer deals",
            mitigation="Fix all critical gaps before audit. Conduct mock audit to validate readiness.",
            severity="high"
        ))

        risks.append(WizardRisk(
            risk="Data breach leads to GDPR/HIPAA fines and lawsuits",
            mitigation="Implement MFA, encryption, monitoring NOW. Conduct penetration test.",
            severity="critical"
        ))

        risks.append(WizardRisk(
            risk="Compliance gaps grow faster than team can remediate",
            mitigation="Prioritize critical gaps. Consider hiring compliance consultant. Automate where possible.",
            severity="medium"
        ))

        return risks

    def _create_handoffs(self, task: WizardTask) -> List[WizardHandoff]:
        """Create handoffs for compliance work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(WizardHandoff(
                owner="Security Team / CISO",
                what="Implement technical controls (MFA, encryption, monitoring), conduct penetration test",
                when="Before audit"
            ))
            handoffs.append(WizardHandoff(
                owner="Legal / Compliance Officer",
                what="Review policies, ensure regulatory compliance, manage auditor relationship",
                when="Throughout audit process"
            ))
            handoffs.append(WizardHandoff(
                owner="External Auditor",
                what="Conduct SOC 2 / ISO 27001 audit, issue certification report",
                when="After remediation complete"
            ))

        return handoffs
