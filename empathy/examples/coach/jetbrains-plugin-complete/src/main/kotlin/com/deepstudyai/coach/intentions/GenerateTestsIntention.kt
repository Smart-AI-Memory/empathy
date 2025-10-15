package com.deepstudyai.coach.intentions

import com.intellij.codeInsight.intention.IntentionAction
import com.intellij.codeInsight.intention.PriorityAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Intention action to generate tests for untested code.
 */
class GenerateTestsIntention : IntentionAction, PriorityAction {

    override fun getText(): String = "Generate unit tests"

    override fun getFamilyName(): String = "Coach/Testing"

    override fun isAvailable(project: Project, editor: Editor?, file: PsiFile?): Boolean {
        if (editor == null || file == null) return false

        // Don't show in test files
        if (file.name.contains("Test") || file.name.contains("Spec")) {
            return false
        }

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Check for function/method declarations
        return lineText.contains(Regex("(function|def|fun|public|private|protected)\\s+\\w+\\s*\\("))
    }

    override fun invoke(project: Project, editor: Editor?, file: PsiFile?) {
        if (editor == null || file == null) return

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)

        // Add a TODO comment suggesting test generation
        val suggestion = when {
            file.name.endsWith(".java") || file.name.endsWith(".kt") -> {
                "    // TODO: Add unit tests using JUnit/Mockito\n    // - Test happy path\n    // - Test edge cases\n    // - Test error handling\n"
            }
            file.name.endsWith(".py") -> {
                "    # TODO: Add unit tests using pytest\n    # - Test happy path\n    # - Test edge cases\n    # - Test error handling\n"
            }
            file.name.endsWith(".js") || file.name.endsWith(".ts") -> {
                "    // TODO: Add unit tests using Jest/Vitest\n    // - Test happy path\n    // - Test edge cases\n    // - Test error handling\n"
            }
            else -> "// TODO: Add unit tests\n"
        }

        document.insertString(lineStartOffset, suggestion)
    }

    override fun startInWriteAction(): Boolean = true

    override fun getPriority(): PriorityAction.Priority = PriorityAction.Priority.NORMAL
}
