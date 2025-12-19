"""
Tests for Security Analysis Wizard

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import os
import tempfile

import pytest

from empathy_software_plugin.wizards.security_analysis_wizard import (
    SecurityAnalysisWizard,
)


class TestSecurityAnalysisWizard:
    """Test Security Analysis Wizard"""

    @pytest.mark.asyncio
    async def test_basic_initialization(self):
        """Test wizard initializes correctly"""
        wizard = SecurityAnalysisWizard()

        assert wizard.name == "Security Analysis Wizard"
        assert wizard.level == 4
        assert wizard.pattern_detector is not None
        assert wizard.exploit_analyzer is not None

    @pytest.mark.asyncio
    async def test_sql_injection_detection(self):
        """Test detection of SQL injection vulnerabilities"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "database.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
def get_user(username):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query).fetchone()

def search_users(search_term):
    # Another SQL injection
    query = "SELECT * FROM users WHERE name LIKE '%" + search_term + "%'"
    return db.execute(query).fetchall()
"""
                )

            result = await wizard.analyze({"source_files": [vuln_file], "project_path": tmpdir})

            vulnerabilities = result["vulnerabilities_found"]
            assert vulnerabilities >= 2  # Should find both SQL injections

            by_category = result["by_category"]
            assert "injection" in by_category
            assert by_category["injection"] >= 2

    @pytest.mark.asyncio
    async def test_hardcoded_credentials_detection(self):
        """Test detection of hardcoded credentials"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "config.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
# Hardcoded credentials - CRITICAL security issue
API_KEY = "sk_live_abc123def456"
SECRET_TOKEN = "secret_token_12345"
DATABASE_PASSWORD = "MySuperSecretPassword123"

def connect():
    password = "hardcoded_password"
    return db.connect(password)
"""
                )

            result = await wizard.analyze({"source_files": [vuln_file], "project_path": tmpdir})

            vulnerabilities = result["vulnerabilities_found"]
            assert vulnerabilities >= 3  # Should find multiple hardcoded credentials

            by_severity = result["by_severity"]
            assert by_severity["CRITICAL"] >= 1

    @pytest.mark.asyncio
    async def test_xss_vulnerability_detection(self):
        """Test detection of XSS vulnerabilities"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "views.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
def render_comment(comment):
    # XSS vulnerability - innerHTML with user input
    html = f"<div>{comment}</div>"
    element.innerHTML = html
    return html

def show_message(msg):
    # Another XSS
    document.write(msg)
"""
                )

            result = await wizard.analyze({"source_files": [vuln_file], "project_path": tmpdir})

            by_category = result["by_category"]
            assert "cross_site_scripting" in by_category

    @pytest.mark.asyncio
    async def test_command_injection_detection(self):
        """Test detection of command injection"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "system.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
import os
import subprocess

def execute_command(user_command):
    # Command injection vulnerability
    os.system(user_command)

def run_script(script_name):
    # Another command injection
    subprocess.call(f"python {script_name}", shell=True)
"""
                )

            result = await wizard.analyze({"source_files": [vuln_file], "project_path": tmpdir})

            by_category = result["by_category"]
            assert "injection" in by_category

    @pytest.mark.asyncio
    async def test_weak_cryptography_detection(self):
        """Test detection of weak cryptography"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "auth.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
import hashlib

def hash_password(password):
    # Weak crypto - MD5
    return hashlib.md5(password.encode()).hexdigest()

def hash_token(token):
    # Weak crypto - SHA1
    return hashlib.sha1(token.encode()).hexdigest()
