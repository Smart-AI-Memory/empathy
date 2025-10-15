package com.deepstudyai.coach.intentions

import com.intellij.codeInsight.intention.IntentionAction
import com.intellij.codeInsight.intention.PriorityAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Intention action to add alt text to images for accessibility.
 */
class AddAltTextIntention : IntentionAction, PriorityAction {

    override fun getText(): String = "Add alt text for accessibility"

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

        // Check for <img> tags without alt attribute
        return lineText.contains(Regex("<img[^>]*src")) && !lineText.contains(Regex("alt\\s*="))
    }

    override fun invoke(project: Project, editor: Editor?, file: PsiFile?) {
        if (editor == null || file == null) return

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Add alt attribute after src
        val fixedText = lineText.replace(
            Regex("(<img[^>]*src=\"[^\"]*\")"),
            "$1 alt=\"TODO: Add descriptive alt text\""
        )

        if (fixedText != lineText) {
            document.replaceString(lineStartOffset, lineEndOffset, fixedText)
        }
    }

    override fun startInWriteAction(): Boolean = true

    override fun getPriority(): PriorityAction.Priority = PriorityAction.Priority.HIGH
}
