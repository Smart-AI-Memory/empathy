/**
 * PromptEnhancer - Enhances XML prompts with refined context
 *
 * Takes user's refined answers from Socratic questioning and injects them
 * into XML-enhanced prompts for more targeted LLM output.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

/**
 * Refinement context from user answers
 */
export interface RefinementContext {
    focus?: string;
    depth?: string;
    scope?: string;
    testType?: string;
    coverage?: string;
    goal?: string;
    style?: string;
    priority?: string;
    [key: string]: string | string[] | undefined;
}

/**
 * XML prompt structure
 */
export interface XMLPrompt {
    role: string;
    goal: string;
    context?: Record<string, string>;
    instructions: string[];
    constraints?: string[];
    outputFormat?: string;
}

/**
 * Enhanced prompt result
 */
export interface EnhancedPrompt {
    xmlPrompt: XMLPrompt;
    xmlString: string;
    enhancements: string[];
}

/**
 * Workflow prompt templates
 */
const WORKFLOW_PROMPTS: Record<string, XMLPrompt> = {
    'code-review': {
        role: 'Senior Code Reviewer',
        goal: 'Review the provided code',
        instructions: [
            'Analyze code quality and structure',
            'Identify potential issues and bugs',
            'Suggest improvements',
            'Check for best practices'
        ],
        constraints: [
            'Be constructive in feedback',
            'Prioritize actionable suggestions'
        ]
    },
    'test-gen': {
        role: 'Test Engineer',
        goal: 'Generate comprehensive tests',
        instructions: [
            'Analyze code for testable components',
            'Generate appropriate test cases',
            'Include edge cases',
            'Follow testing best practices'
        ],
        constraints: [
            'Use the project\'s testing framework',
            'Follow existing test patterns'
        ]
    },
    'refactor-plan': {
        role: 'Software Architect',
        goal: 'Plan code refactoring',
        instructions: [
            'Analyze current code structure',
            'Identify areas for improvement',
            'Propose refactoring steps',
            'Consider impact on existing code'
        ],
        constraints: [
            'Minimize breaking changes',
            'Maintain backwards compatibility where possible'
        ]
    },
    'security-audit': {
        role: 'Security Engineer',
        goal: 'Audit code for security vulnerabilities',
        instructions: [
            'Check for OWASP Top 10 vulnerabilities',
            'Identify potential security risks',
            'Review authentication and authorization',
            'Check for data exposure'
        ],
        constraints: [
            'Follow security best practices',
            'Provide severity ratings'
        ]
    },
    'bug-predict': {
        role: 'Quality Assurance Engineer',
        goal: 'Predict potential bugs',
        instructions: [
            'Analyze code patterns',
            'Identify bug-prone areas',
            'Check for common error patterns',
            'Review error handling'
        ]
    },
    'perf-audit': {
        role: 'Performance Engineer',
        goal: 'Analyze code performance',
        instructions: [
            'Identify performance bottlenecks',
            'Check for memory issues',
            'Review algorithm efficiency',
            'Suggest optimizations'
        ]
    },
    'doc-gen': {
        role: 'Technical Writer',
        goal: 'Generate documentation',
        instructions: [
            'Analyze code structure',
            'Document functions and classes',
            'Create usage examples',
            'Add inline comments where helpful'
        ]
    },
    'pro-review': {
        role: 'Principal Software Engineer',
        goal: 'Perform comprehensive code review',
        instructions: [
            'Review architecture and design',
            'Check code quality',
            'Analyze security implications',
            'Evaluate maintainability'
        ],
        constraints: [
            'Provide actionable feedback',
            'Rate severity of issues'
        ]
    }
};

/**
 * Focus-specific instruction enhancements
 */
const FOCUS_ENHANCEMENTS: Record<string, string[]> = {
    'security': [
        'Prioritize security vulnerability detection',
        'Check for injection attacks (SQL, XSS, command)',
        'Review authentication and session handling',
        'Flag any hardcoded credentials or secrets'
    ],
    'performance': [
        'Identify O(n²) or worse algorithms',
        'Check for memory leaks and inefficient patterns',
        'Review database query efficiency',
        'Suggest caching opportunities'
    ],
    'maintainability': [
        'Evaluate code readability and organization',
        'Check for proper abstraction levels',
        'Review naming conventions',
        'Assess test coverage needs'
    ],
    'best-practices': [
        'Check adherence to language idioms',
        'Review error handling patterns',
        'Evaluate documentation quality',
        'Assess code reusability'
    ]
};

/**
 * Depth-specific constraints
 */
const DEPTH_CONSTRAINTS: Record<string, string[]> = {
    'quick': [
        'Focus on high-impact issues only',
        'Skip minor style issues',
        'Limit to 5 key findings'
    ],
    'standard': [
        'Balance thoroughness with efficiency',
        'Include moderate detail in findings',
        'Aim for 10-15 key findings'
    ],
    'deep': [
        'Perform line-by-line analysis',
        'Include all findings regardless of severity',
        'Provide detailed explanations for each issue'
    ]
};

