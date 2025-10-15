import * as vscode from 'vscode';

export class CompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];

        // Coach framework imports
        completions.push(
            this.createImportCompletion('BaseWizard', 'from coach.base_wizard import BaseWizard'),
            this.createImportCompletion('WizardResult', 'from coach.types import WizardResult, Severity, CodeExample')
        );

        // Check if we're in a wizard class
        const text = document.getText();
        if (text.includes('BaseWizard') || text.includes('class') && text.includes('Wizard')) {
            completions.push(
                this.createMethodCompletion('analyze', this.getAnalyzeMethodSnippet()),
                this.createMethodCompletion('__init__', this.getInitMethodSnippet())
            );
        }

        // WizardResult completions
        if (text.includes('WizardResult') || text.includes('return')) {
            completions.push(
                this.createClassCompletion('WizardResult', this.getWizardResultSnippet())
            );
        }

        // Severity completions
        if (text.includes('Severity')) {
            completions.push(
                this.createEnumCompletion('ERROR', 'Severity.ERROR'),
                this.createEnumCompletion('WARNING', 'Severity.WARNING'),
                this.createEnumCompletion('INFO', 'Severity.INFO')
            );
        }

        return completions;
    }

    private createImportCompletion(label: string, insertText: string): vscode.CompletionItem {
        const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Module);
        item.insertText = new vscode.SnippetString(insertText);
        item.detail = 'Coach Framework';
        return item;
    }

    private createMethodCompletion(label: string, snippet: string): vscode.CompletionItem {
        const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Method);
        item.insertText = new vscode.SnippetString(snippet);
        item.detail = 'Coach Wizard Method';
        return item;
    }

    private createClassCompletion(label: string, snippet: string): vscode.CompletionItem {
        const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Class);
        item.insertText = new vscode.SnippetString(snippet);
        item.detail = 'Coach Framework';
        return item;
    }

    private createEnumCompletion(label: string, insertText: string): vscode.CompletionItem {
        const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.EnumMember);
        item.insertText = insertText;
        item.detail = 'Severity Level';
        return item;
    }

    private getAnalyzeMethodSnippet(): string {
        return `def analyze(self, code: str, context: dict) -> WizardResult:
    """Analyze the code and return results."""
    # TODO: Implement analysis logic

    return WizardResult(
        wizard=self.name,
        diagnosis="\${1:Diagnosis}",
        severity=Severity.\${2|INFO,WARNING,ERROR|},
        recommendations=[
            "\${3:Recommendation}"
        ],
        code_examples=[],
        references=[]
    )
    \$0`;
    }

    private getInitMethodSnippet(): string {
        return `def __init__(self):
    super().__init__(
        name="\${1:WizardName}",
        description="\${2:Description}",
        version="1.0.0"
    )
    \$0`;
    }

    private getWizardResultSnippet(): string {
        return `WizardResult(
    wizard="\${1:WizardName}",
    diagnosis="\${2:Diagnosis}",
    severity=Severity.\${3|INFO,WARNING,ERROR|},
    recommendations=[
        "\${4:Recommendation}"
    ],
    code_examples=[],
    references=[]
)`;
    }
}
