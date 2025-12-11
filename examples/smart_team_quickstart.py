#!/usr/bin/env python3
"""
Smart Team Quickstart - Multi-Agent Project Analyzer

This is NOT a "hello world" - it's a genuinely useful tool.

Describe what you want to build, and a team of AI agents will:
1. Break it into components (Architect)
2. Identify risks and issues (Critic)
3. Suggest concrete first steps (Implementer)

All agents coordinate through shared short-term memory,
discovering and building on each other's insights.

Usage:
    python smart_team_quickstart.py

Or import and use programmatically:
    from smart_team_quickstart import analyze_project
    result = analyze_project("I want to build a REST API for user authentication")
"""

import re
from dataclasses import dataclass

# Import Empathy Framework
from empathy_os import AccessTier, EmpathyOS, TeamSession, get_redis_memory


@dataclass
class Component:
    """A component identified by the Architect."""

    name: str
    description: str
    complexity: str  # low, medium, high
    dependencies: list[str]


@dataclass
class Risk:
    """A risk identified by the Critic."""

    title: str
    severity: str  # low, medium, high, critical
    mitigation: str
    affects_components: list[str]


@dataclass
class Step:
    """A concrete step suggested by the Implementer."""

    order: int
    action: str
    rationale: str
    estimated_effort: str  # quick, moderate, significant


@dataclass
class ProjectAnalysis:
    """Complete analysis from all agents."""

    project_description: str
    components: list[Component]
    risks: list[Risk]
    first_steps: list[Step]
    agent_insights: dict[str, str]  # What each agent discovered


class ArchitectAgent:
    """Breaks projects into logical components."""

    def __init__(self, empathy: EmpathyOS):
        self.empathy = empathy
        self.agent_id = "architect"

    def analyze(self, description: str) -> list[Component]:
        """Identify components in the project description."""
        components = []

        # Pattern matching for common architectural elements
        patterns = {
            "api": (
                r"\b(api|endpoint|rest|graphql|server)\b",
                "API Layer",
                "Handles external requests and responses",
            ),
            "auth": (
                r"\b(auth|login|user|permission|token|jwt|signup|register)\b",
                "Authentication",
                "User identity and access control",
            ),
            "database": (
                r"\b(database|db|storage|persist|save|store|postgres|mysql|mongo|sql)\b",
                "Data Layer",
                "Persistent storage and data management",
            ),
            "ui": (
                r"\b(ui|frontend|interface|page|component|react|vue|site|web|app)\b",
                "User Interface",
                "Visual components and user interactions",
            ),
            "cache": (
                r"\b(cache|redis|memory|fast|performance)\b",
                "Caching Layer",
                "Performance optimization through caching",
            ),
            "queue": (
                r"\b(queue|async|background|job|worker|task)\b",
                "Task Queue",
                "Asynchronous processing and job management",
            ),
            "notification": (
                r"\b(notification|email|alert|webhook|sms)\b",
                "Notifications",
                "User alerts and external integrations",
            ),
            "payment": (
                r"\b(payment|checkout|billing|stripe|paypal|commerce|purchase|subscription)\b",
                "Payment Processing",
                "Financial transactions and billing",
            ),
            "cart": (
                r"\b(cart|order|basket|shopping)\b",
                "Shopping Cart",
                "Order management and checkout flow",
            ),
            "inventory": (
                r"\b(inventory|stock|product|catalog|item)\b",
                "Inventory System",
                "Product catalog and stock management",
            ),
            "realtime": (
                r"\b(realtime|real-time|socket|websocket|chat|live|stream)\b",
                "Real-Time System",
                "Live updates and bidirectional communication",
            ),
            "search": (
                r"\b(search|filter|query|elasticsearch|find)\b",
                "Search Engine",
                "Content discovery and filtering",
            ),
            "files": (
                r"\b(file|upload|image|media|attachment|document)\b",
                "File Storage",
                "Media uploads and document management",
            ),
        }

        desc_lower = description.lower()
        found_components = []

        for key, (pattern, name, desc) in patterns.items():
            if re.search(pattern, desc_lower, re.IGNORECASE):
                # Determine complexity based on co-occurring terms
                complexity = "medium"
                if key == "auth" and "oauth" in desc_lower:
                    complexity = "high"
                elif key == "database" and any(
                    x in desc_lower for x in ["scale", "distributed", "replica"]
                ):
                    complexity = "high"
                elif key == "ui" and "responsive" in desc_lower:
                    complexity = "medium"

                found_components.append(key)
                components.append(
                    Component(name=name, description=desc, complexity=complexity, dependencies=[])
                )

        # Add dependencies based on common patterns
        for comp in components:
            if comp.name == "API Layer" and any(c.name == "Authentication" for c in components):
                comp.dependencies.append("Authentication")
            if comp.name == "Authentication" and any(c.name == "Data Layer" for c in components):
                comp.dependencies.append("Data Layer")
            if comp.name == "Caching Layer":
                comp.dependencies.append("Data Layer")

        # If nothing detected, add generic components
        if not components:
            components = [
                Component("Core Logic", "Main application functionality", "medium", []),
                Component("Configuration", "Application settings and environment", "low", []),
            ]

        # Store findings in short-term memory for other agents
        self.empathy.stash(
            "architect_components",
            {
                "count": len(components),
                "names": [c.name for c in components],
                "high_complexity": [c.name for c in components if c.complexity == "high"],
            },
        )

        # Signal completion
        self.empathy.send_signal(
            "analysis_complete", {"agent": self.agent_id, "components_found": len(components)}
        )

        return components


