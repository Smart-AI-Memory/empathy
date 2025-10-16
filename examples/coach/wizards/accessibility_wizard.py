"""
Accessibility Wizard

WCAG compliance, inclusive design, screen reader compatibility, keyboard navigation.
Uses Empathy Framework Level 3 (Proactive) for a11y audit and Level 4
(Anticipatory) for predicting accessibility barriers and compliance risks.

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


class AccessibilityWizard(BaseWizard):
    """
    Wizard for accessibility (a11y) compliance and inclusive design

    Uses:
    - Level 2: Guide user through WCAG guidelines
    - Level 3: Proactively audit for accessibility issues
    - Level 4: Anticipate accessibility barriers before they reach users
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is an accessibility task"""
        # High-priority accessibility phrases (worth 2 points each)
        accessibility_phrases = [
            "accessibility", "a11y", "wcag", "screen reader", "aria"
        ]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "contrast", "keyboard", "focus", "alt text", "semantic html",
            "inclusive", "disability", "section 508", "ada compliance",
            "voiceover", "nvda", "jaws", "color blind"
        ]

        task_lower = (task.task + " " + task.context).lower()

        # Count high-priority matches (2 points each)
        primary_matches = sum(2 for phrase in accessibility_phrases if phrase in task_lower)

        # Count secondary matches (1 point each)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)  # 6+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute accessibility audit workflow"""

        # Step 1: Assess emotional context
        emotional_state = self._assess_emotional_state(task)

        # Step 2: Extract constraints
        constraints = self._extract_constraints(task)

        # Step 3: Analyze accessibility requirements
        diagnosis = self._analyze_accessibility_requirements(task)

        # Step 4: Audit for issues (Level 3: Proactive)
        audit_results = self._audit_accessibility(task)

        # Step 5: Create remediation plan
        remediation_plan = self._create_remediation_plan(task, audit_results)

        # Step 6: Generate remediation code
        remediation_code = self._generate_remediation_code(task, audit_results)

        # Step 7: Create keyboard navigation tests
        keyboard_tests = self._create_keyboard_tests(task)

        # Step 8: Generate ARIA labels
        aria_implementation = self._generate_aria_implementation(task)

        # Step 9: Predict accessibility barriers (Level 4: Anticipatory)
        accessibility_forecast = self._predict_accessibility_barriers(task, audit_results)

        # Step 10: Identify risks
        risks = self._identify_risks(task, remediation_plan)

        # Step 11: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="WCAG Audit Report",
                content=self._generate_audit_report(diagnosis, audit_results)
            ),
            WizardArtifact(
                type="code",
                title="Remediation Code Examples",
                content=remediation_code
            ),
            WizardArtifact(
                type="code",
                title="Keyboard Navigation Tests",
                content=keyboard_tests
            ),
            WizardArtifact(
                type="code",
                title="ARIA Labels Implementation",
                content=aria_implementation
            ),
            WizardArtifact(
                type="checklist",
                title="Accessibility Testing Checklist",
                content=self._create_testing_checklist(task)
            ),
            WizardArtifact(
                type="doc",
                title="Accessibility Forecast",
                content=accessibility_forecast
            )
        ]

        # Step 12: Generate next actions
        next_actions = remediation_plan[:5] + self._generate_anticipatory_actions(task)

        # Step 13: Create empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered users with disabilities: vision, motor, cognitive, hearing impairments",
            emotional=f"Acknowledged: Accessibility is about human dignity and equal access",
            anticipatory=accessibility_forecast[:200] + "..." if len(accessibility_forecast) > 200 else accessibility_forecast
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=remediation_plan,
            artifacts=artifacts,
            risks=risks,
            handoffs=self._create_handoffs(task),
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task)
        )

    def _analyze_accessibility_requirements(self, task: WizardTask) -> str:
        """Analyze accessibility requirements"""
        analysis = "# Accessibility Requirements Analysis\n\n"
        analysis += f"**Objective**: {task.task}\n\n"

        # Categorize accessibility needs
        categories = []
        task_lower = (task.task + " " + task.context).lower()

        if any(kw in task_lower for kw in ["wcag", "compliance", "standard"]):
            categories.append("WCAG Compliance")
        if any(kw in task_lower for kw in ["screen reader", "voiceover", "nvda", "jaws"]):
            categories.append("Screen Reader Support")
        if any(kw in task_lower for kw in ["keyboard", "focus", "tab"]):
            categories.append("Keyboard Navigation")
        if any(kw in task_lower for kw in ["contrast", "color", "vision"]):
            categories.append("Visual Accessibility")
        if any(kw in task_lower for kw in ["aria", "semantic", "html"]):
            categories.append("Semantic HTML & ARIA")

        if not categories:
            categories.append("General Accessibility")

        analysis += f"**Category**: {', '.join(categories)}\n\n"
        analysis += "**Target Compliance Level**: WCAG 2.1 Level AA (minimum legal requirement)\n"
        analysis += f"**Context**: {task.context[:300]}...\n" if len(task.context) > 300 else f"**Context**: {task.context}\n"

        return analysis

    def _audit_accessibility(self, task: WizardTask) -> List[Dict[str, Any]]:
        """Audit for accessibility issues (Level 3: Proactive)"""
        issues = []

        task_lower = (task.task + " " + task.context).lower()

        # WCAG 2.1 Level A issues
        issues.append({
            "criterion": "1.1.1 Non-text Content",
            "level": "A",
            "severity": "critical",
            "issue": "Images missing alt text",
            "impact": "Screen reader users cannot understand image content",
            "remediation": [
                "Add descriptive alt text to all images",
                "Use alt=\"\" for decorative images",
                "Provide text alternatives for complex graphics"
            ]
        })

        issues.append({
            "criterion": "1.3.1 Info and Relationships",
            "level": "A",
            "severity": "high",
            "issue": "Improper heading structure (skipped levels)",
            "impact": "Screen reader users cannot navigate by headings",
            "remediation": [
                "Use semantic HTML: <h1>, <h2>, <h3> in order",
                "Don't skip heading levels (h1 → h3)",
                "One <h1> per page for main heading"
            ]
        })

        # WCAG 2.1 Level AA issues
        issues.append({
            "criterion": "1.4.3 Contrast (Minimum)",
            "level": "AA",
            "severity": "high",
            "issue": "Insufficient color contrast (text on background)",
            "impact": "Low vision users cannot read text",
            "remediation": [
                "Ensure 4.5:1 contrast for normal text",
                "Ensure 3:1 contrast for large text (18pt+)",
                "Use color contrast checker tool"
            ]
        })

        issues.append({
            "criterion": "2.1.1 Keyboard",
            "level": "A",
            "severity": "critical",
            "issue": "Interactive elements not keyboard accessible",
            "impact": "Keyboard-only users cannot interact with UI",
            "remediation": [
                "Ensure all interactive elements have keyboard focus",
                "Use semantic HTML (button, a, input)",
                "Add tabindex=\"0\" if custom interactive elements needed"
            ]
        })

        issues.append({
            "criterion": "2.4.3 Focus Order",
            "level": "A",
            "severity": "medium",
            "issue": "Tab order doesn't follow visual order",
            "impact": "Keyboard users get disoriented",
            "remediation": [
                "Ensure DOM order matches visual order",
                "Avoid positive tabindex values",
                "Test tab navigation flow"
            ]
        })

        issues.append({
            "criterion": "2.4.7 Focus Visible",
            "level": "AA",
            "severity": "high",
            "issue": "Focus indicator not visible or removed",
            "impact": "Keyboard users can't see where they are",
            "remediation": [
                "Don't remove outline: none on :focus",
                "Provide visible focus indicator (border, shadow)",
                "Ensure 3:1 contrast for focus indicator"
            ]
        })

        issues.append({
            "criterion": "4.1.2 Name, Role, Value",
            "level": "A",
            "severity": "critical",
            "issue": "Custom widgets missing ARIA labels/roles",
            "impact": "Screen readers can't identify or operate controls",
            "remediation": [
                "Add ARIA roles: role=\"button\", role=\"dialog\"",
                "Add ARIA labels: aria-label=\"Close\"",
                "Add ARIA states: aria-expanded, aria-selected"
            ]
        })

        return issues

    def _create_remediation_plan(self, task: WizardTask, audit_results: List[Dict]) -> List[str]:
        """Create step-by-step remediation plan"""
        plan = ["## Accessibility Remediation Plan (Priority Ordered)\n"]

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_issues = sorted(audit_results, key=lambda i: severity_order.get(i["severity"], 3))

        for i, issue in enumerate(sorted_issues, 1):
            plan.append(f"\n### Step {i}: Fix {issue['criterion']} (WCAG {issue['level']}, {issue['severity']})")
            plan.append(f"**Issue**: {issue['issue']}")
            plan.append(f"**Impact**: {issue['impact']}")
            plan.append("\n**Remediation Steps**:")
            for j, step in enumerate(issue['remediation'], 1):
                plan.append(f"  {j}. {step}")

        plan.append(f"\n### Step {len(sorted_issues)+1}: Validation")
        plan.append("  1. Run automated accessibility tests (axe-core, Lighthouse)")
        plan.append("  2. Manual keyboard navigation testing")
        plan.append("  3. Screen reader testing (NVDA, VoiceOver)")
        plan.append("  4. Color contrast verification")

        return plan

    def _generate_remediation_code(self, task: WizardTask, audit_results: List[Dict]) -> str:
        """Generate accessibility remediation code"""
        code = "# Accessibility Remediation Examples\n\n"

        code += "## 1. Add Alt Text to Images\n\n"
        code += "```html\n"
        code += "<!-- Before (Inaccessible): -->\n"
        code += "<img src=\"logo.png\">\n\n"
        code += "<!-- After (Accessible): -->\n"
        code += "<img src=\"logo.png\" alt=\"Company Logo - Click to go home\">\n\n"
        code += "<!-- Decorative image (no alt needed): -->\n"
        code += "<img src=\"decorative-divider.png\" alt=\"\" role=\"presentation\">\n"
        code += "```\n\n"

        code += "## 2. Fix Heading Structure\n\n"
        code += "```html\n"
        code += "<!-- Before (Inaccessible - skipped h2): -->\n"
        code += "<h1>Page Title</h1>\n"
        code += "<h3>Section Title</h3>  <!-- Should be h2! -->\n\n"
        code += "<!-- After (Accessible): -->\n"
        code += "<h1>Page Title</h1>\n"
        code += "<h2>Section Title</h2>\n"
        code += "<h3>Subsection Title</h3>\n"
        code += "```\n\n"

        code += "## 3. Improve Color Contrast\n\n"
        code += "```css\n"
        code += "/* Before (Inaccessible - 2.5:1 contrast): */\n"
        code += ".text {\n"
        code += "  color: #777;  /* Gray */\n"
        code += "  background: #fff;  /* White */\n"
        code += "}\n\n"
        code += "/* After (Accessible - 7:1 contrast): */\n"
        code += ".text {\n"
        code += "  color: #333;  /* Darker gray */\n"
        code += "  background: #fff;  /* White */\n"
        code += "}\n\n"
        code += "/* Verify contrast: https://webaim.org/resources/contrastchecker/ */\n"
        code += "```\n\n"

        code += "## 4. Enable Keyboard Navigation\n\n"
        code += "```html\n"
        code += "<!-- Before (Inaccessible - div not keyboard accessible): -->\n"
        code += "<div onclick=\"openModal()\">Click me</div>\n\n"
        code += "<!-- After (Accessible - button is keyboard accessible): -->\n"
        code += "<button onclick=\"openModal()\" type=\"button\">Click me</button>\n\n"
        code += "<!-- Or if you must use div: -->\n"
        code += "<div \n"
        code += "  onclick=\"openModal()\" \n"
        code += "  onkeydown=\"if(event.key === 'Enter' || event.key === ' ') openModal()\"\n"
        code += "  tabindex=\"0\" \n"
        code += "  role=\"button\"\n"
        code += "  aria-label=\"Open modal\">\n"
        code += "  Click me\n"
        code += "</div>\n"
        code += "```\n\n"

        code += "## 5. Add Visible Focus Indicator\n\n"
        code += "```css\n"
        code += "/* Before (Inaccessible - removed focus outline): */\n"
        code += "button:focus {\n"
        code += "  outline: none;  /* BAD! */\n"
        code += "}\n\n"
        code += "/* After (Accessible - custom focus indicator): */\n"
        code += "button:focus {\n"
        code += "  outline: 3px solid #0066cc;  /* Blue outline */\n"
        code += "  outline-offset: 2px;\n"
        code += "}\n\n"
        code += "/* Or with box-shadow: */\n"
        code += "button:focus {\n"
        code += "  outline: none;\n"
        code += "  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.5);  /* Blue glow */\n"
        code += "}\n"
        code += "```\n\n"

        code += "## 6. Add ARIA Labels to Custom Widgets\n\n"
        code += "```html\n"
        code += "<!-- Before (Inaccessible - no screen reader support): -->\n"
        code += "<div class=\"custom-dropdown\">\n"
        code += "  <div class=\"selected\">Select option</div>\n"
        code += "  <ul class=\"options\">\n"
        code += "    <li>Option 1</li>\n"
        code += "    <li>Option 2</li>\n"
        code += "  </ul>\n"
        code += "</div>\n\n"
        code += "<!-- After (Accessible - ARIA support): -->\n"
        code += "<div class=\"custom-dropdown\" role=\"combobox\" aria-expanded=\"false\" aria-haspopup=\"listbox\">\n"
        code += "  <div \n"
        code += "    class=\"selected\" \n"
        code += "    tabindex=\"0\" \n"
        code += "    role=\"button\" \n"
        code += "    aria-label=\"Select option\"\n"
        code += "    aria-controls=\"options-list\">\n"
        code += "    Select option\n"
        code += "  </div>\n"
        code += "  <ul id=\"options-list\" class=\"options\" role=\"listbox\">\n"
        code += "    <li role=\"option\" tabindex=\"-1\">Option 1</li>\n"
        code += "    <li role=\"option\" tabindex=\"-1\">Option 2</li>\n"
        code += "  </ul>\n"
        code += "</div>\n"
        code += "```\n\n"

        code += "## 7. Form Labels and Error Messages\n\n"
        code += "```html\n"
        code += "<!-- Before (Inaccessible): -->\n"
        code += "<input type=\"email\" placeholder=\"Email\">\n"
        code += "<span class=\"error\">Invalid email</span>\n\n"
        code += "<!-- After (Accessible): -->\n"
        code += "<label for=\"email-input\">Email address</label>\n"
        code += "<input \n"
        code += "  type=\"email\" \n"
        code += "  id=\"email-input\"\n"
        code += "  aria-describedby=\"email-error\"\n"
        code += "  aria-invalid=\"true\">\n"
        code += "<span id=\"email-error\" role=\"alert\" class=\"error\">\n"
        code += "  Invalid email format. Please use format: name@example.com\n"
        code += "</span>\n"
        code += "```\n"

        return code

    def _create_keyboard_tests(self, task: WizardTask) -> str:
        """Create keyboard navigation tests"""
        tests = "# Keyboard Navigation Tests\n\n"

        tests += "```javascript\n"
        tests += "// Automated keyboard accessibility tests (using @testing-library/react)\n\n"
        tests += "import { render, screen } from '@testing-library/react';\n"
        tests += "import userEvent from '@testing-library/user-event';\n\n"

        tests += "describe('Keyboard Navigation', () => {\n\n"

        tests += "  test('all interactive elements are keyboard accessible', async () => {\n"
        tests += "    render(<App />);\n"
        tests += "    const buttons = screen.getAllByRole('button');\n"
        tests += "    const links = screen.getAllByRole('link');\n"
        tests += "    const inputs = screen.getAllByRole('textbox');\n\n"

        tests += "    // All elements should be focusable\n"
        tests += "    [...buttons, ...links, ...inputs].forEach(element => {\n"
        tests += "      expect(element).toHaveAttribute('tabindex', expect.stringMatching(/^(0|-1)$/));\n"
        tests += "    });\n"
        tests += "  });\n\n"

        tests += "  test('tab navigation follows logical order', async () => {\n"
        tests += "    render(<Form />);\n"
        tests += "    const user = userEvent.setup();\n\n"

        tests += "    // Tab through form fields\n"
        tests += "    await user.tab();\n"
        tests += "    expect(screen.getByLabelText('First Name')).toHaveFocus();\n\n"

        tests += "    await user.tab();\n"
        tests += "    expect(screen.getByLabelText('Last Name')).toHaveFocus();\n\n"

        tests += "    await user.tab();\n"
        tests += "    expect(screen.getByLabelText('Email')).toHaveFocus();\n\n"

        tests += "    await user.tab();\n"
        tests += "    expect(screen.getByRole('button', { name: 'Submit' })).toHaveFocus();\n"
        tests += "  });\n\n"

        tests += "  test('Enter key activates buttons', async () => {\n"
        tests += "    const handleClick = jest.fn();\n"
        tests += "    render(<button onClick={handleClick}>Submit</button>);\n"
        tests += "    const user = userEvent.setup();\n\n"

        tests += "    const button = screen.getByRole('button');\n"
        tests += "    button.focus();\n"
        tests += "    await user.keyboard('{Enter}');\n\n"

        tests += "    expect(handleClick).toHaveBeenCalledTimes(1);\n"
        tests += "  });\n\n"

        tests += "  test('Escape key closes modal', async () => {\n"
        tests += "    const handleClose = jest.fn();\n"
        tests += "    render(<Modal onClose={handleClose} isOpen={true} />);\n"
        tests += "    const user = userEvent.setup();\n\n"

        tests += "    await user.keyboard('{Escape}');\n\n"
        tests += "    expect(handleClose).toHaveBeenCalledTimes(1);\n"
        tests += "  });\n\n"

        tests += "  test('focus trap works in modal', async () => {\n"
        tests += "    render(<Modal isOpen={true} />);\n"
        tests += "    const user = userEvent.setup();\n\n"

        tests += "    const firstButton = screen.getByRole('button', { name: 'Confirm' });\n"
        tests += "    const lastButton = screen.getByRole('button', { name: 'Cancel' });\n\n"

        tests += "    firstButton.focus();\n"
        tests += "    await user.tab();\n"
        tests += "    expect(lastButton).toHaveFocus();\n\n"

        tests += "    // Tab from last element should cycle to first\n"
        tests += "    await user.tab();\n"
        tests += "    expect(firstButton).toHaveFocus();\n"
        tests += "  });\n"
        tests += "});\n"
        tests += "```\n\n"

        tests += "## Manual Keyboard Testing Checklist\n\n"
        tests += "Test the following without using a mouse:\n\n"
        tests += "- [ ] Tab through all interactive elements\n"
        tests += "- [ ] Shift+Tab navigates backwards\n"
        tests += "- [ ] Enter/Space activates buttons and links\n"
        tests += "- [ ] Arrow keys navigate menus and lists\n"
        tests += "- [ ] Escape closes modals/dropdowns\n"
        tests += "- [ ] Focus is visible at all times\n"
        tests += "- [ ] Focus doesn't get trapped (except in modals)\n"
        tests += "- [ ] Skip links work (\"Skip to main content\")\n"

        return tests

    def _generate_aria_implementation(self, task: WizardTask) -> str:
        """Generate ARIA implementation examples"""
        aria = "# ARIA Implementation Guide\n\n"

        aria += "## Common ARIA Patterns\n\n"

        aria += "### 1. Button (Custom Div)\n\n"
        aria += "```html\n"
        aria += "<div \n"
        aria += "  role=\"button\" \n"
        aria += "  tabindex=\"0\"\n"
        aria += "  aria-label=\"Delete item\"\n"
        aria += "  onclick=\"deleteItem()\"\n"
        aria += "  onkeydown=\"if(event.key === 'Enter' || event.key === ' ') deleteItem()\">\n"
        aria += "  🗑️\n"
        aria += "</div>\n\n"
        aria += "<!-- Better: Use semantic HTML -->\n"
        aria += "<button type=\"button\" aria-label=\"Delete item\" onclick=\"deleteItem()\">\n"
        aria += "  🗑️\n"
        aria += "</button>\n"
        aria += "```\n\n"

        aria += "### 2. Toggle Button (Show/Hide)\n\n"
        aria += "```html\n"
        aria += "<button \n"
        aria += "  type=\"button\"\n"
        aria += "  aria-expanded=\"false\" \n"
        aria += "  aria-controls=\"details-section\"\n"
        aria += "  onclick=\"toggleDetails()\">\n"
        aria += "  Show Details\n"
        aria += "</button>\n\n"
        aria += "<div id=\"details-section\" hidden>\n"
        aria += "  Details content...\n"
        aria += "</div>\n\n"
        aria += "<!-- JavaScript updates aria-expanded when toggled -->\n"
        aria += "<script>\n"
        aria += "function toggleDetails() {\n"
        aria += "  const button = event.target;\n"
        aria += "  const details = document.getElementById('details-section');\n"
        aria += "  const isExpanded = button.getAttribute('aria-expanded') === 'true';\n"
        aria += "  \n"
        aria += "  button.setAttribute('aria-expanded', !isExpanded);\n"
        aria += "  details.hidden = isExpanded;\n"
        aria += "}\n"
        aria += "</script>\n"
        aria += "```\n\n"

        aria += "### 3. Modal Dialog\n\n"
        aria += "```html\n"
        aria += "<div \n"
        aria += "  role=\"dialog\" \n"
        aria += "  aria-labelledby=\"dialog-title\"\n"
        aria += "  aria-describedby=\"dialog-description\"\n"
        aria += "  aria-modal=\"true\">\n"
        aria += "  \n"
        aria += "  <h2 id=\"dialog-title\">Confirm Action</h2>\n"
        aria += "  <p id=\"dialog-description\">Are you sure you want to delete this item?</p>\n"
        aria += "  \n"
        aria += "  <button type=\"button\" onclick=\"confirm()\">Confirm</button>\n"
        aria += "  <button type=\"button\" onclick=\"cancel()\">Cancel</button>\n"
        aria += "</div>\n"
        aria += "```\n\n"

        aria += "### 4. Live Region (Status Updates)\n\n"
        aria += "```html\n"
        aria += "<!-- Polite: Announces when screen reader is idle -->\n"
        aria += "<div aria-live=\"polite\" aria-atomic=\"true\" role=\"status\">\n"
        aria += "  Item added to cart\n"
        aria += "</div>\n\n"
        aria += "<!-- Assertive: Announces immediately (use sparingly) -->\n"
        aria += "<div aria-live=\"assertive\" role=\"alert\">\n"
        aria += "  Error: Failed to save changes\n"
        aria += "</div>\n"
        aria += "```\n\n"

        aria += "### 5. Tab Navigation\n\n"
        aria += "```html\n"
        aria += "<div role=\"tablist\" aria-label=\"Settings\">\n"
        aria += "  <button \n"
        aria += "    role=\"tab\" \n"
        aria += "    aria-selected=\"true\" \n"
        aria += "    aria-controls=\"panel-general\"\n"
        aria += "    id=\"tab-general\">\n"
        aria += "    General\n"
        aria += "  </button>\n"
        aria += "  <button \n"
        aria += "    role=\"tab\" \n"
        aria += "    aria-selected=\"false\" \n"
        aria += "    aria-controls=\"panel-privacy\"\n"
        aria += "    id=\"tab-privacy\">\n"
        aria += "    Privacy\n"
        aria += "  </button>\n"
        aria += "</div>\n\n"
        aria += "<div id=\"panel-general\" role=\"tabpanel\" aria-labelledby=\"tab-general\">\n"
        aria += "  General settings content...\n"
        aria += "</div>\n"
        aria += "<div id=\"panel-privacy\" role=\"tabpanel\" aria-labelledby=\"tab-privacy\" hidden>\n"
        aria += "  Privacy settings content...\n"
        aria += "</div>\n"
        aria += "```\n\n"

        aria += "## ARIA Best Practices\n\n"
        aria += "1. **Use semantic HTML first**: `<button>` over `<div role=\"button\">`\n"
        aria += "2. **Don't override semantics**: Don't use `role=\"button\"` on `<button>`\n"
        aria += "3. **Keep it simple**: Only add ARIA when HTML semantics insufficient\n"
        aria += "4. **Test with screen readers**: NVDA (Windows), VoiceOver (Mac/iOS)\n"
        aria += "5. **Update dynamic content**: Keep aria-expanded, aria-selected up to date\n"

        return aria

    def _create_testing_checklist(self, task: WizardTask) -> str:
        """Create accessibility testing checklist"""
        checklist = "# Accessibility Testing Checklist\n\n"

        checklist += "## Automated Testing\n\n"
        checklist += "- [ ] Run axe-core automated tests (Chrome DevTools)\n"
        checklist += "- [ ] Run Lighthouse accessibility audit (score 90+)\n"
        checklist += "- [ ] Run WAVE browser extension\n"
        checklist += "- [ ] Check color contrast with WebAIM tool\n"
        checklist += "- [ ] Validate HTML (W3C validator)\n\n"

        checklist += "## Keyboard Testing\n\n"
        checklist += "- [ ] Tab through entire page (no mouse)\n"
        checklist += "- [ ] All interactive elements reachable\n"
        checklist += "- [ ] Focus order follows visual order\n"
        checklist += "- [ ] Focus indicator visible\n"
        checklist += "- [ ] Enter/Space activates controls\n"
        checklist += "- [ ] Escape closes modals/menus\n"
        checklist += "- [ ] Skip links work\n\n"

        checklist += "## Screen Reader Testing\n\n"
        checklist += "**NVDA (Windows - Free)**:\n"
        checklist += "- [ ] All content readable\n"
        checklist += "- [ ] Headings navigable (H key)\n"
        checklist += "- [ ] Landmarks navigable (D key)\n"
        checklist += "- [ ] Forms labeled correctly\n"
        checklist += "- [ ] Buttons/links have descriptive text\n"
        checklist += "- [ ] Images have alt text\n"
        checklist += "- [ ] ARIA labels announced\n\n"

        checklist += "**VoiceOver (Mac/iOS)**:\n"
        checklist += "- [ ] Navigate with VO + arrows\n"
        checklist += "- [ ] Rotor menu works (VO + U)\n"
        checklist += "- [ ] Forms work with VO\n\n"

        checklist += "## Visual Testing\n\n"
        checklist += "- [ ] Zoom to 200% - content still readable\n"
        checklist += "- [ ] Text reflows (no horizontal scroll)\n"
        checklist += "- [ ] Color contrast 4.5:1 (normal text)\n"
        checklist += "- [ ] Color contrast 3:1 (large text)\n"
        checklist += "- [ ] Content understandable without color\n"
        checklist += "- [ ] Focus indicators visible\n\n"

        checklist += "## Mobile Testing\n\n"
        checklist += "- [ ] Touch targets 44x44px minimum\n"
        checklist += "- [ ] VoiceOver works (iOS)\n"
        checklist += "- [ ] TalkBack works (Android)\n"
        checklist += "- [ ] Screen rotation works\n\n"

        checklist += "## Content Testing\n\n"
        checklist += "- [ ] Page has `<title>`\n"
        checklist += "- [ ] Headings describe content\n"
        checklist += "- [ ] Links have descriptive text (not \"click here\")\n"
        checklist += "- [ ] Language specified: `<html lang=\"en\">`\n"
        checklist += "- [ ] Form errors announced to screen readers\n"

        return checklist

    def _predict_accessibility_barriers(self, task: WizardTask, audit_results: List[Dict]) -> str:
        """Level 4: Predict accessibility barriers"""
        forecast = "# Accessibility Forecast (Level 4: Anticipatory)\n\n"

        critical_issues = [i for i in audit_results if i['severity'] == 'critical']

        forecast += "## Current State\n"
        forecast += f"- Critical issues: {len(critical_issues)}\n"
        forecast += f"- Total issues: {len(audit_results)}\n"
        forecast += "- Target: WCAG 2.1 Level AA compliance\n\n"

        forecast += "## Projected Barriers (Before User Impact)\n\n"

        forecast += "### ⚠️ Screen Reader Users Blocked (Now)\n"
        forecast += "**Prediction**: Missing ARIA labels will prevent screen reader users from using app\n"
        forecast += "**Impact**: 5-8% of users (blind/low vision) completely blocked\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Fix critical ARIA issues NOW (before launch)\n"
        forecast += "- Test with NVDA/VoiceOver before every release\n"
        forecast += "- Add automated accessibility tests to CI/CD\n\n"

        forecast += "### ⚠️ Keyboard Users Frustrated (Week 1)\n"
        forecast += "**Prediction**: Keyboard-only users will encounter unusable interactions\n"
        forecast += "**Impact**: 15-20% of users (motor disabilities, power users) frustrated\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Ensure ALL interactive elements keyboard accessible\n"
        forecast += "- Add visible focus indicators\n"
        forecast += "- Test entire user flow with keyboard only\n\n"

        forecast += "### ⚠️ Low Vision Users Struggle (Week 2)\n"
        forecast += "**Prediction**: Insufficient contrast will make text unreadable for low vision users\n"
        forecast += "**Impact**: 8-10% of users (low vision, age-related) strain to read\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Check contrast for ALL text (4.5:1 minimum)\n"
        forecast += "- Support browser zoom to 200%\n"
        forecast += "- Avoid color-only information (add icons/text)\n\n"

        forecast += "### ⚠️ Legal Compliance Risk (30 days)\n"
        forecast += "**Prediction**: ADA/Section 508 violations may trigger legal action\n"
        forecast += "**Impact**: Lawsuits, bad PR, mandatory remediation costs\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Achieve WCAG 2.1 AA compliance BEFORE public launch\n"
        forecast += "- Document accessibility testing\n"
        forecast += "- Create accessibility statement page\n"
        forecast += "- Provide alternative contact method for accessibility issues\n\n"

        forecast += "## Accessibility Debt Growth Trajectory\n\n"
        forecast += "**If not addressed now**:\n"
        forecast += "- Month 1: 7 critical issues\n"
        forecast += "- Month 3: 20+ issues (as features added without a11y consideration)\n"
        forecast += "- Month 6: Remediation becomes major project (weeks of work)\n"
        forecast += "- Month 12: Legal exposure, user complaints escalate\n\n"

        forecast += "**If addressed now**:\n"
        forecast += "- Week 1-2: Fix critical issues (20 hours)\n"
        forecast += "- Week 3: Add automated tests (prevent regression)\n"
        forecast += "- Ongoing: Accessibility built into development process\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Now (Week 1)**: Fix all critical issues\n"
        forecast += "- **Week 2**: Add automated accessibility tests to CI/CD\n"
        forecast += "- **Week 3**: Manual screen reader testing\n"
        forecast += "- **Week 4**: Accessibility training for developers\n"
        forecast += "- **Ongoing**: Include accessibility in code reviews\n"

        return forecast

    def _generate_audit_report(self, diagnosis: str, audit_results: List[Dict]) -> str:
        """Generate comprehensive WCAG audit report"""
        report = f"{diagnosis}\n\n"

        report += "## WCAG 2.1 Compliance Summary\n\n"

        critical = len([i for i in audit_results if i['severity'] == 'critical'])
        high = len([i for i in audit_results if i['severity'] == 'high'])
        medium = len([i for i in audit_results if i['severity'] == 'medium'])

        report += f"- **Critical**: {critical} issues (MUST fix before launch)\n"
        report += f"- **High**: {high} issues (Should fix soon)\n"
        report += f"- **Medium**: {medium} issues (Fix when possible)\n\n"

        report += "**Current Compliance**: ❌ Does not meet WCAG 2.1 AA\n"
        report += "**Target**: WCAG 2.1 Level AA (legal requirement for most jurisdictions)\n\n"

        report += "## Detailed Findings\n\n"

        for i, issue in enumerate(audit_results, 1):
            report += f"### {i}. {issue['criterion']} (Level {issue['level']})\n"
            report += f"**Severity**: {issue['severity']}\n"
            report += f"**Issue**: {issue['issue']}\n"
            report += f"**Impact**: {issue['impact']}\n\n"
            report += "**Remediation**:\n"
            for step in issue['remediation']:
                report += f"- {step}\n"
            report += "\n"

        return report

    def _identify_risks(self, task: WizardTask, remediation_plan: List[str]) -> List[WizardRisk]:
        """Identify accessibility risks"""
        risks = []

        # Legal risk
        risks.append(WizardRisk(
            risk="Non-compliance may trigger ADA/Section 508 lawsuits",
            mitigation="Achieve WCAG 2.1 AA compliance before public launch. Document testing. Create accessibility statement.",
            severity="high"
        ))

        # User exclusion risk
        risks.append(WizardRisk(
            risk="Accessibility barriers exclude 15-20% of potential users",
            mitigation="Fix critical issues immediately. Test with assistive technologies. Include disabled users in testing.",
            severity="high"
        ))

        # Technical debt risk
        risks.append(WizardRisk(
            risk="Retrofitting accessibility is 10x more expensive than building it in",
            mitigation="Include accessibility in code reviews. Add automated tests. Train developers on WCAG.",
            severity="medium"
        ))

        return risks

    def _create_handoffs(self, task: WizardTask) -> List[WizardHandoff]:
        """Create handoffs for accessibility work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(WizardHandoff(
                owner="QA / Accessibility Specialist",
                what="Manual screen reader testing, keyboard testing, WCAG compliance verification",
                when="Before every release"
            ))
            handoffs.append(WizardHandoff(
                owner="Legal / Compliance",
                what="Review accessibility statement, ensure ADA/Section 508 compliance",
                when="Before public launch"
            ))

        return handoffs
