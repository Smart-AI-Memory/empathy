"""
Design Review Wizard

Evaluates architecture for trade-offs, risks, and alignment with goals.
Uses Empathy Framework Level 4 (Anticipatory) to identify future issues
and Level 5 (Systems) thinking for holistic analysis.

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


class DesignReviewWizard(BaseWizard):
    """
    Wizard for architecture and design review

    Uses:
    - Level 3: Proactively identify design patterns and anti-patterns
    - Level 4: Anticipate scalability, maintainability, and operational issues
    - Level 5: Systems thinking for holistic analysis
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a design review task"""
        design_keywords = [
            "design",
            "architecture",
            "arch",
            "review",
            "refactor",
            "scalability",
            "performance",
            "scale",
            "technical debt",
            "trade-off",
            "tradeoff",
            "decision",
            "adr",
            "system design",
        ]

        task_lower = (task.task + " " + task.context).lower()
        matches = sum(1 for keyword in design_keywords if keyword in task_lower)

        return min(matches / 2.0, 1.0)  # 2+ keywords = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute design review workflow"""

        # Step 1: Assess context
        constraints = self._extract_constraints(task)
        emotional_state = self._assess_emotional_state(task)

        # Step 2: Identify design goals
        goals = self._identify_design_goals(task)

        # Step 3: Analyze architecture (Level 3: Proactive pattern detection)
        architecture_analysis = self._analyze_architecture(task, goals)

        # Step 4: Identify trade-offs
        tradeoffs = self._identify_tradeoffs(task, architecture_analysis)

        # Step 5: Assess risks (Level 4: Anticipatory)
        risks = self._assess_design_risks(task, architecture_analysis, tradeoffs)

        # Step 6: Evaluate non-functional requirements
        nfr_assessment = self._evaluate_nfrs(task, architecture_analysis)

        # Step 7: Generate diagnosis
        diagnosis = self._create_diagnosis(architecture_analysis, tradeoffs)

        # Step 8: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="Architecture Analysis",
                content=architecture_analysis["detailed_analysis"],
            ),
            WizardArtifact(
                type="doc", title="Trade-off Analysis", content=self._format_tradeoffs(tradeoffs)
            ),
            WizardArtifact(
                type="adr",
                title="Architecture Decision Record (Draft)",
                content=self._generate_adr(task, architecture_analysis, tradeoffs),
            ),
            WizardArtifact(
                type="checklist",
                title="Design Review Checklist",
                content=self._create_review_checklist(nfr_assessment),
            ),
        ]

        # Step 9: Create plan
        plan = [
            "Review current architecture documentation",
            f"Evaluate {len(tradeoffs)} identified trade-offs",
            "Assess non-functional requirements",
            "Document key design decisions",
            "Identify refactoring opportunities",
            "Create migration plan if needed",
        ]

        # Step 10: Generate next actions
        next_actions = [
            "Schedule architecture review meeting with team",
            "Document design decisions in ADR",
            "Create proof-of-concept for risky areas",
            "Update architecture diagrams",
            "Set up monitoring for identified risks",
        ]

        # Add anticipatory actions
        anticipatory_actions = self._generate_anticipatory_actions(task)
        next_actions.extend(anticipatory_actions)

        # Step 11: Create handoffs
        handoffs = []
        if task.role in ["developer", "architect"]:
            handoffs.append(
                WizardHandoff(
                    owner="team", what="Architecture review meeting", when="Within 1 week"
                )
            )
        if "refactor" in task.task.lower():
            handoffs.append(
                WizardHandoff(
                    owner="pm",
                    what="Refactoring timeline and resource allocation",
                    when="Before starting work",
                )
            )

        # Step 12: Empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role} perspective with focus on {', '.join(goals[:2])}",
            emotional=f"Acknowledged {'high' if 'refactor' in task.task.lower() else 'normal'} complexity and technical debt concerns",
            anticipatory=f"Identified {len(risks)} future risks and provided {len(anticipatory_actions)} proactive recommendations",
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

    def _identify_design_goals(self, task: WizardTask) -> list[str]:
        """Identify design goals from task"""
        goals = []

        context_lower = task.context.lower() + " " + task.task.lower()

        goal_keywords = {
            "scalability": "Scalability",
            "scale": "Scalability",
            "performance": "Performance",
            "maintainability": "Maintainability",
            "maintain": "Maintainability",
            "security": "Security",
            "reliability": "Reliability",
            "availability": "Availability",
            "cost": "Cost efficiency",
            "developer experience": "Developer experience",
            "testing": "Testability",
        }

        for keyword, goal in goal_keywords.items():
            if keyword in context_lower and goal not in goals:
                goals.append(goal)

        if not goals:
            goals = ["Maintainability", "Scalability"]  # Default goals

        return goals

    def _analyze_architecture(self, task: WizardTask, goals: list[str]) -> dict[str, Any]:
        """Analyze architecture (Level 3: Proactive pattern detection)"""

        context_lower = task.context.lower()

        # Detect architecture patterns
        patterns = []
        if "microservice" in context_lower:
            patterns.append("Microservices")
        if "monolith" in context_lower:
            patterns.append("Monolithic")
        if "event" in context_lower or "queue" in context_lower:
            patterns.append("Event-driven")
        if "api" in context_lower and "gateway" in context_lower:
            patterns.append("API Gateway")
        if "serverless" in context_lower or "lambda" in context_lower:
            patterns.append("Serverless")

        # Detect concerns
        concerns = []
        if "database" in context_lower or "db" in context_lower:
            concerns.append("Data management")
        if "cache" in context_lower or "redis" in context_lower:
            concerns.append("Caching strategy")
        if "auth" in context_lower:
            concerns.append("Authentication/Authorization")
        if "deploy" in context_lower:
            concerns.append("Deployment strategy")

        # Generate detailed analysis
        detailed_analysis = f"""# Architecture Analysis

## Identified Patterns
{chr(10).join(f"- {p}" for p in patterns) if patterns else "- No specific patterns detected"}

## Key Concerns
{chr(10).join(f"- {c}" for c in concerns) if concerns else "- General architecture review"}

## Alignment with Goals
{chr(10).join(f"- {g}: {'Well addressed' if any(g.lower() in p.lower() for p in patterns + concerns) else 'Needs attention'}" for g in goals)}

## Architecture Assessment
Based on the context, this appears to be a {''.join(patterns[:1]) if patterns else 'standard'} architecture.

### Strengths
- Addresses core functional requirements
- {'Scalable architecture chosen' if 'microservice' in context_lower or 'serverless' in context_lower else 'Clear architecture boundaries'}

### Areas for Improvement
- {'Consider service boundaries' if 'monolith' in context_lower else 'Monitor service complexity'}
- {'Add caching layer' if 'cache' not in context_lower and 'performance' in str(goals).lower() else 'Optimize caching strategy'}
- Document key design decisions
"""

        return {
            "patterns": patterns,
            "concerns": concerns,
            "goals_alignment": dict.fromkeys(goals, "partial"),
            "detailed_analysis": detailed_analysis,
        }

    def _identify_tradeoffs(self, task: WizardTask, analysis: dict) -> list[dict[str, str]]:
        """Identify architecture trade-offs"""
        tradeoffs = []

        patterns = analysis.get("patterns", [])

        # Common trade-offs based on patterns
        if "Microservices" in patterns:
            tradeoffs.append(
                {
                    "decision": "Microservices Architecture",
                    "benefit": "Independent scalability, team autonomy, technology flexibility",
                    "cost": "Increased operational complexity, distributed system challenges, network latency",
                    "recommendation": "Consider: service mesh, centralized logging, distributed tracing",
                }
            )

        if "Monolithic" in patterns:
            tradeoffs.append(
                {
                    "decision": "Monolithic Architecture",
                    "benefit": "Simpler deployment, easier debugging, lower operational overhead",
                    "cost": "Limited scalability, tighter coupling, slower development velocity at scale",
                    "recommendation": "Consider: modular monolith pattern, domain boundaries, migration path",
                }
            )

        if "Serverless" in patterns:
            tradeoffs.append(
                {
                    "decision": "Serverless Architecture",
                    "benefit": "Zero server management, auto-scaling, pay-per-use",
                    "cost": "Cold starts, vendor lock-in, limited execution time, debugging complexity",
                    "recommendation": "Consider: function warmers, local development tools, multi-cloud strategy",
                }
            )

        if "Event-driven" in patterns:
            tradeoffs.append(
                {
                    "decision": "Event-Driven Architecture",
                    "benefit": "Loose coupling, scalability, resilience",
                    "cost": "Eventual consistency, debugging complexity, message ordering challenges",
                    "recommendation": "Consider: event schema registry, dead letter queues, idempotency",
                }
            )

        # Generic trade-off if none detected
        if not tradeoffs:
            tradeoffs.append(
                {
                    "decision": "Current Architecture Approach",
                    "benefit": "Meets immediate functional requirements",
                    "cost": "May have hidden technical debt or scalability limitations",
                    "recommendation": "Conduct thorough architecture review to identify specific trade-offs",
                }
            )

        return tradeoffs

    def _assess_design_risks(
        self, task: WizardTask, analysis: dict, tradeoffs: list[dict]
    ) -> list[WizardRisk]:
        """Assess design risks (Level 4: Anticipatory)"""
        risks = []

        # Risk based on complexity
        if len(analysis.get("patterns", [])) > 2:
            risks.append(
                WizardRisk(
                    risk="Architecture complexity may overwhelm team",
                    mitigation="Start with simpler approach, add complexity incrementally as team gains experience",
                    severity="high",
                )
            )

        # Risk based on patterns
        if "Microservices" in analysis.get("patterns", []):
            risks.append(
                WizardRisk(
                    risk="Distributed system failures and cascading issues",
                    mitigation="Implement circuit breakers, timeouts, and comprehensive monitoring",
                    severity="high",
                )
            )
            risks.append(
                WizardRisk(
                    risk="Data consistency across services",
                    mitigation="Use saga pattern or event sourcing for distributed transactions",
                    severity="medium",
                )
            )

        if "Monolithic" in analysis.get("patterns", []):
            risks.append(
                WizardRisk(
                    risk="Future scalability bottlenecks",
                    mitigation="Design with clear module boundaries, plan migration path to distributed architecture",
                    severity="medium",
                )
            )

        # General risks
        risks.append(
            WizardRisk(
                risk="Technical debt accumulation",
                mitigation="Regular architecture reviews, refactoring time in sprints, ADR documentation",
                severity="medium",
            )
        )

        risks.append(
            WizardRisk(
                risk="Knowledge silos in complex architecture",
                mitigation="Architecture documentation, team knowledge sharing sessions, pair programming",
                severity="low",
            )
        )

        return risks[:5]  # Top 5 risks

    def _evaluate_nfrs(self, task: WizardTask, analysis: dict) -> dict[str, str]:
        """Evaluate non-functional requirements"""
        return {
            "Scalability": "Review service boundaries and data partitioning strategy",
            "Performance": "Establish performance budgets and monitoring",
            "Security": "Conduct security review and threat modeling",
            "Reliability": "Define SLOs and implement health checks",
            "Maintainability": "Ensure code quality standards and documentation",
            "Observability": "Implement logging, metrics, and tracing",
        }

    def _create_diagnosis(self, analysis: dict, tradeoffs: list[dict]) -> str:
        """Create diagnosis of architecture"""
        patterns = analysis.get("patterns", [])
        pattern_str = ", ".join(patterns) if patterns else "standard"

        return f"{pattern_str} architecture with {len(tradeoffs)} key trade-offs requiring evaluation and {len(analysis.get('concerns', []))} primary concerns"

    def _format_tradeoffs(self, tradeoffs: list[dict]) -> str:
        """Format trade-offs as documentation"""
        content = "# Architecture Trade-off Analysis\n\n"

        for i, tradeoff in enumerate(tradeoffs, 1):
            content += f"## Trade-off {i}: {tradeoff['decision']}\n\n"
            content += f"### Benefits\n{tradeoff['benefit']}\n\n"
            content += f"### Costs\n{tradeoff['cost']}\n\n"
            content += f"### Recommendation\n{tradeoff['recommendation']}\n\n"
            content += "---\n\n"

        return content

    def _generate_adr(self, task: WizardTask, analysis: dict, tradeoffs: list[dict]) -> str:
        """Generate Architecture Decision Record"""
        patterns = analysis.get("patterns", ["Current approach"])
        main_pattern = patterns[0] if patterns else "Architecture"

        return f"""# Architecture Decision Record: {main_pattern}

## Status
Proposed

## Context
{task.context}

## Decision
Adopt {main_pattern} architecture to address requirements.

## Consequences

### Positive
- Addresses core functional requirements
- Aligns with team capabilities
- {tradeoffs[0]['benefit'] if tradeoffs else 'Meets immediate needs'}

### Negative
- {tradeoffs[0]['cost'] if tradeoffs else 'Requires ongoing maintenance'}
- Requires team training and documentation
- May need refactoring as requirements evolve

### Neutral
- Standard industry pattern
- Well-documented approach
- Community support available

## Trade-offs
{chr(10).join(f"- {t['decision']}: {t['benefit']} vs {t['cost']}" for t in tradeoffs[:3])}

## Alternatives Considered
[To be filled based on team discussion]

## Follow-up Actions
1. Create detailed architecture diagrams
2. Document service boundaries and contracts
3. Establish monitoring and observability
4. Plan for incremental rollout
5. Schedule regular architecture reviews

---
*Date*: [Current date]
*Participants*: [Team members]
*Status*: Draft - Requires review
"""

    def _create_review_checklist(self, nfr_assessment: dict) -> str:
        """Create design review checklist"""
        return f"""# Design Review Checklist

## Functional Requirements
- [ ] All user stories addressed
- [ ] Edge cases considered
- [ ] Error handling defined

## Non-Functional Requirements
{chr(10).join(f"- [ ] {nfr}: {assessment}" for nfr, assessment in nfr_assessment.items())}

## Architecture
- [ ] Architecture diagrams created/updated
- [ ] Service boundaries clearly defined
- [ ] Data flow documented
- [ ] Integration points identified

## Security
- [ ] Threat model created
- [ ] Authentication/authorization design reviewed
- [ ] Data encryption strategy defined
- [ ] Compliance requirements addressed

## Scalability
- [ ] Load estimates documented
- [ ] Scaling strategy defined
- [ ] Database sharding/partitioning planned
- [ ] Caching strategy defined

## Reliability
- [ ] SLOs defined
- [ ] Error handling strategy
- [ ] Retry/timeout policies
- [ ] Circuit breaker patterns

## Operability
- [ ] Deployment strategy defined
- [ ] Monitoring and alerting planned
- [ ] Logging strategy defined
- [ ] Disaster recovery plan

## Documentation
- [ ] ADR created
- [ ] README updated
- [ ] API documentation
- [ ] Runbooks for operations

## Team Readiness
- [ ] Team has necessary skills
- [ ] Training plan if needed
- [ ] On-call procedures defined
- [ ] Knowledge transfer plan

---
*Review Date*: [Date]
*Reviewers*: [Names]
"""
