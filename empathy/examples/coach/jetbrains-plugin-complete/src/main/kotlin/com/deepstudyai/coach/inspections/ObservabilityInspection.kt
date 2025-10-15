package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Observability inspection powered by the ObservabilityWizard.
 *
 * Recommends logging, metrics, tracing strategies for production debugging.
 */
class ObservabilityInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "ObservabilityWizard"

    override fun getTask(): String = "Observability review"

    override fun getContext(): String = "Analyze logging, metrics, and tracing implementation"

    override fun getQuickFixFamily(): String = "Coach Observability Fix"

    override fun getDisplayName(): String = "Observability Analysis (ObservabilityWizard)"

    override fun getShortName(): String = "CoachObservability"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
