/**
 * Coach LSP Client for JetBrains IDEs
 * Connects to Python LSP server using Language Server Protocol
 *
 * Copyright 2025 Deep Study AI, LLC
 * Licensed under the Apache License, Version 2.0
 */

package com.deepstudyai.coach.lsp

import com.intellij.openapi.Disposable
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import kotlinx.coroutines.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.eclipse.lsp4j.*
import org.eclipse.lsp4j.jsonrpc.Launcher
import org.eclipse.lsp4j.launch.LSPLauncher
import org.eclipse.lsp4j.services.LanguageClient
import org.eclipse.lsp4j.services.LanguageServer
import java.io.InputStream
import java.io.OutputStream
import java.util.concurrent.CompletableFuture
import java.util.concurrent.TimeUnit

/**
 * Request/Response types for Coach LSP custom methods
 */
@Serializable
data class WizardTaskRequest(
    val wizardName: String,
    val role: String = "developer",
    val task: String,
    val context: String = "",
    val preferences: String = "",
    val riskTolerance: String = "medium"
)

@Serializable
data class WizardResult(
    val routing: List<String>,
    val primaryOutput: WizardOutput,
    val supplementalOutputs: List<WizardOutput>,
    val collaboration: CollaborationInfo,
    val overallConfidence: Double,
    val executionTimeMs: Long,
    val cacheHit: Boolean = false
)

@Serializable
data class WizardOutput(
    val wizard: String,
    val diagnosis: String,
    val recommendations: List<String>,
    val predictedImpact: PredictedImpact,
    val codeExamples: List<CodeExample>,
    val confidence: Double
)

@Serializable
data class PredictedImpact(
    val timeline: String,
    val severity: String,
    val affectedAreas: List<String>
)

@Serializable
data class CodeExample(
    val language: String,
    val code: String,
    val explanation: String
)

@Serializable
data class CollaborationInfo(
    val consultedWizards: List<String>,
    val consensusAreas: List<String>,
    val disagreements: List<Disagreement>
)

@Serializable
data class Disagreement(
    val topic: String,
    val positions: Map<String, String>
)

@Serializable
data class MultiWizardReviewRequest(
    val scenario: String,
    val files: List<String>
)

@Serializable
data class PredictionRequest(
    val code: String,
    val context: String,
    val language: String
)

/**
 * Main LSP client service for Coach
 * Manages connection to Python LSP server
 */
@Service(Service.Level.PROJECT)
class CoachLSPClient(private val project: Project) : Disposable {
    private val logger = Logger.getInstance(CoachLSPClient::class.java)
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private var languageServer: LanguageServer? = null
    private var serverProcess: Process? = null
    private var isConnected = false

    // Cache for wizard results (5 minute TTL)
    private val resultCache = mutableMapOf<String, CachedResult>()
    private data class CachedResult(val result: WizardResult, val timestamp: Long)
    private val CACHE_TTL_MS = 5 * 60 * 1000L // 5 minutes

    companion object {
        fun getInstance(project: Project): CoachLSPClient = project.service()

        // LSP Custom Method Names
        const val COACH_RUN_WIZARD = "coach/runWizard"
        const val COACH_MULTI_WIZARD_REVIEW = "coach/multiWizardReview"
        const val COACH_PREDICT = "coach/predict"
        const val COACH_HEALTH_CHECK = "coach/healthCheck"
    }

    /**
     * Start LSP server process and establish connection
     */
    suspend fun start() = withContext(Dispatchers.IO) {
        if (isConnected) {
            logger.info("Coach LSP server already running")
            return@withContext
        }

        logger.info("Starting Coach LSP server...")

        try {
            // Start Python LSP server process
            val serverPath = getServerPath()
            val processBuilder = ProcessBuilder(
                "python3", "-m", "lsp.server"
            ).apply {
                directory(serverPath.toFile().parentFile.parentFile) // examples/coach directory
                redirectErrorStream(false)
            }

            serverProcess = processBuilder.start()

            // Create LSP client
            val client = CoachLanguageClient(project)

            // Create launcher and start listening
            val launcher = LSPLauncher.createClientLauncher(
                client,
                serverProcess!!.inputStream,
                serverProcess!!.outputStream
            )

            languageServer = launcher.remoteProxy
            launcher.startListening()

            // Initialize server
            val initParams = InitializeParams().apply {
                processId = ProcessHandle.current().pid().toInt()
                rootUri = project.basePath
                capabilities = ClientCapabilities().apply {
                    textDocument = TextDocumentClientCapabilities().apply {
                        diagnostic = DiagnosticCapabilities()
                        codeAction = CodeActionCapabilities()
                        hover = HoverCapabilities()
                    }
                }
            }

            val initResult = languageServer!!.initialize(initParams).get(10, TimeUnit.SECONDS)
            languageServer!!.initialized(InitializedParams())

            isConnected = true
            logger.info("Coach LSP server started successfully: ${initResult.capabilities}")

            // Health check
            healthCheck()

        } catch (e: Exception) {
            logger.error("Failed to start Coach LSP server", e)
            throw CoachLSPException("Failed to start LSP server: ${e.message}", e)
        }
    }

