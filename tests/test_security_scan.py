"""
Automated Security Scanning with Bandit

Runs Bandit security scanner on the codebase to detect common vulnerabilities.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import subprocess


class TestSecurityScanning:
    """Test automated security scanning with Bandit"""

    def test_bandit_security_scan(self):
        """Run Bandit security scanner and ensure no high/medium severity issues"""

        # Run bandit scan
        subprocess.run(
            [
                "bandit",
                "-r",
                "src/",
                "empathy_software_plugin/",
                "empathy_llm_toolkit/",
                "coach_wizards/",
                "empathy_healthcare_plugin/",
                "-f",
                "json",
                "-o",
                "security_scan_results.json",
                "--severity-level",
                "medium",
                "--confidence-level",
                "medium",
            ],
            capture_output=True,
            text=True,
        )

        # Read results
        with open("security_scan_results.json") as f:
            scan_data = json.load(f)

        issues = scan_data.get("results", [])
        high_severity = [r for r in issues if r["issue_severity"] == "HIGH"]
        medium_severity = [r for r in issues if r["issue_severity"] == "MEDIUM"]

        # Print summary
        print("\n🔒 Security Scan Results:")
        print(f"  Total issues: {len(issues)}")
        print(f"  High severity: {len(high_severity)}")
        print(f"  Medium severity: {len(medium_severity)}")

        # Assert no high or medium severity issues
        if high_severity:
            print("\n❌ High severity issues found:")
            for issue in high_severity:
                print(f"  - {issue['test_id']}: {issue['issue_text']}")
                print(f"    File: {issue['filename']}:{issue['line_number']}")

        if medium_severity:
            print("\n⚠️  Medium severity issues found:")
            for issue in medium_severity:
                print(f"  - {issue['test_id']}: {issue['issue_text']}")
                print(f"    File: {issue['filename']}:{issue['line_number']}")

        # Fail if any high or medium severity issues found
        assert len(high_severity) == 0, f"Found {len(high_severity)} high severity security issues"
        assert (
            len(medium_severity) == 0
        ), f"Found {len(medium_severity)} medium severity security issues"

        print("\n✅ Security scan passed: No high or medium severity vulnerabilities detected")

    def test_bandit_is_installed(self):
        """Verify Bandit is installed and accessible"""
        result = subprocess.run(["bandit", "--version"], capture_output=True, text=True)
        assert result.returncode == 0, "Bandit is not installed. Run: pip install bandit"
        assert "bandit" in result.stdout.lower()
