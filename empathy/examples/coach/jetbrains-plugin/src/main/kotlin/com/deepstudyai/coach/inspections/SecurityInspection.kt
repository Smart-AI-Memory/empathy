/**
 * Security Inspection for Coach
 * Detects security vulnerabilities using SecurityWizard
 *
 * Copyright 2025 Deep Study AI, LLC
 * Licensed under the Apache License, Version 2.0
 */

package com.deepstudyai.coach.inspections

import com.deepstudyai.coach.lsp.CoachLSPClient
import com.intellij.codeInspection.*
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiElementVisitor
import com.intellij.psi.PsiFile
import kotlinx.coroutines.runBlocking

/**
 * Main security inspection
 * Detects SQL injection, XSS, hardcoded secrets, and other security issues
 */
class SecurityInspection : LocalInspectionTool() {
    private val logger = Logger.getInstance(SecurityInspection::class.java)

    override fun getDisplayName(): String = "Coach Security Analysis"
    override fun getGroupDisplayName(): String = "Coach"
    override fun getShortName(): String = "CoachSecurity"
    override fun isEnabledByDefault(): Boolean = true

    override fun buildVisitor(holder: ProblemsHolder, isOnTheFly: Boolean): PsiElementVisitor {
        return SecurityVisitor(holder, isOnTheFly)
    }

    /**
     * PSI visitor that inspects code elements for security issues
     */
    private class SecurityVisitor(
        private val holder: ProblemsHolder,
        private val isOnTheFly: Boolean
    ) : PsiElementVisitor() {
        private val logger = Logger.getInstance(SecurityVisitor::class.java)

        override fun visitFile(file: PsiFile) {
            super.visitFile(file)

            // Quick pattern-based checks (instant)
            checkSQLInjection(file)
            checkXSS(file)
            checkHardcodedSecrets(file)
            checkWeakCrypto(file)
            checkInsecureDeserialization(file)

            // Optional: Deep analysis with SecurityWizard (async)
            if (isOnTheFly) {
                performDeepAnalysis(file)
            }
        }

        /**
         * Check for SQL injection vulnerabilities
         */
        private fun checkSQLInjection(file: PsiFile) {
            val text = file.text

            // Python f-string SQL
            val pythonSQLPattern = Regex("""f["'].*?SELECT.*?\{.*?\}.*?["']""", RegexOption.IGNORE_CASE)
            pythonSQLPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Potential SQL injection vulnerability - use parameterized queries",
                    ProblemHighlightType.ERROR,
                    SQLInjectionQuickFix()
                )
            }

            // JavaScript/TypeScript template literals
            val jsSQLPattern = Regex("""`.*?SELECT.*?\$\{.*?\}.*?`""", RegexOption.IGNORE_CASE)
            jsSQLPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Potential SQL injection vulnerability - use parameterized queries",
                    ProblemHighlightType.ERROR,
                    SQLInjectionQuickFix()
                )
            }

            // String concatenation with SQL keywords
            val concatSQLPattern = Regex("""["']SELECT.*?["']\s*\+""", RegexOption.IGNORE_CASE)
            concatSQLPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "SQL query concatenation detected - use parameterized queries",
                    ProblemHighlightType.WARNING,
                    SQLInjectionQuickFix()
                )
            }
        }

        /**
         * Check for XSS vulnerabilities
         */
        private fun checkXSS(file: PsiFile) {
            val text = file.text

            // innerHTML usage
            val innerHTMLPattern = Regex("""innerHTML\s*=\s*[^;]+""")
            innerHTMLPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Potential XSS vulnerability - sanitize HTML or use textContent",
                    ProblemHighlightType.WARNING,
                    XSSQuickFix()
                )
            }

            // dangerouslySetInnerHTML
            val dangerousHTMLPattern = Regex("""dangerouslySetInnerHTML\s*=\s*\{\{""")
            dangerousHTMLPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Potential XSS vulnerability - sanitize HTML with DOMPurify",
                    ProblemHighlightType.WARNING,
                    XSSQuickFix()
                )
            }

            // document.write with variables
            val documentWritePattern = Regex("""document\.write\([^)]*\$\{[^}]+\}[^)]*\)""")
            documentWritePattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Potential XSS vulnerability - avoid document.write with user input",
                    ProblemHighlightType.WARNING,
                    XSSQuickFix()
                )
            }
        }

        /**
         * Check for hardcoded secrets
         */
        private fun checkHardcodedSecrets(file: PsiFile) {
            val text = file.text

            // Hardcoded passwords, API keys, tokens
            val secretPattern = Regex(
                """(password|secret|api_key|apikey|token|access_key)\s*[=:]\s*["'][^"']{8,}["']""",
                RegexOption.IGNORE_CASE
            )
            secretPattern.findAll(text).forEach { match ->
                // Skip if it's a placeholder or example
                val value = match.value.lowercase()
                if (value.contains("example") ||
                    value.contains("placeholder") ||
                    value.contains("your_") ||
                    value.contains("xxx")) {
                    return@forEach
                }

                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Hardcoded secret detected - use environment variables or secrets manager",
                    ProblemHighlightType.WARNING,
                    HardcodedSecretQuickFix()
                )
            }

            // AWS keys pattern
            val awsKeyPattern = Regex("""AKIA[0-9A-Z]{16}""")
            awsKeyPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "AWS access key detected - never commit credentials to version control",
                    ProblemHighlightType.ERROR
                )
            }
        }

        /**
         * Check for weak cryptography
         */
        private fun checkWeakCrypto(file: PsiFile) {
            val text = file.text

            // MD5/SHA1 usage
            val weakHashPattern = Regex("""(md5|sha1)\(""", RegexOption.IGNORE_CASE)
            weakHashPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Weak cryptographic hash - use SHA-256 or better",
                    ProblemHighlightType.WARNING,
                    WeakCryptoQuickFix()
                )
            }

            // DES encryption
            val desPattern = Regex("""DES\(""", RegexOption.IGNORE_CASE)
            desPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "DES encryption is obsolete - use AES-256",
                    ProblemHighlightType.ERROR,
                    WeakCryptoQuickFix()
                )
            }
        }

        /**
         * Check for insecure deserialization
         */
        private fun checkInsecureDeserialization(file: PsiFile) {
            val text = file.text

            // Python pickle
            val picklePattern = Regex("""pickle\.loads?\(""")
            picklePattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Insecure deserialization - validate and sanitize input before unpickling",
                    ProblemHighlightType.WARNING
                )
            }

            // JavaScript eval
            val evalPattern = Regex("""eval\(""")
            evalPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "eval() is dangerous - use JSON.parse() or safer alternatives",
                    ProblemHighlightType.ERROR
                )
            }
        }

        /**
         * Perform deep analysis with SecurityWizard (async)
         */
        private fun performDeepAnalysis(file: PsiFile) {
            val project = file.project
            val lspClient = CoachLSPClient.getInstance(project)

            try {
                runBlocking {
                    lspClient.analyzeDocument(file.virtualFile, file.text)
                }
            } catch (e: Exception) {
                logger.warn("Deep security analysis failed", e)
            }
        }

        private fun findElementAt(file: PsiFile, offset: Int): PsiElement? {
            return file.findElementAt(offset)
        }
    }
}