    /**
     * Stop LSP server
     */
    suspend fun stop() = withContext(Dispatchers.IO) {
        try {
            languageServer?.shutdown()?.get(5, TimeUnit.SECONDS)
            languageServer?.exit()
            serverProcess?.destroy()
            serverProcess?.waitFor(5, TimeUnit.SECONDS)
            isConnected = false
            logger.info("Coach LSP server stopped")
        } catch (e: Exception) {
            logger.error("Error stopping Coach LSP server", e)
            serverProcess?.destroyForcibly()
        }
    }

    /**
     * Run a specific wizard
     */
    suspend fun runWizard(
        wizardName: String,
        task: String,
        context: String = "",
        role: String = "developer"
    ): WizardResult = withContext(Dispatchers.IO) {
        ensureConnected()

        // Check cache
        val cacheKey = "$wizardName:$task:$context"
        resultCache[cacheKey]?.let { cached ->
            if (System.currentTimeMillis() - cached.timestamp < CACHE_TTL_MS) {
                logger.info("Cache hit for $wizardName")
                return@withContext cached.result.copy(cacheHit = true)
            }
        }

        logger.info("Running wizard: $wizardName")

        try {
            val params = listOf(
                wizardName,
                mapOf(
                    "role" to role,
                    "task" to task,
                    "context" to context
                )
            )

            val result = languageServer!!
                .workspaceService
                .executeCommand(ExecuteCommandParams(COACH_RUN_WIZARD, params))
                .get(30, TimeUnit.SECONDS)

            val wizardResult = Json.decodeFromString<WizardResult>(Json.encodeToString(result))

            // Cache result
            resultCache[cacheKey] = CachedResult(wizardResult, System.currentTimeMillis())

            // Clean old cache entries
            cleanCache()

            return@withContext wizardResult

        } catch (e: Exception) {
            logger.error("Failed to run wizard $wizardName", e)
            throw CoachLSPException("Wizard execution failed: ${e.message}", e)
        }
    }

    /**
     * Run multi-wizard review
     */
    suspend fun multiWizardReview(
        scenario: String,
        files: List<String>
    ): WizardResult = withContext(Dispatchers.IO) {
        ensureConnected()

        logger.info("Running multi-wizard review: $scenario")

        try {
            val params = listOf(scenario, files)

            val result = languageServer!!
                .workspaceService
                .executeCommand(ExecuteCommandParams(COACH_MULTI_WIZARD_REVIEW, params))
                .get(60, TimeUnit.SECONDS)

            return@withContext Json.decodeFromString<WizardResult>(Json.encodeToString(result))

        } catch (e: Exception) {
            logger.error("Failed to run multi-wizard review", e)
            throw CoachLSPException("Multi-wizard review failed: ${e.message}", e)
        }
    }

    /**
     * Get Level 4 prediction for code
     */
    suspend fun getPrediction(
        code: String,
        context: String,
        language: String
    ): Map<String, Any> = withContext(Dispatchers.IO) {
        ensureConnected()

        try {
            val params = listOf(
                mapOf(
                    "code" to code,
                    "context" to context,
                    "language" to language
                )
            )

            val result = languageServer!!
                .workspaceService
                .executeCommand(ExecuteCommandParams(COACH_PREDICT, params))
                .get(10, TimeUnit.SECONDS)

            @Suppress("UNCHECKED_CAST")
            return@withContext result as Map<String, Any>

        } catch (e: Exception) {
            logger.error("Failed to get prediction", e)
            return@withContext emptyMap()
        }
    }

