/**
 * Diagnostics Provider
 * Analyzes code and shows issues (red/yellow squiggly lines)
 */

import * as vscode from 'vscode';
import { LanguageClient } from 'vscode-languageclient/node';

export class CoachDiagnosticsProvider {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private analysisQueue: Map<string, NodeJS.Timeout> = new Map();

    constructor(
        private client: LanguageClient,
        context: vscode.ExtensionContext
    ) {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('coach');
        context.subscriptions.push(this.diagnosticCollection);

        // Listen for LSP diagnostics
        this.client.onNotification('textDocument/publishDiagnostics', (params) => {
            this.handleLSPDiagnostics(params);
        });
    }

    /**
     * Analyze document on demand
     */
    async analyzeDocument(document: vscode.TextDocument): Promise<void> {
        // Debounce analysis (wait 500ms after last change)
        const uri = document.uri.toString();

        if (this.analysisQueue.has(uri)) {
            clearTimeout(this.analysisQueue.get(uri)!);
        }

        const timeout = setTimeout(async () => {
            this.analysisQueue.delete(uri);
            await this.performAnalysis(document);
        }, 500);

        this.analysisQueue.set(uri, timeout);
    }

    /**
     * Perform actual analysis
     */
    private async performAnalysis(document: vscode.TextDocument): Promise<void> {
        const diagnostics: vscode.Diagnostic[] = [];

        // Quick pattern-based analysis (local, instant)
        diagnostics.push(...this.analyzeSecurityPatterns(document));
        diagnostics.push(...this.analyzePerformancePatterns(document));
        diagnostics.push(...this.analyzeAccessibilityPatterns(document));

        // Set diagnostics immediately (don't wait for LSP)
        this.diagnosticCollection.set(document.uri, diagnostics);

        // Optionally: Request deep analysis from LSP server
        // (This would be async and update diagnostics when complete)
        try {
            await this.client.sendRequest('coach/analyzeDocument', {
                uri: document.uri.toString(),
                text: document.getText()
            });
        } catch (error) {
            // LSP analysis is optional, don't fail if it doesn't work
            console.log('LSP analysis failed:', error);
        }
    }

    /**
     * Handle diagnostics from LSP server
     */
    private handleLSPDiagnostics(params: any): void {
        const uri = vscode.Uri.parse(params.uri);
        const diagnostics = params.diagnostics.map((d: any) => this.convertLSPDiagnostic(d));
        this.diagnosticCollection.set(uri, diagnostics);
    }

    private convertLSPDiagnostic(lspDiag: any): vscode.Diagnostic {
        const range = new vscode.Range(
            lspDiag.range.start.line,
            lspDiag.range.start.character,
            lspDiag.range.end.line,
            lspDiag.range.end.character
        );

        const diagnostic = new vscode.Diagnostic(
            range,
            lspDiag.message,
            this.convertSeverity(lspDiag.severity)
        );

        diagnostic.source = lspDiag.source || 'coach';
        diagnostic.code = lspDiag.code;

        return diagnostic;
    }

    private convertSeverity(lspSeverity: number): vscode.DiagnosticSeverity {
        switch (lspSeverity) {
            case 1: return vscode.DiagnosticSeverity.Error;
            case 2: return vscode.DiagnosticSeverity.Warning;
            case 3: return vscode.DiagnosticSeverity.Information;
            case 4: return vscode.DiagnosticSeverity.Hint;
            default: return vscode.DiagnosticSeverity.Warning;
        }
    }

    // Pattern-based analysis (instant, local)

