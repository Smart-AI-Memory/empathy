/**
 * Empathy Framework VS Code Extension
 *
 * Provides integration with Empathy Framework including:
 * - Status bar showing health score and cost savings
 * - Command palette for all CLI commands
 * - Sidebar with pattern browser
 * - Inline diagnostics from inspection
 * - Quick fix actions and auto-scan on save
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { PowerPanel } from './panels/PowerPanel';
import { EmpathyDashboardProvider } from './panels/EmpathyDashboardPanel';
import { MemoryPanelProvider } from './panels/MemoryPanelProvider';
// REMOVED in v3.5.5: Refactor Advisor panel - kept for future use
// import { RefactorAdvisorPanel } from './panels/RefactorAdvisorPanel';
import { ResearchSynthesisPanel } from './panels/ResearchSynthesisPanel';
import { CodeReviewPanelProvider } from './panels/CodeReviewPanelProvider';
import { InitializeWizardPanel } from './panels/InitializeWizardPanel';
// REMOVED in v3.5.5: Test Generator panel - kept for future use
// import { TestGeneratorPanel } from './panels/TestGeneratorPanel';
// HIDDEN in v3.5.5: Workflow Wizard panel - temporarily hidden
// import { WorkflowWizardPanel } from './panels/WorkflowWizardPanel';
import { DocAnalysisPanel } from './panels/DocAnalysisPanel';
import { initializeProject, showWelcomeIfNeeded as showInitializeWelcome } from './commands/initializeProject';
import { WorkflowHistoryService, WORKFLOW_METADATA } from './services/WorkflowHistoryService';
import { KeyboardLayoutDetector } from './services/KeyboardLayoutDetector';
import { FeedbackService } from './services/FeedbackService';
import { NextCommandHintService } from './services/NextCommandHintService';
import { SocraticFormService } from './services/SocraticFormService';
import { GuidedPanelProvider } from './panels/GuidedPanelProvider';

// Status bar items
let statusBarItem: vscode.StatusBarItem;
let quickActionItems: vscode.StatusBarItem[] = [];

// Health provider (used for diagnostics)
let healthProvider: HealthTreeProvider;

// Extension path (for accessing bundled scripts)
let extensionPath: string;

// Refresh timer
let refreshTimer: NodeJS.Timeout | undefined;

// Diagnostics collection for Problem Panel (Feature F)
let diagnosticCollection: vscode.DiagnosticCollection;

// Security diagnostics collection (separate from lint issues)
let securityDiagnosticCollection: vscode.DiagnosticCollection;

// File watcher for auto-scan (Feature E)
let fileWatcher: vscode.FileSystemWatcher | undefined;

// File watcher for security findings
let securityFindingsWatcher: vscode.FileSystemWatcher | undefined;

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Empathy Framework extension activated');

    // Store extension path for accessing bundled scripts
    extensionPath = context.extensionPath;

    // Initialize workflow history service
    WorkflowHistoryService.getInstance().initialize(context);

    // Initialize next command hint service (ghost text suggestions)
    NextCommandHintService.getInstance().initialize(context);

    // Initialize Socratic form service (LLM-powered conversations)
    SocraticFormService.getInstance().initialize(context);

    // Initialize keyboard layout detector and run first-time detection
    const keyboardDetector = KeyboardLayoutDetector.getInstance();
    keyboardDetector.initialize(context);
    keyboardDetector.promptFirstTimeDetection().then(async () => {
        const layout = await keyboardDetector.detect();
        console.log(`Empathy: Keyboard layout: ${layout}`);
    });

    // Create status bar
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.command = 'empathy.status';
    context.subscriptions.push(statusBarItem);

    // Create quick action status bar items (Enhancement 3: Status Bar Toolbar)
    const quickActions = [
        { icon: '$(calendar)', tooltip: 'Morning Briefing (Ctrl+Shift+E M)', command: 'empathy.morning', priority: 99 },
        { icon: '$(rocket)', tooltip: 'Pre-Ship Check (Ctrl+Shift+E S)', command: 'empathy.ship', priority: 98 },
        { icon: '$(tools)', tooltip: 'Fix All Issues (Ctrl+Shift+E F)', command: 'empathy.fixAll', priority: 97 },
        { icon: '$(play)', tooltip: 'Run Workflow (Ctrl+Shift+E W)', command: 'empathy.runWorkflowQuick', priority: 96 },
    ];

    for (const action of quickActions) {
        const item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            action.priority
        );
        item.text = action.icon;
        item.tooltip = action.tooltip;
        item.command = action.command;
        quickActionItems.push(item);
        context.subscriptions.push(item);
    }

    // Create diagnostics collection (Feature F)
    diagnosticCollection = vscode.languages.createDiagnosticCollection('empathy');
    context.subscriptions.push(diagnosticCollection);

    // Create security diagnostics collection (separate from lint issues)
    securityDiagnosticCollection = vscode.languages.createDiagnosticCollection('empathy-security');
    context.subscriptions.push(securityDiagnosticCollection);

    // Create health provider (for diagnostics support)
    healthProvider = new HealthTreeProvider(diagnosticCollection, securityDiagnosticCollection);

    // Register dashboard webview provider (with context for persistence)
    const dashboardProvider = new EmpathyDashboardProvider(context.extensionUri, context);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            EmpathyDashboardProvider.viewType,
            dashboardProvider
        )
    );

    // Memory panel (Beta) - requires backend server for full functionality
    // Only register if beta features are enabled
    const config = vscode.workspace.getConfiguration('empathy');
    const showBetaFeatures = config.get<boolean>('showBetaFeatures', false);
    let memoryProvider: MemoryPanelProvider | null = null;

    if (showBetaFeatures) {
        memoryProvider = new MemoryPanelProvider(context.extensionUri, context);
        context.subscriptions.push(
            vscode.window.registerWebviewViewProvider(
                MemoryPanelProvider.viewType,
                memoryProvider,
                {
                    webviewOptions: {
                        retainContextWhenHidden: true
                    }
                }
            )
        );
    }

    // Register Code Review Panel (shows interactive code review findings)
    const codeReviewProvider = CodeReviewPanelProvider.getInstance(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            CodeReviewPanelProvider.viewType,
            codeReviewProvider,
            {
                webviewOptions: {
                    retainContextWhenHidden: true
                }
            }
        )
    );

    // REMOVED in v3.5.5: Refactor Advisor panel - kept for future use
    // const refactorAdvisorProvider = new RefactorAdvisorPanel(context.extensionUri, context);
    // context.subscriptions.push(
    //     vscode.window.registerWebviewViewProvider(
    //         RefactorAdvisorPanel.viewType,
    //         refactorAdvisorProvider,
    //         {
    //             webviewOptions: {
    //                 retainContextWhenHidden: true
    //             }
    //         }
    //     )
    // );

    // DEPRECATED in v1.4.0: Research Synthesis panel - kept for future use
    // const researchSynthesisProvider = new ResearchSynthesisPanel(context.extensionUri, context);
    // context.subscriptions.push(
    //     vscode.window.registerWebviewViewProvider(
    //         ResearchSynthesisPanel.viewType,
    //         researchSynthesisProvider,
    //         {
    //             webviewOptions: {
    //                 retainContextWhenHidden: true
    //             }
    //         }
    //     )
    // );

    // REMOVED in v3.5.5: Test Generator panel - kept for future use
    // Opens in main editor area (not sidebar) using createOrShow pattern
    // context.subscriptions.push(
    //     vscode.commands.registerCommand('empathy.openTestGenerator', () => {
    //         TestGeneratorPanel.createOrShow(context.extensionUri);
    //     })
    // );

    // HIDDEN in v3.5.5: Workflow Wizard panel - temporarily hidden, kept for future use
    // const workflowWizardProvider = new WorkflowWizardPanel(context.extensionUri, context);
    // context.subscriptions.push(
    //     vscode.window.registerWebviewViewProvider(
    //         WorkflowWizardPanel.viewType,
    //         workflowWizardProvider,
    //         {
    //             webviewOptions: {
    //                 retainContextWhenHidden: true
    //             }
    //         }
    //     )
    // );

    // Register commands - existing
    const commands = [
        { name: 'empathy.morning', handler: cmdMorning },
        { name: 'empathy.ship', handler: cmdShip },
        { name: 'empathy.fixAll', handler: cmdFixAll },
        { name: 'empathy.learn', handler: cmdLearn },
        { name: 'empathy.costs', handler: cmdCosts },
        { name: 'empathy.dashboard', handler: cmdDashboard },
        { name: 'empathy.syncClaude', handler: cmdSyncClaude },
        { name: 'empathy.status', handler: cmdStatus },
        // New commands for Health view actions (Features A, B, C, D)
        { name: 'empathy.refreshHealth', handler: cmdRefreshHealth },
        { name: 'empathy.runScan', handler: cmdRunScan },
        { name: 'empathy.runSecurityScan', handler: cmdRunSecurityScan },
        { name: 'empathy.fixLint', handler: cmdFixLint },
        { name: 'empathy.fixFormat', handler: cmdFixFormat },
        { name: 'empathy.runTests', handler: cmdRunTests },
        { name: 'empathy.viewDetails', handler: cmdViewDetails },
        { name: 'empathy.openFile', handler: cmdOpenFile },
        { name: 'empathy.ignoreIssue', handler: cmdIgnoreIssue },
        { name: 'empathy.openWebDashboard', handler: cmdOpenWebDashboard },
        // Memory commands (Beta) - only functional if beta features enabled
        { name: 'empathy.memory.showPanel', handler: () => {
            if (showBetaFeatures) {
                vscode.commands.executeCommand('empathy-memory.focus');
            } else {
                vscode.window.showInformationMessage('Memory features are in beta. Enable "empathy.showBetaFeatures" in settings to use.');
            }
        }},
        { name: 'empathy.memory.refreshStatus', handler: () => {
            if (memoryProvider) {
                memoryProvider.refresh();
                vscode.window.showInformationMessage('Memory status refreshed');
            } else {
                vscode.window.showInformationMessage('Memory features are in beta. Enable "empathy.showBetaFeatures" in settings to use.');
            }
        }},
        // Initialize wizard (accepts optional { force: true } to skip "already initialized" check)
        { name: 'empathy.initializeProject', handler: (options?: { force?: boolean }) => initializeProject(context, options) },
        // REMOVED in v3.5.5: Test Generator wizard
        // { name: 'empathy.testGenerator.show', handler: () => vscode.commands.executeCommand('empathy.openTestGenerator') },
        // Workflow Wizard - temporarily hidden in v3.5.5
        { name: 'empathy.workflowWizard.show', handler: () => {
            vscode.window.showInformationMessage('Workflow Wizard is being redesigned. Use Cmd+Shift+E W for quick workflow access.');
        }},
        // Context menu commands (Enhancement 4)
        { name: 'empathy.reviewFile', handler: cmdReviewFile },
        { name: 'empathy.scanFolder', handler: cmdScanFolder },
        { name: 'empathy.generateTests', handler: cmdGenerateTests },
        { name: 'empathy.securityAudit', handler: cmdSecurityAudit },
        // Workflow history (Keyboard Conductor)
        { name: 'empathy.recentWorkflows', handler: cmdRecentWorkflows },
        // Keyboard layout configuration
        { name: 'empathy.applyKeyboardLayout', handler: cmdApplyKeyboardLayout },
        { name: 'empathy.redetectKeyboardLayout', handler: cmdRedetectKeyboardLayout },
        // Power user mode toggle
        { name: 'empathy.togglePowerMode', handler: cmdTogglePowerMode },
        // Guided panel (Socratic forms)
        { name: 'empathy.openGuidedPanel', handler: () => cmdOpenGuidedPanel(context) },
        { name: 'empathy.openPlanMode', handler: () => cmdOpenGuidedPanel(context, 'plan-refinement') },
        { name: 'empathy.openLearnMode', handler: () => cmdOpenGuidedPanel(context, 'learning-mode') },
        // Focus sidebar dashboard
        { name: 'empathy.focusDashboard', handler: cmdFocusDashboard },
    ];

    for (const cmd of commands) {
        context.subscriptions.push(
            vscode.commands.registerCommand(cmd.name, cmd.handler)
        );
    }

    // Register Power Panel command (needs extensionUri)
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.openPowerPanel', () => {
            PowerPanel.createOrShow(context.extensionUri);
        })
    );

    // Register Documentation Analysis Panel command
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.openDocAnalysis', () => {
            DocAnalysisPanel.createOrShow(context.extensionUri);
        })
    );

    // Register Socratic Refinement / Agent Workflow Designer command
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.socraticRefinement', async () => {
            const socraticService = SocraticFormService.getInstance();
            socraticService.initialize(context);

            // Show agent-design mode selection
            const modeChoice = await vscode.window.showQuickPick(
                [
                    {
                        label: '$(organization) Design Agent Crew',
                        description: 'Create a multi-agent workflow team',
                        value: 'crew-composition'
                    },
                    {
                        label: '$(list-tree) Decompose Complex Task',
                        description: 'Break down a task into agent-assignable subtasks',
                        value: 'task-decomposition'
                    },
                    {
                        label: '$(file-code) Engineer Agent Prompt',
                        description: 'Create an optimized XML-enhanced prompt',
                        value: 'prompt-engineering'
                    }
                ],
                {
                    title: 'Agent Workflow Designer',
                    placeHolder: 'What would you like to design?'
                }
            );

            if (!modeChoice) {
                return;
            }

            // Start Socratic form with agent-design mode
            await socraticService.startForm('agent-design', {
                mode: modeChoice.value,
                initialContext: `Design mode: ${modeChoice.label.replace(/\$\([^)]+\)\s*/, '')}`
            });
        })
    );

    // Register command to open workflow reports in editor
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.openReportInEditor', async (args: { workflowName: string; output: string; input?: string }) => {
            const workflowNames: Record<string, string> = {
                'code-review': 'Code Review',
                'bug-predict': 'Bug Prediction',
                'security-audit': 'Security Audit',
                'perf-audit': 'Performance Audit',
                'refactor-plan': 'Refactoring Plan',
                'health-check': 'Health Check',
                'pr-review': 'PR Review',
                'pro-review': 'Code Analysis',
            };

            const displayName = workflowNames[args.workflowName] || args.workflowName;
            const timestamp = new Date().toLocaleString();

            let content = `# ${displayName} Report\n\n`;
            content += `**Generated:** ${timestamp}\n`;
            if (args.input) {
                content += `**Target:** ${args.input}\n`;
            }
            content += `\n---\n\n`;
            content += args.output;
            content += `\n\n---\n*Generated by Empathy Framework*`;

            const doc = await vscode.workspace.openTextDocument({
                content,
                language: 'markdown',
            });
            await vscode.window.showTextDocument(doc, {
                viewColumn: vscode.ViewColumn.One,
                preview: false,
                preserveFocus: false
            });
        })
    );

    // Register goToLocation command for navigating to findings
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.goToLocation',
            async (args: { file: string; line?: number; column?: number }) => {
                try {
                    // Handle workspace-relative paths
                    let uri: vscode.Uri | undefined;
                    if (path.isAbsolute(args.file)) {
                        uri = vscode.Uri.file(args.file);
                    } else {
                        // Try to resolve relative to workspace folders
                        const workspaceFolders = vscode.workspace.workspaceFolders;
                        if (!workspaceFolders || workspaceFolders.length === 0) {
                            vscode.window.showErrorMessage('No workspace folder open');
                            return;
                        }

                        // Try each workspace folder until we find the file
                        for (const wsFolder of workspaceFolders) {
                            const candidateUri = vscode.Uri.joinPath(wsFolder.uri, args.file);
                            try {
                                await vscode.workspace.fs.stat(candidateUri);
                                uri = candidateUri;
                                break;
                            } catch {
                                // File not found in this workspace, try next
                                continue;
                            }
                        }

                        if (!uri) {
                            vscode.window.showErrorMessage(`File not found: ${args.file}`);
                            return;
                        }
                    }

                    const doc = await vscode.workspace.openTextDocument(uri);
                    const line = Math.max(0, (args.line ?? 1) - 1); // Convert to 0-indexed
                    const col = Math.max(0, (args.column ?? 1) - 1); // Convert to 0-indexed

                    await vscode.window.showTextDocument(doc, {
                        selection: new vscode.Range(line, col, line, col),
                        viewColumn: vscode.ViewColumn.One
                    });
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to open file: ${error}`);
                }
            }
        )
    );

    // Register quick workflow command - allows running any workflow directly with WebView output
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.runWorkflowQuick', async (workflowArg?: string) => {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }

            // Hierarchical workflow picker - organized by category
            const workflowCategories = [
                {
                    category: 'Code Quality',
                    categoryIcon: '$(eye)',
                    workflows: [
                        { label: 'Code Review', value: 'code-review', icon: '$(eye)', type: 'file' as const },
                        { label: 'Bug Prediction', value: 'bug-predict', icon: '$(bug)', type: 'folder' as const },
                        { label: 'Code Analysis', value: 'pro-review', icon: '$(code)', type: 'file' as const },
                        { label: 'Refactoring Plan', value: 'refactor-plan', icon: '$(tools)', type: 'folder' as const },
                    ]
                },
                {
                    category: 'Security & Compliance',
                    categoryIcon: '$(shield)',
                    workflows: [
                        { label: 'Security Audit', value: 'security-audit', icon: '$(shield)', type: 'folder' as const },
                    ]
                },
                {
                    category: 'Testing & Performance',
                    categoryIcon: '$(beaker)',
                    workflows: [
                        { label: 'Test Generation', value: 'test-gen', icon: '$(beaker)', type: 'folder' as const },
                        { label: 'Performance Audit', value: 'perf-audit', icon: '$(dashboard)', type: 'folder' as const },
                    ]
                },
                {
                    category: 'Documentation & Release',
                    categoryIcon: '$(book)',
                    workflows: [
                        { label: 'Documentation', value: 'document-gen', icon: '$(book)', type: 'folder' as const },
                        { label: 'Release Prep', value: 'release-prep', icon: '$(rocket)', type: 'folder' as const },
                    ]
                },
                {
                    category: 'Project Health',
                    categoryIcon: '$(heart)',
                    workflows: [
                        { label: 'Health Check', value: 'health-check', icon: '$(heart)', type: 'folder' as const },
                        { label: 'Dependency Check', value: 'dependency-check', icon: '$(package)', type: 'folder' as const },
                        { label: 'PR Review', value: 'pr-review', icon: '$(git-pull-request)', type: 'folder' as const },
                        { label: 'Research Synthesis', value: 'research-synthesis', icon: '$(search)', type: 'folder' as const },
                    ]
                },
            ];

            // Flatten for direct lookup
            const allWorkflows = workflowCategories.flatMap(c => c.workflows);

            // Select workflow
            let selectedWorkflow: typeof allWorkflows[0] | undefined;
            if (workflowArg) {
                selectedWorkflow = allWorkflows.find(w => w.value === workflowArg);
            }
            if (!selectedWorkflow) {
                // Step 1: Pick category (or show all)
                const categoryItems = [
                    { label: '$(list-unordered) All Workflows', description: 'Show all workflows', value: '__all__' },
                    ...workflowCategories.map(c => ({
                        label: `${c.categoryIcon} ${c.category}`,
                        description: `${c.workflows.length} workflows`,
                        value: c.category
                    }))
                ];

                const categoryPick = await vscode.window.showQuickPick(categoryItems, {
                    placeHolder: 'Select category or show all workflows',
                    ignoreFocusOut: true
                });
                if (!categoryPick) { return; }

                // Step 2: Pick workflow from category
                let workflowsToShow: typeof allWorkflows;
                if (categoryPick.value === '__all__') {
                    workflowsToShow = allWorkflows;
                } else {
                    const selectedCategory = workflowCategories.find(c => c.category === categoryPick.value);
                    workflowsToShow = selectedCategory?.workflows || allWorkflows;
                }

                const pick = await vscode.window.showQuickPick(
                    workflowsToShow.map(w => ({ ...w, label: `${w.icon} ${w.label}`, description: w.value })),
                    { placeHolder: 'Select a workflow to run', ignoreFocusOut: true }
                );
                if (!pick) { return; }
                selectedWorkflow = pick;
            }

            // Select target
            let targetPath = '.';
            if (selectedWorkflow.type === 'folder') {
                const folderResult = await vscode.window.showQuickPick([
                    { label: '$(folder) Entire Project', path: '.' },
                    { label: '$(folder-opened) Select Folder...', path: '__browse__' }
                ], { placeHolder: 'Select scope', ignoreFocusOut: true });

                if (!folderResult) { return; }
                if (folderResult.path === '__browse__') {
                    const uri = await vscode.window.showOpenDialog({
                        canSelectFiles: false, canSelectFolders: true, canSelectMany: false,
                        defaultUri: vscode.Uri.file(workspaceFolder)
                    });
                    if (!uri?.[0]) { return; }
                    targetPath = uri[0].fsPath;
                }
            } else {
                const fileResult = await vscode.window.showQuickPick([
                    { label: '$(file) Current File', path: '__active__' },
                    { label: '$(folder) Entire Project', path: '.' },
                    { label: '$(file-add) Select File...', path: '__browse__' }
                ], { placeHolder: 'Select scope', ignoreFocusOut: true });

                if (!fileResult) { return; }
                if (fileResult.path === '__active__') {
                    targetPath = vscode.window.activeTextEditor?.document.uri.fsPath || '.';
                } else if (fileResult.path === '__browse__') {
                    const uri = await vscode.window.showOpenDialog({
                        canSelectFiles: true, canSelectFolders: false, canSelectMany: false,
                        defaultUri: vscode.Uri.file(workspaceFolder)
                    });
                    if (!uri?.[0]) { return; }
                    targetPath = uri[0].fsPath;
                }
            }

            // Create WebView with loading spinner
            const panel = vscode.window.createWebviewPanel(
                'empathyWorkflow',
                `${selectedWorkflow.label} Report`,
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            panel.webview.html = getLoadingHtml(selectedWorkflow.label, targetPath);

            // Store last output for copy functionality
            let lastOutput = '';

            // Handle messages from WebView
            panel.webview.onDidReceiveMessage(async (message) => {
                console.log('[EmpathyWorkflow] Received message:', message);
                switch (message.command) {
                    case 'copy':
                        await vscode.env.clipboard.writeText(lastOutput);
                        vscode.window.showInformationMessage('Report copied to clipboard');
                        break;
                    case 'runAgain':
                        console.log('[EmpathyWorkflow] Running workflow again');
                        panel.webview.html = getLoadingHtml(selectedWorkflow!.label, targetPath);
                        runWorkflow();
                        break;
                    case 'close':
                        panel.dispose();
                        break;
                }
            });

            // Function to run the workflow
            const runWorkflow = () => {
                const config = vscode.workspace.getConfiguration('empathy');
                const pythonPath = config.get<string>('pythonPath', 'python');
                const inputKey = selectedWorkflow!.value === 'health-check' ? 'path' : 'target';
                const args = ['-m', 'empathy_os.cli', 'workflow', 'run', selectedWorkflow!.value, '--input', JSON.stringify({ [inputKey]: targetPath })];

                // Record in workflow history (Keyboard Conductor feature)
                const historyService = WorkflowHistoryService.getInstance();
                const metadata = WORKFLOW_METADATA[selectedWorkflow!.value] || {
                    displayName: selectedWorkflow!.label,
                    icon: '$(play)'
                };
                historyService.recordExecution({
                    workflowId: selectedWorkflow!.value,
                    displayName: metadata.displayName,
                    target: targetPath,
                    icon: metadata.icon,
                });

                cp.execFile(pythonPath, args, { cwd: workspaceFolder, maxBuffer: 1024 * 1024 * 5 }, (error, stdout, stderr) => {
                    const output = stdout || stderr || (error ? error.message : 'No output');
                    lastOutput = output;
                    const timestamp = new Date().toLocaleString();
                    panel.webview.html = getReportHtml(selectedWorkflow!.label, targetPath, timestamp, output, error?.message || null, selectedWorkflow!.value);
                });
            };

            // Run workflow initially
            runWorkflow();
        })
    );

    // Register URI handler for "Run in Empathy" buttons from documentation
    // Example URI: vscode://Smart-AI-Memory.empathy-framework/runCommand?command=empathy%20init
    context.subscriptions.push(
        vscode.window.registerUriHandler({
            handleUri(uri: vscode.Uri) {
                console.log('Empathy URI Handler received:', uri.toString());

                if (uri.path === '/runCommand') {
                    const params = new URLSearchParams(uri.query);
                    const commandToRun = params.get('command');

                    if (commandToRun) {
                        // Security: Only allow empathy commands
                        if (!commandToRun.startsWith('empathy')) {
                            vscode.window.showErrorMessage(
                                'Only Empathy Framework commands are allowed via URI handler.'
                            );
                            return;
                        }

                        // Find or create a terminal and run the command
                        let terminal = vscode.window.terminals.find(t => t.name === 'Empathy Docs');
                        if (!terminal) {
                            terminal = vscode.window.createTerminal('Empathy Docs');
                        }
                        terminal.show();
                        terminal.sendText(commandToRun);

                        vscode.window.showInformationMessage(
                            `Running: ${commandToRun}`
                        );
                    } else {
                        vscode.window.showWarningMessage(
                            'No command specified in URI. Use ?command=empathy%20...'
                        );
                    }
                } else if (uri.path === '/openWorkflow') {
                    // Alternative: Open a specific workflow in the dashboard
                    const params = new URLSearchParams(uri.query);
                    const workflow = params.get('workflow');

                    if (workflow) {
                        // Focus the dashboard and trigger the workflow
                        vscode.commands.executeCommand('empathy-dashboard.focus');
                        vscode.window.showInformationMessage(
                            `Opening workflow: ${workflow}`
                        );
                    }
                } else {
                    vscode.window.showWarningMessage(
                        `Unknown Empathy URI path: ${uri.path}. Use /runCommand or /openWorkflow.`
                    );
                }
            }
        })
    );

    // Initialize
    updateStatusBar();
    startAutoRefresh(context);
    setupAutoScanOnSave(context); // Feature E
    setupSecurityFindingsWatcher(context); // Security diagnostics

    // Show welcome message on first activation
    showWelcomeIfNeeded(context);

    // Load initial diagnostics (Feature F)
    healthProvider.updateDiagnostics();
    healthProvider.updateSecurityDiagnostics(); // Load persisted security findings
}

/**
 * Extension deactivation
 */
export function deactivate() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    if (fileWatcher) {
        fileWatcher.dispose();
    }
    if (securityFindingsWatcher) {
        securityFindingsWatcher.dispose();
    }
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
    if (securityDiagnosticCollection) {
        securityDiagnosticCollection.dispose();
    }
}

// ============================================================================
// Command Handlers
// ============================================================================

async function cmdMorning() {
    runEmpathyCommand('morning', 'Morning Briefing');
}

async function cmdShip() {
    runEmpathyCommand('ship', 'Pre-Ship Check');
}

async function cmdFixAll() {
    await runEmpathyCommandWithProgress('fix-all', 'Fixing all issues...');
    healthProvider.refresh();
}

async function cmdLearn() {
    runEmpathyCommand('learn --analyze 20', 'Learning Patterns');
}

async function cmdCosts() {
    runEmpathyCommand('costs', 'API Costs');
}

async function cmdDashboard() {
    runEmpathyCommand('dashboard', 'Dashboard', { background: true });
    vscode.window.showInformationMessage(
        'Empathy Dashboard started. Check your browser.'
    );
}

async function cmdSyncClaude() {
    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Syncing patterns to Claude Code...',
            cancellable: false
        },
        async () => {
            const output = await runEmpathyCommandSilent('sync-claude');
            // Open in webview report panel for full visibility
            await vscode.commands.executeCommand('empathy.openReportInEditor', {
                workflowName: 'sync-claude',
                output,
                input: 'Sync Patterns to Claude Code'
            });
        }
    );
}

async function cmdStatus() {
    const data = await getStatusData();
    if (data) {
        const message = [
            `Patterns: ${data.patterns} learned`,
            `Health: ${data.health}`,
            `Costs: $${data.savings.toFixed(2)} saved`,
        ].join(' | ');
        vscode.window.showInformationMessage(`Empathy Status: ${message}`);
    }
}

// Feature A: Quick Fix for Lint
async function cmdFixLint() {
    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Fixing lint issues...',
            cancellable: false,
        },
        async () => {
            await runEmpathyCommandSilent('fix-all --lint-only');
            healthProvider.refresh();
            vscode.window.showInformationMessage('Lint issues fixed!');
        }
    );
}

// Feature A: Quick Fix for Format
async function cmdFixFormat() {
    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Formatting code...',
            cancellable: false,
        },
        async () => {
            await runEmpathyCommandSilent('fix-all --format-only');
            healthProvider.refresh();
            vscode.window.showInformationMessage('Code formatted!');
        }
    );
}

// Feature B: Refresh Health / Run Scan
async function cmdRefreshHealth() {
    healthProvider.refresh();
    healthProvider.updateDiagnostics();
    vscode.window.showInformationMessage('Health data refreshed');
}

async function cmdRunScan() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Running health scan...',
            cancellable: false,
        },
        async () => {
            // Run actual health checks via bundled Python script
            const config = vscode.workspace.getConfiguration('empathy');
            const pythonPath = config.get<string>('pythonPath', 'python');
            const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

            // Ensure .empathy directory exists
            if (!fs.existsSync(empathyDir)) {
                fs.mkdirSync(empathyDir, { recursive: true });
            }

            // Path to bundled health scan script (safe - no shell interpolation)
            const healthScriptPath = path.join(extensionPath, 'scripts', 'health_scan.py');

            return new Promise<void>((resolve) => {
                // Use execFile with array arguments to prevent command injection
                cp.execFile(pythonPath, [healthScriptPath, workspaceFolder, empathyDir],
                    { cwd: workspaceFolder, timeout: 60000 },
                    (error) => {
                        healthProvider.refresh();
                        healthProvider.updateDiagnostics();
                        updateStatusBar();
                        if (error) {
                            vscode.window.showWarningMessage('Health scan completed with warnings');
                        } else {
                            vscode.window.showInformationMessage('Health scan complete!');
                        }
                        resolve();
                    }
                );
            });
        }
    );
}

// Security Scan with diagnostics integration
async function cmdRunSecurityScan() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Running security scan...',
            cancellable: false,
        },
        async () => {
            const config = vscode.workspace.getConfiguration('empathy');
            const pythonPath = config.get<string>('pythonPath', 'python');
            const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

            // Ensure .empathy directory exists
            if (!fs.existsSync(empathyDir)) {
                fs.mkdirSync(empathyDir, { recursive: true });
            }

            return new Promise<void>((resolve) => {
                // Run security-audit workflow with JSON output
                const args = [
                    '-m', 'empathy_os.cli', 'workflow', 'run', 'security-audit',
                    '--input', JSON.stringify({ target: workspaceFolder }),
                    '--json'
                ];

                cp.execFile(pythonPath, args, {
                    cwd: workspaceFolder,
                    maxBuffer: 1024 * 1024 * 5, // 5MB buffer for large outputs
                    timeout: 120000 // 2 minute timeout
                }, (error, stdout, stderr) => {
                    try {
                        // Try to parse JSON output
                        const output = stdout || stderr || '';
                        const result = JSON.parse(output);

                        // Save findings to file
                        const findingsPath = path.join(empathyDir, 'security_findings.json');
                        fs.writeFileSync(findingsPath, JSON.stringify(result, null, 2));

                        // Update diagnostics
                        healthProvider.updateSecurityDiagnostics();

                        // Show summary notification
                        const assessment = result.assessment || {};
                        const breakdown = assessment.severity_breakdown || {};
                        const critical = breakdown.critical || 0;
                        const high = breakdown.high || 0;
                        const medium = breakdown.medium || 0;
                        const low = breakdown.low || 0;
                        const total = critical + high + medium + low;

                        if (critical > 0 || high > 0) {
                            vscode.window.showWarningMessage(
                                `Security scan: ${critical} critical, ${high} high, ${medium} medium, ${low} low findings. Check Problems panel.`
                            );
                        } else if (total > 0) {
                            vscode.window.showInformationMessage(
                                `Security scan complete: ${medium} medium, ${low} low findings`
                            );
                        } else {
                            vscode.window.showInformationMessage('Security scan complete - no issues found!');
                        }
                    } catch (parseErr) {
                        // JSON parse failed - maybe text output or error
                        if (error) {
                            vscode.window.showWarningMessage(`Security scan completed with errors: ${error.message}`);
                        } else {
                            vscode.window.showInformationMessage('Security scan complete');
                        }
                        console.error('Failed to parse security scan output:', parseErr);
                    }
                    resolve();
                });
            });
        }
    );
}

// Feature C: Run Tests
async function cmdRunTests() {
    runEmpathyCommand('ship --tests-only', 'Running Tests');
}

// Feature C: Open file at location
async function cmdOpenFile(filePath?: string, line?: number) {
    if (!filePath) {
        return;
    }
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        return;
    }

    const fullPath = path.isAbsolute(filePath)
        ? filePath
        : path.join(workspaceFolder, filePath);

    try {
        const doc = await vscode.workspace.openTextDocument(fullPath);
        const editor = await vscode.window.showTextDocument(doc);
        if (line && line > 0) {
            const position = new vscode.Position(line - 1, 0);
            editor.selection = new vscode.Selection(position, position);
            editor.revealRange(new vscode.Range(position, position));
        }
    } catch (err) {
        vscode.window.showErrorMessage(`Could not open file: ${filePath}`);
    }
}

// Feature D: View Details
async function cmdViewDetails(item?: HealthItem) {
    if (!item) {
        return;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        return;
    }

    // Show quick pick with options based on item type
    const options: string[] = [];
    if (item.label === 'Lint' || item.label === 'Types') {
        options.push('Fix Issues', 'Show in Terminal', 'View Report');
    } else if (item.label === 'Security') {
        options.push('View Report', 'Run Security Scan');
    } else if (item.label === 'Tests') {
        options.push('Run Tests', 'View Coverage Report');
    } else if (item.label === 'Tech Debt') {
        options.push('View Hotspots', 'Search TODOs');
    } else {
        options.push('Refresh', 'Open Dashboard');
    }

    const selected = await vscode.window.showQuickPick(options, {
        placeHolder: `Actions for ${item.label}`,
    });

    if (!selected) {
        return;
    }

    switch (selected) {
        case 'Fix Issues':
            cmdFixAll();
            break;
        case 'Show in Terminal':
            runEmpathyCommand('ship --verbose', 'Health Check');
            break;
        case 'View Report':
            runEmpathyCommand('dashboard', 'Dashboard', { background: true });
            break;
        case 'Run Security Scan':
            runEmpathyCommand('ship --security-only', 'Security Scan');
            break;
        case 'Run Tests':
            cmdRunTests();
            break;
        case 'View Coverage Report':
            const coverageFile = path.join(workspaceFolder, 'htmlcov', 'index.html');
            if (fs.existsSync(coverageFile)) {
                vscode.env.openExternal(vscode.Uri.file(coverageFile));
            } else {
                vscode.window.showWarningMessage('No coverage report found. Run tests first.');
            }
            break;
        case 'View Hotspots':
            runEmpathyCommand('patterns hotspots', 'Tech Debt Hotspots');
            break;
        case 'Search TODOs':
            vscode.commands.executeCommand('workbench.action.findInFiles', {
                query: 'TODO|FIXME|HACK',
                isRegex: true,
            });
            break;
        case 'Refresh':
            cmdRefreshHealth();
            break;
        case 'Open Dashboard':
            cmdDashboard();
            break;
    }
}

// Feature D: Ignore Issue (add to baseline)
async function cmdIgnoreIssue(item?: HealthItem) {
    if (!item) {
        return;
    }

    const reason = await vscode.window.showInputBox({
        prompt: 'Reason for ignoring this issue (optional)',
        placeHolder: 'e.g., False positive, Will fix in Q2',
    });

    if (reason === undefined) {
        return; // Cancelled
    }

    vscode.window.showInformationMessage(
        `Issue "${item.label}" would be added to baseline. (Feature coming soon)`
    );
}

// ===== Context Menu Commands (Enhancement 4) =====

/**
 * Review a file from context menu - runs code-review workflow on the file
 */
async function cmdReviewFile(uri?: vscode.Uri) {
    const filePath = uri?.fsPath || vscode.window.activeTextEditor?.document.uri.fsPath;
    if (!filePath) {
        vscode.window.showErrorMessage('No file selected');
        return;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const relativePath = filePath.replace(workspaceFolder.uri.fsPath + '/', '');

    // Run code-review workflow via the workflow command
    await vscode.commands.executeCommand('empathy.openReportInEditor', {
        workflowName: 'code-review',
        output: '', // Will be filled by the command
        input: relativePath
    });

    // Actually run the workflow
    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');

    vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: `Reviewing ${relativePath}...`, cancellable: false },
        async () => {
            const cp = await import('child_process');
            return new Promise<void>((resolve) => {
                cp.execFile(
                    pythonPath,
                    ['-m', 'empathy_os', 'workflow', 'run', 'code-review', '--input', JSON.stringify({ path: relativePath })],
                    { cwd: workspaceFolder.uri.fsPath, maxBuffer: 1024 * 1024 * 5 },
                    async (error, stdout, stderr) => {
                        const output = stdout || stderr || (error ? error.message : 'No output');
                        await vscode.commands.executeCommand('empathy.openReportInEditor', {
                            workflowName: 'code-review',
                            output,
                            input: relativePath
                        });
                        resolve();
                    }
                );
            });
        }
    );
}

/**
 * Scan a folder for bugs - runs bug-predict workflow
 */
async function cmdScanFolder(uri?: vscode.Uri) {
    const folderPath = uri?.fsPath;
    if (!folderPath) {
        vscode.window.showErrorMessage('No folder selected');
        return;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const relativePath = folderPath.replace(workspaceFolder.uri.fsPath + '/', '');
    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');

    vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: `Scanning ${relativePath} for bugs...`, cancellable: false },
        async () => {
            const cp = await import('child_process');
            return new Promise<void>((resolve) => {
                cp.execFile(
                    pythonPath,
                    ['-m', 'empathy_os', 'workflow', 'run', 'bug-predict', '--input', JSON.stringify({ path: relativePath })],
                    { cwd: workspaceFolder.uri.fsPath, maxBuffer: 1024 * 1024 * 5 },
                    async (error, stdout, stderr) => {
                        const output = stdout || stderr || (error ? error.message : 'No output');
                        await vscode.commands.executeCommand('empathy.openReportInEditor', {
                            workflowName: 'bug-predict',
                            output,
                            input: relativePath
                        });
                        resolve();
                    }
                );
            });
        }
    );
}

/**
 * Generate tests for a file/folder
 */
async function cmdGenerateTests(uri?: vscode.Uri) {
    const targetPath = uri?.fsPath || vscode.window.activeTextEditor?.document.uri.fsPath;
    if (!targetPath) {
        vscode.window.showErrorMessage('No file or folder selected');
        return;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const relativePath = targetPath.replace(workspaceFolder.uri.fsPath + '/', '');
    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');

    vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: `Generating tests for ${relativePath}...`, cancellable: false },
        async () => {
            const cp = await import('child_process');
            return new Promise<void>((resolve) => {
                cp.execFile(
                    pythonPath,
                    ['-m', 'empathy_os', 'workflow', 'run', 'test-gen', '--input', JSON.stringify({ path: relativePath })],
                    { cwd: workspaceFolder.uri.fsPath, maxBuffer: 1024 * 1024 * 5 },
                    async (error, stdout, stderr) => {
                        const output = stdout || stderr || (error ? error.message : 'No output');
                        await vscode.commands.executeCommand('empathy.openReportInEditor', {
                            workflowName: 'test-gen',
                            output,
                            input: relativePath
                        });
                        resolve();
                    }
                );
            });
        }
    );
}

/**
 * Run security audit on a folder
 */
async function cmdSecurityAudit(uri?: vscode.Uri) {
    const folderPath = uri?.fsPath;
    if (!folderPath) {
        vscode.window.showErrorMessage('No folder selected');
        return;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const relativePath = folderPath.replace(workspaceFolder.uri.fsPath + '/', '');
    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');

    vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: `Running security audit on ${relativePath}...`, cancellable: false },
        async () => {
            const cp = await import('child_process');
            return new Promise<void>((resolve) => {
                cp.execFile(
                    pythonPath,
                    ['-m', 'empathy_os', 'workflow', 'run', 'security-audit', '--input', JSON.stringify({ path: relativePath })],
                    { cwd: workspaceFolder.uri.fsPath, maxBuffer: 1024 * 1024 * 5 },
                    async (error, stdout, stderr) => {
                        const output = stdout || stderr || (error ? error.message : 'No output');
                        await vscode.commands.executeCommand('empathy.openReportInEditor', {
                            workflowName: 'security-audit',
                            output,
                            input: relativePath
                        });
                        resolve();
                    }
                );
            });
        }
    );
}

// ===== Recent Workflows Command (Keyboard Conductor) =====

/**
 * Show recent workflows picker and re-run selected workflow
 * Triggered by ctrl+shift+e z
 */
async function cmdRecentWorkflows() {
    const historyService = WorkflowHistoryService.getInstance();
    const selected = await historyService.showRecentWorkflowsPicker();

    if (selected) {
        // Re-run the selected workflow
        await vscode.commands.executeCommand('empathy.runWorkflowQuick', selected.workflowId);
    }
}

// ===== Keyboard Layout Configuration =====

/**
 * Apply keyboard layout optimized for user's keyboard
 * Supports QWERTY, Dvorak, and Colemak layouts
 */
async function cmdApplyKeyboardLayout() {
    const config = vscode.workspace.getConfiguration('empathy');
    const currentLayout = config.get<string>('keyboardLayout', 'qwerty');

    // Show layout picker
    const layouts = [
        { label: '$(keyboard) QWERTY', description: 'Default layout - M-S-F-D shortcuts', value: 'qwerty' },
        { label: '$(keyboard) Dvorak', description: 'A-O-E-U home row optimized', value: 'dvorak' },
        { label: '$(keyboard) Colemak', description: 'A-R-S-T home row optimized', value: 'colemak' },
    ];

    const selected = await vscode.window.showQuickPick(
        layouts.map(l => ({ ...l, picked: l.value === currentLayout })),
        { placeHolder: `Current: ${currentLayout.toUpperCase()} - Select keyboard layout` }
    );

    if (!selected) { return; }

    if (selected.value === 'qwerty') {
        // QWERTY uses default keybindings, no action needed
        await config.update('keyboardLayout', 'qwerty', vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(
            'QWERTY layout active. Default keybindings are already configured.'
        );
        return;
    }

    // For Dvorak/Colemak, show the keybindings file and guide user
    const layoutFile = path.join(extensionPath, 'keybindings', `${selected.value}.json`);

    try {
        const doc = await vscode.workspace.openTextDocument(layoutFile);
        await vscode.window.showTextDocument(doc, { preview: false });

        // Update setting
        await config.update('keyboardLayout', selected.value, vscode.ConfigurationTarget.Global);

        const action = await vscode.window.showInformationMessage(
            `${selected.value.toUpperCase()} layout selected. Copy the keybindings from this file to your keybindings.json.`,
            'Open Keyboard Shortcuts',
            'Dismiss'
        );

        if (action === 'Open Keyboard Shortcuts') {
            await vscode.commands.executeCommand('workbench.action.openGlobalKeybindingsFile');
        }
    } catch (err) {
        vscode.window.showErrorMessage(`Could not open ${selected.value} keybindings file.`);
    }
}

/**
 * Re-detect keyboard layout from OS
 * Uses FeedbackService for mode-appropriate feedback
 */
async function cmdRedetectKeyboardLayout() {
    const feedback = FeedbackService.getInstance();
    const hints = NextCommandHintService.getInstance();

    try {
        const detector = KeyboardLayoutDetector.getInstance();
        detector.clearCache();
        const detected = await detector.detect();

        const config = vscode.workspace.getConfiguration('empathy');
        const current = config.get<string>('keyboardLayout', 'qwerty');

        if (detected !== current) {
            await config.update('keyboardLayout', detected, vscode.ConfigurationTarget.Global);
            await feedback.notify(`Keyboard: ${detected.toUpperCase()} applied`, 'success');
        } else {
            await feedback.notify(`Keyboard: ${detected.toUpperCase()}`, 'success');
        }

        // Record for next command hints
        hints.recordCommand('empathy.redetectKeyboardLayout');
    } catch {
        await feedback.notify('Keyboard detection failed', 'error');
    }
}

/**
 * Toggle between guided and power feedback modes
 * Power mode: quick inline badges for experienced keyboard users
 * Guided mode: modal dialogs with explanations for new users
 */
async function cmdTogglePowerMode() {
    const config = vscode.workspace.getConfiguration('empathy');
    const current = config.get<string>('feedbackMode', 'guided');
    const newMode = current === 'guided' ? 'power' : 'guided';

    await config.update('feedbackMode', newMode, vscode.ConfigurationTarget.Global);

    // Use FeedbackService to show confirmation (demonstrates the mode)
    const feedback = FeedbackService.getInstance();
    const modeLabel = newMode === 'power' ? 'Power Mode' : 'Guided Mode';
    const modeDesc = newMode === 'power'
        ? 'Quick inline feedback - play your keyboard riffs!'
        : 'Modal dialogs with explanations';

    await feedback.notify(`${modeLabel}: ${modeDesc}`, 'success');

    // Record for next command hints
    NextCommandHintService.getInstance().recordCommand('empathy.togglePowerMode');
}

/**
 * Focus the Empathy sidebar dashboard
 */
async function cmdFocusDashboard(): Promise<void> {
    await vscode.commands.executeCommand('empathy-dashboard.focus');
}

/**
 * Open the Guided Panel with Socratic forms
 * Supports different form types: general, plan-refinement, workflow-customization, learning-mode
 */
function cmdOpenGuidedPanel(
    context: vscode.ExtensionContext,
    formType?: 'general' | 'plan-refinement' | 'workflow-customization' | 'learning-mode'
): void {
    console.log('[Empathy] cmdOpenGuidedPanel called with formType:', formType);
    try {
        GuidedPanelProvider.createOrShow(context.extensionUri, context, {
            formType: formType || 'general',
        });
        console.log('[Empathy] GuidedPanelProvider.createOrShow completed');
    } catch (error) {
        console.error('[Empathy] Error opening guided panel:', error);
        vscode.window.showErrorMessage(`Failed to open Guided Panel: ${error}`);
    }
}

// Open Full Web Dashboard
async function cmdOpenWebDashboard() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');

    // Check if dashboard server is already running
    try {
        const http = await import('http');
        const isRunning = await new Promise<boolean>((resolve) => {
            const req = http.request(
                { host: 'localhost', port: 8765, path: '/api/health', timeout: 1000 },
                (res) => resolve(res.statusCode === 200)
            );
            req.on('error', () => resolve(false));
            req.on('timeout', () => { req.destroy(); resolve(false); });
            req.end();
        });

        if (isRunning) {
            vscode.env.openExternal(vscode.Uri.parse('http://localhost:8765'));
            return;
        }
    } catch {
        // Server not running, continue to start it
    }

    // Start the dashboard server
    vscode.window.showInformationMessage('Starting Empathy Web Dashboard...');

    const proc = cp.spawn(pythonPath, ['-m', 'empathy_os.cli', 'dashboard', '--no-browser'], {
        cwd: workspaceFolder.uri.fsPath,
        detached: true,
        stdio: 'ignore'
    });
    proc.unref();

    // Wait for server to start, then open browser
    setTimeout(() => {
        vscode.env.openExternal(vscode.Uri.parse('http://localhost:8765'));
    }, 2500);
}

// ============================================================================
// Empathy Command Runner
// ============================================================================

interface RunOptions {
    background?: boolean;
}

async function runEmpathyCommand(
    command: string,
    title: string,
    options: RunOptions = {}
): Promise<void> {
    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    // Build arguments as array for safe execution (no shell interpolation)
    const args = ['-m', 'empathy_os.cli', ...command.split(/\s+/)];

    if (options.background) {
        // Use execFile with array arguments to prevent command injection
        cp.execFile(pythonPath, args, { cwd: workspaceFolder });
        return;
    }

    // Show in terminal (terminal.sendText is safe - no shell injection risk)
    const terminal = vscode.window.createTerminal({
        name: `Empathy: ${title}`,
        cwd: workspaceFolder,
    });
    terminal.show();
    terminal.sendText(`${pythonPath} -m empathy_os.cli ${command}`);
}

async function runEmpathyCommandSilent(command: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

        if (!workspaceFolder) {
            reject(new Error('No workspace folder open'));
            return;
        }

        // Build arguments as array for safe execution (no shell interpolation)
        const args = ['-m', 'empathy_os.cli', ...command.split(/\s+/)];

        // Use execFile with array arguments to prevent command injection
        cp.execFile(pythonPath, args, { cwd: workspaceFolder }, (error, stdout, stderr) => {
            if (error) {
                reject(error);
            } else {
                resolve(stdout);
            }
        });
    });
}

async function runEmpathyCommandWithProgress(command: string, message: string): Promise<void> {
    return vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: `Empathy: ${message}`,
            cancellable: false,
        },
        async () => {
            await runEmpathyCommandSilent(command);
        }
    );
}

// ============================================================================
// Feature E: Auto-Scan on Save
// ============================================================================

function setupAutoScanOnSave(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration('empathy');
    const autoScanEnabled = config.get<boolean>('autoScanOnSave', false);

    if (!autoScanEnabled) {
        return;
    }

    // Watch for Python file saves
    fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.py');

    // Debounce mechanism
    let scanTimeout: NodeJS.Timeout | undefined;

    const debouncedScan = () => {
        if (scanTimeout) {
            clearTimeout(scanTimeout);
        }
        scanTimeout = setTimeout(async () => {
            try {
                await runEmpathyCommandSilent('ship --quick --silent');
                healthProvider.refresh();
                healthProvider.updateDiagnostics();
            } catch {
                // Ignore errors in background scan
            }
        }, 2000); // Wait 2 seconds after last save
    };

    fileWatcher.onDidChange(debouncedScan);
    fileWatcher.onDidCreate(debouncedScan);

    context.subscriptions.push(fileWatcher);
}

/**
 * Set up file watcher for security findings
 * Refreshes diagnostics when security_findings.json changes
 */
function setupSecurityFindingsWatcher(context: vscode.ExtensionContext): void {
    // Watch for changes to security_findings.json
    securityFindingsWatcher = vscode.workspace.createFileSystemWatcher('**/.empathy/security_findings.json');

    securityFindingsWatcher.onDidChange(() => {
        healthProvider.updateSecurityDiagnostics();
    });

    securityFindingsWatcher.onDidCreate(() => {
        healthProvider.updateSecurityDiagnostics();
    });

    securityFindingsWatcher.onDidDelete(() => {
        // Clear security diagnostics when file is deleted
        securityDiagnosticCollection.clear();
    });

    context.subscriptions.push(securityFindingsWatcher);
}

// ============================================================================
// Status Bar
// ============================================================================

interface StatusData {
    patterns: number;
    health: string;
    savings: number;
}

async function getStatusData(): Promise<StatusData | null> {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        return null;
    }

    const config = vscode.workspace.getConfiguration('empathy');
    const patternsDir = path.join(
        workspaceFolder,
        config.get<string>('patternsDir', './patterns')
    );
    const empathyDir = path.join(
        workspaceFolder,
        config.get<string>('empathyDir', '.empathy')
    );

    let patterns = 0;
    let savings = 0;

    // Count patterns
    try {
        const debuggingFile = path.join(patternsDir, 'debugging.json');
        if (fs.existsSync(debuggingFile)) {
            const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
            patterns = data.patterns?.length || 0;
        }
    } catch {
        // Ignore errors
    }

    // Get cost savings
    try {
        const costsFile = path.join(empathyDir, 'costs.json');
        if (fs.existsSync(costsFile)) {
            const data = JSON.parse(fs.readFileSync(costsFile, 'utf8'));
            // Sum up daily savings
            for (const daily of Object.values(data.daily_totals || {})) {
                savings += (daily as any).savings || 0;
            }
        }
    } catch {
        // Ignore errors
    }

    return {
        patterns,
        health: patterns > 0 ? 'OK' : 'Setup needed',
        savings,
    };
}

async function updateStatusBar(): Promise<void> {
    const config = vscode.workspace.getConfiguration('empathy');
    const showStatusBar = config.get<boolean>('showStatusBar', true);

    if (!showStatusBar) {
        statusBarItem.hide();
        // Also hide quick action items
        for (const item of quickActionItems) {
            item.hide();
        }
        return;
    }

    const data = await getStatusData();
    if (!data) {
        statusBarItem.text = '$(pulse) Empathy';
        statusBarItem.tooltip = 'No workspace open';
        // Hide quick actions when no workspace
        for (const item of quickActionItems) {
            item.hide();
        }
    } else if (data.patterns === 0) {
        statusBarItem.text = '$(pulse) Empathy: Setup';
        statusBarItem.tooltip = 'Run "empathy learn" to get started';
        // Show quick actions even during setup
        for (const item of quickActionItems) {
            item.show();
        }
    } else {
        statusBarItem.text = `$(pulse) ${data.patterns} patterns | $${data.savings.toFixed(2)} saved`;
        statusBarItem.tooltip = `Empathy Framework\nPatterns: ${data.patterns}\nSavings: $${data.savings.toFixed(2)}`;
        // Show quick action items
        for (const item of quickActionItems) {
            item.show();
        }
    }
    statusBarItem.show();
}

function startAutoRefresh(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration('empathy');
    const autoRefresh = config.get<boolean>('autoRefresh', true);
    const interval = config.get<number>('refreshInterval', 300) * 1000;

    if (autoRefresh && interval > 0) {
        refreshTimer = setInterval(() => {
            updateStatusBar();
            healthProvider.refresh();
        }, interval);
    }
}

// ============================================================================
// Health Provider (for diagnostics)
// ============================================================================

class HealthTreeProvider implements vscode.TreeDataProvider<HealthItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<HealthItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private cachedHealth: HealthData | null = null;
    private diagnosticCollection: vscode.DiagnosticCollection;
    private securityDiagnosticCollection: vscode.DiagnosticCollection;

    constructor(diagnosticCollection: vscode.DiagnosticCollection, securityDiagnosticCollection: vscode.DiagnosticCollection) {
        this.diagnosticCollection = diagnosticCollection;
        this.securityDiagnosticCollection = securityDiagnosticCollection;
    }

    refresh(): void {
        this.cachedHealth = null;
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: HealthItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: HealthItem): Promise<HealthItem[]> {
        // If this is a child element, return its details
        if (element && element.children) {
            return element.children;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return [new HealthItem('No workspace', 'Open a folder to inspect', 'unknown')];
        }

        // Get health data from files or cache
        const health = await this.getHealthData(workspaceFolder);

        const items: HealthItem[] = [];

        // Overall Health Score - clickable to run scan
        const scoreIcon = health.score >= 80 ? 'ok' : health.score >= 50 ? 'warning' : 'error';
        const scoreItem = new HealthItem(
            'Health Score',
            `${health.score}%`,
            scoreIcon,
            undefined,
            'Overall code health score - click to scan'
        );
        scoreItem.command = { command: 'empathy.runScan', title: 'Run Scan' };
        scoreItem.contextValue = 'healthScore';
        items.push(scoreItem);

        // Patterns Learned
        const patternsItem = new HealthItem(
            'Patterns Learned',
            `${health.patterns} bugs tracked`,
            health.patterns > 0 ? 'ok' : 'unknown',
            undefined,
            'Bug patterns learned from git history'
        );
        patternsItem.command = { command: 'empathy.learn', title: 'Learn Patterns' };
        patternsItem.contextValue = 'patterns';
        items.push(patternsItem);

        // Lint Issues - with fix action
        const lintStatus = health.lint.errors === 0 ? 'ok' : health.lint.errors > 10 ? 'error' : 'warning';
        const lintItem = new HealthItem(
            'Lint',
            `${health.lint.errors} errors, ${health.lint.warnings} warnings`,
            lintStatus,
            [
                new HealthItem('Errors', health.lint.errors.toString(), health.lint.errors === 0 ? 'ok' : 'error'),
                new HealthItem('Warnings', health.lint.warnings.toString(), health.lint.warnings === 0 ? 'ok' : 'warning'),
            ],
            'Linting issues from ruff/pylint - click to fix'
        );
        lintItem.command = { command: 'empathy.fixLint', title: 'Fix Lint' };
        lintItem.contextValue = 'lint';
        items.push(lintItem);

        // Type Checking
        const typeStatus = health.types.errors === 0 ? 'ok' : 'error';
        const typesItem = new HealthItem(
            'Types',
            health.types.errors === 0 ? 'All types valid' : `${health.types.errors} type errors`,
            typeStatus,
            undefined,
            'MyPy type checking results'
        );
        typesItem.contextValue = 'types';
        items.push(typesItem);

        // Security
        const secStatus = health.security.high === 0 && health.security.medium === 0 ? 'ok' :
                         health.security.high > 0 ? 'error' : 'warning';
        const secItem = new HealthItem(
            'Security',
            `${health.security.high} high, ${health.security.medium} medium`,
            secStatus,
            [
                new HealthItem('High Severity', health.security.high.toString(), health.security.high === 0 ? 'ok' : 'error'),
                new HealthItem('Medium Severity', health.security.medium.toString(), health.security.medium === 0 ? 'ok' : 'warning'),
                new HealthItem('Low Severity', health.security.low.toString(), 'ok'),
            ],
            'Security vulnerabilities from bandit'
        );
        secItem.contextValue = 'security';
        items.push(secItem);

        // Tests - with run action
        const testStatus = health.tests.failed === 0 ? 'ok' : 'error';
        const testItem = new HealthItem(
            'Tests',
            `${health.tests.passed}/${health.tests.total} passing`,
            testStatus,
            [
                new HealthItem('Passed', health.tests.passed.toString(), 'ok'),
                new HealthItem('Failed', health.tests.failed.toString(), health.tests.failed === 0 ? 'ok' : 'error'),
                new HealthItem('Coverage', `${health.tests.coverage}%`, health.tests.coverage >= 70 ? 'ok' : 'warning'),
            ],
            'Test suite status and coverage - click to run'
        );
        testItem.command = { command: 'empathy.runTests', title: 'Run Tests' };
        testItem.contextValue = 'tests';
        items.push(testItem);

        // Tech Debt
        const debtStatus = health.techDebt.total < 50 ? 'ok' : health.techDebt.total < 200 ? 'warning' : 'error';
        const debtItem = new HealthItem(
            'Tech Debt',
            `${health.techDebt.total} items`,
            debtStatus,
            [
                new HealthItem('TODOs', health.techDebt.todos.toString(), 'info'),
                new HealthItem('FIXMEs', health.techDebt.fixmes.toString(), health.techDebt.fixmes === 0 ? 'ok' : 'warning'),
                new HealthItem('HACKs', health.techDebt.hacks.toString(), health.techDebt.hacks === 0 ? 'ok' : 'error'),
            ],
            'Technical debt from code annotations'
        );
        debtItem.contextValue = 'techDebt';
        items.push(debtItem);

        // Last Updated - with refresh action
        const lastScanItem = new HealthItem(
            'Last Scan',
            health.lastUpdated || 'Never',
            'info',
            undefined,
            'Click to refresh'
        );
        lastScanItem.command = { command: 'empathy.refreshHealth', title: 'Refresh' };
        lastScanItem.contextValue = 'lastScan';
        items.push(lastScanItem);

        return items;
    }

    // Feature F: Update Problem Panel diagnostics
    async updateDiagnostics(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        this.diagnosticCollection.clear();

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(
            workspaceFolder,
            config.get<string>('empathyDir', '.empathy')
        );

        // Read issues from inspection results
        try {
            const issuesFile = path.join(empathyDir, 'issues.json');
            if (!fs.existsSync(issuesFile)) {
                return;
            }

            const data = JSON.parse(fs.readFileSync(issuesFile, 'utf8'));
            const diagnosticsMap = new Map<string, vscode.Diagnostic[]>();

            for (const issue of data.issues || []) {
                const filePath = issue.file || '';
                const line = (issue.line || 1) - 1;
                const message = issue.message || 'Unknown issue';
                const severity = this.getSeverity(issue.severity || 'warning');

                const range = new vscode.Range(line, 0, line, 1000);
                const diagnostic = new vscode.Diagnostic(range, message, severity);
                diagnostic.source = 'Empathy';
                diagnostic.code = issue.rule || issue.type || 'empathy';

                const fullPath = path.isAbsolute(filePath)
                    ? filePath
                    : path.join(workspaceFolder, filePath);

                if (!diagnosticsMap.has(fullPath)) {
                    diagnosticsMap.set(fullPath, []);
                }
                diagnosticsMap.get(fullPath)!.push(diagnostic);
            }

            // Apply diagnostics
            for (const [file, diagnostics] of diagnosticsMap) {
                const uri = vscode.Uri.file(file);
                this.diagnosticCollection.set(uri, diagnostics);
            }
        } catch {
            // Ignore errors reading issues file
        }
    }

    private getSeverity(level: string): vscode.DiagnosticSeverity {
        switch (level.toLowerCase()) {
            case 'error':
            case 'high':
            case 'critical':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
            case 'medium':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
            case 'low':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Hint;
        }
    }

    /**
     * Update security diagnostics from security_findings.json
     * Shows security scan findings as squiggles in the editor
     */
    async updateSecurityDiagnostics(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        this.securityDiagnosticCollection.clear();

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(
            workspaceFolder,
            config.get<string>('empathyDir', '.empathy')
        );

        try {
            const findingsFile = path.join(empathyDir, 'security_findings.json');
            if (!fs.existsSync(findingsFile)) {
                return;
            }

            const data = JSON.parse(fs.readFileSync(findingsFile, 'utf8'));
            const diagnosticsMap = new Map<string, vscode.Diagnostic[]>();

            // Only process needs_review findings (excludes false positives and accepted risks)
            const findings = data.needs_review || [];

            for (const finding of findings) {
                const filePath = finding.file || '';
                const line = (finding.line || 1) - 1;
                const severity = this.getSeverity(finding.severity || 'warning');

                // Rich message with OWASP category and analysis
                const owasp = finding.owasp || 'Security Issue';
                const findingType = finding.type || 'unknown';
                const analysis = finding.analysis || `Potential ${findingType} vulnerability`;
                const message = `[${owasp}] ${findingType}: ${analysis}`;

                const range = new vscode.Range(line, 0, line, 1000);
                const diagnostic = new vscode.Diagnostic(range, message, severity);
                diagnostic.source = 'Empathy Security';
                diagnostic.code = findingType;

                // Add code snippet as related information if available
                if (finding.match) {
                    diagnostic.relatedInformation = [
                        new vscode.DiagnosticRelatedInformation(
                            new vscode.Location(
                                vscode.Uri.file(filePath),
                                range
                            ),
                            `Match: ${finding.match.substring(0, 80)}${finding.match.length > 80 ? '...' : ''}`
                        )
                    ];
                }

                const fullPath = path.isAbsolute(filePath)
                    ? filePath
                    : path.join(workspaceFolder, filePath);

                if (!diagnosticsMap.has(fullPath)) {
                    diagnosticsMap.set(fullPath, []);
                }
                diagnosticsMap.get(fullPath)!.push(diagnostic);
            }

            // Apply diagnostics
            for (const [file, diagnostics] of diagnosticsMap) {
                const uri = vscode.Uri.file(file);
                this.securityDiagnosticCollection.set(uri, diagnostics);
            }
        } catch (err) {
            console.error('Failed to load security findings:', err);
        }
    }

    private async getHealthData(workspaceFolder: string): Promise<HealthData> {
        if (this.cachedHealth) {
            return this.cachedHealth;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(
            workspaceFolder,
            config.get<string>('empathyDir', '.empathy')
        );
        const patternsDir = path.join(
            workspaceFolder,
            config.get<string>('patternsDir', './patterns')
        );

        // Default health data
        const health: HealthData = {
            score: 0,
            patterns: 0,
            lint: { errors: 0, warnings: 0 },
            types: { errors: 0 },
            security: { high: 0, medium: 0, low: 0 },
            tests: { passed: 0, failed: 0, total: 0, coverage: 0 },
            techDebt: { total: 0, todos: 0, fixmes: 0, hacks: 0 },
            lastUpdated: null,
        };

        // Read patterns count
        try {
            const debuggingFile = path.join(patternsDir, 'debugging.json');
            if (fs.existsSync(debuggingFile)) {
                const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
                health.patterns = data.patterns?.length || 0;
            }
        } catch { /* ignore */ }

        // Read health.json if exists (from empathy-inspect or ship)
        try {
            const healthFile = path.join(empathyDir, 'health.json');
            if (fs.existsSync(healthFile)) {
                const data = JSON.parse(fs.readFileSync(healthFile, 'utf8'));
                health.score = data.score || 0;
                health.lint = data.lint || health.lint;
                health.types = data.types || health.types;
                health.security = data.security || health.security;
                health.tests = data.tests || health.tests;
                health.techDebt = data.tech_debt || health.techDebt;
                health.lastUpdated = data.timestamp ? new Date(data.timestamp).toLocaleString() : null;
            }
        } catch { /* ignore */ }

        // Read tech debt from patterns if available
        try {
            const debtFile = path.join(patternsDir, 'tech_debt.json');
            if (fs.existsSync(debtFile)) {
                const data = JSON.parse(fs.readFileSync(debtFile, 'utf8'));
                if (data.snapshots && data.snapshots.length > 0) {
                    const latest = data.snapshots[data.snapshots.length - 1];
                    health.techDebt.total = latest.total_items || 0;
                    if (latest.by_type) {
                        health.techDebt.todos = latest.by_type.todo || 0;
                        health.techDebt.fixmes = latest.by_type.fixme || 0;
                        health.techDebt.hacks = latest.by_type.hack || 0;
                    }
                }
            }
        } catch { /* ignore */ }

        // Calculate score if not set
        if (health.score === 0) {
            let score = 100;
            score -= health.lint.errors * 2;
            score -= health.lint.warnings * 0.5;
            score -= health.types.errors * 3;
            score -= health.security.high * 10;
            score -= health.security.medium * 5;
            score -= health.tests.failed * 5;
            score -= Math.max(0, 70 - health.tests.coverage);
            health.score = Math.max(0, Math.min(100, Math.round(score)));
        }

        this.cachedHealth = health;
        return health;
    }
}

interface HealthData {
    score: number;
    patterns: number;
    lint: { errors: number; warnings: number };
    types: { errors: number };
    security: { high: number; medium: number; low: number };
    tests: { passed: number; failed: number; total: number; coverage: number };
    techDebt: { total: number; todos: number; fixmes: number; hacks: number };
    lastUpdated: string | null;
}

class HealthItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        public readonly status: string,
        public readonly children?: HealthItem[],
        public readonly fullTooltip?: string
    ) {
        super(
            label,
            children ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None
        );
        this.description = value;
        this.tooltip = fullTooltip || `${label}: ${value}`;

        // Set icon based on status
        switch (status) {
            case 'ok':
                this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
                break;
            case 'warning':
                this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('editorWarning.foreground'));
                break;
            case 'error':
                this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
                break;
            case 'info':
                this.iconPath = new vscode.ThemeIcon('info');
                break;
            default:
                this.iconPath = new vscode.ThemeIcon('question');
        }
    }
}

// ============================================================================
// Welcome Message
// ============================================================================

function showWelcomeIfNeeded(context: vscode.ExtensionContext): void {
    const hasShownWelcome = context.globalState.get<boolean>('hasShownWelcome');
    const isInitialized = context.globalState.get<boolean>('empathy.initialized');

    if (!hasShownWelcome) {
        // First-time users get the initialize option prominently
        if (!isInitialized) {
            vscode.window
                .showInformationMessage(
                    'Welcome to Empathy Framework! Set up your project to get started.',
                    'Initialize Project',
                    'Later'
                )
                .then((selection) => {
                    if (selection === 'Initialize Project') {
                        initializeProject(context);
                    }
                });
        } else {
            vscode.window
                .showInformationMessage(
                    'Empathy Framework extension activated! Run "empathy morning" to get started.',
                    'Open Command Palette',
                    'Dismiss'
                )
                .then((selection) => {
                    if (selection === 'Open Command Palette') {
                        vscode.commands.executeCommand(
                            'workbench.action.showCommands',
                            'Empathy'
                        );
                    }
                });
        }
        context.globalState.update('hasShownWelcome', true);
    }
}

// ============================================================================
// WebView HTML Helpers for Quick Workflow Command
// ============================================================================

function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getLoadingHtml(displayName: string, targetPath: string): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${displayName} Report</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            margin: 0;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
        }
        .container { text-align: center; max-width: 500px; }
        h1 { color: var(--vscode-foreground); margin-bottom: 8px; font-size: 24px; }
        .target { color: var(--vscode-descriptionForeground); font-size: 14px; margin-bottom: 40px; }
        .spinner {
            width: 60px; height: 60px;
            border: 4px solid var(--vscode-input-border);
            border-top-color: var(--vscode-button-background);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 40px auto;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .status { margin-top: 24px; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>${displayName} Report</h1>
        <div class="target">Target: ${escapeHtml(targetPath)}</div>
        <div class="spinner"></div>
        <div class="status">Generating report...</div>
    </div>
</body>
</html>`;
}

function getReportHtml(displayName: string, targetPath: string, timestamp: string, output: string, errorMessage: string | null, _workflowName?: string): string {
    const isError = errorMessage !== null;
    const statusColor = isError ? 'var(--vscode-errorForeground)' : 'var(--vscode-testing-iconPassed)';
    const statusText = isError ? 'Error' : 'Complete';
    const statusIcon = isError ? '✗' : '✓';
    const statusBg = isError ? 'rgba(241, 76, 76, 0.15)' : 'rgba(115, 201, 145, 0.15)';

    // Simple markdown-like rendering for headers and code blocks
    const formattedOutput = formatMarkdown(output);

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${displayName} Report</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            margin: 0;
            padding: 24px;
            line-height: 1.6;
        }
        .header {
            border-bottom: 1px solid var(--vscode-input-border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        h1 {
            color: var(--vscode-foreground);
            margin: 0;
            font-size: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .actions {
            display: flex;
            gap: 8px;
        }
        .action-btn {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .action-btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        .action-btn.primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        .action-btn.primary:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            background: ${statusBg};
            color: ${statusColor};
        }
        .meta {
            display: flex;
            gap: 24px;
            font-size: 13px;
            color: var(--vscode-descriptionForeground);
        }
        .content {
            font-family: var(--vscode-editor-font-family);
            font-size: 13px;
        }
        .content h2 {
            color: var(--vscode-foreground);
            border-bottom: 1px solid var(--vscode-input-border);
            padding-bottom: 8px;
            margin-top: 24px;
        }
        .content h3 {
            color: var(--vscode-foreground);
            margin-top: 20px;
        }
        .content pre {
            background: var(--vscode-textCodeBlock-background);
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .content code {
            background: var(--vscode-textCodeBlock-background);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: var(--vscode-editor-font-family);
        }
        .content ul, .content ol {
            padding-left: 24px;
        }
        .content li {
            margin: 4px 0;
        }
        .error-box {
            background: rgba(241, 76, 76, 0.1);
            border: 1px solid var(--vscode-errorForeground);
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .error-title {
            color: var(--vscode-errorForeground);
            font-weight: 600;
            margin-bottom: 8px;
        }
        .footer {
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid var(--vscode-input-border);
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-top">
            <h1>
                ${displayName} Report
                <span class="status-badge">${statusIcon} ${statusText}</span>
            </h1>
            <div class="actions">
                <button class="action-btn" onclick="copyReport()">📋 Copy</button>
                <button class="action-btn primary" onclick="runAgain()">🔄 Run Again</button>
            </div>
        </div>
        <div class="meta">
            <span>Target: ${escapeHtml(targetPath)}</span>
            <span>Generated: ${timestamp}</span>
        </div>
    </div>
    ${isError ? `
    <div class="error-box">
        <div class="error-title">Error Details</div>
        <div>${escapeHtml(errorMessage)}</div>
    </div>
    ` : ''}
    <div class="content">${formattedOutput}</div>
    <div class="footer">Generated by Empathy Framework</div>
    <script>
        const vscode = acquireVsCodeApi();
        function copyReport() {
            vscode.postMessage({ command: 'copy' });
        }
        function runAgain() {
            vscode.postMessage({ command: 'runAgain' });
        }
    </script>
</body>
</html>`;
}

function formatMarkdown(text: string): string {
    // Escape HTML first
    let html = escapeHtml(text);

    // Code blocks (```...```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

    // Inline code (`...`)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Bold (**...**)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italic (*...*)
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Unordered lists (- item)
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // Line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';

    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[123]>)/g, '$1');
    html = html.replace(/(<\/h[123]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul>)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p>(<pre>)/g, '$1');
    html = html.replace(/(<\/pre>)<\/p>/g, '$1');

    return html;
}
