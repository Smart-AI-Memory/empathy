package com.deepstudyai.coach.settings

import com.deepstudyai.coach.services.CoachSettingsService
import com.intellij.openapi.components.service
import com.intellij.openapi.fileChooser.FileChooserDescriptorFactory
import com.intellij.openapi.options.Configurable
import com.intellij.openapi.ui.TextFieldWithBrowseButton
import com.intellij.ui.components.JBCheckBox
import com.intellij.ui.components.JBTextField
import java.awt.GridBagConstraints
import java.awt.GridBagLayout
import java.awt.Insets
import javax.swing.*

/**
 * Application-level settings configurable for Coach.
 */
class CoachSettingsConfigurable : Configurable {

    private val settings = service<CoachSettingsService>()
    private var panel: JPanel? = null

    // LSP Server fields
    private val pythonPathField = TextFieldWithBrowseButton()
    private val serverScriptPathField = TextFieldWithBrowseButton()
    private val autoStartCheckbox = JBCheckBox("Auto-start LSP server")
    private val serverPortField = JBTextField()

    // API Configuration fields
    private val apiProviderCombo = JComboBox(arrayOf("openai", "anthropic", "local"))
    private val apiKeyField = JPasswordField()
    private val apiEndpointField = JBTextField()
    private val modelNameField = JBTextField()

    // Analysis Settings fields
    private val enableRealTimeCheckbox = JBCheckBox("Enable real-time analysis")
    private val debounceField = JBTextField()
    private val maxConcurrentField = JBTextField()

    // Level 4 Predictions fields
    private val enablePredictionsCheckbox = JBCheckBox("Enable Level 4 predictions")
    private val timeframeField = JBTextField()
    private val confidenceField = JBTextField()

    // Cache Settings fields
    private val enableCacheCheckbox = JBCheckBox("Enable caching")
    private val cacheExpirationField = JBTextField()
    private val maxCacheSizeField = JBTextField()

    // UI Settings fields
    private val showInlineHintsCheckbox = JBCheckBox("Show inline hints")
    private val showGutterIconsCheckbox = JBCheckBox("Show gutter icons")
    private val showToolWindowCheckbox = JBCheckBox("Show tool window")

    // Multi-Wizard Collaboration fields
    private val enableCollaborationCheckbox = JBCheckBox("Enable multi-wizard collaboration")
    private val autoSuggestCollabCheckbox = JBCheckBox("Auto-suggest collaboration")

    // Privacy fields
    private val enableTelemetryCheckbox = JBCheckBox("Enable telemetry")
    private val shareUsageCheckbox = JBCheckBox("Share anonymous usage data")

    // Advanced fields
    private val debugModeCheckbox = JBCheckBox("Debug mode")
    private val logLevelCombo = JComboBox(arrayOf("DEBUG", "INFO", "WARN", "ERROR"))

