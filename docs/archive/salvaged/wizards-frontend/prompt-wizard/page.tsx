'use client';

import { useState } from 'react';
import { toast } from 'react-hot-toast';
import WizardLayout from '@/components/wizard/WizardLayout';
import WizardNavigation from '@/components/wizard/WizardNavigation';
import WizardExport from '@/components/wizard/WizardExport';
import { useWizard } from '@/hooks/useWizard';
import { WizardConfig } from '@/types/wizard';
import TextInputWithDictation from '@/components/ui/TextInputWithDictation';

const wizardConfig: WizardConfig = {
  id: 'prompt-engineering',
  title: 'Prompt Engineering Wizard',
  description: 'Create effective prompts with best practices and optimization',
  icon: '✨',
  category: 'training',
  estimatedTime: '10-15 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Getting started', isComplete: false },
    { id: 'use-case', title: 'Use Case', description: 'Define your goal', isComplete: false },
    { id: 'context', title: 'Context', description: 'Set the scene', isComplete: false },
    { id: 'instructions', title: 'Instructions', description: 'Core prompt', isComplete: false },
    { id: 'examples', title: 'Examples', description: 'Few-shot learning', isComplete: false, isOptional: true },
    { id: 'constraints', title: 'Constraints', description: 'Guardrails & format', isComplete: false },
    { id: 'optimize', title: 'Optimize', description: 'Token & clarity', isComplete: false },
    { id: 'review', title: 'Review', description: 'Final prompt', isComplete: false },
  ],
  exportFormats: [
    { id: 'markdown', label: 'Markdown', extension: 'md', mimeType: 'text/markdown' },
    { id: 'json', label: 'JSON', extension: 'json', mimeType: 'application/json' },
    { id: 'text', label: 'Plain Text', extension: 'txt', mimeType: 'text/plain' },
  ],
};

const USE_CASES = [
  { value: 'customer-support', label: 'Customer Support', description: 'Help users with questions and issues' },
  { value: 'content-generation', label: 'Content Generation', description: 'Create blog posts, articles, marketing copy' },
  { value: 'code-assistant', label: 'Code Assistant', description: 'Help with programming tasks and debugging' },
  { value: 'data-analysis', label: 'Data Analysis', description: 'Analyze and interpret data' },
  { value: 'creative-writing', label: 'Creative Writing', description: 'Stories, scripts, creative content' },
  { value: 'education', label: 'Education & Tutoring', description: 'Teach and explain concepts' },
  { value: 'research', label: 'Research Assistant', description: 'Gather and synthesize information' },
  { value: 'custom', label: 'Custom Use Case', description: 'Define your own use case' },
];

const OUTPUT_FORMATS = [
  { value: 'bullet-points', label: 'Bullet Points' },
  { value: 'paragraph', label: 'Paragraphs' },
  { value: 'json', label: 'JSON Structure' },
  { value: 'markdown', label: 'Markdown' },
  { value: 'code', label: 'Code Block' },
  { value: 'table', label: 'Table' },
];

const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'casual', label: 'Casual' },
  { value: 'formal', label: 'Formal' },
  { value: 'technical', label: 'Technical' },
  { value: 'empathetic', label: 'Empathetic' },
];

