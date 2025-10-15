import * as vscode from 'vscode';
import { AnalysisService } from '../services/AnalysisService';

export class CodeActionProvider implements vscode.CodeActionProvider {
    static readonly providedCodeActionKinds = [
        vscode.CodeActionKind.QuickFix
    ];

    private analysisService: AnalysisService;

    constructor(analysisService: AnalysisService) {
        this.analysisService = analysisService;
    }

    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): vscode.CodeAction[] {
        const codeActions: vscode.CodeAction[] = [];

        // Get Coach diagnostics
        const coachDiagnostics = context.diagnostics.filter(d =>
            d.source?.startsWith('Coach')
        );

        for (const diagnostic of coachDiagnostics) {
            // Create quick fixes based on diagnostic
            codeActions.push(
                ...this.createQuickFixes(document, diagnostic)
            );
        }

        return codeActions;
    }

    private createQuickFixes(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction[] {
        const fixes: vscode.CodeAction[] = [];

        // Extract wizard ID from diagnostic
        const wizardId = diagnostic.code as string;

        // Get analysis result
        const result = this.analysisService.getAnalysisResult(
            document.uri.fsPath,
            wizardId
        );

        if (!result || !result.result.recommendations) {
            return fixes;
        }

        // Create a quick fix for each recommendation
        result.result.recommendations.slice(0, 3).forEach((recommendation, index) => {
            const fix = new vscode.CodeAction(
                recommendation,
                vscode.CodeActionKind.QuickFix
            );

            fix.diagnostics = [diagnostic];
            fix.edit = new vscode.WorkspaceEdit();

            // For now, we'll add a comment with the recommendation
            // In production, we'd implement specific fixes based on the wizard
            const position = diagnostic.range.start;
            const commentText = this.createCommentForRecommendation(
                recommendation,
                document.languageId
            );

            fix.edit.insert(
                document.uri,
                position,
                commentText
            );

            fixes.push(fix);
        });

        return fixes;
    }

    private createCommentForRecommendation(
        recommendation: string,
        languageId: string
    ): string {
        const commentStart = this.getCommentStart(languageId);
        return `${commentStart} TODO (Coach): ${recommendation}\n`;
    }

    private getCommentStart(languageId: string): string {
        const commentStarts: Record<string, string> = {
            'python': '#',
            'javascript': '//',
            'typescript': '//',
            'java': '//',
            'go': '//',
            'rust': '//',
            'csharp': '//',
            'cpp': '//',
            'c': '//',
            'php': '//',
            'ruby': '#',
            'yaml': '#',
            'shell': '#',
            'bash': '#'
        };

        return commentStarts[languageId] || '//';
    }
}
