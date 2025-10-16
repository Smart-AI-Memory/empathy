/**
 * Coach VS Code Extension
 * Main entry point for the extension
 *
 * Copyright 2025 Deep Study AI, LLC
 * Licensed under the Apache License, Version 2.0
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from 'vscode-languageclient/node';
import { CoachPanel } from './views/coach-panel';
import { WizardsTreeProvider } from './views/wizard-tree';
import { ArtifactsTreeProvider } from './views/artifact-tree';
import { CoachCodeActionProvider } from './providers/code-actions';
import { CoachHoverProvider } from './providers/hover';
import { CoachDiagnosticsProvider } from './providers/diagnostics';

let client: LanguageClient | undefined;
let coachPanel: CoachPanel | undefined;
let diagnosticsProvider: CoachDiagnosticsProvider | undefined;

export async function activate(context: vscode.ExtensionContext) {
    console.log('Coach extension activating...');

    // Start Language Server
    await startLanguageServer(context);

    // Initialize UI components
    coachPanel = new CoachPanel(context, client!);

    // Register tree view providers
    const wizardsProvider = new WizardsTreeProvider(client!);
    const artifactsProvider = new ArtifactsTreeProvider();

    vscode.window.registerTreeDataProvider('coach.wizardsView', wizardsProvider);
    vscode.window.registerTreeDataProvider('coach.artifactsView', artifactsProvider);

    // Register providers
    const codeActionProvider = new CoachCodeActionProvider(client!);
    const hoverProvider = new CoachHoverProvider(client!);
    diagnosticsProvider = new CoachDiagnosticsProvider(client!, context);

    // Register code actions for all supported languages
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { scheme: 'file' },
            codeActionProvider,
            {
                providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
            }
        )
    );

    // Register hover provider
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(
            { scheme: 'file' },
            hoverProvider
        )
    );

    // Set up diagnostics on file open and change
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(doc => {
            diagnosticsProvider?.analyzeDocument(doc);
        })
    );

    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(event => {
            diagnosticsProvider?.analyzeDocument(event.document);
        })
    );

    // Analyze all open documents
    vscode.workspace.textDocuments.forEach(doc => {
        diagnosticsProvider?.analyzeDocument(doc);
    });

    // Register commands
    registerCommands(context, artifactsProvider);

    // Set up auto-triggers
    setupAutoTriggers(context);

    // Show welcome message on first activation
    const isFirstTime = context.globalState.get('coach.firstActivation', true);
    if (isFirstTime) {
        await showWelcomeMessage();
        await context.globalState.update('coach.firstActivation', false);
    }

    // Update status bar
    updateStatusBar('Coach: Ready', '$(check) All systems operational');

    console.log('Coach extension activated successfully');
}

export function deactivate(): Thenable<void> | undefined {
    if (client) {
        return client.stop();
    }
    return undefined;
}

async function startLanguageServer(context: vscode.ExtensionContext) {
    // Path to LSP server (auto-detect or use configured path)
    const config = vscode.workspace.getConfiguration('coach');
    let serverPath = config.get<string>('lsp.serverPath', '');

    if (!serverPath) {
        // Auto-detect: look for lsp/server.py in workspace
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            serverPath = path.join(workspaceFolder.uri.fsPath, 'examples', 'coach', 'lsp', 'server.py');
        }
    }

    // Server options: run Python LSP server
    const serverOptions: ServerOptions = {
        command: 'python3',
        args: ['-m', 'lsp.server'],
        transport: TransportKind.stdio,
        options: {
            cwd: path.dirname(path.dirname(serverPath)) // examples/coach directory
        }
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: 'file', language: 'python' },
            { scheme: 'file', language: 'javascript' },
            { scheme: 'file', language: 'typescript' },
            { scheme: 'file', language: 'typescriptreact' },
            { scheme: 'file', language: 'javascriptreact' },
            { scheme: 'file', language: 'java' },
            { scheme: 'file', language: 'kotlin' },
            { scheme: 'file', language: 'go' },
            { scheme: 'file', language: 'rust' },
            { scheme: 'file', language: 'ruby' },
            { scheme: 'file', language: 'php' },
            { scheme: 'file', language: 'csharp' }
        ],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*')
        }
    };

    // Create and start the client
    client = new LanguageClient(
        'coachLanguageServer',
        'Coach Language Server',
        serverOptions,
        clientOptions
    );

    await client.start();
    console.log('Coach Language Server started');

    // Health check
    try {
        const health = await client.sendRequest('coach/healthCheck', []);
        console.log('Coach LSP health check:', health);
    } catch (error) {
        console.error('Coach LSP health check failed:', error);
        vscode.window.showErrorMessage('Coach Language Server failed to start. Check that Python 3.12+ is installed.');
    }
}

function registerCommands(context: vscode.ExtensionContext, artifactsProvider: ArtifactsTreeProvider) {
    // Analyze current file
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.analyzeFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('PerformanceWizard', 'Analyze current file for issues', editor.document.uri);
        })
    );

    // Debug function
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.debugFunction', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || !editor.selection) {
                vscode.window.showWarningMessage('No code selected');
                return;
            }

            const selectedText = editor.document.getText(editor.selection);
            await runWizardAnalysis('DebuggingWizard', `Debug this function:\n${selectedText}`, editor.document.uri);
        })
    );

    // Generate tests
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.generateTests', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('TestingWizard', 'Generate comprehensive test suite', editor.document.uri);
        })
    );

    // Security audit
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.securityAudit', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('SecurityWizard', 'Run security audit', editor.document.uri);
        })
    );

    // Performance profile
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.performanceProfile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('PerformanceWizard', 'Profile performance and identify bottlenecks', editor.document.uri);
        })
    );

    // Generate API spec
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.generateAPISpec', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('APIWizard', 'Generate OpenAPI specification', editor.document.uri);
        })
    );

    // Accessibility check
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.a11yCheck', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('AccessibilityWizard', 'Check accessibility (WCAG 2.1 AA)', editor.document.uri);
        })
    );

    // Refactor
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.refactor', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('RefactoringWizard', 'Suggest refactorings', editor.document.uri);
        })
    );

    // Database review
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.databaseReview', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            await runWizardAnalysis('DatabaseWizard', 'Review database schema and queries', editor.document.uri);
        })
    );

    // Multi-wizard review
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.startMultiWizard', async () => {
            // Show quick pick for scenario
            const scenario = await vscode.window.showQuickPick([
                'new_api_endpoint',
                'database_migration',
                'production_incident',
                'new_feature_launch',
                'performance_issue',
                'compliance_audit',
                'global_expansion',
                'new_developer_onboarding'
            ], {
                placeHolder: 'Select collaboration scenario'
            });

            if (!scenario) {
                return;
            }

            const editor = vscode.window.activeTextEditor;
            const files = editor ? [editor.document.uri.toString()] : [];

            await runMultiWizardReview(scenario, files, artifactsProvider);
        })
    );

    // Show panel
    context.subscriptions.push(
        vscode.commands.registerCommand('coach.showPanel', () => {
            if (coachPanel) {
                coachPanel.show();
            }
        })
    );
}

async function runWizardAnalysis(wizardName: string, task: string, fileUri: vscode.Uri) {
    if (!client) {
        vscode.window.showErrorMessage('Coach Language Server not connected');
        return;
    }

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Coach ${wizardName}`,
        cancellable: false
    }, async (progress) => {
        progress.report({ message: 'Analyzing...' });

        try {
            const result = await client.sendRequest('coach/runWizard', [
                wizardName,
                {
                    role: 'developer',
                    task: task,
                    context: fileUri.toString()
                }
            ]);

            // Show result in panel
            if (coachPanel) {
                coachPanel.showWizardResult(result);
            }

            // Show notification
            vscode.window.showInformationMessage(
                `${wizardName} completed (confidence: ${Math.round(result.overall_confidence * 100)}%)`
            );

        } catch (error) {
            vscode.window.showErrorMessage(`Coach ${wizardName} failed: ${error}`);
        }
    });
}

async function runMultiWizardReview(scenario: string, files: string[], artifactsProvider: ArtifactsTreeProvider) {
    if (!client) {
        vscode.window.showErrorMessage('Coach Language Server not connected');
        return;
    }

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Coach Multi-Wizard Review`,
        cancellable: false
    }, async (progress) => {
        progress.report({ message: `Running ${scenario}...` });

        try {
            const result = await client.sendRequest('coach/multiWizardReview', [scenario, files]);

            // Show result in panel
            if (coachPanel) {
                coachPanel.showMultiWizardResult(result);
            }

            // Add artifacts to tree view
            artifactsProvider.addArtifacts(result);

            // Show notification
            vscode.window.showInformationMessage(
                `Multi-wizard review completed: ${result.routing.length} wizards collaborated`
            );

        } catch (error) {
            vscode.window.showErrorMessage(`Multi-wizard review failed: ${error}`);
        }
    });
}

function setupAutoTriggers(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('coach');

    // Auto-trigger on file save
    if (config.get('autoTriggers.onFileSave')) {
        context.subscriptions.push(
            vscode.workspace.onDidSaveTextDocument(async (document) => {
                const wizards = config.get<string[]>('autoTriggers.onFileSave', []);
                for (const wizard of wizards) {
                    await runWizardAnalysis(wizard, 'Auto-analysis on save', document.uri);
                }
            })
        );
    }

    // Auto-trigger on test failure (detect via terminal output)
    if (config.get('autoTriggers.onTestFailure')) {
        // This would require terminal output monitoring
        // Implementation depends on test framework
    }
}

function updateStatusBar(text: string, tooltip: string) {
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = text;
    statusBarItem.tooltip = tooltip;
    statusBarItem.command = 'coach.showPanel';
    statusBarItem.show();
}

async function showWelcomeMessage() {
    const selection = await vscode.window.showInformationMessage(
        'Welcome to Coach! AI with Level 4 Anticipatory Empathy for software development.',
        'Show Tutorial',
        'View Wizards',
        'Dismiss'
    );

    if (selection === 'Show Tutorial') {
        vscode.env.openExternal(vscode.Uri.parse('https://docs.coach-ai.dev/tutorial'));
    } else if (selection === 'View Wizards') {
        vscode.commands.executeCommand('coach.showPanel');
    }
}
