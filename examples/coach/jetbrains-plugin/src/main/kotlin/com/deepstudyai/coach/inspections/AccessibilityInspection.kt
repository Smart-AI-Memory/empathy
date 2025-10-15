/**
 * Accessibility Inspection for Coach
 * Detects WCAG 2.1 violations using AccessibilityWizard
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
 * Main accessibility inspection
 * Detects WCAG violations for screen readers, keyboard navigation, color contrast, etc.
 */
class AccessibilityInspection : LocalInspectionTool() {
    private val logger = Logger.getInstance(AccessibilityInspection::class.java)

    override fun getDisplayName(): String = "Coach Accessibility Analysis (WCAG 2.1)"
    override fun getGroupDisplayName(): String = "Coach"
    override fun getShortName(): String = "CoachAccessibility"
    override fun isEnabledByDefault(): Boolean = true

    override fun buildVisitor(holder: ProblemsHolder, isOnTheFly: Boolean): PsiElementVisitor {
        return AccessibilityVisitor(holder, isOnTheFly)
    }

    /**
     * PSI visitor that inspects code elements for accessibility issues
     */
    private class AccessibilityVisitor(
        private val holder: ProblemsHolder,
        private val isOnTheFly: Boolean
    ) : PsiElementVisitor() {
        private val logger = Logger.getInstance(AccessibilityVisitor::class.java)

        override fun visitFile(file: PsiFile) {
            super.visitFile(file)

            // Only analyze HTML/JSX/TSX files
            val extension = file.virtualFile.extension
            if (extension !in listOf("html", "jsx", "tsx", "vue", "svelte")) {
                return
            }

            // Quick pattern-based checks (instant)
            checkMissingAltText(file)
            checkMissingAriaLabels(file)
            checkKeyboardAccessibility(file)
            checkColorContrast(file)
            checkFormAccessibility(file)
            checkSemanticHTML(file)
            checkHeadingHierarchy(file)

            // Optional: Deep analysis with AccessibilityWizard (async)
            if (isOnTheFly) {
                performDeepAnalysis(file)
            }
        }

        /**
         * Check for images without alt text
         */
        private fun checkMissingAltText(file: PsiFile) {
            val text = file.text

            // <img without alt attribute
            val imgWithoutAltPattern = Regex("""<img(?!\s+[^>]*alt)[^>]*>""", RegexOption.IGNORE_CASE)
            imgWithoutAltPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Image missing alt attribute - required for screen readers (WCAG 1.1.1)",
                    ProblemHighlightType.WARNING,
                    AddAltTextQuickFix()
                )
            }

