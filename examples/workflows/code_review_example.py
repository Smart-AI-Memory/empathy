#!/usr/bin/env python3
"""Code Review Workflow Example

Demonstrates tiered code analysis using the 3-tier model system:
1. Haiku (cheap): Classify change type (bug fix, feature, refactor)
2. Sonnet (capable): Security scan and bug pattern matching
3. Opus (premium): Architectural review (conditional on complexity)

The premium stage only runs for:
- Changes affecting 10+ files
- Core module modifications
- Explicitly flagged critical changes

Run:
    python examples/workflows/code_review_example.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio

from empathy_os.workflows import CodeReviewWorkflow


async def review_simple_change():
    """Review a simple 2-file change (no architectural review)."""
    print("\n" + "-" * 50)
    print("  SCENARIO 1: Simple Bug Fix (2 files)")
    print("-" * 50 + "\n")

    workflow = CodeReviewWorkflow(file_threshold=10, core_modules=["src/core/", "src/security/"])

    diff = """
--- a/src/utils.py
+++ b/src/utils.py
@@ -15,7 +15,8 @@ def process_data(data):
     if not data:
         return None
-    result = data.get('value')
+    # Fix: Added null check for nested value
+    result = data.get('value') if data else None
     return result
"""

    result = await workflow.execute(
        diff=diff,
        files_changed=["src/utils.py", "tests/test_utils.py"],
        is_core_module=False,
    )

    _print_result(result, "Simple Bug Fix")


async def review_large_change():
    """Review a large change affecting many files (triggers architectural review)."""
    print("\n" + "-" * 50)
    print("  SCENARIO 2: Large Feature (15 files)")
    print("-" * 50 + "\n")

    workflow = CodeReviewWorkflow(file_threshold=10)

    # Large change with 15 files
    files = [
        "src/api/routes.py",
        "src/api/handlers.py",
        "src/api/middleware.py",
        "src/models/user.py",
        "src/models/session.py",
        "src/services/auth.py",
        "src/services/token.py",
        "src/utils/crypto.py",
        "src/utils/validators.py",
        "src/config/settings.py",
        "tests/test_auth.py",
        "tests/test_token.py",
        "tests/test_routes.py",
        "tests/test_handlers.py",
        "docs/auth.md",
    ]

    diff = """
--- /dev/null
+++ b/src/services/auth.py
@@ -0,0 +1,50 @@
+# New authentication service
+import hashlib
+
+def authenticate(username, password):
+    # TODO: Add rate limiting
+    hashed = hashlib.sha256(password.encode()).hexdigest()
+    return verify_credentials(username, hashed)
"""

    result = await workflow.execute(diff=diff, files_changed=files, is_core_module=False)

    _print_result(result, "Large Feature")


async def review_core_change():
    """Review a change to core modules (always triggers architectural review)."""
    print("\n" + "-" * 50)
    print("  SCENARIO 3: Core Module Change")
    print("-" * 50 + "\n")

    workflow = CodeReviewWorkflow(file_threshold=10, core_modules=["src/core/", "src/security/"])

    diff = """
--- a/src/security/auth.py
+++ b/src/security/auth.py
@@ -20,6 +20,10 @@ class AuthManager:
     def verify_token(self, token):
+        # Added api_key check
+        if token.startswith('api_key_'):
+            return self.verify_api_key(token)
         return jwt.decode(token, self.secret)
"""

    result = await workflow.execute(
        diff=diff,
        files_changed=["src/security/auth.py"],
        is_core_module=True,  # Explicitly marked as core
    )

    _print_result(result, "Core Security Change")


def _print_result(result, scenario_name):
    """Print workflow results."""
    if result.success:
        print(f"✓ Review completed: {scenario_name}\n")

        # Stage summary
        print("Stages:")
        for stage in result.stages:
            if stage.skipped:
                print(f"  {stage.name:20} [SKIPPED] - {stage.skip_reason}")
            else:
                print(f"  {stage.name:20} [{stage.tier.value:8}] ${stage.cost:.6f}")
        print()

        # Security findings
        output = result.final_output or {}
        security = output.get("security_findings", [])
        if security:
            print("⚠ Security Findings:")
            for finding in security:
                print(f"  [{finding['severity']}] {finding['message']}")
            print()

        # Recommendations
        recommendations = output.get("recommendations", [])
        if recommendations:
            print("Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
            print()

        # Assessment
        assessment = output.get("assessment", {})
        if assessment:
            print(f"Verdict: {assessment.get('verdict', 'N/A').upper()}")
            print(f"Confidence: {assessment.get('confidence', 0):.0%}")
            print()

        # Cost summary
        report = result.cost_report
        print(f"Cost: ${report.total_cost:.6f} (saved {report.savings_percent:.1f}%)")

    else:
        print(f"✗ Review failed: {result.error}")


async def main():
    """Run all code review scenarios."""
    print("\n" + "=" * 60)
    print("  CODE REVIEW WORKFLOW DEMO")
    print("=" * 60)

    # Run different scenarios
    await review_simple_change()
    await review_large_change()
    await review_core_change()

    print("\n" + "=" * 60)
    print("  Demo complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
