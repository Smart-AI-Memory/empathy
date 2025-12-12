/**
 * Memory Panel Provider
 *
 * Webview provider for the Empathy Memory Control Panel.
 * Manages the webview lifecycle, handles messages from the UI,
 * and communicates with the backend API.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import {
    MemoryAPIService,
    Classification,
    MemoryStatus,
    MemoryStats,
    PatternSummary,
    HealthCheck
} from '../services/MemoryAPIService';

/**
 * Message types from webview to extension
 */
type WebviewMessage =
    | { type: 'refresh' }
    | { type: 'startRedis' }
    | { type: 'stopRedis' }
    | { type: 'listPatterns'; classification?: Classification }
    | { type: 'exportPatterns'; classification?: Classification }
    | { type: 'deletePattern'; patternId: string }
    | { type: 'healthCheck' }
    | { type: 'clearShortTerm' }
    | { type: 'ready' };

/**
 * Webview provider for Memory Control Panel
 */
export class MemoryPanelProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'empathyMemory.controlPanel';

    private _view?: vscode.WebviewView;
    private _apiService: MemoryAPIService;
    private _autoRefreshTimer?: NodeJS.Timeout;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _context: vscode.ExtensionContext
    ) {
        // Initialize API service with config
        const config = vscode.workspace.getConfiguration('empathyMemory');
        this._apiService = new MemoryAPIService({
            host: config.get<string>('apiHost') || 'localhost',
            port: config.get<number>('apiPort') || 8765,
            timeout: 10000
        });

        // Listen for config changes
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration('empathyMemory')) {
                this._updateAPIConfig();
                this._refreshPanel();
            }
        });
    }

    /**
     * Resolve webview view (called by VS Code)
     */
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ): void {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(this._extensionUri, 'webview'),
                vscode.Uri.joinPath(this._extensionUri, 'media')
            ]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(
            async (message: WebviewMessage) => {
                await this._handleMessage(message);
            }
        );

        // Handle panel visibility
        webviewView.onDidChangeVisibility(() => {
            if (webviewView.visible) {
                this._startAutoRefresh();
                this._refreshPanel();
            } else {
                this._stopAutoRefresh();
            }
        });

        // Handle disposal
        webviewView.onDidDispose(() => {
            this._stopAutoRefresh();
            this._view = undefined;
        });

        // Start auto-refresh if enabled
        if (webviewView.visible) {
            this._startAutoRefresh();
        }
    }

    /**
     * Handle messages from webview
     */
    private async _handleMessage(message: WebviewMessage): Promise<void> {
        try {
            switch (message.type) {
                case 'ready':
                    // Webview is ready, send initial data
                    await this._refreshPanel();
                    break;

                case 'refresh':
                    await this._refreshPanel();
                    break;

                case 'startRedis':
                    await this._startRedis();
                    break;

                case 'stopRedis':
                    await this._stopRedis();
                    break;

                case 'listPatterns':
                    await this._listPatterns(message.classification);
                    break;

                case 'exportPatterns':
                    await this._exportPatterns(message.classification);
                    break;

                case 'deletePattern':
                    await this._deletePattern(message.patternId);
                    break;

                case 'healthCheck':
                    await this._runHealthCheck();
                    break;

                case 'clearShortTerm':
                    await this._clearShortTerm();
                    break;
            }
        } catch (error) {
            this._showError(`Error: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Refresh panel data
     */
    private async _refreshPanel(): Promise<void> {
        try {
            const [status, stats] = await Promise.all([
                this._apiService.getStatus(),
                this._apiService.getStatistics()
            ]);

            this._postMessage({
                type: 'statusUpdate',
                status,
                stats
            });
        } catch (error) {
            // API might not be running - show connection error
            this._postMessage({
                type: 'connectionError',
                message: 'Cannot connect to Memory API. Make sure the backend is running on port 8765.'
            });
        }
    }

    /**
     * Start Redis
     */
    private async _startRedis(): Promise<void> {
        try {
            const result = await this._apiService.startRedis();
            if (result.success) {
                this._showInfo('Redis started successfully');
            } else {
                this._showWarning(result.message);
            }
            await this._refreshPanel();
        } catch (error) {
            this._showError(`Failed to start Redis: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Stop Redis
     */
    private async _stopRedis(): Promise<void> {
        try {
            const result = await this._apiService.stopRedis();
            if (result.success) {
                this._showInfo('Redis stopped');
            } else {
                this._showWarning(result.message);
            }
            await this._refreshPanel();
        } catch (error) {
            this._showError(`Failed to stop Redis: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * List patterns
     */
    private async _listPatterns(classification?: Classification): Promise<void> {
        try {
            const patterns = await this._apiService.listPatterns(classification);
            this._postMessage({
                type: 'patternsUpdate',
                patterns
            });
        } catch (error) {
            this._showError(`Failed to list patterns: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Export patterns
     */
    private async _exportPatterns(classification?: Classification): Promise<void> {
        try {
            const result = await this._apiService.exportPatterns(classification);

            // Prompt user for save location
            const uri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file('patterns_export.json'),
                filters: {
                    'JSON Files': ['json']
                }
            });

            if (uri) {
                const content = JSON.stringify(result.export_data, null, 2);
                await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
                this._showInfo(`Exported ${result.pattern_count} patterns to ${uri.fsPath}`);
            }
        } catch (error) {
            this._showError(`Failed to export patterns: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Delete pattern
     */
    private async _deletePattern(patternId: string): Promise<void> {
        const confirmed = await vscode.window.showWarningMessage(
            `Delete pattern ${patternId}?`,
            { modal: true },
            'Delete'
        );

        if (confirmed === 'Delete') {
            try {
                await this._apiService.deletePattern(patternId);
                this._showInfo(`Pattern ${patternId} deleted`);
                await this._refreshPanel();
            } catch (error) {
                this._showError(`Failed to delete pattern: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    }

    /**
     * Run health check
     */
    private async _runHealthCheck(): Promise<void> {
        try {
            const health = await this._apiService.healthCheck();
            this._postMessage({
                type: 'healthUpdate',
                health
            });

            // Show notification based on health status
            if (health.overall === 'healthy') {
                this._showInfo('System health: Healthy');
            } else if (health.overall === 'degraded') {
                this._showWarning('System health: Degraded - see panel for details');
            } else {
                this._showError('System health: Unhealthy - see panel for details');
            }
        } catch (error) {
            this._showError(`Health check failed: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Clear short-term memory
     */
    private async _clearShortTerm(): Promise<void> {
        const confirmed = await vscode.window.showWarningMessage(
            'Clear all short-term memory? This cannot be undone.',
            { modal: true },
            'Clear'
        );

        if (confirmed === 'Clear') {
            try {
                const result = await this._apiService.clearShortTerm();
                this._showInfo(`Cleared ${result.keys_deleted} keys from short-term memory`);
                await this._refreshPanel();
            } catch (error) {
                this._showError(`Failed to clear memory: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    }

    /**
     * Start auto-refresh timer
     */
    private _startAutoRefresh(): void {
        const config = vscode.workspace.getConfiguration('empathyMemory');
        if (!config.get<boolean>('autoRefresh')) {
            return;
        }

        const interval = config.get<number>('autoRefreshInterval') || 30;
        this._autoRefreshTimer = setInterval(() => {
            this._refreshPanel();
        }, interval * 1000);
    }

    /**
     * Stop auto-refresh timer
     */
    private _stopAutoRefresh(): void {
        if (this._autoRefreshTimer) {
            clearInterval(this._autoRefreshTimer);
            this._autoRefreshTimer = undefined;
        }
    }

    /**
     * Update API configuration
     */
    private _updateAPIConfig(): void {
        const config = vscode.workspace.getConfiguration('empathyMemory');
        this._apiService.updateConfig({
            host: config.get<string>('apiHost') || 'localhost',
            port: config.get<number>('apiPort') || 8765
        });
    }

    /**
     * Post message to webview
     */
    private _postMessage(message: any): void {
        this._view?.webview.postMessage(message);
    }

    /**
     * Show info notification
     */
    private _showInfo(message: string): void {
        const config = vscode.workspace.getConfiguration('empathyMemory');
        if (config.get<boolean>('showNotifications')) {
            vscode.window.showInformationMessage(`Empathy Memory: ${message}`);
        }
    }

    /**
     * Show warning notification
     */
    private _showWarning(message: string): void {
        const config = vscode.workspace.getConfiguration('empathyMemory');
        if (config.get<boolean>('showNotifications')) {
            vscode.window.showWarningMessage(`Empathy Memory: ${message}`);
        }
    }

    /**
     * Show error notification
     */
    private _showError(message: string): void {
        vscode.window.showErrorMessage(`Empathy Memory: ${message}`);
    }

    /**
     * Get HTML for webview
     */
    private _getHtmlForWebview(webview: vscode.Webview): string {
        // Load HTML template
        const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'index.html');
        const cssPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'styles.css');

        // Convert to webview URIs
        const cssUri = webview.asWebviewUri(cssPath);

        // Read HTML template
        let html = '';
        try {
            html = fs.readFileSync(htmlPath.fsPath, 'utf8');
            // Replace CSS placeholder
            html = html.replace('{{cssUri}}', cssUri.toString());
        } catch (error) {
            // Fallback HTML if template not found
            html = this._getFallbackHtml(cssUri.toString());
        }

        return html;
    }

    /**
     * Get fallback HTML (inline)
     */
    private _getFallbackHtml(cssUri: string): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="${cssUri}" rel="stylesheet">
    <title>Empathy Memory Panel</title>
</head>
<body>
    <div class="container">
        <h1>Empathy Memory Panel</h1>
        <p>Loading webview template...</p>
    </div>
</body>
</html>`;
    }

    /**
     * Public method to refresh from external commands
     */
    public refresh(): void {
        this._refreshPanel();
    }
}