class CriticAgent:
    """Identifies risks and potential issues."""

    def __init__(self, empathy: EmpathyOS):
        self.empathy = empathy
        self.agent_id = "critic"

    def analyze(self, description: str, components: list[Component]) -> list[Risk]:
        """Identify risks based on description and components."""
        risks = []
        desc_lower = description.lower()

        # Check architect's findings
        arch_findings = self.empathy.retrieve("architect_components", agent_id="architect")
        high_complexity_components = (
            arch_findings.get("high_complexity", []) if arch_findings else []
        )

        # Risk patterns
        if any(c.name == "Authentication" for c in components):
            risks.append(
                Risk(
                    title="Security vulnerabilities in auth",
                    severity="high",
                    mitigation="Use established auth libraries (Passport, Auth0). Never store plaintext passwords.",
                    affects_components=["Authentication"],
                )
            )

        if any(c.name == "Data Layer" for c in components):
            risks.append(
                Risk(
                    title="Data migration complexity",
                    severity="medium",
                    mitigation="Design schema migrations from day one. Use versioned migrations.",
                    affects_components=["Data Layer"],
                )
            )

        if any(c.name == "Payment Processing" for c in components):
            risks.append(
                Risk(
                    title="PCI compliance requirements",
                    severity="critical",
                    mitigation="Use Stripe/PayPal APIs - never store card numbers. Implement proper error handling for failed payments.",
                    affects_components=["Payment Processing"],
                )
            )

        if any(c.name == "Shopping Cart" for c in components):
            risks.append(
                Risk(
                    title="Cart abandonment and state management",
                    severity="medium",
                    mitigation="Persist cart state server-side. Implement recovery emails. Handle concurrent modifications.",
                    affects_components=["Shopping Cart"],
                )
            )

        if any(c.name == "Inventory System" for c in components):
            risks.append(
                Risk(
                    title="Race conditions in stock management",
                    severity="high",
                    mitigation="Use database transactions for stock updates. Implement optimistic locking. Test concurrent purchases.",
                    affects_components=["Inventory System"],
                )
            )

        if any(c.name == "Real-Time System" for c in components):
            risks.append(
                Risk(
                    title="WebSocket scaling complexity",
                    severity="medium",
                    mitigation="Plan for horizontal scaling (Redis pub/sub). Handle reconnection gracefully. Test with many concurrent connections.",
                    affects_components=["Real-Time System"],
                )
            )

        if any(c.name == "File Storage" for c in components):
            risks.append(
                Risk(
                    title="File upload security risks",
                    severity="high",
                    mitigation="Validate file types server-side. Scan for malware. Use CDN/S3 - don't store on app server.",
                    affects_components=["File Storage"],
                )
            )

        if len(components) > 4:
            risks.append(
                Risk(
                    title="Scope creep - too many components",
                    severity="medium",
                    mitigation="Prioritize MVP. Build core functionality first, add features incrementally.",
                    affects_components=[c.name for c in components[:2]],
                )
            )

        if high_complexity_components:
            risks.append(
                Risk(
                    title=f"High complexity in {', '.join(high_complexity_components)}",
                    severity="high",
                    mitigation="Consider breaking into smaller services or using proven frameworks.",
                    affects_components=high_complexity_components,
                )
            )

        if "scale" in desc_lower or "million" in desc_lower:
            risks.append(
                Risk(
                    title="Premature optimization for scale",
                    severity="medium",
                    mitigation="Build for current needs first. Design for scale, implement when needed.",
                    affects_components=["All"],
                )
            )

        # Always add at least one risk (there's always something)
        if not risks:
            risks.append(
                Risk(
                    title="Undefined requirements",
                    severity="low",
                    mitigation="Document specific requirements before building. Define success criteria.",
                    affects_components=["Core Logic"],
                )
            )

        # Store findings for implementer
        self.empathy.stash(
            "critic_risks",
            {
                "count": len(risks),
                "high_severity": [r.title for r in risks if r.severity in ["high", "critical"]],
                "blocked_components": list(
                    {c for r in risks for c in r.affects_components if r.severity == "high"}
                ),
            },
        )

        self.empathy.send_signal(
            "analysis_complete", {"agent": self.agent_id, "risks_found": len(risks)}
        )

        return risks