/**
 * Quick fix for SQL injection
 */
class SQLInjectionQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Convert to parameterized query"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        val element = descriptor.psiElement
        val text = element.text

        // Convert Python f-string to parameterized query
        if (text.contains("f\"") || text.contains("f'")) {
            val converted = convertPythonFString(text)
            // Apply fix (simplified - production would use PSI manipulation)
            logger.info("Would convert to: $converted")
        }

        // Convert JavaScript template literal
        if (text.contains("`")) {
            val converted = convertJSTemplateLiteral(text)
            logger.info("Would convert to: $converted")
        }
    }

    private fun convertPythonFString(text: String): String {
        // Extract variables from f-string
        val vars = Regex("""\{(\w+)\}""").findAll(text).map { it.groupValues[1] }.toList()
        val paramQuery = text.replace(Regex("""\{(\w+)\}"""), "?")
        return "$paramQuery, (${vars.joinToString(", ")})"
    }

    private fun convertJSTemplateLiteral(text: String): String {
        val vars = Regex("""\$\{(\w+)\}""").findAll(text).map { it.groupValues[1] }.toList()
        val paramQuery = text.replace(Regex("""\$\{(\w+)\}"""), "?")
        return "$paramQuery, [${vars.joinToString(", ")}]"
    }

    companion object {
        private val logger = Logger.getInstance(SQLInjectionQuickFix::class.java)
    }
}

/**
 * Quick fix for XSS
 */
class XSSQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Sanitize HTML output"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        val element = descriptor.psiElement
        val text = element.text

        if (text.contains("innerHTML")) {
            logger.info("Would replace innerHTML with textContent or DOMPurify.sanitize()")
        } else if (text.contains("dangerouslySetInnerHTML")) {
            logger.info("Would wrap with DOMPurify.sanitize()")
        }
    }

    companion object {
        private val logger = Logger.getInstance(XSSQuickFix::class.java)
    }
}

/**
 * Quick fix for hardcoded secrets
 */
class HardcodedSecretQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Use environment variable"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        val element = descriptor.psiElement
        logger.info("Would replace hardcoded secret with process.env.SECRET_NAME or os.getenv('SECRET_NAME')")
    }

    companion object {
        private val logger = Logger.getInstance(HardcodedSecretQuickFix::class.java)
    }
}

/**
 * Quick fix for weak cryptography
 */
class WeakCryptoQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Use strong cryptography"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        val element = descriptor.psiElement
        val text = element.text

        if (text.contains("md5", ignoreCase = true) || text.contains("sha1", ignoreCase = true)) {
            logger.info("Would replace with SHA-256 or better")
        } else if (text.contains("DES", ignoreCase = true)) {
            logger.info("Would replace with AES-256")
        }
    }

    companion object {
        private val logger = Logger.getInstance(WeakCryptoQuickFix::class.java)
    }
}