    override fun createComponent(): JComponent {
        val mainPanel = JPanel(GridBagLayout())
        val gbc = GridBagConstraints().apply {
            fill = GridBagConstraints.HORIZONTAL
            anchor = GridBagConstraints.WEST
            insets = Insets(5, 5, 5, 5)
            weightx = 1.0
        }

        // Configure file choosers
        pythonPathField.addBrowseFolderListener(
            "Select Python Executable",
            "Choose the Python interpreter to use",
            null,
            FileChooserDescriptorFactory.createSingleFileDescriptor()
        )

        serverScriptPathField.addBrowseFolderListener(
            "Select LSP Server Script",
            "Choose the Coach LSP server script",
            null,
            FileChooserDescriptorFactory.createSingleFileDescriptor()
        )

        var row = 0

        // LSP Server Configuration
        addSectionTitle(mainPanel, gbc, row++, "LSP Server Configuration")
        addLabeledField(mainPanel, gbc, row++, "Python Path:", pythonPathField)
        addLabeledField(mainPanel, gbc, row++, "Server Script Path:", serverScriptPathField)
        addField(mainPanel, gbc, row++, autoStartCheckbox)
        addLabeledField(mainPanel, gbc, row++, "Server Port (0=auto):", serverPortField)

        // API Configuration
        addSectionTitle(mainPanel, gbc, row++, "API Configuration")
        addLabeledField(mainPanel, gbc, row++, "API Provider:", apiProviderCombo)
        addLabeledField(mainPanel, gbc, row++, "API Key:", apiKeyField)
        addLabeledField(mainPanel, gbc, row++, "API Endpoint:", apiEndpointField)
        addLabeledField(mainPanel, gbc, row++, "Model Name:", modelNameField)

        // Analysis Settings
        addSectionTitle(mainPanel, gbc, row++, "Analysis Settings")
        addField(mainPanel, gbc, row++, enableRealTimeCheckbox)
        addLabeledField(mainPanel, gbc, row++, "Debounce (ms):", debounceField)
        addLabeledField(mainPanel, gbc, row++, "Max Concurrent:", maxConcurrentField)

        // Level 4 Predictions
        addSectionTitle(mainPanel, gbc, row++, "Level 4 Predictions")
        addField(mainPanel, gbc, row++, enablePredictionsCheckbox)
        addLabeledField(mainPanel, gbc, row++, "Timeframe (days):", timeframeField)
        addLabeledField(mainPanel, gbc, row++, "Confidence Threshold:", confidenceField)

        // Cache Settings
        addSectionTitle(mainPanel, gbc, row++, "Cache Settings")
        addField(mainPanel, gbc, row++, enableCacheCheckbox)
        addLabeledField(mainPanel, gbc, row++, "Expiration (minutes):", cacheExpirationField)
        addLabeledField(mainPanel, gbc, row++, "Max Size:", maxCacheSizeField)

        // UI Settings
        addSectionTitle(mainPanel, gbc, row++, "UI Settings")
        addField(mainPanel, gbc, row++, showInlineHintsCheckbox)
        addField(mainPanel, gbc, row++, showGutterIconsCheckbox)
        addField(mainPanel, gbc, row++, showToolWindowCheckbox)

        // Multi-Wizard Collaboration
        addSectionTitle(mainPanel, gbc, row++, "Multi-Wizard Collaboration")
        addField(mainPanel, gbc, row++, enableCollaborationCheckbox)
        addField(mainPanel, gbc, row++, autoSuggestCollabCheckbox)

        // Privacy & Telemetry
        addSectionTitle(mainPanel, gbc, row++, "Privacy & Telemetry")
        addField(mainPanel, gbc, row++, enableTelemetryCheckbox)
        addField(mainPanel, gbc, row++, shareUsageCheckbox)

        // Advanced
        addSectionTitle(mainPanel, gbc, row++, "Advanced")
        addField(mainPanel, gbc, row++, debugModeCheckbox)
        addLabeledField(mainPanel, gbc, row++, "Log Level:", logLevelCombo)

        // Wrap in scroll pane
        panel = JPanel(BorderLayout()).apply {
            add(JScrollPane(mainPanel), BorderLayout.CENTER)
        }

        reset()
        return panel!!
    }

    private fun addSectionTitle(panel: JPanel, gbc: GridBagConstraints, row: Int, title: String) {
        gbc.gridx = 0
        gbc.gridy = row
        gbc.gridwidth = 2
        panel.add(JLabel("<html><b>$title</b></html>").apply {
            border = BorderFactory.createEmptyBorder(10, 0, 5, 0)
        }, gbc)
        gbc.gridwidth = 1
    }

    private fun addLabeledField(panel: JPanel, gbc: GridBagConstraints, row: Int, label: String, component: JComponent) {
        gbc.gridx = 0
        gbc.gridy = row
        gbc.weightx = 0.0
        panel.add(JLabel(label), gbc)

        gbc.gridx = 1
        gbc.weightx = 1.0
        panel.add(component, gbc)
    }

    private fun addField(panel: JPanel, gbc: GridBagConstraints, row: Int, component: JComponent) {
        gbc.gridx = 0
        gbc.gridy = row
        gbc.gridwidth = 2
        panel.add(component, gbc)
        gbc.gridwidth = 1
    }

    override fun isModified(): Boolean {
        val state = settings.state
        return pythonPathField.text != state.pythonPath ||
                serverScriptPathField.text != state.serverScriptPath ||
                autoStartCheckbox.isSelected != state.autoStartServer ||
                serverPortField.text.toIntOrNull() != state.serverPort ||
                apiProviderCombo.selectedItem != state.apiProvider ||
                String(apiKeyField.password) != state.apiKey ||
                apiEndpointField.text != state.apiEndpoint ||
                modelNameField.text != state.modelName ||
                enableRealTimeCheckbox.isSelected != state.enableRealTimeAnalysis ||
                debounceField.text.toIntOrNull() != state.analysisDebounceMs ||
                maxConcurrentField.text.toIntOrNull() != state.maxConcurrentAnalyses ||
                enablePredictionsCheckbox.isSelected != state.enablePredictions ||
                timeframeField.text.toIntOrNull() != state.predictionTimeframe ||
                confidenceField.text.toDoubleOrNull() != state.predictionConfidenceThreshold ||
                enableCacheCheckbox.isSelected != state.enableCaching ||
                cacheExpirationField.text.toIntOrNull() != state.cacheExpirationMinutes ||
                maxCacheSizeField.text.toIntOrNull() != state.maxCacheSize ||
                showInlineHintsCheckbox.isSelected != state.showInlineHints ||
                showGutterIconsCheckbox.isSelected != state.showGutterIcons ||
                showToolWindowCheckbox.isSelected != state.showToolWindow ||
                enableCollaborationCheckbox.isSelected != state.enableCollaboration ||
                autoSuggestCollabCheckbox.isSelected != state.autoSuggestCollaboration ||
                enableTelemetryCheckbox.isSelected != state.enableTelemetry ||
                shareUsageCheckbox.isSelected != state.shareAnonymousUsage ||
                debugModeCheckbox.isSelected != state.debugMode ||
                logLevelCombo.selectedItem != state.logLevel
    }