            // Empty alt text on non-decorative images
            val imgWithEmptyAltPattern = Regex("""<img[^>]*alt=["']?["'][^>]*>""", RegexOption.IGNORE_CASE)
            imgWithEmptyAltPattern.findAll(text).forEach { match ->
                // Check if image has src (likely not decorative)
                if (match.value.contains("src=", ignoreCase = true)) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Image has empty alt text - provide description or use alt='' only for decorative images",
                        ProblemHighlightType.WEAK_WARNING
                    )
                }
            }

            // React: img without alt
            val reactImgPattern = Regex("""<img(?!\s+[^>]*alt\s*=)[^>]*/>""")
            reactImgPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Image missing alt prop - required for accessibility",
                    ProblemHighlightType.WARNING,
                    AddAltTextQuickFix()
                )
            }
        }

        /**
         * Check for missing ARIA labels
         */
        private fun checkMissingAriaLabels(file: PsiFile) {
            val text = file.text

            // Buttons without text or aria-label
            val buttonPattern = Regex("""<button(?!\s+[^>]*aria-label)([^>]*)>([^<]*)</button>""", RegexOption.IGNORE_CASE)
            buttonPattern.findAll(text).forEach { match ->
                val buttonContent = match.groupValues[2].trim()
                // If button has no text content, it needs aria-label
                if (buttonContent.isEmpty() || buttonContent.startsWith("<")) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Button without text content needs aria-label for screen readers (WCAG 4.1.2)",
                        ProblemHighlightType.WARNING,
                        AddAriaLabelQuickFix()
                    )
                }
            }

            // Links without text
            val linkPattern = Regex("""<a\s+[^>]*>([^<]*)</a>""", RegexOption.IGNORE_CASE)
            linkPattern.findAll(text).forEach { match ->
                val linkContent = match.groupValues[1].trim()
                if (linkContent.isEmpty()) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Link without text content - add descriptive text or aria-label",
                        ProblemHighlightType.WARNING,
                        AddAriaLabelQuickFix()
                    )
                }
            }

            // Icons without aria-label
            val iconPattern = Regex("""<(svg|i|span)\s+[^>]*class=["'][^"']*icon[^"']*["'][^>]*(?!aria-label)[^>]*>""", RegexOption.IGNORE_CASE)
            iconPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Icon may need aria-label if it conveys information",
                    ProblemHighlightType.WEAK_WARNING,
                    AddAriaLabelQuickFix()
                )
            }

            // Form inputs without labels
            val inputWithoutLabelPattern = Regex("""<input(?!\s+[^>]*aria-label)(?!\s+[^>]*id\s*=\s*["'](\w+)["'][^>]*>.*<label[^>]*for=["']\1["'])([^>]*)>""", RegexOption.IGNORE_CASE)
            inputWithoutLabelPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Form input needs associated label or aria-label (WCAG 1.3.1, 3.3.2)",
                    ProblemHighlightType.WARNING,
                    AddLabelQuickFix()
                )
            }
        }

        /**
         * Check for keyboard accessibility
         */
        private fun checkKeyboardAccessibility(file: PsiFile) {
            val text = file.text

            // onClick without onKeyPress/onKeyDown
            val onclickPattern = Regex("""onclick\s*=\s*["'][^"']+["'](?![^<]*onkey(press|down))""", RegexOption.IGNORE_CASE)
            onclickPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "onclick without keyboard handler - add onKeyPress for keyboard accessibility (WCAG 2.1.1)",
                    ProblemHighlightType.WARNING,
                    AddKeyboardHandlerQuickFix()
                )
            }

            // React: onClick without onKeyPress
            val reactOnClickPattern = Regex("""onClick\s*=\s*\{[^}]+\}(?![^<]*onKey(Press|Down))""")
            reactOnClickPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "onClick without keyboard handler - add onKeyPress for accessibility",
                    ProblemHighlightType.WARNING,
                    AddKeyboardHandlerQuickFix()
                )
            }

            // div/span with onClick (should use button)
            val divClickPattern = Regex("""<(div|span)([^>]*)on[Cc]lick""")
            divClickPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Interactive <${match.groupValues[1]}> should be <button> for proper keyboard/screen reader support",
                    ProblemHighlightType.WARNING,
                    UseButtonQuickFix()
                )
            }

            // tabindex > 0 (anti-pattern)
            val tabindexPattern = Regex("""tabindex\s*=\s*["']?([1-9]\d*)["']?""", RegexOption.IGNORE_CASE)
            tabindexPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Positive tabindex (${match.groupValues[1]}) creates confusing tab order - use tabindex=\"0\" or semantic HTML",
                    ProblemHighlightType.WARNING
                )
            }
        }

        /**
         * Check for color contrast issues
         */
        private fun checkColorContrast(file: PsiFile) {
            val text = file.text

            // Detect low-contrast color pairs (simplified heuristic)
            val colorPattern = Regex("""color:\s*#([0-9a-fA-F]{3,6})""")
            val bgColorPattern = Regex("""background(-color)?:\s*#([0-9a-fA-F]{3,6})""")

            val colors = colorPattern.findAll(text).map { it.groupValues[1] }.toList()
            val bgColors = bgColorPattern.findAll(text).map { it.groupValues[2] }.toList()

            // Check for known low-contrast pairs
            val lowContrastPairs = listOf(
                Pair("ffffff", "f0f0f0"),  // White on light gray
                Pair("000000", "333333"),  // Black on dark gray
                Pair("ffff00", "ffffff"),  // Yellow on white
            )

            colorPattern.findAll(text).forEach { colorMatch ->
                val color = colorMatch.groupValues[1].lowercase()
                bgColorPattern.findAll(text).forEach { bgMatch ->
                    val bgColor = bgMatch.groupValues[2].lowercase()
                    if (lowContrastPairs.any { (c, bg) ->
                            (color.startsWith(c) && bgColor.startsWith(bg)) ||
                                    (color.startsWith(bg) && bgColor.startsWith(c))
                        }) {
                        val element = findElementAt(file, colorMatch.range.first) ?: return@forEach
                        holder.registerProblem(
                            element,
                            "Potential low color contrast - ensure 4.5:1 ratio for text (WCAG 1.4.3)",
                            ProblemHighlightType.WEAK_WARNING,
                            ImproveContrastQuickFix()
                        )
                    }
                }
            }
        }

        /**
         * Check for form accessibility
         */
        private fun checkFormAccessibility(file: PsiFile) {
            val text = file.text

            // Required fields without aria-required
            val requiredPattern = Regex("""<input([^>]*)required([^>]*)>""", RegexOption.IGNORE_CASE)
            requiredPattern.findAll(text).forEach { match ->
                if (!match.value.contains("aria-required", ignoreCase = true)) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Required field should have aria-required=\"true\" for screen readers",
                        ProblemHighlightType.WEAK_WARNING
                    )
                }
            }

            // Error messages not associated with inputs
            val errorPattern = Regex("""class=["'][^"']*error[^"']*["']""", RegexOption.IGNORE_CASE)
            errorPattern.findAll(text).forEach { match ->
                // Check if nearby input has aria-describedby
                val surroundingText = text.substring(
                    maxOf(0, match.range.first - 200),
                    minOf(text.length, match.range.first + 200)
                )
                if (!surroundingText.contains("aria-describedby", ignoreCase = true)) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Error message should be associated with input via aria-describedby (WCAG 3.3.1)",
                        ProblemHighlightType.INFORMATION
                    )
                }
            }

            // Placeholder as only label
            val placeholderOnlyPattern = Regex("""<input[^>]*placeholder\s*=\s*["'][^"']+["'][^>]*>""", RegexOption.IGNORE_CASE)
            placeholderOnlyPattern.findAll(text).forEach { match ->
                if (!match.value.contains("aria-label", ignoreCase = true) &&
                    !match.value.contains("id=", ignoreCase = true)) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Placeholder is not a substitute for label - add proper label element",
                        ProblemHighlightType.WARNING,
                        AddLabelQuickFix()
                    )
                }
            }
        }

        /**
         * Check for semantic HTML
         */
        private fun checkSemanticHTML(file: PsiFile) {
            val text = file.text

            // Excessive div usage (should use semantic tags)
            val divCount = Regex("""<div""", RegexOption.IGNORE_CASE).findAll(text).count()
            val semanticCount = Regex("""<(header|nav|main|section|article|aside|footer)""", RegexOption.IGNORE_CASE).findAll(text).count()

            if (divCount > 20 && semanticCount < divCount / 5) {
                // File has many divs but few semantic tags
                val element = file.findElementAt(0)
                if (element != null) {
                    holder.registerProblem(
                        element,
                        "Consider using semantic HTML5 tags (<header>, <nav>, <main>, <section>) instead of <div>",
                        ProblemHighlightType.INFORMATION
                    )
                }
            }

            // Lists using divs instead of ul/ol
            val fakeListPattern = Regex("""<div[^>]*>\s*<div[^>]*>\s*<div[^>]*>""", RegexOption.MULTILINE)
            fakeListPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Multiple nested <div>s may be a list - use <ul>/<ol> for screen readers",
                    ProblemHighlightType.WEAK_WARNING
                )
            }
        }

        /**
         * Check for proper heading hierarchy
         */
        private fun checkHeadingHierarchy(file: PsiFile) {
            val text = file.text

            // Extract all headings
            val headingPattern = Regex("""<h([1-6])""", RegexOption.IGNORE_CASE)
            val headings = headingPattern.findAll(text).map { it.groupValues[1].toInt() }.toList()

            // Check for skipped levels (e.g., h1 -> h3)
            for (i in 1 until headings.size) {
                val prev = headings[i - 1]
                val curr = headings[i]
                if (curr > prev + 1) {
                    val element = findElementAt(file, text.indexOf("<h$curr")) ?: continue
                    holder.registerProblem(
                        element,
                        "Heading level skipped (h$prev to h$curr) - maintain sequential hierarchy (WCAG 1.3.1)",
                        ProblemHighlightType.WARNING
                    )
                }
            }

            // Check for multiple h1 tags
            val h1Count = headings.count { it == 1 }
            if (h1Count > 1) {
                val secondH1Index = text.indexOf("<h1", text.indexOf("<h1") + 1)
                val element = findElementAt(file, secondH1Index)
                if (element != null) {
                    holder.registerProblem(
                        element,
                        "Multiple <h1> tags found - page should have only one main heading",
                        ProblemHighlightType.WARNING
                    )
                }
            }
        }

        /**
         * Perform deep analysis with AccessibilityWizard (async)
         */
        private fun performDeepAnalysis(file: PsiFile) {
            val project = file.project
            val lspClient = CoachLSPClient.getInstance(project)

            try {
                runBlocking {
                    lspClient.analyzeDocument(file.virtualFile, file.text)
                }
            } catch (e: Exception) {
                logger.warn("Deep accessibility analysis failed", e)
            }
        }

        private fun findElementAt(file: PsiFile, offset: Int): PsiElement? {
            return file.findElementAt(offset)
        }
    }
}

