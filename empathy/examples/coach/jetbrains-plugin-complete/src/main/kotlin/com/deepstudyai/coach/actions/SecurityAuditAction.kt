package com.deepstudyai.coach.actions

import com.deepstudyai.coach.services.AnalysisService
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages

/**
 * Action to run a security audit on the current file.
 */
class SecurityAuditAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val psiFile = e.getData(CommonDataKeys.PSI_FILE) ?: run {
            Messages.showErrorDialog(project, "No file selected", "Coach Security Audit")
            return
        }

        val analysisService = AnalysisService.getInstance(project)

        Messages.showInfoMessage(
            project,
            "Running security audit on ${psiFile.name}...",
            "Coach Security Audit"
        )

        analysisService.analyzeWithWizard(
            psiFile = psiFile,
            wizardId = "SecurityWizard",
            role = "security_engineer",
            task = "Comprehensive security audit",
            context = "Check for all common security vulnerabilities"
        ).thenAccept { result ->
            val message = buildString {
                append("Security Audit Results for ${psiFile.name}\n\n")
                append("Severity: ${result.severity}\n\n")
                append("Diagnosis:\n${result.diagnosis}\n\n")
                if (result.recommendations.isNotEmpty()) {
                    append("Recommendations:\n")
                    result.recommendations.forEach { rec ->
                        append("• $rec\n")
                    }
                }
            }

            Messages.showInfoMessage(project, message, "Security Audit Complete")
        }.exceptionally { throwable ->
            Messages.showErrorDialog(
                project,
                "Security audit failed: ${throwable.message}",
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
