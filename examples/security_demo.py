"""
Security Analysis Wizard - Live Demonstration

Shows security vulnerability detection and exploitability assessment.

⚠️  WARNING: This file contains INTENTIONALLY VULNERABLE code for demonstration purposes.
    DO NOT use this code in production. DO NOT deploy this code to any live system.
    The vulnerabilities are for educational use only to demonstrate the Security Wizard.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import os
import tempfile

# Mock vulnerable code samples
VULNERABLE_AUTH_CODE = '''
import sqlite3

def login_user(username, password):
    """Authenticate user - VULNERABLE!"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # CRITICAL: SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)

    user = cursor.fetchone()
    return user is not None
'''

VULNERABLE_API_CODE = """
from flask import Flask, request

app = Flask(__name__)

# CRITICAL: Missing authentication + Command injection
@app.route('/admin/execute')
def admin_execute():
    import os
    command = request.args.get('cmd')
    # CRITICAL: Command injection with shell=True
    os.system(command)
    return "Executed"

# HIGH: XSS vulnerability
@app.route('/display')
def display_message():
    msg = request.args.get('message')
    # HIGH: XSS via innerHTML equivalent
    return f"<div>{msg}</div>"
"""

VULNERABLE_PAYMENT_CODE = '''
import os

# CRITICAL: Loading credentials - should use secure secret management
API_KEY = os.getenv("DEMO_STRIPE_API_KEY", "sk_live_DEMO_KEY_NOT_REAL")
SECRET_TOKEN = os.getenv("DEMO_STRIPE_SECRET", "whsec_DEMO_SECRET_NOT_REAL")

def process_payment(amount, card_number):
    """Process payment - CRITICAL ISSUES!"""
    # HIGH: Sensitive data in logs
    print(f"Processing payment: card={card_number}, amount={amount}")

    # MEDIUM: Using MD5 (weak crypto)
    import hashlib
    token = hashlib.md5(card_number.encode()).hexdigest()

    return {"status": "processed", "token": token}