/**
 * PromptEnhancer - Singleton service for enhancing prompts
 */
export class PromptEnhancer {
    private static instance: PromptEnhancer;

    private constructor() {}

    static getInstance(): PromptEnhancer {
        if (!PromptEnhancer.instance) {
            PromptEnhancer.instance = new PromptEnhancer();
        }
        return PromptEnhancer.instance;
    }

    /**
     * Enhance a workflow prompt with refined context
     */
    enhance(workflowName: string, refinement: RefinementContext): EnhancedPrompt {
        const basePrompt = WORKFLOW_PROMPTS[workflowName] || this.createGenericPrompt(workflowName);
        const enhancements: string[] = [];

        // Clone the base prompt
        const enhancedPrompt: XMLPrompt = {
            role: basePrompt.role,
            goal: basePrompt.goal,
            context: {},
            instructions: [...basePrompt.instructions],
            constraints: [...(basePrompt.constraints || [])],
            outputFormat: basePrompt.outputFormat
        };

        // Enhance goal based on focus
        if (refinement.focus && refinement.focus !== 'all') {
            enhancedPrompt.goal = `${basePrompt.goal} with focus on ${refinement.focus}`;
            enhancedPrompt.context!.user_focus = refinement.focus;
            enhancements.push(`Added focus: ${refinement.focus}`);

            // Add focus-specific instructions
            const focusInstructions = FOCUS_ENHANCEMENTS[refinement.focus];
            if (focusInstructions) {
                enhancedPrompt.instructions = [
                    ...focusInstructions,
                    ...enhancedPrompt.instructions
                ];
                enhancements.push(`Added ${focusInstructions.length} focus-specific instructions`);
            }
        }

        // Add depth context
        if (refinement.depth) {
            enhancedPrompt.context!.depth = refinement.depth;
            enhancements.push(`Added depth: ${refinement.depth}`);

            // Add depth-specific constraints
            const depthConstraints = DEPTH_CONSTRAINTS[refinement.depth];
            if (depthConstraints) {
                enhancedPrompt.constraints = [
                    ...enhancedPrompt.constraints!,
                    ...depthConstraints
                ];
                enhancements.push(`Added ${depthConstraints.length} depth-specific constraints`);
            }
        }

        // Add scope context
        if (refinement.scope) {
            enhancedPrompt.context!.scope = refinement.scope;
            enhancements.push(`Added scope: ${refinement.scope}`);
        }

        // Add test generation specifics
        if (refinement.testType) {
            enhancedPrompt.context!.test_type = refinement.testType;
            this.addTestTypeInstructions(enhancedPrompt, refinement.testType);
            enhancements.push(`Added test type: ${refinement.testType}`);
        }

        if (refinement.coverage) {
            enhancedPrompt.context!.coverage_target = refinement.coverage;
            this.addCoverageConstraints(enhancedPrompt, refinement.coverage);
            enhancements.push(`Added coverage target: ${refinement.coverage}`);
        }

        // Add refactoring goal
        if (refinement.goal) {
            enhancedPrompt.context!.refactoring_goal = refinement.goal;
            this.addRefactoringInstructions(enhancedPrompt, refinement.goal);
            enhancements.push(`Added refactoring goal: ${refinement.goal}`);
        }

        // Add documentation style
        if (refinement.style) {
            enhancedPrompt.context!.doc_style = refinement.style;
            this.addDocStyleInstructions(enhancedPrompt, refinement.style);
            enhancements.push(`Added documentation style: ${refinement.style}`);
        }

        // Add priority filter
        if (refinement.priority) {
            enhancedPrompt.context!.priority_filter = refinement.priority;
            this.addPriorityConstraints(enhancedPrompt, refinement.priority);
            enhancements.push(`Added priority filter: ${refinement.priority}`);
        }

        return {
            xmlPrompt: enhancedPrompt,
            xmlString: this.toXMLString(enhancedPrompt),
            enhancements
        };
    }

    /**
     * Convert prompt to XML string
     */
    toXMLString(prompt: XMLPrompt): string {
        let xml = '<prompt>\n';
        xml += `  <role>${this.escapeXml(prompt.role)}</role>\n`;
        xml += `  <goal>${this.escapeXml(prompt.goal)}</goal>\n`;

        if (prompt.context && Object.keys(prompt.context).length > 0) {
            xml += '  <context>\n';
            for (const [key, value] of Object.entries(prompt.context)) {
                xml += `    <${key}>${this.escapeXml(value)}</${key}>\n`;
            }
            xml += '  </context>\n';
        }

        xml += '  <instructions>\n';
        for (const instruction of prompt.instructions) {
            xml += `    <step>${this.escapeXml(instruction)}</step>\n`;
        }
        xml += '  </instructions>\n';

        if (prompt.constraints && prompt.constraints.length > 0) {
            xml += '  <constraints>\n';
            for (const constraint of prompt.constraints) {
                xml += `    <rule>${this.escapeXml(constraint)}</rule>\n`;
            }
            xml += '  </constraints>\n';
        }

        if (prompt.outputFormat) {
            xml += `  <output_format>${this.escapeXml(prompt.outputFormat)}</output_format>\n`;
        }

        xml += '</prompt>';
        return xml;
    }

