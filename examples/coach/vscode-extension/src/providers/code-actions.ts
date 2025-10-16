/**
 * Code Actions Provider
 * Provides quick fixes from Coach wizards
 */

import * as vscode from 'vscode';
import { LanguageClient } from 'vscode-languageclient/node';

export class CoachCodeActionProvider implements vscode.CodeActionProvider {
    constructor(private client: LanguageClient) {}

    async provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.CodeAction[]> {
        const actions: vscode.CodeAction[] = [];

        // Get diagnostics for this range
        const diagnostics = context.diagnostics.filter(
            d => d.source?.startsWith('coach.')
        );

        for (const diagnostic of diagnostics) {
            const wizardActions = this.createActionsForDiagnostic(
                document,
                diagnostic,
                range
            );
            actions.push(...wizardActions);
        }

        return actions;
    }

    private createActionsForDiagnostic(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic,
        range: vscode.Range
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        if (diagnostic.source === 'coach.security') {
            actions.push(...this.createSecurityFixes(document, diagnostic, range));
        } else if (diagnostic.source === 'coach.performance') {
            actions.push(...this.createPerformanceFixes(document, diagnostic, range));
        } else if (diagnostic.source === 'coach.accessibility') {
            actions.push(...this.createAccessibilityFixes(document, diagnostic, range));
        }

        return actions;
    }

    private createSecurityFixes(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic,
        range: vscode.Range
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        // SQL Injection fix
        if (diagnostic.message.toLowerCase().includes('sql injection')) {
            const fix = new vscode.CodeAction(
                '🛡️ SecurityWizard: Use parameterized query',
                vscode.CodeActionKind.QuickFix
            );
            fix.diagnostics = [diagnostic];
            fix.edit = this.createSQLInjectionFix(document, diagnostic.range);
            fix.isPreferred = true;
            actions.push(fix);

            // Alternative: Add input validation
            const validate = new vscode.CodeAction(
                '🛡️ SecurityWizard: Add input validation',
                vscode.CodeActionKind.QuickFix
            );
            validate.diagnostics = [diagnostic];
            validate.edit = this.createInputValidationFix(document, diagnostic.range);
            actions.push(validate);
        }

        // XSS fix
        if (diagnostic.message.toLowerCase().includes('xss') ||
            diagnostic.message.toLowerCase().includes('cross-site scripting')) {
            const fix = new vscode.CodeAction(
                '🛡️ SecurityWizard: Escape HTML output',
                vscode.CodeActionKind.QuickFix
            );
            fix.diagnostics = [diagnostic];
            fix.edit = this.createXSSFix(document, diagnostic.range);
            fix.isPreferred = true;
            actions.push(fix);
        }

        // Generic security review
        const review = new vscode.CodeAction(
            '🛡️ SecurityWizard: Run full security audit',
            vscode.CodeActionKind.QuickFix
        );
        review.command = {
            title: 'Run Security Audit',
            command: 'coach.securityAudit',
            arguments: [document.uri]
        };
        actions.push(review);

        return actions;
    }

    private createPerformanceFixes(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic,
        range: vscode.Range
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        // N+1 query fix
        if (diagnostic.message.toLowerCase().includes('n+1')) {
            const fix = new vscode.CodeAction(
                '⚡ PerformanceWizard: Use batch query',
                vscode.CodeActionKind.QuickFix
            );
            fix.diagnostics = [diagnostic];
            fix.edit = this.createBatchQueryFix(document, diagnostic.range);
            fix.isPreferred = true;
            actions.push(fix);
        }

        // Caching suggestion
        const cache = new vscode.CodeAction(
            '⚡ PerformanceWizard: Add caching',
            vscode.CodeActionKind.QuickFix
        );
        cache.diagnostics = [diagnostic];
        cache.edit = this.createCachingFix(document, diagnostic.range);
        actions.push(cache);

        // Run performance profile
        const profile = new vscode.CodeAction(
            '⚡ PerformanceWizard: Run performance profile',
            vscode.CodeActionKind.QuickFix
        );
        profile.command = {
            title: 'Profile Performance',
            command: 'coach.performanceProfile',
            arguments: [document.uri]
        };
        actions.push(profile);

        return actions;
    }

