package com.smartaimemory.plugin.ui

import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.ContentFactory
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTabbedPane
import com.intellij.ui.table.JBTable
import com.smartaimemory.plugin.services.MemDocsService
import com.smartaimemory.plugin.models.EmpathyAnalysis
import com.smartaimemory.plugin.models.Issue
import com.smartaimemory.plugin.models.Prediction
import com.smartaimemory.plugin.models.CodeSymbol
import java.awt.BorderLayout
import java.awt.Color
import java.awt.Component
import javax.swing.*
import javax.swing.table.DefaultTableCellRenderer
import javax.swing.table.DefaultTableModel
import javax.swing.tree.DefaultMutableTreeNode
import javax.swing.tree.DefaultTreeModel

/**
 * Tool window displaying Empathy Framework analysis results
 *
 * This tool window provides three tabs:
 * 1. Issues - Security, performance, and quality issues
 * 2. Predictions - Level 4 Anticipatory predictions
 * 3. Code Structure - Symbol tree navigation
 */
class AnalysisResultsToolWindow : ToolWindowFactory {

    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val panel = AnalysisResultsPanel(project)
        val content = ContentFactory.getInstance().createContent(panel, "", false)
        toolWindow.contentManager.addContent(content)
    }
}

/**
 * Main panel containing the analysis results UI
 */
class AnalysisResultsPanel(private val project: Project) : JPanel(BorderLayout()) {

    private val memDocsService = project.getService(MemDocsService::class.java)
    private val tabbedPane = JBTabbedPane()

    // Tab 1: Issues
    private val issuesTable = JBTable()
    private val issuesModel = DefaultTableModel(
        arrayOf("Severity", "Category", "Description", "Line"),
        0
    ).apply {
        // Make table read-only
        override fun isCellEditable(row: Int, column: Int) = false
    }

    // Tab 2: Predictions
    private val predictionsTable = JBTable()
    private val predictionsModel = DefaultTableModel(
        arrayOf("Confidence", "Timeline", "Prediction", "Impact"),
        0
    ).apply {
        override fun isCellEditable(row: Int, column: Int) = false
    }

    // Tab 3: Symbols
    private val symbolsTree = JTree()

    init {
        setupUI()
    }

    private fun setupUI() {
        // Issues tab
        issuesTable.model = issuesModel
        issuesTable.setDefaultRenderer(Any::class.java, IssueSeverityRenderer())
        issuesTable.rowHeight = 25
        issuesTable.setShowGrid(true)
        issuesTable.gridColor = Color(60, 60, 60)
        val issuesPanel = JBScrollPane(issuesTable)
        tabbedPane.addTab("Issues", issuesPanel)

        // Predictions tab
        predictionsTable.model = predictionsModel
        predictionsTable.setDefaultRenderer(Any::class.java, PredictionConfidenceRenderer())
        predictionsTable.rowHeight = 25
        predictionsTable.setShowGrid(true)
        predictionsTable.gridColor = Color(60, 60, 60)
        val predictionsPanel = JBScrollPane(predictionsTable)
        tabbedPane.addTab("Predictions", predictionsPanel)

        // Symbols tab
        symbolsTree.isRootVisible = true
        symbolsTree.showsRootHandles = true
        val symbolsPanel = JBScrollPane(symbolsTree)
        tabbedPane.addTab("Code Structure", symbolsPanel)

        add(tabbedPane, BorderLayout.CENTER)

        // Bottom panel with refresh button and status
        val bottomPanel = JPanel(BorderLayout())
        val refreshButton = JButton("Refresh Analysis")
        refreshButton.addActionListener { refreshAnalysis() }
        bottomPanel.add(refreshButton, BorderLayout.WEST)

        val statusLabel = JLabel("Ready")
        statusLabel.horizontalAlignment = SwingConstants.RIGHT
        statusLabel.border = BorderFactory.createEmptyBorder(5, 5, 5, 5)
        bottomPanel.add(statusLabel, BorderLayout.EAST)

        add(bottomPanel, BorderLayout.SOUTH)
    }

    /**
     * Load analysis results for a specific file
     */
    fun loadAnalysis(filePath: String) {
        val analysis = memDocsService.getAnalysis(filePath) ?: run {
            showNoAnalysisMessage()
            return
        }

        // Clear existing data
        issuesModel.rowCount = 0
        predictionsModel.rowCount = 0

        // Populate issues
        analysis.issues.forEach { issue ->
            issuesModel.addRow(arrayOf(
                issue.severity,
                issue.category,
                issue.description,
                issue.lineNumber
            ))
        }

        // Populate predictions
        analysis.predictions.forEach { prediction ->
            predictionsModel.addRow(arrayOf(
                "${prediction.confidence}%",
                prediction.timeline,
                prediction.prediction,
                prediction.impact
            ))
        }

        // Populate symbols tree
        updateSymbolsTree(analysis.symbols)

        // Update status
        updateStatus(analysis)
    }

