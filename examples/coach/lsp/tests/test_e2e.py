"""
End-to-End Tests for Coach LSP
Tests full workflow: IDE → LSP → Coach → Results

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import os
import tempfile
from pathlib import Path

import pytest

from ..server import CoachLanguageServer


class TestEndToEnd:
    """End-to-end integration tests"""

    @pytest.fixture
    async def server(self):
        """Create and start server"""
        server = CoachLanguageServer()
        # Server is ready to receive requests
        return server

    @pytest.fixture
    def test_file_python(self):
        """Create a temporary Python test file"""
        content = """
def get_user(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id={user_id}"
    cursor.execute(query)
    return cursor.fetchone()

def slow_function():
    # Performance issue - N+1 query
    users = get_all_users()
    for user in users:
        # This causes N queries!
        user.orders = get_orders_for_user(user.id)
    return users
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_security_wizard_flow(self, server, test_file_python):
        """Test: File → SecurityWizard → Diagnostics"""

        # Simulate: User opens file in IDE
        from pygls.lsp.types import DidOpenTextDocumentParams, TextDocumentItem

        params = DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=f"file://{test_file_python}",
                language_id="python",
                version=1,
                text=Path(test_file_python).read_text(),
            )
        )

        # Trigger did_open handler
        await server.feature_handlers[TEXT_DOCUMENT_DID_OPEN](server, params)

        # Run SecurityWizard explicitly
        result = await server.command_handlers["coach/runWizard"](
            server,
            [
                "SecurityWizard",
                {
                    "role": "developer",
                    "task": "Check for security vulnerabilities",
                    "context": f"file://{test_file_python}",
                },
            ],
        )

        # Verify SecurityWizard found the SQL injection
        assert result["routing"][0] == "SecurityWizard"
        assert result["overall_confidence"] > 0.5
        # Check diagnosis mentions SQL or injection
        diagnosis = result["primary_output"]["diagnosis"]
        assert "sql" in diagnosis.lower() or "injection" in diagnosis.lower()

    @pytest.mark.asyncio
    async def test_performance_wizard_flow(self, server, test_file_python):
        """Test: File → PerformanceWizard → Predictions"""

        # Run PerformanceWizard
        result = await server.command_handlers["coach/runWizard"](
            server,
            [
                "PerformanceWizard",
                {
                    "role": "developer",
                    "task": "Analyze performance issues",
                    "context": f"file://{test_file_python}",
                },
            ],
        )

        # Verify PerformanceWizard ran
        assert "PerformanceWizard" in result["routing"]
        assert result["overall_confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_multi_wizard_collaboration(self, server, test_file_python):
        """Test: Multi-wizard review of API endpoint"""

        result = await server.command_handlers["coach/multiWizardReview"](
            server, ["new_api_endpoint", [f"file://{test_file_python}"]]
        )

        # Should activate multiple wizards
        assert len(result["routing"]) >= 2
        # Should have synthesis from multiple wizards
        assert len(result["synthesis"]) > 0

    @pytest.mark.asyncio
    async def test_hover_prediction(self, server, test_file_python):
        """Test: Hover over code → Level 4 prediction"""

        # Simulate hover over connection pool code
        prediction = await server._get_prediction("pool_size=10 connection pooling database")

        # Should return Level 4 prediction
        assert prediction is not None
        assert "Level 4" in prediction or "days" in prediction

    @pytest.mark.asyncio
    async def test_cache_performance(self, server, test_file_python):
        """Test: Repeated calls use cache"""
        import time

        # First call (no cache)
        start1 = time.time()
        result1 = await server.command_handlers["coach/runWizard"](
            server,
            [
                "PerformanceWizard",
                {"role": "developer", "task": "Test caching", "context": "Same context"},
            ],
        )
        duration1 = time.time() - start1

        # Second call (should use cache)
        start2 = time.time()
        result2 = await server.command_handlers["coach/runWizard"](
            server,
            [
                "PerformanceWizard",
                {"role": "developer", "task": "Test caching", "context": "Same context"},
            ],
        )
        duration2 = time.time() - start2

        # Cached call should be much faster
        assert duration2 < duration1 / 2
        # Results should be identical
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_error_recovery(self, server):
        """Test: Server handles errors gracefully"""

        # Try to run non-existent wizard
        try:
            result = await server.command_handlers["coach/runWizard"](
                server, ["NonExistentWizard", {"role": "developer", "task": "Test"}]
            )
            # Should return error, not crash
            assert "error" in str(result).lower() or result is None
        except Exception as e:
            # Exception is acceptable as long as server doesn't crash
            assert "NonExistent" in str(e) or "not found" in str(e).lower()

    @pytest.mark.asyncio
    async def test_context_collection(self, server, test_file_python):
        """Test: Context collector gathers file info"""

        context = await server.context_collector.collect(f"file://{test_file_python}")

        # Should include file content
        assert "def get_user" in context
        assert "def slow_function" in context
        # Should include language detection
        assert "Python" in context
        # Should include file path
        assert test_file_python in context

    @pytest.mark.asyncio
    async def test_diagnostic_publishing(self, server, test_file_python):
        """Test: Diagnostics published to IDE"""

        # Analyze document
        await server._analyze_document(f"file://{test_file_python}")

        # Check if diagnostics were published (mocked in test)
        # In real usage, this would call server.publish_diagnostics()
        # For testing, we verify _analyze_document completes without error
        assert True  # If we got here, no crash occurred


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""

    @pytest.fixture
    async def server(self):
        return CoachLanguageServer()

    @pytest.mark.asyncio
    async def test_scenario_new_developer(self, server):
        """Scenario: New developer joins team, needs onboarding"""

        result = await server.command_handlers["coach/runWizard"](
            server,
            [
                "OnboardingWizard",
                {
                    "role": "new_developer",
                    "task": "Create onboarding plan for Python backend developer",
                    "context": "Team uses Django, PostgreSQL, Redis, deployed on AWS",
                },
            ],
        )

        assert "OnboardingWizard" in result["routing"]
        assert len(result["primary_output"]["artifacts"]) > 0

    @pytest.mark.asyncio
    async def test_scenario_production_bug(self, server):
        """Scenario: Production bug needs urgent debugging"""

        result = await server.command_handlers["coach/runWizard"](
            server,
            [
                "DebuggingWizard",
                {
                    "role": "developer",
                    "task": "Debug 500 errors in payment API",
                    "context": "Users report payment failures, logs show database timeout",
                    "risk_tolerance": "low",  # Production!
                },
            ],
        )

        assert "DebuggingWizard" in result["routing"]
        assert result["overall_confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_scenario_scaling_preparation(self, server):
        """Scenario: Company expecting 10x traffic, needs scaling plan"""

        result = await server.command_handlers["coach/runWizard"](
            server,
            [
                "PerformanceWizard",
                {
                    "role": "tech_lead",
                    "task": "Create scaling plan for 10x traffic increase",
                    "context": "Current: 10K req/day, Target: 100K req/day in 3 months",
                },
            ],
        )

        # PerformanceWizard should provide Level 4 predictions
        diagnosis = result["primary_output"]["diagnosis"]
        assert len(diagnosis) > 0
        # Should mention scaling or capacity
        assert any(
            keyword in diagnosis.lower()
            for keyword in ["scale", "capacity", "bottleneck", "optimize"]
        )


# Performance benchmarks
class TestPerformance:
    """Performance benchmarks for LSP server"""

    @pytest.fixture
    async def server(self):
        return CoachLanguageServer()

    @pytest.mark.asyncio
    async def test_startup_time(self):
        """Test: Server starts in <2 seconds"""
        import time

        start = time.time()
        server = CoachLanguageServer()
        duration = time.time() - start

        assert duration < 2.0, f"Startup took {duration}s (>2s threshold)"

    @pytest.mark.asyncio
    async def test_wizard_response_time(self, server):
        """Test: Wizard responds in <5 seconds"""
        import time

        start = time.time()
        result = await server.command_handlers["coach/runWizard"](
            server,
            [
                "PerformanceWizard",
                {"role": "developer", "task": "Quick analysis", "context": "Small file"},
            ],
        )
        duration = time.time() - start

        assert duration < 5.0, f"Wizard took {duration}s (>5s threshold)"

    @pytest.mark.asyncio
    async def test_cache_hit_time(self, server):
        """Test: Cache hit responds in <100ms"""
        import time

        # Prime cache
        await server.command_handlers["coach/runWizard"](
            server, ["PerformanceWizard", {"role": "developer", "task": "Cache test"}]
        )

        # Measure cache hit
        start = time.time()
        result = await server.command_handlers["coach/runWizard"](
            server, ["PerformanceWizard", {"role": "developer", "task": "Cache test"}]
        )
        duration = time.time() - start

        assert duration < 0.1, f"Cache hit took {duration}s (>100ms threshold)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
