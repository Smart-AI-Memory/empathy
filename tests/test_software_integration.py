"""
Integration Tests for Software Development Plugin

Tests all three wizards working together on realistic projects.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import os
import tempfile

import pytest

from empathy_software_plugin.wizards.enhanced_testing_wizard import (
    EnhancedTestingWizard,
)
from empathy_software_plugin.wizards.performance_profiling_wizard import (
    PerformanceProfilingWizard,
)
from empathy_software_plugin.wizards.security_analysis_wizard import (
    SecurityAnalysisWizard,
)


class TestSoftwarePluginIntegration:
    """Integration tests for all Software Development wizards"""

    @pytest.mark.asyncio
    async def test_complete_project_analysis(self):
        """Test all three wizards analyzing the same project"""

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a realistic project with multiple issues
            api_file = os.path.join(tmpdir, "api.py")
            with open(api_file, "w") as f:
                f.write(
                    """
import hashlib
import os

# Hardcoded credential - security issue
API_KEY = "sk_live_abc123"

def authenticate_user(username, password):
    # Weak cryptography - security issue
    password_hash = hashlib.md5(password.encode()).hexdigest()

    # SQL injection - security issue
    query = f"SELECT * FROM users WHERE username='{username}' AND password_hash='{password_hash}'"
    user = db.execute(query).fetchone()

    return user is not None

def get_user_posts(user_id):
    # N+1 query pattern - performance issue
    # This function is called repeatedly
    query = f"SELECT * FROM posts WHERE user_id={user_id}"
    return db.execute(query).fetchall()

def process_user_request(user_id):
    # Hot path - performance issue
    # High-risk code - testing issue (no tests)
    user = get_user(user_id)
    posts = []
    for i in range(100):
        posts.extend(get_user_posts(i))
    return {"user": user, "posts": posts}

def execute_command(user_command):
    # Command injection - security issue
    os.system(user_command)
"""
                )

            # Create test file (incomplete coverage)
            test_file = os.path.join(tmpdir, "test_api.py")
            with open(test_file, "w") as f:
                f.write(
                    """
def test_authenticate_user():
    # Only tests happy path
    assert authenticate_user("user", "pass") is not None

# Missing tests for:
# - get_user_posts
# - process_user_request (HIGH RISK - payment/auth related)
# - execute_command (HIGH RISK - system command)
"""
                )

            # Create profiling data
            profile_data = json.dumps(
                {
                    "functions": [
                        {
                            "name": "process_user_request",
                            "file": api_file,
                            "line": 25,
                            "total_time": 4.5,
                            "self_time": 0.5,
                            "calls": 100,
                            "cumulative_time": 4.5,
                            "percent": 45.0,
                        },
                        {
                            "name": "get_user_posts",
                            "file": api_file,
                            "line": 19,
                            "total_time": 4.0,
                            "self_time": 0.004,
                            "calls": 1000,
                            "cumulative_time": 4.0,
                            "percent": 40.0,
                        },
                    ]
                }
            )

            # Endpoint configuration
            endpoint_config = {api_file: {"endpoint_public": True}}

            # Run all three wizards
            testing_wizard = EnhancedTestingWizard()
            performance_wizard = PerformanceProfilingWizard()
            security_wizard = SecurityAnalysisWizard()

            testing_result = await testing_wizard.analyze(
                {"source_files": [api_file], "test_files": [test_file], "project_path": tmpdir}
            )

            performance_result = await performance_wizard.analyze(
                {"profiler_data": profile_data, "profiler_type": "simple_json"}
            )

            security_result = await security_wizard.analyze(
                {
                    "source_files": [api_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            # Verify each wizard found issues
            assert len(testing_result["predictions"]) > 0
            assert len(performance_result["predictions"]) > 0
            assert len(security_result["predictions"]) > 0

            # Testing wizard should identify high-risk gaps
            high_risk_gaps = testing_result.get("high_risk_gaps", [])
            assert len(high_risk_gaps) > 0

            # Performance wizard should detect bottlenecks
            bottlenecks = performance_result.get("bottlenecks", [])
            assert len(bottlenecks) > 0
            # Should detect hot path or N+1 query
            bottleneck_types = {b["type"] for b in bottlenecks}
            assert "hot_path" in bottleneck_types or "n_plus_one" in bottleneck_types

            # Security wizard should find multiple vulnerabilities
            vulnerabilities = security_result.get("vulnerabilities_found", 0)
            assert vulnerabilities >= 3  # SQL injection, hardcoded creds, weak crypto

    @pytest.mark.asyncio
    async def test_integrated_risk_assessment(self):
        """Test combining predictions from all wizards for risk assessment"""

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create vulnerable payment processing code
            payment_file = os.path.join(tmpdir, "payment.py")
            with open(payment_file, "w") as f:
                f.write(
                    """
