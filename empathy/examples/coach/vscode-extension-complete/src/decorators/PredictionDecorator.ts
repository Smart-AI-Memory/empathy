import * as vscode from 'vscode';
import { AnalysisService } from '../services/AnalysisService';

export class PredictionDecorator implements vscode.Disposable {
    private decorationType: vscode.TextEditorDecorationType;
    private analysisService: AnalysisService;

    constructor(analysisService: AnalysisService) {
        this.analysisService = analysisService;

        // Create decoration type for predictions
        this.decorationType = vscode.window.createTextEditorDecorationType({
            gutterIconPath: vscode.Uri.parse('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSI4IiBjeT0iOCIgcj0iNyIgZmlsbD0iI2ZmYzEwNyIvPjwvc3ZnPg=='),
            gutterIconSize: 'contain',
            overviewRulerColor: '#ffc107',
            overviewRulerLane: vscode.OverviewRulerLane.Right
        });
    }

    async updateDecorations(editor: vscode.TextEditor): Promise<void> {
        const config = vscode.workspace.getConfiguration('coach');
        if (!config.get('enablePredictions') || !config.get('showGutterIcons')) {
            return;
        }

        try {
            const predictions = await this.analysisService.getPredictions(
                editor.document,
                config.get<number>('predictionTimeframe') || 60
            );

            const threshold = config.get<number>('predictionConfidenceThreshold') || 0.7;
            const significantPredictions = predictions.filter(p => p.confidence >= threshold);

            const decorations: vscode.DecorationOptions[] = significantPredictions.map(prediction => {
                const hoverMessage = new vscode.MarkdownString();
                hoverMessage.appendMarkdown(`**🔮 Level 4 Prediction** (${(prediction.confidence * 100).toFixed(0)}% confidence)\n\n`);
                hoverMessage.appendMarkdown(`**${prediction.issue}**\n\n`);
                hoverMessage.appendMarkdown(`Expected in ~${prediction.timeframe} days\n\n`);
                hoverMessage.appendMarkdown(`**Impact:** ${prediction.impact}\n\n`);
                hoverMessage.appendMarkdown(`**Preventive Action:** ${prediction.preventiveAction}`);

                return {
                    range: new vscode.Range(0, 0, 0, 0),
                    hoverMessage
                };
            });

            editor.setDecorations(this.decorationType, decorations);
        } catch (error) {
            console.error('Failed to update prediction decorations:', error);
        }
    }

    dispose(): void {
        this.decorationType.dispose();
    }
}
