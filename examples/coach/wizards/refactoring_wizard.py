"""Refactoring Wizard

Analyzes code quality, identifies technical debt, and orchestrates safe refactoring.
Uses Empathy Framework Level 3 (Proactive) for smell detection and Level 4
(Anticipatory) for predicting maintainability issues.

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


class RefactoringWizard(BaseWizard):
    """Wizard for code quality analysis and refactoring

    Uses:
    - Level 2: Guide user through refactoring decisions
    - Level 3: Proactively detect code smells
    - Level 4: Anticipate maintainability crisis before it happens
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a refactoring task"""
        # High-priority refactoring phrases (worth 2 points each)
        refactoring_phrases = [
            "refactor",
            "refactoring",
            "code quality",
            "technical debt",
            "clean code",
            "code smell",
            "maintainability",
        ]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "complexity",
            "duplicate",
            "duplication",
            "extract",
            "split",
            "simplify",
            "improve",
            "cleanup",
            "reorganize",
            "restructure",
        ]

        task_lower = (task.task + " " + task.context).lower()

        # Count high-priority matches (2 points each)
        primary_matches = sum(2 for phrase in refactoring_phrases if phrase in task_lower)

        # Count secondary matches (1 point each)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)  # 6+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute refactoring workflow"""
        # Step 1: Assess emotional context
        self._assess_emotional_state(task)

        # Step 2: Extract constraints
        self._extract_constraints(task)

        # Step 3: Analyze code quality
        diagnosis = self._analyze_code_quality(task)

        # Step 4: Detect code smells (Level 3: Proactive)
        smells = self._detect_code_smells(task)

        # Step 5: Assess complexity metrics
        complexity = self._assess_complexity(task)

        # Step 6: Create refactoring plan
        refactoring_plan = self._create_refactoring_plan(task, smells, complexity)

        # Step 7: Generate refactored code examples
        refactored_code = self._generate_refactored_code(task, smells)

        # Step 8: Predict maintainability issues (Level 4: Anticipatory)
        maintainability_forecast = self._predict_maintainability_issues(task, smells, complexity)

        # Step 9: Identify risks
        risks = self._identify_risks(task, refactoring_plan)

        # Step 10: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="Code Quality Report",
                content=self._generate_quality_report(diagnosis, smells, complexity),
            ),
            WizardArtifact(
                type="doc",
                title="Refactoring Plan",
                content="\n".join(refactoring_plan),
            ),
            WizardArtifact(type="code", title="Refactored Code Examples", content=refactored_code),
            WizardArtifact(
                type="doc",
                title="Maintainability Forecast",
                content=maintainability_forecast,
            ),
            WizardArtifact(
                type="checklist",
                title="Refactoring Safety Checklist",
                content=self._create_safety_checklist(task),
            ),
        ]

        # Step 11: Generate next actions
        next_actions = [
            "Run full test suite before starting refactoring",
            "Create feature branch for refactoring work",
            "Refactor in small, atomic commits (one smell at a time)",
            "Run tests after each refactoring step",
            "Request code review before merging",
        ] + self._generate_anticipatory_actions(task)

        # Step 12: Create empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role}'s constraints: test coverage, deployment risk, time pressure",
            emotional="Acknowledged: Refactoring can feel like 'non-productive' work, but prevents future crisis",
            anticipatory=f"Identified {len(smells)} issues that will become critical in 30-60 days without intervention",
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=refactoring_plan,
            artifacts=artifacts,
            risks=risks,
            handoffs=self._create_handoffs(task),
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _analyze_code_quality(self, task: WizardTask) -> str:
        """Analyze overall code quality"""
        analysis = "# Code Quality Analysis\n\n"
        analysis += f"**Scope**: {task.task}\n\n"

        # Infer quality issues from context
        task_lower = (task.task + " " + task.context).lower()

        quality_score = 100  # Start with perfect score

        if "long" in task_lower or "large" in task_lower or "400 lines" in task_lower:
            quality_score -= 20
            analysis += "⚠️ **Long method/class detected** (readability impact)\n"

        if "duplicate" in task_lower or "copy" in task_lower or "repeated" in task_lower:
            quality_score -= 25
            analysis += "⚠️ **Code duplication detected** (maintainability impact)\n"

        if "complex" in task_lower or "nested" in task_lower or "difficult" in task_lower:
            quality_score -= 20
            analysis += "⚠️ **High complexity detected** (testing/debugging impact)\n"

        if "god class" in task_lower or "too many" in task_lower:
            quality_score -= 25
            analysis += "⚠️ **God class / SRP violation** (single responsibility principle)\n"

        if "tight" in task_lower or "coupling" in task_lower:
            quality_score -= 15
            analysis += "⚠️ **Tight coupling detected** (flexibility impact)\n"

        analysis += f"\n**Quality Score**: {quality_score}/100\n"

        if quality_score >= 80:
            analysis += "✅ **Status**: Good quality, minor improvements recommended\n"
        elif quality_score >= 60:
            analysis += "⚠️ **Status**: Moderate issues, refactoring recommended soon\n"
        else:
            analysis += "🚨 **Status**: Critical issues, refactoring required to prevent crisis\n"

        return analysis

    def _detect_code_smells(self, task: WizardTask) -> list[dict[str, Any]]:
        """Detect code smells (Level 3: Proactive)"""
        smells = []
        task_lower = (task.task + " " + task.context).lower()

        # Long method/class
        if any(kw in task_lower for kw in ["long", "large", "400 lines", "500 lines"]):
            smells.append(
                {
                    "smell": "Long Method / God Class",
                    "severity": "high",
                    "description": "Method or class exceeds reasonable length (100+ lines for methods, 300+ for classes)",
                    "impact": "Difficult to understand, test, and maintain",
                    "refactorings": [
                        "Extract Method: Break into smaller, focused methods",
                        "Extract Class: Split responsibilities into separate classes",
                        "Replace Method with Method Object: For complex algorithms",
                    ],
                },
            )

        # Code duplication
        if any(kw in task_lower for kw in ["duplicate", "copy", "repeated", "similar"]):
            smells.append(
                {
                    "smell": "Duplicate Code",
                    "severity": "high",
                    "description": "Same or very similar code exists in multiple places",
                    "impact": "Bug fixes must be applied in multiple places, increasing error risk",
                    "refactorings": [
                        "Extract Method: Create shared method for duplicated logic",
                        "Pull Up Method: Move common code to parent class",
                        "Form Template Method: Extract common algorithm structure",
                    ],
                },
            )

        # High complexity
        if any(kw in task_lower for kw in ["complex", "nested", "cyclomatic", "cognitive"]):
            smells.append(
                {
                    "smell": "High Complexity",
                    "severity": "high",
                    "description": "Cyclomatic complexity > 10 or cognitive complexity > 15",
                    "impact": "Difficult to test all code paths, high bug risk",
                    "refactorings": [
                        "Decompose Conditional: Extract complex conditions into well-named methods",
                        "Replace Nested Conditional with Guard Clauses",
                        "Replace Conditional with Polymorphism: For type-based branching",
                    ],
                },
            )

        # God class / SRP violation
        if any(
            kw in task_lower
            for kw in ["god class", "too many", "does everything", "multiple responsibilities"]
        ):
            smells.append(
                {
                    "smell": "God Class / SRP Violation",
                    "severity": "critical",
                    "description": "Class has too many responsibilities (violates Single Responsibility Principle)",
                    "impact": "Changes to one feature break unrelated features, difficult to reuse",
                    "refactorings": [
                        "Extract Class: Split into multiple focused classes",
                        "Extract Subclass: Separate specialized behavior",
                        "Replace Data Value with Object: Extract complex data structures",
                    ],
                },
            )

        # Feature envy
        if any(kw in task_lower for kw in ["feature envy", "accessing", "calls methods"]):
            smells.append(
                {
                    "smell": "Feature Envy",
                    "severity": "medium",
                    "description": "Method uses data/methods from another class more than its own",
                    "impact": "Responsibilities misplaced, tight coupling",
                    "refactorings": [
                        "Move Method: Move to the class it's most interested in",
                        "Extract Method then Move Method: For partial feature envy",
                    ],
                },
            )

        # Primitive obsession
        if any(kw in task_lower for kw in ["primitive", "string", "dict", "tuple", "type hints"]):
            smells.append(
                {
                    "smell": "Primitive Obsession",
                    "severity": "medium",
                    "description": "Using primitives (strings, dicts) instead of domain objects",
                    "impact": "Validation scattered, lack of type safety",
                    "refactorings": [
                        "Replace Data Value with Object: Create domain objects",
                        "Introduce Parameter Object: For method parameter groups",
                        "Replace Type Code with Class: For status/type fields",
                    ],
                },
            )

        # If no specific smells detected, provide general analysis
        if not smells:
            smells.append(
                {
                    "smell": "General Code Improvement",
                    "severity": "low",
                    "description": "Code could benefit from standard refactoring practices",
                    "impact": "Minor maintainability impact",
                    "refactorings": [
                        "Rename Method/Variable: Improve clarity",
                        "Extract Method: Break down long methods",
                        "Add Type Hints: Improve IDE support and type safety",
                    ],
                },
            )

        return smells

    def _assess_complexity(self, task: WizardTask) -> dict[str, Any]:
        """Assess complexity metrics"""
        task_lower = (task.task + " " + task.context).lower()

        # Infer complexity from context
        cyclomatic = 5  # Default
        cognitive = 3
        nesting = 2

        if "nested" in task_lower or "complex" in task_lower:
            cyclomatic = 18  # High
            cognitive = 22
            nesting = 5

        return {
            "cyclomatic_complexity": cyclomatic,
            "cognitive_complexity": cognitive,
            "nesting_depth": nesting,
            "assessment": (
                "High complexity - refactoring recommended"
                if cyclomatic > 10
                else "Acceptable complexity"
            ),
        }

    def _create_refactoring_plan(
        self,
        task: WizardTask,
        smells: list[dict],
        complexity: dict,
    ) -> list[str]:
        """Create step-by-step refactoring plan"""
        plan = ["## Refactoring Plan (Risk-Ordered: Lowest Risk First)\n"]

        # Sort smells by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_smells = sorted(smells, key=lambda s: severity_order.get(s["severity"], 3))

        for i, smell in enumerate(sorted_smells, 1):
            plan.append(f"\n### Step {i}: Fix {smell['smell']} (Severity: {smell['severity']})")
            plan.append(f"**Issue**: {smell['description']}")
            plan.append(f"**Impact**: {smell['impact']}")
            plan.append("\n**Recommended Refactorings**:")
            for j, refactoring in enumerate(smell["refactorings"], 1):
                plan.append(f"  {chr(96 + j)}. {refactoring}")

            # Add safety steps
            plan.append("\n**Safety Steps**:")
            plan.append("  - Run tests before starting")
            plan.append("  - Make incremental changes (one refactoring at a time)")
            plan.append("  - Run tests after each change")
            plan.append("  - Commit immediately if tests pass")

        # Add validation step
        plan.append(f"\n### Step {len(sorted_smells) + 1}: Validation")
        plan.append("  - Run full test suite (unit + integration)")
        plan.append("  - Check code coverage hasn't decreased")
        plan.append("  - Run static analysis (linters, type checkers)")
        plan.append("  - Request peer code review")

        return plan

    def _generate_refactored_code(self, task: WizardTask, smells: list[dict]) -> str:
        """Generate refactored code examples"""
        code = "# Refactoring Examples\n\n"

        for smell in smells[:2]:  # Show top 2 smells
            code += f"## {smell['smell']}\n\n"

            if smell["smell"] == "Long Method / God Class":
                code += """# Before (Long Method):
def process_order(order_data):
    # Validate order (20 lines)
    if not order_data.get('user_id'):
        raise ValueError("Missing user_id")
    if not order_data.get('items'):
        raise ValueError("Missing items")
    # ... 15 more validation lines ...

    # Calculate totals (15 lines)
    subtotal = 0
    for item in order_data['items']:
        subtotal += item['price'] * item['quantity']
    tax = subtotal * 0.08
    total = subtotal + tax
    # ... 10 more calculation lines ...

    # Process payment (20 lines)
    # ... payment processing logic ...

    # Send notifications (15 lines)
    # ... notification logic ...

    return order

# After (Extract Method):
def process_order(order_data):
    validate_order(order_data)
    totals = calculate_order_totals(order_data)
    payment = process_payment(order_data, totals)
    send_order_notifications(order_data, payment)
    return create_order_record(order_data, totals, payment)

def validate_order(order_data):
    \"\"\"Validate order data (single responsibility)\"\"\"
    if not order_data.get('user_id'):
        raise ValueError("Missing user_id")
    if not order_data.get('items'):
        raise ValueError("Missing items")
    # ... validation logic ...

def calculate_order_totals(order_data):
    \"\"\"Calculate order totals (single responsibility)\"\"\"
    subtotal = sum(item['price'] * item['quantity'] for item in order_data['items'])
    tax = subtotal * 0.08
    return {'subtotal': subtotal, 'tax': tax, 'total': subtotal + tax}

# Benefits: Each method < 20 lines, single responsibility, testable in isolation

"""

            elif smell["smell"] == "Duplicate Code":
                code += """# Before (Duplicate Code):
def get_active_users():
    users = db.query("SELECT * FROM users")
    active_users = []
    for user in users:
        if user['status'] == 'active' and user['email_verified']:
            active_users.append(user)
    return active_users

def get_active_admins():
    users = db.query("SELECT * FROM users")
    active_admins = []
    for user in users:
        if user['status'] == 'active' and user['email_verified'] and user['role'] == 'admin':
            active_admins.append(user)
    return active_admins

# After (Extract Method):
def filter_active_verified_users(users, role=None):
    \"\"\"Shared filtering logic\"\"\"
    filtered = []
    for user in users:
        if user['status'] == 'active' and user['email_verified']:
            if role is None or user['role'] == role:
                filtered.append(user)
    return filtered

def get_active_users():
    users = db.query("SELECT * FROM users")
    return filter_active_verified_users(users)

def get_active_admins():
    users = db.query("SELECT * FROM users")
    return filter_active_verified_users(users, role='admin')

# Benefits: DRY principle, single source of truth, easier to maintain

"""

            elif smell["smell"] == "High Complexity":
                code += """# Before (High Complexity - Cyclomatic: 15):
def calculate_discount(user, order, promo_code):
    discount = 0
    if user['membership'] == 'gold':
        if order['total'] > 100:
            if promo_code and promo_code['type'] == 'percentage':
                discount = order['total'] * promo_code['value'] * 1.2  # Gold bonus
            elif promo_code and promo_code['type'] == 'fixed':
                discount = promo_code['value'] * 1.5  # Gold bonus
            else:
                discount = order['total'] * 0.15
        elif order['total'] > 50:
            discount = order['total'] * 0.10
    elif user['membership'] == 'silver':
        if order['total'] > 100:
            discount = order['total'] * 0.10
        elif order['total'] > 50:
            discount = order['total'] * 0.05
    # ... more nested conditions ...
    return discount

# After (Guard Clauses + Extract Method - Cyclomatic: 4):
def calculate_discount(user, order, promo_code):
    \"\"\"Calculate discount with guard clauses\"\"\"
    # Guard clauses for early exit
    if order['total'] < 50:
        return 0

    base_discount = get_membership_discount(user['membership'], order['total'])
    promo_discount = apply_promo_code(promo_code, order['total'], user['membership'])

    return max(base_discount, promo_discount)  # Best discount wins

def get_membership_discount(membership, total):
    \"\"\"Calculate base membership discount\"\"\"
    discount_rates = {
        'gold': {100: 0.15, 50: 0.10},
        'silver': {100: 0.10, 50: 0.05}
    }

    rates = discount_rates.get(membership, {})
    for threshold, rate in sorted(rates.items(), reverse=True):
        if total >= threshold:
            return total * rate
    return 0

def apply_promo_code(promo_code, total, membership):
    \"\"\"Apply promo code with membership bonuses\"\"\"
    if not promo_code:
        return 0

    bonus_multiplier = 1.2 if membership == 'gold' else 1.0

    if promo_code['type'] == 'percentage':
        return total * promo_code['value'] * bonus_multiplier
    elif promo_code['type'] == 'fixed':
        return promo_code['value'] * bonus_multiplier

    return 0

# Benefits: Reduced nesting (0 → 2 levels), lower complexity, easier to test

"""

        return code

    def _predict_maintainability_issues(
        self,
        task: WizardTask,
        smells: list[dict],
        complexity: dict,
    ) -> str:
        """Level 4: Predict future maintainability crisis"""
        forecast = "# Maintainability Forecast (Level 4: Anticipatory)\n\n"

        # Count critical issues
        critical_smells = [s for s in smells if s["severity"] in ["critical", "high"]]

        forecast += "## Current State\n"
        forecast += f"- Code smells detected: {len(smells)} ({len(critical_smells)} critical/high severity)\n"
        forecast += f"- Cyclomatic complexity: {complexity['cyclomatic_complexity']}\n"
        forecast += f"- Nesting depth: {complexity['nesting_depth']}\n\n"

        forecast += "## Projected Issues (Next 30-90 Days)\n\n"

        # Predict onboarding issues
        forecast += "### ⚠️ Developer Onboarding Slowdown (30 days)\n"
        forecast += "**Prediction**: New team members will struggle to understand codebase\n"
        forecast += "**Impact**: 2-3x longer ramp-up time (2 weeks → 6 weeks)\n"
        forecast += "**Cause**: High complexity + long methods make code difficult to follow\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Refactor god classes into focused modules NOW\n"
        forecast += "- Add architectural documentation (ADRs)\n"
        forecast += "- Extract complex algorithms into well-named methods\n\n"

        # Predict bug density increase
        forecast += "### ⚠️ Bug Density Increase (45 days)\n"
        forecast += "**Prediction**: Bug rate will increase 2-3x as code complexity compounds\n"
        forecast += "**Impact**: More time spent debugging, slower feature velocity\n"
        forecast += "**Cause**: Duplicate code + high complexity = difficult to test all paths\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Eliminate duplicate code to reduce surface area for bugs\n"
        forecast += "- Simplify complex methods (target: cyclomatic complexity < 10)\n"
        forecast += "- Add tests for complex code paths\n\n"

        # Predict feature velocity decline
        forecast += "### ⚠️ Feature Velocity Decline (60 days)\n"
        forecast += "**Prediction**: Time to add features will increase 50-100%\n"
        forecast += "**Impact**: Miss product deadlines, lose competitive advantage\n"
        forecast += "**Cause**: Technical debt makes every change risky and time-consuming\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Allocate 20% of sprint capacity to refactoring (like paying down debt)\n"
        forecast += "- Apply 'boy scout rule': Leave code better than you found it\n"
        forecast += "- Track code quality metrics in CI pipeline\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Now (Week 1-2)**: Fix critical smells (god classes, high duplication)\n"
        forecast += (
            "- **Week 3-4**: Simplify high-complexity methods (reduce cyclomatic complexity)\n"
        )
        forecast += "- **Week 5-6**: Add tests for newly refactored code\n"
        forecast += "- **Ongoing**: Establish 'no new code smells' policy in code reviews\n"

        return forecast

    def _generate_quality_report(self, diagnosis: str, smells: list[dict], complexity: dict) -> str:
        """Generate comprehensive quality report"""
        report = f"{diagnosis}\n\n"

        report += "## Detected Code Smells\n\n"
        for i, smell in enumerate(smells, 1):
            report += f"### {i}. {smell['smell']} (Severity: {smell['severity']})\n"
            report += f"**Description**: {smell['description']}\n"
            report += f"**Impact**: {smell['impact']}\n\n"

        report += "## Complexity Metrics\n\n"
        report += f"- **Cyclomatic Complexity**: {complexity['cyclomatic_complexity']} "
        report += "(Target: < 10, Acceptable: < 15)\n"
        report += f"- **Cognitive Complexity**: {complexity['cognitive_complexity']} "
        report += "(Target: < 15, Acceptable: < 25)\n"
        report += f"- **Nesting Depth**: {complexity['nesting_depth']} "
        report += "(Target: < 3, Acceptable: < 4)\n\n"
        report += f"**Assessment**: {complexity['assessment']}\n"

        return report

    def _create_safety_checklist(self, task: WizardTask) -> str:
        """Create refactoring safety checklist"""
        checklist = """# Refactoring Safety Checklist

## Before Starting
- [ ] Full test suite passes (unit + integration)
- [ ] Current test coverage documented (baseline)
- [ ] Create feature branch: `refactor/[description]`
- [ ] Backup important files (if no VCS)

## During Refactoring
- [ ] Make ONE change at a time (atomic refactorings)
- [ ] Run tests after EACH change
- [ ] Commit immediately if tests pass
- [ ] Use IDE automated refactorings when available (safer)
- [ ] Keep each commit small (< 200 lines changed)

## After Refactoring
- [ ] Full test suite passes
- [ ] Test coverage hasn't decreased
- [ ] Run static analysis (linters, type checkers)
- [ ] Performance hasn't degraded (benchmark if critical path)
- [ ] Code review by peer

## Deployment
- [ ] Deploy to staging first
- [ ] Run smoke tests in staging
- [ ] Monitor error rates after production deploy
- [ ] Have rollback plan ready

## Red Flags (STOP if you see these)
- ❌ Tests start failing mysteriously
- ❌ Test coverage drops > 5%
- ❌ Refactoring scope grows beyond original plan
- ❌ Temptation to "fix bugs while refactoring" (separate PRs!)
- ❌ Changes touch > 10 files (break into smaller steps)
"""
        return checklist

    def _identify_risks(self, task: WizardTask, refactoring_plan: list[str]) -> list[WizardRisk]:
        """Identify refactoring risks"""
        risks = []

        # Behavior change risk
        risks.append(
            WizardRisk(
                risk="Refactoring may accidentally change behavior",
                mitigation="Run full test suite after each atomic refactoring step. If tests fail, revert immediately.",
                severity="high",
            ),
        )

        # Scope creep risk
        risks.append(
            WizardRisk(
                risk="Refactoring scope may grow ('while we're here, let's also...')",
                mitigation="Stick to original plan. Create separate tickets for additional improvements.",
                severity="medium",
            ),
        )

        # Test coverage gap risk
        risks.append(
            WizardRisk(
                risk="Low test coverage may hide behavioral changes",
                mitigation="Add tests BEFORE refactoring complex code. Target: 80%+ coverage.",
                severity="high",
            ),
        )

        return risks

    def _create_handoffs(self, task: WizardTask) -> list[WizardHandoff]:
        """Create handoffs for refactoring work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(
                WizardHandoff(
                    owner="Team Lead / Senior Dev",
                    what="Code review of refactored code (focus on behavior preservation)",
                    when="After refactoring complete, before merge",
                ),
            )

        return handoffs
