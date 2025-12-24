"""
Security Audit Crew

A multi-agent crew that performs comprehensive security audits.
Demonstrates CrewAI's hierarchical collaboration patterns with:
- 5 specialized agents with distinct roles
- Hierarchical task delegation from Security Lead
- Memory Graph integration for cross-analysis learning
- Structured output with severity scoring

Usage:
    from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

    crew = SecurityAuditCrew(api_key="...")
    report = await crew.audit("path/to/codebase")

    print(f"Found {len(report.findings)} security issues")
    for finding in report.critical_findings:
        print(f"  - {finding.title}: {finding.remediation}")

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Security finding severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(Enum):
    """Security finding categories (OWASP-aligned)."""

    INJECTION = "injection"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA = "sensitive_data_exposure"
    XXE = "xml_external_entities"
    BROKEN_ACCESS = "broken_access_control"
    MISCONFIGURATION = "security_misconfiguration"
    XSS = "cross_site_scripting"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    VULNERABLE_COMPONENTS = "vulnerable_components"
    INSUFFICIENT_LOGGING = "insufficient_logging"
    OTHER = "other"


@dataclass
class SecurityFinding:
    """A single security finding from the audit."""

    title: str
    description: str
    severity: Severity
    category: FindingCategory
    file_path: str | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    remediation: str | None = None
    cwe_id: str | None = None
    cvss_score: float | None = None
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
            "remediation": self.remediation,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class SecurityReport:
    """Complete security audit report."""

    target: str
    findings: list[SecurityFinding]
    summary: str = ""
    audit_duration_seconds: float = 0.0
    agents_used: list[str] = field(default_factory=list)
    memory_graph_hits: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def critical_findings(self) -> list[SecurityFinding]:
        """Get critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    @property
    def high_findings(self) -> list[SecurityFinding]:
        """Get high severity findings."""
        return [f for f in self.findings if f.severity == Severity.HIGH]

    @property
    def findings_by_category(self) -> dict[str, list[SecurityFinding]]:
        """Group findings by category."""
        result: dict[str, list[SecurityFinding]] = {}
        for finding in self.findings:
            cat = finding.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(finding)
        return result

    @property
    def risk_score(self) -> float:
        """Calculate overall risk score (0-100)."""
        if not self.findings:
            return 0.0

        weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 0.5,
        }

        total = sum(weights[f.severity] * f.confidence for f in self.findings)
        return min(100.0, total)

    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            "target": self.target,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "audit_duration_seconds": self.audit_duration_seconds,
            "agents_used": self.agents_used,
            "memory_graph_hits": self.memory_graph_hits,
            "risk_score": self.risk_score,
            "finding_counts": {
                "critical": len(self.critical_findings),
                "high": len(self.high_findings),
                "total": len(self.findings),
            },
            "metadata": self.metadata,
        }


@dataclass
class SecurityAuditConfig:
    """Configuration for security audit crew."""

    # API Configuration
    provider: str = "anthropic"
    api_key: str | None = None

    # Scan Configuration
    scan_depth: str = "standard"  # "quick", "standard", "thorough"
    include_patterns: list[str] = field(
        default_factory=lambda: ["*.py", "*.js", "*.ts", "*.java", "*.go"]
    )
    exclude_patterns: list[str] = field(
        default_factory=lambda: ["*test*", "*spec*", "node_modules/*", "venv/*"]
    )

    # Memory Graph
    memory_graph_enabled: bool = True
    memory_graph_path: str = "patterns/security_memory.json"

    # Agent Tiers
    lead_tier: str = "premium"
    hunter_tier: str = "capable"
    assessor_tier: str = "capable"
    remediation_tier: str = "premium"
    compliance_tier: str = "cheap"

    # Resilience
    resilience_enabled: bool = True
    timeout_seconds: float = 300.0

    # XML Prompts
    xml_prompts_enabled: bool = True
    xml_schema_version: str = "1.0"


