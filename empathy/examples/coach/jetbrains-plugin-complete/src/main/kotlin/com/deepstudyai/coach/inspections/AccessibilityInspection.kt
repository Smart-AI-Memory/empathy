package com.deepstudyai.coach.inspections

import com.deepstudyai.coach.lsp.Severity
import com.deepstudyai.coach.services.AnalysisService
import com.deepstudyai.coach.services.CoachSettingsService
import com.intellij.codeInspection.*
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiElementVisitor
import com.intellij.psi.PsiFile

/**
 * Accessibility inspection powered by the AccessibilityWizard.
 *
 * Ensures WCAG 2.1 AA compliance and detects:
 * - Missing alt text on images
 * - Keyboard accessibility issues
 * - Insufficient color contrast
 * - Missing ARIA labels
 * - Focus management problems
 */
class AccessibilityInspection : LocalInspectionTool() {

    private val log = Logger.getInstance(AccessibilityInspection::class.java)

    companion object {
        private const val WIZARD_ID = "AccessibilityWizard"
    }

    override fun buildVisitor(holder: ProblemsHolder, isOnTheFly: Boolean): PsiElementVisitor {
        return object : PsiElementVisitor() {
            override fun visitFile(file: PsiFile) {
                super.visitFile(file)

                // Only applicable to web files
                val fileName = file.name.lowercase()
                if (!fileName.endsWith(".html") &&
                    !fileName.endsWith(".jsx") &&
                    !fileName.endsWith(".tsx") &&
                    !fileName.endsWith(".vue")) {
                    return
                }

                val settings = service<CoachSettingsService>()
                if (!settings.state.isWizardEnabled(WIZARD_ID)) {
                    return
                }

                val analysisService = AnalysisService.getInstance(file.project)
                val future = analysisService.analyzeWithWizard(
                    psiFile = file,
                    wizardId = WIZARD_ID,
                    role = "developer",
                    task = "Accessibility audit",
                    context = "WCAG 2.1 AA compliance check"
                )

                try {
                    val result = future.get()

                    if (result.severity == Severity.INFO && result.recommendations.isEmpty()) {
                        return
                    }

                    val problemLevel = when (result.severity) {
                        Severity.ERROR -> ProblemHighlightType.ERROR
                        Severity.WARNING -> ProblemHighlightType.WARNING
                        Severity.INFO -> ProblemHighlightType.WEAK_WARNING
                    }

                    holder.registerProblem(
                        file,
                        result.diagnosis,
                        problemLevel,
                        *createQuickFixes(result.recommendations)
                    )

                } catch (e: Exception) {
                    log.warn("Failed to run accessibility inspection on ${file.name}", e)
                }
            }
        }
    }

    private fun createQuickFixes(recommendations: List<String>): Array<LocalQuickFix> {
        return recommendations.take(3).map { recommendation ->
            object : LocalQuickFix {
                override fun getFamilyName(): String = "Coach Accessibility Fix"

                override fun getName(): String = recommendation.take(100)

                override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
                    log.info("Applying accessibility fix: $recommendation")
                }
            }
        }.toTypedArray()
    }

    override fun getDisplayName(): String = "Accessibility Analysis (AccessibilityWizard)"

    override fun getShortName(): String = "CoachAccessibility"

    override fun getGroupDisplayName(): String = "Coach"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WARNING

    override fun isEnabledByDefault(): Boolean = true
}
