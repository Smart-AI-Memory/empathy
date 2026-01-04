#!/usr/bin/env python3
"""Example 3: Security False Positive Learning
===========================================

Demonstrates how persistent memory enables AI to learn from team
security decisions—reducing noise and focusing on real issues.

BEFORE: Same false positives flagged every scan.
AFTER:  "Suppressing 8 warnings you've previously marked as acceptable."

Run this example:
    pip install empathy-framework
    python 03_security_learning.py

What it shows:
    1. Scan code for security vulnerabilities
    2. Record team decisions about findings
    3. Apply learned patterns to future scans
    4. Reduce alert fatigue with institutional knowledge

Copyright 2025 Smart AI Memory, LLC
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from empathy_software_plugin.wizards import SecurityLearningWizard


def seed_team_decisions(wizard: SecurityLearningWizard):
    """Simulate team security decisions from past reviews"""
    decisions_data = {
        "decisions": [
            # Team decided: SQL injection warnings in ORM code are false positives
            {
                "finding_hash": "sql_injection",
                "decision": "false_positive",
                "reason": "Using SQLAlchemy ORM which handles SQL escaping",
                "decided_by": "@sarah",
                "decided_at": (datetime.now() - timedelta(days=45)).isoformat(),
                "applies_to": "all",  # Applies to all SQL injection findings
            },
            # Team decided: Math.random() is acceptable for non-security use
            {
                "finding_hash": "insecure_random",
                "decision": "accepted",
                "reason": "Only used for UI animations, not security",
                "decided_by": "@mike",
                "decided_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "applies_to": "all",
            },
            # Team decided: XSS warnings in React are false positives
            {
                "finding_hash": "xss",
                "decision": "false_positive",
                "reason": "React's JSX auto-escapes, dangerouslySetInnerHTML not used",
                "decided_by": "@tech_lead",
                "decided_at": (datetime.now() - timedelta(days=60)).isoformat(),
                "applies_to": "all",
            },
        ],
    }

    # Store in pattern storage
    decisions_file = wizard.pattern_storage_path / "team_decisions.json"
    decisions_file.parent.mkdir(parents=True, exist_ok=True)
    with open(decisions_file, "w") as f:
        json.dump(decisions_data, f, indent=2)


async def main():
    # Initialize the wizard
    wizard = SecurityLearningWizard(pattern_storage_path="./patterns/security")

    # -------------------------------------------------------------------------
    # STEP 1: Load team decisions (simulating accumulated knowledge)
    # -------------------------------------------------------------------------
    print("Loading team security decisions from past reviews...")
    seed_team_decisions(wizard)
    print("  ✓ Loaded 3 team decisions")

    # -------------------------------------------------------------------------
    # STEP 2: Create sample code to scan
    # -------------------------------------------------------------------------
    sample_dir = Path("./sample_security")
    sample_dir.mkdir(exist_ok=True)

    # Create sample file with various security patterns
    sample_file = sample_dir / "example.py"
    sample_file.write_text(
        """
from database import db

def get_user(user_id):
    # This triggers SQL injection warning
    # But team decided: ORM handles escaping
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

def generate_token():
    # This triggers insecure random warning
    # But team decided: OK for non-security use
    import random
    return random.random()

def render_html(content):
    # This triggers XSS warning
    # But team decided: React escapes by default
    return f"<div>{content}</div>"

def execute_command(cmd):
    # This is a REAL vulnerability - not suppressed
    import subprocess
    subprocess.call(cmd, shell=True)

def store_secret():
    # This is a REAL vulnerability - not suppressed
    api_key = "sk-secret-key-12345"
    return api_key
