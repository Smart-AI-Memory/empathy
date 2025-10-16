"""
Debugging Wizard

Analyzes bugs, forms hypotheses, proposes fixes, and creates regression tests.
Uses Empathy Framework Level 3 (Proactive) for pattern detection and Level 4
(Anticipatory) for preventing future issues.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import re
from typing import List, Dict, Any

from .base_wizard import (
    BaseWizard,
    WizardTask,
    WizardOutput,
    WizardArtifact,
    WizardRisk,
    WizardHandoff,
    EmpathyChecks,
)


class DebuggingWizard(BaseWizard):
    """
    Wizard for debugging issues and proposing fixes

    Uses:
    - Level 2: Guide user through reproduction steps
    - Level 3: Proactively detect error patterns
    - Level 4: Anticipate related issues and prevention strategies
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a debugging task"""
        debug_keywords = [
            "bug", "error", "fail", "crash", "500", "exception",
            "trace", "stack", "debug", "broken", "issue"
        ]

        task_lower = (task.task + " " + task.context).lower()
        matches = sum(1 for keyword in debug_keywords if keyword in task_lower)

        return min(matches / 3.0, 1.0)  # 3+ keywords = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute debugging workflow"""

        # Step 1: Assess emotional context (someone is likely stressed!)
        emotional_state = self._assess_emotional_state(task)

        # Step 2: Extract constraints
        constraints = self._extract_constraints(task)

        # Step 3: Analyze the error
        diagnosis = self._analyze_error(task)

        # Step 4: Form hypotheses (Level 3: Proactive pattern detection)
        hypotheses = self._form_hypotheses(task, diagnosis)

        # Step 5: Create reproduction plan
        repro_plan = self._create_repro_plan(task, hypotheses)

        # Step 6: Generate patch (Level 2: Guided)
        patch = self._generate_patch(task, hypotheses)

        # Step 7: Create regression test
        test = self._create_regression_test(task, hypotheses)

        # Step 8: Identify risks
        risks = self._identify_risks(task, hypotheses)

        # Step 9: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="Root Cause Analysis",
                content=diagnosis
            ),
            WizardArtifact(
                type="code",
                title="Proposed Patch",
                content=patch
            ),
            WizardArtifact(
                type="code",
                title="Regression Test",
                content=test
            ),
            WizardArtifact(
                type="checklist",
                title="Deployment Checklist",
                content=self._create_deployment_checklist(task)
            )
        ]

        # Step 10: Generate next actions
        next_actions = [
            "Reproduce issue in staging environment",
            "Apply patch and verify fix",
            "Run regression test suite",
            "Code review with senior dev",
            "Deploy to staging, monitor for 1 hour",
            "Deploy to production with rollback plan ready"
        ]

        # Add anticipatory actions
        anticipatory_actions = self._generate_anticipatory_actions(task)
        next_actions.extend(anticipatory_actions)

        # Step 11: Create handoffs
        handoffs = []
        if task.role == "developer":
            handoffs.append(WizardHandoff(
                owner="senior_dev",
                what="Code review of patch",
                when="Before deployment"
            ))
        if emotional_state["urgency"] == "high":
            handoffs.append(WizardHandoff(
                owner="pm",
                what="Timeline impact assessment",
                when="Within 1 hour"
            ))

        # Step 12: Empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role} constraints: {constraints['output_style'] if 'output_style' in constraints else 'standard'} output, {task.risk_tolerance} risk tolerance",
            emotional=f"Acknowledged {'high' if emotional_state['urgency'] == 'high' else 'normal'} pressure situation with {len(emotional_state['stress_indicators'])} stress indicators",
            anticipatory=f"Provided {len(anticipatory_actions)} proactive actions: regression test, rollback plan, deployment checklist"
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=repro_plan + ["Apply patch", "Run tests", "Deploy"],
            artifacts=artifacts,
            risks=risks,
            handoffs=handoffs,
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task)
        )

    def _analyze_error(self, task: WizardTask) -> str:
        """Analyze error from context"""
        context_lower = task.context.lower()

        # Common error patterns
        if "500" in context_lower or "internal server error" in context_lower:
            return "HTTP 500 Internal Server Error - likely backend exception or null pointer"

        if "null" in context_lower or "none" in context_lower:
            return "Null/None reference error - missing configuration or uninitialized variable"

        if "timeout" in context_lower:
            return "Timeout error - slow query, network issue, or deadlock"

        if "permission" in context_lower or "401" in context_lower or "403" in context_lower:
            return "Permission/authentication error - missing credentials or wrong scope"

        # Generic
        return "Error detected in logs - requires reproduction and detailed analysis"

    def _form_hypotheses(self, task: WizardTask, diagnosis: str) -> List[Dict[str, Any]]:
        """Form 2-3 hypotheses about root cause"""
        hypotheses = []

        if "null" in diagnosis.lower():
            hypotheses.append({
                "cause": "Missing configuration value on cold start",
                "likelihood": "high",
                "test": "Check config loading in startup sequence"
            })
            hypotheses.append({
                "cause": "Race condition in initialization",
                "likelihood": "medium",
                "test": "Add logging to init order"
            })

        elif "500" in diagnosis:
            hypotheses.append({
                "cause": "Unhandled exception in request handler",
                "likelihood": "high",
                "test": "Review recent code changes in handlers"
            })
            hypotheses.append({
                "cause": "Database connection failure",
                "likelihood": "medium",
                "test": "Check DB connection pool settings"
            })

        elif "timeout" in diagnosis.lower():
            hypotheses.append({
                "cause": "Slow database query (N+1 problem)",
                "likelihood": "high",
                "test": "Enable query logging and check for loops"
            })
            hypotheses.append({
                "cause": "Downstream service latency",
                "likelihood": "medium",
                "test": "Add timeout monitoring to external calls"
            })

        else:
            hypotheses.append({
                "cause": "Unknown - requires log analysis",
                "likelihood": "unknown",
                "test": "Reproduce with verbose logging"
            })

        return hypotheses[:3]  # Max 3 hypotheses

    def _create_repro_plan(self, task: WizardTask, hypotheses: List[Dict]) -> List[str]:
        """Create minimal reproduction plan"""
        plan = [
            "Set up staging environment with same config as production",
            f"Enable verbose logging for {self._extract_component(task)}",
        ]

        # Add hypothesis-specific steps
        for i, hyp in enumerate(hypotheses[:2], 1):
            plan.append(f"Test hypothesis {i}: {hyp['test']}")

        plan.append("Document reproduction steps and logs")

        return plan

    def _extract_component(self, task: WizardTask) -> str:
        """Extract component name from context"""
        # Simple heuristic: look for capitalized words or "Service X" pattern
        match = re.search(r'Service ([A-Z]\w*)|([A-Z]\w+Service)', task.context)
        if match:
            return match.group(1) or match.group(2)
        return "affected component"

    def _generate_patch(self, task: WizardTask, hypotheses: List[Dict]) -> str:
        """Generate proposed patch (simplified example)"""
        if hypotheses and "null" in hypotheses[0]["cause"].lower():
            return """# Proposed Patch: Add null guard and default config

```python
# Before:
def initialize():
    config_value = load_config('KEY')
    process(config_value)

# After:
def initialize():
    config_value = load_config('KEY')
    if config_value is None:
        config_value = get_default_config('KEY')
        logger.warning(f"Config KEY not found, using default: {config_value}")
    process(config_value)
```

Lines changed: ~5
Risk: Low - defensive coding pattern
"""

        return """# Proposed Patch: Add error handling

```python
# Add try-except block around suspected code
try:
    # ... existing code ...
except Exception as e:
    logger.error(f"Error in handler: {e}", exc_info=True)
    return {"error": "Internal error"}, 500
```

Lines changed: ~3-5
Risk: Low - improves error visibility
"""

    def _create_regression_test(self, task: WizardTask, hypotheses: List[Dict]) -> str:
        """Create regression test"""
        return """# Regression Test

```python
def test_handle_missing_config():
    \"\"\"Ensure system handles missing config gracefully\"\"\"
    # Arrange: Remove config value
    with mock.patch('load_config', return_value=None):
        # Act: Trigger code path
        result = initialize()

        # Assert: Should use default, not crash
        assert result is not None
        assert "default" in str(result).lower()

def test_error_response_format():
    \"\"\"Ensure errors return proper 500 response\"\"\"
    # Arrange: Force an error
    with mock.patch('process', side_effect=Exception("Test error")):
        # Act
        response, status = handler()

        # Assert
        assert status == 500
        assert "error" in response
```
"""

    def _create_deployment_checklist(self, task: WizardTask) -> str:
        """Create deployment checklist"""
        return """# Deployment Checklist

- [ ] Code review completed
- [ ] All tests passing (including new regression test)
- [ ] Staging deployment successful
- [ ] Monitoring shows no new errors (1 hour observation)
- [ ] Rollback plan documented and tested
- [ ] On-call engineer notified
- [ ] Production deployment scheduled
- [ ] Post-deployment monitoring (2 hours)
- [ ] Incident post-mortem scheduled (if critical)
"""

    def _identify_risks(self, task: WizardTask, hypotheses: List[Dict]) -> List[WizardRisk]:
        """Identify deployment risks"""
        risks = [
            WizardRisk(
                risk="Patch doesn't address root cause",
                mitigation="Test all hypotheses before deploying",
                severity="high" if task.risk_tolerance == "low" else "medium"
            ),
            WizardRisk(
                risk="Introduces new edge case",
                mitigation="Comprehensive regression testing + code review",
                severity="medium"
            )
        ]

        if task.risk_tolerance == "low":
            risks.append(WizardRisk(
                risk="Production deployment causes outage",
                mitigation="Deploy during low-traffic window with immediate rollback capability",
                severity="high"
            ))

        return risks
