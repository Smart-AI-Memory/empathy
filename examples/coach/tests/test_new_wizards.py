"""
Comprehensive QA Tests for New Wizards (10 wizards)

Tests all 10 new wizards with various inputs, edge cases, and collaboration patterns.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import pytest

from examples.coach import Coach, WizardTask
from examples.coach.wizards import APIWizard, ComplianceWizard, DatabaseWizard, PerformanceWizard


class TestNewWizardRouting:
    """Test that Coach routes tasks to correct new wizards"""

    @pytest.mark.asyncio
    async def test_performance_wizard_routing(self):
        """Performance keywords should route to PerformanceWizard"""
        coach = Coach()

        test_cases = [
            "Slow database queries causing timeouts",
            "API endpoint has high latency (2s response time)",
            "Performance bottleneck in user dashboard",
            "Need to optimize query performance",
            "Application memory usage too high",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer",
                task=task_desc,
                context="Performance issue",
                risk_tolerance="medium",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "PerformanceWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_refactoring_wizard_routing(self):
        """Refactoring keywords should route to RefactoringWizard"""
        coach = Coach()

        test_cases = [
            "Code is too complex and needs refactoring",
            "God class with 500 lines needs to be split",
            "Technical debt is slowing us down",
            "Duplicate code across multiple files",
            "Improve code quality and maintainability",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer", task=task_desc, context="Code quality", risk_tolerance="low"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "RefactoringWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_api_wizard_routing(self):
        """API keywords should route to APIWizard"""
        coach = Coach()

        test_cases = [
            "Design REST API for user management",
            "Create OpenAPI specification for endpoints",
            "Need API versioning strategy",
            "Generate Swagger documentation",
            "Build new GraphQL endpoint",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer", task=task_desc, context="API development", risk_tolerance="medium"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "APIWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_database_wizard_routing(self):
        """Database keywords should route to DatabaseWizard"""
        coach = Coach()

        test_cases = [
            "Design database schema for new feature",
            "Create Alembic migration for user table",
            "SQL query is slow and needs optimization",
            "Need to add indexes for performance",
            "Database migration for production",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer", task=task_desc, context="Database work", risk_tolerance="low"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "DatabaseWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_devops_wizard_routing(self):
        """DevOps keywords should route to DevOpsWizard"""
        coach = Coach()

        test_cases = [
            "Set up CI/CD pipeline with GitHub Actions",
            "Deploy application to Kubernetes cluster",
            "Create Terraform infrastructure code",
            "Automate deployment process",
            "Configure Docker containers for app",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer", task=task_desc, context="Infrastructure", risk_tolerance="medium"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "DevOpsWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_onboarding_wizard_routing(self):
        """Onboarding keywords should route to OnboardingWizard"""
        coach = Coach()

        test_cases = [
            "New developer starting next week, create onboarding plan",
            "Knowledge transfer needed for handoff",
            "Create learning path for junior engineer",
            "Ramp up new team member quickly",
            "Generate codebase tour for new dev",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="team_lead", task=task_desc, context="Team growth", risk_tolerance="low"
            )
            result = await coach.process(task, multi_wizard=False)
            assert "OnboardingWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_accessibility_wizard_routing(self):
        """Accessibility keywords should route to AccessibilityWizard"""
        coach = Coach()

        test_cases = [
            "Check WCAG 2.1 AA compliance for website",
            "Add screen reader support to forms",
            "Fix accessibility violations in UI",
            "Ensure keyboard navigation works",
            "Improve color contrast for better a11y",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer",
                task=task_desc,
                context="Accessibility requirements",
                risk_tolerance="medium",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "AccessibilityWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_localization_wizard_routing(self):
        """Localization keywords should route to LocalizationWizard"""
        coach = Coach()

        test_cases = [
            "Add i18n support for Spanish and French",
            "Extract strings for translation",
            "Implement localization framework",
            "Support RTL languages like Arabic",
            "Create multilingual version of app",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer",
                task=task_desc,
                context="Global expansion",
                risk_tolerance="medium",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "LocalizationWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_compliance_wizard_routing(self):
        """Compliance keywords should route to ComplianceWizard"""
        coach = Coach()

        test_cases = [
            "Prepare for SOC 2 audit next quarter",
            "HIPAA compliance check needed",
            "GDPR compliance for EU customers",
            "Security audit preparation",
            "ISO 27001 certification requirements",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="team_lead",
                task=task_desc,
                context="Compliance requirements",
                risk_tolerance="low",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "ComplianceWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_monitoring_wizard_routing(self):
        """Monitoring keywords should route to MonitoringWizard"""
        coach = Coach()

        test_cases = [
            "Set up monitoring dashboard for production",
            "Define SLO for API availability",
            "Create incident response runbooks",
            "Configure Grafana alerts",
            "Implement observability for microservices",
        ]

        for task_desc in test_cases:
            task = WizardTask(
                role="developer",
                task=task_desc,
                context="Production monitoring",
                risk_tolerance="low",
            )
            result = await coach.process(task, multi_wizard=False)
            assert "MonitoringWizard" in result.routing, f"Failed for: {task_desc}"
            assert result.overall_confidence > 0.5


class TestCollaborationPatterns:
    """Test multi-wizard collaboration patterns"""

    @pytest.mark.asyncio
    async def test_new_api_endpoint_pattern(self):
        """'new api endpoint' should activate collaboration pattern"""
        coach = Coach()

        task = WizardTask(
            role="developer",
            task="Build new api endpoint for user profiles",
            context="Need REST endpoint with auth",
            risk_tolerance="medium",
        )

        result = await coach.process(task, multi_wizard=True)

        # Should route to APIWizard (primary) + SecurityWizard + TestingWizard + DocumentationWizard
        set(result.routing)

        # At least 2 wizards should be activated (APIWizard + SecurityWizard minimum)
        assert len(result.routing) >= 2, f"Expected multi-wizard, got: {result.routing}"
        assert "APIWizard" in result.routing, "APIWizard should be primary"

    @pytest.mark.asyncio
    async def test_database_migration_pattern(self):
        """'database migration' should activate collaboration pattern"""
        coach = Coach()

        task = WizardTask(
            role="developer",
            task="Database migration for production schema change",
            context="Need to add new tables with zero downtime",
            risk_tolerance="low",
        )

        result = await coach.process(task, multi_wizard=True)

        # Should route to DatabaseWizard (primary) + DevOpsWizard + MonitoringWizard
        assert len(result.routing) >= 2, f"Expected multi-wizard, got: {result.routing}"
        assert "DatabaseWizard" in result.routing, "DatabaseWizard should be included"

    @pytest.mark.asyncio
    async def test_performance_issue_pattern(self):
        """'performance issue' should activate collaboration pattern"""
        coach = Coach()

        task = WizardTask(
            role="developer",
            task="Performance issue with slow database queries",
            context="API response time is 3 seconds, needs to be under 200ms",
            risk_tolerance="high",
        )

        result = await coach.process(task, multi_wizard=True)

        # Should route to PerformanceWizard (primary) + DatabaseWizard + RefactoringWizard
        assert len(result.routing) >= 2, f"Expected multi-wizard, got: {result.routing}"
        assert "PerformanceWizard" in result.routing, "PerformanceWizard should be included"

    @pytest.mark.asyncio
    async def test_compliance_audit_pattern(self):
        """'compliance audit' should activate collaboration pattern"""
        coach = Coach()

        task = WizardTask(
            role="team_lead",
            task="Compliance audit preparation for SOC 2",
            context="Audit scheduled in 60 days",
            risk_tolerance="low",
        )

        result = await coach.process(task, multi_wizard=True)

        # Should route to ComplianceWizard (primary) + SecurityWizard + DocumentationWizard
        assert len(result.routing) >= 2, f"Expected multi-wizard, got: {result.routing}"
        assert "ComplianceWizard" in result.routing, "ComplianceWizard should be included"


class TestWizardOutputQuality:
    """Test that wizard outputs are comprehensive and high-quality"""

    @pytest.mark.asyncio
    async def test_performance_wizard_output_quality(self):
        """PerformanceWizard should produce comprehensive artifacts"""
        wizard = PerformanceWizard()

        task = WizardTask(
            role="developer",
            task="Optimize slow API endpoint",
            context="Endpoint returns 500ms, need < 200ms",
            risk_tolerance="medium",
        )

        output = wizard.execute(task)

        # Check output structure
        assert output.diagnosis, "Diagnosis should not be empty"
        assert len(output.plan) >= 3, "Should have multi-step plan"
        assert len(output.artifacts) >= 3, "Should have multiple artifacts"
        assert len(output.risks) >= 1, "Should identify risks"
        assert output.confidence > 0.5, "Should be confident for performance task"

        # Check artifact types
        artifact_types = [a.type for a in output.artifacts]
        assert "doc" in artifact_types, "Should have documentation artifacts"
        assert "code" in artifact_types, "Should have code artifacts"

    @pytest.mark.asyncio
    async def test_database_wizard_output_quality(self):
        """DatabaseWizard should produce comprehensive migration artifacts"""
        wizard = DatabaseWizard()

        task = WizardTask(
            role="developer",
            task="Create database migration for user_preferences table",
            context="Need new table with foreign key to users",
            risk_tolerance="low",
        )

        output = wizard.execute(task)

        # Check output structure
        assert output.diagnosis, "Diagnosis should not be empty"
        assert len(output.plan) >= 3, "Should have migration plan"
        assert len(output.artifacts) >= 3, "Should have migration artifacts"
        assert len(output.risks) >= 1, "Should identify migration risks"

        # Check empathy checks
        assert output.empathy_checks.cognitive, "Should have cognitive empathy"
        assert output.empathy_checks.emotional, "Should have emotional empathy"
        assert output.empathy_checks.anticipatory, "Should have anticipatory empathy"

    @pytest.mark.asyncio
    async def test_api_wizard_output_quality(self):
        """APIWizard should produce OpenAPI spec and implementation"""
        wizard = APIWizard()

        task = WizardTask(
            role="developer",
            task="Design REST API for user management",
            context="CRUD operations with authentication",
            risk_tolerance="medium",
        )

        output = wizard.execute(task)

        # Check for OpenAPI artifact
        openapi_artifact = next((a for a in output.artifacts if "OpenAPI" in a.title), None)
        assert openapi_artifact is not None, "Should have OpenAPI specification"
        assert "openapi:" in openapi_artifact.content, "Should contain valid OpenAPI spec"

        # Check for implementation artifact
        impl_artifact = next((a for a in output.artifacts if "Implementation" in a.title), None)
        assert impl_artifact is not None, "Should have implementation code"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_ambiguous_task_routing(self):
        """Ambiguous tasks should still route to best match"""
        coach = Coach()

        task = WizardTask(
            role="developer", task="Fix the thing", context="It's broken", risk_tolerance="medium"
        )

        result = await coach.process(task, multi_wizard=False)

        # Should fallback gracefully
        assert result.overall_confidence >= 0.0, "Should have confidence score"
        assert len(result.routing) >= 1, "Should route to at least one wizard or fallback"

    @pytest.mark.asyncio
    async def test_empty_context_handling(self):
        """Should handle tasks with minimal context"""
        coach = Coach()

        task = WizardTask(
            role="developer",
            task="Performance optimization needed",
            context="",
            risk_tolerance="medium",
        )

        result = await coach.process(task, multi_wizard=False)

        assert "PerformanceWizard" in result.routing, "Should still route correctly"
        assert result.overall_confidence > 0.3, "Should have reasonable confidence"

    @pytest.mark.asyncio
    async def test_multi_wizard_coordination(self):
        """Multiple wizards should coordinate without conflicts"""
        coach = Coach()

        task = WizardTask(
            role="developer",
            task="Build secure API with monitoring",
            context="Need authentication, rate limiting, and observability",
            risk_tolerance="low",
        )

        result = await coach.process(task, multi_wizard=True)

        # Should activate multiple wizards
        assert len(result.routing) >= 2, "Should route to multiple wizards"

        # Should have synthesis
        assert result.synthesis, "Should synthesize multiple outputs"
        assert (
            "Combined Actions" in result.synthesis
            or "Additional Recommendations" in result.synthesis
        )


class TestLevel4Anticipatory:
    """Test Level 4 Anticipatory Empathy features"""

    @pytest.mark.asyncio
    async def test_performance_wizard_predicts_scaling_issues(self):
        """PerformanceWizard should predict future bottlenecks"""
        wizard = PerformanceWizard()

        task = WizardTask(
            role="developer",
            task="Current performance is acceptable but worried about scaling",
            context="200ms response time at 1K users/day",
            risk_tolerance="medium",
        )

        output = wizard.execute(task)

        # Check for anticipatory empathy (Level 4)
        assert output.empathy_checks.anticipatory, "Should have anticipatory empathy"

        # Should have scaling forecast artifact
        scaling_artifact = next(
            (a for a in output.artifacts if "Scaling" in a.title or "Projection" in a.title), None
        )
        assert scaling_artifact is not None, "Should predict future scaling issues"
        assert "days" in scaling_artifact.content.lower(), "Should include timeline predictions"

    @pytest.mark.asyncio
    async def test_compliance_wizard_predicts_audit_needs(self):
        """ComplianceWizard should anticipate audit requirements"""
        wizard = ComplianceWizard()

        task = WizardTask(
            role="team_lead",
            task="We'll need SOC 2 certification eventually",
            context="Growing startup, no compliance work done yet",
            risk_tolerance="low",
        )

        output = wizard.execute(task)

        # Should identify gaps before audit
        assert len(output.risks) >= 2, "Should identify compliance risks"

        # Should have timeline-based recommendations
        assert output.empathy_checks.anticipatory, "Should anticipate future needs"


# Performance benchmarks
class TestPerformance:
    """Test that wizards respond quickly"""

    @pytest.mark.asyncio
    async def test_wizard_response_time(self):
        """Wizards should execute in < 1 second"""
        import time

        wizard = PerformanceWizard()

        task = WizardTask(
            role="developer",
            task="Optimize database queries",
            context="Slow performance",
            risk_tolerance="medium",
        )

        start = time.time()
        output = wizard.execute(task)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Wizard took {elapsed:.2f}s (should be < 1s)"
        assert output.confidence > 0.0, "Should complete successfully"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
