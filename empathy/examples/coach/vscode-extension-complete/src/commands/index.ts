import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { CoachLSPClient } from '../lsp/CoachLSPClient';
import { AnalysisService } from '../services/AnalysisService';
import { WizardRegistry } from '../services/WizardRegistry';

export function registerCommands(
    context: vscode.ExtensionContext,
    lspClient: CoachLSPClient,
    analysisService: AnalysisService,
    wizardRegistry: WizardRegistry,
    providers: any
): void {
    // Analyze File
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.analyzeFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active file to analyze');
                return;
            }

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Coach: Analyzing file...',
                cancellable: false
            }, async (progress) => {
                try {
                    const results = await analysisService.analyzeWithAllWizards(
                        editor.document,
                        editor.document.languageId
                    );

                    if (results.length === 0) {
                        vscode.window.showInformationMessage('No issues found!');
                    } else {
                        vscode.window.showInformationMessage(
                            `Found ${results.length} analysis result(s). Check Problems panel.`
                        );
                    }

                    providers.resultsProvider.refresh();
                } catch (error) {
                    vscode.window.showErrorMessage(`Analysis failed: ${error}`);
                }
            });
        })
    );

    // Analyze Workspace
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.analyzeWorkspace', async () => {
            const files = await vscode.workspace.findFiles('**/*.{py,js,ts,java,go,rs}', '**/node_modules/**');

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Coach: Analyzing workspace...',
                cancellable: true
            }, async (progress, token) => {
                let completed = 0;
                for (const file of files) {
                    if (token.isCancellationRequested) {
                        break;
                    }

                    progress.report({
                        message: `${completed}/${files.length} files`,
                        increment: (1 / files.length) * 100
                    });

                    try {
                        const document = await vscode.workspace.openTextDocument(file);
                        await analysisService.analyzeWithAllWizards(document, document.languageId);
                    } catch (error) {
                        console.error(`Failed to analyze ${file.fsPath}:`, error);
                    }

                    completed++;
                }

                const stats = analysisService.getStatistics();
                vscode.window.showInformationMessage(
                    `Workspace analysis complete! Errors: ${stats.errors}, Warnings: ${stats.warnings}`
                );

                providers.resultsProvider.refresh();
            });
        })
    );

    // Security Audit
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.securityAudit', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                return;
            }

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Coach: Running security audit...'
            }, async () => {
                const result = await analysisService.analyzeWithWizard(
                    editor.document,
                    'SecurityWizard',
                    'security_engineer',
                    'Comprehensive security audit'
                );

                const panel = vscode.window.createWebviewPanel(
                    'coachSecurityAudit',
                    'Security Audit Results',
                    vscode.ViewColumn.Two,
                    {}
                );

                panel.webview.html = generateSecurityAuditHTML(result);
            });
        })
    );

    // Multi-Wizard Review
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.multiWizardReview', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                return;
            }

            const scenario = detectScenario(editor.document);
            const wizards = wizardRegistry.getCollaborationWizards(scenario);

            if (wizards.length === 0) {
                vscode.window.showInformationMessage('No collaboration scenario detected');
                return;
            }

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Coach: Multi-wizard review (${scenario})...`
            }, async () => {
                const result = await analysisService.multiWizardAnalysis(
                    editor.document,
                    wizards,
                    scenario
                );

                const panel = vscode.window.createWebviewPanel(
                    'coachMultiWizard',
                    'Multi-Wizard Review',
                    vscode.ViewColumn.Two,
                    {}
                );

                panel.webview.html = generateMultiWizardHTML(result);
            });
        })
    );

    // Level 4 Predictions
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.level4Predictions', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                return;
            }

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Coach: Generating Level 4 predictions...'
            }, async () => {
                const predictions = await analysisService.getPredictions(editor.document);

                const panel = vscode.window.createWebviewPanel(
                    'coachPredictions',
                    'Level 4 Predictions',
                    vscode.ViewColumn.Two,
                    {}
                );

                panel.webview.html = generatePredictionsHTML(predictions);
                providers.predictionsProvider.refresh();
            });
        })
    );

    // Clear Results
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.clearResults', () => {
            analysisService.clearResults();
            providers.resultsProvider.refresh();
            vscode.window.showInformationMessage('Coach results cleared');
        })
    );

    // Refresh Results
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.refreshResults', () => {
            providers.resultsProvider.refresh();
            providers.wizardsProvider.refresh();
            providers.predictionsProvider.refresh();
        })
    );

    // Show Settings
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.showSettings', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'coach');
        })
    );

    // New Wizard Project (Framework feature - Approach 2)
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.newWizardProject', async () => {
            const folder = await vscode.window.showOpenDialog({
                canSelectFolders: true,
                canSelectFiles: false,
                canSelectMany: false,
                openLabel: 'Create Project Here'
            });

            if (!folder || folder.length === 0) {
                return;
            }

            const projectName = await vscode.window.showInputBox({
                prompt: 'Enter project name',
                placeHolder: 'my-coach-wizard'
            });

            if (!projectName) {
                return;
            }

            const projectPath = path.join(folder[0].fsPath, projectName);
            createWizardProject(projectPath, projectName);

            vscode.window.showInformationMessage(
                `Created Coach wizard project at ${projectPath}`,
                'Open Project'
            ).then(selection => {
                if (selection === 'Open Project') {
                    vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(projectPath));
                }
            });
        })
    );

    // New Wizard File (Framework feature - Approach 2)
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.newWizard', async () => {
            const wizardName = await vscode.window.showInputBox({
                prompt: 'Enter wizard name',
                placeHolder: 'ExampleWizard'
            });

            if (!wizardName) {
                return;
            }

            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }

            const wizardPath = path.join(workspaceFolder.uri.fsPath, 'wizards', `${wizardName.toLowerCase()}.wizard.py`);
            createWizardFile(wizardPath, wizardName);

            const doc = await vscode.workspace.openTextDocument(wizardPath);
            await vscode.window.showTextDocument(doc);
        })
    );
}

function detectScenario(document: vscode.TextDocument): string {
    const text = document.getText().toLowerCase();
    const fileName = path.basename(document.fileName).toLowerCase();

    if (text.includes('payment') || text.includes('stripe')) return 'payment';
    if (text.includes('auth') || text.includes('login')) return 'authentication';
    if (fileName.includes('controller') || fileName.includes('api')) return 'api';
    if (fileName.includes('test') || fileName.includes('spec')) return 'testing';
    if (fileName.includes('docker') || fileName.includes('yaml')) return 'deployment';

    return 'general';
}

function createWizardProject(projectPath: string, projectName: string): void {
    // Create directory structure
    fs.mkdirSync(projectPath, { recursive: true });
    fs.mkdirSync(path.join(projectPath, 'wizards'));
    fs.mkdirSync(path.join(projectPath, 'tests'));
    fs.mkdirSync(path.join(projectPath, 'config'));

    // Create files (similar to JetBrains implementation)
    // ... files created here
}

function createWizardFile(wizardPath: string, wizardName: string): void {
    const template = `from coach.base_wizard import BaseWizard
