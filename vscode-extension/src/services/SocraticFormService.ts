/**
 * SocraticFormService - LLM-powered conversational forms
 *
 * Uses a Socratic approach to refine user intent before execution.
 * Supports three form types:
 * - plan-refinement: Complex implementation planning
 * - workflow-customization: Modifying command chains
 * - learning-mode: Tutorial and progressive skill building
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';

/**
 * Form types supported by the Socratic service
 */
export type FormType = 'plan-refinement' | 'workflow-customization' | 'learning-mode' | 'general' | 'agent-design';

/**
 * A single message in the conversation
 */
export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
    options?: string[]; // For multiple choice responses
}

/**
 * Conversation state
 */
export interface ConversationState {
    formType: FormType;
    messages: ChatMessage[];
    context: Record<string, any>;
    isComplete: boolean;
    result?: any;
}

/**
 * Form configuration
 */
interface FormConfig {
    systemPrompt: string;
    initialQuestion: string;
    maxTurns: number;
}

/**
 * XML-enhanced prompt template for structured LLM interactions
 */
function buildXMLPrompt(config: {
    role: string;
    goal: string;
    instructions: string[];
    constraints: string[];
    outputFormat?: string;
}): string {
    return `<prompt>
  <role>${config.role}</role>
  <goal>${config.goal}</goal>
  <instructions>
${config.instructions.map(i => `    <step>${i}</step>`).join('\n')}
  </instructions>
  <constraints>
${config.constraints.map(c => `    <rule>${c}</rule>`).join('\n')}
  </constraints>
  ${config.outputFormat ? `<output_format>${config.outputFormat}</output_format>` : ''}
  <method>socratic</method>
</prompt>`;
}

const FORM_CONFIGS: Record<FormType, FormConfig> = {
    'plan-refinement': {
        systemPrompt: buildXMLPrompt({
            role: 'Senior Software Architect',
            goal: 'Help user plan implementation using the Socratic method',
            instructions: [
                'Ask ONE clarifying question at a time',
                'Understand what they are building and why',
                'Identify constraints, requirements, and dependencies',
                'Explore trade-offs between different approaches',
                'When ready, provide structured implementation plan'
            ],
            constraints: [
                'Be concise - max 2-3 sentences per response',
                'Focus on actionable next steps',
                'Avoid over-engineering suggestions',
                'Consider existing codebase patterns'
            ],
            outputFormat: 'markdown with headers and bullet points for final plan'
        }),
        initialQuestion: 'What are you trying to build or implement? Give me a brief description.',
        maxTurns: 10,
    },
    'workflow-customization': {
        systemPrompt: buildXMLPrompt({
            role: 'Empathy Framework Configuration Expert',
            goal: 'Help user customize workflow chains and automation',
            instructions: [
                'Identify which workflow they want to modify',
                'Understand the desired command sequence',
                'Determine scope: project-specific or global',
                'Validate the workflow chain makes sense',
                'Generate YAML configuration when complete'
            ],
            constraints: [
                'Use only valid workflow names: morning, ship, fix-all, code-review, security-audit, test-gen, refactor-plan, health-check',
                'Keep chains under 5 commands for performance',
                'Suggest keyboard shortcuts where applicable'
            ],
            outputFormat: 'YAML configuration block in code fence'
        }),
        initialQuestion: 'Which workflow would you like to customize? You can also describe the flow you\'re trying to create.',
        maxTurns: 6,
    },
    'learning-mode': {
        systemPrompt: buildXMLPrompt({
            role: 'Friendly Empathy Framework Tutor',
            goal: 'Guide user through learning features progressively using Socratic questioning',
            instructions: [
                'Assess user experience level first',
                'Start with foundational concepts',
                'Introduce features one at a time',
                'Provide keyboard shortcuts for each feature',
                'Offer to run demos when appropriate',
                'Build on previous knowledge progressively'
            ],
            constraints: [
                'Use encouraging, supportive language',
                'Never overwhelm with too much information at once',
                'Always provide the keyboard shortcut: Ctrl+Shift+E + key',
                'Celebrate small wins'
            ],
            outputFormat: 'conversational with inline code for shortcuts'
        }),
        initialQuestion: 'Welcome to Empathy Framework! Have you used code quality tools before, or is this your first time?',
        maxTurns: 15,
    },
    'general': {
        systemPrompt: buildXMLPrompt({
            role: 'Empathy Framework Assistant',
            goal: 'Answer questions about code quality, workflows, and best practices',
            instructions: [
                'Understand the user question clearly',
                'Provide concise, practical answers',
                'Include relevant commands or shortcuts',
                'Suggest next steps when appropriate'
            ],
            constraints: [
                'Be concise - aim for clarity over completeness',
                'Focus on Empathy Framework features',
                'Provide examples when helpful'
            ]
        }),
        initialQuestion: 'How can I help you with Empathy Framework today?',
        maxTurns: 20,
    },
    'agent-design': {
        systemPrompt: buildXMLPrompt({
            role: 'AI Agent Architect',
            goal: 'Help design multi-agent workflows using CrewAI/LangGraph patterns',
            instructions: [
                'Understand the complex task to be accomplished',
                'Identify distinct expertise areas needed',
                'Suggest agent roles with clear responsibilities',
                'Design agent collaboration patterns (sequential, parallel, hierarchical)',
                'Generate XML-enhanced prompts for each agent',
                'Consider cost optimization - use cheaper models for simple tasks'
            ],
            constraints: [
                'Keep crews to 3-5 agents maximum for manageability',
                'Each agent should have a single clear responsibility',
                'Prompts should follow XML-enhanced structure',
                'Consider model tier routing: cheap (Haiku) for simple, capable (Sonnet) for complex, premium (Opus) for synthesis',
                'Validate task dependencies before suggesting parallel execution'
            ],
            outputFormat: 'YAML crew config + XML prompts for each agent in code fences'
        }),
        initialQuestion: 'What complex task do you want to accomplish with a multi-agent crew? Describe the overall goal and any specific requirements.',
        maxTurns: 12,
    },
};

