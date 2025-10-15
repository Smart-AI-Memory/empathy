package com.deepstudyai.coach.inspections

import com.deepstudyai.coach.lsp.Severity
import com.deepstudyai.coach.lsp.WizardResult
import com.deepstudyai.coach.services.AnalysisService
import com.deepstudyai.coach.services.CoachSettingsService
import com.intellij.codeInspection.*
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiElementVisitor
import com.intellij.psi.PsiFile

/**
 * Base class for all Coach inspections.
 *
 * Provides common functionality for running wizard analysis and
 * reporting problems.
 */
abstract class BaseCoachInspection : LocalInspectionTool() {

    protected val log = Logger.getInstance(this::class.java)

    /**
     * The wizard ID to use for this inspection.
     */
    abstract fun getWizardId(): String

    /**
     * The task description for the wizard.
     */
    open fun getTask(): String = "Code analysis"

    /**
     * The context for the wizard.
     */
    open fun getContext(): String = ""

    /**
     * The role for the wizard.
     */
    open fun getRole(): String = "developer"

    /**
     * Check if this inspection is applicable to the file.
     */
    open fun isApplicable(file: PsiFile): Boolean = true

    /**
     * Get the family name for quick fixes.
     */
    open fun getQuickFixFamily(): String = "Coach Quick Fix"

    override fun buildVisitor(holder: ProblemsHolder, isOnTheFly: Boolean): PsiElementVisitor {
        return object : PsiElementVisitor() {
            override fun visitFile(file: PsiFile) {
                super.visitFile(file)

                // Check if applicable
                if (!isApplicable(file)) {
                    return
                }

                // Check if the wizard is enabled
                val settings = service<CoachSettingsService>()
                if (!settings.state.isWizardEnabled(getWizardId())) {
                    return
                }

                // Run analysis
                val analysisService = AnalysisService.getInstance(file.project)
                val future = analysisService.analyzeWithWizard(
                    psiFile = file,
                    wizardId = getWizardId(),
                    role = getRole(),
                    task = getTask(),
                    context = getContext()
                )

                try {
                    val result = future.get()
                    processResult(result, file, holder)
                } catch (e: Exception) {
                    log.warn("Failed to run ${getWizardId()} inspection on ${file.name}", e)
                }
            }
        }
    }

    /**
     * Process the wizard result and register problems.
     */
    protected open fun processResult(result: WizardResult, file: PsiFile, holder: ProblemsHolder) {
        // Skip if no issues found
        if (result.severity == Severity.INFO && result.recommendations.isEmpty()) {
            return
        }

        // Convert severity to problem highlight type
        val problemLevel = when (result.severity) {
            Severity.ERROR -> ProblemHighlightType.ERROR
            Severity.WARNING -> ProblemHighlightType.WARNING
            Severity.INFO -> ProblemHighlightType.WEAK_WARNING
        }

        // Create quick fixes
        val quickFixes = createQuickFixes(result, file.project)

        // Register the problem
        holder.registerProblem(
            file,
            result.diagnosis,
            problemLevel,
            *quickFixes
        )
    }

    /**
     * Create quick fixes from the wizard result.
     */
    protected open fun createQuickFixes(result: WizardResult, project: Project): Array<LocalQuickFix> {
        return result.recommendations.take(3).map { recommendation ->
            object : LocalQuickFix {
                override fun getFamilyName(): String = getQuickFixFamily()

                override fun getName(): String = recommendation.take(100)

                override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
                    // Subclasses can override to provide actual implementations
                    log.info("Applying ${getWizardId()} fix: $recommendation")
                }
            }
        }.toTypedArray()
    }

    override fun getGroupDisplayName(): String = "Coach"

    override fun isEnabledByDefault(): Boolean = true
}
