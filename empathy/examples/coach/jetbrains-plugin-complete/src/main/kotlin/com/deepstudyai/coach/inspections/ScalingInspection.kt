package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Scaling inspection powered by the ScalingWizard.
 *
 * Predicts scaling bottlenecks, suggests architecture improvements for high load.
 */
class ScalingInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "ScalingWizard"

    override fun getTask(): String = "Scaling analysis"

    override fun getContext(): String = "Predict scaling bottlenecks and suggest improvements"

    override fun getQuickFixFamily(): String = "Coach Scaling Fix"

    override fun getDisplayName(): String = "Scaling Analysis (ScalingWizard)"

    override fun getShortName(): String = "CoachScaling"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WARNING
}