# XML Prompt Templates for Security Audit Agents
XML_PROMPT_TEMPLATES = {
    "security_lead": """<agent role="security_lead" version="{schema_version}">
  <identity>
    <role>Security Audit Lead</role>
    <expertise>Security coordination, risk prioritization, executive reporting</expertise>
  </identity>

  <goal>
    Coordinate the security audit team to identify and prioritize vulnerabilities.
    Synthesize findings into an actionable security report.
  </goal>

  <instructions>
    <step>Coordinate the security audit team and assign analysis tasks</step>
    <step>Review and deduplicate findings from all specialists</step>
    <step>Prioritize findings by risk score and exploitability</step>
    <step>Calculate overall risk score for the target</step>
    <step>Generate executive summary with key recommendations</step>
  </instructions>

  <constraints>
    <rule>Focus on actionable, exploitable vulnerabilities</rule>
    <rule>Minimize false positives through validation</rule>
    <rule>Provide clear risk context for each finding</rule>
    <rule>Include both technical and business impact</rule>
  </constraints>

  <output_format>
    <section name="summary">Executive summary of security posture</section>
    <section name="risk_score">Overall risk score 0-100</section>
    <section name="critical_findings">Vulnerabilities requiring immediate attention</section>
    <section name="recommendations">Prioritized remediation roadmap</section>
  </output_format>
</agent>""",
    "vulnerability_hunter": """<agent role="vulnerability_hunter" version="{schema_version}">
  <identity>
    <role>Vulnerability Hunter</role>
    <expertise>OWASP Top 10, penetration testing, vulnerability identification</expertise>
  </identity>

  <goal>
    Identify security vulnerabilities in code and configuration.
  </goal>

  <instructions>
    <step>Scan for OWASP Top 10 vulnerabilities</step>
    <step>Identify injection points (SQL, command, LDAP)</step>
    <step>Check for authentication and authorization flaws</step>
    <step>Review cryptographic implementations</step>
    <step>Detect hardcoded secrets and credentials</step>
    <step>Document each finding with file, line, and evidence</step>
  </instructions>

  <constraints>
    <rule>Focus on exploitable vulnerabilities</rule>
    <rule>Provide proof-of-concept or attack vector</rule>
    <rule>Include file path and line number</rule>
    <rule>Rate severity using CVSS methodology</rule>
  </constraints>

  <owasp_categories>
    <category>A01 - Broken Access Control</category>
    <category>A02 - Cryptographic Failures</category>
    <category>A03 - Injection</category>
    <category>A04 - Insecure Design</category>
    <category>A05 - Security Misconfiguration</category>
    <category>A06 - Vulnerable Components</category>
    <category>A07 - Auth Failures</category>
    <category>A08 - Software Integrity Failures</category>
    <category>A09 - Logging Failures</category>
    <category>A10 - SSRF</category>
  </owasp_categories>

  <output_format>
    <section name="findings">Vulnerabilities with severity, location, and evidence</section>
    <section name="summary">Vulnerability distribution summary</section>
  </output_format>
</agent>""",
    "risk_assessor": """<agent role="risk_assessor" version="{schema_version}">
  <identity>
    <role>Risk Assessor</role>
    <expertise>CVSS scoring, risk analysis, threat modeling</expertise>
  </identity>

  <goal>
    Assess the risk level of identified vulnerabilities.
  </goal>

  <instructions>
    <step>Calculate CVSS scores for each vulnerability</step>
    <step>Assess exploitability and attack complexity</step>
    <step>Evaluate blast radius and data sensitivity</step>
    <step>Consider existing mitigating controls</step>
    <step>Prioritize by business impact</step>
    <step>Identify attack chains and compound risks</step>
  </instructions>

  <constraints>
    <rule>Use CVSS 3.1 methodology consistently</rule>
    <rule>Consider environmental factors</rule>
    <rule>Identify dependencies between findings</rule>
    <rule>Provide confidence levels for assessments</rule>
  </constraints>

  <cvss_vectors>
    <metric name="AV">Attack Vector (Network, Adjacent, Local, Physical)</metric>
    <metric name="AC">Attack Complexity (Low, High)</metric>
    <metric name="PR">Privileges Required (None, Low, High)</metric>
    <metric name="UI">User Interaction (None, Required)</metric>
    <metric name="S">Scope (Unchanged, Changed)</metric>
    <metric name="C">Confidentiality Impact (None, Low, High)</metric>
    <metric name="I">Integrity Impact (None, Low, High)</metric>
    <metric name="A">Availability Impact (None, Low, High)</metric>
  </cvss_vectors>

  <output_format>
    <section name="assessments">Risk assessments with CVSS scores</section>
    <section name="summary">Overall risk level and key concerns</section>
  </output_format>
</agent>""",
    "remediation_expert": """<agent role="remediation_expert" version="{schema_version}">
  <identity>
    <role>Remediation Expert</role>
    <expertise>Secure coding, security engineering, fix implementation</expertise>
  </identity>

  <goal>
    Generate actionable remediation strategies for each vulnerability.
  </goal>

  <instructions>
    <step>Analyze root cause of each vulnerability</step>
    <step>Design fix strategy with code examples</step>
    <step>Consider backwards compatibility</step>
    <step>Prioritize fixes by effort vs impact</step>
    <step>Identify quick wins and long-term improvements</step>
    <step>Suggest testing approach for each fix</step>
  </instructions>

  <constraints>
    <rule>Provide complete, copy-pasteable code fixes</rule>
    <rule>Consider side effects and regressions</rule>
    <rule>Include before/after code snippets</rule>
    <rule>Reference security best practices</rule>
  </constraints>

  <remediation_types>
    <type>Code Fix - Direct code changes</type>
    <type>Configuration - Settings/environment changes</type>
    <type>Architecture - Structural improvements</type>
    <type>Dependency - Library updates/replacements</type>
    <type>Process - Development workflow changes</type>
  </remediation_types>

  <output_format>
    <section name="remediations">Fix strategies with code examples</section>
    <section name="summary">Remediation roadmap by priority</section>
  </output_format>
</agent>""",
    "compliance_mapper": """<agent role="compliance_mapper" version="{schema_version}">
  <identity>
    <role>Compliance Mapper</role>
    <expertise>Security standards, CWE/CVE mapping, regulatory compliance</expertise>
  </identity>

  <goal>
    Map vulnerabilities to standards and identify compliance implications.
  </goal>

  <instructions>
    <step>Map each finding to CWE identifiers</step>
    <step>Check for related CVEs in dependencies</step>
    <step>Identify OWASP category alignment</step>
    <step>Assess regulatory compliance impact (GDPR, HIPAA, PCI-DSS)</step>
    <step>Document audit trail requirements</step>
    <step>Suggest compliance-focused remediation priorities</step>
  </instructions>

  <constraints>
    <rule>Use official CWE/CVE identifiers</rule>
    <rule>Consider multiple compliance frameworks</rule>
    <rule>Highlight mandatory vs recommended fixes</rule>
    <rule>Include references to standards</rule>
  </constraints>

  <compliance_frameworks>
    <framework>OWASP Top 10</framework>
    <framework>CWE/SANS Top 25</framework>
    <framework>PCI-DSS</framework>
    <framework>HIPAA</framework>
    <framework>GDPR</framework>
    <framework>SOC 2</framework>
  </compliance_frameworks>

  <output_format>
    <section name="mappings">CWE/CVE mappings for each finding</section>
    <section name="compliance">Regulatory implications and requirements</section>
    <section name="summary">Compliance status overview</section>
  </output_format>
</agent>""",
}