"""
                )

            result = await wizard.analyze({"source_files": [vuln_file], "project_path": tmpdir})

            by_category = result["by_category"]
            assert "cryptographic_failures" in by_category

    @pytest.mark.asyncio
    async def test_exploitability_assessment(self):
        """Test Level 4 exploitability assessment"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create vulnerable file
            vuln_file = os.path.join(tmpdir, "api.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
def public_search(query):
    # Publicly accessible SQL injection
    result = db.execute(f"SELECT * FROM data WHERE query='{query}'")
    return result.fetchall()
"""
                )

            # Mark endpoint as public
            endpoint_config = {vuln_file: {"endpoint_public": True}}

            result = await wizard.analyze(
                {
                    "source_files": [vuln_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            assessments = result["exploitability_assessments"]
            assert len(assessments) > 0

            # Should have high exploitability for public SQL injection
            high_exploitable = [
                a for a in assessments if a["exploitability"] in ["CRITICAL", "HIGH"]
            ]
            assert len(high_exploitable) > 0

            # Check assessment structure
            assessment = high_exploitable[0]
            assert "accessibility" in assessment
            assert "attack_complexity" in assessment
            assert "exploit_likelihood" in assessment
            assert "reasoning" in assessment
            assert "mitigation_urgency" in assessment

    @pytest.mark.asyncio
    async def test_public_vs_internal_risk(self):
        """Test risk assessment difference between public and internal endpoints"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            public_file = os.path.join(tmpdir, "public_api.py")
            with open(public_file, "w") as f:
                f.write(
                    """
def public_endpoint(user_input):
    query = f"SELECT * FROM data WHERE id={user_input}"
    return db.execute(query).fetchone()
"""
                )

            internal_file = os.path.join(tmpdir, "internal_api.py")
            with open(internal_file, "w") as f:
                f.write(
                    """
def internal_endpoint(user_input):
    query = f"SELECT * FROM data WHERE id={user_input}"
    return db.execute(query).fetchone()
"""
                )

            endpoint_config = {
                public_file: {"endpoint_public": True},
                internal_file: {"endpoint_public": False},
            }

            result = await wizard.analyze(
                {
                    "source_files": [public_file, internal_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            assessments = result["exploitability_assessments"]

            # Find assessments for each file
            public_assessments = [
                a for a in assessments if "public_api.py" in a["vulnerability"]["file_path"]
            ]
            internal_assessments = [
                a for a in assessments if "internal_api.py" in a["vulnerability"]["file_path"]
            ]

            # Public should have higher exploit likelihood
            if public_assessments and internal_assessments:
                assert (
                    public_assessments[0]["exploit_likelihood"]
                    > internal_assessments[0]["exploit_likelihood"]
                )

    @pytest.mark.asyncio
    async def test_predictions_generated(self):
        """Test Level 4 predictions"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple vulnerabilities
            vuln_file = os.path.join(tmpdir, "vulnerable.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
API_KEY = "sk_live_secret123"

def search(query):
    result = db.execute(f"SELECT * FROM users WHERE name='{query}'")
    return result.fetchall()

def authenticate(user, password):
    hash = hashlib.md5(password.encode()).hexdigest()
    return hash == stored_hash
"""
                )

            endpoint_config = {vuln_file: {"endpoint_public": True}}

            result = await wizard.analyze(
                {
                    "source_files": [vuln_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            predictions = result["predictions"]
            assert len(predictions) > 0

            # Should have imminent exploitation risk prediction
            exploitation_preds = [p for p in predictions if "exploitation" in p["type"].lower()]
            assert len(exploitation_preds) > 0

            # Check prediction structure
            pred = predictions[0]
            assert "type" in pred
            assert "severity" in pred
            assert "description" in pred
            assert "prevention_steps" in pred

    @pytest.mark.asyncio
    async def test_recommendations_generated(self):
        """Test recommendations are actionable"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "api.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id={user_id}"
    return db.execute(query).fetchone()
"""
                )

            endpoint_config = {vuln_file: {"endpoint_public": True}}

            result = await wizard.analyze(
                {
                    "source_files": [vuln_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            recommendations = result["recommendations"]
            assert len(recommendations) > 0

            # Should have specific recommendations
            assert any(
                "parameterized" in r.lower() or "prepared statement" in r.lower()
                for r in recommendations
            )

    @pytest.mark.asyncio
    async def test_severity_grouping(self):
        """Test vulnerabilities grouped by severity"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "mixed.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
# CRITICAL: SQL injection + hardcoded credential
API_KEY = "secret123"

def search(query):
    result = db.execute(f"SELECT * FROM users WHERE query='{query}'")
    return result.fetchall()

# MEDIUM: Weak crypto
def hash_data(data):
    return hashlib.md5(data.encode()).hexdigest()
"""
                )

            result = await wizard.analyze({"source_files": [vuln_file], "project_path": tmpdir})

            by_severity = result["by_severity"]

            # Should have vulnerabilities at multiple severity levels
            assert by_severity["CRITICAL"] > 0
            assert "HIGH" in by_severity or "MEDIUM" in by_severity

    @pytest.mark.asyncio
    async def test_insights_generation(self):
        """Test security insights"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = os.path.join(tmpdir, "api.py")
            with open(vuln_file, "w") as f:
                f.write(
                    """
def endpoint1(query):
    db.execute(f"SELECT * FROM data WHERE q='{query}'")

def endpoint2(search):
    db.execute(f"SELECT * FROM users WHERE s='{search}'")

def endpoint3(term):
    db.execute(f"SELECT * FROM products WHERE t='{term}'")
"""
                )

            endpoint_config = {vuln_file: {"endpoint_public": True}}

            result = await wizard.analyze(
                {
                    "source_files": [vuln_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            insights = result["insights"]

            assert "most_common_category" in insights
            assert "critical_exploitable" in insights
            assert "exploitable_percent" in insights
            assert "public_exposure" in insights
            assert "immediate_action_required" in insights

            # Multiple SQL injections = most common should be injection
            assert insights["most_common_category"] == "injection"

    @pytest.mark.asyncio
    async def test_standard_wizard_interface(self):
        """Test wizard follows BaseWizard interface"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, "w") as f:
                f.write("def test(): pass")

            result = await wizard.analyze({"source_files": [test_file], "project_path": tmpdir})

            # Check standard wizard outputs
            assert "predictions" in result
            assert "recommendations" in result
            assert "confidence" in result

            # Confidence should be between 0 and 1
            assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_empty_project(self):
        """Test handling of project with no vulnerabilities"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            safe_file = os.path.join(tmpdir, "safe.py")
            with open(safe_file, "w") as f:
                f.write(
                    """
def safe_function():
    # Safe code with parameterized queries
    result = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return result.fetchone()
"""
                )

            result = await wizard.analyze({"source_files": [safe_file], "project_path": tmpdir})

            # Should handle gracefully
            assert "vulnerabilities_found" in result
            assert "predictions" in result
            assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_mitigation_urgency_levels(self):
        """Test different mitigation urgency levels"""
        wizard = SecurityAnalysisWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            critical_file = os.path.join(tmpdir, "critical.py")
            with open(critical_file, "w") as f:
                f.write(
                    """
def public_search(query):
    # Public SQL injection - IMMEDIATE urgency
    result = db.execute(f"SELECT * FROM users WHERE q='{query}'")
    return result.fetchall()
"""
                )

            endpoint_config = {critical_file: {"endpoint_public": True}}

            result = await wizard.analyze(
                {
                    "source_files": [critical_file],
                    "project_path": tmpdir,
                    "endpoint_config": endpoint_config,
                }
            )

            assessments = result["exploitability_assessments"]

            # Should have IMMEDIATE mitigation urgency for public SQL injection
            immediate = [a for a in assessments if "IMMEDIATE" in a["mitigation_urgency"]]
            assert len(immediate) > 0


class TestOWASPPatternDetector:
    """Test OWASP pattern detection"""

    @pytest.mark.asyncio
    async def test_sql_injection_patterns(self):
        """Test SQL injection pattern detection"""
        from empathy_software_plugin.wizards.security.owasp_patterns import (
            OWASPPatternDetector,
        )

        detector = OWASPPatternDetector()

        code = """
def vulnerable1(user_input):
    query = f"SELECT * FROM users WHERE name='{user_input}'"
    return db.execute(query)

def vulnerable2(search):
    query = "SELECT * FROM data WHERE q = '" + search + "'"
    return db.execute(query)
"""

        vulnerabilities = detector.detect_vulnerabilities(code, "test.py")

        # Should detect both SQL injections
        sql_injections = [v for v in vulnerabilities if v["category"] == "injection"]
        assert len(sql_injections) >= 2

    @pytest.mark.asyncio
    async def test_hardcoded_secret_patterns(self):
        """Test hardcoded secret detection"""
        from empathy_software_plugin.wizards.security.owasp_patterns import (
            OWASPPatternDetector,
        )

        detector = OWASPPatternDetector()

        code = """
API_KEY = "sk_live_12345"
SECRET_TOKEN = "secret_abc123"
PASSWORD = "MyPassword123"
"""

        vulnerabilities = detector.detect_vulnerabilities(code, "config.py")

        # Should detect hardcoded secrets
        secrets = [
            v
            for v in vulnerabilities
            if "hardcoded" in v["name"].lower() or "credential" in v["name"].lower()
        ]
        assert len(secrets) >= 3


class TestExploitAnalyzer:
    """Test exploit analysis for Level 4 predictions"""

    @pytest.mark.asyncio
    async def test_exploit_likelihood_calculation(self):
        """Test exploit likelihood calculation"""
        from empathy_software_plugin.wizards.security.exploit_analyzer import (
            ExploitAnalyzer,
        )

        analyzer = ExploitAnalyzer()

        # Public SQL injection - should have high likelihood
        vulnerability = {
            "category": "injection",
            "name": "SQL Injection",
            "severity": "CRITICAL",
            "file_path": "api.py",
            "line_number": 10,
        }

        endpoint_context = {"endpoint_public": True}

        assessment = analyzer.assess_exploitability(vulnerability, endpoint_context)

        # Should have high exploit likelihood
        assert assessment.exploit_likelihood > 0.7
        assert assessment.exploitability in ["CRITICAL", "HIGH"]
        assert (
            "IMMEDIATE" in assessment.mitigation_urgency
            or "URGENT" in assessment.mitigation_urgency
        )

    @pytest.mark.asyncio
    async def test_internal_vs_public_accessibility(self):
        """Test accessibility impact on exploitability"""
        from empathy_software_plugin.wizards.security.exploit_analyzer import (
            ExploitAnalyzer,
        )

        analyzer = ExploitAnalyzer()

        vulnerability = {
            "category": "injection",
            "name": "SQL Injection",
            "severity": "HIGH",
            "file_path": "api.py",
            "line_number": 10,
        }

        # Public endpoint
        public_assessment = analyzer.assess_exploitability(vulnerability, {"endpoint_public": True})

        # Internal endpoint
        internal_assessment = analyzer.assess_exploitability(
            vulnerability, {"endpoint_public": False}
        )

        # Public should have higher likelihood
        assert public_assessment.exploit_likelihood > internal_assessment.exploit_likelihood


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