    /**
     * Health check
     */
    suspend fun healthCheck(): Map<String, Any> = withContext(Dispatchers.IO) {
        ensureConnected()

        try {
            val result = languageServer!!
                .workspaceService
                .executeCommand(ExecuteCommandParams(COACH_HEALTH_CHECK, emptyList()))
                .get(5, TimeUnit.SECONDS)

            @Suppress("UNCHECKED_CAST")
            val health = result as Map<String, Any>
            logger.info("Health check: $health")
            return@withContext health

        } catch (e: Exception) {
            logger.error("Health check failed", e)
            return@withContext mapOf("status" to "error", "message" to e.message)
        }
    }

    /**
     * Analyze document (sends textDocument/didOpen notification)
     */
    suspend fun analyzeDocument(file: VirtualFile, content: String) = withContext(Dispatchers.IO) {
        ensureConnected()

        try {
            val params = DidOpenTextDocumentParams(
                TextDocumentItem(
                    file.url,
                    getLanguageId(file),
                    1,
                    content
                )
            )

            languageServer!!.textDocumentService.didOpen(params)

        } catch (e: Exception) {
            logger.error("Failed to analyze document", e)
        }
    }

    /**
     * Notify document change
     */
    suspend fun documentChanged(file: VirtualFile, content: String) = withContext(Dispatchers.IO) {
        ensureConnected()

        try {
            val params = DidChangeTextDocumentParams(
                VersionedTextDocumentIdentifier(file.url, 1),
                listOf(
                    TextDocumentContentChangeEvent(content)
                )
            )

            languageServer!!.textDocumentService.didChange(params)

        } catch (e: Exception) {
            logger.error("Failed to notify document change", e)
        }
    }

    // Helper methods

    private fun ensureConnected() {
        if (!isConnected) {
            throw CoachLSPException("LSP server not connected. Call start() first.")
        }
    }

    private fun getServerPath(): java.nio.file.Path {
        // Look for lsp/server.py in project or configured path
        val projectPath = java.nio.file.Paths.get(project.basePath ?: "")
        val serverPath = projectPath.resolve("examples/coach/lsp/server.py")

        if (!serverPath.toFile().exists()) {
            throw CoachLSPException("LSP server not found at $serverPath")
        }

        return serverPath
    }

    private fun getLanguageId(file: VirtualFile): String {
        return when (file.extension) {
            "py" -> "python"
            "js" -> "javascript"
            "ts" -> "typescript"
            "tsx" -> "typescriptreact"
            "jsx" -> "javascriptreact"
            "java" -> "java"
            "kt" -> "kotlin"
            "go" -> "go"
            "rs" -> "rust"
            "rb" -> "ruby"
            "php" -> "php"
            "cs" -> "csharp"
            else -> "plaintext"
        }
    }

    private fun cleanCache() {
        val now = System.currentTimeMillis()
        resultCache.entries.removeIf { (_, cached) ->
            now - cached.timestamp > CACHE_TTL_MS
        }
    }

    override fun dispose() {
        scope.cancel()
        runBlocking {
            stop()
        }
    }
}

/**
 * Language client implementation (receives notifications from server)
 */
class CoachLanguageClient(private val project: Project) : LanguageClient {
    private val logger = Logger.getInstance(CoachLanguageClient::class.java)

    override fun telemetryEvent(params: Any?) {
        logger.info("Telemetry: $params")
    }

    override fun publishDiagnostics(params: PublishDiagnosticsParams?) {
        params?.let {
            logger.info("Diagnostics for ${it.uri}: ${it.diagnostics.size} issues")
            // Diagnostics are handled by CoachExternalAnnotator
        }
    }

    override fun showMessage(params: MessageParams?) {
        params?.let {
            logger.info("Server message (${it.type}): ${it.message}")
        }
    }

    override fun showMessageRequest(params: ShowMessageRequestParams?): CompletableFuture<MessageActionItem> {
        return CompletableFuture.completedFuture(MessageActionItem("OK"))
    }

    override fun logMessage(params: MessageParams?) {
        params?.let {
            when (it.type) {
                MessageType.Error -> logger.error("LSP: ${it.message}")
                MessageType.Warning -> logger.warn("LSP: ${it.message}")
                else -> logger.info("LSP: ${it.message}")
            }
        }
    }
}

/**
 * Custom exception for LSP errors
 */
class CoachLSPException(message: String, cause: Throwable? = null) : Exception(message, cause)
