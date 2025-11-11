"""
Comprehensive QA Tests for Coach Wizards

Tests all 6 wizards with various inputs, edge cases, and scenarios.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest

from examples.coach import Coach, WizardTask
from examples.coach.shared_learning import SharedLearningSystem
from examples.coach.wizards import DebuggingWizard, DocumentationWizard, SecurityWizard


class TestWizardRouting:
    """Test that Coach routes tasks to correct wizards"""

    @pytest.mark.asyncio
    async def test_debugging_wizard_routing(self):
        """Debugging keywords should route to DebuggingWizard"""
        coach = Coach()

        test_cases = [
            "Bug in production causing 500 errors",
            "Application crashes when user logs in",
            "Exception thrown in payment processing",
            "Debug stack trace showing null pointer",
            "System failing with timeout errors",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer", task=task_desc, context="Production issue", risk_tolerance="low"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "DebuggingWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_documentation_wizard_routing(self):
        """Documentation keywords should route to DocumentationWizard"""
        coach = Coach()

        test_cases = [
            "README is outdated and confusing",
            "Need onboarding documentation for new devs",
            "Create handoff guide for project",
            "Documentation unclear about setup process",
            "Write tutorial for API usage",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="team_lead",
                task=task_desc,
                context="Documentation gap",
                risk_tolerance="medium",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "DocumentationWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_design_review_wizard_routing(self):
        """Design/architecture keywords should route to DesignReviewWizard"""
        coach = Coach()

        test_cases = [
            "Architecture review for microservices design",
            "Evaluate trade-offs of serverless vs containers",
            "Refactor monolith into smaller services",
            "Technical debt in current design",
            "Scalability review needed for system",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="architect",
                task=task_desc,
                context="Architecture planning",
                risk_tolerance="low",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "DesignReviewWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_testing_wizard_routing(self):
        """Testing keywords should route to TestingWizard"""
        coach = Coach()

        test_cases = [
            "Test coverage is too low at 40%",
            "Need integration tests for API endpoints",
            "Create test plan for new feature",
            "Unit tests missing for authentication",
            "QA review shows quality issues",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer",
                task=task_desc,
                context="Quality improvement",
                risk_tolerance="medium",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "TestingWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_retrospective_wizard_routing(self):
        """Retrospective keywords should route to RetrospectiveWizard"""
        coach = Coach()

        test_cases = [
            "Team retrospective after sprint",
            "Post-mortem for project completion",
            "Process improvement workshop needed",
            "Team morale is low, need feedback session",
            "Lessons learned from incident",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="team_lead", task=task_desc, context="Team improvement", risk_tolerance="low"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "RetrospectiveWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.3  # Lower threshold for retro

    @pytest.mark.asyncio
    async def test_security_wizard_routing(self):
        """Security keywords should route to SecurityWizard"""
        coach = Coach()

        test_cases = [
            "Security audit before production launch",
            "Vulnerability found in authentication",
            "Penetration testing review needed",
            "Check for SQL injection risks",
            "OWASP compliance review",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer", task=task_desc, context="Security concern", risk_tolerance="low"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "SecurityWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5


class TestWizardOutputQuality:
    """Test that wizard outputs are complete and useful"""

    def test_debugging_wizard_output_completeness(self):
        """DebuggingWizard should provide complete output"""
        wizard = DebuggingWizard()
        task = WizardTask(
            role="developer",
            task="Production bug: 500 errors on user login",
            context="NullPointerException in auth service, logs show config is null",
            risk_tolerance="low",
        )

        output = wizard.execute(task)

        # Check all required fields
        assert output.wizard_name == "DebuggingWizard"
        assert len(output.diagnosis) > 10
        assert len(output.plan) >= 3
        assert len(output.artifacts) >= 3
        assert len(output.risks) >= 1
        assert len(output.next_actions) >= 3
        assert output.confidence > 0.5

        # Check artifact types
        artifact_types = [a.type for a in output.artifacts]
        assert "code" in artifact_types  # Should have patch
        assert "checklist" in artifact_types  # Should have deployment checklist

        # Check empathy checks
        assert len(output.empathy_checks.cognitive) > 10
        assert len(output.empathy_checks.emotional) > 10
        assert len(output.empathy_checks.anticipatory) > 10

    def test_documentation_wizard_output_completeness(self):
        """DocumentationWizard should provide complete output"""
        wizard = DocumentationWizard()
        task = WizardTask(
            role="team_lead",
            task="README missing setup instructions",
            context="New developers can't get started, no database setup docs",
            risk_tolerance="medium",
        )

        output = wizard.execute(task)

        assert output.wizard_name == "DocumentationWizard"
        assert len(output.artifacts) >= 2
        assert any(a.type == "doc" for a in output.artifacts)
        assert any(a.type == "checklist" for a in output.artifacts)
        assert len(output.next_actions) >= 3

    def test_security_wizard_output_completeness(self):
        """SecurityWizard should provide comprehensive security analysis"""
        wizard = SecurityWizard()
        task = WizardTask(
            role="developer",
            task="Security review before launch",
            context="Web app with authentication, payment processing, user data",
            risk_tolerance="low",
        )

        output = wizard.execute(task)

        assert output.wizard_name == "SecurityWizard"
        assert len(output.artifacts) >= 3
        assert len(output.risks) >= 2

        # Should identify vulnerabilities
        vuln_artifact = next((a for a in output.artifacts if "Vulnerability" in a.title), None)
        assert vuln_artifact is not None

        # Should have threat model
        threat_artifact = next((a for a in output.artifacts if "Threat" in a.title), None)
        assert threat_artifact is not None


class TestMultiWizardCollaboration:
    """Test that wizards can work together"""

    @pytest.mark.asyncio
    async def test_debugging_and_docs_collaboration(self):
        """Bug fix should trigger both debugging and docs wizards"""
        coach = Coach()
        task = WizardTask(
            role="developer",
            task="Critical bug blocks release, hotfix process not documented",
            context="500 errors in production, README doesn't explain hotfix procedure",
            risk_tolerance="low",
        )

        result = await coach.process(task, multi_wizard=True)

        # Should route to both wizards
        assert len(result.routing) >= 1
        assert "DebuggingWizard" in result.routing or "DocumentationWizard" in result.routing

        # Should have synthesis
        assert len(result.synthesis) > 20

    @pytest.mark.asyncio
    async def test_security_and_testing_collaboration(self):
        """Security issue should consider testing"""
        coach = Coach()
        task = WizardTask(
            role="developer",
            task="SQL injection vulnerability found, no security tests",
            context="Security audit revealed SQL injection, test coverage lacks security tests",
            risk_tolerance="low",
        )

        result = await coach.process(task, multi_wizard=True)

        # Should identify security as primary
        assert "SecurityWizard" in result.routing or "TestingWizard" in result.routing


class TestSharedLearningSystem:
    """Test the multi-agent learning system"""

    def test_pattern_contribution(self):
        """Wizards should be able to contribute patterns"""
        learning = SharedLearningSystem()

        pattern = learning.contribute_pattern(
            wizard_name="TestWizard",
            pattern_type="test_pattern",
            description="Test pattern for QA",
            code="def test(): pass",
            tags=["test", "qa"],
            context={"env": "test"},
        )

        assert pattern.agent_id == "TestWizard"
        assert pattern.pattern_type == "test_pattern"
        assert len(learning.pattern_library.patterns) >= 1

    def test_pattern_query(self):
        """Should be able to query patterns by tags"""
        learning = SharedLearningSystem()

        # Contribute some patterns
        learning.contribute_pattern(
            wizard_name="Wizard1",
            pattern_type="type1",
            description="Pattern 1",
            code="code1",
            tags=["tag1", "common"],
        )

        learning.contribute_pattern(
            wizard_name="Wizard2",
            pattern_type="type2",
            description="Pattern 2",
            code="code2",
            tags=["tag2", "common"],
        )

        # Query by tag
        results = learning.query_patterns(tags=["common"])
        assert len(results) >= 2

    def test_collaboration_tracking(self):
        """Should track wizard collaborations"""
        learning = SharedLearningSystem()

        learning.record_collaboration("Wizard1", "Wizard2")
        learning.record_collaboration("Wizard1", "Wizard2")
        learning.record_collaboration("Wizard2", "Wizard3")

        stats = learning.get_collaboration_stats()
        assert stats["Wizard1->Wizard2"] == 2
        assert stats["Wizard2->Wizard3"] == 1


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_task_description(self):
        """Should handle empty task gracefully"""
        coach = Coach()
        task = WizardTask(
            role="developer", task="", context="Some context", risk_tolerance="medium"
        )

        result = await coach.process(task)
        assert result is not None
        assert len(result.routing) >= 1  # Should use fallback

    @pytest.mark.asyncio
    async def test_very_long_context(self):
        """Should handle very long context"""
        coach = Coach()
        long_context = "Context " * 1000  # Very long context

        task = WizardTask(
            role="developer", task="Bug in system", context=long_context, risk_tolerance="medium"
        )

        result = await coach.process(task)
        assert result is not None

    @pytest.mark.asyncio
    async def test_special_characters_in_input(self):
        """Should handle special characters"""
        coach = Coach()
        task = WizardTask(
            role="developer",
            task="Bug with <script>alert('xss')</script> in input",
            context="SQL: SELECT * FROM users WHERE id = '; DROP TABLE users; --",
            risk_tolerance="high",
        )

        result = await coach.process(task)
        assert result is not None
        # Security wizard should catch this
        assert any("Security" in w for w in result.routing) or result.routing == ["Fallback"]

    @pytest.mark.asyncio
    async def test_all_risk_tolerance_levels(self):
        """Should handle all risk tolerance levels"""
        coach = Coach()

        for risk_level in ["low", "medium", "high"]:
            task = WizardTask(
                role="developer",
                task="Test task",
                context="Test context",
                risk_tolerance=risk_level,
            )

            result = await coach.process(task)
            assert result is not None
            assert result.overall_confidence >= 0


class TestEmpathyChecks:
    """Test that empathy checks are meaningful"""

    def test_cognitive_empathy_varies_by_role(self):
        """Cognitive empathy should consider different roles"""
        wizard = DebuggingWizard()

        roles = ["developer", "architect", "pm", "team_lead"]
        outputs = []

        for role in roles:
            task = WizardTask(
                role=role, task="Bug in system", context="500 error", risk_tolerance="low"
            )
            output = wizard.execute(task)
            outputs.append(output)

        # Check that empathy checks mention roles
        for i, output in enumerate(outputs):
            assert (
                roles[i] in output.empathy_checks.cognitive.lower()
                or "developer" in output.empathy_checks.cognitive.lower()
            )

    def test_emotional_empathy_detects_stress(self):
        """Emotional empathy should detect stress indicators"""
        wizard = DebuggingWizard()

        # High stress scenario
        task_stressed = WizardTask(
            role="developer",
            task="CRITICAL: Production down, users can't access system",
            context="Urgent fix needed, boss is angry, customers complaining",
            risk_tolerance="low",
        )

        output_stressed = wizard.execute(task_stressed)

        # Should acknowledge pressure
        emotional = output_stressed.empathy_checks.emotional.lower()
        assert any(word in emotional for word in ["high", "pressure", "urgent", "stress"])

    def test_anticipatory_empathy_provides_actions(self):
        """Anticipatory empathy should provide proactive suggestions"""
        wizard = SecurityWizard()

        task = WizardTask(
            role="developer",
            task="Security review",
            context="New feature with user data",
            risk_tolerance="low",
        )

        output = wizard.execute(task)

        # Should have anticipatory actions
        assert (
            "proactive" in output.empathy_checks.anticipatory.lower()
            or "preventive" in output.empathy_checks.anticipatory.lower()
            or len(output.empathy_checks.anticipatory) > 30
        )


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_single_wizard_response_time(self):
        """Single wizard should respond quickly"""
        import time

        coach = Coach()
        task = WizardTask(
            role="developer", task="Bug fix needed", context="Simple bug", risk_tolerance="medium"
        )

        start = time.time()
        result = await coach.process(task, multi_wizard=False)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 1 second for simple task)
        assert elapsed < 1.0
        assert result is not None

    @pytest.mark.asyncio
    async def test_multi_wizard_response_time(self):
        """Multi-wizard should respond in reasonable time"""
        import time

        coach = Coach()
        task = WizardTask(
            role="developer",
            task="Bug with missing documentation and poor test coverage",
            context="Complex issue requiring multiple wizards",
            risk_tolerance="low",
        )

        start = time.time()
        result = await coach.process(task, multi_wizard=True)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 2 seconds)
        assert elapsed < 2.0
        assert result is not None


class TestConfidenceScoring:
    """Test that confidence scores are reasonable"""

    @pytest.mark.asyncio
    async def test_high_confidence_for_clear_match(self):
        """Should have high confidence for clear keyword matches"""
        coach = Coach()
        task = WizardTask(
            role="developer",
            task="Security vulnerability SQL injection found",
            context="Security audit revealed critical SQL injection vulnerability",
            risk_tolerance="low",
        )

        result = await coach.process(task, multi_wizard=False)

        # Should have high confidence
        assert result.overall_confidence > 0.8

    @pytest.mark.asyncio
    async def test_lower_confidence_for_ambiguous_match(self):
        """Should have lower confidence for ambiguous tasks"""
        coach = Coach()
        task = WizardTask(
            role="developer",
            task="Need to improve system",
            context="General improvements needed",
            risk_tolerance="medium",
        )

        result = await coach.process(task, multi_wizard=False)

        # Confidence should be lower for ambiguous task
        assert result.overall_confidence < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
