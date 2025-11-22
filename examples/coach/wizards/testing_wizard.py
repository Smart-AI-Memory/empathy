"""
Testing Wizard

Suggests test plans, adds missing test cases, measures coverage and quality.
Uses Empathy Framework Level 3 (Proactive) to identify untested paths
and Level 4 (Anticipatory) to prevent future test gaps.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from typing import Any

from .base_wizard import (
    BaseWizard,
    EmpathyChecks,
    WizardArtifact,
    WizardHandoff,
    WizardOutput,
    WizardRisk,
    WizardTask,
)


class TestingWizard(BaseWizard):  # noqa: pytest - Not a test class
    """
    Wizard for test planning and quality assurance

    Uses:
    - Level 2: Guide test writing with clear examples
    - Level 3: Proactively identify missing test cases
    - Level 4: Anticipate testing gaps and prevent regressions
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a testing task"""
        test_keywords = [
            "test",
            "testing",
            "coverage",
            "quality",
            "qa",
            "unit test",
            "integration",
            "e2e",
            "end-to-end",
            "regression",
            "test plan",
            "test case",
        ]

        task_lower = (task.task + " " + task.context).lower()
        matches = sum(1 for keyword in test_keywords if keyword in task_lower)

        return min(matches / 2.0, 1.0)  # 2+ keywords = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute testing workflow"""

        # Step 1: Assess context
        self._extract_constraints(task)
        self._assess_emotional_state(task)

        # Step 2: Analyze testing needs
        test_analysis = self._analyze_testing_needs(task)

        # Step 3: Identify missing tests (Level 3: Proactive)
        missing_tests = self._identify_missing_tests(task, test_analysis)

        # Step 4: Generate test plan
        test_plan = self._generate_test_plan(task, test_analysis, missing_tests)

        # Step 5: Create test examples
        test_examples = self._generate_test_examples(task, missing_tests)

        # Step 6: Assess risks
        risks = self._assess_testing_risks(task, test_analysis)

        # Step 7: Generate diagnosis
        diagnosis = self._create_diagnosis(test_analysis, missing_tests)

        # Step 8: Create artifacts
        artifacts = [
            WizardArtifact(type="doc", title="Test Plan", content=test_plan),
            WizardArtifact(type="code", title="Test Examples", content=test_examples),
            WizardArtifact(
                type="checklist",
                title="Testing Checklist",
                content=self._create_testing_checklist(test_analysis),
            ),
            WizardArtifact(
                type="doc",
                title="Coverage Analysis",
                content=self._generate_coverage_report(test_analysis, missing_tests),
            ),
        ]

        # Step 9: Create plan
        plan = [
            "Analyze current test coverage",
            f"Identify {len(missing_tests)} missing test scenarios",
            "Write unit tests for critical paths",
            "Add integration tests for key flows",
            "Set up CI/CD test automation",
            "Establish coverage thresholds",
        ]

        # Step 10: Generate next actions
        next_actions = [
            "Set up test framework if not present",
            "Write tests for identified gaps",
            "Configure coverage reporting",
            "Add tests to CI/CD pipeline",
            "Set minimum coverage threshold (e.g., 80%)",
        ]

        # Add anticipatory actions
        anticipatory_actions = self._generate_anticipatory_actions(task)
        next_actions.extend(anticipatory_actions)

        # Step 11: Create handoffs
        handoffs = []
        if test_analysis["coverage_status"] == "low":
            handoffs.append(
                WizardHandoff(
                    owner="team",
                    what="Code review for testability improvements",
                    when="Before adding tests",
                )
            )

        # Step 12: Empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role} testing needs with {test_analysis['test_types']} focus",
            emotional=f"Acknowledged {'testing fatigue' if 'low' in test_analysis.get('coverage_status', '') else 'quality concerns'}",
            anticipatory=f"Identified {len(missing_tests)} proactive test scenarios to prevent future issues",
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=plan,
            artifacts=artifacts,
            risks=risks,
            handoffs=handoffs,
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _analyze_testing_needs(self, task: WizardTask) -> dict[str, Any]:
        """Analyze what types of tests are needed"""
        context_lower = task.context.lower() + " " + task.task.lower()

        test_types = []
        if "unit" in context_lower or "test" in task.task.lower():
            test_types.append("unit")
        if "integration" in context_lower or "api" in context_lower:
            test_types.append("integration")
        if "e2e" in context_lower or "end-to-end" in context_lower or "ui" in context_lower:
            test_types.append("e2e")
        if "performance" in context_lower or "load" in context_lower:
            test_types.append("performance")
        if "security" in context_lower:
            test_types.append("security")

        if not test_types:
            test_types = ["unit", "integration"]  # Default

        # Estimate coverage
        coverage_status = "unknown"
        if "low" in context_lower or "missing" in context_lower or "no test" in context_lower:
            coverage_status = "low"
        elif "coverage" in context_lower:
            coverage_status = "needs_improvement"

        return {
            "test_types": ", ".join(test_types),
            "coverage_status": coverage_status,
            "focus_areas": self._identify_focus_areas(context_lower),
        }

    def _identify_focus_areas(self, context_lower: str) -> list[str]:
        """Identify areas needing test focus"""
        areas = []

        area_keywords = {
            "authentication": ["auth", "login", "password"],
            "authorization": ["permission", "role", "access"],
            "data_validation": ["validation", "input", "sanitize"],
            "error_handling": ["error", "exception", "failure"],
            "edge_cases": ["edge", "boundary", "limit"],
            "business_logic": ["business", "logic", "rule"],
            "api_endpoints": ["api", "endpoint", "route"],
            "database": ["database", "db", "query", "sql"],
        }

        for area, keywords in area_keywords.items():
            if any(kw in context_lower for kw in keywords):
                areas.append(area)

        return areas[:5]  # Top 5

    def _identify_missing_tests(self, task: WizardTask, analysis: dict) -> list[dict[str, str]]:
        """Identify missing test scenarios (Level 3: Proactive)"""
        missing = []

        focus_areas = analysis["focus_areas"]

        # Generate test scenarios based on focus areas
        if "authentication" in focus_areas:
            missing.append(
                {"scenario": "Valid credentials login", "type": "unit", "priority": "high"}
            )
            missing.append(
                {"scenario": "Invalid credentials login", "type": "unit", "priority": "high"}
            )
            missing.append(
                {
                    "scenario": "Account lockout after failed attempts",
                    "type": "integration",
                    "priority": "medium",
                }
            )

        if "authorization" in focus_areas:
            missing.append(
                {
                    "scenario": "User with correct permissions can access resource",
                    "type": "integration",
                    "priority": "high",
                }
            )
            missing.append(
                {
                    "scenario": "User without permissions gets 403",
                    "type": "integration",
                    "priority": "high",
                }
            )

        if "data_validation" in focus_areas:
            missing.append({"scenario": "Valid input accepted", "type": "unit", "priority": "high"})
            missing.append(
                {
                    "scenario": "Invalid input rejected with clear error",
                    "type": "unit",
                    "priority": "high",
                }
            )
            missing.append(
                {
                    "scenario": "SQL injection attempts blocked",
                    "type": "security",
                    "priority": "high",
                }
            )

        if "error_handling" in focus_areas:
            missing.append(
                {
                    "scenario": "Graceful handling of network failures",
                    "type": "integration",
                    "priority": "medium",
                }
            )
            missing.append(
                {
                    "scenario": "Proper error messages for user",
                    "type": "integration",
                    "priority": "medium",
                }
            )

        if "edge_cases" in focus_areas:
            missing.append(
                {"scenario": "Empty input handling", "type": "unit", "priority": "medium"}
            )
            missing.append(
                {"scenario": "Maximum input size handling", "type": "unit", "priority": "medium"}
            )

        # Generic missing tests
        if not missing:
            missing = [
                {"scenario": "Happy path test", "type": "unit", "priority": "high"},
                {"scenario": "Error case handling", "type": "unit", "priority": "high"},
                {"scenario": "Edge case validation", "type": "unit", "priority": "medium"},
            ]

        return missing[:10]  # Top 10 missing tests

    def _generate_test_plan(self, task: WizardTask, analysis: dict, missing: list[dict]) -> str:
        """Generate comprehensive test plan"""
        return f"""# Test Plan

## Objectives
- Achieve comprehensive test coverage
- Prevent regressions
- Ensure code quality

## Test Types
{analysis['test_types']}

## Current Status
Coverage: {analysis['coverage_status']}
Focus Areas: {', '.join(analysis['focus_areas'])}

## Test Scenarios

### High Priority ({len([t for t in missing if t['priority'] == 'high'])} tests)
{chr(10).join(f"- {t['scenario']} ({t['type']} test)" for t in missing if t['priority'] == 'high')}

### Medium Priority ({len([t for t in missing if t['priority'] == 'medium'])} tests)
{chr(10).join(f"- {t['scenario']} ({t['type']} test)" for t in missing if t['priority'] == 'medium')}

## Test Environment
- Development: Local test runner
- CI/CD: Automated on every PR
- Staging: Integration and E2E tests
- Production: Smoke tests post-deployment

## Coverage Goals
- Unit tests: 80%+ coverage
- Integration tests: Key user flows
- E2E tests: Critical business paths

## Timeline
- Week 1: Write high-priority unit tests
- Week 2: Add integration tests
- Week 3: Set up CI/CD automation
- Week 4: Achieve coverage goals

## Success Criteria
- [ ] All high-priority tests passing
- [ ] 80%+ code coverage
- [ ] CI/CD pipeline green
- [ ] No critical paths untested
"""

    def _generate_test_examples(self, task: WizardTask, missing: list[dict]) -> str:
        """Generate example test code"""
        if not missing:
            return "# No specific test examples generated"

        first_test = missing[0]

        return f"""# Test Examples

## Example 1: {first_test['scenario']}

```python
def test_{first_test['scenario'].lower().replace(' ', '_')}():
    \"\"\"Test: {first_test['scenario']}\"\"\"
    # Arrange: Set up test data and dependencies
    test_user = {{
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }}

    # Act: Execute the code under test
    result = create_user(test_user)

    # Assert: Verify expected behavior
    assert result is not None
    assert result["email"] == test_user["email"]
    assert result["name"] == test_user["name"]
    assert "id" in result  # User should have an ID assigned
    assert "password" not in result  # Password should not be in response
```

## Example 2: Error Handling

```python
def test_handles_invalid_input():
    \"\"\"Test: System handles invalid input gracefully\"\"\"
    # Arrange
    invalid_input = None

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        process_input(invalid_input)

    assert "Invalid input" in str(exc_info.value)
```

## Example 3: Integration Test

```python
@pytest.mark.integration
def test_end_to_end_user_flow():
    \"\"\"Test: Complete user flow from start to finish\"\"\"
    # Arrange
    client = TestClient(app)

    # Act
    response = client.post("/api/action", json={{"key": "value"}})

    # Assert
    assert response.status_code == 200
    assert response.json()["success"] is True
```

## Example 4: Mock External Dependencies

```python
@patch('module.external_service')
def test_with_mocked_dependency(mock_service):
    \"\"\"Test: Function works with mocked external service\"\"\"
    # Arrange
    mock_service.return_value = {{"data": "mocked"}}

    # Act
    result = function_using_service()

    # Assert
    assert result["data"] == "mocked"
    mock_service.assert_called_once()
```

## Test Fixtures

```python
@pytest.fixture
def sample_data():
    \"\"\"Provide sample data for tests\"\"\"
    return {{
        "id": 1,
        "name": "Test",
        "value": 42
    }}

@pytest.fixture
def db_session():
    \"\"\"Provide test database session\"\"\"
    # Set up test database
    session = create_test_session()
    yield session
    # Teardown
    session.close()
```
"""

    def _assess_testing_risks(self, task: WizardTask, analysis: dict) -> list[WizardRisk]:
        """Assess testing risks"""
        risks = []

        if analysis["coverage_status"] == "low":
            risks.append(
                WizardRisk(
                    risk="Low test coverage leaves bugs undetected",
                    mitigation="Prioritize tests for critical paths, gradually increase coverage",
                    severity="high",
                )
            )

        risks.append(
            WizardRisk(
                risk="Flaky tests reduce CI/CD reliability",
                mitigation="Use stable test data, avoid time-dependent tests, retry failed tests",
                severity="medium",
            )
        )

        risks.append(
            WizardRisk(
                risk="Slow test suite impacts developer productivity",
                mitigation="Parallelize tests, use test doubles for external services, optimize database tests",
                severity="medium",
            )
        )

        risks.append(
            WizardRisk(
                risk="Tests become maintenance burden",
                mitigation="Follow DRY principles, use fixtures, refactor tests regularly",
                severity="low",
            )
        )

        return risks

    def _create_diagnosis(self, analysis: dict, missing: list[dict]) -> str:
        """Create diagnosis"""
        return f"{analysis['test_types']} testing needed with {analysis['coverage_status']} coverage; {len(missing)} critical test scenarios identified"

    def _create_testing_checklist(self, analysis: dict) -> str:
        """Create testing checklist"""
        return f"""# Testing Checklist

## Test Framework Setup
- [ ] Test framework installed (pytest, jest, etc.)
- [ ] Test configuration file created
- [ ] Test directory structure set up
- [ ] CI/CD integration configured

## Test Coverage
- [ ] Unit tests for all public functions
- [ ] Integration tests for key workflows
- [ ] E2E tests for critical user paths
- [ ] Edge cases covered
- [ ] Error handling tested

## Test Quality
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Test names clearly describe what they test
- [ ] Tests are independent and can run in any order
- [ ] No hard-coded values (use fixtures/constants)
- [ ] External dependencies mocked

## Specific Areas ({', '.join(analysis['focus_areas'])})
{chr(10).join(f"- [ ] {area.replace('_', ' ').title()} tested" for area in analysis['focus_areas'])}

## CI/CD
- [ ] Tests run on every commit
- [ ] Coverage reports generated
- [ ] Minimum coverage threshold enforced
- [ ] Test results visible in PRs

## Documentation
- [ ] Testing guide in README
- [ ] Test fixtures documented
- [ ] Mock setup explained
- [ ] How to run tests locally

---
*Last Updated*: [Date]
"""

    def _generate_coverage_report(self, analysis: dict, missing: list[dict]) -> str:
        """Generate coverage analysis"""
        return f"""# Coverage Analysis

## Current Status
Coverage Level: {analysis['coverage_status']}

## Identified Gaps
Total Missing Test Scenarios: {len(missing)}

### By Priority
- High: {len([t for t in missing if t['priority'] == 'high'])}
- Medium: {len([t for t in missing if t['priority'] == 'medium'])}
- Low: {len([t for t in missing if t.get('priority') == 'low'])}

### By Type
- Unit: {len([t for t in missing if t['type'] == 'unit'])}
- Integration: {len([t for t in missing if t['type'] == 'integration'])}
- E2E: {len([t for t in missing if t['type'] == 'e2e'])}
- Security: {len([t for t in missing if t['type'] == 'security'])}

## Recommendations
1. Start with high-priority unit tests
2. Add integration tests for critical flows
3. Set up automated coverage reporting
4. Aim for 80%+ coverage milestone
5. Review and update tests during code reviews

## Tools
- Coverage tool: pytest-cov / coverage.py
- CI/CD: GitHub Actions / GitLab CI
- Reporting: Codecov / Coveralls

---
*Analysis Date*: [Current Date]
"""