    /**
     * Create a generic prompt for unknown workflows
     */
    private createGenericPrompt(workflowName: string): XMLPrompt {
        return {
            role: 'AI Assistant',
            goal: `Execute the ${workflowName} workflow`,
            instructions: [
                'Analyze the provided context',
                'Execute the requested task',
                'Provide clear and actionable output'
            ]
        };
    }

    /**
     * Add test type specific instructions
     */
    private addTestTypeInstructions(prompt: XMLPrompt, testType: string): void {
        switch (testType) {
            case 'unit':
                prompt.instructions.unshift(
                    'Focus on testing individual functions and methods',
                    'Mock external dependencies',
                    'Test one unit of functionality per test'
                );
                break;
            case 'integration':
                prompt.instructions.unshift(
                    'Test component interactions',
                    'Verify data flow between modules',
                    'Test with real dependencies where practical'
                );
                break;
            case 'edge-cases':
                prompt.instructions.unshift(
                    'Focus on boundary conditions',
                    'Test null/undefined inputs',
                    'Test maximum and minimum values',
                    'Test error conditions'
                );
                break;
        }
    }

    /**
     * Add coverage specific constraints
     */
    private addCoverageConstraints(prompt: XMLPrompt, coverage: string): void {
        switch (coverage) {
            case 'critical':
                prompt.constraints = prompt.constraints || [];
                prompt.constraints.push(
                    'Focus only on critical code paths',
                    'Prioritize error handling and main flows'
                );
                break;
            case '80':
                prompt.constraints = prompt.constraints || [];
                prompt.constraints.push(
                    'Target 80% line coverage',
                    'Include happy path and common error cases'
                );
                break;
            case 'comprehensive':
                prompt.constraints = prompt.constraints || [];
                prompt.constraints.push(
                    'Maximize test coverage',
                    'Include all edge cases and error paths',
                    'Test all public methods and properties'
                );
                break;
        }
    }

    /**
     * Add refactoring goal instructions
     */
    private addRefactoringInstructions(prompt: XMLPrompt, goal: string): void {
        switch (goal) {
            case 'complexity':
                prompt.instructions.unshift(
                    'Identify high cyclomatic complexity',
                    'Suggest function extraction',
                    'Simplify nested conditionals'
                );
                break;
            case 'performance':
                prompt.instructions.unshift(
                    'Profile for performance bottlenecks',
                    'Suggest algorithm improvements',
                    'Identify unnecessary computations'
                );
                break;
            case 'patterns':
                prompt.instructions.unshift(
                    'Identify applicable design patterns',
                    'Suggest structural improvements',
                    'Improve code organization'
                );
                break;
            case 'modernize':
                prompt.instructions.unshift(
                    'Update to latest language features',
                    'Replace deprecated APIs',
                    'Adopt modern coding conventions'
                );
                break;
        }
    }

    /**
     * Add documentation style instructions
     */
    private addDocStyleInstructions(prompt: XMLPrompt, style: string): void {
        switch (style) {
            case 'api':
                prompt.instructions.unshift(
                    'Generate JSDoc/docstring format',
                    'Document parameters and return types',
                    'Include usage examples'
                );
                prompt.outputFormat = 'API reference documentation';
                break;
            case 'tutorial':
                prompt.instructions.unshift(
                    'Create step-by-step guides',
                    'Include practical examples',
                    'Explain concepts progressively'
                );
                prompt.outputFormat = 'Tutorial-style documentation';
                break;
            case 'readme':
                prompt.instructions.unshift(
                    'Create project overview',
                    'Include installation steps',
                    'Add quick start examples'
                );
                prompt.outputFormat = 'README.md format';
                break;
        }
    }

    /**
     * Add priority filter constraints
     */
    private addPriorityConstraints(prompt: XMLPrompt, priority: string): void {
        prompt.constraints = prompt.constraints || [];
        switch (priority) {
            case 'critical':
                prompt.constraints.push(
                    'Only report blocking issues',
                    'Skip minor suggestions and style issues'
                );
                break;
            case 'important':
                prompt.constraints.push(
                    'Report important and critical issues',
                    'Skip minor style suggestions'
                );
                break;
            case 'all':
                prompt.constraints.push(
                    'Include all findings',
                    'Report suggestions and minor issues'
                );
                break;
        }
    }

    /**
     * Escape XML special characters
     */
    private escapeXml(str: string): string {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;');
    }

    /**
     * Get base prompt for a workflow
     */
    getBasePrompt(workflowName: string): XMLPrompt | undefined {
        return WORKFLOW_PROMPTS[workflowName];
    }

    /**
     * List all workflows with prompt templates
     */
    getAvailableWorkflows(): string[] {
        return Object.keys(WORKFLOW_PROMPTS);
    }
}
