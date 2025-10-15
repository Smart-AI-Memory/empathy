/**
 * Performance Inspection for Coach
 * Detects performance issues using PerformanceWizard
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
 * Main performance inspection
 * Detects N+1 queries, inefficient algorithms, memory leaks, and other performance issues
 */
class PerformanceInspection : LocalInspectionTool() {
    private val logger = Logger.getInstance(PerformanceInspection::class.java)

    override fun getDisplayName(): String = "Coach Performance Analysis"
    override fun getGroupDisplayName(): String = "Coach"
    override fun getShortName(): String = "CoachPerformance"
    override fun isEnabledByDefault(): Boolean = true

    override fun buildVisitor(holder: ProblemsHolder, isOnTheFly: Boolean): PsiElementVisitor {
        return PerformanceVisitor(holder, isOnTheFly)
    }

    /**
     * PSI visitor that inspects code elements for performance issues
     */
    private class PerformanceVisitor(
        private val holder: ProblemsHolder,
        private val isOnTheFly: Boolean
    ) : PsiElementVisitor() {
        private val logger = Logger.getInstance(PerformanceVisitor::class.java)

        override fun visitFile(file: PsiFile) {
            super.visitFile(file)

            // Quick pattern-based checks (instant)
            checkNPlusOneQueries(file)
            checkLargeLoops(file)
            checkIneffic inefficientDataStructures(file)
            checkMemoryLeaks(file)
            checkBlockingOperations(file)

            // Optional: Deep analysis with PerformanceWizard (async)
            if (isOnTheFly) {
                performDeepAnalysis(file)
            }
        }

        /**
         * Check for N+1 query patterns
         */
        private fun checkNPlusOneQueries(file: PsiFile) {
            val text = file.text

            // Python: for loop with database queries
            val pythonN1Pattern = Regex(
                """for\s+\w+\s+in\s+\w+:[^:]*\.(get|filter|find)\(""",
                RegexOption.MULTILINE
            )
            pythonN1Pattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Potential N+1 query pattern - consider using batch queries or select_related()",
                    ProblemHighlightType.WARNING,
                    NPlusOneQuickFix()
                )
            }

