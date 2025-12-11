/**
 * Philosophy Wizard Configuration
 *
 * Declarative configuration for the AI Philosophy Statement wizard.
 * This replaces 600 lines of imperative code with ~150 lines of configuration.
 */

import { createWizard } from '@/lib/wizard/core/WizardBuilder';
import { WizardBuilderConfig } from '@/lib/wizard/core/types';
import { BaseExporter } from '@/lib/wizard/core/BaseExporter';

/**
 * Philosophy statement markdown exporter
 */
class PhilosophyExporter extends BaseExporter {
  readonly format = 'philosophy-md';
  readonly label = 'Philosophy Statement (Markdown)';
  readonly extension = 'md';
  readonly mimeType = 'text/markdown';

  export(data: Record<string, any>, config: WizardBuilderConfig): string {
    const { context, domain, principles, empathyLevel, coreValues, customValue, userExamples } =
      data;

    const allValues = [...(coreValues || [])];
    if (customValue) allValues.push(customValue);

    return `# AI Training Philosophy Statement

## Context & Purpose
${context || 'Define how the AI should interact and assist users.'}
${domain ? `\n**Domain**: ${domain}` : ''}

## Guiding Principles
${principles && principles.length > 0 ? principles.map((p: string) => `- ${this.getPrincipleName(p)}`).join('\n') : '- Not specified'}

## Empathy Level
**Target**: ${this.getEmpathyLevelName(empathyLevel)}
${this.getEmpathyLevelDescription(empathyLevel)}

## Core Values
${allValues.length > 0 ? allValues.map((v: string) => `- ${v}`).join('\n') : '- Not specified'}

## Behavioral Examples
${userExamples || 'Not provided'}

## Implementation Guidelines

1. **Prioritize** ${allValues[0] || 'core principles'} in all interactions
2. **Operate at** ${this.getEmpathyLevelName(empathyLevel).split(':')[1] || 'the appropriate empathy level'}
3. **Apply** ${this.getPrincipleName(principles?.[0]) || 'guiding principles'} when making decisions
4. **Balance** technical accuracy with human understanding
5. **Continuously** learn from user interactions and feedback

## Training Prompts

### System Prompt Template
\`\`\`
You are an AI assistant trained with ${this.getEmpathyLevelName(empathyLevel)} capabilities.

Core Philosophy:
${allValues.slice(0, 3).map((v: string) => `- ${v}`).join('\n')}

Your role is to ${context ? context.toLowerCase() : 'assist users effectively'}.

Apply these principles:
${principles ? principles.slice(0, 3).map((p: string) => `- ${this.getPrincipleName(p)}`).join('\n') : ''}
\`\`\`

### Example Training Scenarios
${userExamples ? `\n${userExamples}\n` : '\n(Add specific examples for your use case)\n'}

---

*Generated with SmartAI Memory Philosophy Wizard*
*${this.formatDate()}*
`;
  }

  private getPrincipleName(id: string): string {
    const principles: Record<string, string> = {
      goleman: 'Emotional Intelligence (Goleman)',
      voss: 'Tactical Empathy (Chris Voss)',
      naval: 'First Principles (Naval Ravikant)',
      socratic: 'Socratic Method',
      growth: 'Growth Mindset (Dweck)',
      stoic: 'Stoic Philosophy',
    };
    return principles[id] || id;
  }

  private getEmpathyLevelName(id: string): string {
    const levels: Record<string, string> = {
      level1: 'Level 1: Reactive',
      level2: 'Level 2: Guided',
      level3: 'Level 3: Proactive',
      level4: 'Level 4: Anticipatory',
      level5: 'Level 5: Systems',
    };
    return levels[id] || 'Not specified';
  }

  private getEmpathyLevelDescription(id: string): string {
    const descriptions: Record<string, string> = {
      level1: 'Respond when asked',
      level2: 'Collaborative exploration',
      level3: 'Act before being asked',
      level4: 'Predict needs before they manifest',
      level5: 'Build structures that help at scale',
    };
    return descriptions[id] || '';
  }
}

/**
 * Philosophy wizard configuration
 */