    private createAccessibilityFixes(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic,
        range: vscode.Range
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        // ARIA label fix
        if (diagnostic.message.toLowerCase().includes('aria')) {
            const fix = new vscode.CodeAction(
                '♿ AccessibilityWizard: Add ARIA label',
                vscode.CodeActionKind.QuickFix
            );
            fix.diagnostics = [diagnostic];
            fix.edit = this.createARIAFix(document, diagnostic.range);
            fix.isPreferred = true;
            actions.push(fix);
        }

        // Color contrast fix
        if (diagnostic.message.toLowerCase().includes('contrast')) {
            const fix = new vscode.CodeAction(
                '♿ AccessibilityWizard: Improve color contrast',
                vscode.CodeActionKind.QuickFix
            );
            fix.diagnostics = [diagnostic];
            fix.edit = this.createContrastFix(document, diagnostic.range);
            actions.push(fix);
        }

        return actions;
    }

    // Fix implementations
    private createSQLInjectionFix(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.WorkspaceEdit {
        const edit = new vscode.WorkspaceEdit();
        const line = document.lineAt(range.start.line);
        const text = line.text;

        // Example: Convert f"SELECT * FROM users WHERE id={user_id}"
        // To: "SELECT * FROM users WHERE id=?", (user_id,)
        if (text.includes("f'") || text.includes('f"')) {
            // Simple pattern matching (production would use AST)
            const newText = text.replace(
                /f['"](.+?)['"]/,
                (match, query) => {
                    // Extract variables from f-string
                    const vars = query.match(/\{(\w+)\}/g)?.map((v: string) => v.slice(1, -1)) || [];
                    const paramQuery = query.replace(/\{(\w+)\}/g, '?');
                    return `"${paramQuery}", (${vars.join(', ')},)`;
                }
            );
            edit.replace(document.uri, line.range, newText);
        }

        return edit;
    }

    private createInputValidationFix(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.WorkspaceEdit {
        const edit = new vscode.WorkspaceEdit();

        // Add input validation before the vulnerable line
        const validation = `    # Validate input\n    if not isinstance(user_id, int):\n        raise ValueError("Invalid user_id")\n`;
        edit.insert(document.uri, new vscode.Position(range.start.line, 0), validation);

        return edit;
    }

    private createXSSFix(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.WorkspaceEdit {
        const edit = new vscode.WorkspaceEdit();
        const line = document.lineAt(range.start.line);

        // Add HTML escaping
        if (document.languageId === 'python') {
            const newText = line.text.replace(
                /(\w+)/,
                'html.escape($1)'
            );
            edit.replace(document.uri, line.range, newText);

            // Add import if not present
            const firstLine = document.lineAt(0);
            if (!document.getText().includes('import html')) {
                edit.insert(document.uri, firstLine.range.start, 'import html\n');
            }
        }

        return edit;
    }

    private createBatchQueryFix(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.WorkspaceEdit {
        const edit = new vscode.WorkspaceEdit();

        // Add comment suggesting batch query
        const suggestion = `    # TODO: Replace with batch query to avoid N+1:\n    # orders = Order.objects.filter(user_id__in=[u.id for u in users])\n`;
        edit.insert(document.uri, new vscode.Position(range.start.line, 0), suggestion);

        return edit;
    }

    private createCachingFix(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.WorkspaceEdit {
        const edit = new vscode.WorkspaceEdit();

        // Add caching decorator or comment
        const cacheCode = `    # Add caching:\n    @cache.memoize(timeout=300)\n`;
        edit.insert(document.uri, new vscode.Position(range.start.line, 0), cacheCode);

        return edit;
    }

    private createARIAFix(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.WorkspaceEdit {
        const edit = new vscode.WorkspaceEdit();
        const line = document.lineAt(range.start.line);

        // Add aria-label attribute
        if (line.text.includes('<button')) {
            const newText = line.text.replace(
                /<button/,
                '<button aria-label="Button description"'
            );
            edit.replace(document.uri, line.range, newText);
        }

        return edit;
    }

    private createContrastFix(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.WorkspaceEdit {
        const edit = new vscode.WorkspaceEdit();

        // Add comment about WCAG contrast requirements
        const suggestion = `/* TODO: Improve color contrast to meet WCAG AA (4.5:1) or AAA (7:1) */\n`;
        edit.insert(document.uri, new vscode.Position(range.start.line, 0), suggestion);

        return edit;
    }
}
