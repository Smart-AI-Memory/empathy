/**
 * GuidedPanelProvider - Rich webview panel for guided mode
 *
 * Provides an interactive panel for new users with:
 * - Summary of what just happened
 * - Detailed results/reports
 * - Embedded Socratic chat interface
 * - Next step action buttons
 * - Keyboard shortcut hints
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import { SocraticFormService, FormType, ChatMessage, ConversationState } from '../services/SocraticFormService';

/**
 * Panel state for persistence
 */
interface GuidedPanelState {
    conversationId: string;
    formType: FormType;
    summary?: string;
    results?: string;
    workflowName?: string;
}

/**
 * Message types from webview to extension
 */
type WebviewMessage =
    | { type: 'ready' }
    | { type: 'sendMessage'; text: string }
    | { type: 'selectOption'; option: string }
    | { type: 'runAction'; action: string }
    | { type: 'newConversation'; formType: FormType }
    | { type: 'clearChat' }
    | { type: 'copyResult' };

/**
 * GuidedPanelProvider - Creates and manages the guided mode webview
 */
export class GuidedPanelProvider {
    public static currentPanel: GuidedPanelProvider | undefined;
    private static readonly viewType = 'empathyGuidedPanel';

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private readonly _context: vscode.ExtensionContext;
    private readonly _socraticService: SocraticFormService;
    private _disposables: vscode.Disposable[] = [];
    private _state: GuidedPanelState;