export default function PromptWizard() {
  const wizard = useWizard(wizardConfig);
  const [showOutput, setShowOutput] = useState(false);

  // Form data
  const [useCase, setUseCase] = useState('');
  const [customUseCase, setCustomUseCase] = useState('');
  const [role, setRole] = useState('');
  const [background, setBackground] = useState('');
  const [task, setTask] = useState('');
  const [specificInstructions, setSpecificInstructions] = useState('');
  const [examples, setExamples] = useState<Array<{ input: string; output: string }>>([]);
  const [outputFormat, setOutputFormat] = useState('');
  const [tone, setTone] = useState('');
  const [maxLength, setMaxLength] = useState('');
  const [constraints, setConstraints] = useState('');

  const generatePrompt = () => {
    const sections = [];

    // Role & Context
    if (role || background) {
      sections.push('## Role & Context');
      if (role) sections.push(`You are ${role}.`);
      if (background) sections.push(background);
      sections.push('');
    }

    // Task
    sections.push('## Task');
    sections.push(task || 'Your task is...');
    sections.push('');

    // Instructions
    if (specificInstructions) {
      sections.push('## Instructions');
      sections.push(specificInstructions);
      sections.push('');
    }

    // Examples
    if (examples.length > 0) {
      sections.push('## Examples');
      examples.forEach((ex, i) => {
        sections.push(`### Example ${i + 1}`);
        sections.push(`**Input:** ${ex.input}`);
        sections.push(`**Output:** ${ex.output}`);
        sections.push('');
      });
    }

    // Output Format & Constraints
    if (outputFormat || tone || maxLength || constraints) {
      sections.push('## Output Requirements');
      if (outputFormat) sections.push(`- **Format:** ${OUTPUT_FORMATS.find(f => f.value === outputFormat)?.label}`);
      if (tone) sections.push(`- **Tone:** ${TONE_OPTIONS.find(t => t.value === tone)?.label}`);
      if (maxLength) sections.push(`- **Length:** ${maxLength} tokens maximum`);
      if (constraints) {
        sections.push(`- **Constraints:**`);
        constraints.split('\n').forEach(c => sections.push(`  - ${c}`));
      }
      sections.push('');
    }

    return sections.join('\n');
  };

  const renderStep = () => {
    const currentStep = wizardConfig.steps[wizard.currentStep];

    switch (currentStep.id) {
      case 'welcome':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="text-6xl mb-4">✨</div>
              <h2 className="text-3xl font-bold mb-4">Prompt Engineering Wizard</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Create effective prompts using proven techniques and best practices. This wizard will
                guide you through crafting prompts that get better results from AI models.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🎯</div>
                <h3 className="font-semibold mb-2">Clear Objectives</h3>
                <p className="text-sm text-gray-400">Define exactly what you want to achieve</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🧠</div>
                <h3 className="font-semibold mb-2">Context Setting</h3>
                <p className="text-sm text-gray-400">Provide the right background information</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">📊</div>
                <h3 className="font-semibold mb-2">Example-Driven</h3>
                <p className="text-sm text-gray-400">Use few-shot learning for better results</p>
              </div>
            </div>

            <button
              onClick={() => {
                wizard.completeStep('welcome');
                wizard.nextStep();
              }}
              className="w-full mt-8 px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-medium text-lg hover:opacity-90 transition-opacity"
            >
              Get Started →
            </button>
          </div>
        );

      case 'use-case':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">What's Your Use Case?</h2>
              <p className="text-gray-400">Choose the type of task you want to accomplish</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {USE_CASES.map((uc) => (
                <button
                  key={uc.value}
                  onClick={() => setUseCase(uc.value)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    useCase === uc.value
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <div className="font-semibold mb-1">{uc.label}</div>
                  <div className="text-sm text-gray-400">{uc.description}</div>
                </button>
              ))}
            </div>

            {useCase === 'custom' && (
              <div>
                <label className="block text-sm font-medium mb-2">Describe Your Use Case</label>
                <TextInputWithDictation
                  multiline
                  rows={4}
                  value={customUseCase}
                  onChange={(e) => setCustomUseCase(e.target.value)}
                  placeholder="Describe what you want to accomplish..."
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                  enableDictation={true}
                />
              </div>
            )}

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!useCase}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('use-case');
                wizard.updateData('useCase', useCase);
                wizard.updateData('customUseCase', customUseCase);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'context':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Set the Context</h2>
              <p className="text-gray-400">Define the AI's role and provide background information</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                AI Role <span className="text-gray-500">(Optional)</span>
              </label>
              <TextInputWithDictation
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="e.g., a helpful customer support agent, an expert Python developer..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                enableDictation={true}
              />
              <p className="text-xs text-gray-500 mt-1">
                Giving the AI a specific role helps it respond more appropriately
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Background Context <span className="text-gray-500">(Optional)</span>
              </label>
              <TextInputWithDictation
                multiline
                rows={5}
                value={background}
                onChange={(e) => setBackground(e.target.value)}
                placeholder="Provide any relevant background information, domain knowledge, or situational context..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                enableDictation={true}
              />
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={true}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('context');
                wizard.updateData('role', role);
                wizard.updateData('background', background);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'instructions':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Define the Task</h2>
              <p className="text-gray-400">What exactly do you want the AI to do?</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Main Task *</label>
              <TextInputWithDictation
                multiline
                rows={4}
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Be specific about what you want the AI to do..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                enableDictation={true}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Specific Instructions <span className="text-gray-500">(Optional)</span>
              </label>
              <TextInputWithDictation
                multiline
                rows={6}
                value={specificInstructions}
                onChange={(e) => setSpecificInstructions(e.target.value)}
                placeholder="Step-by-step instructions, special requirements, things to focus on or avoid..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                enableDictation={true}
              />
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">💡</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Pro Tip</div>
                  <div className="text-sm text-gray-300">
                    Break complex tasks into clear, numbered steps. Use imperative language ("Analyze...", "Create...", "List...").
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={task.length > 10}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('instructions');
                wizard.updateData('task', task);
                wizard.updateData('specificInstructions', specificInstructions);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'examples':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">
                Add Examples <span className="text-sm text-gray-500">(Optional)</span>
              </h2>
              <p className="text-gray-400">Few-shot learning: provide examples of the desired input/output</p>
            </div>

            {examples.map((example, index) => (
              <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="font-semibold">Example {index + 1}</div>
                  <button
                    onClick={() => setExamples(examples.filter((_, i) => i !== index))}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Remove
                  </button>
                </div>
                <div>
                  <label className="block text-sm mb-1">Input</label>
                  <TextInputWithDictation
                    multiline
                    rows={2}
                    value={example.input}
                    onChange={(e) => {
                      const newExamples = [...examples];
                      newExamples[index].input = e.target.value;
                      setExamples(newExamples);
                    }}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none"
                    enableDictation={true}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Output</label>
                  <TextInputWithDictation
                    multiline
                    rows={3}
                    value={example.output}
                    onChange={(e) => {
                      const newExamples = [...examples];
                      newExamples[index].output = e.target.value;
                      setExamples(newExamples);
                    }}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none"
                    enableDictation={true}
                  />
                </div>
              </div>
            ))}

            <button
              onClick={() => setExamples([...examples, { input: '', output: '' }])}
              className="w-full py-3 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
            >
              + Add Example
            </button>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={true}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('examples');
                wizard.updateData('examples', examples);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'constraints':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Output Requirements</h2>
              <p className="text-gray-400">Define the format, tone, and constraints for the output</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Output Format</label>
                <select
                  value={outputFormat}
                  onChange={(e) => setOutputFormat(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                >
                  <option value="">Select format...</option>
                  {OUTPUT_FORMATS.map((format) => (
                    <option key={format.value} value={format.value}>
                      {format.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Tone</label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                >
                  <option value="">Select tone...</option>
                  {TONE_OPTIONS.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Max Length (tokens) <span className="text-gray-500">(Optional)</span>
              </label>
              <input
                type="number"
                value={maxLength}
                onChange={(e) => setMaxLength(e.target.value)}
                placeholder="e.g., 500"
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Additional Constraints <span className="text-gray-500">(Optional)</span>
              </label>
              <TextInputWithDictation
                multiline
                rows={5}
                value={constraints}
                onChange={(e) => setConstraints(e.target.value)}
                placeholder="One constraint per line, e.g.:\nMust cite sources\nAvoid technical jargon\nUse simple language"
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                enableDictation={true}
              />
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={true}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('constraints');
                wizard.updateData('outputFormat', outputFormat);
                wizard.updateData('tone', tone);
                wizard.updateData('maxLength', maxLength);
                wizard.updateData('constraints', constraints);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'optimize':
        const currentPrompt = generatePrompt();
        const tokenEstimate = Math.ceil(currentPrompt.split(' ').length * 1.3);

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Optimize Your Prompt</h2>
              <p className="text-gray-400">Review metrics and suggestions for improvement</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Estimated Tokens</div>
                <div className="text-3xl font-bold">{tokenEstimate}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Clarity Score</div>
                <div className="text-3xl font-bold text-green-400">
                  {task && role ? 'High' : task ? 'Medium' : 'Low'}
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Examples</div>
                <div className="text-3xl font-bold">{examples.length}</div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="font-semibold mb-3">Optimization Suggestions</h3>
              <div className="space-y-2 text-sm">
                {!role && (
                  <div className="flex gap-2 text-yellow-400">
                    <span>⚠️</span>
                    <span>Consider adding a role to improve context</span>
                  </div>
                )}
                {examples.length === 0 && (
                  <div className="flex gap-2 text-yellow-400">
                    <span>⚠️</span>
                    <span>Adding examples (few-shot learning) can significantly improve results</span>
                  </div>
                )}
                {!outputFormat && (
                  <div className="flex gap-2 text-yellow-400">
                    <span>⚠️</span>
                    <span>Specifying an output format helps ensure consistent results</span>
                  </div>
                )}
                {role && examples.length > 0 && outputFormat && (
                  <div className="flex gap-2 text-green-400">
                    <span>✓</span>
                    <span>Your prompt looks well-structured!</span>
                  </div>
                )}
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={true}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('optimize');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'review':
        const finalPrompt = generatePrompt();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Your Final Prompt</h2>
              <p className="text-gray-400">Review and export your engineered prompt</p>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Generated Prompt</h3>
                <button
                  onClick={() => setShowOutput(!showOutput)}
                  className="text-sm text-primary hover:text-primary/80"
                >
                  {showOutput ? 'Hide' : 'Show'} Preview
                </button>
              </div>

              {showOutput && (
                <pre className="bg-gray-900 p-4 rounded text-sm overflow-x-auto whitespace-pre-wrap">
                  {finalPrompt}
                </pre>
              )}
            </div>

            <WizardExport
              formats={wizardConfig.exportFormats}
              content={finalPrompt}
              filename={`prompt-${Date.now()}`}
            />

            <div className="flex gap-4">
              <button
                onClick={() => wizard.goToStep(0)}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                Create Another Prompt
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('review');
                  toast.success('Prompt engineering complete!');
                }}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-secondary hover:opacity-90 rounded-lg font-medium transition-opacity"
              >
                Complete Wizard
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <WizardLayout
      config={wizardConfig}
      currentStep={wizard.currentStep}
      totalSteps={wizardConfig.steps.length}
      progress={wizard.progress}
      onStepClick={wizard.goToStep}
    >
      {renderStep()}
    </WizardLayout>
  );
}
