package com.smartaimemory.plugin.services

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.smartaimemory.plugin.models.EmpathyAnalysis
import com.smartaimemory.plugin.settings.SmartAIMemorySettings
import java.net.HttpURLConnection
import java.net.URL

/**
 * Service for communicating with the Empathy Framework API
 */
@Service(Service.Level.PROJECT)
class EmpathyApiService(private val project: Project) {

    private val settings: SmartAIMemorySettings
        get() = project.getService(SmartAIMemorySettings::class.java)

    /**
     * Analyze code using the Empathy Framework API
     *
     * @param code Source code to analyze
     * @param language Programming language (python, javascript, etc.)
     * @param wizard Analysis wizard (security, performance, etc.)
     * @param tier Analysis tier (free, pro)
     * @return EmpathyAnalysis result
     */
    fun analyzeCode(
        code: String,
        language: String,
        wizard: String = "security",
        tier: String = "pro"
    ): EmpathyAnalysis {
        try {
            val url = URL("${settings.empathyServiceUrl}/api/analyze")
            val connection = url.openConnection() as HttpURLConnection

            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("Authorization", "Bearer ${settings.apiKey}")
            connection.doOutput = true

            // Build JSON request
            val jsonRequest = """
                {
                    "code": ${escapeJson(code)},
                    "language": "$language",
                    "wizard": "$wizard",
                    "tier": "$tier"
                }
            """.trimIndent()

            // Send request
            connection.outputStream.use { it.write(jsonRequest.toByteArray()) }

            // Read response
            val responseCode = connection.responseCode
            if (responseCode == 200) {
                val response = connection.inputStream.bufferedReader().readText()
                return parseApiResponse(response)
            } else {
                throw Exception("API returned error code: $responseCode")
            }

        } catch (e: Exception) {
            System.err.println("Error calling Empathy API: ${e.message}")
            throw e
        }
    }

    /**
     * Check if API is reachable
     */
    fun testConnection(): Boolean {
        return try {
            val url = URL("${settings.empathyServiceUrl}/health")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.responseCode == 200
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Escape JSON string
     */
    private fun escapeJson(text: String): String {
        return "\"" + text
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t") + "\""
    }

    /**
     * Parse API response into EmpathyAnalysis
     */
    private fun parseApiResponse(response: String): EmpathyAnalysis {
        // TODO: Implement proper JSON parsing
        // For now, return a stub
        throw NotImplementedError("API response parsing not yet implemented")
    }
}