    /**
     * Create or show the guided panel
     */
    public static createOrShow(
        extensionUri: vscode.Uri,
        context: vscode.ExtensionContext,
        options?: {
            formType?: FormType;
            summary?: string;
            results?: string;
            workflowName?: string;
        }
    ): GuidedPanelProvider {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If panel exists, reveal it
        if (GuidedPanelProvider.currentPanel) {
            GuidedPanelProvider.currentPanel._panel.reveal(column);
            if (options) {
                GuidedPanelProvider.currentPanel.updateContent(options);
            }
            return GuidedPanelProvider.currentPanel;
        }

        // Create new panel
        const panel = vscode.window.createWebviewPanel(
            GuidedPanelProvider.viewType,
            'Empathy Guide',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media'),
                    vscode.Uri.joinPath(extensionUri, 'webview'),
                ],
            }
        );

        GuidedPanelProvider.currentPanel = new GuidedPanelProvider(
            panel,
            extensionUri,
            context,
            options
        );

        return GuidedPanelProvider.currentPanel;
    }

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        context: vscode.ExtensionContext,
        options?: {
            formType?: FormType;
            summary?: string;
            results?: string;
            workflowName?: string;
        }
    ) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._context = context;
        this._socraticService = SocraticFormService.getInstance();
        this._socraticService.initialize(context);

        // Initialize state
        const conversationId = `guided-${Date.now()}`;
        this._state = {
            conversationId,
            formType: options?.formType || 'general',
            summary: options?.summary,
            results: options?.results,
            workflowName: options?.workflowName,
        };

        // Start conversation
        this._socraticService.startConversation(
            conversationId,
            this._state.formType,
            { workflowName: options?.workflowName }
        );

        // Set initial HTML
        this._panel.webview.html = this._getHtmlForWebview();

        // Handle messages from webview
        this._panel.webview.onDidReceiveMessage(
            async (message: WebviewMessage) => {
                await this._handleMessage(message);
            },
            null,
            this._disposables
        );

        // Handle panel disposal
        this._panel.onDidDispose(
            () => this.dispose(),
            null,
            this._disposables
        );
    }

    /**
     * Update panel content
     */
    public updateContent(options: {
        formType?: FormType;
        summary?: string;
        results?: string;
        workflowName?: string;
    }): void {
        if (options.summary !== undefined) this._state.summary = options.summary;
        if (options.results !== undefined) this._state.results = options.results;
        if (options.workflowName !== undefined) this._state.workflowName = options.workflowName;

        if (options.formType && options.formType !== this._state.formType) {
            // Start new conversation with new form type
            const newId = `guided-${Date.now()}`;
            this._state.conversationId = newId;
            this._state.formType = options.formType;
            this._socraticService.startConversation(newId, options.formType, {
                workflowName: this._state.workflowName,
            });
        }

        this._sendFullState();
    }

    /**
     * Handle messages from webview
     */
    private async _handleMessage(message: WebviewMessage): Promise<void> {
        console.log('[GuidedPanel] Received message:', message.type, message);
        switch (message.type) {
            case 'ready':
                console.log('[GuidedPanel] Webview ready, sending full state');
                this._sendFullState();
                break;

            case 'sendMessage':
                await this._handleUserMessage(message.text);
                break;

            case 'selectOption':
                await this._handleUserMessage(message.option);
                break;

            case 'runAction':
                await this._handleAction(message.action);
                break;

            case 'newConversation':
                this._startNewConversation(message.formType);
                break;

            case 'clearChat':
                this._clearChat();
                break;

            case 'copyResult':
                if (this._state.results) {
                    await vscode.env.clipboard.writeText(this._state.results);
                    vscode.window.showInformationMessage('Results copied to clipboard');
                }
                break;
        }
    }

    /**
     * Handle user message in chat
     */
    private async _handleUserMessage(text: string): Promise<void> {
        // Show typing indicator
        this._postMessage({ type: 'typing', isTyping: true });

        const response = await this._socraticService.sendMessage(
            this._state.conversationId,
            text
        );

        this._postMessage({ type: 'typing', isTyping: false });

        if (response) {
            this._postMessage({
                type: 'newMessage',
                message: response,
            });

            const state = this._socraticService.getConversation(this._state.conversationId);
            if (state?.isComplete) {
                this._postMessage({
                    type: 'conversationComplete',
                    result: state.result,
                });
            }
        }
    }

    /**
     * Handle action button click
     */
    private async _handleAction(action: string): Promise<void> {
        console.log('[GuidedPanel] Running action:', action);
        switch (action) {
            case 'ship':
                await vscode.commands.executeCommand('empathy.ship');
                break;
            case 'fixAll':
                await vscode.commands.executeCommand('empathy.fixAll');
                break;
            case 'dashboard':
                await vscode.commands.executeCommand('empathy.dashboard');
                break;
            case 'morning':
                await vscode.commands.executeCommand('empathy.morning');
                break;
            case 'runTests':
                await vscode.commands.executeCommand('empathy.runTests');
                break;
            case 'runWorkflow':
                await vscode.commands.executeCommand('empathy.runWorkflowQuick');
                break;
            case 'researchSynthesis':
                // Launch Research Synthesis workflow directly
                await vscode.commands.executeCommand('empathy.runWorkflow', 'research-synthesis');
                break;
            case 'agentFactory':
                // Launch Agent Factory (Socratic crew design flow)
                await vscode.commands.executeCommand('empathy.agentFactory');
                break;
            default:
                console.log(`[GuidedPanel] Unknown action: ${action}`);
        }
    }

    /**
     * Start a new conversation
     */
    private _startNewConversation(formType: FormType): void {
        const newId = `guided-${Date.now()}`;
        this._state.conversationId = newId;
        this._state.formType = formType;

        this._socraticService.startConversation(newId, formType, {
            workflowName: this._state.workflowName,
        });

        this._sendFullState();
    }

    /**
     * Clear current chat
     */
    private _clearChat(): void {
        this._socraticService.deleteConversation(this._state.conversationId);
        this._startNewConversation(this._state.formType);
    }

    /**
     * Send full state to webview
     */
    private _sendFullState(): void {
        const conversation = this._socraticService.getConversation(this._state.conversationId);

        this._postMessage({
            type: 'fullState',
            state: this._state,
            messages: conversation?.messages.filter(m => m.role !== 'system') || [],
            isComplete: conversation?.isComplete || false,
            result: conversation?.result,
        });
    }

    /**
     * Post message to webview
     */
    private _postMessage(message: any): void {
        this._panel.webview.postMessage(message);
    }

    /**
     * Get HTML for webview
     */
    private _getHtmlForWebview(): string {
        const webview = this._panel.webview;
        const nonce = this._getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Empathy Guide</title>
    <style>
        :root {
            --bg: var(--vscode-editor-background);
            --fg: var(--vscode-editor-foreground);
            --border: var(--vscode-input-border);
            --accent: var(--vscode-button-background);
            --accent-hover: var(--vscode-button-hoverBackground);
            --input-bg: var(--vscode-input-background);
            --card-bg: var(--vscode-editorWidget-background);
            --success: #4EC9B0;
            --info: #9CDCFE;
            --warning: #DCDCAA;
            --error: #F14C4C;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: var(--vscode-font-family);
            background: var(--bg);
            color: var(--fg);
            padding: 16px;
            line-height: 1.5;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 16px;
        }

        .header h1 {
            font-size: 20px;
            font-weight: 600;
        }

        .header-actions {
            display: flex;
            gap: 8px;
        }

        /* Cards */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .card-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--info);
        }

        .card-content {
            font-size: 13px;
        }

        .card-content pre {
            background: var(--input-bg);
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
        }

        /* Chat Container */
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 400px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }

        .message {
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
        }

        .message.user {
            align-items: flex-end;
        }

        .message.assistant {
            align-items: flex-start;
        }

        .message-bubble {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 13px;
        }

        .message.user .message-bubble {
            background: var(--accent);
            color: var(--vscode-button-foreground);
            border-bottom-right-radius: 4px;
        }

        .message.assistant .message-bubble {
            background: var(--input-bg);
            border-bottom-left-radius: 4px;
        }

        .message-bubble pre {
            background: rgba(0,0,0,0.2);
            padding: 8px;
            border-radius: 4px;
            margin-top: 8px;
            overflow-x: auto;
        }

        .message-bubble code {
            background: rgba(0,0,0,0.2);
            padding: 2px 4px;
            border-radius: 2px;
            font-family: var(--vscode-editor-font-family);
            font-size: 12px;
        }

        .typing-indicator {
            display: none;
            padding: 10px 16px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .typing-indicator.visible {
            display: block;
        }

        /* Chat Input */
        .chat-input-container {
            display: flex;
            padding: 12px;
            border-top: 1px solid var(--border);
            gap: 8px;
        }

        .chat-input {
            flex: 1;
            background: var(--input-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px 12px;
            color: var(--fg);
            font-family: var(--vscode-font-family);
            font-size: 13px;
            resize: none;
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--accent);
        }

        /* Buttons */
        .btn {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: none;
            padding: 8px 14px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background 0.15s;
        }

        .btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .btn.primary {
            background: var(--accent);
            color: var(--vscode-button-foreground);
        }

        .btn.primary:hover {
            background: var(--accent-hover);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Action Buttons Grid */
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 8px;
            margin-top: 16px;
        }

        .action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 12px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
        }

        .action-btn:hover {
            border-color: var(--accent);
            background: var(--input-bg);
        }

        .action-btn .icon {
            font-size: 20px;
        }

        .action-btn .label {
            font-size: 12px;
            font-weight: 500;
        }

        .action-btn .shortcut {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
        }

        /* Form Type Selector */
        .form-selector {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }

        .form-selector .btn.active {
            background: var(--accent);
            color: var(--vscode-button-foreground);
        }

        /* Completion Banner */
        .completion-banner {
            display: none;
            background: rgba(78, 201, 176, 0.15);
            border: 1px solid var(--success);
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 16px;
        }

        .completion-banner.visible {
            display: block;
        }

        .completion-banner h3 {
            color: var(--success);
            margin-bottom: 8px;
        }

        /* Hidden utility */
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Empathy Guide</h1>
            <div class="header-actions">
                <button class="btn" id="btnClearChat">Clear Chat</button>
                <button class="btn" id="btnCopyResults">Copy Results</button>
            </div>
        </header>

        <!-- Summary Card (shown when workflow result available) -->
        <div id="summaryCard" class="card hidden">
            <div class="card-header">
                <span class="card-title">Summary</span>
            </div>
            <div class="card-content" id="summaryContent"></div>
        </div>

        <!-- Results Card (collapsible) -->
        <div id="resultsCard" class="card hidden">
            <div class="card-header">
                <span class="card-title">Results</span>
                <button class="btn" id="btnToggleResults">Toggle</button>
            </div>
            <div class="card-content" id="resultsContent"></div>
        </div>

        <!-- Completion Banner -->
        <div id="completionBanner" class="completion-banner">
            <h3>Plan Complete!</h3>
            <p id="completionText"></p>
        </div>

        <!-- Form Type Selector -->
        <div class="form-selector" id="formSelector">
            <button class="btn" data-form="general">General</button>
            <button class="btn" data-form="plan-refinement">Plan</button>
            <button class="btn" data-form="workflow-customization">Customize</button>
            <button class="btn" data-form="learning-mode">Learn</button>
        </div>

        <!-- Chat Container -->
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages"></div>
            <div class="typing-indicator" id="typingIndicator">Assistant is thinking...</div>
            <div class="chat-input-container">
                <textarea
                    class="chat-input"
                    id="chatInput"
                    rows="2"
                    placeholder="Type your message..."
                ></textarea>
                <button class="btn primary" id="btnSend">Send</button>
            </div>
        </div>

        <!-- Next Actions -->
        <div class="actions-grid" id="actionsGrid">
            <div class="action-btn" data-action="morning">
                <span class="icon">&#x1F324;</span>
                <span class="label">Morning</span>
                <span class="shortcut">Ctrl+Shift+E M</span>
            </div>
            <div class="action-btn" data-action="ship">
                <span class="icon">&#x1F680;</span>
                <span class="label">Ship Check</span>
                <span class="shortcut">Ctrl+Shift+E S</span>
            </div>
            <div class="action-btn" data-action="fixAll">
                <span class="icon">&#x1F527;</span>
                <span class="label">Fix All</span>
                <span class="shortcut">Ctrl+Shift+E F</span>
            </div>
            <div class="action-btn" data-action="runWorkflow">
                <span class="icon">&#x25B6;</span>
                <span class="label">Workflows</span>
                <span class="shortcut">Ctrl+Shift+E W</span>
            </div>
            <div class="action-btn" data-action="runTests">
                <span class="icon">&#x1F9EA;</span>
                <span class="label">Run Tests</span>
                <span class="shortcut">Ctrl+Shift+E T</span>
            </div>
            <div class="action-btn" data-action="researchSynthesis">
                <span class="icon">&#x1F50D;</span>
                <span class="label">Research</span>
                <span class="shortcut">Workflow</span>
            </div>
            <div class="action-btn" data-action="agentFactory">
                <span class="icon">&#x1F916;</span>
                <span class="label">Agent Factory</span>
                <span class="shortcut">Design Crew</span>
            </div>
            <div class="action-btn" data-action="dashboard">
                <span class="icon">&#x1F4CA;</span>
                <span class="label">Dashboard</span>
                <span class="shortcut">Ctrl+Shift+E D</span>
            </div>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        let currentFormType = 'general';

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            console.log('[GuidedPanel WebView] DOMContentLoaded');
            vscode.postMessage({ type: 'ready' });
            setupEventListeners();
        });

        function setupEventListeners() {
            console.log('[GuidedPanel WebView] Setting up event listeners');

            // Header buttons
            document.getElementById('btnClearChat').addEventListener('click', clearChat);
            document.getElementById('btnCopyResults').addEventListener('click', copyResults);
            document.getElementById('btnToggleResults').addEventListener('click', toggleResults);
            document.getElementById('btnSend').addEventListener('click', sendMessage);

            // Chat input
            document.getElementById('chatInput').addEventListener('keydown', handleKeyDown);

            // Form type selector
            document.querySelectorAll('#formSelector .btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const formType = btn.dataset.form;
                    console.log('[GuidedPanel WebView] Form type selected:', formType);
                    selectFormType(formType);
                });
            });

            // Action buttons
            document.querySelectorAll('#actionsGrid .action-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const action = btn.dataset.action;
                    console.log('[GuidedPanel WebView] Action clicked:', action);
                    runAction(action);
                });
            });

            console.log('[GuidedPanel WebView] Event listeners ready');
        }

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;

            switch (message.type) {
                case 'fullState':
                    renderFullState(message);
                    break;

                case 'newMessage':
                    appendMessage(message.message);
                    break;

                case 'typing':
                    document.getElementById('typingIndicator').classList.toggle('visible', message.isTyping);
                    break;

                case 'conversationComplete':
                    showCompletion(message.result);
                    break;
            }
        });

        function renderFullState(data) {
            currentFormType = data.state.formType;

            // Update form selector
            document.querySelectorAll('.form-selector .btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.form === currentFormType);
            });

            // Show/hide summary
            const summaryCard = document.getElementById('summaryCard');
            const summaryContent = document.getElementById('summaryContent');
            if (data.state.summary) {
                summaryContent.textContent = data.state.summary;
                summaryCard.classList.remove('hidden');
            } else {
                summaryCard.classList.add('hidden');
            }

            // Show/hide results
            const resultsCard = document.getElementById('resultsCard');
            const resultsContent = document.getElementById('resultsContent');
            if (data.state.results) {
                resultsContent.innerHTML = '<pre>' + escapeHtml(data.state.results) + '</pre>';
                resultsCard.classList.remove('hidden');
            } else {
                resultsCard.classList.add('hidden');
            }

            // Render messages
            const container = document.getElementById('chatMessages');
            container.innerHTML = '';
            data.messages.forEach(msg => appendMessage(msg, false));

            // Show completion if applicable
            if (data.isComplete && data.result) {
                showCompletion(data.result);
            }
        }

        function appendMessage(msg, scroll = true) {
            const container = document.getElementById('chatMessages');
            const div = document.createElement('div');
            div.className = 'message ' + msg.role;

            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.innerHTML = formatMessage(msg.content);

            div.appendChild(bubble);
            container.appendChild(div);

            if (scroll) {
                container.scrollTop = container.scrollHeight;
            }
        }

        function formatMessage(text) {
            // Simple markdown-like formatting
            let html = escapeHtml(text);

            // Code blocks
            html = html.replace(/\`\`\`(\\w*)\\n([\\s\\S]*?)\`\`\`/g, '<pre><code>$2</code></pre>');

            // Inline code
            html = html.replace(/\`([^\`]+)\`/g, '<code>$1</code>');

            // Bold
            html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');

            // Line breaks
            html = html.replace(/\\n/g, '<br>');

            return html;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const text = input.value.trim();
            if (!text) return;

            // Add user message immediately
            appendMessage({ role: 'user', content: text });

            // Clear input
            input.value = '';

            // Send to extension
            vscode.postMessage({ type: 'sendMessage', text });
        }

        function handleKeyDown(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        function selectFormType(formType) {
            currentFormType = formType;
            vscode.postMessage({ type: 'newConversation', formType });
        }

        function runAction(action) {
            console.log('[GuidedPanel WebView] runAction called:', action);
            vscode.postMessage({ type: 'runAction', action });
        }

        function clearChat() {
            vscode.postMessage({ type: 'clearChat' });
        }

        function copyResults() {
            vscode.postMessage({ type: 'copyResult' });
        }

        function toggleResults() {
            const content = document.getElementById('resultsContent');
            content.classList.toggle('hidden');
        }

        function showCompletion(result) {
            const banner = document.getElementById('completionBanner');
            const text = document.getElementById('completionText');

            if (result && result.plan) {
                text.textContent = 'Your implementation plan is ready. Check the last message above.';
            } else if (result && result.yaml) {
                text.textContent = 'Configuration generated. Copy the YAML from the chat above.';
            } else {
                text.textContent = 'Conversation complete. Start a new one with the buttons above.';
            }

            banner.classList.add('visible');
        }
    </script>
</body>
</html>`;
    }

    /**
     * Generate nonce for CSP
     */
    private _getNonce(): string {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < 32; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }

    /**
     * Dispose panel
     */
    public dispose(): void {
        GuidedPanelProvider.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
}
