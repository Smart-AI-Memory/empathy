package com.deepstudyai.coach.intentions

import com.intellij.codeInsight.intention.IntentionAction
import com.intellij.codeInsight.intention.PriorityAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Intention action to add ARIA labels for accessibility.
 */
class AddAriaLabelIntention : IntentionAction, PriorityAction {

    override fun getText(): String = "Add ARIA label for accessibility"

    override fun getFamilyName(): String = "Coach/Accessibility"

    override fun isAvailable(project: Project, editor: Editor?, file: PsiFile?): Boolean {
        if (editor == null || file == null) return false

        // Only applicable to HTML/JSX/TSX files
        if (!file.name.endsWith(".html") &&
            !file.name.endsWith(".jsx") &&
            !file.name.endsWith(".tsx")) {
            return false
        }

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Check for interactive elements without aria-label
        return (lineText.contains(Regex("<(button|input|select|textarea|a)")) &&
                !lineText.contains(Regex("aria-label")) &&
                !lineText.contains(Regex(">\\s*\\w+"))) // Has no text content
    }

    override fun invoke(project: Project, editor: Editor?, file: PsiFile?) {
        if (editor == null || file == null) return

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Add aria-label attribute
        val fixedText = lineText.replace(
            Regex("(<(button|input|select|textarea|a)[^>]*)>"),
            "$1 aria-label=\"TODO: Add descriptive label\">",
            RegexOption.IGNORE_CASE
        )

        if (fixedText != lineText) {
            document.replaceString(lineStartOffset, lineEndOffset, fixedText)
        }
    }

    override fun startInWriteAction(): Boolean = true

    override fun getPriority(): PriorityAction.Priority = PriorityAction.Priority.HIGH
}
