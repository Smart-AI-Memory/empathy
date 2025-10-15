package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Documentation inspection powered by the DocumentationWizard.
 *
 * Identifies missing docs, suggests improvements, generates API documentation.
 */
class DocumentationInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "DocumentationWizard"

    override fun getTask(): String = "Documentation review"

    override fun getContext(): String = "Identify missing or inadequate documentation"

    override fun getQuickFixFamily(): String = "Coach Documentation Fix"

    override fun getDisplayName(): String = "Documentation Analysis (DocumentationWizard)"

    override fun getShortName(): String = "CoachDocumentation"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
