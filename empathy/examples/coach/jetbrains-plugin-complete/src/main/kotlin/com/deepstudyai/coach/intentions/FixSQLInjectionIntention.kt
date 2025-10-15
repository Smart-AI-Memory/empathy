package com.deepstudyai.coach.intentions

import com.intellij.codeInsight.intention.IntentionAction
import com.intellij.codeInsight.intention.PriorityAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Intention action to fix SQL injection vulnerabilities.
 *
 * Suggests using parameterized queries instead of string concatenation.
 */
class FixSQLInjectionIntention : IntentionAction, PriorityAction {

    override fun getText(): String = "Fix SQL injection vulnerability (use parameterized query)"

    override fun getFamilyName(): String = "Coach/Security"

    override fun isAvailable(project: Project, editor: Editor?, file: PsiFile?): Boolean {
        if (editor == null || file == null) return false

        // Check if the current line contains potential SQL injection
        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Simple heuristic: look for SQL keywords with string concatenation
        return lineText.contains(Regex("(SELECT|INSERT|UPDATE|DELETE).*\\+.*", RegexOption.IGNORE_CASE))
    }

    override fun invoke(project: Project, editor: Editor?, file: PsiFile?) {
        if (editor == null || file == null) return

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Generate fix based on language
        val fixedText = when {
            file.name.endsWith(".java") || file.name.endsWith(".kt") -> {
                convertToJavaParameterizedQuery(lineText)
            }
            file.name.endsWith(".py") -> {
                convertToPythonParameterizedQuery(lineText)
            }
            file.name.endsWith(".js") || file.name.endsWith(".ts") -> {
                convertToJavaScriptParameterizedQuery(lineText)
            }
            else -> lineText
        }

        if (fixedText != lineText) {
            document.replaceString(lineStartOffset, lineEndOffset, fixedText)
        }
    }

    private fun convertToJavaParameterizedQuery(query: String): String {
        // Example: "SELECT * FROM users WHERE id = " + userId
        // Convert to: "SELECT * FROM users WHERE id = ?" // and use PreparedStatement

        if (query.contains("\"SELECT") || query.contains("'SELECT")) {
            val comment = "  // TODO: Use PreparedStatement with parameter binding"
            return query.replace(Regex("\\+\\s*\\w+"), " = ?") + comment
        }
        return query
    }

    private fun convertToPythonParameterizedQuery(query: String): String {
        // Example: f"SELECT * FROM users WHERE id = {user_id}"
        // Convert to: "SELECT * FROM users WHERE id = %s"  # and use parameter binding

        if (query.contains("f\"") || query.contains("f'")) {
            val comment = "  # TODO: Use parameterized query with cursor.execute(sql, params)"
            return query.replace(Regex("\\{\\w+\\}"), "%s") + comment
        }
        return query
    }

    private fun convertToJavaScriptParameterizedQuery(query: String): String {
        // Example: `SELECT * FROM users WHERE id = ${userId}`
        // Convert to: "SELECT * FROM users WHERE id = $1"  // and use parameterized query

        var paramIndex = 1
        val result = query.replace(Regex("\\$\\{\\w+\\}")) {
            "$" + paramIndex++
        }

        if (result != query) {
            return result + "  // TODO: Use parameterized query"
        }
        return query
    }

    override fun startInWriteAction(): Boolean = true

    override fun getPriority(): PriorityAction.Priority = PriorityAction.Priority.HIGH
}
