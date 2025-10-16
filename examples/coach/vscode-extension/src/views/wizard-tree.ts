/**
 * Wizards Tree View Provider
 * Displays all 16 wizards in sidebar
 */

import * as vscode from 'vscode';
import { LanguageClient } from 'vscode-languageclient/node';

export class WizardsTreeProvider implements vscode.TreeDataProvider<WizardItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<WizardItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor(private client: LanguageClient) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: WizardItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: WizardItem): Promise<WizardItem[]> {
        if (!element) {
            // Root level: categories
            return [
                new WizardItem('Critical Infrastructure', '', vscode.TreeItemCollapsibleState.Expanded, 'category'),
                new WizardItem('Development Workflow', '', vscode.TreeItemCollapsibleState.Expanded, 'category'),
                new WizardItem('Architecture & Design', '', vscode.TreeItemCollapsibleState.Expanded, 'category'),
                new WizardItem('Infrastructure & Ops', '', vscode.TreeItemCollapsibleState.Expanded, 'category'),
                new WizardItem('Cross-Cutting Concerns', '', vscode.TreeItemCollapsibleState.Expanded, 'category'),
                new WizardItem('Team & Process', '', vscode.TreeItemCollapsibleState.Expanded, 'category')
            ];
        } else {
            // Wizards per category
            return this.getWizardsForCategory(element.label as string);
        }
    }

    private getWizardsForCategory(category: string): WizardItem[] {
        const wizardMap: { [key: string]: Array<{ name: string; icon: string; description: string }> } = {
            'Critical Infrastructure': [
                { name: 'SecurityWizard', icon: 'shield', description: 'STRIDE threat modeling, penetration testing' },
                { name: 'ComplianceWizard', icon: 'law', description: 'SOC 2, HIPAA, GDPR audit preparation' }
            ],
            'Development Workflow': [
                { name: 'DebuggingWizard', icon: 'bug', description: 'Root cause analysis, regression tests' },
                { name: 'TestingWizard', icon: 'beaker', description: 'Test strategy, coverage analysis' },
                { name: 'RefactoringWizard', icon: 'code', description: 'Code quality, technical debt' },
                { name: 'PerformanceWizard', icon: 'pulse', description: 'Profiling, optimization, scaling' }
            ],
            'Architecture & Design': [
                { name: 'DesignReviewWizard', icon: 'symbol-class', description: 'Architecture evaluation' },
                { name: 'APIWizard', icon: 'symbol-interface', description: 'OpenAPI specs, REST design' },
                { name: 'DatabaseWizard', icon: 'database', description: 'Schema design, query optimization' }
            ],
            'Infrastructure & Ops': [
                { name: 'DevOpsWizard', icon: 'rocket', description: 'CI/CD, Terraform, Kubernetes' },
                { name: 'MonitoringWizard', icon: 'graph', description: 'SLOs, alerting, incident response' }
            ],
            'Cross-Cutting Concerns': [
                { name: 'DocumentationWizard', icon: 'book', description: 'Technical writing, handoff guides' },
                { name: 'AccessibilityWizard', icon: 'accessibility', description: 'WCAG compliance, a11y' },
                { name: 'LocalizationWizard', icon: 'globe', description: 'i18n/L10n, translations' }
            ],
            'Team & Process': [
                { name: 'OnboardingWizard', icon: 'mortar-board', description: 'Knowledge transfer, learning paths' },
                { name: 'RetrospectiveWizard', icon: 'feedback', description: 'Post-mortems, process improvement' }
            ]
        };

        const wizards = wizardMap[category] || [];
        return wizards.map(w => new WizardItem(
            w.name,
            w.description,
            vscode.TreeItemCollapsibleState.None,
            'wizard',
            w.icon
        ));
    }
}

class WizardItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        private description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'category' | 'wizard',
        private icon?: string
    ) {
        super(label, collapsibleState);
        this.tooltip = description;
        this.description = type === 'wizard' ? description : '';

        if (type === 'wizard') {
            this.contextValue = 'wizard';
            this.command = {
                command: 'coach.runWizard',
                title: 'Run Wizard',
                arguments: [label]
            };

            if (icon) {
                this.iconPath = new vscode.ThemeIcon(icon);
            }
        }
    }
}
