package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Debugging inspection powered by the DebuggingWizard.
 *
 * Helps debug complex issues by analyzing stack traces, logs, and runtime behavior.
 */
class DebuggingInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "DebuggingWizard"

    override fun getTask(): String = "Debug assistance"

    override fun getContext(): String = "Analyze potential runtime issues and debugging opportunities"

    override fun getQuickFixFamily(): String = "Coach Debugging Fix"

    override fun getDisplayName(): String = "Debugging Analysis (DebuggingWizard)"

    override fun getShortName(): String = "CoachDebugging"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