/**
 * SocraticFormService - Handles LLM-powered conversational forms
 */
export class SocraticFormService {
    private static instance: SocraticFormService;
    private conversations: Map<string, ConversationState> = new Map();
    private context: vscode.ExtensionContext | null = null;

    private constructor() {}

    static getInstance(): SocraticFormService {
        if (!SocraticFormService.instance) {
            SocraticFormService.instance = new SocraticFormService();
        }
        return SocraticFormService.instance;
    }

    /**
     * Initialize with extension context for state persistence
     */
    initialize(context: vscode.ExtensionContext): void {
        this.context = context;
        this.loadPersistedConversations();
    }

    /**
     * Start an interactive Socratic form session with QuickPick UI
     */
    async startForm(
        formType: FormType,
        options: { mode?: string; initialContext?: string } = {}
    ): Promise<void> {
        const conversationId = `${formType}-${Date.now()}`;
        const config = FORM_CONFIGS[formType];

        // Show initial question
        await vscode.window.showInformationMessage(
            config.initialQuestion,
            { modal: false }
        );

        // Start interactive input loop
        let turnCount = 0;
        const maxTurns = config.maxTurns;
        const messages: ChatMessage[] = [
            { role: 'system', content: config.systemPrompt, timestamp: Date.now() }
        ];

        // Add mode context if provided
        if (options.mode) {
            messages.push({
                role: 'user',
                content: `I want to use ${options.mode} mode. ${options.initialContext || ''}`,
                timestamp: Date.now()
            });
        }

        while (turnCount < maxTurns) {
            // Get user input
            const userInput = await vscode.window.showInputBox({
                title: `${this.getFormTitle(formType)} (${turnCount + 1}/${maxTurns})`,
                prompt: turnCount === 0 ? config.initialQuestion : 'Your response',
                placeHolder: 'Type your response...',
                ignoreFocusOut: true
            });

            if (!userInput) {
                // User cancelled
                const action = await vscode.window.showQuickPick(
                    ['Continue conversation', 'End and summarize', 'Cancel'],
                    { title: 'What would you like to do?' }
                );

                if (action === 'Cancel') {
                    return;
                } else if (action === 'End and summarize') {
                    break;
                }
                continue;
            }

            messages.push({ role: 'user', content: userInput, timestamp: Date.now() });
            turnCount++;

            // Get LLM response (or fallback)
            const response = await this.generateResponse(messages, formType);
            messages.push({ role: 'assistant', content: response, timestamp: Date.now() });

            // Show response in output channel or information message
            const outputChannel = vscode.window.createOutputChannel('Empathy Agent Designer');
            outputChannel.clear();
            outputChannel.appendLine(`=== ${this.getFormTitle(formType)} ===\n`);
            outputChannel.appendLine(response);
            outputChannel.show(true);

            // Check for completion signals
            if (this.detectCompletion(response, formType)) {
                const result = this.extractResult(response, formType);
                if (result) {
                    // Offer to copy or save the result
                    const action = await vscode.window.showQuickPick(
                        [
                            { label: '$(copy) Copy to Clipboard', value: 'copy' },
                            { label: '$(new-file) Open in New File', value: 'file' },
                            { label: '$(check) Done', value: 'done' }
                        ],
                        { title: 'What would you like to do with the result?' }
                    );

                    if (action?.value === 'copy') {
                        await vscode.env.clipboard.writeText(result);
                        vscode.window.showInformationMessage('Copied to clipboard!');
                    } else if (action?.value === 'file') {
                        const doc = await vscode.workspace.openTextDocument({
                            content: result,
                            language: 'yaml'
                        });
                        await vscode.window.showTextDocument(doc);
                    }
                }
                break;
            }
        }
    }

