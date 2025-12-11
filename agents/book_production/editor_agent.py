"""
Editor Agent - Draft Polishing

The quality assurance agent in the book production pipeline. Responsible for:
1. Checking voice consistency across sections
2. Verifying code examples are correct and complete
3. Ensuring structural compliance with chapter template
4. Flagging missing elements
5. Making automated fixes for common issues

Uses Claude Sonnet for fast iteration on rule-based editing.

Key Insight from Experience:
Good editing is systematic, not subjective. We can encode
the rules that make chapters consistent and apply them automatically.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import re
from datetime import datetime
from typing import Any

from .base import SonnetAgent
from .state import AgentPhase, Draft, DraftVersion, EditResult


class EditorAgent(SonnetAgent):
    """
    Polishes drafts for publication quality.

    Model: Claude Sonnet (fast iteration, rule-based)

    Responsibilities:
    - Check voice consistency (authority, not hedging)
    - Verify code correctness (syntax, completeness)
    - Ensure structural compliance (all sections present)
    - Flag missing elements (quotes, exercises, takeaways)
    - Apply automated fixes where possible
    """

    name = "EditorAgent"
    description = "Polishes drafts for publication quality"
    empathy_level = 4

    # Style rules to enforce
    STYLE_RULES = {
        "no_hedging": {
            "patterns": [
                r"\bmight\b",
                r"\bperhaps\b",
                r"\bpossibly\b",
                r"\bcould be\b",
                r"\bseems to\b",
                r"\bappears to\b",
            ],
            "description": "Remove hedging language - state facts confidently",
            "severity": "medium",
        },
        "active_voice": {
            "patterns": [
                r"\bis being\b",
                r"\bwas done\b",
                r"\bwere made\b",
                r"\bhas been\b",
            ],
            "description": "Prefer active voice over passive",
            "severity": "low",
        },
        "code_blocks_labeled": {
            "patterns": [r"```\n"],  # Unlabeled code block
            "description": "All code blocks should have language labels",
            "severity": "high",
        },
    }

    # Required chapter elements
    REQUIRED_ELEMENTS = {
        "opening_quote": {
            "pattern": r'^>\s*"[^"]+"\s*$',
            "description": "Opening quote at start of chapter",
            "location": "start",
        },
        "introduction": {
            "pattern": r"##\s*(Introduction|Overview)",
            "description": "Introduction section",
            "location": "early",
        },
        "what_youll_learn": {
            "pattern": r"\*\*What You'll Learn\*\*|\*\*Learning Objectives\*\*",
            "description": "Learning objectives section",
            "location": "early",
        },
        "key_takeaways": {
            "pattern": r"##\s*Key Takeaways",
            "description": "Key takeaways section",
            "location": "late",
        },
        "try_it_yourself": {
            "pattern": r"##\s*Try It Yourself|##\s*Exercise",
            "description": "Hands-on exercise section",
            "location": "late",
        },
        "next_chapter": {
            "pattern": r"\*\*Next:\*\*|\*\*Next Chapter:\*\*",
            "description": "Navigation to next chapter",
            "location": "end",
        },
    }

    def get_system_prompt(self) -> str:
        """System prompt for editing"""
        return """You are a technical editor specializing in programming books.

Your job is to polish chapter drafts for publication quality.

## Editing Priorities

1. **Voice Consistency**
   - Remove hedging: "might", "perhaps", "possibly" → state facts directly
   - Use active voice: "The system processes" not "is processed by"
   - Maintain authority: "MemDocs stores" not "MemDocs can store"

2. **Code Quality**
   - All code blocks must have language labels (```python, ```javascript)
   - Code must be syntactically correct
   - Comments should explain non-obvious lines
   - Examples should be complete and runnable

3. **Structure Compliance**
   - Opening quote present
   - Introduction with learning objectives
   - 5-7 main sections with consistent formatting
   - Key takeaways (5-6 bullets, start with verbs)
   - Try It Yourself exercise
   - Next chapter navigation

4. **Formatting**
   - Section breaks (---) between major sections
   - Bold for key terms on first use
   - Tables for comparisons
   - Consistent heading levels

When you find issues:
- List them with severity (critical/high/medium/low)
- Provide the fix or suggest improvement
- Note the line/section affected

