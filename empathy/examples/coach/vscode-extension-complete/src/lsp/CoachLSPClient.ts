import * as vscode from 'vscode';
import * as path from 'path';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

export interface WizardResult {
    wizard: string;
    diagnosis: string;
    severity: 'ERROR' | 'WARNING' | 'INFO';
    recommendations: string[];
    codeExamples: CodeExample[];
    estimatedTime?: string;
    references: string[];
}

export interface CodeExample {
    before?: string;
    after: string;
    explanation: string;
}

export interface MultiWizardResult {
    scenario: string;
    wizards: string[];
    results: WizardResult[];
    collaboration: CollaborationInfo[];
    summary: string;
}

export interface CollaborationInfo {
    wizards: string[];
    insight: string;
}

export interface PredictedImpact {
    issue: string;
    timeframe: number;
    severity: 'ERROR' | 'WARNING' | 'INFO';
    impact: string;
    preventiveAction: string;
    confidence: number;
}

export interface HealthStatus {
    status: string;
    version: string;
    uptime: number;
}

export class CoachLSPClient {
    private client: LanguageClient | undefined;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    async start(): Promise<void> {
        const config = vscode.workspace.getConfiguration('coach');
        const pythonPath = config.get<string>('pythonPath') || 'python';
        const serverScriptPath = config.get<string>('serverScriptPath');

        if (!serverScriptPath) {
            throw new Error('Coach LSP server script path not configured. Please set coach.serverScriptPath in settings.');
        }

        // Server options
        const serverOptions: ServerOptions = {
            command: pythonPath,
            args: [serverScriptPath],
            transport: TransportKind.stdio
        };

        // Client options
        const clientOptions: LanguageClientOptions = {
            documentSelector: [
                { scheme: 'file', language: 'python' },
                { scheme: 'file', language: 'javascript' },
                { scheme: 'file', language: 'typescript' },
                { scheme: 'file', language: 'java' },
                { scheme: 'file', language: 'go' },
                { scheme: 'file', language: 'rust' },
                { scheme: 'file', language: 'csharp' },
                { scheme: 'file', language: 'php' },
                { scheme: 'file', language: 'ruby' }
            ],
            synchronize: {
                fileEvents: vscode.workspace.createFileSystemWatcher('**/*')
            }
        };

        // Create language client
        this.client = new LanguageClient(
            'coachLanguageServer',
            'Coach Language Server',
            serverOptions,
            clientOptions
        );

        // Start the client
        await this.client.start();

        console.log('Coach LSP client started');

        // Perform health check
        try {
            const health = await this.healthCheck();
            console.log(`LSP server health: ${health.status} (version ${health.version})`);
        } catch (error) {
            console.warn('Health check failed:', error);
        }
    }

    async stop(): Promise<void> {
        if (this.client) {
            await this.client.stop();
            this.client = undefined;
        }
    }

    async restart(): Promise<void> {
        await this.stop();
        await this.start();
    }

    async runWizard(
        wizardName: string,
        code: string,
        filePath: string,
        role: string = 'developer',
        task: string = '',
        context: string = ''
    ): Promise<WizardResult> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest('workspace/executeCommand', {
            command: 'coach/runWizard',
            arguments: [
                wizardName,
                {
                    code,
                    filePath,
                    role,
                    task,
                    context
                }
            ]
        });

        return result as WizardResult;
    }

    async multiWizardReview(
        wizards: string[],
        code: string,
        filePath: string,
        scenario: string = '',
        context: string = ''
    ): Promise<MultiWizardResult> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest('workspace/executeCommand', {
            command: 'coach/multiWizardReview',
            arguments: [
                wizards,
                {
                    code,
                    filePath,
                    scenario,
                    context
                }
            ]
        });

        return result as MultiWizardResult;
    }

    async predict(
        code: string,
        filePath: string,
        timeframe: number = 60
    ): Promise<PredictedImpact[]> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest('workspace/executeCommand', {
            command: 'coach/predict',
            arguments: [
                {
                    code,
                    filePath,
                    timeframe
                }
            ]
        });

        return result as PredictedImpact[];
    }

    async healthCheck(): Promise<HealthStatus> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest('workspace/executeCommand', {
            command: 'coach/healthCheck',
            arguments: []
        });

        return result as HealthStatus;
    }

    isRunning(): boolean {
        return this.client !== undefined;
    }
}
