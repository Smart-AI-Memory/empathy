"""
Agent Orchestration Wizard - Level 4 Anticipatory Empathy

Alerts developers when multi-agent system complexity will become unmanageable.

In our experience building AI Nurse Florence with LangGraph multi-agent systems,
we learned that agent coordination complexity grows non-linearly. This wizard
detects when simple orchestration patterns will fail at scale.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from empathy_os.plugins import BaseWizard


class AgentOrchestrationWizard(BaseWizard):
    """
    Level 4 Anticipatory: Predicts multi-agent coordination issues.

    What We Learned Building Multi-Agent Systems:
    - Simple sequential agents scale fine to 3-5 agents
    - Parallel agent coordination needs explicit state management at 5+
    - Agent-to-agent communication requires structured protocols at 7+
    - Without planning, refactoring happens around 10 agents (painful)
    """

    def __init__(self):
        super().__init__(
            name="Agent Orchestration Wizard",
            domain="software",
            empathy_level=4,
            category="ai_development",
        )

    def get_required_context(self) -> list[str]:
        """Required context for analysis"""
        return [
            "agent_definitions",  # Agent classes/configs
            "orchestration_code",  # Code that coordinates agents
            "project_path",  # Project root
        ]

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze agent orchestration patterns and predict coordination issues.

        In our experience: Multi-agent complexity sneaks up fast.
        By agent #7-10, you need formal orchestration or face refactoring.
        """
        self.validate_context(context)

        agents = context["agent_definitions"]
        orchestration = context["orchestration_code"]

        # Current issues
        issues = await self._analyze_orchestration_patterns(agents, orchestration)

        # Level 4: Predict future coordination breakdowns
        predictions = await self._predict_orchestration_complexity(agents, orchestration, context)

        recommendations = self._generate_recommendations(issues, predictions)
        patterns = self._extract_patterns(issues, predictions)

        return {
            "issues": issues,
            "predictions": predictions,
            "recommendations": recommendations,
            "patterns": patterns,
            "confidence": 0.85,
            "metadata": {
                "wizard": self.name,
                "empathy_level": self.empathy_level,
                "agent_count": len(agents),
                "orchestration_complexity": self._assess_complexity(orchestration),
            },
        }

    async def _analyze_orchestration_patterns(
        self, agents: list[dict], orchestration: list[str]
    ) -> list[dict[str, Any]]:
        """Analyze current orchestration patterns"""
        issues = []

        agent_count = len(agents)

        # Issue: No state management with multiple agents
        if agent_count > 3 and not self._has_state_management(orchestration):
            issues.append(
                {
                    "severity": "warning",
                    "type": "missing_state_management",
                    "message": (
                        f"You have {agent_count} agents without centralized state management. "
                        "In our experience, agent coordination becomes unreliable beyond 3 agents "
                        "without explicit state tracking."
                    ),
                    "suggestion": "Implement shared state pattern (e.g., LangGraph StateGraph, custom State class)",
                }
            )

        # Issue: No error handling between agents
        if not self._has_agent_error_handling(orchestration):
            issues.append(
                {
                    "severity": "warning",
                    "type": "missing_error_handling",
                    "message": (
                        "No agent-level error handling detected. When one agent fails, "
                        "entire pipeline crashes. In our experience, this creates brittle systems."
                    ),
                    "suggestion": "Add try-except wrappers, fallback agents, retry logic",
                }
            )

        # Issue: Circular agent dependencies
        if self._detect_circular_dependencies(agents):
            issues.append(
                {
                    "severity": "error",
                    "type": "circular_dependencies",
                    "message": (
                        "Circular dependencies detected between agents. "
                        "This creates deadlocks and unpredictable behavior."
                    ),
                    "suggestion": "Restructure agent graph to be acyclic (DAG)",
                }
            )

        # Issue: No agent communication protocol
        if agent_count > 5 and not self._has_communication_protocol(agents):
            issues.append(
                {
                    "severity": "info",
                    "type": "ad_hoc_communication",
                    "message": (
                        f"{agent_count} agents with ad-hoc communication. "
                        "In our experience, structured protocols become essential beyond 5 agents."
                    ),
                    "suggestion": "Define message schemas, use TypedDict for agent inputs/outputs",
                }
            )

        return issues

    async def _predict_orchestration_complexity(
        self, agents: list[dict], orchestration: list[str], full_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Level 4: Predict when orchestration will break down.

        Based on our experience: Coordination complexity = O(n²) with agents.
        """
        predictions = []

        agent_count = len(agents)

        # Pattern 1: Approaching complexity threshold
        if 7 <= agent_count <= 12:
            predictions.append(
                {
                    "type": "orchestration_complexity_threshold",
                    "alert": (
                        f"You have {agent_count} agents. In our experience, multi-agent systems "
                        "become difficult to manage around 10 agents without formal orchestration. "
                        "Alert: Design orchestration framework before complexity compounds."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Adopt orchestration framework (LangGraph, CrewAI, custom)",
                        "Define agent state machine explicitly",
                        "Implement agent registry (dynamic agent discovery)",
                        "Add agent performance monitoring",
                        "Create agent testing framework",
                    ],
                    "reasoning": (
                        f"Coordination complexity: {agent_count} agents = "
                        f"{agent_count * (agent_count - 1) // 2} potential interactions. "
                        "We hit refactoring wall at 10 agents. Proactive design prevents crisis."
                    ),
                    "personal_experience": (
                        "Building AI Nurse Florence, we started with 3 agents (simple sequence). "
                        "By agent 7, we needed LangGraph StateGraph. By agent 12, we needed "
                        "full orchestration framework. Wish we'd designed for it earlier."
                    ),
                }
            )

        # Pattern 2: Sequential agents that should be parallel
        if agent_count > 5 and self._all_sequential(orchestration):
            predictions.append(
                {
                    "type": "sequential_bottleneck",
                    "alert": (
                        f"{agent_count} agents running sequentially. In our experience, "
                        "sequential execution becomes a bottleneck. Alert: Identify parallelization "
                        "opportunities before performance degrades."
                    ),
                    "probability": "medium-high",
                    "impact": "medium",
                    "prevention_steps": [
                        "Analyze agent dependency graph",
                        "Identify independent agents (can run parallel)",
                        "Implement parallel execution (asyncio.gather, ThreadPoolExecutor)",
                        "Add result aggregation layer",
                    ],
                    "reasoning": (
                        "Many agents have no dependencies on each other. "
                        "Sequential execution leaves performance on table."
                    ),
                }
            )

        # Pattern 3: Growing agent communication overhead
        if agent_count > 6:
            predictions.append(
                {
                    "type": "communication_overhead",
                    "alert": (
                        f"With {agent_count} agents, communication overhead grows quadratically. "
                        "In our experience, agent-to-agent communication becomes bottleneck. "
                        "Alert: Implement efficient communication patterns."
                    ),
                    "probability": "medium",
                    "impact": "medium",
                    "prevention_steps": [
                        "Use pub-sub pattern (agents subscribe to relevant messages only)",
                        "Implement message routing (don't broadcast everything)",
                        "Add message queues for async communication",
                        "Create agent isolation (agents don't need to know about all others)",
                    ],
                    "reasoning": (
                        f"Full mesh communication: {agent_count}² = {agent_count ** 2} channels. "
                        "Selective communication dramatically reduces overhead."
                    ),
                }
            )

        # Pattern 4: No agent versioning strategy
        if agent_count > 4 and not self._has_agent_versioning(agents):
            predictions.append(
                {
                    "type": "agent_version_chaos",
                    "alert": (
                        "No agent versioning detected. In our experience, as agents evolve, "
                        "breaking changes cause cascade failures. Alert: Implement versioning "
                        "before inter-agent contracts become implicit."
                    ),
                    "probability": "medium-high",
                    "impact": "high",
                    "prevention_steps": [
                        "Add version to each agent (semantic versioning)",
                        "Define agent API contracts (input/output schemas)",
                        "Implement compatibility checks",
                        "Create agent migration paths for breaking changes",
                    ],
                    "reasoning": (
                        "When agent A changes output format, agent B breaks. "
                        "Versioning prevents cascade failures."
                    ),
                }
            )

        # Pattern 5: Missing observability
        if agent_count > 5 and not self._has_observability(orchestration):
            predictions.append(
                {
                    "type": "orchestration_black_box",
                    "alert": (
                        f"With {agent_count} agents, you have limited visibility into orchestration flow. "
                        "In our experience, debugging multi-agent issues without observability is extremely difficult. "
                        "Alert: Add observability before issues become impossible to diagnose."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Add structured logging (agent name, inputs, outputs, timing)",
                        "Implement distributed tracing (correlate agent executions)",
                        "Create agent execution visualizer (see flow in real-time)",
                        "Add performance metrics per agent",
                        "Build debugging tools (replay agent execution)",
                    ],
                    "reasoning": (
                        "Multi-agent debugging: 'Which agent failed? Why? With what input?' "
                        "Impossible to answer without observability."
                    ),
                    "personal_experience": (
                        "We spent 3 days debugging an agent cascade failure. Root cause: "
                        "Agent #4 was receiving null from Agent #2. No logging made this "
                        "a nightmare. Never again."
                    ),
                }
            )

        return predictions

    def _generate_recommendations(self, issues: list[dict], predictions: list[dict]) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Critical issues first
        critical = [i for i in issues if i.get("severity") == "error"]
        if critical:
            recommendations.append(
                f"[CRITICAL] Fix {len(critical)} critical orchestration issues immediately"
            )

        # High-impact predictions
        for pred in predictions:
            if pred.get("impact") == "high":
                recommendations.append(f"\n[ALERT] {pred['alert']}")
                if "personal_experience" in pred:
                    recommendations.append(f"Experience: {pred['personal_experience']}")
                recommendations.append("Prevention steps:")
                for i, step in enumerate(pred["prevention_steps"][:3], 1):
                    recommendations.append(f"  {i}. {step}")

        return recommendations

    def _extract_patterns(
        self, issues: list[dict], predictions: list[dict]
    ) -> list[dict[str, Any]]:
        """Extract cross-domain patterns"""
        return [
            {
                "pattern_type": "coordination_complexity_threshold",
                "description": (
                    "Systems with multiple coordinating components hit complexity threshold "
                    "around 7-10 components. Formal orchestration becomes essential."
                ),
                "domain_agnostic": True,
                "applicable_to": [
                    "Multi-agent AI systems",
                    "Microservices architecture",
                    "Distributed systems",
                    "Team coordination (humans)",
                    "Clinical care coordination (healthcare)",
                ],
                "threshold": "7-10 components",
                "solution": "Adopt formal orchestration framework before threshold",
            }
        ]

    # Helper methods

    def _has_state_management(self, orchestration: list[str]) -> bool:
        """Check for centralized state management"""
        for file_path in orchestration:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content
                        for kw in ["StateGraph", "AgentState", "shared_state", "TypedDict"]
                    ):
                        return True
            except OSError:
                pass
        return False

    def _has_agent_error_handling(self, orchestration: list[str]) -> bool:
        """Check for agent-level error handling"""
        for file_path in orchestration:
            try:
                with open(file_path) as f:
                    content = f.read()
                    # Look for error handling patterns
                    if "try:" in content and "agent" in content.lower():
                        return True
            except OSError:
                pass
        return False

    def _detect_circular_dependencies(self, agents: list[dict]) -> bool:
        """Detect circular dependencies between agents"""
        # Simplified detection - would need actual dependency analysis
        # For now, just check if agents reference each other
        _agent_names = [a.get("name", "") for a in agents]

        for agent in agents:
            deps = agent.get("dependencies", [])
            if agent.get("name") in deps:
                return True  # Self-dependency
        return False

    def _has_communication_protocol(self, agents: list[dict]) -> bool:
        """Check for structured communication protocol"""
        # Look for message schemas, TypedDict, etc.
        for agent in agents:
            if "message_schema" in agent or "input_schema" in agent:
                return True
        return False

    def _assess_complexity(self, orchestration: list[str]) -> str:
        """Assess orchestration complexity"""
        if len(orchestration) == 0:
            return "none"
        elif len(orchestration) <= 2:
            return "low"
        elif len(orchestration) <= 5:
            return "medium"
        else:
            return "high"

    def _all_sequential(self, orchestration: list[str]) -> bool:
        """Check if all agents run sequentially"""
        for file_path in orchestration:
            try:
                with open(file_path) as f:
                    content = f.read()
                    # Look for parallel execution indicators
                    if any(
                        kw in content
                        for kw in ["asyncio.gather", "ThreadPool", "parallel", "concurrent"]
                    ):
                        return False
            except OSError:
                pass
        return True

    def _has_agent_versioning(self, agents: list[dict]) -> bool:
        """Check if agents have version information"""
        for agent in agents:
            if "version" in agent or "api_version" in agent:
                return True
        return False

    def _has_observability(self, orchestration: list[str]) -> bool:
        """Check for observability features"""
        for file_path in orchestration:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content for kw in ["logger", "trace", "span", "metrics", "telemetry"]
                    ):
                        return True
            except OSError:
                pass
        return False
