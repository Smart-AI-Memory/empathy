package com.deepstudyai.coach.inspections

import com.intellij.codeInspection.HighlightDisplayLevel
import com.intellij.psi.PsiFile

/**
 * CI/CD inspection powered by the CICDWizard.
 *
 * Optimizes pipelines, suggests deployment strategies, reviews Docker/K8s configs.
 */
class CICDInspection : BaseCoachInspection() {

    override fun getWizardId(): String = "CICDWizard"

    override fun getTask(): String = "CI/CD pipeline review"

    override fun getContext(): String = "Optimize pipelines and deployment configurations"

    override fun getQuickFixFamily(): String = "Coach CI/CD Fix"

    override fun isApplicable(file: PsiFile): Boolean {
        val fileName = file.name.lowercase()
        // Check for CI/CD and deployment configuration files
        return fileName.endsWith(".yml") ||
                fileName.endsWith(".yaml") ||
                fileName == "dockerfile" ||
                fileName == "jenkinsfile" ||
                fileName.contains("docker-compose") ||
                fileName.contains(".github/workflows") ||
                fileName.contains(".gitlab-ci") ||
                fileName.contains("azure-pipelines")
    }

    override fun getDisplayName(): String = "CI/CD Analysis (CICDWizard)"

    override fun getShortName(): String = "CoachCICD"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WARNING
}