class ImplementerAgent:
    """Suggests concrete first steps."""

    def __init__(self, empathy: EmpathyOS):
        self.empathy = empathy
        self.agent_id = "implementer"

    def analyze(
        self, description: str, components: list[Component], risks: list[Risk]
    ) -> list[Step]:
        """Generate concrete first steps based on components and risks."""
        steps = []

        # Get insights from other agents
        _arch_findings = self.empathy.retrieve("architect_components", agent_id="architect")
        critic_findings = self.empathy.retrieve("critic_risks", agent_id="critic")

        blocked = critic_findings.get("blocked_components", []) if critic_findings else []
        high_risks = critic_findings.get("high_severity", []) if critic_findings else []

        step_num = 1

        # Step 1: Always start with setup
        steps.append(
            Step(
                order=step_num,
                action="Set up project structure and version control",
                rationale="Foundation for all other work. Enables collaboration and rollback.",
                estimated_effort="quick",
            )
        )
        step_num += 1

        # Step 2: Address high-severity risks first
        if high_risks:
            steps.append(
                Step(
                    order=step_num,
                    action=f"Research and plan mitigation for: {high_risks[0]}",
                    rationale="Addressing high risks early prevents costly rework later.",
                    estimated_effort="moderate",
                )
            )
            step_num += 1

        # Step 3: Start with lowest-dependency component
        independent = [c for c in components if not c.dependencies and c.name not in blocked]
        if independent:
            easiest = min(
                independent, key=lambda c: {"low": 0, "medium": 1, "high": 2}[c.complexity]
            )
            steps.append(
                Step(
                    order=step_num,
                    action=f"Implement {easiest.name}: {easiest.description}",
                    rationale=f"No dependencies, {easiest.complexity} complexity. Quick win builds momentum.",
                    estimated_effort="moderate" if easiest.complexity != "low" else "quick",
                )
            )
            step_num += 1

        # Step 4: If auth exists, do it early (but after foundation)
        if any(c.name == "Authentication" for c in components) and "Authentication" not in blocked:
            steps.append(
                Step(
                    order=step_num,
                    action="Set up authentication with a proven library",
                    rationale="Many features depend on auth. Using a library reduces security risk.",
                    estimated_effort="moderate",
                )
            )
            step_num += 1

        # Step 5: Data layer if present
        if any(c.name == "Data Layer" for c in components):
            steps.append(
                Step(
                    order=step_num,
                    action="Design database schema with migrations",
                    rationale="Data model shapes everything else. Migrations enable safe changes.",
                    estimated_effort="moderate",
                )
            )
            step_num += 1

        # Final step: Testing strategy
        steps.append(
            Step(
                order=step_num,
                action="Write tests for first implemented component",
                rationale="Early testing catches issues before they compound. Sets quality standard.",
                estimated_effort="quick",
            )
        )

        # Store final synthesis
        self.empathy.stash(
            "implementer_plan",
            {
                "total_steps": len(steps),
                "quick_wins": len([s for s in steps if s.estimated_effort == "quick"]),
                "first_action": steps[0].action if steps else None,
            },
        )

        self.empathy.send_signal(
            "analysis_complete", {"agent": self.agent_id, "steps_generated": len(steps)}
        )

        return steps


