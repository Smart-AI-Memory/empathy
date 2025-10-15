package com.deepstudyai.coach.annotators

import com.deepstudyai.coach.lsp.Severity
import com.deepstudyai.coach.services.AnalysisService
import com.deepstudyai.coach.services.CoachSettingsService
import com.intellij.lang.annotation.AnnotationHolder
import com.intellij.lang.annotation.Annotator
import com.intellij.lang.annotation.HighlightSeverity
import com.intellij.openapi.components.service
import com.intellij.openapi.editor.markup.GutterIconRenderer
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiFile
import javax.swing.Icon
import com.intellij.openapi.util.IconLoader

/**
 * Annotator that displays Level 4 predictions in the editor.
 *
 * Shows gutter icons and inline hints for predicted future issues.
 */
class CoachPredictionAnnotator : Annotator {

    companion object {
        private val PREDICTION_ICON: Icon = IconLoader.getIcon("/icons/prediction.svg", CoachPredictionAnnotator::class.java)
        private val ERROR_PREDICTION_ICON: Icon = IconLoader.getIcon("/icons/prediction-error.svg", CoachPredictionAnnotator::class.java)
        private val WARNING_PREDICTION_ICON: Icon = IconLoader.getIcon("/icons/prediction-warning.svg", CoachPredictionAnnotator::class.java)
    }

    override fun annotate(element: PsiElement, holder: AnnotationHolder) {
        // Only annotate at the file level to avoid performance issues
        if (element !is PsiFile) return

        val settings = service<CoachSettingsService>()
        if (!settings.state.enablePredictions || !settings.state.showGutterIcons) {
            return
        }

        val project = element.project
        val analysisService = AnalysisService.getInstance(project)

        try {
            // Get predictions for this file
            val future = analysisService.getPredictions(element, timeframe = settings.state.predictionTimeframe)
            val predictions = future.get()

            if (predictions.isEmpty()) {
                return
            }

            // Filter by confidence threshold
            val significantPredictions = predictions.filter {
                it.confidence >= settings.state.predictionConfidenceThreshold
            }

            if (significantPredictions.isEmpty()) {
                return
            }

            // Add annotations for each prediction
            significantPredictions.forEach { prediction ->
                val severity = when (prediction.severity) {
                    Severity.ERROR -> HighlightSeverity.ERROR
                    Severity.WARNING -> HighlightSeverity.WARNING
                    Severity.INFO -> HighlightSeverity.WEAK_WARNING
                }

                val icon = when (prediction.severity) {
                    Severity.ERROR -> ERROR_PREDICTION_ICON
                    Severity.WARNING -> WARNING_PREDICTION_ICON
                    Severity.INFO -> PREDICTION_ICON
                }

                val message = buildString {
                    append("🔮 Level 4 Prediction (${(prediction.confidence * 100).toInt()}% confidence)\n")
                    append("${prediction.issue}\n\n")
                    append("Expected in ~${prediction.timeframe} days\n\n")
                    append("Impact: ${prediction.impact}\n\n")
                    append("Preventive Action: ${prediction.preventiveAction}")
                }

                // Create gutter icon renderer
                val gutterIconRenderer = object : GutterIconRenderer() {
                    override fun getIcon(): Icon = icon

                    override fun getTooltipText(): String = message

                    override fun equals(other: Any?): Boolean = false

                    override fun hashCode(): Int = prediction.issue.hashCode()
                }

                // Add the annotation with gutter icon
                holder.newAnnotation(severity, message)
                    .range(element.textRange)
                    .gutterIconRenderer(gutterIconRenderer)
                    .create()
            }
        } catch (e: Exception) {
            // Silently ignore prediction errors to avoid disrupting the editor
            // Predictions are optional enhancements
        }
    }
}
