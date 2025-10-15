export interface WizardMetadata {
    id: string;
    name: string;
    description: string;
    category: WizardCategory;
    applicableLanguages: string[];
    icon: string;
    defaultEnabled: boolean;
}

export enum WizardCategory {
    SECURITY = 'Security',
    PERFORMANCE = 'Performance',
    ACCESSIBILITY = 'Accessibility',
    DEBUGGING = 'Debugging',
    TESTING = 'Testing',
    REFACTORING = 'Refactoring',
    DATABASE = 'Database',
    API = 'API',
    SCALING = 'Scaling',
    OBSERVABILITY = 'Observability',
    CICD = 'CI/CD',
    DOCUMENTATION = 'Documentation',
    COMPLIANCE = 'Compliance',
    MIGRATION = 'Migration',
    MONITORING = 'Monitoring',
    LOCALIZATION = 'Localization',
    CUSTOM = 'Custom'
}

export class WizardRegistry {
    private wizards: Map<string, WizardMetadata> = new Map();

    constructor() {
        this.registerBuiltInWizards();
    }

    private registerBuiltInWizards(): void {
        const wizards: WizardMetadata[] = [
            {
                id: 'SecurityWizard',
                name: 'Security Wizard',
                description: 'Detects security vulnerabilities including SQL injection, XSS, hardcoded secrets, and CSRF',
                category: WizardCategory.SECURITY,
                applicableLanguages: ['*'],
                icon: 'shield',
                defaultEnabled: true
            },
            {
                id: 'PerformanceWizard',
                name: 'Performance Wizard',
                description: 'Identifies performance issues like N+1 queries, memory leaks, and inefficient algorithms',
                category: WizardCategory.PERFORMANCE,
                applicableLanguages: ['*'],
                icon: 'dashboard',
                defaultEnabled: true
            },
            {
                id: 'AccessibilityWizard',
                name: 'Accessibility Wizard',
                description: 'Ensures WCAG 2.1 AA compliance, detects missing alt text, keyboard accessibility issues',
                category: WizardCategory.ACCESSIBILITY,
                applicableLanguages: ['html', 'javascript', 'typescript', 'jsx', 'tsx', 'vue'],
                icon: 'accessibility',
                defaultEnabled: true
            },
            {
                id: 'DebuggingWizard',
                name: 'Debugging Wizard',
                description: 'Helps debug complex issues by analyzing stack traces, logs, and runtime behavior',
                category: WizardCategory.DEBUGGING,
                applicableLanguages: ['*'],
                icon: 'bug',
                defaultEnabled: true
            },
            {
                id: 'TestingWizard',
                name: 'Testing Wizard',
                description: 'Suggests tests, identifies untested code paths, recommends test strategies',
                category: WizardCategory.TESTING,
                applicableLanguages: ['*'],
                icon: 'beaker',
                defaultEnabled: true
            },
            {
                id: 'RefactoringWizard',
                name: 'Refactoring Wizard',
                description: 'Identifies code smells, suggests refactoring opportunities, improves maintainability',
                category: WizardCategory.REFACTORING,
                applicableLanguages: ['*'],
                icon: 'symbol-method',
                defaultEnabled: true
            },
            {
                id: 'DatabaseWizard',
                name: 'Database Wizard',
                description: 'Optimizes queries, suggests indexes, detects schema issues',
                category: WizardCategory.DATABASE,
                applicableLanguages: ['sql', 'python', 'javascript', 'typescript', 'java', 'csharp'],
                icon: 'database',
                defaultEnabled: true
            },
            {
                id: 'APIWizard',
                name: 'API Wizard',
                description: 'Reviews API design, suggests REST/GraphQL best practices, validates OpenAPI specs',
                category: WizardCategory.API,
                applicableLanguages: ['*'],
                icon: 'symbol-interface',
                defaultEnabled: true
            },
            {
                id: 'ScalingWizard',
                name: 'Scaling Wizard',
                description: 'Predicts scaling bottlenecks, suggests architecture improvements for high load',
                category: WizardCategory.SCALING,
                applicableLanguages: ['*'],
                icon: 'graph',
                defaultEnabled: true
            },
            {
                id: 'ObservabilityWizard',
                name: 'Observability Wizard',
                description: 'Recommends logging, metrics, tracing strategies for production debugging',
                category: WizardCategory.OBSERVABILITY,
                applicableLanguages: ['*'],
                icon: 'eye',
                defaultEnabled: true
            },
            {
                id: 'CICDWizard',
                name: 'CI/CD Wizard',
                description: 'Optimizes pipelines, suggests deployment strategies, reviews Docker/K8s configs',
                category: WizardCategory.CICD,
                applicableLanguages: ['yaml', 'dockerfile', 'jenkinsfile', 'bash', 'shell'],
                icon: 'repo-forked',
                defaultEnabled: true
            },
            {
                id: 'DocumentationWizard',
                name: 'Documentation Wizard',
                description: 'Identifies missing docs, suggests improvements, generates API documentation',
                category: WizardCategory.DOCUMENTATION,
                applicableLanguages: ['*'],
                icon: 'book',
                defaultEnabled: true
            },
            {
                id: 'ComplianceWizard',
                name: 'Compliance Wizard',
                description: 'Checks GDPR, HIPAA, PCI-DSS compliance, identifies data privacy issues',
                category: WizardCategory.COMPLIANCE,
                applicableLanguages: ['*'],
                icon: 'law',
                defaultEnabled: true
            },
            {
                id: 'MigrationWizard',
                name: 'Migration Wizard',
                description: 'Assists with framework upgrades, language migrations, dependency updates',
                category: WizardCategory.MIGRATION,
                applicableLanguages: ['*'],
                icon: 'move',
                defaultEnabled: true
            },
            {
                id: 'MonitoringWizard',
                name: 'Monitoring Wizard',
                description: 'Reviews alerting strategies, suggests SLOs/SLIs, identifies monitoring gaps',
                category: WizardCategory.MONITORING,
                applicableLanguages: ['*'],
                icon: 'pulse',
                defaultEnabled: true
            },
            {
                id: 'LocalizationWizard',
                name: 'Localization Wizard',
                description: 'Detects hardcoded strings, suggests i18n strategies, validates translations',
                category: WizardCategory.LOCALIZATION,
                applicableLanguages: ['*'],
                icon: 'globe',
                defaultEnabled: true
            }
        ];

        wizards.forEach(wizard => this.register(wizard));
    }