import hashlib

def process_payment(amount, card_number):
    # NO TESTS - high risk gap
    # SQL injection - security issue
    query = f"INSERT INTO payments (amount, card) VALUES ({amount}, '{card_number}')"
    db.execute(query)

    # Weak crypto for sensitive data
    encrypted_card = hashlib.md5(card_number.encode()).hexdigest()

    return True
"""
                )

            test_file = os.path.join(tmpdir, "test_payment.py")
            with open(test_file, "w") as f:
                f.write("# No tests for payment processing!")

            profile_data = json.dumps(
                {
                    "functions": [
                        {
                            "name": "process_payment",
                            "file": payment_file,
                            "line": 3,
                            "total_time": 0.5,
                            "self_time": 0.5,
                            "calls": 1000,
                            "cumulative_time": 0.5,
                            "percent": 50.0,
                        }
                    ]
                }
            )

            endpoint_config = {payment_file: {"endpoint_public": True}}

            # Run wizards
            testing_wizard = EnhancedTestingWizard()
            performance_wizard = PerformanceProfilingWizard()
            security_wizard = SecurityAnalysisWizard()

            testing_result = await testing_wizard.analyze(
                {"source_files": [payment_file], "test_files": [test_file], "project_path": tmpdir}
            )

            performance_result = await performance_wizard.analyze(
                {"profiler_data": profile_data, "profiler_type": "simple_json"}
            )

            security_result = await security_wizard.analyze(
                {
                    "source_files": [payment_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            # Combine risk assessments
            critical_issues = []

            # Check for untested payment code (CRITICAL)
            high_risk_gaps = testing_result.get("high_risk_gaps", [])
            for gap in high_risk_gaps:
                if "payment" in gap.get("function_name", "").lower():
                    critical_issues.append(
                        {
                            "type": "untested_payment_code",
                            "severity": "CRITICAL",
                            "source": "testing_wizard",
                        }
                    )

            # Check for exploitable vulnerabilities (CRITICAL)
            assessments = security_result.get("exploitability_assessments", [])
            for assessment in assessments:
                if assessment.get("exploitability") in ["CRITICAL", "HIGH"]:
                    critical_issues.append(
                        {
                            "type": "exploitable_vulnerability",
                            "severity": assessment["exploitability"],
                            "vulnerability": assessment["vulnerability"]["name"],
                            "source": "security_wizard",
                        }
                    )

            # Check for performance bottlenecks in critical code (HIGH)
            bottlenecks = performance_result.get("bottlenecks", [])
            for bottleneck in bottlenecks:
                if "payment" in bottleneck.get("function_name", "").lower():
                    critical_issues.append(
                        {
                            "type": "payment_performance_bottleneck",
                            "severity": "HIGH",
                            "source": "performance_wizard",
                        }
                    )

            # Should have identified multiple critical issues
            assert len(critical_issues) >= 2

            # Should have issues from multiple wizards
            sources = {issue["source"] for issue in critical_issues}
            assert len(sources) >= 2

    @pytest.mark.asyncio
    async def test_wizard_recommendations_complement(self):
        """Test that wizard recommendations work together"""

        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = os.path.join(tmpdir, "app.py")
            with open(code_file, "w") as f:
                f.write(
                    """
def search_users(query):
    # SQL injection + no tests + performance issue
    results = []
    for i in range(1000):
        result = db.execute(f"SELECT * FROM users WHERE name LIKE '%{query}%'").fetchone()
        if result:
            results.append(result)
    return results