from coach.types import WizardResult, Severity

class ${wizardName}(BaseWizard):
    """${wizardName} wizard."""

    def __init__(self):
        super().__init__(
            name="${wizardName}",
            description="",
            version="1.0.0"
        )

    def analyze(self, code: str, context: dict) -> WizardResult:
        """Analyze the code and return results."""
        # TODO: Implement analysis logic

        return WizardResult(
            wizard=self.name,
            diagnosis="",
            severity=Severity.INFO,
            recommendations=[],
            code_examples=[],
            references=[]
        )
`;

    fs.mkdirSync(path.dirname(wizardPath), { recursive: true });
    fs.writeFileSync(wizardPath, template);
}

function generateSecurityAuditHTML(result: any): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #e74c3c; }
        .recommendation { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Security Audit Results</h1>
    <h2>Severity: ${result.severity}</h2>
    <p>${result.diagnosis}</p>
    <h3>Recommendations:</h3>
    ${result.recommendations.map((r: string) => `<div class="recommendation">${r}</div>`).join('')}
</body>
</html>`;
}

function generateMultiWizardHTML(result: any): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .wizard { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Multi-Wizard Review: ${result.scenario}</h1>
    <p><strong>Wizards:</strong> ${result.wizards.join(', ')}</p>
    <h2>Summary:</h2>
    <p>${result.summary}</p>
    <h3>Individual Results:</h3>
    ${result.results.map((r: any) => `
        <div class="wizard">
            <h4>${r.wizard}</h4>
            <p>${r.diagnosis}</p>
        </div>
    `).join('')}
</body>
</html>`;
}

function generatePredictionsHTML(predictions: any[]): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .prediction { background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ffc107; }
        .error { border-left-color: #e74c3c; background: #ffe6e6; }
    </style>
</head>
<body>
    <h1>Level 4 Predictions</h1>
    ${predictions.map(p => `
        <div class="prediction ${p.severity === 'ERROR' ? 'error' : ''}">
            <h3>${p.issue}</h3>
            <p><strong>Timeframe:</strong> ~${p.timeframe} days</p>
            <p><strong>Confidence:</strong> ${(p.confidence * 100).toFixed(0)}%</p>
            <p><strong>Impact:</strong> ${p.impact}</p>
            <p><strong>Preventive Action:</strong> ${p.preventiveAction}</p>
        </div>
    `).join('')}
</body>
</html>`;
}
