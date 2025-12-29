/**
 * Initialize Wizard Panel
 *
 * Multi-step onboarding wizard for new Empathy Framework users.
 * Guides users through provider selection, API key setup, and config generation.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Supported LLM providers
 */
type Provider = 'anthropic' | 'openai' | 'google' | 'ollama';

/**
 * Wizard step definitions
 */
type WizardStep = 'welcome' | 'provider' | 'apiKey' | 'preferences' | 'generate' | 'complete';

/**
 * Message types from webview to extension
 */
type WebviewMessage =
    | { type: 'ready' }
    | { type: 'selectProvider'; provider: Provider }
    | { type: 'setApiKey'; provider: Provider; key: string }
    | { type: 'validateApiKey'; provider: Provider; key: string }
    | { type: 'setTierPreference'; tier: string; model: string }
    | { type: 'generateConfig' }
    | { type: 'runDemo' }
    | { type: 'complete' }
    | { type: 'back' }
    | { type: 'skip' };

/**
 * Wizard state
 */
interface WizardState {
    currentStep: WizardStep;
    provider: Provider | null;
    apiKeyValid: boolean;
    preferences: {
        cheap?: string;
        capable?: string;
        premium?: string;
    };
    configGenerated: boolean;
}

/**
 * Initialize Wizard Panel for onboarding new users
 */
export class InitializeWizardPanel {
    public static readonly viewType = 'empathy.initializeWizard';

