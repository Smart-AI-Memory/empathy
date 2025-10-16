/**
 * Coach Panel
 * Main webview panel for displaying wizard results
 */

import * as vscode from 'vscode';
import { LanguageClient } from 'vscode-languageclient/node';

export class CoachPanel {
    private panel: vscode.WebviewPanel | undefined;

    constructor(
        private context: vscode.ExtensionContext,
        private client: LanguageClient
    ) {}

    show(): void {
        if (this.panel) {
            this.panel.reveal();
        } else {
            this.panel = vscode.window.createWebviewPanel(
                'coachPanel',
                'Coach Assistant',
                vscode.ViewColumn.Two,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            this.panel.webview.html = this.getInitialHtml();

            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });
        }
    }

    showWizardResult(result: any): void {
        this.show();
        if (this.panel) {
            this.panel.webview.postMessage({
                type: 'wizardResult',
                result: result
            });
        }
    }

    showMultiWizardResult(result: any): void {
        this.show();
        if (this.panel) {
            this.panel.webview.postMessage({
                type: 'multiWizardResult',
                result: result
            });
        }
    }

    private getInitialHtml(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coach Assistant</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: var(--vscode-textLink-foreground);
            border-bottom: 2px solid var(--vscode-textLink-foreground);
            padding-bottom: 10px;
        }
        h2 {
            color: var(--vscode-textPreformat-foreground);
            margin-top: 30px;
        }
        .wizard-badge {
            display: inline-block;
            background-color: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-right: 8px;
        }
        .confidence {
            color: var(--vscode-testing-iconPassed);
            font-weight: bold;
        }
        .artifact {
            background-color: var(--vscode-textCodeBlock-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 15px;
            margin: 15px 0;
        }
        .artifact-header {
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin-bottom: 10px;
        }
        .artifact-content {
            white-space: pre-wrap;
            font-family: var(--vscode-editor-font-family);
            font-size: 0.9em;
        }
        .synthesis {
            background-color: var(--vscode-inputValidation-infoBackground);
            border-left: 4px solid var(--vscode-inputValidation-infoBorder);
            padding: 15px;
            margin: 20px 0;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--vscode-descriptionForeground);
        }
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
        .routing {
            margin: 15px 0;
        }
        .routing-item {
            display: inline-block;
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            padding: 6px 12px;
            border-radius: 4px;
            margin: 4px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div id="content">
        <div class="empty-state">
            <div class="empty-state-icon">🎯</div>
            <h2>Coach Assistant</h2>
            <p>Run a wizard command to see results here.</p>
            <p style="margin-top: 20px;">
                Try: <code>Coach: Analyze Current File</code><br>
                Or: <code>Coach: Multi-Wizard Review</code>
            </p>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        window.addEventListener('message', event => {
            const message = event.data;

            if (message.type === 'wizardResult') {
                displayWizardResult(message.result);
            } else if (message.type === 'multiWizardResult') {
                displayMultiWizardResult(message.result);
            }
        });

        function displayWizardResult(result) {
            const content = document.getElementById('content');
            const primary = result.primary_output;

            let html = \`
                <h1>\${primary.wizard_name}</h1>
                <div class="confidence">
                    Confidence: \${Math.round(result.overall_confidence * 100)}%
                </div>

                <h2>Diagnosis</h2>
                <div class="artifact-content">\${escapeHtml(primary.diagnosis)}</div>
            \`;

            if (primary.artifacts && primary.artifacts.length > 0) {
                html += '<h2>Artifacts</h2>';
                for (const artifact of primary.artifacts) {
                    html += \`
                        <div class="artifact">
                            <div class="artifact-header">📄 \${artifact.name} (\${artifact.format})</div>
                            <div class="artifact-content">\${escapeHtml(artifact.content)}</div>
                        </div>
                    \`;
                }
            }

            content.innerHTML = html;
        }

        function displayMultiWizardResult(result) {
            const content = document.getElementById('content');

            let html = \`
                <h1>Multi-Wizard Collaboration</h1>
                <div class="confidence">
                    Overall Confidence: \${Math.round(result.overall_confidence * 100)}%
                </div>

                <h2>Routing</h2>
                <div class="routing">
            \`;

            for (const wizard of result.routing) {
                html += \`<span class="routing-item">\${wizard}</span>\`;
            }

            html += '</div>';

            // Primary output
            const primary = result.primary_output;
            html += \`
                <h2>\${primary.wizard_name} (Primary)</h2>
                <div class="artifact-content">\${escapeHtml(primary.diagnosis)}</div>
            \`;

            // Secondary outputs
            if (result.secondary_outputs && result.secondary_outputs.length > 0) {
                html += '<h2>Additional Wizard Insights</h2>';
                for (const output of result.secondary_outputs) {
                    html += \`
                        <div class="artifact">
                            <div class="artifact-header">\${output.wizard_name}</div>
                            <div class="artifact-content">\${escapeHtml(output.diagnosis)}</div>
                        </div>
                    \`;
                }
            }

            // Synthesis
            if (result.synthesis) {
                html += \`
                    <h2>Synthesis</h2>
                    <div class="synthesis">
                        \${escapeHtml(result.synthesis)}
                    </div>
                \`;
            }

            content.innerHTML = html;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>`;
    }
}
