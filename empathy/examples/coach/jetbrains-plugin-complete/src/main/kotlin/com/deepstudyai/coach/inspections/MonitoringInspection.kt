package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Monitoring inspection powered by the MonitoringWizard.
 *
 * Reviews alerting strategies, suggests SLOs/SLIs, identifies monitoring gaps.
 */
class MonitoringInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "MonitoringWizard"

    override fun getTask(): String = "Monitoring review"

    override fun getContext(): String = "Analyze monitoring, alerting, and SLO/SLI implementation"

    override fun getQuickFixFamily(): String = "Coach Monitoring Fix"

    override fun getDisplayName(): String = "Monitoring Analysis (MonitoringWizard)"

    override fun getShortName(): String = "CoachMonitoring"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
