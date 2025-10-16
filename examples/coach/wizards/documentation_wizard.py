"""
Documentation Wizard

Identifies friction points and generates/updates docs to unblock teams.
Uses Empathy Framework Level 2 (Guided) for clear communication and
Level 4 (Anticipatory) to prevent future documentation gaps.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

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


class DocumentationWizard(BaseWizard):
    """
    Wizard for creating and updating documentation

    Uses:
    - Level 2: Guide readers with clear, structured docs
    - Level 3: Proactively identify common questions
    - Level 4: Anticipate onboarding and handoff needs
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a documentation task"""
        doc_keywords = [
            "doc", "readme", "documentation", "unclear", "confusing",
            "onboarding", "handoff", "guide", "tutorial", "explain"
        ]

        task_lower = (task.task + " " + task.context).lower()
        matches = sum(1 for keyword in doc_keywords if keyword in task_lower)

        return min(matches / 2.0, 1.0)  # 2+ keywords = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute documentation workflow"""

        # Step 1: Identify target audience and pain points
        audience = self._identify_audience(task)
        pain_points = self._identify_pain_points(task)

        # Step 2: Determine doc type needed
        doc_type = self._determine_doc_type(task, pain_points)

        # Step 3: Extract constraints
        constraints = self._extract_constraints(task)

        # Step 4: Generate diagnosis
        diagnosis = self._create_diagnosis(audience, pain_points, doc_type)

        # Step 5: Create documentation (Level 2: Guided)
        doc_content = self._generate_documentation(task, audience, pain_points, doc_type)

        # Step 6: Create handoff checklist
        handoff_checklist = self._create_handoff_checklist(task, audience)

        # Step 7: Identify gaps (Level 3: Proactive)
        potential_gaps = self._identify_potential_gaps(task, doc_type)

        # Step 8: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title=f"{doc_type} Documentation",
                content=doc_content
            ),
            WizardArtifact(
                type="checklist",
                title="Handoff Checklist",
                content=handoff_checklist
            )
        ]

        # Add gap-filling artifacts if identified
        if potential_gaps:
            artifacts.append(WizardArtifact(
                type="doc",
                title="Identified Documentation Gaps",
                content=self._format_gaps(potential_gaps)
            ))

        # Step 9: Create plan
        plan = [
            f"Identify friction for {audience['role']} role",
            f"Write {doc_type} addressing {len(pain_points)} pain points",
            "Review with target audience member",
            "Update README/docs with new content",
            "Add to onboarding checklist"
        ]

        # Step 10: Generate next actions
        next_actions = [
            "Draft documentation section",
            "Request review from target role",
            "Update main README with link",
            "Add to team wiki/docs site",
            "Share in team channel"
        ]

        # Add anticipatory actions
        anticipatory_actions = self._generate_anticipatory_actions(task)
        next_actions.extend(anticipatory_actions)

        # Step 11: Identify risks
        risks = [
            WizardRisk(
                risk="Documentation becomes stale quickly",
                mitigation="Add 'Last Updated' date and assign owner for quarterly review",
                severity="medium"
            ),
            WizardRisk(
                risk="Too technical for target audience",
                mitigation="Include glossary and 'Prerequisites' section",
                severity="low"
            )
        ]

        # Step 12: Create handoffs
        handoffs = [
            WizardHandoff(
                owner=audience["role"],
                what="Review documentation for clarity",
                when="Before merging"
            )
        ]

        # Step 13: Empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {audience['role']} perspective with {audience['experience']} experience level",
            emotional=f"Acknowledged confusion/frustration from {len(pain_points)} identified pain points",
            anticipatory=f"Proactively identified {len(potential_gaps)} potential doc gaps and created handoff checklist"
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
            confidence=self.can_handle(task)
        )

    def _identify_audience(self, task: WizardTask) -> Dict[str, str]:
        """Identify target audience for docs"""
        audience = {
            "role": task.role,
            "experience": "intermediate"
        }

        # Detect experience level from context
        if "new" in task.context.lower() or "onboarding" in task.task.lower():
            audience["experience"] = "beginner"
        elif "senior" in task.context.lower() or "architect" in task.role:
            audience["experience"] = "advanced"

        return audience

    def _identify_pain_points(self, task: WizardTask) -> List[str]:
        """Identify documentation pain points"""
        pain_points = []

        context_lower = task.context.lower() + " " + task.task.lower()

        pain_keywords = {
            "unclear": "Unclear instructions or explanations",
            "outdated": "Outdated information",
            "missing": "Missing critical information",
            "confusing": "Confusing structure or terminology",
            "handoff": "Handoff process not documented",
            "setup": "Setup/installation instructions missing",
            "example": "Missing examples or use cases"
        }

        for keyword, pain in pain_keywords.items():
            if keyword in context_lower:
                pain_points.append(pain)

        # If none found, assume general clarity issue
        if not pain_points:
            pain_points.append("General documentation clarity improvements needed")

        return pain_points

    def _determine_doc_type(self, task: WizardTask, pain_points: List[str]) -> str:
        """Determine what type of doc to create"""
        task_lower = task.task.lower() + " " + task.context.lower()

        if "readme" in task_lower:
            return "README"
        elif "handoff" in task_lower or any("handoff" in p.lower() for p in pain_points):
            return "Handoff Guide"
        elif "onboarding" in task_lower:
            return "Onboarding Guide"
        elif "setup" in task_lower or "install" in task_lower:
            return "Setup Guide"
        elif "api" in task_lower:
            return "API Documentation"
        elif "hotfix" in task_lower:
            return "Hotfix Process"
        else:
            return "Quick Start Guide"

    def _create_diagnosis(self, audience: Dict, pain_points: List[str], doc_type: str) -> str:
        """Create diagnosis of documentation needs"""
        return f"{doc_type} needed for {audience['role']} ({audience['experience']} level) to address: {', '.join(pain_points[:2])}"

    def _generate_documentation(self, task: WizardTask, audience: Dict,
                                pain_points: List[str], doc_type: str) -> str:
        """Generate the actual documentation"""

        if doc_type == "Handoff Guide":
            return self._generate_handoff_guide(task)
        elif doc_type == "README":
            return self._generate_readme_section(task, pain_points)
        elif doc_type == "Hotfix Process":
            return self._generate_hotfix_process(task)
        elif doc_type == "Setup Guide":
            return self._generate_setup_guide(task)
        else:
            return self._generate_quick_start(task, audience)

    def _generate_handoff_guide(self, task: WizardTask) -> str:
        """Generate handoff documentation"""
        return """# Handoff Guide

## Quick Context
**What**: [Brief description of what's being handed off]
**Why**: [Reason for handoff]
**Urgency**: [Timeline/urgency level]

## Current State
- **Status**: [Where things stand now]
- **Blockers**: [Any current blockers]
- **Next Steps**: [Immediate next actions]

## Key Information
### Technical Context
- Repository: [Link]
- Branch: [Branch name]
- Environment: [Staging/production]
- Related PRs: [Links]

### Business Context
- Stakeholders: [Who cares about this]
- Deadline: [When it's needed]
- Success Criteria: [How we know it's done]

## How to Continue
1. [First step]
2. [Second step]
3. [Third step]

## Gotchas / Known Issues
- [Thing to watch out for #1]
- [Thing to watch out for #2]

## Resources
- [Relevant doc link]
- [Relevant slack channel]
- [Person to ask: @username]

## Questions?
Contact: [Your name] via [Slack/Email]
Availability: [Your availability]

---
*Last Updated*: [Date]
*Handoff From*: [Your name]
*Handoff To*: [Recipient name/role]
"""

    def _generate_readme_section(self, task: WizardTask, pain_points: List[str]) -> str:
        """Generate README section addressing pain points"""
        return """# [Feature/Component Name]

## Overview
[1-2 sentence description of what this does and why it exists]

## Quick Start
```bash
# Step 1: [Action]
command here

# Step 2: [Action]
another command

# Step 3: Verify
test command
```

## Configuration
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `PARAM_1` | Yes | - | [What it does] |
| `PARAM_2` | No | `value` | [What it does] |

## Common Use Cases
### Use Case 1: [Name]
```python
# Example code
example_usage()
```

### Use Case 2: [Name]
```python
# Another example
another_example()
```

## Troubleshooting
**Problem**: [Common issue]
**Solution**: [How to fix]

**Problem**: [Another issue]
**Solution**: [How to fix]

## Additional Resources
- [Link to full docs]
- [Link to API reference]
- [Link to examples]

---
*Last Updated*: [Date]
*Maintained By*: [@team/owner]
"""

    def _generate_hotfix_process(self, task: WizardTask) -> str:
        """Generate hotfix process documentation"""
        return """# Hotfix Process

## When to Use This Process
- Production is broken or severely degraded
- Customer-facing functionality is impaired
- Security vulnerability needs immediate patch

## Quick Checklist
- [ ] Identify root cause
- [ ] Create hotfix branch from `main`
- [ ] Implement minimal fix
- [ ] Add regression test
- [ ] Get emergency review (15 min timebox)
- [ ] Deploy to staging
- [ ] Smoke test (10 min)
- [ ] Deploy to production
- [ ] Monitor for 1 hour
- [ ] Schedule post-mortem

## Step-by-Step

### 1. Create Hotfix Branch
```bash
git checkout main
git pull origin main
git checkout -b hotfix/ISSUE-123-description
```

### 2. Implement Fix
- **Keep it minimal** - only fix the immediate issue
- **Add logging** - help diagnose if it happens again
- **Add test** - prevent regression

### 3. Get Review
- Tag senior engineer in PR
- Use "HOTFIX" label
- Include in PR description:
  - Root cause
  - Impact
  - Rollback plan

### 4. Deploy
```bash
# Deploy to staging
./deploy.sh staging

# Verify fix
./smoke-test.sh

# Deploy to production
./deploy.sh production

# Monitor
./monitor.sh --duration 1h
```

### 5. Follow Up
- Schedule post-mortem within 24 hours
- Document lessons learned
- Create tickets for long-term fixes

## Rollback Plan
If the hotfix causes issues:
```bash
# Immediate rollback
./rollback.sh production

# Verify system restored
./health-check.sh
```

## Who to Notify
- [ ] On-call engineer
- [ ] Engineering manager
- [ ] Product manager (if customer-facing)
- [ ] Customer support (if customer-facing)

---
*Process Owner*: Engineering Team
*Last Updated*: [Date]
"""

    def _generate_setup_guide(self, task: WizardTask) -> str:
        """Generate setup/installation guide"""
        return """# Setup Guide

## Prerequisites
- [Tool 1]: Version X.X+
- [Tool 2]: Version Y.Y+
- [Access needed]: [Description]

## Installation

### Option 1: Quick Start (Recommended)
```bash
# One-line install
./install.sh
```

### Option 2: Manual Setup
```bash
# Step 1: Clone repository
git clone [repo-url]
cd [repo-name]

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Configure
cp .env.example .env
# Edit .env with your values

# Step 4: Initialize
./init.sh
```

## Configuration
Edit `.env` file:
```bash
# Required
API_KEY=your_key_here
DATABASE_URL=postgres://...

# Optional
LOG_LEVEL=INFO
```

## Verify Installation
```bash
# Run health check
./health-check.sh

# Expected output:
# ✓ Database connected
# ✓ API accessible
# ✓ All services running
```

## Next Steps
1. [Read the quick start guide](link)
2. [Try the tutorial](link)
3. [Join team Slack channel](link)

## Troubleshooting
See [Troubleshooting Guide](link) or ask in #engineering-help

---
*Last Updated*: [Date]
"""

    def _generate_quick_start(self, task: WizardTask, audience: Dict) -> str:
        """Generate quick start guide"""
        return """# Quick Start Guide

## What You'll Learn
In 10 minutes, you'll:
- [Outcome 1]
- [Outcome 2]
- [Outcome 3]

## Before You Start
You'll need:
- [Prerequisite 1]
- [Prerequisite 2]

## Step 1: [Action Name]
[Brief explanation of why this step]

```bash
# Command to run
command_here --with-flags
```

Expected output:
```
Success! [Description of what you should see]
```

## Step 2: [Action Name]
[Brief explanation]

```bash
another_command
```

## Step 3: [Action Name]
[Brief explanation]

```bash
final_command
```

## You're Done!
You should now have [description of end state].

## Next Steps
- [Link to advanced guide]
- [Link to API docs]
- [Link to examples]

## Questions?
- Check [FAQ](link)
- Ask in #team-channel
- Email [support email]

---
*Estimated Time*: 10 minutes
*Difficulty*: {audience['experience'].capitalize()}
*Last Updated*: [Date]
"""

    def _create_handoff_checklist(self, task: WizardTask, audience: Dict) -> str:
        """Create handoff checklist"""
        return """# Documentation Handoff Checklist

- [ ] Documentation reviewed by target audience
- [ ] All code examples tested and working
- [ ] Links verified (no 404s)
- [ ] Screenshots/diagrams up to date
- [ ] "Last Updated" date added
- [ ] Maintainer/owner assigned
- [ ] Added to main README/index
- [ ] Shared in team channel
- [ ] Added to onboarding docs (if relevant)
- [ ] Feedback loop established (how to report issues)
"""

    def _identify_potential_gaps(self, task: WizardTask, doc_type: str) -> List[str]:
        """Proactively identify potential documentation gaps"""
        gaps = []

        # Based on doc type, suggest related docs
        if doc_type == "Setup Guide":
            gaps.append("Consider also creating: Troubleshooting guide for common setup issues")
            gaps.append("Consider also creating: Development environment guide")

        if doc_type == "Hotfix Process":
            gaps.append("Consider also creating: Incident response playbook")
            gaps.append("Consider also creating: Post-mortem template")

        if doc_type == "README":
            gaps.append("Consider also creating: Architecture decision records (ADRs)")
            gaps.append("Consider also creating: API documentation")

        return gaps

    def _format_gaps(self, gaps: List[str]) -> str:
        """Format identified gaps as doc"""
        content = "# Identified Documentation Gaps\n\n"
        content += "The following related documentation should be considered:\n\n"
        for gap in gaps:
            content += f"- {gap}\n"
        return content