    /**
     * Get display title for form type
     */
    private getFormTitle(formType: FormType): string {
        const titles: Record<FormType, string> = {
            'plan-refinement': 'Plan Refinement',
            'workflow-customization': 'Workflow Customization',
            'learning-mode': 'Learning Mode',
            'general': 'Empathy Assistant',
            'agent-design': 'Agent Workflow Designer'
        };
        return titles[formType] || formType;
    }

    /**
     * Generate LLM response or fallback
     */
    private async generateResponse(messages: ChatMessage[], formType: FormType): Promise<string> {
        try {
            // Try to use LLMChatService
            const llmService = await import('./LLMChatService');
            const service = llmService.LLMChatService.getInstance();

            const response = await service.chat(
                messages.map(m => ({ role: m.role, content: m.content })),
                { maxTokens: 2048, temperature: 0.7 }
            );

            return response.content;
        } catch (error) {
            // Return contextual fallback based on form type
            return this.getFormFallbackResponse(formType, messages);
        }
    }

    /**
     * Get fallback response for interactive form when LLM unavailable
     */
    private getFormFallbackResponse(formType: FormType, messages: ChatMessage[]): string {
        const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
        const userContent = lastUserMessage?.content.toLowerCase() || '';

        if (formType === 'agent-design') {
            if (userContent.includes('crew') || userContent.includes('team')) {
                return `Based on your requirements, I suggest a crew structure:

\`\`\`yaml
crew:
  name: custom-workflow-crew
  agents:
    - name: researcher
      role: Information Gatherer
      model_tier: cheap  # Haiku for quick lookups
      goal: Gather and summarize relevant information

    - name: analyzer
      role: Deep Analysis Expert
      model_tier: capable  # Sonnet for complex analysis
      goal: Analyze gathered information for patterns and insights

    - name: synthesizer
      role: Solution Architect
      model_tier: premium  # Opus for synthesis and decisions
      goal: Synthesize analysis into actionable recommendations

  workflow:
    type: sequential
    steps:
      - agent: researcher
      - agent: analyzer
      - agent: synthesizer
\`\`\`

Would you like me to generate the XML-enhanced prompts for each agent?`;
            }

            return `To design an effective agent workflow, let me understand:

1. **Task Complexity**: Is this a single-step task or does it require multiple specialized skills?
2. **Expertise Areas**: What domains of knowledge are needed? (e.g., coding, research, analysis)
3. **Collaboration Pattern**: Should agents work sequentially, in parallel, or hierarchically?

What's the primary goal you're trying to accomplish?`;
        }

        return `I understand you're working on: "${userContent.substring(0, 100)}..."

Let me help you clarify the next steps. What specific aspect would you like to focus on?`;
    }

