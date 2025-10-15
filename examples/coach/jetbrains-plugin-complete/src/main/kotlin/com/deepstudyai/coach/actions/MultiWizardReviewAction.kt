package com.deepstudyai.coach.actions

import com.deepstudyai.coach.services.AnalysisService
import com.deepstudyai.coach.services.WizardRegistry
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages

/**
 * Action to run multi-wizard collaborative review.
 */
class MultiWizardReviewAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val psiFile = e.getData(CommonDataKeys.PSI_FILE) ?: run {
            Messages.showErrorDialog(project, "No file selected", "Coach Multi-Wizard Review")
            return
        }

        // Detect scenario based on file content
        val scenario = detectScenario(psiFile.text, psiFile.name)

        val wizardRegistry = WizardRegistry.getInstance(project)
        val wizards = wizardRegistry.getCollaborationWizards(scenario)

        if (wizards.isEmpty()) {
            Messages.showInfoMessage(
                project,
                "No wizard collaboration scenario detected for this file.",
                "Coach Multi-Wizard Review"
            )
            return
        }

        Messages.showInfoMessage(
            project,
            "Running multi-wizard review ($scenario) on ${psiFile.name}...\nWizards: ${wizards.joinToString(", ")}",
            "Coach Multi-Wizard Review"
        )

        val analysisService = AnalysisService.getInstance(project)

        analysisService.multiWizardAnalysis(
            psiFile = psiFile,
            wizards = wizards,
            scenario = scenario,
            context = "Collaborative review with multiple perspectives"
        ).thenAccept { result ->
            val message = buildString {
                append("Multi-Wizard Review Complete\n\n")
                append("Scenario: ${result.scenario}\n")
                append("Wizards: ${result.wizards.joinToString(", ")}\n\n")

                if (result.collaboration.isNotEmpty()) {
                    append("Collaboration Insights:\n")
                    result.collaboration.forEach { collab ->
                        append("• [${collab.wizards.joinToString("+")}] ${collab.insight}\n")
                    }
                    append("\n")
                }

                append("Summary:\n${result.summary}\n\n")
                append("Check the Coach tool window for individual wizard results.")
            }

            Messages.showInfoMessage(project, message, "Multi-Wizard Review Complete")
        }.exceptionally { throwable ->
            Messages.showErrorDialog(
                project,
                "Multi-wizard review failed: ${throwable.message}",
                "Coach Error"
            )
            null
        }
    }

    private fun detectScenario(text: String, fileName: String): String {
        val lowerText = text.lowercase()
        val lowerFileName = fileName.lowercase()

        return when {
            lowerText.contains("payment") || lowerText.contains("stripe") || lowerText.contains("paypal") -> "payment"
            lowerText.contains("authentication") || lowerText.contains("login") || lowerText.contains("oauth") -> "authentication"
            lowerFileName.contains("controller") || lowerFileName.contains("api") || lowerFileName.contains("route") -> "api"
            lowerText.contains("select") || lowerText.contains("insert") || lowerFileName.contains("repository") -> "database"
            lowerFileName.contains(".html") || lowerFileName.contains(".jsx") || lowerFileName.contains(".tsx") -> "frontend"
            lowerFileName.contains("docker") || lowerFileName.contains("jenkins") || lowerFileName.contains(".yml") -> "deployment"
            lowerText.contains("migration") || lowerText.contains("upgrade") -> "migration"
            else -> "general"
        }
    }

    override fun update(e: AnActionEvent) {
        val psiFile = e.getData(CommonDataKeys.PSI_FILE)
        e.presentation.isEnabled = psiFile != null
    }
}
