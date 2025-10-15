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
 * Performance inspection powered by the PerformanceWizard.
 *
 * Detects performance issues including:
 * - N+1 query problems
 * - Memory leaks
 * - Inefficient algorithms
 * - Unoptimized loops
 * - Resource contention
 */
class PerformanceInspection : LocalInspectionTool() {

    private val log = Logger.getInstance(PerformanceInspection::class.java)

    companion object {
        private const val WIZARD_ID = "PerformanceWizard"
    }

    override fun buildVisitor(holder: ProblemsHolder, isOnTheFly: Boolean): PsiElementVisitor {
        return object : PsiElementVisitor() {
            override fun visitFile(file: PsiFile) {
                super.visitFile(file)

                val settings = service<CoachSettingsService>()
                if (!settings.state.isWizardEnabled(WIZARD_ID)) {
                    return
                }

                val analysisService = AnalysisService.getInstance(file.project)
                val future = analysisService.analyzeWithWizard(
                    psiFile = file,
                    wizardId = WIZARD_ID,
                    role = "developer",
                    task = "Performance analysis",
                    context = "Identify performance bottlenecks and optimization opportunities"
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
                    log.warn("Failed to run performance inspection on ${file.name}", e)
                }
            }
        }
    }

    private fun createQuickFixes(recommendations: List<String>): Array<LocalQuickFix> {
        return recommendations.take(3).map { recommendation ->
            object : LocalQuickFix {
                override fun getFamilyName(): String = "Coach Performance Fix"

                override fun getName(): String = recommendation.take(100)

                override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
                    log.info("Applying performance fix: $recommendation")
                }
            }
        }.toTypedArray()
    }

    override fun getDisplayName(): String = "Performance Analysis (PerformanceWizard)"

    override fun getShortName(): String = "CoachPerformance"

    override fun getGroupDisplayName(): String = "Coach"

    override fun getDefaultLevel(): HighlightDisplayLevel = HighlightDisplayLevel.WARNING

    override fun isEnabledByDefault(): Boolean = true
}
