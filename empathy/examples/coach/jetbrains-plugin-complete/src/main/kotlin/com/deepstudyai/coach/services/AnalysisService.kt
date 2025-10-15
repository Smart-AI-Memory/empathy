package com.deepstudyai.coach.services

import com.deepstudyai.coach.lsp.*
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile
import kotlinx.coroutines.*
import java.util.concurrent.CompletableFuture
import java.util.concurrent.ConcurrentHashMap

/**
 * Service for coordinating analysis across multiple wizards.
 *
 * Manages analysis requests, caching, and multi-wizard coordination.
 */
@Service(Service.Level.PROJECT)
class AnalysisService(private val project: Project) {

    private val log = Logger.getInstance(AnalysisService::class.java)
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val analysisResults = ConcurrentHashMap<String, AnalysisResult>()
    private val activeAnalyses = ConcurrentHashMap<String, Job>()

    companion object {
        fun getInstance(project: Project): AnalysisService = project.service()
    }

    /**
     * Analyzes a file with a specific wizard.
     */
    fun analyzeWithWizard(
        psiFile: PsiFile,
        wizardId: String,
        role: String = "developer",
        task: String = "",
        context: String = ""
    ): CompletableFuture<WizardResult> {
        val lspClient = CoachLSPClient.getInstance(project)
        val cacheService = service<CoachCacheService>()

        val filePath = psiFile.virtualFile.path
        val code = psiFile.text

        // Check cache first
        val cacheKey = generateCacheKey(filePath, wizardId, code)
        cacheService.get(cacheKey)?.let { cachedResult ->
            log.debug("Returning cached result for $filePath with $wizardId")
            return CompletableFuture.completedFuture(cachedResult as WizardResult)
        }

        return lspClient.runWizard(wizardId, code, filePath, role, task, context)
            .thenApply { result ->
                // Cache the result
                cacheService.put(cacheKey, result)

                // Store in analysis results
                val analysisKey = "$filePath:$wizardId"
                analysisResults[analysisKey] = AnalysisResult(
                    filePath = filePath,
                    wizardId = wizardId,
                    result = result,
                    timestamp = System.currentTimeMillis()
                )

                result
            }
    }

    /**
     * Analyzes a file with multiple wizards in collaboration mode.
     */
    fun multiWizardAnalysis(
        psiFile: PsiFile,
        wizards: List<String>,
        scenario: String = "",
        context: String = ""
    ): CompletableFuture<MultiWizardResult> {
        val lspClient = CoachLSPClient.getInstance(project)
        val cacheService = service<CoachCacheService>()

        val filePath = psiFile.virtualFile.path
        val code = psiFile.text

        // Check cache
        val cacheKey = generateCacheKey(filePath, wizards.joinToString(","), code)
        cacheService.get(cacheKey)?.let { cachedResult ->
            log.debug("Returning cached multi-wizard result for $filePath")
            return CompletableFuture.completedFuture(cachedResult as MultiWizardResult)
        }

        return lspClient.multiWizardReview(wizards, code, filePath, scenario, context)
            .thenApply { result ->
                // Cache the result
                cacheService.put(cacheKey, result)

                result
            }
    }

    /**
     * Analyzes a file with all applicable wizards.
     */
    fun analyzeWithAllWizards(
        psiFile: PsiFile,
        language: String
    ): CompletableFuture<List<WizardResult>> {
        val wizardRegistry = WizardRegistry.getInstance(project)
        val applicableWizards = wizardRegistry.getWizardsForLanguage(language)

        if (applicableWizards.isEmpty()) {
            return CompletableFuture.completedFuture(emptyList())
        }

        // Run all wizards in parallel
        val futures = applicableWizards.map { wizard ->
            analyzeWithWizard(psiFile, wizard.id)
        }

        return CompletableFuture.allOf(*futures.toTypedArray())
            .thenApply {
                futures.mapNotNull { future ->
                    try {
                        future.get()
                    } catch (e: Exception) {
                        log.warn("Failed to get wizard result", e)
                        null
                    }
                }
            }
    }

    /**
     * Gets Level 4 predictions for a file.
     */
    fun getPredictions(
        psiFile: PsiFile,
        timeframe: Int = 60
    ): CompletableFuture<List<PredictedImpact>> {
        val lspClient = CoachLSPClient.getInstance(project)
        val cacheService = service<CoachCacheService>()

        val filePath = psiFile.virtualFile.path
        val code = psiFile.text

        // Check cache
        val cacheKey = generateCacheKey(filePath, "predictions", code)
        cacheService.get(cacheKey)?.let { cachedResult ->
            @Suppress("UNCHECKED_CAST")
            return CompletableFuture.completedFuture(cachedResult as List<PredictedImpact>)
        }

        return lspClient.predict(code, filePath, timeframe)
            .thenApply { predictions ->
                // Cache the result
                cacheService.put(cacheKey, predictions)
                predictions
            }
    }

