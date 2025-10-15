import * as vscode from 'vscode';
import { CoachLSPClient } from './lsp/CoachLSPClient';
import { WizardRegistry } from './services/WizardRegistry';
import { AnalysisService } from './services/AnalysisService';
import { CacheService } from './services/CacheService';
import { DiagnosticsManager } from './diagnostics/DiagnosticsManager';
import { CodeActionProvider } from './codeActions/CodeActionProvider';
import { CompletionProvider } from './completion/CompletionProvider';
import { CoachResultsProvider } from './views/CoachResultsProvider';
import { CoachWizardsProvider } from './views/CoachWizardsProvider';
import { CoachPredictionsProvider } from './views/CoachPredictionsProvider';
import { PredictionDecorator } from './decorators/PredictionDecorator';
import { registerCommands } from './commands';

let lspClient: CoachLSPClient | undefined;
let analysisService: AnalysisService | undefined;
let diagnosticsManager: DiagnosticsManager | undefined;

export async function activate(context: vscode.ExtensionContext) {
    console.log('Coach extension activating...');

    try {
        // Initialize services
        const cacheService = new CacheService();
        const wizardRegistry = new WizardRegistry();

        // Initialize LSP client
        const config = vscode.workspace.getConfiguration('coach');
        if (config.get('autoStartServer')) {
            lspClient = new CoachLSPClient(context);
            await lspClient.start();
        }

        // Initialize analysis service
        analysisService = new AnalysisService(lspClient!, wizardRegistry, cacheService);

        // Initialize diagnostics
        diagnosticsManager = new DiagnosticsManager(analysisService, wizardRegistry);
        context.subscriptions.push(diagnosticsManager);

        // Register code actions
        const codeActionProvider = new CodeActionProvider(analysisService);
        context.subscriptions.push(
            vscode.languages.registerCodeActionsProvider(
                { scheme: 'file' },
                codeActionProvider,
                { providedCodeActionKinds: CodeActionProvider.providedCodeActionKinds }
            )
        );

        // Register completion provider (Framework feature - Approach 2)
        const completionProvider = new CompletionProvider();
        context.subscriptions.push(
            vscode.languages.registerCompletionItemProvider(
                { language: 'python', pattern: '**/*.wizard.py' },
                completionProvider,
                '.'
            )
        );

        // Register tree view providers
        const resultsProvider = new CoachResultsProvider(analysisService);
        const wizardsProvider = new CoachWizardsProvider(wizardRegistry);
        const predictionsProvider = new CoachPredictionsProvider(analysisService);

        vscode.window.registerTreeDataProvider('coachResultsView', resultsProvider);
        vscode.window.registerTreeDataProvider('coachWizardsView', wizardsProvider);
        vscode.window.registerTreeDataProvider('coachPredictionsView', predictionsProvider);

        // Initialize prediction decorator
        const predictionDecorator = new PredictionDecorator(analysisService);
        context.subscriptions.push(predictionDecorator);

        // Register all commands
        registerCommands(context, lspClient!, analysisService, wizardRegistry, {
            resultsProvider,
            wizardsProvider,
            predictionsProvider
        });

        // Watch for configuration changes
        context.subscriptions.push(
            vscode.workspace.onDidChangeConfiguration(async (e) => {
                if (e.affectsConfiguration('coach')) {
                    // Restart LSP client if server settings changed
                    if (e.affectsConfiguration('coach.pythonPath') ||
                        e.affectsConfiguration('coach.serverScriptPath')) {
                        await lspClient?.restart();
                    }

                    // Clear cache if caching disabled
                    if (e.affectsConfiguration('coach.enableCaching')) {
                        cacheService.clear();
                    }
                }
            })
        );

        // Watch for document changes for real-time analysis
        const config2 = vscode.workspace.getConfiguration('coach');
        if (config2.get('enableRealTimeAnalysis')) {
            let debounceTimer: NodeJS.Timeout | undefined;
            context.subscriptions.push(
                vscode.workspace.onDidChangeTextDocument((e) => {
                    if (debounceTimer) {
                        clearTimeout(debounceTimer);
                    }

                    const debounceMs = config2.get<number>('analysisDebounceMs') || 1000;
                    debounceTimer = setTimeout(async () => {
                        const document = e.document;
                        if (document.uri.scheme === 'file') {
                            await diagnosticsManager?.updateDiagnostics(document);
                        }
                    }, debounceMs);
                })
            );
        }

        // Watch for active editor changes
        context.subscriptions.push(
            vscode.window.onDidChangeActiveTextEditor((editor) => {
                if (editor) {
                    predictionDecorator.updateDecorations(editor);
                }
            })
        );

        console.log('Coach extension activated successfully!');

        // Show welcome message
        vscode.window.showInformationMessage(
            'Coach extension activated! Use "Coach: Analyze File" to get started.',
            'Open Settings',
            'Analyze File'
        ).then(selection => {
            if (selection === 'Open Settings') {
                vscode.commands.executeCommand('coach.showSettings');
            } else if (selection === 'Analyze File') {
                vscode.commands.executeCommand('coach.analyzeFile');
            }
        });

    } catch (error) {
        console.error('Failed to activate Coach extension:', error);
        vscode.window.showErrorMessage(`Coach extension activation failed: ${error}`);
    }
}

export function deactivate(): Thenable<void> | undefined {
    console.log('Coach extension deactivating...');

    if (lspClient) {
        return lspClient.stop();
    }

    return undefined;
}
