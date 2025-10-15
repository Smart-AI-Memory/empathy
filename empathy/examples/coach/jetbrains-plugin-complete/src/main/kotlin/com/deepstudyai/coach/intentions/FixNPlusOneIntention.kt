package com.deepstudyai.coach.intentions

import com.intellij.codeInsight.intention.IntentionAction
import com.intellij.codeInsight.intention.PriorityAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Intention action to fix N+1 query problems.
 *
 * Suggests using eager loading or batch fetching.
 */
class FixNPlusOneIntention : IntentionAction, PriorityAction {

    override fun getText(): String = "Fix N+1 query problem (use eager loading)"

    override fun getFamilyName(): String = "Coach/Performance"

    override fun isAvailable(project: Project, editor: Editor?, file: PsiFile?): Boolean {
        if (editor == null || file == null) return false

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Look for patterns that suggest N+1 queries
        return lineText.contains(Regex("for.*in|forEach|map")) &&
                (lineText.contains(Regex("get|find|fetch", RegexOption.IGNORE_CASE)) ||
                 file.text.contains(Regex("@OneToMany|@ManyToOne|relationship")))
    }

    override fun invoke(project: Project, editor: Editor?, file: PsiFile?) {
        if (editor == null || file == null) return

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)

        // Add a comment suggesting eager loading
        val suggestion = when {
            file.name.endsWith(".java") || file.name.endsWith(".kt") -> {
                "// TODO: Use @EntityGraph or JOIN FETCH to avoid N+1 queries\n"
            }
            file.name.endsWith(".py") -> {
                "# TODO: Use select_related() or prefetch_related() to avoid N+1 queries\n"
            }
            file.name.endsWith(".js") || file.name.endsWith(".ts") -> {
                "// TODO: Use include/populate to eager load relationships\n"
            }
            else -> "// TODO: Use eager loading to avoid N+1 queries\n"
        }

        document.insertString(lineStartOffset, suggestion)
    }

    override fun startInWriteAction(): Boolean = true

    override fun getPriority(): PriorityAction.Priority = PriorityAction.Priority.NORMAL
}
