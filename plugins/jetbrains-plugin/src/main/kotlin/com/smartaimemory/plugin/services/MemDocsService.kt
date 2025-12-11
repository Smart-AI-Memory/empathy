package com.smartaimemory.plugin.services

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.smartaimemory.plugin.models.EmpathyAnalysis
import com.smartaimemory.plugin.models.Issue
import com.smartaimemory.plugin.models.Prediction
import com.smartaimemory.plugin.models.CodeSymbol
import java.io.File

/**
 * Service for reading and parsing MemDocs analysis results
 *
 * This service provides access to Empathy Framework analysis results
 * stored in the .memdocs/ directory.
 */
@Service(Service.Level.PROJECT)
class MemDocsService(private val project: Project) {

    /**
     * Get analysis results for a specific file
     *
     * @param filePath Absolute path to the file
     * @return EmpathyAnalysis object or null if no analysis exists
     */
    fun getAnalysis(filePath: String): EmpathyAnalysis? {
        try {
            // Find .memdocs directory in project
            val memDocsDir = findMemDocsDirectory() ?: return null

            // Convert file path to MemDocs identifier
            val fileIdentifier = getFileIdentifier(filePath)

            // Read index.json
            val indexFile = File(memDocsDir, "docs/$fileIdentifier/index.json")
            if (!indexFile.exists()) {
                return null
            }

            val jsonContent = indexFile.readText()
            return parseAnalysisJson(jsonContent, filePath)

        } catch (e: Exception) {
            // Log error but don't crash
            System.err.println("Error reading MemDocs analysis: ${e.message}")
            return null
        }
    }

    /**
     * Find the .memdocs directory in the project
     */
    private fun findMemDocsDirectory(): File? {
        val projectPath = project.basePath ?: return null
        val memDocsDir = File(projectPath, ".memdocs")
        return if (memDocsDir.exists() && memDocsDir.isDirectory) memDocsDir else null
    }

    /**
     * Convert file path to MemDocs identifier
     * Example: /path/to/project/src/auth/login.py -> login
     */
    private fun getFileIdentifier(filePath: String): String {
        val file = File(filePath)
        return file.nameWithoutExtension
    }

    /**
     * Parse JSON content into EmpathyAnalysis object
     */
    private fun parseAnalysisJson(jsonContent: String, filePath: String): EmpathyAnalysis {
        // Simple JSON parsing (in production, use a proper JSON library like Gson or kotlinx.serialization)
        val issues = mutableListOf<Issue>()
        val predictions = mutableListOf<Prediction>()
        val symbols = mutableListOf<CodeSymbol>()

        // For now, use a basic parser
        // TODO: Replace with proper JSON library
        val issuesRegex = """"severity":\s*"([^"]+)"[^}]*"category":\s*"([^"]+)"[^}]*"description":\s*"([^"]+)"[^}]*"line_number":\s*(\d+)""".toRegex()
        issuesRegex.findAll(jsonContent).forEach { match ->
            issues.add(Issue(
                severity = match.groupValues[1],
                category = match.groupValues[2],
                description = match.groupValues[3],
                lineNumber = match.groupValues[4].toInt()
            ))
        }

        val predictionsRegex = """"confidence":\s*(\d+)[^}]*"timeline":\s*"([^"]+)"[^}]*"prediction":\s*"([^"]+)"[^}]*"impact":\s*"([^"]+)"""".toRegex()
        predictionsRegex.findAll(jsonContent).forEach { match ->
            predictions.add(Prediction(
                confidence = match.groupValues[1].toInt(),
                timeline = match.groupValues[2],
                prediction = match.groupValues[3],
                impact = match.groupValues[4]
            ))
        }

        val symbolsRegex = """"name":\s*"([^"]+)"[^}]*"type":\s*"([^"]+)"[^}]*"line_number":\s*(\d+)""".toRegex()
        symbolsRegex.findAll(jsonContent).forEach { match ->
            symbols.add(CodeSymbol(
                name = match.groupValues[1],
                type = match.groupValues[2],
                lineNumber = match.groupValues[3].toInt(),
                filePath = filePath
            ))
        }

        return EmpathyAnalysis(
            filePath = filePath,
            language = detectLanguage(filePath),
            issues = issues,
            predictions = predictions,
            symbols = symbols
        )
    }

    /**
     * Detect programming language from file extension
     */
    private fun detectLanguage(filePath: String): String {
        return when (File(filePath).extension) {
            "py" -> "python"
            "js" -> "javascript"
            "ts" -> "typescript"
            "java" -> "java"
            "kt" -> "kotlin"
            "go" -> "go"
            "rs" -> "rust"
            else -> "unknown"
        }
    }

    /**
     * Refresh analysis cache for a file
     */
    fun refreshCache(filePath: String) {
        // TODO: Implement cache refresh logic
    }

    /**
     * Check if analysis exists for a file
     */
    fun hasAnalysis(filePath: String): Boolean {
        return getAnalysis(filePath) != null
    }

    /**
     * Get all files with analysis results
     */
    fun getAnalyzedFiles(): List<String> {
        // TODO: Scan .memdocs/docs/ directory
        return emptyList()
    }

    /**
     * Semantic search across all analysis results
     */
    fun semanticSearch(query: String, limit: Int = 10): List<EmpathyAnalysis> {
        // TODO: Implement FAISS vector search
        return emptyList()
    }

    // ===== STUB IMPLEMENTATION (for testing) =====

    private fun createStubAnalysis(filePath: String): EmpathyAnalysis? {
        // Return null for now - will be replaced with actual implementation
        return null

        // Example stub data (uncomment for testing UI):
        /*
        return EmpathyAnalysis(
            filePath = filePath,
            language = "python",
            issues = listOf(
                Issue(
                    severity = "high",
                    category = "security",
                    description = "Potential SQL injection vulnerability",
                    lineNumber = 42
                ),
                Issue(
                    severity = "medium",
                    category = "performance",
                    description = "N+1 query detected",
                    lineNumber = 78
                )
            ),
            predictions = listOf(
                Prediction(
                    confidence = 85,
                    timeline = "2 weeks",
                    prediction = "Database connection pool will be exhausted under high load",
                    impact = "Service degradation or outages"
                )
            ),
            symbols = listOf(
                CodeSymbol(
                    name = "process_payment",
                    type = "function",
                    lineNumber = 25,
                    filePath = filePath,
                    signature = "def process_payment(amount: float, customer_id: str)"
                ),
                CodeSymbol(
                    name = "PaymentProcessor",
                    type = "class",
                    lineNumber = 10,
                    filePath = filePath
                )
            )
        )
        */
    }
}
