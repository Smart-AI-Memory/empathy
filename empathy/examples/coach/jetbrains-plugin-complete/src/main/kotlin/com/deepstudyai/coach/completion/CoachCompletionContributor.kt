package com.deepstudyai.coach.completion

import com.intellij.codeInsight.completion.*
import com.intellij.codeInsight.lookup.LookupElementBuilder
import com.intellij.patterns.PlatformPatterns
import com.intellij.util.ProcessingContext
import com.intellij.openapi.util.IconLoader
import javax.swing.Icon

/**
 * Code completion contributor for Coach framework APIs.
 *
 * Provides intelligent autocomplete for wizard development.
 */
class CoachCompletionContributor : CompletionContributor() {

    companion object {
        private val COACH_ICON: Icon = IconLoader.getIcon("/icons/coach.svg", CoachCompletionContributor::class.java)
    }

    init {
        // Completion for Python files
        extend(
            CompletionType.BASIC,
            PlatformPatterns.psiElement(),
            CoachApiCompletionProvider()
        )
    }
}

/**
 * Completion provider for Coach framework APIs.
 */
class CoachApiCompletionProvider : CompletionProvider<CompletionParameters>() {

    override fun addCompletions(
        parameters: CompletionParameters,
        context: ProcessingContext,
        result: CompletionResultSet
    ) {
        val file = parameters.originalFile
        if (!file.name.endsWith(".py")) {
            return
        }

        val text = file.text
        val icon = IconLoader.getIcon("/icons/coach.svg", CoachCompletionContributor::class.java)

        // Add Coach framework imports
        if (text.contains("from coach") || text.contains("import coach")) {
            addCoachImportCompletions(result, icon)
        }

        // Add wizard class completions
        if (text.contains("BaseWizard") || text.contains("class") && text.contains("Wizard")) {
            addWizardMethodCompletions(result, icon)
        }

        // Add WizardResult completions
        if (text.contains("WizardResult") || text.contains("return")) {
            addWizardResultCompletions(result, icon)
        }

        // Add Severity completions
        if (text.contains("Severity")) {
            addSeverityCompletions(result, icon)
        }
    }

    private fun addCoachImportCompletions(result: CompletionResultSet, icon: Icon) {
        result.addElement(
            LookupElementBuilder.create("from coach.base_wizard import BaseWizard")
                .withIcon(icon)
                .withTypeText("Coach Framework")
                .withPresentableText("BaseWizard import")
        )

        result.addElement(
            LookupElementBuilder.create("from coach.types import WizardResult, Severity, CodeExample")
                .withIcon(icon)
                .withTypeText("Coach Framework")
                .withPresentableText("Coach types import")
        )

        result.addElement(
            LookupElementBuilder.create("from langchain.chat_models import ChatOpenAI")
                .withIcon(icon)
                .withTypeText("LangChain")
                .withPresentableText("LangChain ChatOpenAI")
        )
    }

    private fun addWizardMethodCompletions(result: CompletionResultSet, icon: Icon) {
        result.addElement(
            LookupElementBuilder.create(
                """def analyze(self, code: str, context: dict) -> WizardResult:
    """Analyze the code and return results."""
    # TODO: Implement analysis logic

    return WizardResult(
        wizard=self.name,
        diagnosis="",
        severity=Severity.INFO,
        recommendations=[],
        code_examples=[],
        references=[]
    )"""
            )
                .withIcon(icon)
                .withTypeText("Coach Wizard")
                .withPresentableText("analyze() method")
        )

        result.addElement(
            LookupElementBuilder.create(
                """def __init__(self):
    super().__init__(
        name="YourWizard",
        description="Wizard description",
        version="1.0.0"
    )"""
            )
                .withIcon(icon)
                .withTypeText("Coach Wizard")
                .withPresentableText("__init__() method")
        )
    }

    private fun addWizardResultCompletions(result: CompletionResultSet, icon: Icon) {
        result.addElement(
            LookupElementBuilder.create(
                """WizardResult(
    wizard="WizardName",
    diagnosis="Issue description",
    severity=Severity.WARNING,
    recommendations=[
        "Recommendation 1",
        "Recommendation 2"
    ],
    code_examples=[],
    references=[]
)"""
            )
                .withIcon(icon)
                .withTypeText("Coach Framework")
                .withPresentableText("WizardResult")
        )

        result.addElement(
            LookupElementBuilder.create(
                """CodeExample(
    before=\"\"\"
# Before code
\"\"\",
    after=\"\"\"
# After code
\"\"\",
    explanation="Explanation"
)"""
            )
                .withIcon(icon)
                .withTypeText("Coach Framework")
                .withPresentableText("CodeExample")
        )
    }

    private fun addSeverityCompletions(result: CompletionResultSet, icon: Icon) {
        result.addElement(
            LookupElementBuilder.create("Severity.ERROR")
                .withIcon(icon)
                .withTypeText("Critical issues")
                .withPresentableText("Severity.ERROR")
        )

        result.addElement(
            LookupElementBuilder.create("Severity.WARNING")
                .withIcon(icon)
                .withTypeText("Warning level")
                .withPresentableText("Severity.WARNING")
        )

        result.addElement(
            LookupElementBuilder.create("Severity.INFO")
                .withIcon(icon)
                .withTypeText("Informational")
                .withPresentableText("Severity.INFO")
        )
    }
}
