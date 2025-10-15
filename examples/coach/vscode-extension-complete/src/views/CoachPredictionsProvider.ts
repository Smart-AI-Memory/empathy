import * as vscode from 'vscode';
import { AnalysisService } from '../services/AnalysisService';

export class CoachPredictionsProvider implements vscode.TreeDataProvider<PredictionItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<PredictionItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private predictions: any[] = [];

    constructor(private analysisService: AnalysisService) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    async updatePredictions(document: vscode.TextDocument): Promise<void> {
        try {
            this.predictions = await this.analysisService.getPredictions(document);
            this.refresh();
        } catch (error) {
            console.error('Failed to update predictions:', error);
        }
    }

    getTreeItem(element: PredictionItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: PredictionItem): PredictionItem[] {
        if (!element) {
            return this.predictions.map(p => {
                const icon = p.severity === 'ERROR' ? 'error' :
                             p.severity === 'WARNING' ? 'warning' : 'info';
                const confidencePercent = (p.confidence * 100).toFixed(0);

                return new PredictionItem(
                    `${p.issue} (~${p.timeframe}d, ${confidencePercent}%)`,
                    p.impact,
                    icon
                );
            });
        }

        return [];
    }
}

class PredictionItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        description: string,
        icon: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.tooltip = description;
        this.description = description;
        this.iconPath = new vscode.ThemeIcon(icon);
    }
}
