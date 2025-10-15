package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel
import com.intellij.psi.PsiFile

/**
 * API inspection powered by the APIWizard.
 *
 * Reviews API design, suggests REST/GraphQL best practices, validates OpenAPI specs.
 */
class APIInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "APIWizard"

    override fun getTask(): String = "API design review"

    override fun getContext(): String = "Review API endpoints and design patterns"

    override fun getQuickFixFamily(): String = "Coach API Fix"

    override fun isApplicable(file: PsiFile): Boolean {
        val fileName = file.name.lowercase()
        val text = file.text.lowercase()
        // Check for files that typically contain API code
        return fileName.contains("controller") ||
                fileName.contains("handler") ||
                fileName.contains("api") ||
                fileName.contains("route") ||
                fileName.endsWith(".yaml") && (text.contains("openapi") || text.contains("swagger")) ||
                text.contains(Regex("@(Get|Post|Put|Delete|Patch)Mapping"))
    }

    override fun getDisplayName(): String = "API Design Analysis (APIWizard)"

    override fun getShortName(): String = "CoachAPI"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WARNING
}
