/**
 * Morning Briefing Panel - Styled Daily Report
 *
 * Displays the morning briefing in a beautifully formatted webview panel
 */

import * as vscode from 'vscode';

export class MorningBriefingPanel {
    public static currentPanel: MorningBriefingPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, briefingText: string) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Set the webview's initial html content
        this._panel.webview.html = this._getHtmlForWebview(briefingText);

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'runCommand':
                        await vscode.commands.executeCommand(`empathy.${message.command}`);
                        break;
                    case 'openDashboard':
                        await vscode.commands.executeCommand('empathy.dashboard');
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    public static createOrShow(extensionUri: vscode.Uri, briefingText: string) {
        const column = vscode.ViewColumn.One;

        // If we already have a panel, update and show it
        if (MorningBriefingPanel.currentPanel) {
            MorningBriefingPanel.currentPanel._panel.webview.html =
                MorningBriefingPanel.currentPanel._getHtmlForWebview(briefingText);
            MorningBriefingPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'morningBriefing',
            '☀️ Morning Briefing',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
            }
        );

        MorningBriefingPanel.currentPanel = new MorningBriefingPanel(panel, extensionUri, briefingText);
    }

    public dispose() {
        MorningBriefingPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _getHtmlForWebview(briefingText: string): string {
        const timestamp = new Date().toLocaleString();

        // Parse the briefing text to extract sections
        const sections = this._parseBriefing(briefingText);

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Briefing</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            padding: 32px;
            line-height: 1.6;
        }

        .header {
            text-align: center;
            margin-bottom: 48px;
            padding-bottom: 24px;
            border-bottom: 2px solid var(--vscode-panel-border);
        }

        .header h1 {
            font-size: 32px;
            font-weight: 300;
            margin-bottom: 12px;
            color: var(--vscode-foreground);
        }

        .header .date {
            font-size: 18px;
            color: var(--vscode-descriptionForeground);
            font-weight: 300;
        }

        .section {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
            color: var(--vscode-textLink-foreground);
            border-bottom: 1px solid var(--vscode-panel-border);
            padding-bottom: 8px;
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }

        .stat {
            text-align: center;
            padding: 16px;
            background: var(--vscode-editor-background);
            border-radius: 6px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: var(--vscode-foreground);
            margin-bottom: 4px;
        }

        .stat-label {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .check-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            background: var(--vscode-editor-background);
            border-radius: 4px;
        }

        .check-status {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }

        .check-status.ok {
            background: rgba(16, 185, 129, 0.2);
            color: var(--vscode-testing-iconPassed);
        }

        .check-status.warn {
            background: rgba(245, 158, 11, 0.2);
            color: var(--vscode-editorWarning-foreground);
        }

        .recent-patterns {
            list-style: none;
        }

        .recent-patterns li {
            padding: 8px 12px;
            margin-bottom: 6px;
            background: var(--vscode-editor-background);
            border-radius: 4px;
            font-size: 13px;
        }

        .recent-patterns li::before {
            content: "→";
            margin-right: 8px;
            color: var(--vscode-textLink-foreground);
        }

        .action-buttons {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        .btn {
            padding: 10px 20px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
        }

        .btn:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .btn.secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }

        .btn.secondary:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .suggestion {
            padding: 16px;
            background: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textLink-foreground);
            border-radius: 4px;
            margin-bottom: 12px;
        }

        .footer {
            text-align: center;
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid var(--vscode-panel-border);
            color: var(--vscode-descriptionForeground);
            font-size: 12px;
        }

        .emoji {
            font-size: 24px;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span class="emoji">☀️</span>Morning Briefing</h1>
        <div class="date">${sections.date || timestamp}</div>
    </div>

    ${sections.patterns ? `
    <div class="section">
        <div class="section-title">Patterns Learned</div>
        <div class="stat-grid">
            <div class="stat">
                <div class="stat-value">${sections.patterns.bugs || 0}</div>
                <div class="stat-label">Bug Patterns</div>
            </div>
            <div class="stat">
                <div class="stat-value">${sections.patterns.security || 0}</div>
                <div class="stat-label">Security Decisions</div>
            </div>
            <div class="stat">
                <div class="stat-value">${sections.patterns.newThisWeek || 0}</div>
                <div class="stat-label">New This Week</div>
            </div>
        </div>
        ${sections.patterns.recent && sections.patterns.recent.length > 0 ? `
        <div style="margin-top: 16px;">
            <div style="font-size: 12px; color: var(--vscode-descriptionForeground); margin-bottom: 8px;">Recent patterns:</div>
            <ul class="recent-patterns">
                ${sections.patterns.recent.map((p: string) => `<li>${p}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
    </div>
    ` : ''}

    ${sections.health ? `
    <div class="section">
        <div class="section-title">Quick Health Check</div>
        ${sections.health.items ? sections.health.items.map((item: any) => `
        <div class="check-item">
            <span>${item.name}</span>
            <span class="check-status ${item.status === 'OK' ? 'ok' : 'warn'}">${item.value}</span>
        </div>
        `).join('') : ''}
        ${sections.health.overall ? `
        <div style="margin-top: 16px; text-align: center; font-size: 14px;">
            <strong>Overall:</strong> ${sections.health.overall}
        </div>
        ` : ''}
    </div>
    ` : ''}

    ${sections.suggestions && sections.suggestions.length > 0 ? `
    <div class="section">
        <div class="section-title">Suggested Focus Today</div>
        ${sections.suggestions.map((suggestion: string, i: number) => `
        <div class="suggestion">
            <strong>${i + 1}.</strong> ${suggestion}
        </div>
        `).join('')}
    </div>
    ` : ''}

    <div class="action-buttons">
        <button class="btn" onclick="runCommand('ship')">🚀 Run Ship</button>
        <button class="btn secondary" onclick="runCommand('fixAll')">🔧 Fix All</button>
        <button class="btn secondary" onclick="openDashboard()">📊 Dashboard</button>
    </div>

    <div class="footer">
        Generated by Empathy Framework • ${timestamp}
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function runCommand(cmd) {
            vscode.postMessage({ type: 'runCommand', command: cmd });
        }

        function openDashboard() {
            vscode.postMessage({ type: 'openDashboard' });
        }
    </script>
</body>
</html>`;
    }

    private _parseBriefing(text: string): any {
        const sections: any = {};

        // Extract date
        const dateMatch = text.match(/(\w+,\s+\w+\s+\d+,\s+\d{4})/);
        if (dateMatch) {
            sections.date = dateMatch[1];
        }

        // Extract patterns
        const bugPatternsMatch = text.match(/Bug patterns:\s+(\d+)/);
        const securityMatch = text.match(/Security decisions:\s+(\d+)/);
        const newThisWeekMatch = text.match(/New this week:\s+(\d+)/);

        if (bugPatternsMatch || securityMatch || newThisWeekMatch) {
            sections.patterns = {
                bugs: bugPatternsMatch ? parseInt(bugPatternsMatch[1]) : 0,
                security: securityMatch ? parseInt(securityMatch[1]) : 0,
                newThisWeek: newThisWeekMatch ? parseInt(newThisWeekMatch[1]) : 0,
                recent: []
            };

            // Extract recent pattern bullets
            const recentSection = text.match(/New this week:[\s\S]*?(?=\n\n|\nTECH DEBT|$)/);
            if (recentSection) {
                const bullets = recentSection[0].match(/- .+/g);
                if (bullets) {
                    sections.patterns.recent = bullets.map((b: string) => b.replace(/^- /, ''));
                }
            }
        }

        // Extract health check
        const lintMatch = text.match(/Lint:\s+(\w+)/);
        const gitMatch = text.match(/Git:\s+(.+)/);
        const overallMatch = text.match(/Overall:\s+(.+)/);

        if (lintMatch || gitMatch) {
            sections.health = {
                items: [],
                overall: overallMatch ? overallMatch[1].trim() : null
            };

            if (lintMatch) {
                sections.health.items.push({
                    name: 'Lint',
                    value: lintMatch[1],
                    status: lintMatch[1].includes('OK') ? 'OK' : 'WARN'
                });
            }
            if (gitMatch) {
                sections.health.items.push({
                    name: 'Git',
                    value: gitMatch[1].trim(),
                    status: gitMatch[1].includes('uncommitted') ? 'WARN' : 'OK'
                });
            }
        }

        // Extract suggestions
        const suggestionsSection = text.match(/SUGGESTED FOCUS TODAY[\s\S]*?(?=\n\n={50}|$)/);
        if (suggestionsSection) {
            const bullets = suggestionsSection[0].match(/\d+\.\s+(.+)/g);
            if (bullets) {
                sections.suggestions = bullets.map(b => b.replace(/^\d+\.\s+/, ''));
            }
        }

        return sections;
    }
}
