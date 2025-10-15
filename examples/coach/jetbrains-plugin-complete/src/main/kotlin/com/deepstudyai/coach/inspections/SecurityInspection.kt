package com.deepstudyai.coach.inspections

import com.deepstudyai.coach.lsp.Severity
import com.deepstudyai.coach.services.AnalysisService
import com.deepstudyai.coach.services.CoachSettingsService
import com.intellij.codeInspection.*
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiElementVisitor
import com.intellij.psi.PsiFile

/**
 * Security inspection powered by the SecurityWizard.
 *
 * Detects security vulnerabilities including:
 * - SQL injection
 * - Cross-site scripting (XSS)
 * - Hardcoded secrets
 * - CSRF vulnerabilities
 * - Insecure deserialization
 * - Command injection
 */
class SecurityInspection : LocalInspectionTool() {

    private val log = Logger.getInstance(SecurityInspection::class.java)

    companion object {
        private const val WIZARD_ID = "SecurityWizard"
    }

    override fun buildVisitor(holder: ProblemsHolder, isOnTheFly: Boolean): PsiElementVisitor {
        return object : PsiElementVisitor() {
            override fun visitFile(file: PsiFile) {
                super.visitFile(file)

                // Check if the wizard is enabled
                val settings = service<CoachSettingsService>()
                if (!settings.state.isWizardEnabled(WIZARD_ID)) {
                    return
                }

                // Run security analysis
                val analysisService = AnalysisService.getInstance(file.project)
                val future = analysisService.analyzeWithWizard(
                    psiFile = file,
                    wizardId = WIZARD_ID,
                    role = "developer",
                    task = "Security audit",
                    context = "Check for common security vulnerabilities"
                )

                try {
                    val result = future.get()

                    // Skip if no issues found
                    if (result.severity == Severity.INFO && result.recommendations.isEmpty()) {
                        return
                    }

                    // Create problem descriptor
                    val problemLevel = when (result.severity) {
                        Severity.ERROR -> ProblemHighlightType.ERROR
                        Severity.WARNING -> ProblemHighlightType.WARNING
                        Severity.INFO -> ProblemHighlightType.WEAK_WARNING
                    }

                    // Register the problem
                    holder.registerProblem(
                        file,
                        result.diagnosis,
                        problemLevel,
                        *createQuickFixes(result.recommendations, file.project)
                    )

                } catch (e: Exception) {
                    log.warn("Failed to run security inspection on ${file.name}", e)
                }
            }
        }
    }

    private fun createQuickFixes(recommendations: List<String>, project: Project): Array<LocalQuickFix> {
        return recommendations.take(3).mapIndexed { index, recommendation ->
            object : LocalQuickFix {
                override fun getFamilyName(): String = "Coach Security Fix"

                override fun getName(): String = recommendation.take(100)

                override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
                    // The actual fix implementation would be in specific intention actions
                    // This is a placeholder that shows the recommendation
                    log.info("Applying security fix: $recommendation")
                }
            }
        }.toTypedArray()
    }

    override fun getDisplayName(): String = "Security Analysis (SecurityWizard)"

    override fun getShortName(): String = "CoachSecurity"

    override fun getGroupDisplayName(): String = "Coach"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WARNING

    override fun isEnabledByDefault(): Boolean = true
}