    override fun apply() {
        val state = settings.state
        state.pythonPath = pythonPathField.text
        state.serverScriptPath = serverScriptPathField.text
        state.autoStartServer = autoStartCheckbox.isSelected
        state.serverPort = serverPortField.text.toIntOrNull() ?: 0
        state.apiProvider = apiProviderCombo.selectedItem as String
        state.apiKey = String(apiKeyField.password)
        state.apiEndpoint = apiEndpointField.text
        state.modelName = modelNameField.text
        state.enableRealTimeAnalysis = enableRealTimeCheckbox.isSelected
        state.analysisDebounceMs = debounceField.text.toIntOrNull() ?: 1000
        state.maxConcurrentAnalyses = maxConcurrentField.text.toIntOrNull() ?: 3
        state.enablePredictions = enablePredictionsCheckbox.isSelected
        state.predictionTimeframe = timeframeField.text.toIntOrNull() ?: 60
        state.predictionConfidenceThreshold = confidenceField.text.toDoubleOrNull() ?: 0.7
        state.enableCaching = enableCacheCheckbox.isSelected
        state.cacheExpirationMinutes = cacheExpirationField.text.toIntOrNull() ?: 60
        state.maxCacheSize = maxCacheSizeField.text.toIntOrNull() ?: 1000
        state.showInlineHints = showInlineHintsCheckbox.isSelected
        state.showGutterIcons = showGutterIconsCheckbox.isSelected
        state.showToolWindow = showToolWindowCheckbox.isSelected
        state.enableCollaboration = enableCollaborationCheckbox.isSelected
        state.autoSuggestCollaboration = autoSuggestCollabCheckbox.isSelected
        state.enableTelemetry = enableTelemetryCheckbox.isSelected
        state.shareAnonymousUsage = shareUsageCheckbox.isSelected
        state.debugMode = debugModeCheckbox.isSelected
        state.logLevel = logLevelCombo.selectedItem as String
    }

    override fun reset() {
        val state = settings.state
        pythonPathField.text = state.pythonPath
        serverScriptPathField.text = state.serverScriptPath
        autoStartCheckbox.isSelected = state.autoStartServer
        serverPortField.text = state.serverPort.toString()
        apiProviderCombo.selectedItem = state.apiProvider
        apiKeyField.text = state.apiKey
        apiEndpointField.text = state.apiEndpoint
        modelNameField.text = state.modelName
        enableRealTimeCheckbox.isSelected = state.enableRealTimeAnalysis
        debounceField.text = state.analysisDebounceMs.toString()
        maxConcurrentField.text = state.maxConcurrentAnalyses.toString()
        enablePredictionsCheckbox.isSelected = state.enablePredictions
        timeframeField.text = state.predictionTimeframe.toString()
        confidenceField.text = state.predictionConfidenceThreshold.toString()
        enableCacheCheckbox.isSelected = state.enableCaching
        cacheExpirationField.text = state.cacheExpirationMinutes.toString()
        maxCacheSizeField.text = state.maxCacheSize.toString()
        showInlineHintsCheckbox.isSelected = state.showInlineHints
        showGutterIconsCheckbox.isSelected = state.showGutterIcons
        showToolWindowCheckbox.isSelected = state.showToolWindow
        enableCollaborationCheckbox.isSelected = state.enableCollaboration
        autoSuggestCollabCheckbox.isSelected = state.autoSuggestCollaboration
        enableTelemetryCheckbox.isSelected = state.enableTelemetry
        shareUsageCheckbox.isSelected = state.shareAnonymousUsage
        debugModeCheckbox.isSelected = state.debugMode
        logLevelCombo.selectedItem = state.logLevel
    }

    override fun getDisplayName(): String = "Coach"

    override fun disposeUIResources() {
        panel = null
    }
}
