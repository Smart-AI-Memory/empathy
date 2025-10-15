package com.deepstudyai.coach.actions

import com.deepstudyai.coach.services.AnalysisService
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages

/**
 * Action to analyze the current file with all applicable wizards.
 */
class AnalyzeFileAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val psiFile = e.getData(CommonDataKeys.PSI_FILE) ?: run {
            Messages.showErrorDialog(project, "No file selected", "Coach")
            return
        }

        val language = psiFile.language.displayName
        val analysisService = AnalysisService.getInstance(project)

        // Show progress message
        Messages.showInfoMessage(
            project,
            "Analyzing ${psiFile.name} with Coach wizards...\nThis may take a moment.",
            "Coach Analysis"
        )

        // Run analysis
        analysisService.analyzeWithAllWizards(psiFile, language).thenAccept { results ->
            val message = if (results.isEmpty()) {
                "No issues found in ${psiFile.name}"
            } else {
                buildString {
                    append("Found ${results.size} analysis result(s) for ${psiFile.name}:\n\n")
                    results.take(5).forEach { result ->
                        append("${result.wizard}: ${result.diagnosis}\n")
                    }
                    if (results.size > 5) {
                        append("\n... and ${results.size - 5} more. Check the Coach tool window for details.")
                    }
                }
            }

            Messages.showInfoMessage(project, message, "Coach Analysis Complete")
        }.exceptionally { throwable ->
            Messages.showErrorDialog(
                project,
                "Analysis failed: ${throwable.message}",
                "Coach Error"
            )
            null
        }
    }

    override fun update(e: AnActionEvent) {
        val psiFile = e.getData(CommonDataKeys.PSI_FILE)
        e.presentation.isEnabled = psiFile != null
    }
}