"""
                )

            test_file = os.path.join(tmpdir, "test_app.py")
            with open(test_file, "w") as f:
                f.write("# No tests")

            profile_data = json.dumps(
                {
                    "functions": [
                        {
                            "name": "search_users",
                            "file": code_file,
                            "line": 1,
                            "total_time": 8.0,
                            "self_time": 8.0,
                            "calls": 100,
                            "cumulative_time": 8.0,
                            "percent": 80.0,
                        }
                    ]
                }
            )

            endpoint_config = {code_file: {"endpoint_public": True}}

            # Run wizards
            testing_wizard = EnhancedTestingWizard()
            performance_wizard = PerformanceProfilingWizard()
            security_wizard = SecurityAnalysisWizard()

            testing_result = await testing_wizard.analyze(
                {"source_files": [code_file], "test_files": [test_file], "project_path": tmpdir}
            )

            performance_result = await performance_wizard.analyze(
                {"profiler_data": profile_data, "profiler_type": "simple_json"}
            )

            security_result = await security_wizard.analyze(
                {
                    "source_files": [code_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            # Collect all recommendations
            all_recommendations = []
            all_recommendations.extend(testing_result.get("recommendations", []))
            all_recommendations.extend(performance_result.get("recommendations", []))
            all_recommendations.extend(security_result.get("recommendations", []))

            # Should have multiple recommendations addressing different aspects
            assert len(all_recommendations) >= 3

            # Check that recommendations address multiple concerns
            recommendation_text = " ".join(all_recommendations).lower()

            # Should mention testing
            assert any(word in recommendation_text for word in ["test", "coverage", "unit test"])

            # Should mention security
            assert any(
                word in recommendation_text
                for word in ["sql", "injection", "parameterized", "security"]
            )

            # Should mention performance
            assert any(
                word in recommendation_text
                for word in [
                    "performance",
                    "optimize",
                    "batch",
                    "cache",
                    "query",
                    "speed",
                    "time",
                    "fast",
                    "slow",
                    "bottleneck",
                    "profiling",
                    "response",
                ]
            )

    @pytest.mark.asyncio
    async def test_all_wizards_standard_interface(self):
        """Test all wizards follow standard interface"""

        testing_wizard = EnhancedTestingWizard()
        performance_wizard = PerformanceProfilingWizard()
        security_wizard = SecurityAnalysisWizard()

        # All should be Level 4
        assert testing_wizard.level == 4
        assert performance_wizard.level == 4
        assert security_wizard.level == 4

        # All should have names
        assert testing_wizard.name
        assert performance_wizard.name
        assert security_wizard.name

        # All should return standard structure with minimal valid input
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, "w") as f:
                f.write("def test(): pass")

            profile_data = json.dumps({"functions": []})

            testing_result = await testing_wizard.analyze(
                {"source_files": [test_file], "test_files": [test_file], "project_path": tmpdir}
            )

            performance_result = await performance_wizard.analyze(
                {"profiler_data": profile_data, "profiler_type": "simple_json"}
            )

            security_result = await security_wizard.analyze(
                {"source_files": [test_file], "project_path": tmpdir}
            )

            # All should have standard keys
            for result in [testing_result, performance_result, security_result]:
                assert "predictions" in result
                assert "recommendations" in result
                assert "confidence" in result
                assert isinstance(result["predictions"], list)
                assert isinstance(result["recommendations"], list)
                assert 0 <= result["confidence"] <= 1


class TestSoftwarePluginWorkflow:
    """Test realistic development workflows"""

    @pytest.mark.asyncio
    async def test_pre_deployment_workflow(self):
        """Test using all wizards before deployment"""

        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate code ready for deployment
            app_file = os.path.join(tmpdir, "application.py")
            with open(app_file, "w") as f:
                f.write(
                    """
def critical_function(user_input):
    # This is going to production
    result = db.execute(f"SELECT * FROM data WHERE id={user_input}")
    return result.fetchone()
"""
                )

            test_file = os.path.join(tmpdir, "test_application.py")
            with open(test_file, "w") as f:
                f.write("# Minimal tests")

            profile_data = json.dumps(
                {
                    "functions": [
                        {
                            "name": "critical_function",
                            "file": app_file,
                            "line": 2,
                            "total_time": 1.0,
                            "self_time": 1.0,
                            "calls": 100,
                            "cumulative_time": 1.0,
                            "percent": 100.0,
                        }
                    ]
                }
            )

            endpoint_config = {app_file: {"endpoint_public": True}}

            # Pre-deployment checks
            testing_wizard = EnhancedTestingWizard()
            security_wizard = SecurityAnalysisWizard()
            performance_wizard = PerformanceProfilingWizard()

            # Step 1: Security scan
            security_result = await security_wizard.analyze(
                {
                    "source_files": [app_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            # Step 2: Test coverage analysis
            testing_result = await testing_wizard.analyze(
                {"source_files": [app_file], "test_files": [test_file], "project_path": tmpdir}
            )

            # Step 3: Performance check
            performance_result = await performance_wizard.analyze(
                {"profiler_data": profile_data, "profiler_type": "simple_json"}
            )

            # Determine deployment readiness
            blockers = []

            # Check for IMMEDIATE security issues
            for assessment in security_result.get("exploitability_assessments", []):
                if "IMMEDIATE" in assessment.get("mitigation_urgency", ""):
                    blockers.append(f"Security: {assessment['vulnerability']['name']}")

            # Check for critical untested code
            for gap in testing_result.get("high_risk_gaps", []):
                if gap.get("risk_level") == "CRITICAL":
                    blockers.append(f"Testing: Untested {gap['function_name']}")

            # Check for critical performance issues
            for bottleneck in performance_result.get("bottlenecks", []):
                if bottleneck.get("severity") == "CRITICAL":
                    blockers.append(f"Performance: {bottleneck['type']}")

            # Should have identified blockers
            assert len(blockers) > 0

            # Deployment should be blocked
            deployment_ready = len(blockers) == 0
            assert deployment_ready is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