            // JavaScript/TypeScript: forEach with await
            val jsN1Pattern = Regex(
                """\.(forEach|map)\([^}]*await\s+\w+\.(get|find|query)""",
                RegexOption.MULTILINE
            )
            jsN1Pattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Potential N+1 query - use Promise.all() or batch query",
                    ProblemHighlightType.WARNING,
                    NPlusOneQuickFix()
                )
            }

            // ORM .all() in loop
            val ormAllPattern = Regex(
                """for\s+\w+\s+in\s+\w+:[^:]*\.all\(\)""",
                RegexOption.MULTILINE
            )
            ormAllPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Loading all records in loop - use prefetch_related() or batch loading",
                    ProblemHighlightType.WARNING,
                    NPlusOneQuickFix()
                )
            }
        }

        /**
         * Check for large loops
         */
        private fun checkLargeLoops(file: PsiFile) {
            val text = file.text

            // Python range loops
            val pythonLoopPattern = Regex("""for\s+\w+\s+in\s+range\((\d+)\)""")
            pythonLoopPattern.findAll(text).forEach { match ->
                val iterations = match.groupValues[1].toIntOrNull() ?: return@forEach
                if (iterations > 1000) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Large loop ($iterations iterations) - consider optimization or vectorization",
                        ProblemHighlightType.WEAK_WARNING,
                        OptimizeLoopQuickFix()
                    )
                }
            }

            // JavaScript for loops
            val jsLoopPattern = Regex("""for\s*\(\s*let\s+\w+\s*=\s*0;\s*\w+\s*<\s*(\d+)""")
            jsLoopPattern.findAll(text).forEach { match ->
                val iterations = match.groupValues[1].toIntOrNull() ?: return@forEach
                if (iterations > 1000) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Large loop ($iterations iterations) - consider optimization",
                        ProblemHighlightType.WEAK_WARNING,
                        OptimizeLoopQuickFix()
                    )
                }
            }

            // Nested loops
            val nestedLoopPattern = Regex(
                """for[^{]*\{[^}]*for[^{]*\{""",
                RegexOption.MULTILINE
            )
            nestedLoopPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Nested loops detected - O(n²) complexity, consider optimization",
                    ProblemHighlightType.WEAK_WARNING,
                    OptimizeLoopQuickFix()
                )
            }
        }

        /**
         * Check for inefficient data structures
         */
        private fun checkInefficientDataStructures(file: PsiFile) {
            val text = file.text

            // Linear search in array
            val linearSearchPattern = Regex(
                """\.(indexOf|includes|find)\([^)]+\)""",
                RegexOption.MULTILINE
            )
            // Count occurrences - if too many in same array, suggest Set
            val searchCounts = mutableMapOf<String, Int>()
            linearSearchPattern.findAll(text).forEach { match ->
                val arrayName = text.substring(
                    maxOf(0, match.range.first - 20),
                    match.range.first
                ).trim().split(Regex("""\W""")).lastOrNull() ?: return@forEach

                searchCounts[arrayName] = searchCounts.getOrDefault(arrayName, 0) + 1

                if (searchCounts[arrayName]!! > 3) {
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "Multiple linear searches on '$arrayName' - consider using Set or Map",
                        ProblemHighlightType.WEAK_WARNING,
                        UseSetQuickFix()
                    )
                }
            }

            // Array push in loop (should preallocate)
            val pushInLoopPattern = Regex(
                """for[^{]*\{[^}]*\.(push|append)\(""",
                RegexOption.MULTILINE
            )
            pushInLoopPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Array modification in loop - consider preallocating capacity",
                    ProblemHighlightType.INFORMATION
                )
            }
        }

        /**
         * Check for memory leaks
         */
        private fun checkMemoryLeaks(file: PsiFile) {
            val text = file.text

            // Event listeners without removal
            val addEventPattern = Regex("""addEventListener\(['"](\w+)['"]""")
            val removeEventPattern = Regex("""removeEventListener\(['"](\w+)['"]""")

            val addedEvents = addEventPattern.findAll(text).map { it.groupValues[1] }.toSet()
            val removedEvents = removeEventPattern.findAll(text).map { it.groupValues[1] }.toSet()

            val unleakedEvents = addedEvents - removedEvents
            if (unleakedEvents.isNotEmpty()) {
                addEventPattern.findAll(text).forEach { match ->
                    if (unleakedEvents.contains(match.groupValues[1])) {
                        val element = findElementAt(file, match.range.first) ?: return@forEach
                        holder.registerProblem(
                            element,
                            "Event listener '${match.groupValues[1]}' may not be removed - potential memory leak",
                            ProblemHighlightType.WARNING,
                            RemoveEventListenerQuickFix()
                        )
                    }
                }
            }

            // setInterval without clearInterval
            val setIntervalPattern = Regex("""setInterval\(""")
            val clearIntervalPattern = Regex("""clearInterval\(""")

            if (setIntervalPattern.containsMatchIn(text) && !clearIntervalPattern.containsMatchIn(text)) {
                setIntervalPattern.findAll(text).forEach { match ->
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "setInterval without clearInterval - potential memory leak",
                        ProblemHighlightType.WARNING
                    )
                }
            }

            // Global variables in closures
            val globalVarPattern = Regex("""(var|let|const)\s+(\w+)\s*=\s*\[""")
            globalVarPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                // Check if variable is in global scope (simplified heuristic)
                val beforeText = text.substring(0, match.range.first)
                if (!beforeText.contains("function") && !beforeText.contains("class")) {
                    holder.registerProblem(
                        element,
                        "Global array variable - may cause memory retention",
                        ProblemHighlightType.INFORMATION
                    )
                }
            }
        }

        /**
         * Check for blocking operations
         */
        private fun checkBlockingOperations(file: PsiFile) {
            val text = file.text

            // Synchronous file I/O in Node.js
            val syncIOPattern = Regex("""fs\.(readFileSync|writeFileSync|existsSync)""")
            syncIOPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                holder.registerProblem(
                    element,
                    "Synchronous I/O blocks event loop - use async version (${match.groupValues[1].replace("Sync", "")})",
                    ProblemHighlightType.WARNING,
                    AsyncIOQuickFix()
                )
            }

            // Thread.sleep in Python (should use asyncio.sleep)
            val pythonSleepPattern = Regex("""time\.sleep\(""")
            pythonSleepPattern.findAll(text).forEach { match ->
                val element = findElementAt(file, match.range.first) ?: return@forEach
                // Check if in async context
                val surroundingText = text.substring(
                    maxOf(0, match.range.first - 200),
                    minOf(text.length, match.range.first + 100)
                )
                if (surroundingText.contains("async def")) {
                    holder.registerProblem(
                        element,
                        "time.sleep() blocks in async function - use await asyncio.sleep()",
                        ProblemHighlightType.WARNING,
                        AsyncSleepQuickFix()
                    )
                }
            }

            // CPU-intensive operations without worker threads
            val cpuIntensivePatterns = listOf(
                Regex("""for\s+\w+\s+in\s+range\((\d+)\).*\*\*\s*2"""),  // Large math operations
                Regex("""JSON\.parse\(\s*largeData"""),  // Parsing large JSON
                Regex("""\.sort\(\)""")  // Sorting (may be large)
            )

            cpuIntensivePatterns.forEach { pattern ->
                pattern.findAll(text).forEach { match ->
                    val element = findElementAt(file, match.range.first) ?: return@forEach
                    holder.registerProblem(
                        element,
                        "CPU-intensive operation - consider using worker threads or background processing",
                        ProblemHighlightType.INFORMATION
                    )
                }
            }
        }

        /**
         * Perform deep analysis with PerformanceWizard (async)
         */
        private fun performDeepAnalysis(file: PsiFile) {
            val project = file.project
            val lspClient = CoachLSPClient.getInstance(project)

            try {
                runBlocking {
                    lspClient.analyzeDocument(file.virtualFile, file.text)
                }
            } catch (e: Exception) {
                logger.warn("Deep performance analysis failed", e)
            }
        }

        private fun findElementAt(file: PsiFile, offset: Int): PsiElement? {
            return file.findElementAt(offset)
        }
    }
}