    /**
     * Start a new conversation
     */
    startConversation(
        conversationId: string,
        formType: FormType,
        initialContext: Record<string, any> = {}
    ): ConversationState {
        const config = FORM_CONFIGS[formType];

        const state: ConversationState = {
            formType,
            messages: [
                {
                    role: 'system',
                    content: config.systemPrompt,
                    timestamp: Date.now(),
                },
                {
                    role: 'assistant',
                    content: config.initialQuestion,
                    timestamp: Date.now(),
                },
            ],
            context: initialContext,
            isComplete: false,
        };

        this.conversations.set(conversationId, state);
        this.persistConversations();

        return state;
    }

    /**
     * Send a user message and get LLM response
     */
    async sendMessage(
        conversationId: string,
        userMessage: string
    ): Promise<ChatMessage | null> {
        const state = this.conversations.get(conversationId);
        if (!state) {
            console.error(`[SocraticFormService] Conversation not found: ${conversationId}`);
            return null;
        }

        // Add user message
        const userMsg: ChatMessage = {
            role: 'user',
            content: userMessage,
            timestamp: Date.now(),
        };
        state.messages.push(userMsg);

        // Check turn limit
        const config = FORM_CONFIGS[state.formType];
        const userTurns = state.messages.filter(m => m.role === 'user').length;

        if (userTurns >= config.maxTurns) {
            state.isComplete = true;
            const finalMsg: ChatMessage = {
                role: 'assistant',
                content: 'We\'ve covered a lot! Let me summarize what we discussed. You can always start a new conversation to continue.',
                timestamp: Date.now(),
            };
            state.messages.push(finalMsg);
            this.persistConversations();
            return finalMsg;
        }

        // Call LLM
        try {
            const response = await this.callLLM(state);
            const assistantMsg: ChatMessage = {
                role: 'assistant',
                content: response,
                timestamp: Date.now(),
            };
            state.messages.push(assistantMsg);

            // Check if conversation is complete (LLM signals completion)
            if (this.detectCompletion(response, state.formType)) {
                state.isComplete = true;
                state.result = this.extractResult(response, state.formType);
            }

            this.persistConversations();
            return assistantMsg;
        } catch (error) {
            console.error('[SocraticFormService] LLM call failed:', error);
            const errorMsg: ChatMessage = {
                role: 'assistant',
                content: 'I encountered an error processing your request. Please try again.',
                timestamp: Date.now(),
            };
            state.messages.push(errorMsg);
            this.persistConversations();
            return errorMsg;
        }
    }

    /**
     * Get conversation state
     */
    getConversation(conversationId: string): ConversationState | undefined {
        return this.conversations.get(conversationId);
    }

    /**
     * Get all conversation IDs
     */
    getConversationIds(): string[] {
        return Array.from(this.conversations.keys());
    }

    /**
     * Delete a conversation
     */
    deleteConversation(conversationId: string): void {
        this.conversations.delete(conversationId);
        this.persistConversations();
    }

    /**
     * Clear all conversations
     */
    clearAllConversations(): void {
        this.conversations.clear();
        this.persistConversations();
    }

    /**
     * Call the LLM via empathy_os CLI
     */
    private async callLLM(state: ConversationState): Promise<string> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Build conversation for LLM
        const messages = state.messages
            .filter(m => m.role !== 'system')
            .map(m => `${m.role === 'user' ? 'Human' : 'Assistant'}: ${m.content}`)
            .join('\n\n');

        const systemPrompt = state.messages.find(m => m.role === 'system')?.content || '';

