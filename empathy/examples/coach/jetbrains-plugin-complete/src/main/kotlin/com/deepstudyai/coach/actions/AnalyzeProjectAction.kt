package com.deepstudyai.coach.actions

import com.deepstudyai.coach.services.AnalysisService
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.progress.ProgressIndicator
import com.intellij.openapi.progress.ProgressManager
import com.intellij.openapi.progress.Task
import com.intellij.openapi.ui.Messages

/**
 * Action to analyze the entire project with all enabled wizards.
 */
class AnalyzeProjectAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return

        ProgressManager.getInstance().run(object : Task.Backgroundable(
            project,
            "Analyzing Project with Coach",
            true
        ) {
            override fun run(indicator: ProgressIndicator) {
                indicator.isIndeterminate = false
                indicator.fraction = 0.0

                val analysisService = AnalysisService.getInstance(project)

                val job = analysisService.analyzeProject { fileName, current, total ->
                    indicator.text = "Analyzing: $fileName"
                    indicator.fraction = current.toDouble() / total
                }

                // Wait for completion
                while (!job.isCompleted && !indicator.isCanceled) {
                    Thread.sleep(100)
                }

                if (indicator.isCanceled) {
                    analysisService.cancelAnalysis()
                }
            }

            override fun onSuccess() {
                val analysisService = AnalysisService.getInstance(project)
                val stats = analysisService.getStatistics()

                val message = buildString {
                    append("Project analysis complete!\n\n")
                    append("Total analyses: ${stats.totalAnalyses}\n")
                    append("Errors: ${stats.errors}\n")
                    append("Warnings: ${stats.warnings}\n")
                    append("Info: ${stats.infos}\n\n")
                    append("Check the Coach tool window for detailed results.")
                }

                Messages.showInfoMessage(project, message, "Coach Analysis Complete")
            }

            override fun onThrowable(error: Throwable) {
                Messages.showErrorDialog(
                    project,
                    "Project analysis failed: ${error.message}",
                    "Coach Error"
                )
            }
        })
    }

    override fun update(e: AnActionEvent) {
        e.presentation.isEnabled = e.project != null
    }
}
