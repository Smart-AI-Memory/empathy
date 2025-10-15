package com.deepstudyai.coach.services

import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.project.Project

/**
 * Registry of all Coach wizards.
 *
 * Maintains metadata about the 16 built-in wizards and supports
 * registration of custom wizards.
 */
@Service(Service.Level.PROJECT)
class WizardRegistry(private val project: Project) {

    private val wizards = mutableMapOf<String, WizardMetadata>()

    companion object {
        fun getInstance(project: Project): WizardRegistry = project.service()
    }

    init {
        // Register the 16 built-in wizards
        registerBuiltInWizards()
    }

    private fun registerBuiltInWizards() {
        register(WizardMetadata(
            id = "SecurityWizard",
            name = "Security Wizard",
            description = "Detects security vulnerabilities including SQL injection, XSS, hardcoded secrets, and CSRF",
            category = WizardCategory.SECURITY,
            applicableLanguages = listOf("Java", "Python", "JavaScript", "TypeScript", "Kotlin", "Go", "Ruby", "PHP", "C#"),
            icon = "security.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "PerformanceWizard",
            name = "Performance Wizard",
            description = "Identifies performance issues like N+1 queries, memory leaks, and inefficient algorithms",
            category = WizardCategory.PERFORMANCE,
            applicableLanguages = listOf("Java", "Python", "JavaScript", "TypeScript", "Kotlin", "Go", "C++", "C#"),
            icon = "performance.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "AccessibilityWizard",
            name = "Accessibility Wizard",
            description = "Ensures WCAG 2.1 AA compliance, detects missing alt text, keyboard accessibility issues",
            category = WizardCategory.ACCESSIBILITY,
            applicableLanguages = listOf("HTML", "JavaScript", "TypeScript", "JSX", "TSX", "Vue", "React"),
            icon = "accessibility.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "DebuggingWizard",
            name = "Debugging Wizard",
            description = "Helps debug complex issues by analyzing stack traces, logs, and runtime behavior",
            category = WizardCategory.DEBUGGING,
            applicableLanguages = listOf("*"), // All languages
            icon = "debugging.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "TestingWizard",
            name = "Testing Wizard",
            description = "Suggests tests, identifies untested code paths, recommends test strategies",
            category = WizardCategory.TESTING,
            applicableLanguages = listOf("Java", "Python", "JavaScript", "TypeScript", "Kotlin", "Go", "Ruby", "C#"),
            icon = "testing.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "RefactoringWizard",
            name = "Refactoring Wizard",
            description = "Identifies code smells, suggests refactoring opportunities, improves maintainability",
            category = WizardCategory.REFACTORING,
            applicableLanguages = listOf("*"),
            icon = "refactoring.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "DatabaseWizard",
            name = "Database Wizard",
            description = "Optimizes queries, suggests indexes, detects schema issues",
            category = WizardCategory.DATABASE,
            applicableLanguages = listOf("SQL", "Java", "Python", "JavaScript", "TypeScript", "Kotlin", "C#"),
            icon = "database.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "APIWizard",
            name = "API Wizard",
            description = "Reviews API design, suggests REST/GraphQL best practices, validates OpenAPI specs",
            category = WizardCategory.API,
            applicableLanguages = listOf("Java", "Python", "JavaScript", "TypeScript", "Kotlin", "Go", "C#"),
            icon = "api.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "ScalingWizard",
            name = "Scaling Wizard",
            description = "Predicts scaling bottlenecks, suggests architecture improvements for high load",
            category = WizardCategory.SCALING,
            applicableLanguages = listOf("*"),
            icon = "scaling.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "ObservabilityWizard",
            name = "Observability Wizard",
            description = "Recommends logging, metrics, tracing strategies for production debugging",
            category = WizardCategory.OBSERVABILITY,
            applicableLanguages = listOf("*"),
            icon = "observability.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "CICDWizard",
            name = "CI/CD Wizard",
            description = "Optimizes pipelines, suggests deployment strategies, reviews Docker/K8s configs",
            category = WizardCategory.CICD,
            applicableLanguages = listOf("YAML", "Dockerfile", "Jenkinsfile", "Bash", "Shell"),
            icon = "cicd.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "DocumentationWizard",
            name = "Documentation Wizard",
            description = "Identifies missing docs, suggests improvements, generates API documentation",
            category = WizardCategory.DOCUMENTATION,
            applicableLanguages = listOf("*"),
            icon = "documentation.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "ComplianceWizard",
            name = "Compliance Wizard",
            description = "Checks GDPR, HIPAA, PCI-DSS compliance, identifies data privacy issues",
            category = WizardCategory.COMPLIANCE,
            applicableLanguages = listOf("*"),
            icon = "compliance.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "MigrationWizard",
            name = "Migration Wizard",
            description = "Assists with framework upgrades, language migrations, dependency updates",
            category = WizardCategory.MIGRATION,
            applicableLanguages = listOf("*"),
            icon = "migration.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "MonitoringWizard",
            name = "Monitoring Wizard",
            description = "Reviews alerting strategies, suggests SLOs/SLIs, identifies monitoring gaps",
            category = WizardCategory.MONITORING,
            applicableLanguages = listOf("*"),
            icon = "monitoring.svg",
            defaultEnabled = true
        ))

        register(WizardMetadata(
            id = "LocalizationWizard",
            name = "Localization Wizard",
            description = "Detects hardcoded strings, suggests i18n strategies, validates translations",
            category = WizardCategory.LOCALIZATION,
            applicableLanguages = listOf("Java", "Python", "JavaScript", "TypeScript", "Kotlin", "Swift", "Go"),
            icon = "localization.svg",
            defaultEnabled = true
        ))
    }

