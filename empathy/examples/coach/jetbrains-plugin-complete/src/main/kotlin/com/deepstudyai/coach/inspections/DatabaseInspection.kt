package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel
import com.intellij.psi.PsiFile

/**
 * Database inspection powered by the DatabaseWizard.
 *
 * Optimizes queries, suggests indexes, detects schema issues.
 */
class DatabaseInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "DatabaseWizard"

    override fun getTask(): String = "Database optimization"

    override fun getContext(): String = "Analyze database queries and schema"

    override fun getQuickFixFamily(): String = "Coach Database Fix"

    override fun isApplicable(file: PsiFile): Boolean {
        val fileName = file.name.lowercase()
        // Check for files that typically contain database code
        return fileName.endsWith(".sql") ||
                fileName.contains("repository") ||
                fileName.contains("dao") ||
                file.text.contains(Regex("(SELECT|INSERT|UPDATE|DELETE)\\s", RegexOption.IGNORE_CASE))
    }

    override fun getDisplayName(): String = "Database Analysis (DatabaseWizard)"

    override fun getShortName(): String = "CoachDatabase"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WARNING
}
