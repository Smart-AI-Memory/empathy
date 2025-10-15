package com.deepstudyai.coach.lsp

import com.deepstudyai.coach.services.CoachSettingsService
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import kotlinx.coroutines.*
import kotlinx.serialization.json.Json
import org.eclipse.lsp4j.*
import org.eclipse.lsp4j.jsonrpc.Launcher
import org.eclipse.lsp4j.launch.LSPLauncher
import org.eclipse.lsp4j.services.LanguageClient
import org.eclipse.lsp4j.services.LanguageServer
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.net.URI
import java.util.concurrent.CompletableFuture
import java.util.concurrent.TimeUnit

/**
 * LSP client for communicating with the Coach Python LSP server.
 *
 * This service manages the lifecycle of the LSP connection and provides
 * methods for executing Coach-specific commands.
 */
@Service(Service.Level.PROJECT)
class CoachLSPClient(private val project: Project) : LanguageClient {

    private val log = Logger.getInstance(CoachLSPClient::class.java)
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private var languageServer: LanguageServer? = null
    private var serverProcess: Process? = null
    private var launcher: Launcher<LanguageServer>? = null

    @Volatile
    private var isConnected = false

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    companion object {
        private const val CONNECTION_TIMEOUT = 30_000L // 30 seconds
        private const val REQUEST_TIMEOUT = 60_000L // 60 seconds

        fun getInstance(project: Project): CoachLSPClient = project.service()
    }

    /**
     * Starts the LSP server process and establishes connection.
     */
    fun start(): CompletableFuture<InitializeResult> {
        if (isConnected) {
            log.warn("LSP client already connected")
            return CompletableFuture.completedFuture(null)
        }

        val settings = service<CoachSettingsService>()
        val pythonPath = settings.state.pythonPath
        val serverScriptPath = settings.state.serverScriptPath

        if (pythonPath.isEmpty() || serverScriptPath.isEmpty()) {
            log.error("Python path or server script path not configured")
            return CompletableFuture.failedFuture(
                IllegalStateException("Coach LSP server not configured. Please check settings.")
            )
        }

        return CompletableFuture.supplyAsync {
            try {
                // Start the Python LSP server process
                val processBuilder = ProcessBuilder(pythonPath, serverScriptPath)
                processBuilder.redirectError(ProcessBuilder.Redirect.INHERIT)
                serverProcess = processBuilder.start()

                val inputStream: InputStream = serverProcess!!.inputStream
                val outputStream: OutputStream = serverProcess!!.outputStream

                // Create LSP launcher
                launcher = LSPLauncher.createClientLauncher(
                    this,
                    inputStream,
                    outputStream
                )

                // Start listening
                launcher!!.startListening()
                languageServer = launcher!!.remoteProxy

                // Initialize the server
                val initParams = InitializeParams().apply {
                    processId = ProcessHandle.current().pid().toInt()
                    rootUri = project.basePath?.let { URI.create("file://$it").toString() }
                    capabilities = ClientCapabilities().apply {
                        textDocument = TextDocumentClientCapabilities().apply {
                            codeAction = CodeActionCapabilities().apply {
                                codeActionLiteralSupport = CodeActionCapabilities.CodeActionLiteralSupport().apply {
                                    codeActionKind = CodeActionCapabilities.CodeActionKindCapabilities().apply {
                                        valueSet = listOf(
                                            CodeActionKind.QuickFix,
                                            CodeActionKind.Refactor,
                                            CodeActionKind.RefactorExtract,
                                            CodeActionKind.RefactorInline,
                                            CodeActionKind.RefactorRewrite,
                                            CodeActionKind.Source
                                        )
                                    }
                                }
                            }
                            diagnostic = DiagnosticCapabilities()
                            hover = HoverCapabilities()
                        }
                        workspace = WorkspaceClientCapabilities().apply {
                            executeCommand = ExecuteCommandCapabilities()
                        }
                    }
                }

                val initResult = languageServer!!.initialize(initParams)
                    .get(CONNECTION_TIMEOUT, TimeUnit.MILLISECONDS)

                languageServer!!.initialized(InitializedParams())

                isConnected = true
                log.info("Coach LSP client connected successfully")

                initResult
            } catch (e: Exception) {
                log.error("Failed to start Coach LSP server", e)
                cleanup()
                throw e
            }
        }
    }

    /**
     * Stops the LSP server and cleans up resources.
     */
    fun stop() {
        if (!isConnected) {
            return
        }

        try {
            languageServer?.shutdown()?.get(5, TimeUnit.SECONDS)
            languageServer?.exit()
        } catch (e: Exception) {
            log.warn("Error during LSP server shutdown", e)
        } finally {
            cleanup()
        }
    }

    private fun cleanup() {
        isConnected = false
        languageServer = null
        launcher = null

        serverProcess?.let { process ->
            if (process.isAlive) {
                process.destroy()
                if (!process.waitFor(5, TimeUnit.SECONDS)) {
                    process.destroyForcibly()
                }
            }
        }
        serverProcess = null
    }

