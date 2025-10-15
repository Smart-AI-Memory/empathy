package com.deepstudyai.coach.listeners

import com.deepstudyai.coach.lsp.CoachLSPClient
import com.deepstudyai.coach.services.CoachCacheService
import com.deepstudyai.coach.services.CoachSettingsService
import com.intellij.openapi.components.service
import com.intellij.openapi.editor.Document
import com.intellij.openapi.editor.event.DocumentEvent
import com.intellij.openapi.editor.event.DocumentListener
import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.project.Project
import kotlinx.coroutines.*
import java.net.URI

/**
 * Document listener that tracks changes and notifies the LSP server.
 *
 * Implements real-time analysis with debouncing.
 */
class CoachDocumentListener(private val project: Project) : DocumentListener {

    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private val pendingUpdates = mutableMapOf<Document, Job>()

    override fun documentChanged(event: DocumentEvent) {
        val settings = service<CoachSettingsService>()
        if (!settings.state.enableRealTimeAnalysis) {
            return
        }

        val document = event.document
        val debounceMs = settings.state.analysisDebounceMs.toLong()

        // Cancel pending update for this document
        pendingUpdates[document]?.cancel()

        // Schedule new update with debouncing
        val job = scope.launch {
            delay(debounceMs)

            // Get file info
            val virtualFile = FileDocumentManager.getInstance().getFile(document) ?: return@launch
            val uri = URI.create("file://${virtualFile.path}").toString()
            val text = document.text

            // Invalidate cache for this file
            val cacheService = service<CoachCacheService>()
            cacheService.invalidateFile(virtualFile.path)

            // Notify LSP server of change
            try {
                val lspClient = CoachLSPClient.getInstance(project)
                lspClient.didChangeTextDocument(
                    uri = uri,
                    version = document.modificationStamp.toInt(),
                    text = text
                )
            } catch (e: Exception) {
                // Silently ignore LSP errors to avoid disrupting editing
            }
        }

        pendingUpdates[document] = job
    }

    fun dispose() {
        scope.cancel()
        pendingUpdates.clear()
    }
}