    private static currentPanel: InitializeWizardPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private readonly _context: vscode.ExtensionContext;
    private _state: WizardState;
    private _disposables: vscode.Disposable[] = [];

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        context: vscode.ExtensionContext
    ) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._context = context;
        this._state = {
            currentStep: 'welcome',
            provider: null,
            apiKeyValid: false,
            preferences: {},
            configGenerated: false
        };

        // Set up webview
        this._panel.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(extensionUri, 'webview'),
                vscode.Uri.joinPath(extensionUri, 'media')
            ]
        };

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
     * Create or show the wizard panel
     */
    public static createOrShow(context: vscode.ExtensionContext): void {
        const column = vscode.ViewColumn.One;

        // If panel exists, show it
        if (InitializeWizardPanel.currentPanel) {
            InitializeWizardPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Create new panel
        const panel = vscode.window.createWebviewPanel(
            InitializeWizardPanel.viewType,
            'Initialize Empathy',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(context.extensionUri, 'webview'),
                    vscode.Uri.joinPath(context.extensionUri, 'media')
                ]
            }
        );

        InitializeWizardPanel.currentPanel = new InitializeWizardPanel(
            panel,
            context.extensionUri,
            context
        );
    }

    /**
     * Handle messages from webview
     */
    private async _handleMessage(message: WebviewMessage): Promise<void> {
        switch (message.type) {
            case 'ready':
                this._updateWebview();
                break;

            case 'selectProvider':
                this._state.provider = message.provider;
                // Brief delay so user sees selection before advancing
                this._postMessage({ type: 'providerSelected', provider: message.provider });
                setTimeout(() => {
                    if (message.provider === 'ollama') {
                        // Ollama doesn't need API key
                        this._state.apiKeyValid = true;
                        this._state.currentStep = 'preferences';
                    } else {
                        this._state.currentStep = 'apiKey';
                    }
                    this._updateWebview();
                }, 300);
                break;

            case 'validateApiKey':
                const isValid = await this._validateApiKey(message.provider, message.key);
                this._state.apiKeyValid = isValid;
                if (isValid) {
                    // Store securely
                    await this._context.secrets.store(
                        `empathy.${message.provider}.apiKey`,
                        message.key
                    );
                }
                this._postMessage({
                    type: 'keyValidationResult',
                    valid: isValid
                });
                break;

            case 'setApiKey':
                if (this._state.apiKeyValid) {
                    this._state.currentStep = 'preferences';
                    this._updateWebview();
                }
                break;

            case 'setTierPreference':
                this._state.preferences[message.tier as keyof typeof this._state.preferences] = message.model;
                break;

            case 'generateConfig':
                await this._generateConfigFile();
                this._state.configGenerated = true;
                this._state.currentStep = 'complete';
                this._updateWebview();
                break;

            case 'runDemo':
                await this._runDemo();
                break;

            case 'complete':
                // Mark wizard as completed
                await this._context.globalState.update('empathy.initialized', true);
                await this._context.globalState.update('empathy.initializedAt', new Date().toISOString());
                this._panel.dispose();
                vscode.window.showInformationMessage(
                    'Empathy Framework initialized! Try running a workflow from the dashboard.'
                );
                break;

            case 'back':
                this._goBack();
                break;

            case 'skip':
                // Skip to next logical step
                if (this._state.currentStep === 'apiKey') {
                    this._state.currentStep = 'preferences';
                    this._updateWebview();
                } else if (this._state.currentStep === 'preferences') {
                    // Skip preferences and generate config directly
                    this._generateConfigFile();
                    this._state.configGenerated = true;
                    this._state.currentStep = 'complete';
                    this._updateWebview();
                }
                break;
        }
    }

    /**
     * Navigate back to previous step
     */
    private _goBack(): void {
        const stepOrder: WizardStep[] = ['welcome', 'provider', 'apiKey', 'preferences', 'complete'];
        const currentIndex = stepOrder.indexOf(this._state.currentStep);
        if (currentIndex > 0) {
            this._state.currentStep = stepOrder[currentIndex - 1];
            this._updateWebview();
        }
    }

    /**
     * Validate API key format and optionally test connection
     */
    private async _validateApiKey(provider: Provider, key: string): Promise<boolean> {
        // Basic format validation
        if (!key || key.trim().length === 0) {
            return false;
        }

        switch (provider) {
            case 'anthropic':
                // Anthropic keys start with sk-ant-
                return key.startsWith('sk-ant-') && key.length > 20;

            case 'openai':
                // OpenAI keys start with sk-
                return key.startsWith('sk-') && key.length > 20;

            case 'google':
                // Google/Gemini API keys start with AIza
                return key.startsWith('AIza') && key.length > 30;

            default:
                return true;
        }
    }

    /**
     * Generate empathy.config.yml file
     */
    private async _generateConfigFile(): Promise<void> {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder open. Please open a folder first.');
            return;
        }

        const workspaceRoot = workspaceFolders[0].uri.fsPath;
        const configPath = path.join(workspaceRoot, 'empathy.config.yml');

        // Get default models based on provider
        const defaultModels = this._getDefaultModels(this._state.provider || 'anthropic');

        const configContent = `# Empathy Framework Configuration
# Generated by Initialize Wizard on ${new Date().toISOString()}

# Primary LLM provider
provider: ${this._state.provider || 'anthropic'}

# Model tier preferences (optional overrides)
model_preferences:
  cheap: ${this._state.preferences.cheap || defaultModels.cheap}
  capable: ${this._state.preferences.capable || defaultModels.capable}
  premium: ${this._state.preferences.premium || defaultModels.premium}

# Workflow settings
workflows:
  # Cost guardrail - workflows will gracefully degrade if exceeded
  max_cost_per_run: 5.00

  # Enable XML-structured outputs for workflows
  xml_enhanced: true

# Memory settings
memory:
  # Enable Redis-backed short-term memory
  enabled: true
  redis_url: redis://localhost:6379

# Telemetry settings
telemetry:
  # Store call logs for analytics
  enabled: true
  storage: jsonl  # jsonl, sqlite, or none
`;

        try {
            fs.writeFileSync(configPath, configContent, 'utf8');
            vscode.window.showInformationMessage(`Created ${configPath}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create config: ${error}`);
        }
    }

    /**
     * Get default models for a provider
     */
    private _getDefaultModels(provider: Provider): { cheap: string; capable: string; premium: string } {
        switch (provider) {
            case 'anthropic':
                return {
                    cheap: 'claude-3-5-haiku-20241022',
                    capable: 'claude-sonnet-4-20250514',
                    premium: 'claude-opus-4-20250514'
                };
            case 'openai':
                return {
                    cheap: 'gpt-4o-mini',
                    capable: 'gpt-4o',
                    premium: 'o1'
                };
            case 'google':
                return {
                    cheap: 'gemini-2.0-flash-exp',
                    capable: 'gemini-1.5-pro',
                    premium: 'gemini-2.5-pro'
                };
            case 'ollama':
                return {
                    cheap: 'llama3.2:3b',
                    capable: 'llama3.1:8b',
                    premium: 'llama3.1:70b'
                };
            default:
                return {
                    cheap: 'claude-3-5-haiku-20241022',
                    capable: 'claude-sonnet-4-20250514',
                    premium: 'claude-opus-4-20250514'
                };
        }
    }

    /**
     * Run demo workflow
     */
    private async _runDemo(): Promise<void> {
        // Create demo file
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            return;
        }

        const demoPath = path.join(workspaceFolders[0].uri.fsPath, 'hello_empathy.py');
        const demoContent = `"""Your first Empathy workflow - generated by Initialize Wizard."""
from empathy_os.workflows import SecurityAuditWorkflow

def main():
    # Run a quick security scan on this file
    workflow = SecurityAuditWorkflow()
    result = workflow.run(target=".")

    print(f"Scan complete! Found {len(result.final_output.get('findings', []))} items.")
    print(f"Cost: \${result.cost_report.total_cost:.4f}")

if __name__ == "__main__":
    main()
`;

        try {
            fs.writeFileSync(demoPath, demoContent, 'utf8');
            const doc = await vscode.workspace.openTextDocument(demoPath);
            await vscode.window.showTextDocument(doc);
            vscode.window.showInformationMessage(
                'Created hello_empathy.py - run it with: python hello_empathy.py'
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create demo: ${error}`);
        }
    }

    /**
     * Post message to webview
     */
    private _postMessage(message: unknown): void {
        this._panel.webview.postMessage(message);
    }

    /**
     * Update webview with current state
     */
    private _updateWebview(): void {
        this._postMessage({
            type: 'stateUpdate',
            state: this._state
        });
    }

    /**
     * Get HTML content for webview
     */
    private _getHtmlForWebview(): string {
        const nonce = this._getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}' 'unsafe-inline';">
    <title>Initialize Empathy</title>
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
            padding: 24px;
            min-height: 100vh;
        }

        .wizard-container {
            max-width: 600px;
            margin: 0 auto;
        }

        .step-indicator {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 32px;
        }

        .step-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--vscode-input-border);
            transition: all 0.3s ease;
        }

        .step-dot.active {
            background: var(--vscode-button-background);
            transform: scale(1.2);
        }

        .step-dot.completed {
            background: var(--vscode-testing-iconPassed);
        }

        h1 {
            font-size: 28px;
            margin-bottom: 8px;
            text-align: center;
        }

        .subtitle {
            color: var(--vscode-descriptionForeground);
            text-align: center;
            margin-bottom: 32px;
        }

        .provider-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }

        .provider-card {
            background: var(--vscode-input-background);
            border: 2px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
        }

        .provider-card:hover {
            border-color: var(--vscode-button-background);
            transform: translateY(-2px);
        }

        .provider-card.selected {
            border-color: var(--vscode-button-background);
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        .provider-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .provider-name {
            font-weight: bold;
            margin-bottom: 4px;
        }

        .provider-desc {
            font-size: 12px;
            opacity: 0.8;
        }

        .input-group {
            margin-bottom: 20px;
        }

        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .input-group input {
            width: 100%;
            padding: 12px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            color: var(--vscode-input-foreground);
            font-size: 14px;
        }

        .input-group input:focus {
            outline: none;
            border-color: var(--vscode-button-background);
        }

        .validation-status {
            margin-top: 8px;
            font-size: 12px;
        }

        .validation-status.valid {
            color: var(--vscode-testing-iconPassed);
        }

        .validation-status.invalid {
            color: var(--vscode-testing-iconFailed);
        }

        .button-row {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        button {
            flex: 1;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        button.primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        button.primary:hover {
            background: var(--vscode-button-hoverBackground);
        }

        button.secondary {
            background: transparent;
            border: 1px solid var(--vscode-button-border, var(--vscode-input-border));
            color: var(--vscode-foreground);
        }

        button.secondary:hover {
            background: var(--vscode-input-background);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .success-icon {
            font-size: 64px;
            text-align: center;
            margin-bottom: 16px;
        }

        .feature-list {
            list-style: none;
            margin: 24px 0;
        }

        .feature-list li {
            padding: 8px 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .feature-list li::before {
            content: "✓";
            color: var(--vscode-testing-iconPassed);
            font-weight: bold;
        }

        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>
    <div class="wizard-container">
        <div class="step-indicator" id="stepIndicator">
            <div class="step-dot" data-step="welcome"></div>
            <div class="step-dot" data-step="provider"></div>
            <div class="step-dot" data-step="apiKey"></div>
            <div class="step-dot" data-step="preferences"></div>
            <div class="step-dot" data-step="complete"></div>
        </div>

        <!-- Welcome Step -->
        <div class="step" id="step-welcome">
            <h1>Welcome to Empathy</h1>
            <p class="subtitle">Let's get you set up in under 5 minutes</p>

            <ul class="feature-list">
                <li>Multi-provider LLM support (Anthropic, OpenAI, Google Gemini, Ollama)</li>
                <li>Smart tier routing saves 80-96% on API costs</li>
                <li>10+ production-ready workflows</li>
                <li>Enterprise-ready with XML-enhanced outputs</li>
            </ul>

            <div class="button-row">
                <button class="primary" id="btn-start">Get Started</button>
            </div>
        </div>

        <!-- Provider Selection Step -->
        <div class="step hidden" id="step-provider">
            <h1>Choose Your Provider</h1>
            <p class="subtitle">Select your primary LLM provider</p>

            <div class="provider-grid">
                <div class="provider-card" data-provider="anthropic">
                    <div class="provider-icon">🟣</div>
                    <div class="provider-name">Anthropic</div>
                    <div class="provider-desc">Opus 4.5, Sonnet 4.5 & Haiku</div>
                </div>
                <div class="provider-card" data-provider="openai">
                    <div class="provider-icon">🟢</div>
                    <div class="provider-name">OpenAI</div>
                    <div class="provider-desc">GPT-4o & o1</div>
                </div>
                <div class="provider-card" data-provider="google">
                    <div class="provider-icon">🔵</div>
                    <div class="provider-name">Google Gemini</div>
                    <div class="provider-desc">2M context window</div>
                </div>
                <div class="provider-card" data-provider="ollama">
                    <div class="provider-icon">🦙</div>
                    <div class="provider-name">Ollama</div>
                    <div class="provider-desc">Local Llama models</div>
                </div>
            </div>

            <div class="button-row">
                <button class="secondary" id="btn-back-provider">Back</button>
            </div>
        </div>

        <!-- API Key Step -->
        <div class="step hidden" id="step-apiKey">
            <h1>Enter API Key</h1>
            <p class="subtitle" id="apiKeySubtitle">Enter your API key to continue</p>

            <div class="input-group">
                <label for="apiKey">API Key</label>
                <input type="password" id="apiKey" placeholder="Enter API key...">
                <div class="validation-status" id="keyStatus"></div>
            </div>

            <div class="button-row">
                <button class="secondary" id="btn-back-apikey">Back</button>
                <button class="secondary" id="btn-skip">Skip</button>
                <button class="primary" id="continueKeyBtn" disabled>Continue</button>
            </div>
        </div>

        <!-- Preferences Step -->
        <div class="step hidden" id="step-preferences">
            <h1>Model Preferences</h1>
            <p class="subtitle">Customize which models to use (optional)</p>

            <div class="input-group">
                <label>Using default model configuration for your provider.</label>
                <p style="margin-top: 12px; color: var(--vscode-descriptionForeground);">
                    You can customize these later in empathy.config.yml
                </p>
            </div>

            <div class="button-row">
                <button class="secondary" id="btn-back-prefs">Back</button>
                <button class="primary" id="btn-generate">Generate Config</button>
            </div>
        </div>

        <!-- Complete Step -->
        <div class="step hidden" id="step-complete">
            <div class="success-icon">🎉</div>
            <h1>You're All Set!</h1>
            <p class="subtitle">Empathy Framework is ready to use</p>

            <ul class="feature-list">
                <li>Configuration file created</li>
                <li>API key stored securely</li>
                <li>Ready to run workflows</li>
            </ul>

            <div class="button-row">
                <button class="secondary" id="btn-demo">Create Demo File</button>
                <button class="primary" id="btn-complete">Open Dashboard</button>
            </div>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        let currentState = {
            currentStep: 'welcome',
            provider: null,
            apiKeyValid: false
        };

        // Set up event listeners
        document.getElementById('btn-start').addEventListener('click', startWizard);
        document.getElementById('btn-back-provider').addEventListener('click', goBack);
        document.getElementById('btn-back-apikey').addEventListener('click', goBack);
        document.getElementById('btn-back-prefs').addEventListener('click', goBack);
        document.getElementById('btn-skip').addEventListener('click', skipStep);
        document.getElementById('continueKeyBtn').addEventListener('click', submitKey);
        document.getElementById('btn-generate').addEventListener('click', generateConfig);
        document.getElementById('btn-demo').addEventListener('click', runDemo);
        document.getElementById('btn-complete').addEventListener('click', complete);
        document.getElementById('apiKey').addEventListener('input', validateKey);

        // Provider card click handlers
        document.querySelectorAll('.provider-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const target = e.currentTarget;
                const provider = target.dataset.provider;
                console.log('[Wizard] Provider card clicked:', provider);

                // Immediate visual feedback
                document.querySelectorAll('.provider-card').forEach(c => c.classList.remove('selected'));
                target.classList.add('selected');

                // Send to extension
                selectProvider(provider);
            });
        });

        // Notify extension we're ready
        vscode.postMessage({ type: 'ready' });

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'stateUpdate') {
                currentState = message.state;
                updateUI();
            } else if (message.type === 'keyValidationResult') {
                updateKeyValidation(message.valid);
            }
        });

        function updateUI() {
            try {
                console.log('[Wizard] updateUI called, step:', currentState.currentStep);

                // Hide all steps
                document.querySelectorAll('.step').forEach(step => {
                    step.classList.add('hidden');
                });

                // Show current step
                const currentStepEl = document.getElementById('step-' + currentState.currentStep);
                console.log('[Wizard] Looking for step-' + currentState.currentStep, currentStepEl);
                if (currentStepEl) {
                    currentStepEl.classList.remove('hidden');
                }

                // Update step indicator
                const steps = ['welcome', 'provider', 'apiKey', 'preferences', 'complete'];
                const currentIndex = steps.indexOf(currentState.currentStep);
                document.querySelectorAll('.step-dot').forEach((dot, index) => {
                    dot.classList.remove('active', 'completed');
                    if (index === currentIndex) {
                        dot.classList.add('active');
                    } else if (index < currentIndex) {
                        dot.classList.add('completed');
                    }
                });

                // Update provider selection
                document.querySelectorAll('.provider-card').forEach(card => {
                card.classList.remove('selected');
                if (card.dataset.provider === currentState.provider) {
                    card.classList.add('selected');
                }
            });

            // Update API key subtitle and placeholder
            if (currentState.provider) {
                const providerNames = {
                    anthropic: 'Anthropic',
                    openai: 'OpenAI',
                    google: 'Google Gemini',
                    ollama: 'Ollama'
                };
                const placeholders = {
                    anthropic: 'sk-ant-...',
                    openai: 'sk-...',
                    google: 'AIza...',
                    ollama: 'No key required'
                };
                document.getElementById('apiKeySubtitle').textContent =
                    'Enter your ' + (providerNames[currentState.provider] || currentState.provider) + ' API key';
                document.getElementById('apiKey').placeholder =
                    placeholders[currentState.provider] || 'API key...';
            }
            console.log('[Wizard] updateUI complete');
            } catch (err) {
                console.error('[Wizard] Error in updateUI:', err);
            }
        }

        function startWizard() {
            try {
                console.log('[Wizard] startWizard called');
                currentState.currentStep = 'provider';
                console.log('[Wizard] calling updateUI');
                updateUI();
                console.log('[Wizard] updateUI complete');
            } catch (err) {
                console.error('[Wizard] Error in startWizard:', err);
            }
        }

        function selectProvider(provider) {
            vscode.postMessage({ type: 'selectProvider', provider });
        }

        function validateKey() {
            const key = document.getElementById('apiKey').value;
            if (key.length > 10) {
                vscode.postMessage({
                    type: 'validateApiKey',
                    provider: currentState.provider,
                    key
                });
            }
        }

        function updateKeyValidation(valid) {
            const status = document.getElementById('keyStatus');
            const btn = document.getElementById('continueKeyBtn');

            if (valid) {
                status.textContent = 'Valid API key format';
                status.className = 'validation-status valid';
                btn.disabled = false;
            } else {
                status.textContent = 'Invalid API key format';
                status.className = 'validation-status invalid';
                btn.disabled = true;
            }
        }

        function submitKey() {
            const key = document.getElementById('apiKey').value;
            vscode.postMessage({
                type: 'setApiKey',
                provider: currentState.provider,
                key
            });
        }

        function skipStep() {
            vscode.postMessage({ type: 'skip' });
        }

        function goBack() {
            vscode.postMessage({ type: 'back' });
        }

        function generateConfig() {
            vscode.postMessage({ type: 'generateConfig' });
        }

        function runDemo() {
            vscode.postMessage({ type: 'runDemo' });
        }

        function complete() {
            vscode.postMessage({ type: 'complete' });
        }

        // Initial UI update
        updateUI();
    </script>
</body>
</html>`;
    }

    /**
     * Generate a nonce for CSP
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
     * Dispose of resources
     */
    public dispose(): void {
        InitializeWizardPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