    /**
     * Update the symbols tree with code structure
     */
    private fun updateSymbolsTree(symbols: List<CodeSymbol>) {
        val root = DefaultMutableTreeNode("Code Structure")

        // Group symbols by type
        val symbolsByType = symbols.groupBy { it.type }

        // Create nodes for each type
        symbolsByType.forEach { (type, symbolList) ->
            val typeNode = DefaultMutableTreeNode("${type.capitalize()}s (${symbolList.size})")

            symbolList.forEach { symbol ->
                val symbolNode = DefaultMutableTreeNode(
                    "${symbol.name} (line ${symbol.lineNumber})"
                )
                typeNode.add(symbolNode)
            }

            root.add(typeNode)
        }

        symbolsTree.model = DefaultTreeModel(root)

        // Expand root by default
        symbolsTree.expandRow(0)
    }

    /**
     * Show message when no analysis is available
     */
    private fun showNoAnalysisMessage() {
        issuesModel.rowCount = 0
        predictionsModel.rowCount = 0

        issuesModel.addRow(arrayOf(
            "INFO",
            "No Analysis",
            "No analysis found. Right-click a file and select 'Analyze with Empathy Framework'",
            "-"
        ))

        val root = DefaultMutableTreeNode("No Analysis Available")
        symbolsTree.model = DefaultTreeModel(root)
    }

    /**
     * Update status label with analysis summary
     */
    private fun updateStatus(analysis: EmpathyAnalysis) {
        val issueCount = analysis.issues.size
        val predictionCount = analysis.predictions.size
        val symbolCount = analysis.symbols.size

        val statusText = "$issueCount issues, $predictionCount predictions, $symbolCount symbols"

        // Find status label and update it
        (getComponent(1) as? JPanel)?.let { bottomPanel ->
            (bottomPanel.getComponent(1) as? JLabel)?.text = statusText
        }
    }

    /**
     * Refresh analysis for currently open file
     */
    private fun refreshAnalysis() {
        // Get currently open file
        val editor = FileEditorManager.getInstance(project).selectedTextEditor
        if (editor == null) {
            JOptionPane.showMessageDialog(
                this,
                "No file is currently open",
                "Refresh Analysis",
                JOptionPane.INFORMATION_MESSAGE
            )
            return
        }

        val virtualFile = FileDocumentManager.getInstance().getFile(editor.document)
        if (virtualFile == null) {
            JOptionPane.showMessageDialog(
                this,
                "Unable to identify current file",
                "Refresh Analysis",
                JOptionPane.ERROR_MESSAGE
            )
            return
        }

        // Reload analysis for current file
        loadAnalysis(virtualFile.path)
    }
}

/**
 * Custom renderer for issue severity
 * Color codes issues based on severity level
 */
class IssueSeverityRenderer : DefaultTableCellRenderer() {

    override fun getTableCellRendererComponent(
        table: JTable?,
        value: Any?,
        isSelected: Boolean,
        hasFocus: Boolean,
        row: Int,
        column: Int
    ): Component {
        val component = super.getTableCellRendererComponent(
            table, value, isSelected, hasFocus, row, column
        ) as JLabel

        // Color code the severity column
        if (column == 0 && value is String) {
            val color = when (value.lowercase()) {
                "critical" -> Color(220, 50, 47)   // Red
                "high" -> Color(255, 140, 0)       // Orange
                "medium" -> Color(255, 215, 0)     // Gold
                "low" -> Color(150, 150, 150)      // Gray
                "info" -> Color(100, 149, 237)     // Cornflower blue
                else -> Color(200, 200, 200)
            }

            if (!isSelected) {
                component.foreground = color
                component.font = component.font.deriveFont(java.awt.Font.BOLD)
            }
        }

        return component
    }
}

/**
 * Custom renderer for prediction confidence
 * Color codes predictions based on confidence level
 */
class PredictionConfidenceRenderer : DefaultTableCellRenderer() {

    override fun getTableCellRendererComponent(
        table: JTable?,
        value: Any?,
        isSelected: Boolean,
        hasFocus: Boolean,
        row: Int,
        column: Int
    ): Component {
        val component = super.getTableCellRendererComponent(
            table, value, isSelected, hasFocus, row, column
        ) as JLabel

        // Color code the confidence column
        if (column == 0 && value is String) {
            val confidence = value.removeSuffix("%").toIntOrNull() ?: 0

            val color = when {
                confidence >= 80 -> Color(50, 205, 50)   // Lime green
                confidence >= 60 -> Color(154, 205, 50)  // Yellow green
                confidence >= 40 -> Color(255, 215, 0)   // Gold
                else -> Color(150, 150, 150)             // Gray
            }

            if (!isSelected) {
                component.foreground = color
                component.font = component.font.deriveFont(java.awt.Font.BOLD)
            }
        }

        return component
    }
}