def analyze_project(description: str, verbose: bool = True) -> ProjectAnalysis:
    """
    Analyze a project description using a team of coordinating agents.

    Args:
        description: What you want to build
        verbose: Print progress as agents work

    Returns:
        ProjectAnalysis with components, risks, and recommended steps
    """
    # Initialize shared memory - gracefully fall back to mock if Redis unavailable
    try:
        memory = get_redis_memory()
        # Test connection immediately
        stats = memory.get_stats()
        mode = stats["mode"]
    except Exception:
        # Redis not available - use mock mode (works perfectly for demos)
        memory = get_redis_memory(use_mock=True)
        mode = "mock (Redis not needed for demo)"

    if verbose:
        print(f"\n{'='*60}")
        print("SMART TEAM PROJECT ANALYZER")
        print(f"{'='*60}")
        print(f"Memory: {mode}")
        print(f"\nAnalyzing: {description[:100]}{'...' if len(description) > 100 else ''}")
        print(f"{'='*60}\n")

    # Create team session
    session = TeamSession(
        memory,
        session_id=f"project_analysis_{hash(description) % 10000}",
        purpose="Analyze project requirements",
    )

    # Create agents with appropriate access levels
    architect_empathy = EmpathyOS(
        user_id="architect",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR,
        target_level=4,
    )

    critic_empathy = EmpathyOS(
        user_id="critic",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR,
        target_level=4,
    )

    implementer_empathy = EmpathyOS(
        user_id="implementer",
        short_term_memory=memory,
        access_tier=AccessTier.VALIDATOR,  # Can synthesize final recommendations
        target_level=4,
    )

    # Register with session
    session.add_agent("architect")
    session.add_agent("critic")
    session.add_agent("implementer")

    # Share initial context
    session.share("project_description", description)

    # Create agent instances
    architect = ArchitectAgent(architect_empathy)
    critic = CriticAgent(critic_empathy)
    implementer = ImplementerAgent(implementer_empathy)

    # Phase 1: Architect identifies components
    if verbose:
        print("Phase 1: Architect analyzing structure...")
    components = architect.analyze(description)
    if verbose:
        print(f"         Found {len(components)} components\n")

    # Phase 2: Critic identifies risks (using architect's findings)
    if verbose:
        print("Phase 2: Critic identifying risks...")
    risks = critic.analyze(description, components)
    if verbose:
        print(f"         Found {len(risks)} risks\n")

    # Phase 3: Implementer creates action plan (using both)
    if verbose:
        print("Phase 3: Implementer creating action plan...")
    steps = implementer.analyze(description, components, risks)
    if verbose:
        print(f"         Generated {len(steps)} steps\n")

    # Gather agent insights
    insights = {
        "architect": f"Identified {len(components)} components with {len([c for c in components if c.complexity == 'high'])} high-complexity areas",
        "critic": f"Found {len(risks)} risks, {len([r for r in risks if r.severity == 'high'])} high-severity",
        "implementer": f"Created {len(steps)}-step plan with {len([s for s in steps if s.estimated_effort == 'quick'])} quick wins",
    }

    return ProjectAnalysis(
        project_description=description,
        components=components,
        risks=risks,
        first_steps=steps,
        agent_insights=insights,
    )


def print_analysis(analysis: ProjectAnalysis):
    """Pretty print the analysis results."""
    print(f"\n{'='*60}")
    print("ANALYSIS RESULTS")
    print(f"{'='*60}")

    # Components
    print(f"\n{'COMPONENTS':-^60}")
    for comp in analysis.components:
        deps = f" (depends on: {', '.join(comp.dependencies)})" if comp.dependencies else ""
        print(f"\n  [{comp.complexity.upper()}] {comp.name}")
        print(f"        {comp.description}{deps}")

    # Risks
    print(f"\n{'RISKS':-^60}")
    for risk in analysis.risks:
        severity_icon = {"low": ".", "medium": "!", "high": "!!", "critical": "!!!"}[risk.severity]
        print(f"\n  [{severity_icon}] {risk.title}")
        print(f"        Mitigation: {risk.mitigation}")
        print(f"        Affects: {', '.join(risk.affects_components)}")

    # Action Plan
    print(f"\n{'RECOMMENDED FIRST STEPS':-^60}")
    for step in analysis.first_steps:
        effort_icon = {"quick": "~", "moderate": "~~", "significant": "~~~"}[step.estimated_effort]
        print(f"\n  {step.order}. [{effort_icon}] {step.action}")
        print(f"        Why: {step.rationale}")

    # Agent Summary
    print(f"\n{'AGENT INSIGHTS':-^60}")
    for agent, insight in analysis.agent_insights.items():
        print(f"  {agent.capitalize()}: {insight}")

    print(f"\n{'='*60}\n")


def main():
    """Interactive mode - ask user what they want to build."""
    print("\n" + "=" * 60)
    print("SMART TEAM PROJECT ANALYZER")
    print("=" * 60)
    print("\nDescribe what you want to build, and our team of AI agents")
    print("will analyze it together, sharing insights through")
    print("coordinated short-term memory.\n")

    # Get user input
    print("What do you want to build?")
    print("(Examples: 'A REST API for user authentication',")
    print("          'An e-commerce site with shopping cart',")
    print("          'A real-time chat application')\n")

    description = input("> ").strip()

    if not description:
        # Demo mode with example project
        description = "A REST API with user authentication, rate limiting, and PostgreSQL database"
        print(f"\n[Demo mode] Using example: {description}")

    # Run analysis
    analysis = analyze_project(description)

    # Print results
    print_analysis(analysis)

    # Show coordination stats (graceful fallback)
    try:
        memory = get_redis_memory()
        stats = memory.get_stats()
        keys = stats.get("keys", stats.get("total_keys", 0))
        print(f"\nCoordination: {keys} shared memory items created")
        print(f"Memory mode: {stats.get('mode', 'unknown')}")
    except Exception:
        print("\nCoordination complete (mock mode - no Redis needed for demo)")
        print("Tip: Install Redis for persistent multi-agent memory")


if __name__ == "__main__":
    main()
