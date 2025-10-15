package com.deepstudyai.coach.ui

import com.deepstudyai.coach.lsp.Severity
import com.deepstudyai.coach.services.AnalysisService
import com.deepstudyai.coach.services.CoachProjectService
import com.deepstudyai.coach.services.WizardRegistry
import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.components.JBList
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.content.ContentFactory
import java.awt.BorderLayout
import java.awt.GridBagConstraints
import java.awt.GridBagLayout
import javax.swing.*

/**
 * Factory for creating the Coach tool window.
 *
 * The tool window displays analysis results, statistics, and provides
 * quick access to Coach features.
 */
class CoachToolWindowFactory : ToolWindowFactory {

    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val contentFactory = ContentFactory.getInstance()

        // Create main panel
        val mainPanel = CoachToolWindowPanel(project)
        val content = contentFactory.createContent(mainPanel, "", false)
        toolWindow.contentManager.addContent(content)
    }

    override fun shouldBeAvailable(project: Project): Boolean = true
}

/**
 * Main panel for the Coach tool window.
 */
class CoachToolWindowPanel(private val project: Project) : JPanel(BorderLayout()) {

    private val analysisService = AnalysisService.getInstance(project)
    private val wizardRegistry = WizardRegistry.getInstance(project)
    private val projectService = CoachProjectService.getInstance(project)

    private val statusLabel = JLabel("Ready")
    private val errorCountLabel = JLabel("Errors: 0")
    private val warningCountLabel = JLabel("Warnings: 0")
    private val infoCountLabel = JLabel("Info: 0")

    private val resultsListModel = DefaultListModel<String>()
    private val resultsList = JBList(resultsListModel)

    init {
        createUI()
        refreshResults()
    }

    private fun createUI() {
        // Top panel with status and statistics
        val topPanel = JPanel(GridBagLayout()).apply {
            border = BorderFactory.createEmptyBorder(10, 10, 10, 10)

            val gbc = GridBagConstraints().apply {
                fill = GridBagConstraints.HORIZONTAL
                weightx = 1.0
                gridx = 0
                gridy = 0
            }

            add(statusLabel, gbc)

            gbc.gridy++
            add(JPanel().apply {
                layout = BoxLayout(this, BoxLayout.X_AXIS)
                add(errorCountLabel)
                add(Box.createHorizontalStrut(20))
                add(warningCountLabel)
                add(Box.createHorizontalStrut(20))
                add(infoCountLabel)
            }, gbc)
        }

        // Center panel with results list
        val centerPanel = JPanel(BorderLayout()).apply {
            border = BorderFactory.createTitledBorder("Analysis Results")
            add(JBScrollPane(resultsList), BorderLayout.CENTER)
        }

        // Bottom panel with action buttons
        val bottomPanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = BorderFactory.createEmptyBorder(10, 10, 10, 10)

            add(JButton("Analyze Project").apply {
                addActionListener { analyzeProject() }
            })

            add(Box.createHorizontalStrut(10))

            add(JButton("Refresh").apply {
                addActionListener { refreshResults() }
            })

            add(Box.createHorizontalStrut(10))

            add(JButton("Clear").apply {
                addActionListener { clearResults() }
            })

            add(Box.createHorizontalGlue())

            add(JButton("Settings").apply {
                addActionListener { openSettings() }
            })
        }

        // Add all panels
        add(topPanel, BorderLayout.NORTH)
        add(centerPanel, BorderLayout.CENTER)
        add(bottomPanel, BorderLayout.SOUTH)
    }

    private fun analyzeProject() {
        statusLabel.text = "Analyzing project..."

        analysisService.analyzeProject { fileName, current, total ->
            SwingUtilities.invokeLater {
                statusLabel.text = "Analyzing: $fileName ($current/$total)"
            }
        }.invokeOnCompletion {
            SwingUtilities.invokeLater {
                statusLabel.text = "Analysis complete"
                refreshResults()
            }
        }
    }

    private fun refreshResults() {
        val results = analysisService.getAllAnalysisResults()
        val stats = analysisService.getStatistics()

        // Update statistics
        errorCountLabel.text = "Errors: ${stats.errors}"
        warningCountLabel.text = "Warnings: ${stats.warnings}"
        infoCountLabel.text = "Info: ${stats.infos}"

        // Update results list
        resultsListModel.clear()

        if (results.isEmpty()) {
            resultsListModel.addElement("No analysis results yet")
            resultsListModel.addElement("Click 'Analyze Project' to run analysis")
        } else {
            // Group by file
            val resultsByFile = results.groupBy { it.filePath }

            resultsByFile.forEach { (filePath, fileResults) ->
                val fileName = filePath.substringAfterLast('/')
                resultsListModel.addElement("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                resultsListModel.addElement("📄 $fileName")
                resultsListModel.addElement("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                fileResults.forEach { result ->
                    val icon = when (result.result.severity) {
                        Severity.ERROR -> "🔴"
                        Severity.WARNING -> "🟡"
                        Severity.INFO -> "🔵"
                    }

                    val wizardMetadata = wizardRegistry.getWizard(result.wizardId)
                    val wizardName = wizardMetadata?.name ?: result.wizardId

                    resultsListModel.addElement("  $icon $wizardName")
                    resultsListModel.addElement("     ${result.result.diagnosis}")

                    if (result.result.recommendations.isNotEmpty()) {
                        resultsListModel.addElement("     Recommendations:")
                        result.result.recommendations.take(2).forEach { rec ->
                            resultsListModel.addElement("       • ${rec.take(80)}...")
                        }
                    }

                    resultsListModel.addElement("")
                }
            }
        }

        // Update status
        val health = projectService.healthCheck().get()
        statusLabel.text = if (health.isHealthy) {
            "Ready (${health.lspServerVersion})"
        } else {
            "LSP Server: ${health.lspServerStatus}"
        }
    }

    private fun clearResults() {
        analysisService.clearResults()
        refreshResults()
        statusLabel.text = "Results cleared"
    }

    private fun openSettings() {
        // Open Coach settings
        com.intellij.openapi.options.ShowSettingsUtil.getInstance()
            .showSettingsDialog(project, "Coach")
    }
}