Focus on making the chapter publication-ready while preserving the author's voice."""

    async def process(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Edit the current draft.

        Args:
            state: Current pipeline state with draft

        Returns:
            Updated state with edited draft
        """
        self.logger.info(
            f"Starting editing for Chapter {state['chapter_number']}: {state['chapter_title']}"
        )

        # Update state
        state = self.add_audit_entry(
            state,
            action="editing_started",
            details={"chapter": state["chapter_number"], "version": state["current_version"]},
        )
        state["current_agent"] = self.name
        state["current_phase"] = AgentPhase.EDITING.value

        draft = state.get("current_draft", "")
        if not draft:
            state["errors"].append("No draft to edit")
            return state

        # Phase 1: Automated checks
        issues = await self._check_all_rules(draft)
        state["editing_issues_found"] = issues

        # Phase 2: Check required elements
        missing_elements = self._check_required_elements(draft)
        for element in missing_elements:
            issues.append(
                {
                    "type": "missing_element",
                    "severity": "high",
                    "description": f"Missing: {element['description']}",
                    "element": element["name"],
                    "auto_fixable": False,
                }
            )

        # Phase 3: Apply automated fixes
        edited_draft, fixes_applied = await self._apply_automated_fixes(draft, issues)

        # Phase 4: LLM-assisted editing for complex issues
        if self._has_complex_issues(issues):
            edited_draft = await self._llm_assisted_edit(edited_draft, issues)

        # Calculate style consistency score
        style_score = self._calculate_style_score(edited_draft, issues)

        # Verify code blocks
        code_verified = self._verify_code_blocks(edited_draft)

        # Create new draft version
        new_version = state["current_version"] + 1
        draft_version = DraftVersion(
            version=new_version,
            content=edited_draft,
            word_count=self.count_words(edited_draft),
            created_at=datetime.now().isoformat(),
            created_by=self.name,
            changes_summary=f"Edited: {len(fixes_applied)} auto-fixes, {len(issues)} issues found",
        )

        # Update state
        state["current_draft"] = edited_draft
        state["draft_versions"].append(draft_version)
        state["current_version"] = new_version
        state["editing_issues_fixed"] = len(fixes_applied)
        state["style_consistency_score"] = style_score
        state["code_verified"] = code_verified

        # Mark phase complete
        completed = list(state.get("completed_phases", []))
        completed.append(AgentPhase.EDITING.value)
        state["completed_phases"] = completed

        # Add audit entry
        state = self.add_audit_entry(
            state,
            action="editing_completed",
            details={
                "issues_found": len(issues),
                "issues_fixed": len(fixes_applied),
                "style_score": style_score,
                "code_verified": code_verified,
                "new_version": new_version,
            },
        )

        self.logger.info(
            f"Editing complete: {len(issues)} issues found, "
            f"{len(fixes_applied)} fixed, style score: {style_score:.2f}"
        )

        return state

    async def edit(self, draft: Draft, chapter_title: str) -> EditResult:
        """
        Standalone edit method for direct use.

        Args:
            draft: Draft to edit
            chapter_title: Chapter title for context

        Returns:
            EditResult with edited draft
        """
        from .state import create_initial_state

        # Create minimal state
        state = create_initial_state(
            chapter_number=0,
            chapter_title=chapter_title,
        )
        state["current_draft"] = draft.content
        state["current_version"] = draft.version
        state["draft_versions"] = []

        # Process
        result_state = await self.process(state)

        return EditResult(
            draft=Draft(
                content=result_state["current_draft"],
                version=result_state["current_version"],
                word_count=self.count_words(result_state["current_draft"]),
                patterns_applied=draft.patterns_applied,
            ),
            issues_found=len(result_state["editing_issues_found"]),
            issues_fixed=result_state["editing_issues_fixed"],
            style_score=result_state["style_consistency_score"],
        )

    async def _check_all_rules(self, draft: str) -> list[dict[str, Any]]:
        """Check draft against all style rules"""
        issues = []

        for rule_name, rule in self.STYLE_RULES.items():
            for pattern in rule["patterns"]:
                matches = list(re.finditer(pattern, draft, re.IGNORECASE | re.MULTILINE))
                for match in matches:
                    # Find line number
                    line_num = draft[: match.start()].count("\n") + 1

                    issues.append(
                        {
                            "type": "style_violation",
                            "rule": rule_name,
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "match": match.group(),
                            "line": line_num,
                            "position": match.start(),
                            "auto_fixable": rule_name == "code_blocks_labeled",
                        }
                    )

        return issues

    def _check_required_elements(self, draft: str) -> list[dict[str, Any]]:
        """Check for required chapter elements"""
        missing = []

        for name, element in self.REQUIRED_ELEMENTS.items():
            if not re.search(element["pattern"], draft, re.MULTILINE | re.IGNORECASE):
                missing.append(
                    {
                        "name": name,
                        "description": element["description"],
                        "location": element["location"],
                    }
                )

        return missing

    async def _apply_automated_fixes(
        self,
        draft: str,
        issues: list[dict],
    ) -> tuple[str, list[dict]]:
        """Apply automated fixes for simple issues"""
        fixes_applied = []
        edited = draft

        # Fix unlabeled code blocks
        unlabeled_pattern = r"```\n"
        if re.search(unlabeled_pattern, edited):
            # Default to python for unlabeled blocks
            edited = re.sub(unlabeled_pattern, "```python\n", edited)
            fixes_applied.append(
                {
                    "type": "code_block_label",
                    "description": "Added python label to unlabeled code blocks",
                }
            )

        # Fix common hedging (simple replacements)
        hedging_fixes = [
            (r"\bmight be able to\b", "can"),
            (r"\bperhaps you could\b", "you can"),
            (r"\bit seems that\b", ""),
        ]

        for pattern, replacement in hedging_fixes:
            if re.search(pattern, edited, re.IGNORECASE):
                edited = re.sub(pattern, replacement, edited, flags=re.IGNORECASE)
                fixes_applied.append(
                    {
                        "type": "hedging_removal",
                        "description": f"Replaced '{pattern}' with '{replacement}'",
                    }
                )

        return edited, fixes_applied

    def _has_complex_issues(self, issues: list[dict]) -> bool:
        """Check if there are issues requiring LLM assistance"""
        critical_count = sum(1 for i in issues if i.get("severity") == "critical")
        high_count = sum(1 for i in issues if i.get("severity") == "high")
        missing_count = sum(1 for i in issues if i.get("type") == "missing_element")

        return critical_count > 0 or high_count > 3 or missing_count > 2

    async def _llm_assisted_edit(
        self,
        draft: str,
        issues: list[dict],
    ) -> str:
        """Use LLM to fix complex issues"""
        # Build issue summary
        issue_summary = "\n".join(
            f"- [{i['severity'].upper()}] {i['description']}"
            for i in issues
            if i.get("severity") in ["critical", "high"]
        )

        prompt = f"""Edit this chapter draft to fix the following issues:

## Issues to Fix
{issue_summary}

## Current Draft
{draft[:8000]}  # Truncate for token limits

## Instructions
1. Fix all listed issues
2. Maintain the author's voice and style
3. Keep all existing content that doesn't have issues
4. Return the complete edited draft

Return ONLY the edited draft, no commentary."""

        try:
            edited = await self.generate(prompt, max_tokens=10000)
            return edited
        except Exception as e:
            self.logger.warning(f"LLM-assisted edit failed: {e}")
            return draft

    def _calculate_style_score(
        self,
        draft: str,
        issues: list[dict],
    ) -> float:
        """Calculate style consistency score (0-1)"""
        # Start with perfect score
        score = 1.0

        # Deduct for issues by severity
        severity_penalties = {
            "critical": 0.15,
            "high": 0.08,
            "medium": 0.03,
            "low": 0.01,
        }

        for issue in issues:
            severity = issue.get("severity", "low")
            score -= severity_penalties.get(severity, 0.01)

        # Check positive indicators
        positive_indicators = [
            (r"```\w+\n", 0.02),  # Labeled code blocks
            (r"\*\*[^*]+\*\*", 0.01),  # Bold terms
            (r"^##\s+", 0.01),  # Proper headings
            (r"^---$", 0.01),  # Section breaks
        ]

        for pattern, bonus in positive_indicators:
            matches = len(re.findall(pattern, draft, re.MULTILINE))
            score += min(bonus * matches, 0.05)  # Cap bonus

        return max(0.0, min(1.0, score))

    def _verify_code_blocks(self, draft: str) -> bool:
        """Verify code blocks are syntactically valid"""
        code_pattern = r"```(\w+)\n(.*?)```"
        blocks = re.findall(code_pattern, draft, re.DOTALL)

        for language, code in blocks:
            if language == "python":
                try:
                    compile(code, "<string>", "exec")
                except SyntaxError:
                    return False

        return True
