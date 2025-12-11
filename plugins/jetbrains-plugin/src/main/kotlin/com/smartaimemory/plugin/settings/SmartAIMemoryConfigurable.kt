package com.smartaimemory.plugin.settings

import com.intellij.openapi.options.Configurable
import com.intellij.openapi.project.Project
import javax.swing.*

/**
 * Settings UI panel for SmartAI Memory plugin
 */
class SmartAIMemoryConfigurable(
    private val project: Project
) : Configurable {

    private var settingsPanel: SmartAIMemorySettingsPanel? = null

    override fun getDisplayName(): String = "SmartAI Memory"

    override fun createComponent(): JComponent {
        settingsPanel = SmartAIMemorySettingsPanel()
        reset() // Load current settings
        return settingsPanel!!
    }

    override fun isModified(): Boolean {
        val settings = SmartAIMemorySettings.getInstance(project)
        val panel = settingsPanel ?: return false

        return panel.empathyServiceUrlField.text != settings.empathyServiceUrl ||
               panel.apiKeyField.text != settings.apiKey ||
               panel.autoAnalyzeCheckbox.isSelected != settings.autoAnalyzeOnSave ||
               panel.showAnnotationsCheckbox.isSelected != settings.showInlineAnnotations
    }

    override fun apply() {
        val settings = SmartAIMemorySettings.getInstance(project)
        val panel = settingsPanel ?: return

        settings.empathyServiceUrl = panel.empathyServiceUrlField.text
        settings.apiKey = panel.apiKeyField.text
        settings.autoAnalyzeOnSave = panel.autoAnalyzeCheckbox.isSelected
        settings.showInlineAnnotations = panel.showAnnotationsCheckbox.isSelected
    }

    override fun reset() {
        val settings = SmartAIMemorySettings.getInstance(project)
        settingsPanel?.loadSettings(settings)
    }
}

/**
 * UI Panel for settings
 */
class SmartAIMemorySettingsPanel : JPanel() {
    val empathyServiceUrlField = JTextField(30)
    val apiKeyField = JPasswordField(30)
    val autoAnalyzeCheckbox = JCheckBox("Auto-analyze on save")
    val showAnnotationsCheckbox = JCheckBox("Show inline annotations")

    init {
        layout = BoxLayout(this, BoxLayout.Y_AXIS)
        border = BorderFactory.createEmptyBorder(10, 10, 10, 10)

        // Empathy Service URL
        add(JLabel("Empathy Service URL:"))
        add(empathyServiceUrlField)
        add(Box.createVerticalStrut(10))

        // API Key
        add(JLabel("API Key:"))
        add(apiKeyField)
        add(Box.createVerticalStrut(10))

        // Auto-analyze checkbox
        add(autoAnalyzeCheckbox)
        add(Box.createVerticalStrut(5))

        // Show annotations checkbox
        add(showAnnotationsCheckbox)
        add(Box.createVerticalStrut(20))

        // Info label
        add(JLabel("<html><i>Configure your SmartAI Memory settings.<br>" +
                   "Empathy Service should point to your local or cloud API endpoint.</i></html>"))
    }

    fun loadSettings(settings: SmartAIMemorySettings) {
        empathyServiceUrlField.text = settings.empathyServiceUrl
        apiKeyField.text = settings.apiKey
        autoAnalyzeCheckbox.isSelected = settings.autoAnalyzeOnSave
        showAnnotationsCheckbox.isSelected = settings.showInlineAnnotations
    }
}