'''


async def demo_basic_scanning():
    """Demo 1: Basic Vulnerability Scanning"""
    print("=" * 70)
    print("DEMO 1: Basic Security Vulnerability Scanning")
    print("=" * 70)

    from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

    wizard = SecurityAnalysisWizard()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create vulnerable files
        auth_file = os.path.join(tmpdir, "auth.py")
        with open(auth_file, "w") as f:
            f.write(VULNERABLE_AUTH_CODE)

        api_file = os.path.join(tmpdir, "api.py")
        with open(api_file, "w") as f:
            f.write(VULNERABLE_API_CODE)

        payment_file = os.path.join(tmpdir, "payment.py")
        with open(payment_file, "w") as f:
            f.write(VULNERABLE_PAYMENT_CODE)

        result = await wizard.analyze(
            {"source_files": [auth_file, api_file, payment_file], "project_path": tmpdir}
        )

        print("\n📊 Security Scan Results:")
        print(f"  Total Vulnerabilities: {result['vulnerabilities_found']}")

        print("\n⚠️  By Severity:")
        by_severity = result["by_severity"]
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = by_severity.get(severity, 0)
            if count > 0:
                print(f"    {severity}: {count}")

        print("\n📋 By Category:")
        by_category = result["by_category"]
        for category, count in sorted(by_category.items(), key=lambda x: -x[1])[:5]:
            print(f"    {category}: {count}")

    print("\n" + "=" * 70)


async def demo_exploitability():
    """Demo 2: Level 4 - Exploitability Assessment"""
    print("\n" + "=" * 70)
    print("DEMO 2: Level 4 - Exploitability Assessment")
    print("=" * 70)

    from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

    wizard = SecurityAnalysisWizard()

    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = os.path.join(tmpdir, "auth.py")
        with open(auth_file, "w") as f:
            f.write(VULNERABLE_AUTH_CODE)

        api_file = os.path.join(tmpdir, "api.py")
        with open(api_file, "w") as f:
            f.write(VULNERABLE_API_CODE)

        # Provide endpoint configuration
        endpoint_config = {
            auth_file: {"endpoint_public": False, "requires_authentication": True},
            api_file: {
                "endpoint_public": True,  # Public API!
                "requires_authentication": False,  # No auth!
            },
        }

        result = await wizard.analyze(
            {"source_files": [auth_file, api_file], "endpoint_config": endpoint_config}
        )

        print("\n🔍 EXPLOITABILITY ASSESSMENT:\n")

        for assessment in result["exploitability_assessments"][:5]:
            print(f"  [{assessment['exploitability']}] {assessment['vulnerability']['name']}")
            print(
                f"      File: {os.path.basename(assessment['vulnerability']['file_path'])}:{assessment['vulnerability']['line_number']}"
            )
            print(f"      Accessibility: {assessment['accessibility']}")
            print(f"      Attack Complexity: {assessment['attack_complexity']}")
            print(f"      Exploit Likelihood: {assessment['exploit_likelihood']:.0%}")
            print(f"      Mitigation: {assessment['mitigation_urgency']}")

            if assessment["reasoning"]:
                print("      Reasoning:")
                for reason in assessment["reasoning"][:2]:
                    print(f"        - {reason}")
            print()

    print("=" * 70)


async def demo_predictions():
    """Demo 3: Level 4 Predictions"""
    print("\n" + "=" * 70)
    print("DEMO 3: Level 4 - Security Predictions")
    print("=" * 70)

    from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

    wizard = SecurityAnalysisWizard()

    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = os.path.join(tmpdir, "auth.py")
        with open(auth_file, "w") as f:
            f.write(VULNERABLE_AUTH_CODE)

        api_file = os.path.join(tmpdir, "api.py")
        with open(api_file, "w") as f:
            f.write(VULNERABLE_API_CODE)

        payment_file = os.path.join(tmpdir, "payment.py")
        with open(payment_file, "w") as f:
            f.write(VULNERABLE_PAYMENT_CODE)

        endpoint_config = {api_file: {"endpoint_public": True, "requires_authentication": False}}

        result = await wizard.analyze(
            {
                "source_files": [auth_file, api_file, payment_file],
                "endpoint_config": endpoint_config,
            }
        )

        print("\n🔮 PREDICTIONS:\n")

        for pred in result["predictions"]:
            print(f"  Type: {pred['type'].upper()}")
            print(f"  Severity: {pred['severity'].upper()}")
            print(f"  {pred['description']}")

            if "affected_files" in pred:
                print("\n  Affected Files:")
                for file in pred["affected_files"][:3]:
                    print(f"    - {os.path.basename(file)}")

            if "prevention_steps" in pred:
                print("\n  Prevention Steps:")
                for step in pred["prevention_steps"][:3]:
                    print(f"    - {step}")
            print()

    print("=" * 70)


async def demo_recommendations():
    """Demo 4: Actionable Recommendations"""
    print("\n" + "=" * 70)
    print("DEMO 4: Actionable Security Recommendations")
    print("=" * 70)

    from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

    wizard = SecurityAnalysisWizard()

    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = os.path.join(tmpdir, "auth.py")
        with open(auth_file, "w") as f:
            f.write(VULNERABLE_AUTH_CODE)

        api_file = os.path.join(tmpdir, "api.py")
        with open(api_file, "w") as f:
            f.write(VULNERABLE_API_CODE)

        result = await wizard.analyze(
            {
                "source_files": [auth_file, api_file],
                "endpoint_config": {api_file: {"endpoint_public": True}},
            }
        )

        print("\n📝 RECOMMENDATIONS:\n")

        for rec in result["recommendations"]:
            print(f"  • {rec}")

    print("\n" + "=" * 70)


async def demo_the_value():
    """Demo 5: Show the Value"""
    print("\n" + "=" * 70)
    print("DEMO 5: The Value - Exploitability Prediction")
    print("=" * 70)

    print("\n" + "TRADITIONAL SECURITY SCANNING".center(70))
    print("-" * 70)
    print("✓ SQL Injection found (CRITICAL)")
    print("✓ Hardcoded API key found (HIGH)")
    print("✓ Missing semicolon (STYLE)")
    print("")
    print("Total: 3 issues")
    print("")
    print("...but which one should you fix first?")

    print("\n" + "SECURITY ANALYSIS WIZARD".center(70))
    print("-" * 70)
    print("✓ SQL Injection (CRITICAL)")
    print("   Exploitability: CRITICAL")
    print("   Accessibility: PUBLIC")
    print("   Likelihood: 90%")
    print("   In our experience: Actively scanned by automated tools")
    print("   Mitigation: IMMEDIATE - Fix before deployment")
    print("")
    print("✓ Hardcoded API key (HIGH)")
    print("   Exploitability: HIGH")
    print("   Accessibility: INTERNAL")
    print("   Likelihood: 85%")
    print("   In our experience: Credentials harvested from GitHub leaks")
    print("   Mitigation: URGENT - Fix within 24 hours")

    print("\n" + "THE DIFFERENCE".center(70))
    print("-" * 70)
    print("Traditional scanning finds vulnerabilities.")
    print("Security Wizard predicts which will ACTUALLY be exploited.")
    print("")
    print("It prioritizes by real-world attack likelihood,")
    print("not just theoretical severity.")

    print("\n" + "=" * 70)


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 11 + "SECURITY ANALYSIS WIZARD - DEMONSTRATIONS" + " " * 16 + "║")
    print("║" + " " * 13 + "Vulnerability Detection & Exploit Prediction" + " " * 12 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n⚠️  WARNING: This demo uses INTENTIONALLY VULNERABLE code.")
    print("    For educational purposes only. DO NOT use in production.\n")

    await demo_basic_scanning()
    await demo_exploitability()
    await demo_predictions()
    await demo_recommendations()
    await demo_the_value()

    print("\n" + "=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ OWASP Top 10 pattern detection")
    print("  ✅ Level 4: Exploitability assessment")
    print("  ✅ Level 4: Predicts which vulnerabilities will be exploited")
    print("  ✅ Real-world attack likelihood analysis")
    print("  ✅ Prioritization by actual risk")
    print("\nIn our experience, SQL injection and command injection are")
    print("actively scanned by automated tools. This wizard helps you")
    print("focus on vulnerabilities that are actually exploitable.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
