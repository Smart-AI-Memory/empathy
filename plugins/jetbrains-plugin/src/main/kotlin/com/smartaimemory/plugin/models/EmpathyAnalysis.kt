package com.smartaimemory.plugin.models

/**
 * Represents a complete Empathy Framework analysis result
 */
data class EmpathyAnalysis(
    val filePath: String,
    val language: String,
    val issues: List<Issue>,
    val predictions: List<Prediction>,
    val symbols: List<CodeSymbol>,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * Represents a code issue found during analysis
 * (Layer 1: Rules, Layer 2: Patterns, Layer 3: Expert Analysis)
 */
data class Issue(
    val severity: String,        // "critical", "high", "medium", "low", "info"
    val category: String,         // "security", "performance", "quality", "style"
    val description: String,      // Human-readable description
    val lineNumber: Int,          // Line number where issue occurs
    val layer: Int = 1,           // Empathy layer (1-3)
    val suggestedFix: SuggestedFix? = null
)

/**
 * Represents a suggested fix for an issue
 */
data class SuggestedFix(
    val startOffset: Int,
    val endOffset: Int,
    val replacement: String,
    val description: String
)

/**
 * Represents a Level 4 Anticipatory prediction
 */
data class Prediction(
    val confidence: Int,          // 0-100
    val timeline: String,         // "1 week", "2 weeks", "1 month"
    val prediction: String,       // What will happen
    val impact: String,           // Impact description
    val affectedLines: List<Int>? = null,
    val recommendation: String? = null
)

/**
 * Represents a code symbol (function, class, method, etc.)
 */
data class CodeSymbol(
    val name: String,
    val type: String,             // "function", "class", "method", "variable"
    val lineNumber: Int,
    val filePath: String,
    val signature: String? = null,
    val visibility: String? = null // "public", "private", "protected"
)
