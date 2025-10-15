package com.deepstudyai.coach.intentions

import com.intellij.codeInsight.intention.IntentionAction
import com.intellij.codeInsight.intention.PriorityAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Intention action to fix XSS (Cross-Site Scripting) vulnerabilities.
 *
 * Suggests proper output encoding/escaping for user input.
 */
class FixXSSIntention : IntentionAction, PriorityAction {

    override fun getText(): String = "Fix XSS vulnerability (escape user input)"

    override fun getFamilyName(): String = "Coach/Security"

    override fun isAvailable(project: Project, editor: Editor?, file: PsiFile?): Boolean {
        if (editor == null || file == null) return false

        // Check if the current context has potential XSS
        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        // Look for HTML rendering with variables
        return lineText.contains(Regex("(innerHTML|outerHTML|document\\.write|\\$\\{.*\\})", RegexOption.IGNORE_CASE))
    }

    override fun invoke(project: Project, editor: Editor?, file: PsiFile?) {
        if (editor == null || file == null) return

        val document = editor.document
        val caretOffset = editor.caretModel.offset
        val lineNumber = document.getLineNumber(caretOffset)
        val lineStartOffset = document.getLineStartOffset(lineNumber)
        val lineEndOffset = document.getLineEndOffset(lineNumber)
        val lineText = document.getText(com.intellij.openapi.util.TextRange(lineStartOffset, lineEndOffset))

        val fixedText = when {
            file.name.endsWith(".html") || file.name.endsWith(".jsx") || file.name.endsWith(".tsx") -> {
                fixHTMLXSS(lineText)
            }
            file.name.endsWith(".js") || file.name.endsWith(".ts") -> {
                fixJavaScriptXSS(lineText)
            }
            file.name.endsWith(".java") -> {
                fixJavaXSS(lineText)
            }
            file.name.endsWith(".py") -> {
                fixPythonXSS(lineText)
            }
            else -> lineText
        }

        if (fixedText != lineText) {
            document.replaceString(lineStartOffset, lineEndOffset, fixedText)
        }
    }

    private fun fixHTMLXSS(line: String): String {
        // Replace innerHTML with textContent where appropriate
        if (line.contains("innerHTML")) {
            return line.replace("innerHTML", "textContent") + "  // Changed to textContent to prevent XSS"
        }
        return line
    }

    private fun fixJavaScriptXSS(line: String): String {
        if (line.contains("innerHTML")) {
            return line.replace("innerHTML", "textContent") + "  // Use textContent or sanitize HTML"
        }
        if (line.contains("document.write")) {
            return "// TODO: Replace document.write with safer DOM manipulation\n" + line
        }
        return line
    }

    private fun fixJavaXSS(line: String): String {
        if (line.contains("response.getWriter")) {
            return line + "  // TODO: Use OWASP Java Encoder or escape HTML entities"
        }
        return line
    }

    private fun fixPythonXSS(line: String): String {
        if (line.contains("render_template_string") || line.contains("format(")) {
            return line + "  # TODO: Use Jinja2 autoescaping or html.escape()"
        }
        return line
    }

    override fun startInWriteAction(): Boolean = true

    override fun getPriority(): PriorityAction.Priority = PriorityAction.Priority.HIGH
}