    register(metadata: WizardMetadata): void {
        this.wizards.set(metadata.id, metadata);
    }

    unregister(wizardId: string): void {
        this.wizards.delete(wizardId);
    }

    getWizard(wizardId: string): WizardMetadata | undefined {
        return this.wizards.get(wizardId);
    }

    getAllWizards(): WizardMetadata[] {
        return Array.from(this.wizards.values());
    }

    getWizardsForLanguage(language: string): WizardMetadata[] {
        return this.getAllWizards().filter(wizard =>
            wizard.applicableLanguages.includes('*') ||
            wizard.applicableLanguages.includes(language)
        );
    }

    getWizardsByCategory(category: WizardCategory): WizardMetadata[] {
        return this.getAllWizards().filter(wizard => wizard.category === category);
    }

    getCollaborationWizards(scenario: string): string[] {
        const scenarios: Record<string, string[]> = {
            'payment': ['SecurityWizard', 'ComplianceWizard', 'PerformanceWizard'],
            'authentication': ['SecurityWizard', 'AccessibilityWizard', 'TestingWizard'],
            'api': ['APIWizard', 'SecurityWizard', 'DocumentationWizard', 'PerformanceWizard'],
            'database': ['DatabaseWizard', 'PerformanceWizard', 'SecurityWizard'],
            'frontend': ['AccessibilityWizard', 'PerformanceWizard', 'LocalizationWizard'],
            'deployment': ['CICDWizard', 'MonitoringWizard', 'ObservabilityWizard'],
            'scaling': ['ScalingWizard', 'PerformanceWizard', 'DatabaseWizard', 'MonitoringWizard'],
            'migration': ['MigrationWizard', 'TestingWizard', 'DocumentationWizard']
        };

        return scenarios[scenario.toLowerCase()] || [];
    }
}
