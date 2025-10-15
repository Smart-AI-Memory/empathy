package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Compliance inspection powered by the ComplianceWizard.
 *
 * Checks GDPR, HIPAA, PCI-DSS compliance, identifies data privacy issues.
 */
class ComplianceInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "ComplianceWizard"

    override fun getTask(): String = "Compliance audit"

    override fun getContext(): String = "Check for GDPR, HIPAA, PCI-DSS compliance issues"

    override fun getQuickFixFamily(): String = "Coach Compliance Fix"

    override fun getDisplayName(): String = "Compliance Analysis (ComplianceWizard)"

    override fun getShortName(): String = "CoachCompliance"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.ERROR
}