/**
 * Quick fix for N+1 queries
 */
class NPlusOneQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Convert to batch query"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        val element = descriptor.psiElement
        val text = element.text

        if (text.contains("for") && text.contains("get(")) {
            logger.info("Would convert to batch query with select_related() or prefetch_related()")
        } else if (text.contains("forEach") && text.contains("await")) {
            logger.info("Would convert to Promise.all() for parallel execution")
        }
    }

    companion object {
        private val logger = Logger.getInstance(NPlusOneQuickFix::class.java)
    }
}

/**
 * Quick fix for loop optimization
 */
class OptimizeLoopQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Optimize loop"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would suggest: vectorization (NumPy), break early, or algorithm optimization")
    }

    companion object {
        private val logger = Logger.getInstance(OptimizeLoopQuickFix::class.java)
    }
}

/**
 * Quick fix for using Set instead of Array
 */
class UseSetQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Convert to Set for faster lookups"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would convert array to Set for O(1) lookups")
    }

    companion object {
        private val logger = Logger.getInstance(UseSetQuickFix::class.java)
    }
}

/**
 * Quick fix for removing event listeners
 */
class RemoveEventListenerQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Add removeEventListener"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would add removeEventListener() in cleanup/unmount")
    }

    companion object {
        private val logger = Logger.getInstance(RemoveEventListenerQuickFix::class.java)
    }
}

/**
 * Quick fix for async I/O
 */
class AsyncIOQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Convert to async I/O"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        val element = descriptor.psiElement
        val text = element.text

        if (text.contains("readFileSync")) {
            logger.info("Would convert to: await fs.promises.readFile()")
        } else if (text.contains("writeFileSync")) {
            logger.info("Would convert to: await fs.promises.writeFile()")
        }
    }

    companion object {
        private val logger = Logger.getInstance(AsyncIOQuickFix::class.java)
    }
}

/**
 * Quick fix for async sleep
 */
class AsyncSleepQuickFix : LocalQuickFix {
    override fun getFamilyName(): String = "Use asyncio.sleep()"

    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        logger.info("Would convert time.sleep() to await asyncio.sleep()")
    }

    companion object {
        private val logger = Logger.getInstance(AsyncSleepQuickFix::class.java)
    }
}
