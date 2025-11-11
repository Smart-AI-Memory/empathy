"""
Retrospective Wizard

Extracts lessons learned, proposes process improvements, recognizes contributions.
Uses Empathy Framework Level 2 (Guided) for facilitation and Level 4 (Anticipatory)
to prevent future team friction.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
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


class RetrospectiveWizard(BaseWizard):
    """
    Wizard for team retrospectives and process improvements

    Uses:
    - Level 2: Guide structured retrospective facilitation
    - Level 3: Proactively identify patterns in team dynamics
    - Level 4: Anticipate team friction and prevent burnout
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a retrospective task"""
        retro_keywords = [
            "retrospective",
            "retro",
            "sprint review",
            "lessons learned",
            "postmortem",
            "post-mortem",
            "process improvement",
            "team feedback",
            "what went well",
            "morale",
        ]

        task_lower = (task.task + " " + task.context).lower()
        matches = sum(1 for keyword in retro_keywords if keyword in task_lower)

        return min(matches / 2.0, 1.0)

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute retrospective workflow"""

        # Step 1: Assess team context
        self._extract_constraints(task)
        team_context = self._assess_team_context(task)

        # Step 2: Choose retrospective format
        retro_format = self._choose_retro_format(task, team_context)

        # Step 3: Generate retrospective structure
        retro_structure = self._generate_retro_structure(retro_format)

        # Step 4: Identify patterns (Level 3: Proactive)
        patterns = self._identify_team_patterns(task, team_context)

        # Step 5: Generate action items
        action_items = self._generate_action_items(task, patterns)

        # Step 6: Assess team health
        team_health = self._assess_team_health(task, team_context)

        # Step 7: Create diagnosis
        diagnosis = self._create_diagnosis(team_context, patterns)

        # Step 8: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc", title=f"{retro_format} Retrospective Template", content=retro_structure
            ),
            WizardArtifact(
                type="doc", title="Team Patterns Analysis", content=self._format_patterns(patterns)
            ),
            WizardArtifact(
                type="doc", title="Action Items", content=self._format_action_items(action_items)
            ),
            WizardArtifact(type="doc", title="Team Health Dashboard", content=team_health),
        ]

        # Step 9: Create plan
        plan = [
            "Schedule 60-90 minute retrospective meeting",
            "Share retrospective format with team beforehand",
            "Facilitate discussion using chosen format",
            "Document insights and action items",
            "Assign owners to action items",
            "Schedule follow-up to review progress",
        ]

        # Step 10: Generate next actions
        next_actions = [
            "Send calendar invite with retro format",
            "Create shared doc for async input",
            "Facilitate retrospective meeting",
            "Document outcomes and share with team",
            "Add action items to next sprint planning",
        ]

        # Add anticipatory actions
        anticipatory_actions = self._generate_anticipatory_actions(task)
        next_actions.extend(anticipatory_actions)

        # Step 11: Create handoffs
        handoffs = [
            WizardHandoff(
                owner="team_lead", what="Facilitate retrospective meeting", when="Within 2 weeks"
            ),
            WizardHandoff(owner="team", what="Implement agreed action items", when="Next sprint"),
        ]

        # Step 12: Assess risks
        risks = [
            WizardRisk(
                risk="Retrospective becomes blame session",
                mitigation="Set ground rules, focus on systems not people, use 'I' statements",
                severity="medium",
            ),
            WizardRisk(
                risk="Action items never implemented",
                mitigation="Assign clear owners, add to sprint backlog, review in next retro",
                severity="medium",
            ),
            WizardRisk(
                risk="Team disengagement if no improvements seen",
                mitigation="Start with small wins, celebrate successes, show tangible changes",
                severity="low",
            ),
        ]

        # Step 13: Empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered team dynamics and {team_context['team_size']} team members' perspectives",
            emotional=f"Acknowledged {team_context['morale']} morale and {len(patterns)} identified patterns",
            anticipatory=f"Provided {len(action_items)} proactive improvements to prevent future friction",
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

    def _assess_team_context(self, task: WizardTask) -> dict[str, Any]:
        """Assess team context"""
        context_lower = task.context.lower()

        # Estimate team size
        team_size = "small (3-7)"
        if "large team" in context_lower or "10" in context_lower:
            team_size = "large (10+)"
        elif "medium" in context_lower:
            team_size = "medium (8-12)"

        # Assess morale
        morale = "normal"
        if any(
            word in context_lower for word in ["stressed", "burnout", "overworked", "frustrated"]
        ):
            morale = "low"
        elif any(word in context_lower for word in ["great", "excellent", "motivated"]):
            morale = "high"

        # Detect issues
        issues = []
        if "communication" in context_lower:
            issues.append("communication")
        if "deadline" in context_lower or "rush" in context_lower:
            issues.append("timeline_pressure")
        if "conflict" in context_lower or "disagreement" in context_lower:
            issues.append("team_conflict")
        if "technical debt" in context_lower:
            issues.append("technical_debt")

        return {"team_size": team_size, "morale": morale, "issues": issues}

    def _choose_retro_format(self, task: WizardTask, team_context: dict) -> str:
        """Choose appropriate retrospective format"""
        # Choose based on team context
        if team_context["morale"] == "low":
            return "Mad Sad Glad"  # Good for processing emotions
        elif "timeline_pressure" in team_context["issues"]:
            return "Start Stop Continue"  # Good for quick process changes
        elif team_context["team_size"].startswith("large"):
            return "4Ls (Liked, Learned, Lacked, Longed For)"  # Scalable format
        else:
            return "What Went Well / What Didn't / Action Items"  # Classic format

    def _generate_retro_structure(self, retro_format: str) -> str:
        """Generate retrospective meeting structure"""
        formats = {
            "Mad Sad Glad": self._mad_sad_glad_format(),
            "Start Stop Continue": self._start_stop_continue_format(),
            "4Ls (Liked, Learned, Lacked, Longed For)": self._four_ls_format(),
            "What Went Well / What Didn't / Action Items": self._classic_format(),
        }

        return formats.get(retro_format, self._classic_format())

    def _mad_sad_glad_format(self) -> str:
        return """# Mad Sad Glad Retrospective

## Agenda (90 minutes)
1. **Set the stage** (5 min) - Ground rules, psychological safety
2. **Gather data** (20 min) - Silent brainstorming on sticky notes
3. **Generate insights** (30 min) - Group and discuss themes
4. **Decide what to do** (25 min) - Action items with owners
5. **Close** (10 min) - Appreciations and next steps

## Format

### Mad 😠 (What frustrated us?)
Post sticky notes about things that made the team angry or frustrated.

Examples:
- Unclear requirements
- Production incidents
- Blocked by dependencies

### Sad 😢 (What disappointed us?)
Post sticky notes about things that were disappointing.

Examples:
- Missed deadline
- Feature cut from release
- Team member left

### Glad 😊 (What went well?)
Post sticky notes about positive experiences.

Examples:
- Successful launch
- Great collaboration
- Solved hard problem

## Discussion Questions
- What patterns do we see?
- What's within our control to change?
- What should we try differently next sprint?

## Action Items Template
- [ ] Action: [Description]
  - Owner: [Name]
  - Due: [Date]
  - Success measure: [How we'll know it worked]
"""

    def _start_stop_continue_format(self) -> str:
        return """# Start Stop Continue Retrospective

## Agenda (60 minutes)
1. **Set the stage** (5 min)
2. **Brainstorm** (15 min)
3. **Discuss and prioritize** (25 min)
4. **Action items** (10 min)
5. **Close** (5 min)

## Format

### START 🚀 (What should we start doing?)
Ideas for new practices or experiments.

Examples:
- Start doing daily standups
- Start using feature flags
- Start pairing on complex features

### STOP 🛑 (What should we stop doing?)
Things that aren't working or adding value.

Examples:
- Stop long email threads (use Slack)
- Stop skipping code reviews
- Stop accepting undefined requirements

### CONTINUE ✅ (What should we keep doing?)
Things that are working well.

Examples:
- Continue weekly knowledge shares
- Continue automated testing
- Continue celebrating wins

## Prioritization
Vote on top 3 items per category.
Focus on high-impact, low-effort changes first.

## Action Items
For each selected item:
- [ ] What: [Specific action]
- [ ] Who: [Owner]
- [ ] When: [Timeline]
- [ ] How we'll measure success: [Metric]
"""

    def _four_ls_format(self) -> str:
        return """# 4Ls Retrospective

## Agenda (90 minutes)
1. **Introduction** (5 min)
2. **Individual reflection** (10 min)
3. **Share and group** (30 min)
4. **Discussion** (30 min)
5. **Action planning** (15 min)

## Format

### LIKED 👍 (What did you like?)
Positive experiences and wins.

### LEARNED 📚 (What did you learn?)
New skills, insights, or knowledge gained.

### LACKED 🤔 (What was missing?)
Resources, support, or information we needed.

### LONGED FOR 💭 (What did you wish for?)
Aspirations and desired changes.

## Facilitation Tips
- Give everyone 2 minutes to share per category
- Group similar themes together
- Focus discussion on "Lacked" and "Longed For" for action items

## Action Items
Convert "Lacked" and "Longed For" into concrete actions:
- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3
"""

    def _classic_format(self) -> str:
        return """# Retrospective: What Went Well / What Didn't / Action Items

## Agenda (75 minutes)
1. **Check-in** (5 min)
2. **What went well** (20 min)
3. **What didn't go well** (25 min)
4. **Action items** (20 min)
5. **Appreciations** (5 min)

## Part 1: What Went Well? ✅
Celebrate successes and wins.

Discussion questions:
- What are we proud of?
- What should we do more of?
- Who helped make this possible?

## Part 2: What Didn't Go Well? ⚠️
Identify challenges and problems.

Discussion questions:
- What slowed us down?
- What should we do differently?
- What needs to change?

**Ground rules**:
- Focus on systems, not people
- Assume positive intent
- Be specific with examples

## Part 3: Action Items 🎯
Convert insights into concrete actions.

Template:
- [ ] **Action**: [What we'll do]
  - **Owner**: [Who's responsible]
  - **Timeline**: [When it'll be done]
  - **Success criteria**: [How we'll know it worked]

## Part 4: Appreciations 💙
Recognize individual contributions.
"""

    def _identify_team_patterns(self, task: WizardTask, team_context: dict) -> list[dict[str, str]]:
        """Identify patterns in team dynamics"""
        patterns = []

        issues = team_context["issues"]

        if "communication" in issues:
            patterns.append(
                {
                    "pattern": "Communication gaps",
                    "impact": "Misalignment, rework, frustration",
                    "root_cause": "Async-first culture, timezone differences, or unclear channels",
                    "suggestion": "Daily standups, use of project management tools, clear ownership",
                }
            )

        if "timeline_pressure" in issues:
            patterns.append(
                {
                    "pattern": "Chronic deadline pressure",
                    "impact": "Burnout, technical debt, quality issues",
                    "root_cause": "Underestimation, scope creep, or external pressure",
                    "suggestion": "Better estimation, buffer time, say no to scope changes",
                }
            )

        if "team_conflict" in issues:
            patterns.append(
                {
                    "pattern": "Team conflict or disagreement",
                    "impact": "Slow decision-making, low morale, attrition risk",
                    "root_cause": "Unclear roles, different values, or lack of psychological safety",
                    "suggestion": "Team charter, conflict resolution process, 1-on-1s",
                }
            )

        if "technical_debt" in issues:
            patterns.append(
                {
                    "pattern": "Accumulating technical debt",
                    "impact": "Slower velocity, more bugs, developer frustration",
                    "root_cause": "Pressure to ship, lack of refactoring time",
                    "suggestion": "Dedicated refactoring time, tech debt tracking, quality metrics",
                }
            )

        # Generic patterns
        if not patterns:
            patterns = [
                {
                    "pattern": "Room for process improvement",
                    "impact": "Potential for increased efficiency",
                    "root_cause": "Normal team evolution",
                    "suggestion": "Regular retrospectives to identify specific areas",
                }
            ]

        return patterns

    def _generate_action_items(
        self, task: WizardTask, patterns: list[dict]
    ) -> list[dict[str, str]]:
        """Generate action items from patterns"""
        actions = []

        for pattern in patterns[:3]:  # Top 3 patterns
            actions.append(
                {
                    "action": pattern["suggestion"],
                    "owner": "Team Lead",
                    "timeline": "Next sprint",
                    "success_criteria": f"Reduced {pattern['pattern'].lower()}",
                }
            )

        return actions

    def _assess_team_health(self, task: WizardTask, team_context: dict) -> str:
        """Assess overall team health"""
        return f"""# Team Health Dashboard

## Overall Status: {team_context['morale'].upper()}

## Metrics

### Team Size
{team_context['team_size']}

### Morale
{team_context['morale']}

### Identified Issues
{chr(10).join(f"- {issue.replace('_', ' ').title()}" for issue in team_context['issues']) if team_context['issues'] else "- No major issues identified"}

## Recommendations
1. Continue regular retrospectives (every 2 weeks)
2. Focus on psychological safety
3. Celebrate small wins
4. Address blockers quickly
5. Maintain work-life balance

## Warning Signs to Watch
- [ ] Team members working excessive overtime
- [ ] Increased conflict or tension
- [ ] Declining code review participation
- [ ] Missed sprint commitments repeatedly
- [ ] Team member departures

---
*Assessment Date*: [Current Date]
"""

    def _create_diagnosis(self, team_context: dict, patterns: list[dict]) -> str:
        """Create diagnosis"""
        return f"Team retrospective needed for {team_context['team_size']} team with {team_context['morale']} morale; {len(patterns)} improvement patterns identified"

    def _format_patterns(self, patterns: list[dict]) -> str:
        """Format patterns as documentation"""
        content = "# Team Patterns Analysis\n\n"

        for i, pattern in enumerate(patterns, 1):
            content += f"## Pattern {i}: {pattern['pattern']}\n\n"
            content += f"**Impact**: {pattern['impact']}\n\n"
            content += f"**Root Cause**: {pattern['root_cause']}\n\n"
            content += f"**Suggestion**: {pattern['suggestion']}\n\n"
            content += "---\n\n"

        return content

    def _format_action_items(self, actions: list[dict]) -> str:
        """Format action items"""
        content = "# Retrospective Action Items\n\n"

        for i, action in enumerate(actions, 1):
            content += f"## Action {i}\n\n"
            content += f"- [ ] **Action**: {action['action']}\n"
            content += f"- **Owner**: {action['owner']}\n"
            content += f"- **Timeline**: {action['timeline']}\n"
            content += f"- **Success Criteria**: {action['success_criteria']}\n\n"

        return content
