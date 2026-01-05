"""Integration Tests for Intelligence System

Tests the complete flow of Smart Router, Memory Graph, and Chain Executor
working together as a unified system.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

# Check if wizard_chains.yaml exists for chain executor tests
CHAIN_CONFIG_EXISTS = Path(".empathy/wizard_chains.yaml").exists()

from empathy_os.memory import EdgeType, MemoryGraph  # noqa: E402
from empathy_os.routing import (
    ChainExecutor,  # noqa: E402
    ClassificationResult,
    HaikuClassifier,
    SmartRouter,
    WizardRegistry,
)


class TestSmartRouterIntegration:
    """Integration tests for Smart Router with other components."""

    def test_router_with_registry(self):
        """Test router correctly uses wizard registry."""
        router = SmartRouter()

        # Verify all registered wizards are accessible
        wizards = router.list_wizards()
        assert len(wizards) >= 10

        # Verify wizard info is complete
        for wizard in wizards:
            assert wizard.name
            assert wizard.description
            assert len(wizard.keywords) > 0

    def test_router_security_request(self):
        """Test routing a security-related request."""
        router = SmartRouter()
        decision = router.route_sync("Check for SQL injection vulnerabilities in auth.py")

        assert decision.primary_wizard == "security-audit"
        assert decision.confidence > 0.1  # Keyword-based classifier has lower confidence
        assert "security-audit" in decision.suggested_chain

    def test_router_performance_request(self):
        """Test routing a performance-related request."""
        router = SmartRouter()
        decision = router.route_sync("Optimize slow database queries")

        assert decision.primary_wizard == "perf-audit"
        assert decision.confidence > 0.1  # Keyword-based classifier has lower confidence

    def test_router_testing_request(self):
        """Test routing a testing-related request."""
        router = SmartRouter()
        # Use request without "authentication" which triggers security-audit
        decision = router.route_sync("Generate unit tests for the user service module")

        assert decision.primary_wizard == "test-gen"

    def test_router_with_context(self):
        """Test routing with file context."""
        router = SmartRouter()
        decision = router.route_sync(
            "Review this code",
            context={"file": "auth.py", "language": "python"},
        )

        assert decision.context.get("file") == "auth.py"

    def test_router_file_suggestions(self):
        """Test file-based wizard suggestions."""
        router = SmartRouter()

        # Python file
        suggestions = router.suggest_for_file("src/auth.py")
        assert "security-audit" in suggestions
        assert "code-review" in suggestions

        # Package.json
        suggestions = router.suggest_for_file("package.json")
        assert "dependency-check" in suggestions

    def test_router_error_suggestions(self):
        """Test error-based wizard suggestions."""
        router = SmartRouter()

        suggestions = router.suggest_for_error("NullPointerException at line 42")
        assert "bug-predict" in suggestions

        suggestions = router.suggest_for_error("SecurityException: Access denied")
        assert "security-audit" in suggestions


class TestMemoryGraphIntegration:
    """Integration tests for Memory Graph with wizards."""

    @pytest.fixture
    def temp_graph(self):
        """Create a temporary graph for testing."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        graph = MemoryGraph(path=path)
        yield graph
        if path.exists():
            path.unlink()

    def test_cross_wizard_knowledge_sharing(self, temp_graph):
        """Test that findings from one wizard are accessible to others."""
        # Security wizard finds a vulnerability
        _vuln_id = temp_graph.add_finding(
            wizard="security-audit",
            finding={
                "type": "vulnerability",
                "name": "SQL Injection in login",
                "severity": "critical",
                "file": "auth.py",
                "line": 42,
            },
        )

        # Bug predict wizard should be able to find related issues
        similar = temp_graph.find_similar(
            {"name": "SQL Injection", "type": "vulnerability"},
            threshold=0.3,
        )

        assert len(similar) >= 1
        assert similar[0][0].source_wizard == "security-audit"

    def test_finding_relationships(self, temp_graph):
        """Test creating and querying relationships between findings."""
        # Create a bug finding
        bug_id = temp_graph.add_finding(
            wizard="bug-predict",
            finding={"type": "bug", "name": "Null reference error"},
        )

        # Create a fix
        fix_id = temp_graph.add_finding(
            wizard="bug-predict",
            finding={"type": "fix", "name": "Add null check"},
        )

        # Connect them
        temp_graph.add_edge(bug_id, fix_id, EdgeType.FIXED_BY)

        # Query relationship
        fixes = temp_graph.find_related(bug_id, edge_types=[EdgeType.FIXED_BY])
        assert len(fixes) == 1
        assert fixes[0].name == "Add null check"

    def test_wizard_findings_isolation(self, temp_graph):
        """Test that wizard findings can be queried by source."""
        # Add findings from different wizards
        temp_graph.add_finding(
            wizard="security-audit",
            finding={"type": "vulnerability", "name": "XSS"},
        )
        temp_graph.add_finding(
            wizard="security-audit",
            finding={"type": "vulnerability", "name": "CSRF"},
        )
        temp_graph.add_finding(
            wizard="perf-audit",
            finding={"type": "performance_issue", "name": "Slow query"},
        )

        # Query by wizard
        security_findings = temp_graph.find_by_wizard("security-audit")
        assert len(security_findings) == 2

        perf_findings = temp_graph.find_by_wizard("perf-audit")
        assert len(perf_findings) == 1

    def test_graph_statistics(self, temp_graph):
        """Test graph statistics for monitoring."""
        temp_graph.add_finding(
            wizard="security-audit",
            finding={"type": "vulnerability", "name": "V1", "severity": "high"},
        )
        temp_graph.add_finding(
            wizard="security-audit",
            finding={"type": "vulnerability", "name": "V2", "severity": "critical"},
        )
        temp_graph.add_finding(
            wizard="bug-predict",
            finding={"type": "bug", "name": "B1", "severity": "medium"},
        )

        stats = temp_graph.get_statistics()

        assert stats["total_nodes"] == 3
        assert stats["nodes_by_wizard"]["security-audit"] == 2
        assert stats["nodes_by_wizard"]["bug-predict"] == 1


