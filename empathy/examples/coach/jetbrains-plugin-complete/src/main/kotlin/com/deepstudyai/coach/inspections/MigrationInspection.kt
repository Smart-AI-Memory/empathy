package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Migration inspection powered by the MigrationWizard.
 *
 * Assists with framework upgrades, language migrations, dependency updates.
 */
class MigrationInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "MigrationWizard"

    override fun getTask(): String = "Migration analysis"

    override fun getContext(): String = "Identify migration opportunities and issues"

    override fun getQuickFixFamily(): String = "Coach Migration Fix"

    override fun getDisplayName(): String = "Migration Analysis (MigrationWizard)"

    override fun getShortName(): String = "CoachMigration"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
