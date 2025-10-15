import * as vscode from 'vscode';
import { CoachLSPClient, WizardResult, MultiWizardResult, PredictedImpact } from '../lsp/CoachLSPClient';
import { WizardRegistry } from './WizardRegistry';
import { CacheService } from './CacheService';

export interface AnalysisResult {
    filePath: string;
    wizardId: string;
    result: WizardResult;
    timestamp: number;
}

export interface AnalysisStatistics {
    totalAnalyses: number;
    errors: number;
    warnings: number;
    infos: number;
    wizardCounts: Record<string, number>;
}

export class AnalysisService {
    private results: Map<string, AnalysisResult> = new Map();
    private lspClient: CoachLSPClient;
    private wizardRegistry: WizardRegistry;
    private cacheService: CacheService;

    constructor(
        lspClient: CoachLSPClient,
        wizardRegistry: WizardRegistry,
        cacheService: CacheService
    ) {
        this.lspClient = lspClient;
        this.wizardRegistry = wizardRegistry;
        this.cacheService = cacheService;
    }

    async analyzeWithWizard(
        document: vscode.TextDocument,
        wizardId: string,
        role: string = 'developer',
        task: string = '',
        context: string = ''
    ): Promise<WizardResult> {
        const filePath = document.uri.fsPath;
        const code = document.getText();

        // Check cache
        const cacheKey = this.generateCacheKey(filePath, wizardId, code);
        const cachedResult = this.cacheService.get(cacheKey);
        if (cachedResult) {
            return cachedResult as WizardResult;
        }

        // Run analysis
        const result = await this.lspClient.runWizard(
            wizardId,
            code,
            filePath,
            role,
            task,
            context
        );

        // Cache result
        this.cacheService.set(cacheKey, result);

        // Store result
        const analysisKey = `${filePath}:${wizardId}`;
        this.results.set(analysisKey, {
            filePath,
            wizardId,
            result,
            timestamp: Date.now()
        });

        return result;
    }

    async analyzeWithAllWizards(
        document: vscode.TextDocument,
        language: string
    ): Promise<WizardResult[]> {
        const applicableWizards = this.wizardRegistry.getWizardsForLanguage(language);
        const enabledWizards = this.getEnabledWizards();

        const wizardsToRun = applicableWizards.filter(w =>
            enabledWizards.includes(w.id)
        );

        if (wizardsToRun.length === 0) {
            return [];
        }

        const promises = wizardsToRun.map(wizard =>
            this.analyzeWithWizard(document, wizard.id).catch(error => {
                console.error(`Failed to run ${wizard.id}:`, error);
                return null;
            })
        );

        const results = await Promise.all(promises);
        return results.filter((r): r is WizardResult => r !== null);
    }

    async multiWizardAnalysis(
        document: vscode.TextDocument,
        wizards: string[],
        scenario: string = '',
        context: string = ''
    ): Promise<MultiWizardResult> {
        const filePath = document.uri.fsPath;
        const code = document.getText();

        // Check cache
        const cacheKey = this.generateCacheKey(filePath, wizards.join(','), code);
        const cachedResult = this.cacheService.get(cacheKey);
        if (cachedResult) {
            return cachedResult as MultiWizardResult;
        }

        // Run multi-wizard analysis
        const result = await this.lspClient.multiWizardReview(
            wizards,
            code,
            filePath,
            scenario,
            context
        );

        // Cache result
        this.cacheService.set(cacheKey, result);

        return result;
    }

    async getPredictions(
        document: vscode.TextDocument,
        timeframe: number = 60
    ): Promise<PredictedImpact[]> {
        const filePath = document.uri.fsPath;
        const code = document.getText();

        // Check cache
        const cacheKey = this.generateCacheKey(filePath, 'predictions', code);
        const cachedResult = this.cacheService.get(cacheKey);
        if (cachedResult) {
            return cachedResult as PredictedImpact[];
        }

        // Get predictions
        const predictions = await this.lspClient.predict(code, filePath, timeframe);

        // Cache result
        this.cacheService.set(cacheKey, predictions);

        return predictions;
    }

    getAnalysisResult(filePath: string, wizardId: string): AnalysisResult | undefined {
        return this.results.get(`${filePath}:${wizardId}`);
    }

    getFileAnalysisResults(filePath: string): AnalysisResult[] {
        return Array.from(this.results.values()).filter(r => r.filePath === filePath);
    }

    getAllAnalysisResults(): AnalysisResult[] {
        return Array.from(this.results.values());
    }

    clearResults(): void {
        this.results.clear();
    }

    clearFileResults(filePath: string): void {
        const keys = Array.from(this.results.keys()).filter(key =>
            key.startsWith(`${filePath}:`)
        );
        keys.forEach(key => this.results.delete(key));
    }

    getStatistics(): AnalysisStatistics {
        const results = this.getAllAnalysisResults();
        const errors = results.filter(r => r.result.severity === 'ERROR').length;
        const warnings = results.filter(r => r.result.severity === 'WARNING').length;
        const infos = results.filter(r => r.result.severity === 'INFO').length;

        const wizardCounts: Record<string, number> = {};
        results.forEach(r => {
            wizardCounts[r.wizardId] = (wizardCounts[r.wizardId] || 0) + 1;
        });

        return {
            totalAnalyses: results.length,
            errors,
            warnings,
            infos,
            wizardCounts
        };
    }

    private generateCacheKey(filePath: string, identifier: string, code: string): string {
        const codeHash = this.hashCode(code);
        return `${filePath}:${identifier}:${codeHash}`;
    }

    private hashCode(str: string): number {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return hash;
    }

    private getEnabledWizards(): string[] {
        const config = vscode.workspace.getConfiguration('coach');
        return config.get<string[]>('enabledWizards') || [];
    }
}
