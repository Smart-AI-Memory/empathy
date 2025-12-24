"""
Leverage Point Analysis for System Interventions

Identifies high-leverage intervention points based on Donella Meadows's
seminal work "Leverage Points: Places to Intervene in a System".

Leverage points are places within a complex system where a small shift
can produce big changes in system behavior.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class LeverageLevel(IntEnum):
    """
    Donella Meadows's 12 Leverage Points (ordered by effectiveness)

    Higher numbers = More effective leverage points
    Lower numbers = Less effective (but often easier to implement)
    """

    # Low leverage (easy to change, small impact)
    PARAMETERS = 1  # Constants, numbers (least effective)
    BUFFERS = 2  # Stabilizing stocks relative to flows
    STOCK_FLOW = 3  # Physical structure of system
    DELAYS = 4  # Length of delays relative to change rate
    BALANCING_LOOPS = 5  # Strength of negative feedback loops
    REINFORCING_LOOPS = 6  # Strength of positive feedback loops

    # Medium leverage
    INFORMATION_FLOWS = 7  # Structure of information flows
    RULES = 8  # Rules of the system (incentives, constraints)
    SELF_ORGANIZATION = 9  # Power to add/change system structure

    # High leverage (hard to change, huge impact)
    GOALS = 10  # Goals of the system
    PARADIGM = 11  # Mindset or paradigm out of which system arises
    TRANSCEND_PARADIGM = 12  # Power to transcend paradigms (most effective)


@dataclass
class LeveragePoint:
    """
    A specific leverage point identified in the system

    Represents a place where intervention can create significant change
    in system behavior.
    """

    level: LeverageLevel
    description: str
    problem_domain: str
    impact_potential: float = 0.5  # 0.0-1.0
    implementation_difficulty: float = 0.5  # 0.0-1.0
    current_state: str | None = None
    proposed_intervention: str | None = None
    expected_outcomes: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


class LeveragePointAnalyzer:
    """
    Identifies high-leverage intervention points in AI-human systems

    Based on Donella Meadows's 12 leverage points. Helps identify where
    to intervene in a system for maximum effectiveness.

    **The 12 Leverage Points (in increasing order of effectiveness):**

    1. **Parameters**: Constants, numbers (e.g., change tax rate)
       - Least effective but easiest to change

    2. **Buffers**: Size of stabilizing stocks
       - Example: inventory sizes, account balances

    3. **Stock-Flow Structure**: Physical system structure
       - Example: road networks, factories

    4. **Delays**: Length of delays relative to rate of change
       - Example: feedback delay in learning systems

    5. **Balancing Feedback Loops**: Strength of stabilizing loops
       - Example: quality control mechanisms

    6. **Reinforcing Feedback Loops**: Strength of amplifying loops
       - Example: compound interest, viral growth

    7. **Information Flows**: Structure of information flows
       - Example: transparency, data access

    8. **Rules**: Incentives, punishments, constraints
       - Example: laws, policies, protocols

    9. **Self-Organization**: Power to evolve system structure
       - Example: ability to create new rules

    10. **Goals**: Purpose or function of the system
        - Example: shift from growth to sustainability

    11. **Paradigm**: Mindset underlying the system
        - Example: worldview, shared assumptions

    12. **Transcending Paradigms**: Keep perspective on all paradigms
        - Most effective but hardest to achieve

    Example:
        >>> analyzer = LeveragePointAnalyzer()
        >>> problem = {
        ...     "class": "documentation_burden",
        ...     "description": "Developers spend 40% time on repetitive docs",
        ...     "instances": 18
        ... }
        >>> points = analyzer.find_leverage_points(problem)
        >>> for point in points:
        ...     print(f"{point.level.name}: {point.description}")
    """

    def __init__(self):
        """Initialize LeveragePointAnalyzer"""
        self.identified_points: list[LeveragePoint] = []

    def find_leverage_points(self, problem_class: dict[str, Any]) -> list[LeveragePoint]:
        """
        Find high-leverage intervention points for a problem class

        Analyzes the problem and identifies leverage points at different
        levels of the Meadows hierarchy.

        Args:
            problem_class: Dict with keys:
                - class: Problem category (e.g., "documentation_burden")
                - description: Problem description
                - instances: Number of occurrences (optional)
                - context: Additional context (optional)

        Returns:
            List of leverage points, ranked by effectiveness

        Example:
            >>> problem = {
            ...     "class": "trust_deficit",
            ...     "description": "Users don't trust AI recommendations",
            ...     "instances": 50
            ... }
            >>> points = analyzer.find_leverage_points(problem)
        """
        points: list[LeveragePoint] = []
        problem_type = problem_class.get("class", "unknown")
        description = problem_class.get("description", "")

        # Analyze based on problem type
        if "documentation" in problem_type.lower() or "documentation" in description.lower():
            points.extend(self._analyze_documentation_problem(problem_class))

        elif "trust" in problem_type.lower() or "trust" in description.lower():
            points.extend(self._analyze_trust_problem(problem_class))

        elif "efficiency" in problem_type.lower() or "speed" in description.lower():
            points.extend(self._analyze_efficiency_problem(problem_class))

        else:
            # Generic analysis for unknown problem types
            points.extend(self._generic_leverage_analysis(problem_class))

        # Rank by effectiveness (leverage level)
        points_ranked = self.rank_by_effectiveness(points)

        self.identified_points.extend(points_ranked)
        return points_ranked

    def rank_by_effectiveness(self, points: list[LeveragePoint]) -> list[LeveragePoint]:
        """
        Rank leverage points by Meadows's hierarchy

        Higher leverage levels (paradigms, goals) ranked before lower
        levels (parameters, buffers).

        Args:
            points: List of leverage points to rank

        Returns:
            Sorted list with most effective points first
        """
        return sorted(points, key=lambda p: p.level, reverse=True)

    def _analyze_documentation_problem(self, problem: dict[str, Any]) -> list[LeveragePoint]:
        """Analyze leverage points for documentation problems"""
        points = []

        # High leverage: Change paradigm (how we think about docs)
        points.append(
            LeveragePoint(
                level=LeverageLevel.PARADIGM,
                description="Paradigm shift: Docs as learning artifact, not compliance burden",
                problem_domain="documentation",
                impact_potential=0.9,
                implementation_difficulty=0.8,
                proposed_intervention="Reframe docs as 'capturing team learning' not 'creating artifacts'",
                expected_outcomes=[
                    "Developers see value in documentation",
                    "Documentation becomes natural part of workflow",
                    "Quality improves as purpose clarifies",
                ],
            )
        )

        # High leverage: Change goal
        points.append(
            LeveragePoint(
                level=LeverageLevel.GOALS,
                description="Change goal: From 'comprehensive docs' to 'shared understanding'",
                problem_domain="documentation",
                impact_potential=0.85,
                implementation_difficulty=0.6,
                proposed_intervention="Optimize for team understanding not document completeness",
                expected_outcomes=[
                    "Focus on what matters",
                    "Less redundant documentation",
                    "More collaboration",
                ],
            )
        )

        # Medium leverage: Self-organization (Level 5 systems thinking)
        points.append(
            LeveragePoint(
                level=LeverageLevel.SELF_ORGANIZATION,
                description="Enable self-organization: AI agents auto-generate docs from patterns",
                problem_domain="documentation",
                impact_potential=0.8,
                implementation_difficulty=0.5,
                proposed_intervention="Deploy Level 5 system that detects patterns and auto-documents",
                expected_outcomes=[
                    "Reduce manual documentation by 70%",
                    "Free developers for creative work",
                    "Maintain quality through pattern detection",
                ],
            )
        )

        # Low leverage: Parameters (quickest but least impactful)
        points.append(
            LeveragePoint(
                level=LeverageLevel.PARAMETERS,
                description="Adjust parameters: Reduce required documentation fields",
                problem_domain="documentation",
                impact_potential=0.3,
                implementation_difficulty=0.1,
                proposed_intervention="Cut required fields from 20 to 8",
                expected_outcomes=["Faster documentation", "May not address root cause"],
            )
        )

        return points

    def _analyze_trust_problem(self, problem: dict[str, Any]) -> list[LeveragePoint]:
        """Analyze leverage points for trust problems"""
        points = []

        # High leverage: Paradigm shift
        points.append(
            LeveragePoint(
                level=LeverageLevel.PARADIGM,
                description="Shift paradigm: AI as collaborator, not tool",
                problem_domain="trust",
                impact_potential=0.9,
                implementation_difficulty=0.8,
                proposed_intervention="Reframe AI relationship from automation to collaboration",
                expected_outcomes=[
                    "Users engage differently with AI",
                    "Set appropriate expectations",
                    "Build genuine partnership",
                ],
            )
        )

        # High leverage: Information flows
        points.append(
            LeveragePoint(
                level=LeverageLevel.INFORMATION_FLOWS,
                description="Increase transparency: Show AI reasoning process",
                problem_domain="trust",
                impact_potential=0.75,
                implementation_difficulty=0.4,
                proposed_intervention="Implement explainable AI with visible reasoning chains",
                expected_outcomes=[
                    "Users understand AI decisions",
                    "Can verify AI logic",
                    "Trust through transparency",
                ],
            )
        )

        # Medium leverage: Reinforcing feedback loops
        points.append(
            LeveragePoint(
                level=LeverageLevel.REINFORCING_LOOPS,
                description="Activate virtuous cycle: Success → Trust → Delegation → More Success",
                problem_domain="trust",
                impact_potential=0.7,
                implementation_difficulty=0.5,
                proposed_intervention="Start with high-confidence, low-risk tasks for momentum",
                expected_outcomes=[
                    "Quick wins build trust",
                    "Positive feedback loop activated",
                    "Natural progression to harder tasks",
                ],
            )
        )

        return points

    def _analyze_efficiency_problem(self, problem: dict[str, Any]) -> list[LeveragePoint]:
        """Analyze leverage points for efficiency problems"""
        points = []

        # High leverage: Goals
        points.append(
            LeveragePoint(
                level=LeverageLevel.GOALS,
                description="Redefine goal: From 'fast completion' to 'sustainable pace'",
                problem_domain="efficiency",
                impact_potential=0.8,
                implementation_difficulty=0.6,
                proposed_intervention="Optimize for long-term throughput not short-term speed",
                expected_outcomes=["Prevent burnout", "Sustainable productivity", "Higher quality"],
            )
        )

        # Medium leverage: Delays
        points.append(
            LeveragePoint(
                level=LeverageLevel.DELAYS,
                description="Reduce feedback delays: Real-time testing and validation",
                problem_domain="efficiency",
                impact_potential=0.65,
                implementation_difficulty=0.4,
                proposed_intervention="Implement continuous testing with instant feedback",
                expected_outcomes=["Faster iteration", "Catch errors early", "Better learning"],
            )
        )

        return points

    def _generic_leverage_analysis(self, problem: dict[str, Any]) -> list[LeveragePoint]:
        """Generic leverage point analysis for unknown problem types"""
        points = []

        # Always consider paradigm shift (highest leverage)
        points.append(
            LeveragePoint(
                level=LeverageLevel.PARADIGM,
                description="Question underlying assumptions about this problem",
                problem_domain=problem.get("class", "unknown"),
                impact_potential=0.8,
                implementation_difficulty=0.8,
                proposed_intervention="Examine and challenge fundamental beliefs about problem",
            )
        )

        # Consider information flows
        points.append(
            LeveragePoint(
                level=LeverageLevel.INFORMATION_FLOWS,
                description="Improve information flow and transparency",
                problem_domain=problem.get("class", "unknown"),
                impact_potential=0.6,
                implementation_difficulty=0.4,
                proposed_intervention="Make relevant information more accessible to stakeholders",
            )
        )

        return points

    def get_top_leverage_points(
        self, n: int = 3, min_level: LeverageLevel | None = None
    ) -> list[LeveragePoint]:
        """
        Get top N leverage points, optionally filtered by minimum level

        Args:
            n: Number of top points to return
            min_level: Optional minimum leverage level to consider

        Returns:
            Top N leverage points
        """
        points = self.identified_points

        if min_level:
            points = [p for p in points if p.level >= min_level]

        return sorted(points, key=lambda p: p.level, reverse=True)[:n]

    def analyze_intervention_feasibility(self, point: LeveragePoint) -> dict[str, Any]:
        """
        Analyze feasibility of intervening at a leverage point

        Considers:
        - Impact potential
        - Implementation difficulty
        - Risk level
        - Time to results

        Args:
            point: Leverage point to analyze

        Returns:
            Feasibility analysis with recommendation
        """
        # Calculate feasibility score (impact vs difficulty)
        feasibility_score = point.impact_potential / max(point.implementation_difficulty, 0.1)

        # Determine recommendation
        if feasibility_score > 1.5:
            recommendation = "HIGHLY RECOMMENDED: High impact, manageable difficulty"
        elif feasibility_score > 1.0:
            recommendation = "RECOMMENDED: Good balance of impact and feasibility"
        elif feasibility_score > 0.7:
            recommendation = "CONSIDER: Significant effort but worthwhile impact"
        else:
            recommendation = "CAUTION: High difficulty relative to impact"

        return {
            "leverage_level": point.level.name,
            "impact_potential": point.impact_potential,
            "implementation_difficulty": point.implementation_difficulty,
            "feasibility_score": feasibility_score,
            "recommendation": recommendation,
            "risks": point.risks,
            "expected_outcomes": point.expected_outcomes,
        }

    def reset(self):
        """Reset analyzer state"""
        self.identified_points = []
