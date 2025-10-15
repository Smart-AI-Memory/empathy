package com.deepstudyai.coach.services

import com.deepstudyai.coach.lsp.CoachLSPClient
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import kotlinx.coroutines.*

/**
 * Project-level service for Coach.
 *
 * Manages the lifecycle of Coach components for a specific project,
 * including LSP client initialization and project-specific configuration.
 */
@Service(Service.Level.PROJECT)
class CoachProjectService(private val project: Project) {

    private val log = Logger.getInstance(CoachProjectService::class.java)
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    @Volatile
    private var isInitialized = false

    companion object {
        fun getInstance(project: Project): CoachProjectService = project.service()
    }

    /**
     * Initializes the Coach service for this project.
     */
    fun initialize() {
        if (isInitialized) {
            log.warn("CoachProjectService already initialized for project: ${project.name}")
            return
        }

        scope.launch {
            try {
                log.info("Initializing Coach for project: ${project.name}")

                // Check if auto-start is enabled
                val settings = CoachSettingsService.getInstance().state
                if (!settings.autoStartServer) {
                    log.info("Auto-start disabled, skipping LSP client initialization")
                    return@launch
                }

                // Initialize LSP client
                val lspClient = CoachLSPClient.getInstance(project)
                lspClient.start().thenAccept { initResult ->
                    log.info("LSP client initialized successfully for ${project.name}")
                    log.debug("Server capabilities: ${initResult?.capabilities}")

                    // Perform health check
                    lspClient.healthCheck().thenAccept { health ->
                        log.info("LSP server health: ${health.status} (version ${health.version})")
                    }.exceptionally { e ->
                        log.warn("Health check failed", e)
                        null
                    }
                }.exceptionally { e ->
                    log.error("Failed to initialize LSP client for ${project.name}", e)
                    null
                }

                isInitialized = true
                log.info("Coach initialization completed for project: ${project.name}")

            } catch (e: Exception) {
                log.error("Error during Coach initialization for ${project.name}", e)
            }
        }
    }

    /**
     * Starts the Coach services for this project.
     */
    fun start() {
        if (!isInitialized) {
            initialize()
        }

        scope.launch {
            try {
                val lspClient = CoachLSPClient.getInstance(project)
                if (!lspClient.start().isDone) {
                    lspClient.start().get()
                }
                log.info("Coach services started for project: ${project.name}")
            } catch (e: Exception) {
                log.error("Failed to start Coach services for ${project.name}", e)
            }
        }
    }

    /**
     * Stops the Coach services for this project.
     */
    fun stop() {
        scope.launch {
            try {
                log.info("Stopping Coach services for project: ${project.name}")

                // Stop LSP client
                val lspClient = CoachLSPClient.getInstance(project)
                lspClient.stop()

                // Clear analysis results
                val analysisService = AnalysisService.getInstance(project)
                analysisService.clearResults()

                log.info("Coach services stopped for project: ${project.name}")
            } catch (e: Exception) {
                log.error("Error stopping Coach services for ${project.name}", e)
            }
        }
    }

    /**
     * Restarts the Coach services for this project.
     */
    fun restart() {
        scope.launch {
            stop()
            delay(1000) // Wait for clean shutdown
            start()
        }
    }

    /**
     * Checks if Coach is initialized for this project.
     */
    fun isInitialized(): Boolean {
        return isInitialized
    }

    /**
     * Gets the project instance.
     */
    fun getProject(): Project {
        return project
    }

    /**
     * Performs a health check on all Coach components.
     */
    fun healthCheck(): CompletableFuture<ProjectHealthStatus> {
        return CompletableFuture.supplyAsync {
            try {
                val lspClient = CoachLSPClient.getInstance(project)
                val lspHealth = lspClient.healthCheck().get()

                val analysisService = AnalysisService.getInstance(project)
                val stats = analysisService.getStatistics()

                val cacheService = CoachCacheService.getInstance()
                val cacheStats = cacheService.getStatistics()

                ProjectHealthStatus(
                    projectName = project.name,
                    lspServerStatus = lspHealth.status,
                    lspServerVersion = lspHealth.version,
                    analysisCount = stats.totalAnalyses,
                    cacheSize = cacheStats.totalEntries,
                    isHealthy = lspHealth.status == "healthy"
                )
            } catch (e: Exception) {
                log.warn("Health check failed for ${project.name}", e)
                ProjectHealthStatus(
                    projectName = project.name,
                    lspServerStatus = "error",
                    lspServerVersion = "",
                    analysisCount = 0,
                    cacheSize = 0,
                    isHealthy = false
                )
            }
        }
    }

    /**
     * Gets project configuration summary.
     */
    fun getConfigurationSummary(): ConfigurationSummary {
        val settings = CoachSettingsService.getInstance().state
        val wizardRegistry = WizardRegistry.getInstance(project)

        return ConfigurationSummary(
            projectName = project.name,
            projectPath = project.basePath ?: "",
            pythonPath = settings.pythonPath,
            serverScriptPath = settings.serverScriptPath,
            apiProvider = settings.apiProvider,
            modelName = settings.modelName,
            enabledWizardCount = settings.enabledWizards.size,
            totalWizardCount = wizardRegistry.getWizardCount(),
            realTimeAnalysisEnabled = settings.enableRealTimeAnalysis,
            predictionsEnabled = settings.enablePredictions,
            cachingEnabled = settings.enableCaching
        )
    }

    fun dispose() {
        isInitialized = false
        scope.cancel()
        stop()
    }
}

/**
 * Health status of the Coach project service.
 */
data class ProjectHealthStatus(
    val projectName: String,
    val lspServerStatus: String,
    val lspServerVersion: String,
    val analysisCount: Int,
    val cacheSize: Int,
    val isHealthy: Boolean
)

/**
 * Configuration summary for the project.
 */
data class ConfigurationSummary(
    val projectName: String,
    val projectPath: String,
    val pythonPath: String,
    val serverScriptPath: String,
    val apiProvider: String,
    val modelName: String,
    val enabledWizardCount: Int,
    val totalWizardCount: Int,
    val realTimeAnalysisEnabled: Boolean,
    val predictionsEnabled: Boolean,
    val cachingEnabled: Boolean
)
