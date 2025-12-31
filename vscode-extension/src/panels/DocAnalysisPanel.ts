/**
 * Documentation Analysis Panel - Interactive Documentation Management
 *
 * An Editor Tab panel for managing documentation:
 * 1. Scout Phase - Automatically analyzes codebase for stale/missing docs
 * 2. Selection - User selects which items to document
 * 3. Generation - Creates documentation for selected items
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';

// =============================================================================
// Types
// =============================================================================

interface DocItem {
    id: string;
    file_path: string;
    issue_type: 'stale_doc' | 'missing_docstring' | 'no_documentation';
    severity: 'high' | 'medium' | 'low';
    priority: number;
    details: string;
    days_stale: number;
    loc: number;
    related_source: string[];
}

interface ScoutStats {
    items_found: number;
    stale_docs: number;
    missing_docs: number;
    scout_cost: number;
    duration_ms: number;
    excluded_count: number;
}

interface ExcludedFile {
    file_path: string;
    matched_pattern: string;
    reason: string;
}

interface ScoutResult {
    success: boolean;
    stats: ScoutStats;
    items: DocItem[];
    excluded: ExcludedFile[];
}

interface GenerationResult {
    success: boolean;
    generated: Array<{ file: string; export_path: string | null; cost: number }>;
    failed: Array<{ file: string; error: string }>;
    skipped: Array<{ file: string; reason: string }>;
    total_cost: number;
}

type PanelStage = 'scouting' | 'ready' | 'generating' | 'complete' | 'error';

// =============================================================================
// Utility Functions
// =============================================================================

function getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}

// =============================================================================
// DocAnalysisPanel Class
// =============================================================================

export class DocAnalysisPanel {
    public static currentPanel: DocAnalysisPanel | undefined;

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    private _stage: PanelStage = 'scouting';
    private _items: DocItem[] = [];
    private _selectedIds: Set<string> = new Set();
    private _stats: ScoutStats | null = null;
    private _excluded: ExcludedFile[] = [];
    private _error: string | null = null;
    private _generationProgress: { current: number; total: number; file: string } | null = null;
    private _generationResult: GenerationResult | null = null;

    /**
     * Create or reveal the Documentation Analysis panel
     */
    public static createOrShow(extensionUri: vscode.Uri): DocAnalysisPanel {
        const column = vscode.window.activeTextEditor?.viewColumn || vscode.ViewColumn.One;

        // If panel already exists, reveal it
        if (DocAnalysisPanel.currentPanel) {
            DocAnalysisPanel.currentPanel._panel.reveal(column);
            return DocAnalysisPanel.currentPanel;
        }

        // Create new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyDocAnalysis',
            'Documentation Analysis',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [extensionUri]
            }
        );

        DocAnalysisPanel.currentPanel = new DocAnalysisPanel(panel, extensionUri);
        return DocAnalysisPanel.currentPanel;
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Set initial HTML
        this._panel.webview.html = this._getHtmlForWebview();

        // Handle panel disposal
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from webview
        this._panel.webview.onDidReceiveMessage(
            message => this._handleMessage(message),
            null,
            this._disposables
        );

        // Auto-start scout when panel opens
        this._runScout();
    }

    public dispose() {
        DocAnalysisPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }

    // =========================================================================
    // Message Handling
    // =========================================================================

    private async _handleMessage(message: any) {
        console.log('[DocAnalysisPanel] Received message:', message.type);
        switch (message.type) {
            case 'toggleItem':
                this._toggleItem(message.id, message.selected);
                break;
            case 'selectAll':
                this._selectAll(message.category, message.selected);
                break;
            case 'generateSelected':
                console.log('[DocAnalysisPanel] Handling generateSelected message');
                await this._generateSelected();
                break;
            case 'retry':
                this._stage = 'scouting';
                this._error = null;
                this._updateWebview();
                await this._runScout();
                break;
            case 'reset':
                this._reset();
                break;
        }
    }

    private _toggleItem(id: string, selected: boolean) {
        if (selected) {
            this._selectedIds.add(id);
        } else {
            this._selectedIds.delete(id);
        }
        this._updateWebview();
    }

    private _selectAll(category: 'stale' | 'missing' | 'all', selected: boolean) {
        const targetType = category === 'stale' ? 'stale_doc' :
                          category === 'missing' ? 'missing_docstring' : null;

        this._items.forEach(item => {
            if (targetType === null || item.issue_type === targetType) {
                if (selected) {
                    this._selectedIds.add(item.id);
                } else {
                    this._selectedIds.delete(item.id);
                }
            }
        });
        this._updateWebview();
    }

    private _reset() {
        this._stage = 'scouting';
        this._items = [];
        this._selectedIds = new Set();
        this._stats = null;
        this._error = null;
        this._generationProgress = null;
        this._generationResult = null;
        this._updateWebview();
        this._runScout();
    }

    // =========================================================================
    // Scout Phase
    // =========================================================================

    private async _runScout() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            this._stage = 'error';
            this._error = 'No workspace folder open. Please open a folder to analyze.';
            this._updateWebview();
            return;
        }

        this._stage = 'scouting';
        this._updateWebview();

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        const args = [
            '-m', 'empathy_os.workflows.documentation_orchestrator',
            workspaceFolder,
            '--scout-json'
        ];

        cp.execFile(pythonPath, args, {
            cwd: workspaceFolder,
            maxBuffer: 5 * 1024 * 1024,
            timeout: 180000  // 3 minutes for scout
        }, (error, stdout, stderr) => {
            if (error) {
                this._stage = 'error';
                this._error = `Scout failed: ${error.message}\n${stderr}`;
                this._updateWebview();
                return;
            }

            try {
                const result: ScoutResult = JSON.parse(stdout);

                if (!result.success) {
                    this._stage = 'error';
                    this._error = 'Scout completed but reported failure.';
                    this._updateWebview();
                    return;
                }

                this._items = result.items;
                this._stats = result.stats;
                this._excluded = result.excluded || [];
                this._stage = 'ready';

                // Pre-select high severity items
                result.items.forEach(item => {
                    if (item.severity === 'high') {
                        this._selectedIds.add(item.id);
                    }
                });

                this._updateWebview();
            } catch (parseErr) {
                this._stage = 'error';
                this._error = `Failed to parse scout results: ${parseErr}`;
                this._updateWebview();
            }
        });
    }

    // =========================================================================
    // Generation Phase
    // =========================================================================

    private async _generateSelected() {
        console.log('[DocAnalysisPanel] _generateSelected called');
        console.log('[DocAnalysisPanel] selectedIds:', Array.from(this._selectedIds));
        console.log('[DocAnalysisPanel] items count:', this._items.length);

        if (this._selectedIds.size === 0) {
            vscode.window.showWarningMessage('No items selected for documentation.');
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder found.');
            return;
        }

        // Get selected file paths
        const selectedFiles = this._items
            .filter(item => this._selectedIds.has(item.id))
            .map(item => item.file_path);

        console.log('[DocAnalysisPanel] selectedFiles:', selectedFiles);

        if (selectedFiles.length === 0) {
            vscode.window.showWarningMessage('No files matched selection. Check item IDs.');
            return;
        }

        this._stage = 'generating';
        this._generationProgress = { current: 0, total: selectedFiles.length, file: '' };
        this._updateWebview();

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        const args = [
            '-m', 'empathy_os.workflows.documentation_orchestrator',
            workspaceFolder,
            '--generate-files', JSON.stringify(selectedFiles),
            '--auto'
        ];

        console.log('[DocAnalysisPanel] Running command:', pythonPath, args.join(' '));

        // Show progress notification in VS Code
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Generating documentation for ${selectedFiles.length} file(s)...`,
            cancellable: false
        }, async (progress) => {
            return new Promise<void>((resolve) => {
                cp.execFile(pythonPath, args, {
                    cwd: workspaceFolder,
                    maxBuffer: 10 * 1024 * 1024,
                    timeout: 600000  // 10 minutes for generation
                }, (error, stdout, stderr) => {
                    console.log('[DocAnalysisPanel] Command completed');
                    console.log('[DocAnalysisPanel] stdout:', stdout?.substring(0, 500));
                    console.log('[DocAnalysisPanel] stderr:', stderr?.substring(0, 500));

                    if (error) {
                        console.error('[DocAnalysisPanel] Error:', error);
                        this._stage = 'error';
                        this._error = `Generation failed: ${error.message}\n${stderr}`;
                        this._updateWebview();
                        resolve();
                        return;
                    }

                    try {
                        const result: GenerationResult = JSON.parse(stdout);
                        this._generationResult = result;
                        this._stage = 'complete';
                        this._updateWebview();

                        // Show summary notification
                        const generated = result.generated.length;
                        const failed = result.failed.length;
                        if (failed === 0) {
                            vscode.window.showInformationMessage(
                                `Documentation generated for ${generated} file(s).`
                            );
                        } else {
                            vscode.window.showWarningMessage(
                                `Generated ${generated}, failed ${failed}.`
                            );
                        }
                    } catch (parseErr) {
                        console.error('[DocAnalysisPanel] Parse error:', parseErr);
                        this._stage = 'error';
                        this._error = `Failed to parse generation results: ${parseErr}\n\nOutput: ${stdout?.substring(0, 1000)}`;
                        this._updateWebview();
                    }
                    resolve();
                });
            });
        });
    }

    // =========================================================================
    // Webview Updates
    // =========================================================================

    private _updateWebview() {
        this._panel.webview.postMessage({
            type: 'state',
            stage: this._stage,
            items: this._items,
            selectedIds: Array.from(this._selectedIds),
            stats: this._stats,
            excluded: this._excluded,
            error: this._error,
            generationProgress: this._generationProgress,
            generationResult: this._generationResult
        });
    }

    // =========================================================================
    // HTML Generation
    // =========================================================================

    private _getHtmlForWebview(): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Documentation Analysis</title>
    <style>
        :root {
            --bg-color: var(--vscode-editor-background);
            --text-color: var(--vscode-foreground);
            --border-color: var(--vscode-input-border);
            --hover-bg: var(--vscode-list-hoverBackground);
            --selected-bg: var(--vscode-list-activeSelectionBackground);
            --btn-bg: var(--vscode-button-background);
            --btn-fg: var(--vscode-button-foreground);
            --btn-hover: var(--vscode-button-hoverBackground);
            --badge-bg: var(--vscode-badge-background);
            --badge-fg: var(--vscode-badge-foreground);
            --error-fg: var(--vscode-errorForeground);
            --success-fg: var(--vscode-testing-iconPassed);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--text-color);
            background: var(--bg-color);
            padding: 16px;
            max-width: 900px;
            margin: 0 auto;
        }

        h1 {
            font-size: 1.4em;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stats-bar {
            display: flex;
            gap: 16px;
            padding: 12px;
            background: var(--vscode-input-background);
            border-radius: 6px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }

        .stat {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
        }

        .stat-label {
            font-size: 0.85em;
            color: var(--vscode-descriptionForeground);
        }

        .section {
            margin-bottom: 20px;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            background: var(--vscode-input-background);
            border-radius: 6px 6px 0 0;
            border: 1px solid var(--border-color);
            border-bottom: none;
            cursor: pointer;
        }

        .section-header:hover {
            background: var(--hover-bg);
        }

        .section-header label {
            font-weight: 600;
            flex: 1;
        }

        .section-count {
            background: var(--badge-bg);
            color: var(--badge-fg);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.85em;
        }

        .item-list {
            border: 1px solid var(--border-color);
            border-radius: 0 0 6px 6px;
            max-height: 300px;
            overflow-y: auto;
        }

        .doc-item {
            display: flex;
            align-items: center;
            padding: 10px 12px;
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            gap: 10px;
        }

        .doc-item:last-child {
            border-bottom: none;
        }

        .doc-item:hover {
            background: var(--hover-bg);
        }

        .doc-item.selected {
            background: var(--selected-bg);
        }

        .doc-item input[type="checkbox"] {
            width: 16px;
            height: 16px;
            cursor: pointer;
        }

        .item-content {
            flex: 1;
            min-width: 0;
        }

        .item-path {
            font-family: var(--vscode-editor-font-family);
            font-size: 0.95em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .item-meta {
            font-size: 0.85em;
            color: var(--vscode-descriptionForeground);
            margin-top: 2px;
        }

        .severity-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
            text-transform: uppercase;
        }

        .severity-badge.high {
            background: #dc262622;
            color: #ef4444;
        }

        .severity-badge.medium {
            background: #f59e0b22;
            color: #f59e0b;
        }

        .severity-badge.low {
            background: #22c55e22;
            color: #22c55e;
        }

        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            border-top: 1px solid var(--border-color);
            margin-top: 16px;
        }

        .selected-count {
            color: var(--vscode-descriptionForeground);
        }

        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.95em;
            transition: background 0.2s;
        }

        .btn-primary {
            background: var(--btn-bg);
            color: var(--btn-fg);
        }

        .btn-primary:hover:not(:disabled) {
            background: var(--btn-hover);
        }

        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .btn-secondary {
            background: transparent;
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }

        .btn-secondary:hover {
            background: var(--hover-bg);
        }

        /* Loading State */
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 20px;
            text-align: center;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid var(--border-color);
            border-top-color: var(--btn-bg);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Error State */
        .error-container {
            padding: 20px;
            background: #dc262615;
            border: 1px solid #dc2626;
            border-radius: 6px;
            text-align: center;
        }

        .error-message {
            color: var(--error-fg);
            margin-bottom: 16px;
            white-space: pre-wrap;
            text-align: left;
            font-family: var(--vscode-editor-font-family);
            font-size: 0.9em;
        }

        /* Complete State */
        .complete-container {
            padding: 20px;
        }

        .result-section {
            margin-bottom: 16px;
        }

        .result-section h3 {
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .result-list {
            list-style: none;
        }

        .result-list li {
            padding: 6px 0;
            font-family: var(--vscode-editor-font-family);
            font-size: 0.9em;
        }

        .result-list li.success {
            color: var(--success-fg);
        }

        .result-list li.failed {
            color: var(--error-fg);
        }

        .empty-state {
            padding: 40px 20px;
            text-align: center;
            color: var(--vscode-descriptionForeground);
        }

        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>
    <h1>
        <span>&#128218;</span>
        Documentation Analysis
    </h1>

    <!-- Scouting State -->
    <div id="scouting-view" class="loading-container">
        <div class="spinner"></div>
        <p>Analyzing codebase for documentation gaps...</p>
        <p style="color: var(--vscode-descriptionForeground); margin-top: 8px; font-size: 0.9em;">
            This may take a minute for large codebases
        </p>
    </div>

    <!-- Ready State -->
    <div id="ready-view" class="hidden">
        <div class="stats-bar" id="stats-bar">
            <!-- Stats populated by JS -->
        </div>

        <!-- Stale Docs Section -->
        <div class="section" id="stale-section">
            <div class="section-header" id="stale-header">
                <input type="checkbox" id="select-all-stale">
                <label>STALE DOCS</label>
                <span class="section-count" id="stale-count">0</span>
            </div>
            <div id="stale-list" class="item-list"></div>
        </div>

        <!-- Missing Docs Section -->
        <div class="section" id="missing-section">
            <div class="section-header" id="missing-header">
                <input type="checkbox" id="select-all-missing">
                <label>MISSING DOCS</label>
                <span class="section-count" id="missing-count">0</span>
            </div>
            <div id="missing-list" class="item-list"></div>
        </div>

        <!-- Excluded Files Section (collapsible) -->
        <div class="section" id="excluded-section" style="opacity: 0.7;">
            <div class="section-header" id="excluded-header" style="cursor: pointer;">
                <span style="font-size: 1.1em;">&#128683;</span>
                <label style="cursor: pointer;">EXCLUDED FROM SCAN</label>
                <span class="section-count" id="excluded-count">0</span>
                <span id="excluded-toggle" style="margin-left: auto; font-size: 0.8em;">&#9660; Show</span>
            </div>
            <div id="excluded-list" class="item-list hidden" style="max-height: 200px;"></div>
        </div>

        <div class="footer">
            <span class="selected-count">
                <span id="selected-count">0</span> selected
            </span>
            <div style="display: flex; gap: 8px;">
                <button class="btn btn-secondary" id="reset-btn">Reset</button>
                <button id="generate-btn" class="btn btn-primary" disabled>
                    Generate Selected
                </button>
            </div>
        </div>
    </div>

    <!-- Generating State -->
    <div id="generating-view" class="hidden loading-container">
        <div class="spinner"></div>
        <p style="font-weight: 600;">Generating documentation...</p>
        <p id="generation-progress" style="color: var(--vscode-descriptionForeground); margin-top: 8px;">
            Processing...
        </p>
        <p style="color: var(--vscode-descriptionForeground); margin-top: 16px; font-size: 0.85em; max-width: 400px; text-align: center;">
            This may take several minutes as documentation is generated using AI. Please wait...
        </p>
    </div>

    <!-- Complete State -->
    <div id="complete-view" class="hidden complete-container">
        <div class="result-section" id="generated-section">
            <h3>&#10004; Generated</h3>
            <ul class="result-list" id="generated-list"></ul>
        </div>

        <div class="result-section" id="failed-section">
            <h3>&#10060; Failed</h3>
            <ul class="result-list" id="failed-list"></ul>
        </div>

        <div class="result-section" id="skipped-section">
            <h3>&#9888; Skipped (Protected Files)</h3>
            <ul class="result-list" id="skipped-list"></ul>
        </div>

        <div class="footer">
            <span></span>
            <button class="btn btn-primary" id="new-analysis-btn">Run New Analysis</button>
        </div>
    </div>

    <!-- Error State -->
    <div id="error-view" class="hidden">
        <div class="error-container">
            <p class="error-message" id="error-message"></p>
            <button class="btn btn-primary" id="retry-btn">Retry</button>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();

        // State
        let currentStage = 'scouting';
        let items = [];
        let selectedIds = new Set();
        let stats = null;
        let excluded = [];

        // View elements
        const views = {
            scouting: document.getElementById('scouting-view'),
            ready: document.getElementById('ready-view'),
            generating: document.getElementById('generating-view'),
            complete: document.getElementById('complete-view'),
            error: document.getElementById('error-view')
        };

        // Handle state updates from extension
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'state') {
                currentStage = message.stage;
                items = message.items || [];
                selectedIds = new Set(message.selectedIds || []);
                stats = message.stats;
                excluded = message.excluded || [];

                updateView();

                if (message.stage === 'ready') {
                    renderItems();
                    renderExcluded();
                } else if (message.stage === 'generating' && message.generationProgress) {
                    updateGenerationProgress(message.generationProgress);
                } else if (message.stage === 'complete' && message.generationResult) {
                    renderResults(message.generationResult);
                } else if (message.stage === 'error' && message.error) {
                    document.getElementById('error-message').textContent = message.error;
                }
            }
        });

        function updateView() {
            // Hide all views
            Object.values(views).forEach(view => view.classList.add('hidden'));

            // Show current view
            if (views[currentStage]) {
                views[currentStage].classList.remove('hidden');
            }
        }

        function renderItems() {
            const staleItems = items.filter(i => i.issue_type === 'stale_doc');
            const missingItems = items.filter(i => i.issue_type !== 'stale_doc');

            // Update stats bar
            if (stats) {
                document.getElementById('stats-bar').innerHTML = \`
                    <div class="stat">
                        <span class="stat-value">\${stats.items_found}</span>
                        <span class="stat-label">Total Issues</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">\${stats.stale_docs}</span>
                        <span class="stat-label">Stale Docs</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">\${stats.missing_docs}</span>
                        <span class="stat-label">Missing Docs</span>
                    </div>
                \`;
            }

            // Render stale docs
            document.getElementById('stale-count').textContent = staleItems.length;
            document.getElementById('stale-section').classList.toggle('hidden', staleItems.length === 0);
            document.getElementById('stale-list').innerHTML = staleItems.length > 0
                ? staleItems.map(renderItem).join('')
                : '<div class="empty-state">No stale documentation found</div>';

            // Render missing docs
            document.getElementById('missing-count').textContent = missingItems.length;
            document.getElementById('missing-section').classList.toggle('hidden', missingItems.length === 0);
            document.getElementById('missing-list').innerHTML = missingItems.length > 0
                ? missingItems.map(renderItem).join('')
                : '<div class="empty-state">No missing documentation found</div>';

            // Update selection state
            updateSelectionUI();
        }

        function renderItem(item) {
            const isSelected = selectedIds.has(item.id);
            const isStale = item.issue_type === 'stale_doc';
            const meta = isStale
                ? \`Source changed \${item.days_stale} day\${item.days_stale !== 1 ? 's' : ''} ago\`
                : \`\${item.loc} LOC\`;

            return \`
                <div class="doc-item \${isSelected ? 'selected' : ''}" data-item-id="\${item.id}">
                    <input type="checkbox" \${isSelected ? 'checked' : ''} data-item-id="\${item.id}">
                    <div class="item-content">
                        <div class="item-path">\${item.file_path}</div>
                        <div class="item-meta">\${meta}\${item.details ? ' - ' + item.details : ''}</div>
                    </div>
                    <span class="severity-badge \${item.severity}">\${item.severity}</span>
                </div>
            \`;
        }

        function renderExcluded() {
            const excludedSection = document.getElementById('excluded-section');
            const excludedList = document.getElementById('excluded-list');
            const excludedCount = document.getElementById('excluded-count');

            if (excluded.length === 0) {
                excludedSection.classList.add('hidden');
                return;
            }

            excludedSection.classList.remove('hidden');
            excludedCount.textContent = excluded.length;
            excludedList.innerHTML = excluded.map(e => \`
                <div class="doc-item" style="cursor: default;">
                    <div class="item-content">
                        <div class="item-path">\${e.file_path}</div>
                        <div class="item-meta">\${e.reason} (pattern: \${e.matched_pattern})</div>
                    </div>
                </div>
            \`).join('');
        }

        function toggleExcludedList() {
            const excludedList = document.getElementById('excluded-list');
            const toggleText = document.getElementById('excluded-toggle');
            const isHidden = excludedList.classList.contains('hidden');

            if (isHidden) {
                excludedList.classList.remove('hidden');
                toggleText.innerHTML = '&#9650; Hide';
            } else {
                excludedList.classList.add('hidden');
                toggleText.innerHTML = '&#9660; Show';
            }
        }

        function toggleItem(id) {
            const isSelected = selectedIds.has(id);
            console.log('[Webview] toggleItem:', id, 'currently selected:', isSelected);
            vscode.postMessage({ type: 'toggleItem', id, selected: !isSelected });
        }

        // Event delegation for dynamically rendered items
        function handleItemClick(e) {
            const item = e.target.closest('.doc-item');
            if (item) {
                const id = item.dataset.itemId;
                if (id) {
                    toggleItem(id);
                }
            }
        }

        document.getElementById('stale-list').addEventListener('click', handleItemClick);
        document.getElementById('missing-list').addEventListener('click', handleItemClick);

        function toggleSelectAll(category) {
            const checkbox = document.getElementById(\`select-all-\${category}\`);
            const newState = !checkbox.checked;
            checkbox.checked = newState;
            vscode.postMessage({ type: 'selectAll', category, selected: newState });
        }

        function updateSelectionUI() {
            const count = selectedIds.size;
            document.getElementById('selected-count').textContent = count;
            document.getElementById('generate-btn').disabled = count === 0;

            // Update select-all checkboxes
            const staleItems = items.filter(i => i.issue_type === 'stale_doc');
            const missingItems = items.filter(i => i.issue_type !== 'stale_doc');

            const allStaleSelected = staleItems.length > 0 && staleItems.every(i => selectedIds.has(i.id));
            const allMissingSelected = missingItems.length > 0 && missingItems.every(i => selectedIds.has(i.id));

            document.getElementById('select-all-stale').checked = allStaleSelected;
            document.getElementById('select-all-missing').checked = allMissingSelected;

            // Re-render items to update visual selection state
            const staleList = document.getElementById('stale-list');
            const missingList = document.getElementById('missing-list');

            if (staleItems.length > 0) {
                staleList.innerHTML = staleItems.map(renderItem).join('');
            }
            if (missingItems.length > 0) {
                missingList.innerHTML = missingItems.map(renderItem).join('');
            }
        }

        function generateSelected() {
            console.log('[Webview] generateSelected clicked, selectedIds:', Array.from(selectedIds));
            vscode.postMessage({ type: 'generateSelected' });
        }

        function updateGenerationProgress(progress) {
            document.getElementById('generation-progress').textContent =
                \`Processing \${progress.current} of \${progress.total}...\`;
        }

        function renderResults(result) {
            // Generated files
            const generatedList = document.getElementById('generated-list');
            const generatedSection = document.getElementById('generated-section');
            if (result.generated && result.generated.length > 0) {
                generatedSection.classList.remove('hidden');
                generatedList.innerHTML = result.generated.map(g =>
                    \`<li class="success">+ \${g.file}\${g.export_path ? ' -> ' + g.export_path : ''}</li>\`
                ).join('');
            } else {
                generatedSection.classList.add('hidden');
            }

            // Failed files
            const failedList = document.getElementById('failed-list');
            const failedSection = document.getElementById('failed-section');
            if (result.failed && result.failed.length > 0) {
                failedSection.classList.remove('hidden');
                failedList.innerHTML = result.failed.map(f =>
                    \`<li class="failed">x \${f.file}: \${f.error}</li>\`
                ).join('');
            } else {
                failedSection.classList.add('hidden');
            }

            // Skipped files (protected from modification)
            const skippedList = document.getElementById('skipped-list');
            const skippedSection = document.getElementById('skipped-section');
            if (result.skipped && result.skipped.length > 0) {
                skippedSection.classList.remove('hidden');
                skippedList.innerHTML = result.skipped.map(s =>
                    \`<li style="color: var(--vscode-descriptionForeground);">~ \${s.file}: \${s.reason}</li>\`
                ).join('');
            } else {
                skippedSection.classList.add('hidden');
            }
        }

        function retry() {
            vscode.postMessage({ type: 'retry' });
        }

        function resetPanel() {
            vscode.postMessage({ type: 'reset' });
        }

        // Event listeners (CSP doesn't allow inline onclick handlers)
        document.getElementById('generate-btn').addEventListener('click', function() {
            console.log('[Webview] Generate button clicked');
            generateSelected();
        });

        document.getElementById('reset-btn').addEventListener('click', function() {
            console.log('[Webview] Reset button clicked');
            resetPanel();
        });

        document.getElementById('new-analysis-btn').addEventListener('click', function() {
            console.log('[Webview] New analysis button clicked');
            resetPanel();
        });

        document.getElementById('retry-btn').addEventListener('click', function() {
            console.log('[Webview] Retry button clicked');
            retry();
        });

        document.getElementById('stale-header').addEventListener('click', function() {
            console.log('[Webview] Stale header clicked');
            toggleSelectAll('stale');
        });

        document.getElementById('missing-header').addEventListener('click', function() {
            console.log('[Webview] Missing header clicked');
            toggleSelectAll('missing');
        });

        document.getElementById('excluded-header').addEventListener('click', function() {
            console.log('[Webview] Excluded header clicked');
            toggleExcludedList();
        });

        document.getElementById('select-all-stale').addEventListener('click', function(e) {
            e.stopPropagation();
        });

        document.getElementById('select-all-missing').addEventListener('click', function(e) {
            e.stopPropagation();
        });

        console.log('[Webview] Event listeners attached');
    </script>
</body>
</html>`;
    }
}