        // Create the prompt for the CLI
        const prompt = `${systemPrompt}\n\nConversation so far:\n${messages}\n\nAssistant:`;

        return new Promise((resolve, reject) => {
            // Use empathy_os chat command
            const args = ['-m', 'empathy_os.cli', 'chat', '--message', prompt, '--no-stream'];

            cp.execFile(pythonPath, args, {
                cwd: workspaceFolder,
                maxBuffer: 1024 * 1024,
                timeout: 60000,
            }, (error, stdout, stderr) => {
                if (error) {
                    // Fallback to a helpful message if CLI not available
                    console.error('[SocraticFormService] CLI error:', error);
                    resolve(this.getFallbackResponse(state));
                    return;
                }

                const response = stdout.trim();
                if (response) {
                    resolve(response);
                } else {
                    resolve(this.getFallbackResponse(state));
                }
            });
        });
    }

    /**
     * Fallback response when LLM is not available
     */
    private getFallbackResponse(state: ConversationState): string {
        const lastUserMessage = [...state.messages].reverse().find(m => m.role === 'user');

        switch (state.formType) {
            case 'plan-refinement':
                return `I understand you want to work on: "${lastUserMessage?.content}".

To create a solid plan, consider:
1. **Break it into steps** - What are the main components?
2. **Identify dependencies** - What needs to happen first?
3. **Define success criteria** - How will you know it's done?

Would you like me to help structure this further?`;

            case 'workflow-customization':
                return `I can help you customize that workflow.

Here's how to configure it in your \`empathy.config.yml\`:

\`\`\`yaml
workflow_chains:
  after_${lastUserMessage?.content?.toLowerCase().replace(/\s+/g, '_') || 'workflow'}:
    - ship
    - fix-all
\`\`\`

Would you like to adjust the commands in this chain?`;

            case 'learning-mode':
                return `Great question! Here are some keyboard shortcuts to get you started:

- **Ctrl+Shift+E M** - Morning Briefing
- **Ctrl+Shift+E S** - Pre-Ship Check
- **Ctrl+Shift+E F** - Fix All Issues
- **Ctrl+Shift+E W** - Run Workflow

Try pressing **Ctrl+Shift+E M** to run the morning briefing!

Would you like me to explain any of these in more detail?`;

            default:
                return `I'm here to help with Empathy Framework. You can ask about:
- Running workflows and commands
- Customizing your setup
- Best practices for code quality

What would you like to know more about?`;
        }
    }

    /**
     * Detect if the conversation has reached a natural conclusion
     */
    private detectCompletion(response: string, formType: FormType): boolean {
        const completionSignals = [
            'implementation plan:',
            'here\'s your plan:',
            'final configuration:',
            'here\'s the yaml:',
            '```yaml',
            'you\'re all set!',
            'happy coding!',
            'you\'ve completed',
        ];

        const lowerResponse = response.toLowerCase();
        return completionSignals.some(signal => lowerResponse.includes(signal));
    }

    /**
     * Extract structured result from completion response
     */
    private extractResult(response: string, formType: FormType): any {
        switch (formType) {
            case 'workflow-customization':
                // Extract YAML block if present
                const yamlMatch = response.match(/```yaml\n([\s\S]*?)```/);
                return yamlMatch ? { yaml: yamlMatch[1] } : { text: response };

            case 'plan-refinement':
                // Extract plan sections
                return { plan: response };

            default:
                return { text: response };
        }
    }

    /**
     * Persist conversations to workspace state
     */
    private persistConversations(): void {
        if (!this.context) return;

        const data: Record<string, ConversationState> = {};
        this.conversations.forEach((state, id) => {
            data[id] = state;
        });

        this.context.workspaceState.update('empathy.socraticConversations', data);
    }

    /**
     * Load persisted conversations
     */
    private loadPersistedConversations(): void {
        if (!this.context) return;

        const data = this.context.workspaceState.get<Record<string, ConversationState>>(
            'empathy.socraticConversations'
        );

        if (data) {
            this.conversations = new Map(Object.entries(data));
        }
    }
}