    /**
     * Registers a wizard in the registry.
     */
    fun register(metadata: WizardMetadata) {
        wizards[metadata.id] = metadata
    }

    /**
     * Unregisters a wizard from the registry.
     */
    fun unregister(wizardId: String) {
        wizards.remove(wizardId)
    }

    /**
     * Gets metadata for a specific wizard.
     */
    fun getWizard(wizardId: String): WizardMetadata? {
        return wizards[wizardId]
    }

    /**
     * Gets all registered wizards.
     */
    fun getAllWizards(): List<WizardMetadata> {
        return wizards.values.toList()
    }

    /**
     * Gets wizards applicable to a specific language.
     */
    fun getWizardsForLanguage(language: String): List<WizardMetadata> {
        return wizards.values.filter { wizard ->
            wizard.applicableLanguages.contains("*") ||
            wizard.applicableLanguages.any { it.equals(language, ignoreCase = true) }
        }
    }

    /**
     * Gets wizards in a specific category.
     */
    fun getWizardsByCategory(category: WizardCategory): List<WizardMetadata> {
        return wizards.values.filter { it.category == category }
    }

    /**
     * Gets all enabled wizards.
     */
    fun getEnabledWizards(): List<WizardMetadata> {
        return wizards.values.filter { it.defaultEnabled }
    }

    /**
     * Checks if a wizard is registered.
     */
    fun isRegistered(wizardId: String): Boolean {
        return wizards.containsKey(wizardId)
    }

    /**
     * Gets the total count of registered wizards.
     */
    fun getWizardCount(): Int {
        return wizards.size
    }

    /**
     * Gets wizard IDs that support multi-wizard collaboration for a given scenario.
     */
    fun getCollaborationWizards(scenario: String): List<String> {
        return when (scenario.lowercase()) {
            "payment" -> listOf("SecurityWizard", "ComplianceWizard", "PerformanceWizard")
            "authentication" -> listOf("SecurityWizard", "AccessibilityWizard", "TestingWizard")
            "api" -> listOf("APIWizard", "SecurityWizard", "DocumentationWizard", "PerformanceWizard")
            "database" -> listOf("DatabaseWizard", "PerformanceWizard", "SecurityWizard")
            "frontend" -> listOf("AccessibilityWizard", "PerformanceWizard", "LocalizationWizard")
            "deployment" -> listOf("CICDWizard", "MonitoringWizard", "ObservabilityWizard")
            "scaling" -> listOf("ScalingWizard", "PerformanceWizard", "DatabaseWizard", "MonitoringWizard")
            "migration" -> listOf("MigrationWizard", "TestingWizard", "DocumentationWizard")
            else -> emptyList()
        }
    }
}

/**
 * Metadata about a Coach wizard.
 */
data class WizardMetadata(
    val id: String,
    val name: String,
    val description: String,
    val category: WizardCategory,
    val applicableLanguages: List<String>,
    val icon: String,
    val defaultEnabled: Boolean,
    val customWizard: Boolean = false,
    val wizardPath: String? = null // For custom wizards
)

/**
 * Categories of Coach wizards.
 */
enum class WizardCategory(val displayName: String) {
    SECURITY("Security"),
    PERFORMANCE("Performance"),
    ACCESSIBILITY("Accessibility"),
    DEBUGGING("Debugging"),
    TESTING("Testing"),
    REFACTORING("Refactoring"),
    DATABASE("Database"),
    API("API"),
    SCALING("Scaling"),
    OBSERVABILITY("Observability"),
    CICD("CI/CD"),
    DOCUMENTATION("Documentation"),
    COMPLIANCE("Compliance"),
    MIGRATION("Migration"),
    MONITORING("Monitoring"),
    LOCALIZATION("Localization"),
    CUSTOM("Custom")
}