    /**
     * Executes a custom Coach command.
     */
    fun executeCommand(command: String, arguments: List<Any>): CompletableFuture<Any> {
        if (!isConnected) {
            return CompletableFuture.failedFuture(
                IllegalStateException("LSP client not connected")
            )
        }

        val params = ExecuteCommandParams().apply {
            this.command = command
            this.arguments = arguments
        }

        return languageServer!!.workspaceService
            .executeCommand(params)
            .orTimeout(REQUEST_TIMEOUT, TimeUnit.MILLISECONDS)
    }

    /**
     * Runs a specific wizard on the given code.
     */
    fun runWizard(
        wizardName: String,
        code: String,
        filePath: String,
        role: String = "developer",
        task: String = "",
        context: String = ""
    ): CompletableFuture<WizardResult> {
        val arguments = listOf(
            wizardName,
            mapOf(
                "code" to code,
                "filePath" to filePath,
                "role" to role,
                "task" to task,
                "context" to context
            )
        )

        return executeCommand("coach/runWizard", arguments)
            .thenApply { result ->
                parseWizardResult(result)
            }
    }

    /**
     * Runs multiple wizards in collaboration mode.
     */
    fun multiWizardReview(
        wizards: List<String>,
        code: String,
        filePath: String,
        scenario: String = "",
        context: String = ""
    ): CompletableFuture<MultiWizardResult> {
        val arguments = listOf(
            wizards,
            mapOf(
                "code" to code,
                "filePath" to filePath,
                "scenario" to scenario,
                "context" to context
            )
        )

        return executeCommand("coach/multiWizardReview", arguments)
            .thenApply { result ->
                parseMultiWizardResult(result)
            }
    }

    /**
     * Gets Level 4 predictions for the given code.
     */
    fun predict(
        code: String,
        filePath: String,
        timeframe: Int = 60
    ): CompletableFuture<List<PredictedImpact>> {
        val arguments = listOf(
            mapOf(
                "code" to code,
                "filePath" to filePath,
                "timeframe" to timeframe
            )
        )

        return executeCommand("coach/predict", arguments)
            .thenApply { result ->
                parsePredictions(result)
            }
    }

    /**
     * Checks the health status of the LSP server.
     */
    fun healthCheck(): CompletableFuture<HealthStatus> {
        return executeCommand("coach/healthCheck", emptyList())
            .thenApply { result ->
                parseHealthStatus(result)
            }
    }

    /**
     * Notifies the server that a document was opened.
     */
    fun didOpenTextDocument(uri: String, languageId: String, version: Int, text: String) {
        if (!isConnected) return

        val params = DidOpenTextDocumentParams().apply {
            textDocument = TextDocumentItem(uri, languageId, version, text)
        }

        languageServer?.textDocumentService?.didOpen(params)
    }

    /**
     * Notifies the server that a document was changed.
     */
    fun didChangeTextDocument(uri: String, version: Int, text: String) {
        if (!isConnected) return

        val params = DidChangeTextDocumentParams().apply {
            textDocument = VersionedTextDocumentIdentifier(uri, version)
            contentChanges = listOf(
                TextDocumentContentChangeEvent().apply {
                    this.text = text
                }
            )
        }

        languageServer?.textDocumentService?.didChange(params)
    }

    /**
     * Notifies the server that a document was saved.
     */
    fun didSaveTextDocument(uri: String, text: String? = null) {
        if (!isConnected) return

        val params = DidSaveTextDocumentParams().apply {
            textDocument = TextDocumentIdentifier(uri)
            this.text = text
        }

        languageServer?.textDocumentService?.didSave(params)
    }

    /**
     * Notifies the server that a document was closed.
     */
    fun didCloseTextDocument(uri: String) {
        if (!isConnected) return

        val params = DidCloseTextDocumentParams().apply {
            textDocument = TextDocumentIdentifier(uri)
        }

        languageServer?.textDocumentService?.didClose(params)
    }

    // LanguageClient interface methods

    override fun telemetryEvent(params: Any?) {
        log.info("Telemetry event: $params")
    }

    override fun publishDiagnostics(diagnostics: PublishDiagnosticsParams) {
        // Diagnostics will be handled by the inspections
        log.debug("Received diagnostics for ${diagnostics.uri}")
    }

    override fun showMessage(params: MessageParams) {
        log.info("Server message [${params.type}]: ${params.message}")
    }

    override fun showMessageRequest(params: ShowMessageRequestParams): CompletableFuture<MessageActionItem> {
        log.info("Server message request: ${params.message}")
        return CompletableFuture.completedFuture(null)
    }

    override fun logMessage(params: MessageParams) {
        when (params.type) {
            MessageType.Error -> log.error(params.message)
            MessageType.Warning -> log.warn(params.message)
            MessageType.Info -> log.info(params.message)
            MessageType.Log -> log.debug(params.message)
            else -> log.debug(params.message)
        }
    }

