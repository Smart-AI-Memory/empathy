import * as vscode from 'vscode';
import { AnalysisService } from '../services/AnalysisService';
import { WizardRegistry } from '../services/WizardRegistry';

export class DiagnosticsManager implements vscode.Disposable {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private analysisService: AnalysisService;
    private wizardRegistry: WizardRegistry;

    constructor(analysisService: AnalysisService, wizardRegistry: WizardRegistry) {
        this.analysisService = analysisService;
        this.wizardRegistry = wizardRegistry;
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('coach');
    }

    async updateDiagnostics(document: vscode.TextDocument): Promise<void> {
        if (document.uri.scheme !== 'file') {
            return;
        }

        const language = document.languageId;
        const results = await this.analysisService.analyzeWithAllWizards(document, language);

        const diagnostics: vscode.Diagnostic[] = [];

        for (const result of results) {
            if (result.severity === 'INFO' && result.recommendations.length === 0) {
                continue; // Skip INFO with no recommendations
            }

            const severity = this.convertSeverity(result.severity);
            const message = this.formatDiagnosticMessage(result);

            // Create diagnostic for entire file
            // In a production implementation, we'd parse the diagnosis to find specific line numbers
            const range = new vscode.Range(
                new vscode.Position(0, 0),
                new vscode.Position(0, 0)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                message,
                severity
            );

            diagnostic.source = `Coach (${result.wizard})`;
            diagnostic.code = result.wizard;

            diagnostics.push(diagnostic);
        }

        this.diagnosticCollection.set(document.uri, diagnostics);
    }

    clearDiagnostics(uri?: vscode.Uri): void {
        if (uri) {
            this.diagnosticCollection.delete(uri);
        } else {
            this.diagnosticCollection.clear();
        }
    }

    private convertSeverity(severity: 'ERROR' | 'WARNING' | 'INFO'): vscode.DiagnosticSeverity {
        switch (severity) {
            case 'ERROR':
                return vscode.DiagnosticSeverity.Error;
            case 'WARNING':
                return vscode.DiagnosticSeverity.Warning;
            case 'INFO':
                return vscode.DiagnosticSeverity.Information;
        }
    }

    private formatDiagnosticMessage(result: any): string {
        let message = result.diagnosis;

        if (result.recommendations && result.recommendations.length > 0) {
            message += '\n\nRecommendations:\n';
            result.recommendations.slice(0, 3).forEach((rec: string, index: number) => {
                message += `${index + 1}. ${rec}\n`;
            });
        }

        if (result.estimatedTime) {
            message += `\nEstimated fix time: ${result.estimatedTime}`;
        }

        return message;
    }

    dispose(): void {
        this.diagnosticCollection.dispose();
    }
}
