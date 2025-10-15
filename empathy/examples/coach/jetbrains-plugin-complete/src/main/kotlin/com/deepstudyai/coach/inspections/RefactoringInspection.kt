package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Refactoring inspection powered by the RefactoringWizard.
 *
 * Identifies code smells, suggests refactoring opportunities, improves maintainability.
 */
class RefactoringInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "RefactoringWizard"

    override fun getTask(): String = "Code quality analysis"

    override fun getContext(): String = "Identify code smells and refactoring opportunities"

    override fun getQuickFixFamily(): String = "Coach Refactoring Fix"

    override fun getDisplayName(): String = "Refactoring Analysis (RefactoringWizard)"

    override fun getShortName(): String = "CoachRefactoring"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
