package com.deepstudyai.coach.services

import com.intellij.openapi.components.*

/**
 * Application-level service for Coach settings.
 *
 * Stores global configuration that applies to all projects.
 */
@Service(Service.Level.APP)
@State(
    name = "CoachSettings",
    storages = [Storage("coach.xml")]
)
class CoachSettingsService : PersistentStateComponent<CoachSettingsService.State> {

    private var myState = State()

    companion object {
        fun getInstance(): CoachSettingsService = service()
    }

    override fun getState(): State {
        return myState
    }

    override fun loadState(state: State) {
        myState = state
    }

    /**
     * Settings state.
     */
    data class State(
        // LSP Server Configuration
        var pythonPath: String = "",
        var serverScriptPath: String = "",
        var autoStartServer: Boolean = true,
        var serverPort: Int = 0, // 0 means auto-assign

        // API Configuration
        var apiProvider: String = "openai", // openai, anthropic, local
        var apiKey: String = "",
        var apiEndpoint: String = "",
        var modelName: String = "gpt-4",

        // Analysis Settings
        var enableRealTimeAnalysis: Boolean = true,
        var analysisDebounceMs: Int = 1000,
        var maxConcurrentAnalyses: Int = 3,

        // Level 4 Predictions
        var enablePredictions: Boolean = true,
        var predictionTimeframe: Int = 60, // days
        var predictionConfidenceThreshold: Double = 0.7,

        // Cache Settings
        var enableCaching: Boolean = true,
        var cacheExpirationMinutes: Int = 60,
        var maxCacheSize: Int = 1000,

        // UI Settings
        var showInlineHints: Boolean = true,
        var showGutterIcons: Boolean = true,
        var showToolWindow: Boolean = true,

        // Wizard Settings
        var enabledWizards: MutableSet<String> = mutableSetOf(
            "SecurityWizard",
            "PerformanceWizard",
            "AccessibilityWizard",
            "DebuggingWizard",
            "TestingWizard",
            "RefactoringWizard",
            "DatabaseWizard",
            "APIWizard",
            "ScalingWizard",
            "ObservabilityWizard",
            "CICDWizard",
            "DocumentationWizard",
            "ComplianceWizard",
            "MigrationWizard",
            "MonitoringWizard",
            "LocalizationWizard"
        ),

        // Multi-Wizard Collaboration
        var enableCollaboration: Boolean = true,
        var autoSuggestCollaboration: Boolean = true,

        // Privacy & Telemetry
        var enableTelemetry: Boolean = true,
        var shareAnonymousUsage: Boolean = true,

        // Advanced
        var debugMode: Boolean = false,
        var logLevel: String = "INFO" // DEBUG, INFO, WARN, ERROR
    ) {
        // Helper methods
        fun isWizardEnabled(wizardId: String): Boolean {
            return enabledWizards.contains(wizardId)
        }

        fun enableWizard(wizardId: String) {
            enabledWizards.add(wizardId)
        }

        fun disableWizard(wizardId: String) {
            enabledWizards.remove(wizardId)
        }

        fun toggleWizard(wizardId: String) {
            if (isWizardEnabled(wizardId)) {
                disableWizard(wizardId)
            } else {
                enableWizard(wizardId)
            }
        }

        fun resetToDefaults() {
            pythonPath = ""
            serverScriptPath = ""
            autoStartServer = true
            serverPort = 0
            apiProvider = "openai"
            apiKey = ""
            apiEndpoint = ""
            modelName = "gpt-4"
            enableRealTimeAnalysis = true
            analysisDebounceMs = 1000
            maxConcurrentAnalyses = 3
            enablePredictions = true
            predictionTimeframe = 60
            predictionConfidenceThreshold = 0.7
            enableCaching = true
            cacheExpirationMinutes = 60
            maxCacheSize = 1000
            showInlineHints = true
            showGutterIcons = true
            showToolWindow = true
            enabledWizards = mutableSetOf(
                "SecurityWizard",
                "PerformanceWizard",
                "AccessibilityWizard",
                "DebuggingWizard",
                "TestingWizard",
                "RefactoringWizard",
                "DatabaseWizard",
                "APIWizard",
                "ScalingWizard",
                "ObservabilityWizard",
                "CICDWizard",
                "DocumentationWizard",
                "ComplianceWizard",
                "MigrationWizard",
                "MonitoringWizard",
                "LocalizationWizard"
            )
            enableCollaboration = true
            autoSuggestCollaboration = true
            enableTelemetry = true
            shareAnonymousUsage = true
            debugMode = false
            logLevel = "INFO"
        }
    }
}
