"""Tests for Leverage Point Analysis

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from empathy_os.leverage_points import LeverageLevel, LeveragePoint, LeveragePointAnalyzer


class TestLeverageLevel:
    """Test LeverageLevel enum"""

    def test_leverage_levels_ordered(self):
        """Test that leverage levels are properly ordered"""
        assert LeverageLevel.PARAMETERS == 1
        assert LeverageLevel.TRANSCEND_PARADIGM == 12
        assert LeverageLevel.PARADIGM > LeverageLevel.GOALS
        assert LeverageLevel.GOALS > LeverageLevel.INFORMATION_FLOWS

    def test_all_levels_defined(self):
        """Test that all 12 levels are defined"""
        levels = list(LeverageLevel)
        assert len(levels) == 12


class TestLeveragePoint:
    """Test LeveragePoint dataclass"""

    def test_leverage_point_creation(self):
        """Test creating a leverage point"""
        point = LeveragePoint(
            level=LeverageLevel.PARADIGM,
            description="Shift paradigm",
            problem_domain="trust",
            impact_potential=0.9,
            implementation_difficulty=0.8,
        )

        assert point.level == LeverageLevel.PARADIGM
        assert point.description == "Shift paradigm"
        assert point.problem_domain == "trust"
        assert point.impact_potential == 0.9
        assert point.implementation_difficulty == 0.8

    def test_leverage_point_defaults(self):
        """Test default values"""
        point = LeveragePoint(
            level=LeverageLevel.PARAMETERS,
            description="Test",
            problem_domain="test",
        )

        assert point.impact_potential == 0.5
        assert point.implementation_difficulty == 0.5
        assert point.current_state is None
        assert point.proposed_intervention is None
        assert len(point.expected_outcomes) == 0
        assert len(point.risks) == 0

    def test_leverage_point_with_outcomes_and_risks(self):
        """Test leverage point with outcomes and risks"""
        point = LeveragePoint(
            level=LeverageLevel.GOALS,
            description="Change system goals",
            problem_domain="efficiency",
            expected_outcomes=["Better quality", "Sustainable pace"],
            risks=["Initial resistance", "Learning curve"],
        )

        assert len(point.expected_outcomes) == 2
        assert len(point.risks) == 2


class TestLeveragePointAnalyzer:
    """Test LeveragePointAnalyzer"""

    def test_initialization(self):
        """Test analyzer initializes correctly"""
        analyzer = LeveragePointAnalyzer()

        assert len(analyzer.identified_points) == 0

    def test_find_leverage_points_documentation_problem(self):
        """Test finding leverage points for documentation problem"""
        analyzer = LeveragePointAnalyzer()

        problem = {
            "class": "documentation_burden",
            "description": "Developers spend 40% time on repetitive docs",
            "instances": 18,
        }

        points = analyzer.find_leverage_points(problem)

        assert len(points) > 0
        # Should have high-level points (paradigm, goals)
        high_level_points = [p for p in points if p.level.value >= 10]
        assert len(high_level_points) > 0
        # Should be ranked by effectiveness
        assert points[0].level.value >= points[-1].level.value

    def test_find_leverage_points_trust_problem(self):
        """Test finding leverage points for trust problem"""
        analyzer = LeveragePointAnalyzer()

        problem = {
            "class": "trust_deficit",
            "description": "Users don't trust AI recommendations",
            "instances": 50,
        }

        points = analyzer.find_leverage_points(problem)

        assert len(points) > 0
        # Should include paradigm shift for trust
        paradigm_points = [p for p in points if p.level == LeverageLevel.PARADIGM]
        assert len(paradigm_points) > 0
        # Should include information flows (transparency)
        info_points = [p for p in points if p.level == LeverageLevel.INFORMATION_FLOWS]
        assert len(info_points) > 0

    def test_find_leverage_points_efficiency_problem(self):
        """Test finding leverage points for efficiency problem"""
        analyzer = LeveragePointAnalyzer()

        problem = {
            "class": "efficiency_issue",
            "description": "Team moving too slow",
            "context": "burnout risk",
        }

        points = analyzer.find_leverage_points(problem)

        assert len(points) > 0
        # Should include goals (redefine from fast to sustainable)
        goals_points = [p for p in points if p.level == LeverageLevel.GOALS]
        assert len(goals_points) > 0

    def test_find_leverage_points_unknown_problem(self):
        """Test finding leverage points for unknown problem type"""
        analyzer = LeveragePointAnalyzer()

        problem = {
            "class": "unknown_issue",
            "description": "Something is wrong",
        }

        points = analyzer.find_leverage_points(problem)

        # Should still return generic leverage points
        assert len(points) > 0
        # Should include paradigm (always consider)
        assert any(p.level == LeverageLevel.PARADIGM for p in points)

    def test_rank_by_effectiveness(self):
        """Test ranking points by effectiveness"""
        analyzer = LeveragePointAnalyzer()

        points = [
            LeveragePoint(
                level=LeverageLevel.PARAMETERS,
                description="Low leverage",
                problem_domain="test",
            ),
            LeveragePoint(
                level=LeverageLevel.PARADIGM,
                description="High leverage",
                problem_domain="test",
            ),
            LeveragePoint(
                level=LeverageLevel.GOALS,
                description="Medium-high leverage",
                problem_domain="test",
            ),
        ]

        ranked = analyzer.rank_by_effectiveness(points)

        # Should be sorted highest to lowest
        assert ranked[0].level == LeverageLevel.PARADIGM
        assert ranked[1].level == LeverageLevel.GOALS
        assert ranked[2].level == LeverageLevel.PARAMETERS

    def test_get_top_leverage_points(self):
        """Test getting top N leverage points"""
        analyzer = LeveragePointAnalyzer()

        # Add some points
        problem = {"class": "documentation_burden", "description": "Too much documentation work"}
        analyzer.find_leverage_points(problem)

        top_3 = analyzer.get_top_leverage_points(n=3)

        assert len(top_3) <= 3
        # Should be sorted by level
        if len(top_3) >= 2:
            assert top_3[0].level.value >= top_3[1].level.value

    def test_get_top_leverage_points_with_min_level(self):
        """Test getting top points with minimum level filter"""
        analyzer = LeveragePointAnalyzer()

        problem = {"class": "documentation_burden", "description": "Too much documentation"}
        analyzer.find_leverage_points(problem)

        # Only get high-level points (10+)
        high_level = analyzer.get_top_leverage_points(n=5, min_level=LeverageLevel.GOALS)

        # All should be level 10 or higher
        assert all(p.level.value >= 10 for p in high_level)

    def test_analyze_intervention_feasibility_high_impact_low_difficulty(self):
        """Test feasibility analysis for easy high-impact intervention"""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.INFORMATION_FLOWS,
            description="Add transparency",
            problem_domain="trust",
            impact_potential=0.9,
            implementation_difficulty=0.3,
            expected_outcomes=["Better trust", "Clear decisions"],
            risks=["Info overload"],
        )

        feasibility = analyzer.analyze_intervention_feasibility(point)

        assert feasibility["impact_potential"] == 0.9
        assert feasibility["implementation_difficulty"] == 0.3
        assert feasibility["feasibility_score"] > 1.5
        assert "HIGHLY RECOMMENDED" in feasibility["recommendation"]
        assert len(feasibility["expected_outcomes"]) == 2
        assert len(feasibility["risks"]) == 1

    def test_analyze_intervention_feasibility_low_impact_high_difficulty(self):
        """Test feasibility analysis for hard low-impact intervention"""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.PARAMETERS,
            description="Tweak parameter",
            problem_domain="test",
            impact_potential=0.3,
            implementation_difficulty=0.9,
            expected_outcomes=["Minor improvement"],
        )

        feasibility = analyzer.analyze_intervention_feasibility(point)

        assert feasibility["feasibility_score"] < 0.7
        assert "CAUTION" in feasibility["recommendation"]

    def test_analyze_intervention_feasibility_balanced(self):
        """Test feasibility analysis for balanced intervention"""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.RULES,
            description="Update rules",
            problem_domain="test",
            impact_potential=0.7,
            implementation_difficulty=0.6,
        )

        feasibility = analyzer.analyze_intervention_feasibility(point)

        assert 0.7 < feasibility["feasibility_score"] <= 1.5
        assert (
            "RECOMMENDED" in feasibility["recommendation"]
            or "CONSIDER" in feasibility["recommendation"]
        )

    def test_reset(self):
        """Test resetting analyzer"""
        analyzer = LeveragePointAnalyzer()

        # Add some points
        problem = {"class": "test", "description": "test"}
        analyzer.find_leverage_points(problem)

        assert len(analyzer.identified_points) > 0

        # Reset
        analyzer.reset()

        assert len(analyzer.identified_points) == 0

    def test_analyze_documentation_problem_comprehensive(self):
        """Test comprehensive documentation problem analysis"""
        analyzer = LeveragePointAnalyzer()

        problem = {
            "class": "documentation_burden",
            "description": "Developers spend 40% time on docs",
            "instances": 20,
        }

        points = analyzer.find_leverage_points(problem)

        # Should have paradigm shift point
        paradigm_points = [p for p in points if p.level == LeverageLevel.PARADIGM]
        assert len(paradigm_points) > 0
        paradigm = paradigm_points[0]
        assert "paradigm" in paradigm.description.lower()
        assert paradigm.impact_potential > 0.8

        # Should have goals point
        goals_points = [p for p in points if p.level == LeverageLevel.GOALS]
        assert len(goals_points) > 0

        # Should have self-organization point (Level 5 systems)
        self_org_points = [p for p in points if p.level == LeverageLevel.SELF_ORGANIZATION]
        assert len(self_org_points) > 0

        # Should have low-level parameter point (easy but less effective)
        param_points = [p for p in points if p.level == LeverageLevel.PARAMETERS]
        assert len(param_points) > 0
        param = param_points[0]
        assert param.impact_potential < 0.5

    def test_analyze_trust_problem_comprehensive(self):
        """Test comprehensive trust problem analysis"""
        analyzer = LeveragePointAnalyzer()

        problem = {
            "class": "trust_deficit",
            "description": "Users don't trust AI",
            "instances": 100,
        }

        points = analyzer.find_leverage_points(problem)

        # Should have paradigm shift (AI as collaborator)
        paradigm_points = [p for p in points if p.level == LeverageLevel.PARADIGM]
        assert len(paradigm_points) > 0
        assert "collaborator" in paradigm_points[0].description.lower()

        # Should have information flows (transparency)
        info_points = [p for p in points if p.level == LeverageLevel.INFORMATION_FLOWS]
        assert len(info_points) > 0
        assert "transparency" in info_points[0].description.lower()

        # Should have reinforcing loops (virtuous cycle)
        loop_points = [p for p in points if p.level == LeverageLevel.REINFORCING_LOOPS]
        assert len(loop_points) > 0

    def test_integration_workflow(self):
        """Test full integration workflow"""
        analyzer = LeveragePointAnalyzer()

        # Step 1: Analyze problem
        problem = {
            "class": "efficiency_issue",
            "description": "Team burnout from speed pressure",
            "context": "unsustainable",
        }

        points = analyzer.find_leverage_points(problem)
        assert len(points) > 0

        # Step 2: Get top leverage points
        top_points = analyzer.get_top_leverage_points(n=3)
        assert len(top_points) <= 3

        # Step 3: Analyze feasibility of top point
        if len(top_points) > 0:
            feasibility = analyzer.analyze_intervention_feasibility(top_points[0])
            assert "recommendation" in feasibility
            assert "feasibility_score" in feasibility

        # Step 4: Filter for high-leverage only
        high_leverage = analyzer.get_top_leverage_points(n=5, min_level=LeverageLevel.GOALS)
        assert all(p.level.value >= 10 for p in high_leverage)

    def test_multiple_problems_tracking(self):
        """Test analyzing multiple problems and tracking points"""
        analyzer = LeveragePointAnalyzer()

        # Analyze multiple problems
        problems = [
            {"class": "documentation_burden", "description": "Too much docs"},
            {"class": "trust_deficit", "description": "Low trust"},
            {"class": "efficiency_issue", "description": "Too slow"},
        ]

        for problem in problems:
            analyzer.find_leverage_points(problem)

        # Should have accumulated many points
        assert len(analyzer.identified_points) > 3

        # Should be able to get top points across all problems
        top_all = analyzer.get_top_leverage_points(n=5)
        assert len(top_all) <= 5

    def test_feasibility_score_calculation(self):
        """Test feasibility score calculation edge cases"""
        analyzer = LeveragePointAnalyzer()

        # Zero difficulty should be handled
        point_zero_diff = LeveragePoint(
            level=LeverageLevel.PARAMETERS,
            description="Test",
            problem_domain="test",
            impact_potential=0.5,
            implementation_difficulty=0.0,
        )

        feasibility = analyzer.analyze_intervention_feasibility(point_zero_diff)
        # Should use min(0.1) to avoid division issues
        assert feasibility["feasibility_score"] >= 5.0

    def test_expected_outcomes_present(self):
        """Test that leverage points have expected outcomes"""
        analyzer = LeveragePointAnalyzer()

        problem = {"class": "documentation_burden", "description": "Too much documentation"}

        points = analyzer.find_leverage_points(problem)

        # High-level points should have expected outcomes
        high_points = [p for p in points if p.level.value >= 10]
        for point in high_points:
            assert len(point.expected_outcomes) > 0

    def test_feasibility_medium_range(self):
        """Test feasibility calculation in 0.7-0.8 range (CONSIDER recommendation)"""
        analyzer = LeveragePointAnalyzer()

        # Create point with medium feasibility (score between 0.7 and 0.8)
        # Impact: 0.7, Difficulty: 0.9 → score ≈ 0.778
        point_medium = LeveragePoint(
            level=LeverageLevel.RULES,
            description="Medium difficulty leverage point",
            problem_domain="test",
            impact_potential=0.7,
            implementation_difficulty=0.9,
        )

        feasibility = analyzer.analyze_intervention_feasibility(point_medium)

        # Should be in the 0.7-0.8 range
        assert 0.7 < feasibility["feasibility_score"] < 0.8
        assert feasibility["recommendation"] == "CONSIDER: Significant effort but worthwhile impact"