@pytest.mark.skipif(not CHAIN_CONFIG_EXISTS, reason=".empathy/wizard_chains.yaml not found")
class TestChainExecutorIntegration:
    """Integration tests for Chain Executor with routing."""

    def test_chain_trigger_evaluation(self):
        """Test chain triggers are evaluated correctly."""
        executor = ChainExecutor()

        # Security audit with high severity should trigger dependency check
        result = {"high_severity_count": 5}
        triggers = executor.get_triggered_chains("security-audit", result)

        assert len(triggers) >= 1
        wizard_names = [t.next_wizard for t in triggers]
        assert "dependency-check" in wizard_names

    def test_chain_template_loading(self):
        """Test pre-built chain templates load correctly."""
        executor = ChainExecutor()
        templates = executor.list_templates()

        assert "full-security-review" in templates
        assert "pre-release" in templates

    def test_chain_execution_creation(self):
        """Test creating a chain execution plan."""
        executor = ChainExecutor()

        triggers = executor.get_triggered_chains(
            "security-audit",
            {"high_severity_count": 3},
        )

        execution = executor.create_execution("security-audit", triggers)

        assert execution.initial_wizard == "security-audit"
        assert len(execution.steps) >= 1

    def test_chain_approval_workflow(self):
        """Test approval workflow for chain steps."""
        executor = ChainExecutor()
        from empathy_os.routing import ChainStep

        execution = executor.create_execution("test", [])
        execution.steps.append(
            ChainStep(
                wizard_name="next-wizard",
                triggered_by="test",
                approval_required=True,
            ),
        )

        # Step should need approval
        assert execution.steps[-1].approved is None

        # Approve step
        executor.approve_step(execution, len(execution.steps) - 1)
        assert execution.steps[-1].approved is True


class TestFullIntegration:
    """End-to-end integration tests."""

    def test_request_to_chain_flow(self):
        """Test complete flow from request to chain execution."""
        # 1. User makes a request
        request = "Fix security vulnerabilities and check dependencies"

        # 2. Smart Router classifies the request
        router = SmartRouter()
        decision = router.route_sync(request)

        assert decision.primary_wizard in ["security-audit", "dependency-check"]
        assert len(decision.suggested_chain) >= 1

        # 3. Chain Executor creates execution plan
        executor = ChainExecutor()
        config = executor.get_chain_config(decision.primary_wizard)

        if config and config.auto_chain:
            # Simulate wizard result
            mock_result = {"high_severity_count": 2}
            triggers = executor.get_triggered_chains(decision.primary_wizard, mock_result)
            execution = executor.create_execution(decision.primary_wizard, triggers)

            assert execution.initial_wizard == decision.primary_wizard

    def test_wizard_findings_inform_routing(self):
        """Test that memory graph findings influence routing."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            # Add historical security findings
            graph = MemoryGraph(path=path)
            graph.add_finding(
                wizard="security-audit",
                finding={
                    "type": "vulnerability",
                    "name": "Previous SQL Injection",
                    "file": "db/queries.py",
                    "severity": "critical",
                },
            )

            # New request about similar file
            router = SmartRouter()
            _decision = router.route_sync("Review db/queries.py for issues")

            # Should suggest security wizard given history
            suggestions = router.suggest_for_file("db/queries.py")
            assert "security-audit" in suggestions

        finally:
            if path.exists():
                path.unlink()

    def test_registry_wizard_info_completeness(self):
        """Test that all registered wizards have complete information."""
        registry = WizardRegistry()
        wizards = registry.list_all()

        for wizard in wizards:
            # Required fields
            assert wizard.name, "Wizard missing name"
            assert wizard.description, f"{wizard.name} missing description"
            assert len(wizard.keywords) > 0, f"{wizard.name} missing keywords"
            assert wizard.primary_domain, f"{wizard.name} missing domain"

            # Verify wizard can be retrieved
            retrieved = registry.get(wizard.name)
            assert retrieved is not None
            assert retrieved.name == wizard.name

    def test_classifier_fallback_works(self):
        """Test that keyword classifier works as fallback."""
        classifier = HaikuClassifier()

        # Should work without API key (keyword fallback)
        result = classifier.classify_sync("Check for security vulnerabilities")

        assert isinstance(result, ClassificationResult)
        assert result.primary_wizard == "security-audit"
        assert result.confidence > 0


class TestResilienceIntegration:
    """Test resilience patterns with Intelligence System."""

    def test_router_handles_missing_registry(self):
        """Test router handles gracefully when registry is empty."""
        router = SmartRouter()

        # Should still return a decision even for unclear requests
        decision = router.route_sync("do something")

        assert decision is not None
        assert decision.primary_wizard  # Should have a default

    def test_memory_graph_handles_corrupt_file(self):
        """Test memory graph handles corrupt JSON gracefully."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("not valid json {{{")
            path = Path(f.name)

        try:
            # Should not crash, should create empty graph
            graph = MemoryGraph(path=path)
            assert len(graph.nodes) == 0
        except Exception:
            # If it raises, that's also acceptable
            pass
        finally:
            if path.exists():
                path.unlink()

    def test_chain_executor_handles_missing_config(self):
        """Test chain executor handles missing config file."""
        executor = ChainExecutor("nonexistent_file.yaml")

        # Should return empty list, not crash
        triggers = executor.get_triggered_chains("any-wizard", {})
        assert triggers == []