    // Parsing methods

    private fun parseWizardResult(result: Any): WizardResult {
        // Parse the result from the LSP server
        @Suppress("UNCHECKED_CAST")
        val resultMap = result as? Map<String, Any> ?: throw IllegalArgumentException("Invalid wizard result")

        return WizardResult(
            wizard = resultMap["wizard"] as? String ?: "",
            diagnosis = resultMap["diagnosis"] as? String ?: "",
            severity = Severity.valueOf((resultMap["severity"] as? String ?: "INFO").uppercase()),
            recommendations = (resultMap["recommendations"] as? List<*>)?.filterIsInstance<String>() ?: emptyList(),
            codeExamples = (resultMap["codeExamples"] as? List<*>)?.map { parseCodeExample(it) } ?: emptyList(),
            estimatedTime = resultMap["estimatedTime"] as? String,
            references = (resultMap["references"] as? List<*>)?.filterIsInstance<String>() ?: emptyList()
        )
    }

    private fun parseMultiWizardResult(result: Any): MultiWizardResult {
        @Suppress("UNCHECKED_CAST")
        val resultMap = result as? Map<String, Any> ?: throw IllegalArgumentException("Invalid multi-wizard result")

        return MultiWizardResult(
            scenario = resultMap["scenario"] as? String ?: "",
            wizards = (resultMap["wizards"] as? List<*>)?.filterIsInstance<String>() ?: emptyList(),
            results = (resultMap["results"] as? List<*>)?.map { parseWizardResult(it!!) } ?: emptyList(),
            collaboration = (resultMap["collaboration"] as? List<*>)?.map { parseCollaboration(it) } ?: emptyList(),
            summary = resultMap["summary"] as? String ?: ""
        )
    }

    private fun parsePredictions(result: Any): List<PredictedImpact> {
        @Suppress("UNCHECKED_CAST")
        val predictions = result as? List<*> ?: return emptyList()

        return predictions.mapNotNull { prediction ->
            @Suppress("UNCHECKED_CAST")
            val predMap = prediction as? Map<String, Any> ?: return@mapNotNull null

            PredictedImpact(
                issue = predMap["issue"] as? String ?: "",
                timeframe = predMap["timeframe"] as? Int ?: 30,
                severity = Severity.valueOf((predMap["severity"] as? String ?: "INFO").uppercase()),
                impact = predMap["impact"] as? String ?: "",
                preventiveAction = predMap["preventiveAction"] as? String ?: "",
                confidence = (predMap["confidence"] as? Number)?.toDouble() ?: 0.0
            )
        }
    }

    private fun parseHealthStatus(result: Any): HealthStatus {
        @Suppress("UNCHECKED_CAST")
        val statusMap = result as? Map<String, Any> ?: throw IllegalArgumentException("Invalid health status")

        return HealthStatus(
            status = statusMap["status"] as? String ?: "unknown",
            version = statusMap["version"] as? String ?: "",
            uptime = (statusMap["uptime"] as? Number)?.toLong() ?: 0L
        )
    }

    private fun parseCodeExample(example: Any): CodeExample {
        @Suppress("UNCHECKED_CAST")
        val exampleMap = example as? Map<String, Any> ?: throw IllegalArgumentException("Invalid code example")

        return CodeExample(
            before = exampleMap["before"] as? String,
            after = exampleMap["after"] as? String ?: "",
            explanation = exampleMap["explanation"] as? String ?: ""
        )
    }

    private fun parseCollaboration(collab: Any): CollaborationInfo {
        @Suppress("UNCHECKED_CAST")
        val collabMap = collab as? Map<String, Any> ?: throw IllegalArgumentException("Invalid collaboration info")

        return CollaborationInfo(
            wizards = (collabMap["wizards"] as? List<*>)?.filterIsInstance<String>() ?: emptyList(),
            insight = collabMap["insight"] as? String ?: ""
        )
    }

    fun dispose() {
        scope.cancel()
        stop()
    }
}

// Data classes

enum class Severity {
    ERROR, WARNING, INFO
}

data class WizardResult(
    val wizard: String,
    val diagnosis: String,
    val severity: Severity,
    val recommendations: List<String>,
    val codeExamples: List<CodeExample>,
    val estimatedTime: String?,
    val references: List<String>
)

data class MultiWizardResult(
    val scenario: String,
    val wizards: List<String>,
    val results: List<WizardResult>,
    val collaboration: List<CollaborationInfo>,
    val summary: String
)

data class PredictedImpact(
    val issue: String,
    val timeframe: Int,
    val severity: Severity,
    val impact: String,
    val preventiveAction: String,
    val confidence: Double
)

data class CodeExample(
    val before: String?,
    val after: String,
    val explanation: String
)

data class CollaborationInfo(
    val wizards: List<String>,
    val insight: String
)

data class HealthStatus(
    val status: String,
    val version: String,
    val uptime: Long
)