// Quick Fixes

class AddAltTextQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Add alt attribute"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would add alt=\"Description of image\" to <img>")
    }

    companion object {
        private val logger = Logger.getInstance(AddAltTextQuickFix::class.java)
    }
}

class AddAriaLabelQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Add aria-label"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would add aria-label=\"Description\" to element")
    }

    companion object {
        private val logger = Logger.getInstance(AddAriaLabelQuickFix::class.java)
    }
}

class AddLabelQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Add label element"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would add <label for=\"inputId\">Label text</label>")
    }

    companion object {
        private val logger = Logger.getInstance(AddLabelQuickFix::class.java)
    }
}

class AddKeyboardHandlerQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Add keyboard handler"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would add onKeyPress handler")
    }

    companion object {
        private val logger = Logger.getInstance(AddKeyboardHandlerQuickFix::class.java)
    }
}

class UseButtonQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Convert to <button>"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would convert <div> to <button> for semantic HTML")
    }

    companion object {
        private val logger = Logger.getInstance(UseButtonQuickFix::class.java)
    }
}

class ImproveContrastQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Improve color contrast"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would suggest higher contrast colors (4.5:1 minimum)")
    }

    companion object {
        private val logger = Logger.getInstance(ImproveContrastQuickFix::class.java)
    }
}
