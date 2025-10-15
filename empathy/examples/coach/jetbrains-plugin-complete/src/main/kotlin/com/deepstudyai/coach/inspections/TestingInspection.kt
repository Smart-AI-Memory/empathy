package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel

/**
 * Testing inspection powered by the TestingWizard.
 *
 * Suggests tests, identifies untested code paths, recommends test strategies.
 */
class TestingInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "TestingWizard"

    override fun getTask(): String = "Test coverage analysis"

    override fun getContext(): String = "Identify untested code and suggest test strategies"

    override fun getQuickFixFamily(): String = "Coach Testing Fix"

    override fun getDisplayName(): String = "Testing Analysis (TestingWizard)"

    override fun getShortName(): String = "CoachTesting"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WEAK_WARNING
}
