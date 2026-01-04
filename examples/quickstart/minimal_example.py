"""Minimal Empathy Framework Example
===================================

This is the simplest possible example of using a Coach wizard.
Run this file to see Level 4 Anticipatory predictions in action.

Requirements:
    pip install -r requirements.txt

Usage:
    python minimal_example.py
"""

from datetime import datetime

from coach_wizards.security_wizard import SecurityWizard

# Sample code with security issues
SAMPLE_CODE = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL Injection!
    cursor.execute(query)
    return cursor.fetchone()

API_KEY = "sk-1234567890abcdef"  # Hardcoded secret!
"""


def main():
    print("=" * 60)
    print("Empathy Framework - Minimal Example")
    print("=" * 60)

    # Initialize Security Wizard
    print("\n1. Initializing Security Wizard...")
    wizard = SecurityWizard()

    # Analyze code for current issues
    print("\n2. Analyzing code for current security issues...")
    result = wizard.run_full_analysis(
        code=SAMPLE_CODE,
        file_path="sample.py",
        language="python",
        project_context={
            "team_size": 5,
            "deployment_frequency": "daily",
            "user_count": 1000,
            "growth_rate": "20% monthly",
        },
    )

    # Display current issues
    print(f"\n{'=' * 60}")
    print(f"CURRENT ISSUES FOUND: {len(result.issues)}")
    print(f"{'=' * 60}")

    for i, issue in enumerate(result.issues, 1):
        print(f"\n[{i}] {issue.severity.upper()}: {issue.message}")
        print(f"    Line: {issue.line_number}")
        print(f"    Category: {issue.category}")
        print(f"    Confidence: {issue.confidence:.0%}")
        if issue.fix_suggestion:
            print(f"    Fix: {issue.fix_suggestion}")

    # Display Level 4 Anticipatory predictions
    print(f"\n{'=' * 60}")
    print(f"LEVEL 4 PREDICTIONS (Next 90 days): {len(result.predictions)}")
    print(f"{'=' * 60}")

    for i, pred in enumerate(result.predictions, 1):
        days_ahead = (pred.predicted_date - datetime.now()).days
        print(f"\n[{i}] {pred.impact.upper()}: {pred.issue_type}")
        print(
            f"    Predicted Date: {pred.predicted_date.strftime('%Y-%m-%d')} ({days_ahead} days from now)",
        )
        print(f"    Probability: {pred.probability:.0%}")
        print(f"    Reasoning: {pred.reasoning}")
        print("    Prevention Steps:")
        for step in pred.prevention_steps:
            print(f"      - {step}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"✓ Found {len(result.issues)} current security issues")
    print(f"✓ Predicted {len(result.predictions)} future issues")
    print("✓ Time saved: Prevented issues before they became incidents")
    print("\nThis is Level 4 Anticipatory Empathy in action!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
