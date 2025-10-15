import * as vscode from 'vscode';
import { AnalysisService } from '../services/AnalysisService';

export class CoachResultsProvider implements vscode.TreeDataProvider<ResultItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<ResultItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor(private analysisService: AnalysisService) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ResultItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ResultItem): ResultItem[] {
        if (!element) {
            // Root level - group by file
            const results = this.analysisService.getAllAnalysisResults();
            const fileGroups = new Map<string, typeof results>();

            results.forEach(r => {
                if (!fileGroups.has(r.filePath)) {
                    fileGroups.set(r.filePath, []);
                }
                fileGroups.get(r.filePath)!.push(r);
            });

            return Array.from(fileGroups.entries()).map(([filePath, results]) => {
                const fileName = filePath.split('/').pop() || filePath;
                const errorCount = results.filter(r => r.result.severity === 'ERROR').length;
                const warningCount = results.filter(r => r.result.severity === 'WARNING').length;

                return new ResultItem(
                    `${fileName} (${errorCount}E, ${warningCount}W)`,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'file',
                    filePath,
                    results
                );
            });
        } else if (element.type === 'file' && element.children) {
            // File level - show individual wizard results
            return element.children.map(r => {
                const icon = r.result.severity === 'ERROR' ? '🔴' :
                             r.result.severity === 'WARNING' ? '🟡' : '🔵';

                return new ResultItem(
                    `${icon} ${r.wizardId}`,
                    vscode.TreeItemCollapsibleState.None,
                    'result',
                    r.filePath,
                    undefined,
                    r.result.diagnosis
                );
            });
        }

        return [];
    }
}

class ResultItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'file' | 'result',
        public readonly filePath: string,
        public readonly children?: any[],
        public readonly description?: string
    ) {
        super(label, collapsibleState);
        this.tooltip = description;
        this.contextValue = type;

        if (type === 'result') {
            this.command = {
                command: 'vscode.open',
                title: 'Open File',
                arguments: [vscode.Uri.file(filePath)]
            };
        }
    }
}
