package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Localization inspection powered by the LocalizationWizard.
 *
 * Detects hardcoded strings, suggests i18n strategies, validates translations.
 */
class LocalizationInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "LocalizationWizard"

    override fun getTask(): String = "Localization review"

    override fun getContext(): String = "Identify hardcoded strings and i18n issues"

    override fun getQuickFixFamily(): String = "Coach Localization Fix"

    override fun getDisplayName(): String = "Localization Analysis (LocalizationWizard)"

    override fun getShortName(): String = "CoachLocalization"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
