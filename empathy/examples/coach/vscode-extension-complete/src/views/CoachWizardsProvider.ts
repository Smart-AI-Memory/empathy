import * as vscode from 'vscode';
import { WizardRegistry, WizardCategory } from '../services/WizardRegistry';

export class CoachWizardsProvider implements vscode.TreeDataProvider<WizardItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<WizardItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor(private wizardRegistry: WizardRegistry) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: WizardItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: WizardItem): WizardItem[] {
        if (!element) {
            // Root level - show categories
            const categories = Object.values(WizardCategory);
            return categories.map(category =>
                new WizardItem(category, vscode.TreeItemCollapsibleState.Collapsed, 'category')
            );
        } else if (element.type === 'category') {
            // Category level - show wizards
            const wizards = this.wizardRegistry.getWizardsByCategory(element.label as WizardCategory);
            return wizards.map(w =>
                new WizardItem(w.name, vscode.TreeItemCollapsibleState.None, 'wizard', w.description, w.icon)
            );
        }

        return [];
    }
}

class WizardItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'category' | 'wizard',
        description?: string,
        icon?: string
    ) {
        super(label, collapsibleState);
        this.tooltip = description;
        this.description = description;
        this.iconPath = icon ? new vscode.ThemeIcon(icon) : undefined;
    }
}
