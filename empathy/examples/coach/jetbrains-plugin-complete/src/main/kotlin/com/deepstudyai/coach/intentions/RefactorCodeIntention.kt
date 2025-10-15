package com.deepstudyai.coach.intentions

import com.intellij.codeInsight.intention.IntentionAction
import com.intellij.codeInsight.intention.PriorityAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Intention action to refactor code smells.
 */
class RefactorCodeIntention : IntentionAction, PriorityAction {

    override fun getText(): String = "Refactor code (reduce complexity)"

    override fun getFamilyName(): String = "Coach/Refactoring"

    override fun isAvailable(project: Project, editor: Editor?, file: PsiFile?): Boolean {
        if (editor == null || file == null) return false

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Look for code smells
        return lineText.contains(Regex("(if|else if|else).*\\{")) &&
                countBraces(getMethodBody(document, lineNumber)) > 3
    }

    private fun getMethodBody(document: com.intellij.openapi.editor.Document, startLine: Int): String {
        val startOffset = document.getLineStartOffset(startLine)
        val endOffset = minOf(startOffset + 1000, document.textLength)
        return document.getText(com.intellij.openapi.util.TextRange(startOffset, endOffset))
    }

    private fun countBraces(text: String): Int {
        return text.count { it == '{' }
    }

    override fun invoke(project: Project, editor: Editor?, file: PsiFile?) {
        if (editor == null || file == null) return

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)

        // Add refactoring suggestions
        val suggestion = when {
            file.name.endsWith(".java") || file.name.endsWith(".kt") -> {
                "    // TODO: Refactor complex conditional logic\n    // Consider:\n    // - Extract method\n    // - Use polymorphism\n    // - Apply strategy pattern\n"
            }
            file.name.endsWith(".py") -> {
                "    # TODO: Refactor complex conditional logic\n    # Consider:\n    # - Extract function\n    # - Use dictionary dispatch\n    # - Simplify with guard clauses\n"
            }
            file.name.endsWith(".js") || file.name.endsWith(".ts") -> {
                "    // TODO: Refactor complex conditional logic\n    // Consider:\n    // - Extract function\n    // - Use object literal dispatch\n    // - Early returns for guard clauses\n"
            }
            else -> "// TODO: Refactor complex logic\n"
        }

        document.insertString(lineStartOffset, suggestion)
    }

    override fun startInWriteAction(): Boolean = true

    override fun getPriority(): PriorityAction.Priority = PriorityAction.Priority.NORMAL
}
