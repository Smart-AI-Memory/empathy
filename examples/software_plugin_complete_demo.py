"""
Software Development Plugin - Complete Integration Demo

Shows all wizards working together on a realistic project analysis.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import asyncio
import json
import os
import tempfile

# Simulated project with multiple issues
PROJECT_CODE_SAMPLES = {
    "api.py": """
def get_user(user_id):
    # Missing tests, SQL injection, no error handling
    import sqlite3
    conn = sqlite3.connect('db.sqlite')
    query = f"SELECT * FROM users WHERE id={user_id}"  # SQL Injection!
    return conn.execute(query).fetchone()

def process_request():
    # Performance issue - will be hot path
    import time
    for i in range(1000):
        get_user(i)  # N+1 query pattern!
    return "done"
""",
    "auth.py": """
# Hardcoded credentials
API_KEY = "sk_live_abc123"  # SECURITY ISSUE!

def authenticate(username, password):
    # No tests, vulnerable
    import hashlib
    # Weak crypto
    hash = hashlib.md5(password.encode()).hexdigest()
    return hash == "5f4dcc3b5aa765d61d8327deb882cf99"
""",
    "test_api.py": """
def test_something():
    # Test with no assertions - poor quality!
    result = get_user(1)
""",
}


async def run_complete_analysis():
    """Run complete project analysis with all wizards"""

    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 8 + "SOFTWARE DEVELOPMENT PLUGIN - COMPLETE ANALYSIS" + " " * 13 + "║")
    print("║" + " " * 19 + "All Wizards Working Together" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")

    print("\n" + "=" * 70)
    print("SIMULATED PROJECT ANALYSIS")
    print("=" * 70)

    # Create temporary project
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write code files
        for filename, code in PROJECT_CODE_SAMPLES.items():
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, "w") as f:
                f.write(code)

        print("\n📁 Project Structure:")
        print(f"  {tmpdir}/")
        for filename in PROJECT_CODE_SAMPLES.keys():
            print(f"    - {filename}")

        # Phase 1: Testing Analysis
        print("\n" + "=" * 70)
        print("PHASE 1: TESTING ANALYSIS")
        print("=" * 70)

        from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard

        testing_wizard = EnhancedTestingWizard()

        testing_result = await testing_wizard.analyze(
            {
                "project_path": tmpdir,
                "coverage_report": {},  # No coverage
                "test_files": [os.path.join(tmpdir, "test_api.py")],
                "source_files": [os.path.join(tmpdir, "api.py"), os.path.join(tmpdir, "auth.py")],
            }
        )

        print("\n📊 Test Analysis:")
        print(f"  Coverage: {testing_result['coverage']['overall_coverage']:.1f}%")
        print(f"  Test Quality Score: {testing_result['test_quality']['quality_score']:.1f}/100")
        print(f"  High-Risk Gaps: {len(testing_result['risk_gaps'])}")

        if testing_result["risk_gaps"]:
            print("\n  Top Risk Gaps:")
            for gap in testing_result["risk_gaps"][:3]:
                print(f"    [{gap['risk_level']}] {gap['pattern']}: {gap['reason']}")

        # Phase 2: Security Analysis
        print("\n" + "=" * 70)
        print("PHASE 2: SECURITY ANALYSIS")
        print("=" * 70)

        from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

        security_wizard = SecurityAnalysisWizard()

        security_result = await security_wizard.analyze(
            {
                "source_files": [os.path.join(tmpdir, "api.py"), os.path.join(tmpdir, "auth.py")],
                "endpoint_config": {os.path.join(tmpdir, "api.py"): {"endpoint_public": True}},
            }
        )

        print("\n🔒 Security Analysis:")
        print(f"  Vulnerabilities Found: {security_result['vulnerabilities_found']}")
        by_sev = security_result["by_severity"]
        print(
            f"  Critical: {by_sev['CRITICAL']}, High: {by_sev['HIGH']}, Medium: {by_sev['MEDIUM']}"
        )

        if security_result["exploitability_assessments"]:
            print("\n  Top Exploitable Vulnerabilities:")
            for assessment in security_result["exploitability_assessments"][:3]:
                vuln = assessment["vulnerability"]
                print(f"    [{assessment['exploitability']}] {vuln['name']}")
                print(f"        Likelihood: {assessment['exploit_likelihood']:.0%}")
                print(f"        {assessment['mitigation_urgency']}")

        # Phase 3: Performance Analysis
        print("\n" + "=" * 70)
        print("PHASE 3: PERFORMANCE ANALYSIS")
        print("=" * 70)

        from empathy_software_plugin.wizards.performance_profiling_wizard import (
            PerformanceProfilingWizard,
        )

        # Mock profiling data based on our code
        mock_profile = json.dumps(
            {
                "functions": [
                    {
                        "name": "process_request",
                        "file": "api.py",
                        "line": 9,
                        "total_time": 5.2,
                        "self_time": 0.1,
                        "calls": 10,
                        "cumulative_time": 5.2,
                        "percent": 52.0,
                    },
                    {
                        "name": "get_user",
                        "file": "api.py",
                        "line": 1,
                        "total_time": 4.8,
                        "self_time": 0.05,
                        "calls": 10000,  # N+1!
                        "cumulative_time": 4.8,
                        "percent": 48.0,
                    },
                ]
            }
        )

        performance_wizard = PerformanceProfilingWizard()

        performance_result = await performance_wizard.analyze(
            {"profiler_data": mock_profile, "profiler_type": "simple_json"}
        )

        print("\n⚡ Performance Analysis:")
        summary = performance_result["profiling_summary"]
        print(f"  Total Functions Profiled: {summary['total_functions']}")
        print(f"  Bottlenecks Found: {len(performance_result['bottlenecks'])}")

        if performance_result["bottlenecks"]:
            print("\n  Critical Bottlenecks:")
            for bottleneck in performance_result["bottlenecks"][:3]:
                print(f"    [{bottleneck['severity']}] {bottleneck['type']}")
                print(f"        {bottleneck['function_name']}: {bottleneck['time_cost']:.2f}s")
                print(f"        {bottleneck['fix_suggestion']}")

        # Phase 4: Integrated Risk Assessment
        print("\n" + "=" * 70)
        print("PHASE 4: INTEGRATED RISK ASSESSMENT")
        print("=" * 70)

        # Combine predictions from all wizards
        all_predictions = (
            testing_result.get("predictions", [])
            + security_result.get("predictions", [])
            + performance_result.get("predictions", [])
        )

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_predictions.sort(key=lambda p: severity_order.get(p.get("severity", "low"), 4))

        print("\n🎯 COMBINED RISK ASSESSMENT:")
        print(f"\n  Total Predictions: {len(all_predictions)}")

        print("\n  Top Priority Issues:")
        for i, pred in enumerate(all_predictions[:5], 1):
            print(
                f"\n  {i}. [{pred.get('severity', 'unknown').upper()}] {pred.get('type', 'unknown')}"
            )
            print(f"     {pred.get('description', 'No description')[:100]}...")

        # Phase 5: Actionable Roadmap
        print("\n" + "=" * 70)
        print("PHASE 5: ACTIONABLE DEVELOPMENT ROADMAP")
        print("=" * 70)

        print("\n📋 IMMEDIATE ACTIONS (Before Next Deploy):")

        critical_count = 0

        # Critical security issues
        critical_security = sum(
            1 for p in security_result.get("predictions", []) if p.get("severity") == "critical"
        )
        if critical_security > 0:
            critical_count += critical_security
            print(f"  🔒 Fix {critical_security} CRITICAL security vulnerabilities")
            print("     (SQL injection, hardcoded credentials)")

        # Critical testing gaps
        critical_test_gaps = [
            g for g in testing_result.get("risk_gaps", []) if g.get("risk_level") == "CRITICAL"
        ]
        if critical_test_gaps:
            critical_count += len(critical_test_gaps)
            print(f"  🧪 Add tests for {len(critical_test_gaps)} critical code paths")
            print("     (Authentication, user input validation)")

        # Critical performance issues
        critical_perf = [
            b for b in performance_result.get("bottlenecks", []) if b.get("severity") == "CRITICAL"
        ]
        if critical_perf:
            critical_count += len(critical_perf)
            print(f"  ⚡ Fix {len(critical_perf)} critical performance bottlenecks")
            print("     (N+1 queries, hot paths)")

        print("\n📅 SPRINT PRIORITIES (Next 1-2 Weeks):")
        print("  • Implement parameterized queries")
        print("  • Add comprehensive test suite for auth module")
        print("  • Optimize database query patterns")
        print("  • Add input validation library")
        print("  • Set up pre-commit security scanning")

        print("\n🎯 SUCCESS METRICS:")
        print("  • Security: 0 CRITICAL vulnerabilities")
        print("  • Testing: >70% coverage with quality score >60")
        print("  • Performance: Response time <500ms")

        # Final Summary
        print("\n" + "=" * 70)
        print("ANALYSIS SUMMARY")
        print("=" * 70)

        print("\n📊 Overall Project Health:")
        print(f"  🔒 Security: {critical_security} CRITICAL issues")
        print(f"  🧪 Testing: {testing_result['coverage']['overall_coverage']:.0f}% coverage")
        print(f"  ⚡ Performance: {len(performance_result['bottlenecks'])} bottlenecks")

        print("\n⚠️  Risk Level: HIGH")
        print(f"  {critical_count} critical issues must be addressed before production")

        print("\n💡 In Our Experience:")
        print("  Projects with untested authentication code and SQL injection")
        print("  vulnerabilities experience security incidents within 30 days")
        print("  of deployment. Fix critical issues immediately.")

        print("\n" + "=" * 70)


async def main():
    """Run complete integration demo"""
    await run_complete_analysis()

    print("\n" + "=" * 70)
    print("INTEGRATION DEMO COMPLETE")
    print("=" * 70)
    print("\n✅ Demonstrated:")
    print("  • Enhanced Testing Wizard - Quality analysis")
    print("  • Security Analysis Wizard - Exploit prediction")
    print("  • Performance Profiling Wizard - Bottleneck detection")
    print("  • Integrated risk assessment across all domains")
    print("  • Actionable development roadmap")
    print("\n🎯 Value Proposition:")
    print("  Instead of separate tools giving you disconnected data,")
    print("  the Software Development Plugin provides INTEGRATED analysis")
    print("  with prioritized actions based on REAL risk.")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
