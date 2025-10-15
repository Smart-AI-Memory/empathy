package com.deepstudyai.coach.actions

import com.deepstudyai.coach.services.AnalysisService
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages

/**
 * Action to get Level 4 predictions for the current file.
 */
class Level4PredictionAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val psiFile = e.getData(CommonDataKeys.PSI_FILE) ?: run {
            Messages.showErrorDialog(project, "No file selected", "Coach Level 4 Predictions")
            return
        }

        Messages.showInfoMessage(
            project,
            "Analyzing ${psiFile.name} for Level 4 predictions...\nThis uses AI to predict future issues.",
            "Coach Level 4 Predictions"
        )

        val analysisService = AnalysisService.getInstance(project)

        analysisService.getPredictions(psiFile, timeframe = 60).thenAccept { predictions ->
            if (predictions.isEmpty()) {
                Messages.showInfoMessage(
                    project,
                    "No future issues predicted for ${psiFile.name}.\nYour code looks good for the next 60 days!",
                    "Coach Level 4 Predictions"
                )
                return@thenAccept
            }

            val message = buildString {
                append("Level 4 Predictions for ${psiFile.name}\n")
                append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

                predictions.sortedByDescending { it.confidence }.forEach { prediction ->
                    val icon = when (prediction.severity) {
                        com.deepstudyai.coach.lsp.Severity.ERROR -> "🔴"
                        com.deepstudyai.coach.lsp.Severity.WARNING -> "🟡"
                        com.deepstudyai.coach.lsp.Severity.INFO -> "🔵"
                    }

                    append("$icon ${prediction.issue}\n")
                    append("   Timeframe: ~${prediction.timeframe} days\n")
                    append("   Confidence: ${(prediction.confidence * 100).toInt()}%\n\n")
                    append("   Impact:\n   ${prediction.impact}\n\n")
                    append("   Preventive Action:\n   ${prediction.preventiveAction}\n\n")
                    append("   ────────────────────────────────────────────\n\n")
                }

                append("\nThese are AI predictions based on code patterns and growth trends.\n")
                append("Consider addressing high-confidence predictions proactively.")
            }

            Messages.showInfoMessage(project, message, "Level 4 Predictions")
        }.exceptionally { throwable ->
            Messages.showErrorDialog(
                project,
                "Level 4 prediction failed: ${throwable.message}",
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