""",
    )

    # -------------------------------------------------------------------------
    # STEP 3: Scan with learning applied
    # -------------------------------------------------------------------------
    print("\nScanning for security vulnerabilities...")
    print("(with team decisions applied)\n")

    result = await wizard.analyze(
        {
            "project_path": str(sample_dir),
            "apply_learned_patterns": True,
            "scan_depth": "quick",
        },
    )

    # Clean up
    sample_file.unlink()
    sample_dir.rmdir()

    # -------------------------------------------------------------------------
    # STEP 4: See the power of learned patterns
    # -------------------------------------------------------------------------
    print("=" * 60)
    print("RESULTS: Security Scan with Learning")
    print("=" * 60)

    print("\n📊 SCAN SUMMARY:")
    print(f"   Raw Findings: {result['raw_findings_count']}")
    print(f"   After Learning: {result['summary']['total_after_learning']}")

    learning = result["learning_applied"]
    if learning["enabled"]:
        print("\n🧠 LEARNING APPLIED:")
        print(f"   Suppressed: {learning['suppressed_count']} findings")
        print(f"   Noise Reduction: {learning['noise_reduction_percent']}%")
        print(f"   Team Decisions Used: {result['team_decisions_count']}")

        if learning["suppression_details"]:
            print("\n   Suppression Details:")
            for detail in learning["suppression_details"][:3]:
                print(f"   • {detail['type']}")
                print(f"     Decision: {detail['decision']} by {detail['decided_by']}")
                print(f'     Reason: "{detail["reason"]}"')

    print("\n⚠️  REMAINING FINDINGS (require attention):")
    severity = result["summary"]["by_severity"]
    for level in ["critical", "high", "medium", "low"]:
        if severity.get(level, 0) > 0:
            emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️"}[level]
            print(f"   {emoji} {level}: {severity[level]}")

    print("\n📊 MEMORY BENEFIT:")
    benefit = result["memory_benefit"]
    print(f"   {benefit['value_statement']}")

    # -------------------------------------------------------------------------
    # STEP 5: Show how to record a new decision
    # -------------------------------------------------------------------------
    print("\n" + "-" * 60)
    print("BONUS: Recording a New Team Decision")
    print("-" * 60)

    if result["findings"]:
        finding = result["findings"][0]
        print(f"\nTo suppress '{finding['type']}' in future scans:")
        print(
            """
    await wizard.record_decision(
        finding=result['findings'][0],
        decision="false_positive",
        reason="Explain why this is safe",
        decided_by="@your_name",
        applies_to="pattern"  # or "all" for all of this type
    )
""",
        )

    print("=" * 60)
    print("Without persistent memory, you review the same false positives every scan.")
    print("With Empathy Framework, your AI learns your team's security policies.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


# =============================================================================
# EXPECTED OUTPUT:
# =============================================================================
#
# Loading team security decisions from past reviews...
#   ✓ Loaded 3 team decisions
#
# Scanning for security vulnerabilities...
# (with team decisions applied)
#
# ============================================================
# RESULTS: Security Scan with Learning
# ============================================================
#
# 📊 SCAN SUMMARY:
#    Raw Findings: 5
#    After Learning: 2
#
# 🧠 LEARNING APPLIED:
#    Suppressed: 3 findings
#    Noise Reduction: 60.0%
#    Team Decisions Used: 3
#
#    Suppression Details:
#    • sql_injection
#      Decision: false_positive by @sarah
#      Reason: "Using SQLAlchemy ORM which handles SQL escaping"
#    • insecure_random
#      Decision: accepted by @mike
#      Reason: "Only used for UI animations, not security"
#    • xss
#      Decision: false_positive by @tech_lead
#      Reason: "React's JSX auto-escapes, dangerouslySetInnerHTML not used"
#
# ⚠️  REMAINING FINDINGS (require attention):
#    🚨 critical: 2
#
# 📊 MEMORY BENEFIT:
#    Persistent memory applied 3 team decisions, suppressing 3 warnings.
#
# ============================================================
# Without persistent memory, you review the same false positives every scan.
# With Empathy Framework, your AI learns your team's security policies.
# ============================================================
