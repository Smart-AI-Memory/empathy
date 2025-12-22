/**
 * Empathy Power Panel - Floating Command Panel
 *
 * A rich floating webview panel for power user commands with:
 * - Quick action buttons (Morning, Ship, Fix All, Learn)
 * - Real-time stats display
 * - Command history with re-run capability
 * - Live output streaming
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

export class PowerPanel {
    public static currentPanel: PowerPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _commandHistory: CommandHistoryItem[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'runCommand':
                        await this._runCommand(message.command, message.title);
                        break;
                    case 'rerun':
                        if (message.index !== undefined && this._commandHistory[message.index]) {
                            const cmd = this._commandHistory[message.index];
                            await this._runCommand(cmd.command, cmd.title);
                        }
                        break;
                    case 'refresh':
                        await this._updateStats();
                        break;
                    case 'openDashboard':
                        vscode.commands.executeCommand('empathy.dashboard');
                        break;
                }
            },
            null,
            this._disposables
        );

        // Auto-refresh stats every 30 seconds
        const refreshInterval = setInterval(() => this._updateStats(), 30000);
        this._disposables.push({ dispose: () => clearInterval(refreshInterval) });
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.ViewColumn.Beside;

        // If we already have a panel, show it
        if (PowerPanel.currentPanel) {
            PowerPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyPowerPanel',
            'Empathy Power Panel',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'webview'),
                ],
            }
        );

        PowerPanel.currentPanel = new PowerPanel(panel, extensionUri);
    }

    public dispose() {
        PowerPanel.currentPanel = undefined;

        // Clean up resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private async _runCommand(command: string, title: string) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            this._sendOutput('error', 'No workspace folder open');
            return;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const fullCommand = `${pythonPath} -m empathy_os.cli ${command}`;

        // Add to history
        this._commandHistory.unshift({
            command,
            title,
            timestamp: new Date().toISOString(),
            status: 'running',
        });

        // Limit history to 10 items
        if (this._commandHistory.length > 10) {
            this._commandHistory = this._commandHistory.slice(0, 10);
        }

        // Update UI
        this._sendHistory();
        this._sendOutput('info', `> Running ${title}...`);

        // Execute command
        const process = cp.spawn(pythonPath, ['-m', 'empathy_os.cli', ...command.split(' ')], {
            cwd: workspaceFolder,
            shell: true,
        });

        let output = '';

        process.stdout?.on('data', (data) => {
            output += data.toString();
            this._sendOutput('stdout', data.toString());
        });

        process.stderr?.on('data', (data) => {
            output += data.toString();
            this._sendOutput('stderr', data.toString());
        });

        process.on('close', (code) => {
            // Update history status
            if (this._commandHistory.length > 0) {
                this._commandHistory[0].status = code === 0 ? 'success' : 'failed';
                this._sendHistory();
            }

            if (code === 0) {
                this._sendOutput('success', `\n[Completed successfully]`);
            } else {
                this._sendOutput('error', `\n[Exited with code ${code}]`);
            }

            // Refresh stats after command completes
            this._updateStats();
        });
    }

    private _sendOutput(type: string, text: string) {
        this._panel.webview.postMessage({
            type: 'output',
            outputType: type,
            text,
        });
    }

    private _sendHistory() {
        this._panel.webview.postMessage({
            type: 'history',
            items: this._commandHistory,
        });
    }

    private async _updateStats() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const patternsDir = path.join(workspaceFolder, config.get<string>('patternsDir', './patterns'));
        const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

        const stats = {
            patterns: 0,
            health: 0,
            savings: 0,
            savingsWeek: 0,
        };

        // Count patterns
        try {
            const debuggingFile = path.join(patternsDir, 'debugging.json');
            if (fs.existsSync(debuggingFile)) {
                const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
                stats.patterns = data.patterns?.length || 0;
            }
        } catch { /* ignore */ }

        // Get health score
        try {
            const healthFile = path.join(empathyDir, 'health.json');
            if (fs.existsSync(healthFile)) {
                const data = JSON.parse(fs.readFileSync(healthFile, 'utf8'));
                stats.health = data.score || 0;
            }
        } catch { /* ignore */ }

        // Get cost savings
        try {
            const costsFile = path.join(empathyDir, 'costs.json');
            if (fs.existsSync(costsFile)) {
                const data = JSON.parse(fs.readFileSync(costsFile, 'utf8'));
                const now = new Date();
                const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

                for (const [dateStr, daily] of Object.entries(data.daily_totals || {})) {
                    const date = new Date(dateStr);
                    stats.savings += (daily as any).savings || 0;
                    if (date >= weekAgo) {
                        stats.savingsWeek += (daily as any).savings || 0;
                    }
                }
            }
        } catch { /* ignore */ }

        this._panel.webview.postMessage({
            type: 'stats',
            stats,
        });
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.title = 'Empathy Power Panel';
        this._panel.webview.html = this._getHtmlForWebview(webview);
        this._updateStats();
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        // Get VS Code theme colors
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Empathy Power Panel</title>
    <style>
        :root {
            --bg: var(--vscode-editor-background);
            --fg: var(--vscode-editor-foreground);
            --border: var(--vscode-panel-border);
            --button-bg: var(--vscode-button-background);
            --button-fg: var(--vscode-button-foreground);
            --button-hover: var(--vscode-button-hoverBackground);
            --success: var(--vscode-testing-iconPassed);
            --error: var(--vscode-testing-iconFailed);
            --warning: var(--vscode-editorWarning-foreground);
            --info: var(--vscode-editorInfo-foreground);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--fg);
            background: var(--bg);
            padding: 16px;
            line-height: 1.4;
        }

        h2 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .section {
            margin-bottom: 20px;
        }

        /* Quick Actions Grid */
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }

        .action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 12px 8px;
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
            font-size: 12px;
        }

        .action-btn:hover {
            background: var(--button-bg);
            color: var(--button-fg);
            border-color: var(--button-bg);
        }

        .action-btn .icon {
            font-size: 20px;
            margin-bottom: 4px;
        }

        /* Stats Display */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }

        .stat-item {
            background: var(--vscode-input-background);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 8px 12px;
        }

        .stat-label {
            font-size: 11px;
            opacity: 0.7;
        }

        .stat-value {
            font-size: 16px;
            font-weight: 600;
        }

        .stat-value.success { color: var(--success); }
        .stat-value.warning { color: var(--warning); }
        .stat-value.error { color: var(--error); }

        /* History List */
        .history-list {
            max-height: 150px;
            overflow-y: auto;
        }

        .history-item {
            display: flex;
            align-items: center;
            padding: 6px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 4px;
            background: var(--vscode-input-background);
        }

        .history-item:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .history-status {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .history-status.success { background: var(--success); }
        .history-status.failed { background: var(--error); }
        .history-status.running { background: var(--warning); animation: pulse 1s infinite; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .history-title {
            flex: 1;
        }

        .history-time {
            opacity: 0.5;
            font-size: 10px;
            margin-right: 8px;
        }

        .history-rerun {
            background: none;
            border: none;
            color: var(--info);
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }

        .history-rerun:hover {
            background: var(--vscode-button-secondaryBackground);
        }

        /* Output Console */
        .output-console {
            background: var(--vscode-terminal-background);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 8px;
            font-family: var(--vscode-editor-font-family);
            font-size: 11px;
            line-height: 1.4;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .output-line { margin-bottom: 2px; }
        .output-line.info { color: var(--info); }
        .output-line.stdout { color: var(--fg); }
        .output-line.stderr { color: var(--warning); }
        .output-line.success { color: var(--success); }
        .output-line.error { color: var(--error); }

        .empty-state {
            text-align: center;
            padding: 20px;
            opacity: 0.5;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="section">
        <h2>Quick Actions</h2>
        <div class="actions-grid">
            <button class="action-btn" data-cmd="morning" data-title="Morning Briefing">
                <span class="icon">&#x2600;</span>
                Morning
            </button>
            <button class="action-btn" data-cmd="ship" data-title="Pre-Ship Check">
                <span class="icon">&#x1F680;</span>
                Ship
            </button>
            <button class="action-btn" data-cmd="fix-all" data-title="Fix All Issues">
                <span class="icon">&#x1F527;</span>
                Fix All
            </button>
            <button class="action-btn" data-cmd="learn --analyze 20" data-title="Learn Patterns">
                <span class="icon">&#x1F4DA;</span>
                Learn
            </button>
            <button class="action-btn" data-cmd="workflow list" data-title="List Workflows">
                <span class="icon">&#x25B6;</span>
                Workflows
            </button>
            <button class="action-btn" data-action="dashboard">
                <span class="icon">&#x1F4CA;</span>
                Dashboard
            </button>
        </div>
    </div>

    <div class="section">
        <h2>Quick Stats</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-label">Patterns</div>
                <div class="stat-value" id="stat-patterns">--</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Health</div>
                <div class="stat-value" id="stat-health">--</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Total Savings</div>
                <div class="stat-value success" id="stat-savings">--</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">This Week</div>
                <div class="stat-value success" id="stat-savings-week">--</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Recent Commands</h2>
        <div class="history-list" id="history-list">
            <div class="empty-state">No commands run yet</div>
        </div>
    </div>

    <div class="section">
        <h2>Output</h2>
        <div class="output-console" id="output-console">
            <div class="empty-state">Run a command to see output here</div>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();

        // Action button click handlers - CSP compliant
        document.querySelectorAll('.action-btn[data-cmd]').forEach(btn => {
            btn.addEventListener('click', function() {
                const cmd = this.dataset.cmd;
                const title = this.dataset.title;
                vscode.postMessage({ type: 'runCommand', command: cmd, title: title });
            });
        });

        // Dashboard button
        document.querySelectorAll('.action-btn[data-action="dashboard"]').forEach(btn => {
            btn.addEventListener('click', function() {
                vscode.postMessage({ type: 'openDashboard' });
            });
        });

        // Use event delegation for dynamically created rerun buttons
        document.getElementById('history-list').addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('history-rerun')) {
                const index = parseInt(e.target.dataset.index, 10);
                vscode.postMessage({ type: 'rerun', index: index });
            }
        });

        function refresh() {
            vscode.postMessage({ type: 'refresh' });
        }

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;

            switch (message.type) {
                case 'stats':
                    updateStats(message.stats);
                    break;
                case 'output':
                    appendOutput(message.outputType, message.text);
                    break;
                case 'history':
                    updateHistory(message.items);
                    break;
            }
        });

        function updateStats(stats) {
            document.getElementById('stat-patterns').textContent = stats.patterns + ' learned';

            const healthEl = document.getElementById('stat-health');
            healthEl.textContent = stats.health + '%';
            healthEl.className = 'stat-value ' + (stats.health >= 80 ? 'success' : stats.health >= 50 ? 'warning' : 'error');

            document.getElementById('stat-savings').textContent = '$' + stats.savings.toFixed(2);
            document.getElementById('stat-savings-week').textContent = '$' + stats.savingsWeek.toFixed(2);
        }

        function appendOutput(type, text) {
            const console = document.getElementById('output-console');

            // Clear empty state on first output
            if (console.querySelector('.empty-state')) {
                console.innerHTML = '';
            }

            const line = document.createElement('div');
            line.className = 'output-line ' + type;
            line.textContent = text;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
        }

        function updateHistory(items) {
            const list = document.getElementById('history-list');

            if (items.length === 0) {
                list.innerHTML = '<div class="empty-state">No commands run yet</div>';
                return;
            }

            list.innerHTML = items.map((item, index) => {
                const time = formatTime(item.timestamp);
                return \`
                    <div class="history-item">
                        <span class="history-status \${item.status}"></span>
                        <span class="history-title">\${item.title}</span>
                        <span class="history-time">\${time}</span>
                        <button class="history-rerun" data-index="\${index}">Rerun</button>
                    </div>
                \`;
            }).join('');
        }

        function formatTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = Math.floor((now - date) / 1000);

            if (diff < 60) return 'just now';
            if (diff < 3600) return Math.floor(diff / 60) + ' min ago';
            if (diff < 86400) return Math.floor(diff / 3600) + ' hr ago';
            return date.toLocaleDateString();
        }

        // Initial refresh
        refresh();
    </script>
</body>
</html>`;
    }
}

interface CommandHistoryItem {
    command: string;
    title: string;
    timestamp: string;
    status: 'running' | 'success' | 'failed';
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
