package com.smartaimemory.plugin.actions

import com.intellij.notification.NotificationGroupManager
import com.intellij.notification.NotificationType
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.progress.ProgressIndicator
import com.intellij.openapi.progress.ProgressManager
import com.intellij.openapi.progress.Task
import com.smartaimemory.plugin.services.MemDocsService

/**
 * Context menu action: "Analyze with Empathy Framework"
 */
class AnalyzeFileAction : AnAction("Analyze with Empathy Framework") {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val file = e.getData(CommonDataKeys.VIRTUAL_FILE) ?: return

        val memDocsService = project.getService(MemDocsService::class.java)

        ProgressManager.getInstance().run(object : Task.Backgroundable(
            project,
            "Analyzing ${file.name} with Empathy Framework...",
            true
        ) {
            override fun run(indicator: ProgressIndicator) {
                indicator.text = "Reading MemDocs analysis..."
                indicator.fraction = 0.5

                // Try to load existing analysis
                val analysis = memDocsService.getAnalysis(file.path)

                indicator.fraction = 1.0

                if (analysis != null) {
                    showSuccessNotification(
                        project,
                        "Analysis loaded for ${file.name}",
                        "${analysis.issues.size} issues, ${analysis.predictions.size} predictions found"
                    )
                } else {
                    showWarningNotification(
                        project,
                        "No analysis found for ${file.name}",
                        "Run 'python -m memdocs.workflows.empathy_sync --file ${file.path}' first"
                    )
                }
            }
        })
    }

    override fun update(e: AnActionEvent) {
        val file = e.getData(CommonDataKeys.VIRTUAL_FILE)
        e.presentation.isEnabledAndVisible = file != null && isSupportedLanguage(file.extension)
    }

    private fun isSupportedLanguage(extension: String?): Boolean {
        return extension in listOf("py", "js", "ts", "java", "kt", "go", "rs")
    }

    private fun showSuccessNotification(project: com.intellij.openapi.project.Project, title: String, content: String) {
        NotificationGroupManager.getInstance()
            .getNotificationGroup("SmartAI Memory")
            .createNotification(title, content, NotificationType.INFORMATION)
            .notify(project)
    }

    private fun showWarningNotification(project: com.intellij.openapi.project.Project, title: String, content: String) {
        NotificationGroupManager.getInstance()
            .getNotificationGroup("SmartAI Memory")
            .createNotification(title, content, NotificationType.WARNING)
            .notify(project)
    }
}