    private analyzeSecurityPatterns(document: vscode.TextDocument): vscode.Diagnostic[] {
        const diagnostics: vscode.Diagnostic[] = [];
        const text = document.getText();

        // SQL Injection patterns
        const sqlInjectionRegex = /f['"].*?SELECT.*?\{.*?\}.*?['"]/gi;
        let match;
        while ((match = sqlInjectionRegex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(
                position,
                document.positionAt(match.index + match[0].length)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                'Potential SQL injection vulnerability - use parameterized queries',
                vscode.DiagnosticSeverity.Error
            );
            diagnostic.source = 'coach.security';
            diagnostic.code = 'sql_injection';
            diagnostics.push(diagnostic);
        }

        // XSS patterns (innerHTML, dangerouslySetInnerHTML)
        const xssRegex = /(innerHTML|dangerouslySetInnerHTML)\s*=\s*[^;]+/g;
        while ((match = xssRegex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(
                position,
                document.positionAt(match.index + match[0].length)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                'Potential XSS vulnerability - sanitize HTML or use textContent',
                vscode.DiagnosticSeverity.Warning
            );
            diagnostic.source = 'coach.security';
            diagnostic.code = 'xss';
            diagnostics.push(diagnostic);
        }

        // Hardcoded secrets
        const secretRegex = /(password|secret|api_key|token)\s*=\s*['"][^'"]+['"]/gi;
        while ((match = secretRegex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(
                position,
                document.positionAt(match.index + match[0].length)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                'Hardcoded secret detected - use environment variables',
                vscode.DiagnosticSeverity.Warning
            );
            diagnostic.source = 'coach.security';
            diagnostic.code = 'hardcoded_secret';
            diagnostics.push(diagnostic);
        }

        return diagnostics;
    }

    private analyzePerformancePatterns(document: vscode.TextDocument): vscode.Diagnostic[] {
        const diagnostics: vscode.Diagnostic[] = [];
        const text = document.getText();

        // N+1 query pattern
        const n1Regex = /for\s+\w+\s+in\s+\w+:[\s\S]*?\.(get|filter|find)\(/gi;
        let match;
        while ((match = n1Regex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(
                position,
                document.positionAt(match.index + match[0].length)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                'Potential N+1 query pattern - consider using batch queries',
                vscode.DiagnosticSeverity.Warning
            );
            diagnostic.source = 'coach.performance';
            diagnostic.code = 'n_plus_one';
            diagnostics.push(diagnostic);
        }

        // Large loops
        const largeLoopRegex = /for\s+\w+\s+in\s+range\((\d+)\)/gi;
        while ((match = largeLoopRegex.exec(text)) !== null) {
            const iterations = parseInt(match[1]);
            if (iterations > 1000) {
                const position = document.positionAt(match.index);
                const range = new vscode.Range(
                    position,
                    document.positionAt(match.index + match[0].length)
                );

                const diagnostic = new vscode.Diagnostic(
                    range,
                    `Large loop (${iterations} iterations) - consider optimization`,
                    vscode.DiagnosticSeverity.Information
                );
                diagnostic.source = 'coach.performance';
                diagnostic.code = 'large_loop';
                diagnostics.push(diagnostic);
            }
        }

        return diagnostics;
    }

    private analyzeAccessibilityPatterns(document: vscode.TextDocument): vscode.Diagnostic[] {
        const diagnostics: vscode.Diagnostic[] = [];

        // Only analyze HTML/JSX/TSX files
        if (!['html', 'javascriptreact', 'typescriptreact'].includes(document.languageId)) {
            return diagnostics;
        }

        const text = document.getText();

        // Buttons without aria-label
        const buttonRegex = /<button(?!\s+aria-label)[^>]*>/gi;
        let match;
        while ((match = buttonRegex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(
                position,
                document.positionAt(match.index + match[0].length)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                'Button missing aria-label - add for screen reader accessibility',
                vscode.DiagnosticSeverity.Information
            );
            diagnostic.source = 'coach.accessibility';
            diagnostic.code = 'missing_aria_label';
            diagnostics.push(diagnostic);
        }

        // Images without alt text
        const imgRegex = /<img(?!\s+alt)[^>]*>/gi;
        while ((match = imgRegex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(
                position,
                document.positionAt(match.index + match[0].length)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                'Image missing alt attribute - required for accessibility',
                vscode.DiagnosticSeverity.Warning
            );
            diagnostic.source = 'coach.accessibility';
            diagnostic.code = 'missing_alt';
            diagnostics.push(diagnostic);
        }

        // onclick without keyboard support
        const onclickRegex = /onclick=["'][^"']+["'](?![^<]*onkeypress)/gi;
        while ((match = onclickRegex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(
                position,
                document.positionAt(match.index + match[0].length)
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                'onclick without keyboard support - add onKeyPress for accessibility',
                vscode.DiagnosticSeverity.Information
            );
            diagnostic.source = 'coach.accessibility';
            diagnostic.code = 'keyboard_support';
            diagnostics.push(diagnostic);
        }

        return diagnostics;
    }

    /**
     * Clear diagnostics for a document
     */
    clear(document: vscode.TextDocument): void {
        this.diagnosticCollection.delete(document.uri);
    }

    /**
     * Clear all diagnostics
     */
    clearAll(): void {
        this.diagnosticCollection.clear();
    }
}