    /**
     * Analyzes the entire project.
     */
    fun analyzeProject(
        progressCallback: (String, Int, Int) -> Unit = { _, _, _ -> }
    ): Job {
        val job = scope.launch {
            try {
                val settings = service<CoachSettingsService>()
                val wizardRegistry = WizardRegistry.getInstance(project)

                val enabledWizards = wizardRegistry.getEnabledWizards()
                if (enabledWizards.isEmpty()) {
                    log.warn("No wizards enabled for project analysis")
                    return@launch
                }

                // Get all source files in project
                val sourceFiles = getProjectSourceFiles()
                val totalFiles = sourceFiles.size

                log.info("Starting project analysis: $totalFiles files, ${enabledWizards.size} wizards")

                sourceFiles.forEachIndexed { index, psiFile ->
                    if (!isActive) return@launch // Check for cancellation

                    val language = psiFile.language.displayName
                    progressCallback(psiFile.name, index + 1, totalFiles)

                    try {
                        analyzeWithAllWizards(psiFile, language).get()
                    } catch (e: Exception) {
                        log.warn("Failed to analyze ${psiFile.name}", e)
                    }
                }

                log.info("Project analysis completed")
            } catch (e: CancellationException) {
                log.info("Project analysis cancelled")
            } catch (e: Exception) {
                log.error("Project analysis failed", e)
            }
        }

        activeAnalyses["project"] = job
        return job
    }

    /**
     * Cancels an active analysis.
     */
    fun cancelAnalysis(key: String = "project") {
        activeAnalyses[key]?.cancel()
        activeAnalyses.remove(key)
    }

    /**
     * Gets analysis results for a specific file and wizard.
     */
    fun getAnalysisResult(filePath: String, wizardId: String): AnalysisResult? {
        return analysisResults["$filePath:$wizardId"]
    }

    /**
     * Gets all analysis results for a file.
     */
    fun getFileAnalysisResults(filePath: String): List<AnalysisResult> {
        return analysisResults.values.filter { it.filePath == filePath }
    }

    /**
     * Gets all analysis results.
     */
    fun getAllAnalysisResults(): List<AnalysisResult> {
        return analysisResults.values.toList()
    }

    /**
     * Clears all analysis results.
     */
    fun clearResults() {
        analysisResults.clear()
    }

    /**
     * Clears results for a specific file.
     */
    fun clearFileResults(filePath: String) {
        analysisResults.keys.removeIf { it.startsWith("$filePath:") }
    }

    /**
     * Gets statistics about analysis results.
     */
    fun getStatistics(): AnalysisStatistics {
        val results = analysisResults.values
        val errors = results.count { it.result.severity == Severity.ERROR }
        val warnings = results.count { it.result.severity == Severity.WARNING }
        val infos = results.count { it.result.severity == Severity.INFO }

        val wizardCounts = results.groupBy { it.wizardId }
            .mapValues { it.value.size }

        return AnalysisStatistics(
            totalAnalyses = results.size,
            errors = errors,
            warnings = warnings,
            infos = infos,
            wizardCounts = wizardCounts
        )
    }

    private fun getProjectSourceFiles(): List<PsiFile> {
        // This is a simplified implementation
        // In a real plugin, you'd use PsiManager and traverse the project structure
        // excluding build directories, node_modules, etc.
        return emptyList() // Placeholder
    }

    private fun generateCacheKey(filePath: String, identifier: String, code: String): String {
        val codeHash = code.hashCode()
        return "$filePath:$identifier:$codeHash"
    }

    fun dispose() {
        scope.cancel()
        analysisResults.clear()
        activeAnalyses.values.forEach { it.cancel() }
        activeAnalyses.clear()
    }
}

/**
 * Result of an analysis operation.
 */
data class AnalysisResult(
    val filePath: String,
    val wizardId: String,
    val result: WizardResult,
    val timestamp: Long
)

/**
 * Statistics about analysis results.
 */
data class AnalysisStatistics(
    val totalAnalyses: Int,
    val errors: Int,
    val warnings: Int,
    val infos: Int,
    val wizardCounts: Map<String, Int>
)