export const philosophyWizardConfig: WizardBuilderConfig = createWizard('philosophy-wizard')
  .withTitle('AI Philosophy Statement Wizard')
  .withDescription(
    'Create a comprehensive philosophy statement to guide AI training and behavior based on proven frameworks.'
  )
  .withIcon('🧠')
  .withCategory('training')
  .withEstimatedTime('10-15 minutes')
  .addStep({
    type: 'welcome',
    id: 'welcome',
    title: 'Welcome',
    description: 'Introduction to the Philosophy Wizard',
    heading: 'AI Philosophy Statement Wizard',
    subtitle:
      'Create a comprehensive philosophy statement to guide AI training and behavior. This wizard will help you define principles, values, and empathy levels based on proven frameworks.',
    icon: '🧠',
    features: [
      {
        icon: '✓',
        text: 'Define core principles from proven frameworks (Goleman, Voss, Naval)',
      },
      {
        icon: '✓',
        text: 'Set empathy level (1-5) for AI interactions',
      },
      {
        icon: '✓',
        text: 'Establish core values and behavioral guidelines',
      },
      {
        icon: '✓',
        text: 'Generate ready-to-use training prompts and documentation',
      },
    ],
  })
  .addStep({
    type: 'form',
    id: 'context',
    title: 'Define Context & Purpose',
    description: 'What is the primary purpose of this AI? What domain or context will it operate in?',
    fields: [
      {
        id: 'context',
        type: 'textarea',
        label: 'AI Purpose',
        placeholder:
          'e.g., Assist developers with code analysis and provide empathetic, educational feedback...',
        required: true,
        description: 'Describe the main purpose and role of the AI',
      },
      {
        id: 'domain',
        type: 'text',
        label: 'Domain (Optional)',
        placeholder: 'e.g., Software Development, Healthcare, Education...',
        required: false,
        description: 'Specific domain or industry context',
      },
    ],
  })
  .addStep({
    type: 'form',
    id: 'principles',
    title: 'Select Guiding Principles',
    description:
      'Choose the philosophical frameworks that should guide the AI\'s behavior. Select all that apply.',
    fields: [
      {
        id: 'principles',
        type: 'multiselect',
        label: 'Philosophical Frameworks',
        required: true,
        options: [
          {
            value: 'goleman',
            label: 'Emotional Intelligence (Goleman)',
            description: 'Self-awareness, empathy, and social skills',
          },
          {
            value: 'voss',
            label: 'Tactical Empathy (Chris Voss)',
            description: 'Deep listening and understanding others\' perspectives',
          },
          {
            value: 'naval',
            label: 'First Principles (Naval Ravikant)',
            description: 'Break down to fundamentals and rebuild',
          },
          {
            value: 'socratic',
            label: 'Socratic Method',
            description: 'Question-driven learning and discovery',
          },
          {
            value: 'growth',
            label: 'Growth Mindset (Dweck)',
            description: 'Challenges as opportunities to learn',
          },
          {
            value: 'stoic',
            label: 'Stoic Philosophy',
            description: 'Focus on what you can control',
          },
        ],
      },
    ],
  })
  .addStep({
    type: 'form',
    id: 'empathy-level',
    title: 'Choose Empathy Level',
    description: 'Select the level of empathy the AI should demonstrate. Higher levels are more anticipatory.',
    fields: [
      {
        id: 'empathyLevel',
        type: 'radio',
        label: 'Empathy Level',
        required: true,
        options: [
          {
            value: 'level1',
            label: 'Level 1: Reactive',
            description: 'Respond when asked',
          },
          {
            value: 'level2',
            label: 'Level 2: Guided',
            description: 'Collaborative exploration',
          },
          {
            value: 'level3',
            label: 'Level 3: Proactive',
            description: 'Act before being asked',
          },
          {
            value: 'level4',
            label: 'Level 4: Anticipatory',
            description: 'Predict needs before they manifest',
          },
          {
            value: 'level5',
            label: 'Level 5: Systems',
            description: 'Build structures that help at scale',
          },
        ],
      },
    ],
  })
  .addStep({
    type: 'form',
    id: 'values',
    title: 'Select Core Values',
    description: 'Choose the core values that should guide all AI interactions. Select at least 3.',
    fields: [
      {
        id: 'coreValues',
        type: 'multiselect',
        label: 'Core Values',
        required: true,
        options: [
          { value: 'Truthfulness over validation', label: 'Truthfulness over validation' },
          { value: 'Curiosity over certainty', label: 'Curiosity over certainty' },
          { value: 'Clarity over complexity', label: 'Clarity over complexity' },
          { value: 'Empathy with objectivity', label: 'Empathy with objectivity' },
          { value: 'Learning over knowing', label: 'Learning over knowing' },
          { value: 'Questions over answers', label: 'Questions over answers' },
          { value: 'Understanding context deeply', label: 'Understanding context deeply' },
          { value: 'Continuous improvement', label: 'Continuous improvement' },
        ],
        validation: (value) => {
          if (!value || value.length < 3) {
            return 'Please select at least 3 core values';
          }
          return null;
        },
      },
      {
        id: 'customValue',
        type: 'text',
        label: 'Add Custom Value (Optional)',
        placeholder: 'e.g., Domain-specific principle...',
        required: false,
      },
    ],
  })
  .addStep({
    type: 'form',
    id: 'examples',
    title: 'Provide Example Scenarios',
    description:
      'Add specific examples of how the AI should behave in real situations. This helps train consistent behavior.',
    fields: [
      {
        id: 'userExamples',
        type: 'textarea',
        label: 'Training Examples',
        placeholder: `Example:

User: 'My code is broken and I don't know why'
AI Response: First, I'll help you understand what's happening. Let's break this down step by step...

User: 'Just tell me what's wrong'
AI Response: I found the issue on line 42. Here's what's happening and why it matters...`,
        required: false,
        min: 10,
      },
    ],
  })
  .addStep({
    type: 'review',
    id: 'review',
    title: 'Review Your Philosophy',
    description: 'Review your selections before generating the final philosophy statement.',
    sections: [
      {
        title: 'Context & Purpose',
        fields: ['context', 'domain'],
      },
      {
        title: 'Guiding Principles',
        fields: ['principles'],
      },
      {
        title: 'Empathy Level',
        fields: ['empathyLevel'],
      },
      {
        title: 'Core Values',
        fields: ['coreValues', 'customValue'],
      },
    ],
  })
  .withExportFormat('markdown')
  .withExportFormat('json')
  .build();

// Register custom exporter
import { registerExporter } from '@/lib/wizard/core/ExportRegistry';
registerExporter(new PhilosophyExporter());