class SecurityAuditCrew:
    """
    Multi-agent crew for comprehensive security audits.

    The crew consists of 5 specialized agents:

    1. **Security Lead** (Coordinator)
       - Orchestrates the team
       - Prioritizes and deduplicates findings
       - Generates executive summary
       - Model: Premium tier

    2. **Vulnerability Hunter** (Security Analyst)
       - Scans for OWASP Top 10 vulnerabilities
       - Identifies injection, XSS, auth issues
       - Model: Capable tier

    3. **Risk Assessor** (Risk Analyst)
       - Scores severity using CVSS methodology
       - Assesses blast radius and exploitability
       - Model: Capable tier

    4. **Remediation Expert** (Security Engineer)
       - Generates fix strategies with code examples
       - Prioritizes based on effort vs. impact
       - Model: Premium tier

    5. **Compliance Mapper** (Compliance Officer)
       - Maps findings to CWE, CVE, OWASP
       - Identifies compliance implications
       - Model: Cheap tier

    Example:
        crew = SecurityAuditCrew(api_key="...")
        report = await crew.audit("./src")

        # Access findings
        for finding in report.critical_findings:
            print(f"{finding.title}: {finding.remediation}")

        # Get risk score
        print(f"Risk Score: {report.risk_score}/100")
    """

    def __init__(self, config: SecurityAuditConfig | None = None, **kwargs):
        """
        Initialize the Security Audit Crew.

        Args:
            config: SecurityAuditConfig or pass individual params as kwargs
            **kwargs: Individual config parameters (api_key, provider, etc.)
        """
        if config:
            self.config = config
        else:
            self.config = SecurityAuditConfig(**kwargs)

        self._factory: Any = None
        self._agents: dict[str, Any] = {}
        self._workflow: Any = None
        self._graph: Any = None
        self._initialized = False

    def _render_xml_prompt(self, template_key: str) -> str:
        """Render XML prompt template with config values."""
        template = XML_PROMPT_TEMPLATES.get(template_key, "")
        return template.format(schema_version=self.config.xml_schema_version)

    def _get_system_prompt(self, agent_key: str, fallback: str) -> str:
        """Get system prompt - XML if enabled, fallback otherwise."""
        if self.config.xml_prompts_enabled:
            return self._render_xml_prompt(agent_key)
        return fallback

    async def _initialize(self) -> None:
        """Lazy initialization of agents and workflow."""
        if self._initialized:
            return

        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        # Check if CrewAI is available
        try:
            from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import _check_crewai

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
        """Create the 5 specialized security agents."""
        # 1. Security Lead (Coordinator)
        lead_fallback = """You are the Security Lead, a senior security architect.

Your responsibilities:
1. Coordinate the security audit team
2. Prioritize findings based on business impact
3. Deduplicate overlapping findings
4. Generate executive summaries
5. Ensure comprehensive coverage

You delegate tasks to your team:
- Vulnerability Hunter: Initial scanning and detection
- Risk Assessor: Severity scoring and impact analysis
- Remediation Expert: Fix strategies and code samples
- Compliance Mapper: Regulatory and standards mapping

Always think strategically about the overall security posture."""

        self._agents["lead"] = self._factory.create_agent(
            name="security_lead",
            role="coordinator",
            description="Senior security architect who orchestrates the security audit team",
            system_prompt=self._get_system_prompt("security_lead", lead_fallback),
            model_tier=self.config.lead_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
            resilience_enabled=self.config.resilience_enabled,
        )

        # 2. Vulnerability Hunter (Security Analyst)
        hunter_fallback = """You are the Vulnerability Hunter, an expert security analyst.

Your focus areas:
1. OWASP Top 10 vulnerabilities
2. Injection attacks (SQL, NoSQL, OS command, LDAP)
3. Cross-Site Scripting (XSS) - stored, reflected, DOM
4. Authentication and session management flaws
5. Sensitive data exposure
6. Security misconfigurations
7. Insecure deserialization
8. Known vulnerable components

For each finding, provide:
- Clear description of the vulnerability
- Exact file and line number
- Code snippet showing the issue
- Confidence level (0.0-1.0)

Be thorough but avoid false positives. When uncertain, note the confidence level."""

        self._agents["hunter"] = self._factory.create_agent(
            name="vulnerability_hunter",
            role="security",
            description="Expert at finding OWASP Top 10 and common vulnerabilities",
            system_prompt=self._get_system_prompt("vulnerability_hunter", hunter_fallback),
            model_tier=self.config.hunter_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

        # 3. Risk Assessor (Risk Analyst)
        assessor_fallback = """You are the Risk Assessor, a security risk analyst.

Your methodology:
1. Apply CVSS v3.1 scoring methodology
2. Consider attack vector (Network, Adjacent, Local, Physical)
3. Assess attack complexity (Low, High)
4. Evaluate privileges required (None, Low, High)
5. Determine user interaction requirements
6. Calculate impact on Confidentiality, Integrity, Availability

For each vulnerability:
- Assign CVSS base score (0.0-10.0)
- Map to severity level (Critical: 9.0-10.0, High: 7.0-8.9, Medium: 4.0-6.9, Low: 0.1-3.9)
- Assess blast radius (single component, service, system-wide)
- Evaluate exploitability (known exploits, proof of concept, theoretical)
- Consider business context impact

Be precise and consistent in your scoring methodology."""

        self._agents["assessor"] = self._factory.create_agent(
            name="risk_assessor",
            role="analyst",
            description="Scores vulnerability severity and assesses blast radius",
            system_prompt=self._get_system_prompt("risk_assessor", assessor_fallback),
            model_tier=self.config.assessor_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

        # 4. Remediation Expert (Security Engineer)
        remediation_fallback = """You are the Remediation Expert, a senior security engineer.

For each vulnerability, provide:

1. **Immediate Fix**
   - Specific code changes required
   - Before/after code examples
   - Step-by-step implementation guide

2. **Defense in Depth**
   - Additional protective measures
   - Monitoring and alerting recommendations
   - Related hardening suggestions

3. **Effort Estimation**
   - Time to implement (hours/days)
   - Required expertise level
   - Dependencies or prerequisites

4. **Verification**
   - How to test the fix
   - Regression test suggestions
   - Security test cases

Prioritize fixes by:
- Severity × Exploitability × Effort
- Quick wins (high impact, low effort) first
- Group related fixes for efficiency"""

        self._agents["remediation"] = self._factory.create_agent(
            name="remediation_expert",
            role="debugger",
            description="Generates fix strategies with code examples",
            system_prompt=self._get_system_prompt("remediation_expert", remediation_fallback),
            model_tier=self.config.remediation_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

        # 5. Compliance Mapper (Compliance Officer)
        compliance_fallback = """You are the Compliance Mapper, a security compliance specialist.

Your responsibilities:

1. **CWE Mapping**
   - Map each finding to relevant CWE IDs
   - Provide CWE category and description
   - Link to mitre.org references

2. **CVE Correlation**
   - Check if vulnerability matches known CVEs
   - Note CVE IDs when applicable
   - Reference NVD entries

3. **OWASP Classification**
   - Map to OWASP Top 10 categories
   - Reference OWASP testing guides
   - Note ASVS requirements

4. **Compliance Impact**
   - PCI-DSS requirements affected
   - HIPAA considerations (if healthcare)
   - GDPR implications (if personal data)
   - SOC2 control mappings

5. **Reporting Format**
   - Structured output for compliance reports
   - Evidence gathering suggestions
   - Audit trail recommendations

Be precise with ID references. Verify CWE/CVE mappings are accurate."""

        self._agents["compliance"] = self._factory.create_agent(
            name="compliance_mapper",
            role="analyst",
            description="Maps findings to CWE, CVE, and compliance standards",
            system_prompt=self._get_system_prompt("compliance_mapper", compliance_fallback),
            model_tier=self.config.compliance_tier,
            memory_graph_enabled=self.config.memory_graph_enabled,
            memory_graph_path=self.config.memory_graph_path,
        )

    async def _create_workflow(self) -> None:
        """Create hierarchical workflow with Security Lead as manager."""
        agents = list(self._agents.values())

        self._workflow = self._factory.create_workflow(
            name="security_audit_workflow",
            agents=agents,
            mode="hierarchical",  # Security Lead delegates to others
            description="Comprehensive security audit with coordinated analysis",
        )

    async def audit(
        self,
        target: str,
        context: dict | None = None,
    ) -> SecurityReport:
        """
        Perform a comprehensive security audit.

        Args:
            target: Path to codebase or repository URL
            context: Optional context (previous findings, focus areas, etc.)

        Returns:
            SecurityReport with all findings and recommendations
        """
        import time

        start_time = time.time()

        # Initialize if needed
        await self._initialize()

        context = context or {}
        findings: list[SecurityFinding] = []
        memory_hits = 0

        # Check Memory Graph for similar past findings
        if self._graph and self.config.memory_graph_enabled:
            try:
                similar = self._graph.find_similar(
                    {"name": f"security_audit:{target}", "description": target},
                    threshold=0.4,
                    limit=10,
                )
                if similar:
                    memory_hits = len(similar)
                    context["similar_audits"] = [
                        {
                            "name": node.name,
                            "findings_count": node.metadata.get("findings_count", 0),
                            "risk_score": node.metadata.get("risk_score", 0),
                        }
                        for node, score in similar
                    ]
                    logger.info(f"Found {memory_hits} similar past audits in Memory Graph")
            except Exception as e:
                logger.warning(f"Error querying Memory Graph: {e}")

        # Build audit task for the crew
        audit_task = self._build_audit_task(target, context)

        # Execute the workflow
        try:
            result = await self._workflow.run(audit_task, initial_state=context)

            # Parse findings from result
            findings = self._parse_findings(result)

        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            # Return partial report with error
            return SecurityReport(
                target=target,
                findings=findings,
                summary=f"Audit failed with error: {e}",
                audit_duration_seconds=time.time() - start_time,
                agents_used=list(self._agents.keys()),
                memory_graph_hits=memory_hits,
                metadata={"error": str(e)},
            )

        # Build the report
        duration = time.time() - start_time
        report = SecurityReport(
            target=target,
            findings=findings,
            summary=self._generate_summary(findings),
            audit_duration_seconds=duration,
            agents_used=list(self._agents.keys()),
            memory_graph_hits=memory_hits,
            metadata={
                "scan_depth": self.config.scan_depth,
                "framework": str(self._factory.framework.value),
            },
        )

        # Store findings in Memory Graph
        if self._graph and self.config.memory_graph_enabled and findings:
            try:
                self._graph.add_finding(
                    "security_audit_crew",
                    {
                        "type": "security_audit",
                        "name": f"audit:{target}",
                        "description": report.summary,
                        "findings_count": len(findings),
                        "risk_score": report.risk_score,
                        "critical_count": len(report.critical_findings),
                    },
                )
                self._graph._save()
            except Exception as e:
                logger.warning(f"Error storing audit in Memory Graph: {e}")

        return report

    def _build_audit_task(self, target: str, context: dict) -> str:
        """Build the audit task description for the crew."""
        depth_instructions = {
            "quick": "Focus on critical and high severity issues only. Skip detailed analysis.",
            "standard": "Cover all OWASP Top 10 categories with moderate depth.",
            "thorough": "Perform deep analysis including edge cases and complex attack chains.",
        }

        task = f"""Perform a comprehensive security audit of: {target}

Scan Depth: {self.config.scan_depth}
Instructions: {depth_instructions.get(self.config.scan_depth, depth_instructions["standard"])}

File Patterns to Include: {", ".join(self.config.include_patterns)}
File Patterns to Exclude: {", ".join(self.config.exclude_patterns)}

Workflow:
1. Security Lead coordinates the overall audit strategy
2. Vulnerability Hunter scans for security issues
3. Risk Assessor scores each finding by severity
4. Remediation Expert provides fix strategies
5. Compliance Mapper adds CWE/CVE references

For each finding, provide:
- Title and description
- Severity (critical/high/medium/low/info)
- Category (OWASP classification)
- File path and line number
- Code snippet
- Remediation steps
- CWE ID if applicable
- CVSS score

"""
        if context.get("similar_audits"):
            task += f"""
Previous Similar Audits Found: {len(context["similar_audits"])}
Consider patterns from past audits when analyzing.
"""

        if context.get("focus_areas"):
            task += f"""
Focus Areas Requested: {", ".join(context["focus_areas"])}
"""

        return task

    def _parse_findings(self, result: dict) -> list[SecurityFinding]:
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
        # This is a simplified parser - in production, use structured output
        findings = self._parse_text_findings(output)

        return findings

    def _dict_to_finding(self, data: dict) -> SecurityFinding:
        """Convert dictionary to SecurityFinding."""
        return SecurityFinding(
            title=data.get("title", "Untitled Finding"),
            description=data.get("description", ""),
            severity=Severity(data.get("severity", "medium")),
            category=FindingCategory(data.get("category", "other")),
            file_path=data.get("file_path"),
            line_number=data.get("line_number"),
            code_snippet=data.get("code_snippet"),
            remediation=data.get("remediation"),
            cwe_id=data.get("cwe_id"),
            cvss_score=data.get("cvss_score"),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
        )

    def _parse_text_findings(self, text: str) -> list[SecurityFinding]:
        """Parse findings from unstructured text output."""
        findings = []

        # Simple heuristic parsing - look for severity indicators
        severity_keywords = {
            Severity.CRITICAL: ["critical", "rce", "remote code execution"],
            Severity.HIGH: ["high", "injection", "authentication bypass"],
            Severity.MEDIUM: ["medium", "xss", "csrf"],
            Severity.LOW: ["low", "information disclosure"],
            Severity.INFO: ["info", "informational", "best practice"],
        }

        category_keywords = {
            FindingCategory.INJECTION: ["sql injection", "command injection", "ldap"],
            FindingCategory.XSS: ["xss", "cross-site scripting", "script injection"],
            FindingCategory.BROKEN_AUTH: ["authentication", "session", "password"],
            FindingCategory.SENSITIVE_DATA: ["sensitive data", "encryption", "plaintext"],
            FindingCategory.MISCONFIGURATION: ["misconfiguration", "default", "exposed"],
        }

        # Split into potential findings (very basic)
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
                for indicator in ["vulnerability", "issue", "finding", "detected"]
            ):
                if current_finding:
                    findings.append(current_finding)

                current_finding = SecurityFinding(
                    title=line[:100].strip(),
                    description=line,
                    severity=detected_severity,
                    category=detected_category,
                )

        if current_finding:
            findings.append(current_finding)

        return findings

    def _generate_summary(self, findings: list[SecurityFinding]) -> str:
        """Generate executive summary of findings."""
        if not findings:
            return "No security issues were identified during the audit."

        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high = sum(1 for f in findings if f.severity == Severity.HIGH)
        medium = sum(1 for f in findings if f.severity == Severity.MEDIUM)
        low = sum(1 for f in findings if f.severity == Severity.LOW)

        summary_parts = [f"Security audit identified {len(findings)} findings:"]

        if critical > 0:
            summary_parts.append(f"  - {critical} CRITICAL (immediate action required)")
        if high > 0:
            summary_parts.append(f"  - {high} HIGH (address within 7 days)")
        if medium > 0:
            summary_parts.append(f"  - {medium} MEDIUM (address within 30 days)")
        if low > 0:
            summary_parts.append(f"  - {low} LOW (address in next sprint)")

        # Add top categories
        by_category: dict[str, int] = {}
        for f in findings:
            cat = f.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        if by_category:
            top_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:3]
            summary_parts.append("\nTop vulnerability categories:")
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

        agents_dict: dict = {}
        stats: dict = {
            "agent_count": len(self._agents),
            "agents": agents_dict,
            "framework": self._factory.framework.value if self._factory else "unknown",
            "memory_graph_enabled": self.config.memory_graph_enabled,
        }

        for name, agent in self._agents.items():
            agents_dict[name] = {
                "role": agent.config.role if hasattr(agent, "config") else "unknown",
                "model_tier": getattr(agent.config, "model_tier", "unknown"),
            }

        return stats
