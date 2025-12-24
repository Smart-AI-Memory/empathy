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
  id: 'finetuning-preparation',
  title: 'Fine-tuning Preparation Wizard',
  description: 'Prepare datasets for model customization and fine-tuning',
  icon: '⚙️',
  category: 'training',
  estimatedTime: '25-30 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Getting started', isComplete: false },
    { id: 'model', title: 'Model Selection', description: 'Choose base model', isComplete: false },
    { id: 'upload', title: 'Data Upload', description: 'Add training examples', isComplete: false },
    { id: 'validation', title: 'Format Validation', description: 'Check requirements', isComplete: false },
    { id: 'quality', title: 'Quality Scoring', description: 'Assess examples', isComplete: false },
    { id: 'cost', title: 'Cost Estimation', description: 'Calculate costs', isComplete: false },
    { id: 'export', title: 'Export', description: 'Download dataset', isComplete: false },
  ],
  exportFormats: [
    { id: 'jsonl', label: 'JSONL (Training)', extension: 'jsonl', mimeType: 'application/jsonl' },
    { id: 'json', label: 'JSON (Config)', extension: 'json', mimeType: 'application/json' },
    { id: 'csv', label: 'CSV (Review)', extension: 'csv', mimeType: 'text/csv' },
  ],
};

const MODEL_PROVIDERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    models: [
      { id: 'gpt-5-turbo', name: 'GPT-5 Turbo', baseCost: 10.00, trainCost: 80.00, recommended: true },
      { id: 'gpt-5', name: 'GPT-5', baseCost: 15.00, trainCost: 120.00, recommended: true },
      { id: 'gpt-4o-mini-2025-07-18', name: 'GPT-4o Mini (2025)', baseCost: 0.15, trainCost: 3.00, note: 'Best cost/performance' },
      { id: 'gpt-4o-2025-08-06', name: 'GPT-4o (2025)', baseCost: 2.50, trainCost: 25.00 },
      { id: 'gpt-4.5-turbo', name: 'GPT-4.5 Turbo', baseCost: 5.00, trainCost: 37.50 },
      { id: 'o1-mini', name: 'o1 Mini (Reasoning)', baseCost: 3.00, trainCost: 30.00 },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', baseCost: 0.50, trainCost: 8.00, note: 'Most affordable option' },
    ],
    minExamples: 10,
    format: 'chat',
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    models: [
      { id: 'claude-4.5-sonnet', name: 'Claude 4.5 Sonnet', baseCost: 4.00, trainCost: 40.00, recommended: true },
      { id: 'claude-4-opus', name: 'Claude 4 Opus', baseCost: 15.00, trainCost: 75.00 },
      { id: 'claude-4-sonnet', name: 'Claude 4 Sonnet', baseCost: 3.00, trainCost: 30.00 },
      { id: 'claude-4-haiku', name: 'Claude 4 Haiku', baseCost: 0.25, trainCost: 4.00, note: 'Fastest & cheapest' },
      { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', baseCost: 3.00, trainCost: 30.00, note: 'Proven reliability' },
      { id: 'claude-3-haiku', name: 'Claude 3 Haiku', baseCost: 0.25, trainCost: 4.00, note: 'Legacy low-cost' },
    ],
    minExamples: 50,
    format: 'chat',
  },
  {
    id: 'opensource',
    name: 'Open Source',
    models: [
      { id: 'llama-4-8b', name: 'Llama 4 8B', baseCost: 0, trainCost: 0, recommended: true, note: 'Latest Meta model' },
      { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', baseCost: 0, trainCost: 0, note: 'Most capable Llama 3' },
      { id: 'llama-3.1-70b', name: 'Llama 3.1 70B', baseCost: 0, trainCost: 0, note: 'Stable & well-tested' },
      { id: 'llama-3.1-8b', name: 'Llama 3.1 8B', baseCost: 0, trainCost: 0, note: 'Efficient for simple tasks' },
      { id: 'qwen-2.5-72b', name: 'Qwen 2.5 72B', baseCost: 0, trainCost: 0, note: 'Excellent multilingual' },
      { id: 'deepseek-v3', name: 'DeepSeek V3', baseCost: 0, trainCost: 0, note: 'Strong reasoning' },
      { id: 'mistral-large-2', name: 'Mistral Large 2', baseCost: 0, trainCost: 0, note: 'European alternative' },
      { id: 'mistral-7b', name: 'Mistral 7B v0.3', baseCost: 0, trainCost: 0, note: 'Lightweight & fast' },
      { id: 'mixtral-8x7b', name: 'Mixtral 8x7B', baseCost: 0, trainCost: 0, note: 'MoE architecture' },
    ],
    minExamples: 100,
    format: 'instruct',
  },
];

interface TrainingExample {
  id: string;
  messages?: Array<{ role: string; content: string }>;
  prompt?: string;
  completion?: string;
  tokens?: number;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

interface QualityMetrics {
  avgLength: number;
  diversity: number;
  completeness: number;
  overallScore: number;
}

export default function FinetuningWizard() {
  const wizard = useWizard(wizardConfig);
  const [showOutput, setShowOutput] = useState(false);

  // Form data
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [examples, setExamples] = useState<TrainingExample[]>([]);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null);
  const [epochs, setEpochs] = useState(3);
  const [learningRate, setLearningRate] = useState(0.0001);
  const [batchSize, setBatchSize] = useState(4);

  const getProvider = () => MODEL_PROVIDERS.find(p => p.id === selectedProvider);
  const getModel = () => getProvider()?.models.find(m => m.id === selectedModel);

  const countTokens = (text: string): number => {
    return Math.ceil(text.split(/\s+/).length * 1.3);
  };

  const addExample = () => {
    const provider = getProvider();
    if (!provider) return;

    const newExample: TrainingExample = {
      id: Date.now().toString(),
    };

    if (provider.format === 'chat') {
      newExample.messages = [
        { role: 'system', content: '' },
        { role: 'user', content: '' },
        { role: 'assistant', content: '' },
      ];
    } else {
      newExample.prompt = '';
      newExample.completion = '';
    }

    setExamples([...examples, newExample]);
  };

  const removeExample = (id: string) => {
    setExamples(examples.filter(ex => ex.id !== id));
  };

  const updateExample = (id: string, updates: Partial<TrainingExample>) => {
    setExamples(examples.map(ex => ex.id === id ? { ...ex, ...updates } : ex));
  };

  const parseJSONL = (text: string): TrainingExample[] => {
    try {
      const lines = text.trim().split('\n').filter(line => line.trim());
      const parsed = lines.map((line, idx) => {
        const obj = JSON.parse(line);
        return {
          id: `imported-${idx}`,
          ...obj,
        };
      });
      return parsed;
    } catch (error) {
      toast.error('Invalid JSONL format');
      return [];
    }
  };

  const validateExamples = (): ValidationResult => {
    const errors: string[] = [];
    const warnings: string[] = [];
    const provider = getProvider();

    if (!provider) {
      errors.push('No provider selected');
      return { isValid: false, errors, warnings };
    }

    // Check minimum examples
    if (examples.length < provider.minExamples) {
      errors.push(`Minimum ${provider.minExamples} examples required (found ${examples.length})`);
    }

    // Validate format
    examples.forEach((ex, idx) => {
      if (provider.format === 'chat') {
        if (!ex.messages || ex.messages.length === 0) {
          errors.push(`Example ${idx + 1}: Missing messages array`);
        } else {
          const hasUser = ex.messages.some(m => m.role === 'user');
          const hasAssistant = ex.messages.some(m => m.role === 'assistant');
          if (!hasUser) errors.push(`Example ${idx + 1}: Missing user message`);
          if (!hasAssistant) errors.push(`Example ${idx + 1}: Missing assistant message`);

          ex.messages.forEach((msg, msgIdx) => {
            if (!msg.content || msg.content.trim().length === 0) {
              warnings.push(`Example ${idx + 1}, Message ${msgIdx + 1}: Empty content`);
            }
          });
        }
      } else {
        if (!ex.prompt || ex.prompt.trim().length === 0) {
          errors.push(`Example ${idx + 1}: Missing prompt`);
        }
        if (!ex.completion || ex.completion.trim().length === 0) {
          errors.push(`Example ${idx + 1}: Missing completion`);
        }
      }

      // Token count warnings
      const tokens = calculateExampleTokens(ex);
      if (tokens > 4096) {
        warnings.push(`Example ${idx + 1}: Very long (${tokens} tokens), may be truncated`);
      }
    });

    // Check for diversity
    if (examples.length > 10) {
      const uniquePrompts = new Set(examples.map(ex =>
        ex.messages?.[1]?.content || ex.prompt || ''
      ));
      if (uniquePrompts.size < examples.length * 0.7) {
        warnings.push('Low diversity: Many similar examples detected');
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  };

  const calculateExampleTokens = (example: TrainingExample): number => {
    if (example.messages) {
      return example.messages.reduce((sum, msg) => sum + countTokens(msg.content), 0);
    } else {
      return countTokens(example.prompt || '') + countTokens(example.completion || '');
    }
  };

  const calculateQualityMetrics = (): QualityMetrics => {
    if (examples.length === 0) {
      return { avgLength: 0, diversity: 0, completeness: 0, overallScore: 0 };
    }

    // Average length
    const totalTokens = examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0);
    const avgLength = totalTokens / examples.length;

    // Diversity score (based on unique content)
    const contents = examples.map(ex => {
      if (ex.messages) {
        return ex.messages.map(m => m.content).join(' ');
      } else {
        return (ex.prompt || '') + ' ' + (ex.completion || '');
      }
    });
    const uniqueWords = new Set(contents.join(' ').toLowerCase().split(/\s+/));
    const totalWords = contents.join(' ').split(/\s+/).length;
    const diversity = Math.min(100, (uniqueWords.size / totalWords) * 200);

    // Completeness score (examples with all required fields)
    const provider = getProvider();
    let completeCount = 0;
    examples.forEach(ex => {
      if (provider?.format === 'chat') {
        if (ex.messages && ex.messages.every(m => m.content.trim().length > 0)) {
          completeCount++;
        }
      } else {
        if (ex.prompt && ex.completion && ex.prompt.trim().length > 0 && ex.completion.trim().length > 0) {
          completeCount++;
        }
      }
    });
    const completeness = (completeCount / examples.length) * 100;

    // Overall score
    const overallScore = (
      (Math.min(avgLength / 100, 100) * 0.3) +
      (diversity * 0.4) +
      (completeness * 0.3)
    );

    return { avgLength, diversity, completeness, overallScore };
  };

  const calculateCost = () => {
    const model = getModel();
    if (!model) return { training: 0, inference: 0, total: 0 };

    const totalTokens = examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0);
    const tokensPerMillion = totalTokens / 1000000;

    // Training cost (tokens * epochs * cost per million)
    const trainingCost = tokensPerMillion * epochs * model.trainCost;

    // Estimated inference cost (assuming 1000 requests per month with avg 1000 tokens each)
    const inferenceCost = (1000 * 1000 / 1000000) * model.baseCost;

    return {
      training: trainingCost,
      inference: inferenceCost,
      total: trainingCost + inferenceCost,
    };
  };

  const generateJSONL = (): string => {
    return examples.map(ex => {
      const obj: any = {};
      if (ex.messages) {
        obj.messages = ex.messages;
      } else {
        obj.prompt = ex.prompt;
        obj.completion = ex.completion;
      }
      return JSON.stringify(obj);
    }).join('\n');
  };

  const generateConfig = () => {
    return {
      model: selectedModel,
      provider: selectedProvider,
      hyperparameters: {
        n_epochs: epochs,
        learning_rate_multiplier: learningRate,
        batch_size: batchSize,
      },
      training_file: 'training_data.jsonl',
      validation_split: 0.1,
      examples_count: examples.length,
      total_tokens: examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0),
      estimated_cost: calculateCost(),
      quality_metrics: qualityMetrics,
      created_at: new Date().toISOString(),
    };
  };

  const renderStep = () => {
    const currentStep = wizardConfig.steps[wizard.currentStep];

    switch (currentStep.id) {
      case 'welcome':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="text-6xl mb-4">⚙️</div>
              <h2 className="text-3xl font-bold mb-4">Fine-tuning Preparation Wizard</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Prepare high-quality datasets for model fine-tuning. This wizard helps you format,
                validate, and optimize your training data for better model performance.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🎯</div>
                <h3 className="font-semibold mb-2">Format Validation</h3>
                <p className="text-sm text-gray-400">Ensure your data meets provider requirements</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">📊</div>
                <h3 className="font-semibold mb-2">Quality Scoring</h3>
                <p className="text-sm text-gray-400">Assess dataset diversity and completeness</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">💰</div>
                <h3 className="font-semibold mb-2">Cost Estimation</h3>
                <p className="text-sm text-gray-400">Calculate training and inference costs</p>
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

      case 'model':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Select Base Model</h2>
              <p className="text-gray-400">Choose the model provider and specific model to fine-tune</p>
            </div>

            <div className="space-y-4">
              {MODEL_PROVIDERS.map((provider) => (
                <div key={provider.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                  <div className="flex items-center gap-3 mb-3">
                    <input
                      type="radio"
                      name="provider"
                      checked={selectedProvider === provider.id}
                      onChange={() => {
                        setSelectedProvider(provider.id);
                        setSelectedModel('');
                      }}
                      className="w-4 h-4"
                    />
                    <div>
                      <div className="font-semibold">{provider.name}</div>
                      <div className="text-xs text-gray-400">
                        {provider.format === 'chat' ? 'Chat Format' : 'Instruct Format'} •
                        Min {provider.minExamples} examples
                      </div>
                    </div>
                  </div>

                  {selectedProvider === provider.id && (
                    <div className="ml-7 mt-3 grid grid-cols-1 gap-2">
                      {provider.models.map((model: any) => (
                        <button
                          key={model.id}
                          onClick={() => setSelectedModel(model.id)}
                          className={`p-3 rounded border-2 transition-all text-left relative ${
                            selectedModel === model.id
                              ? 'border-primary bg-primary/10'
                              : 'border-gray-700 hover:border-gray-600'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{model.name}</span>
                                {model.recommended && (
                                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded">
                                    Recommended
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-gray-400 mt-1">
                                Training: ${model.trainCost}/M tokens •
                                Inference: ${model.baseCost}/M tokens
                              </div>
                              {model.note && (
                                <div className="text-xs text-blue-400 mt-1 italic">
                                  {model.note}
                                </div>
                              )}
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {selectedProvider === 'opensource' && (
              <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
                <div className="flex gap-3">
                  <div className="text-2xl">💡</div>
                  <div>
                    <div className="font-semibold text-blue-400 mb-1">Open Source Models</div>
                    <div className="text-sm text-gray-300">
                      You'll need your own compute infrastructure. Costs shown are for API usage only.
                      Self-hosting requires GPU resources (A100, H100, etc.).
                    </div>
                  </div>
                </div>
              </div>
            )}

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!selectedProvider && !!selectedModel}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('model');
                wizard.updateData('provider', selectedProvider);
                wizard.updateData('model', selectedModel);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'upload':
        const provider = getProvider();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Add Training Examples</h2>
              <p className="text-gray-400">
                Add at least {provider?.minExamples} examples in {provider?.format === 'chat' ? 'chat' : 'instruct'} format
              </p>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm font-medium">Import from JSONL</div>
              </div>
              <div className="flex gap-2">
                <input
                  type="file"
                  accept=".jsonl,.json"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onload = (event) => {
                        const text = event.target?.result as string;
                        const imported = parseJSONL(text);
                        if (imported.length > 0) {
                          setExamples(imported);
                          toast.success(`Imported ${imported.length} examples`);
                        }
                      };
                      reader.readAsText(file);
                    }
                  }}
                  className="flex-1 text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-primary file:text-white hover:file:opacity-90"
                />
              </div>
            </div>

            <div className="space-y-3">
              {examples.map((example, index) => (
                <div key={example.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-semibold">Example {index + 1}</div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">
                        ~{calculateExampleTokens(example)} tokens
                      </span>
                      <button
                        onClick={() => removeExample(example.id)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  {provider?.format === 'chat' ? (
                    <div className="space-y-2">
                      {example.messages?.map((msg, msgIdx) => (
                        <div key={msgIdx}>
                          <label className="block text-xs mb-1 capitalize">{msg.role}</label>
                          <TextInputWithDictation
                            multiline
                            value={msg.content}
                            onChange={(e) => {
                              const newMessages = [...(example.messages || [])];
                              newMessages[msgIdx].content = e.target.value;
                              updateExample(example.id, { messages: newMessages });
                            }}
                            placeholder={`Enter ${msg.role} message...`}
                            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                            rows={2}
                            enableDictation={true}
                          />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div>
                        <label className="block text-xs mb-1">Prompt</label>
                        <TextInputWithDictation
                          multiline
                          value={example.prompt || ''}
                          onChange={(e) => updateExample(example.id, { prompt: e.target.value })}
                          placeholder="Enter instruction or prompt..."
                          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                          rows={2}
                          enableDictation={true}
                        />
                      </div>
                      <div>
                        <label className="block text-xs mb-1">Completion</label>
                        <TextInputWithDictation
                          multiline
                          value={example.completion || ''}
                          onChange={(e) => updateExample(example.id, { completion: e.target.value })}
                          placeholder="Enter expected completion..."
                          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                          rows={3}
                          enableDictation={true}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={addExample}
              className="w-full py-3 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
            >
              + Add Example
            </button>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <div className="text-sm font-medium mb-2">Dataset Stats</div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{examples.length}</div>
                  <div className="text-xs text-gray-400">Examples</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">
                    {examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0).toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-400">Total Tokens</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">
                    {examples.length > 0
                      ? Math.round(examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0) / examples.length)
                      : 0
                    }
                  </div>
                  <div className="text-xs text-gray-400">Avg Tokens</div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={examples.length >= (provider?.minExamples || 10)}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('upload');
                wizard.updateData('examples', examples);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'validation':
        const validation = validateExamples();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Format Validation</h2>
              <p className="text-gray-400">Check if your dataset meets all requirements</p>
            </div>

            <div className={`p-6 rounded-lg border-2 ${
              validation.isValid
                ? 'bg-green-900/20 border-green-800'
                : 'bg-red-900/20 border-red-800'
            }`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">{validation.isValid ? '✅' : '❌'}</div>
                <div>
                  <div className="text-xl font-bold">
                    {validation.isValid ? 'Validation Passed' : 'Validation Failed'}
                  </div>
                  <div className="text-sm text-gray-400">
                    {validation.isValid
                      ? 'Your dataset meets all requirements'
                      : 'Please fix the errors below'
                    }
                  </div>
                </div>
              </div>

              {validation.errors.length > 0 && (
                <div className="mb-4">
                  <div className="font-semibold text-red-400 mb-2">Errors:</div>
                  <ul className="space-y-1 text-sm">
                    {validation.errors.map((error, idx) => (
                      <li key={idx} className="flex gap-2">
                        <span>•</span>
                        <span>{error}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {validation.warnings.length > 0 && (
                <div>
                  <div className="font-semibold text-yellow-400 mb-2">Warnings:</div>
                  <ul className="space-y-1 text-sm">
                    {validation.warnings.map((warning, idx) => (
                      <li key={idx} className="flex gap-2">
                        <span>•</span>
                        <span>{warning}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold mb-3">Validation Checklist</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span>{examples.length >= (getProvider()?.minExamples || 10) ? '✅' : '❌'}</span>
                  <span>Minimum examples requirement</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>{validation.errors.length === 0 ? '✅' : '❌'}</span>
                  <span>Format compliance</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>{examples.every(ex => calculateExampleTokens(ex) < 8000) ? '✅' : '⚠️'}</span>
                  <span>Token limits</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>{examples.every(ex => {
                    if (ex.messages) {
                      return ex.messages.every(m => m.content.trim().length > 0);
                    }
                    return ex.prompt && ex.completion && ex.prompt.trim() && ex.completion.trim();
                  }) ? '✅' : '⚠️'}</span>
                  <span>Content completeness</span>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={validation.isValid}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                if (validation.isValid) {
                  setValidationResult(validation);
                  wizard.completeStep('validation');
                  wizard.updateData('validation', validation);
                  wizard.nextStep();
                } else {
                  toast.error('Please fix validation errors before continuing');
                }
              }}
            />
          </div>
        );

      case 'quality':
        const quality = calculateQualityMetrics();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Quality Assessment</h2>
              <p className="text-gray-400">Analyze your dataset quality and diversity</p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <div className="text-center mb-6">
                <div className="text-5xl font-bold mb-2">
                  {Math.round(quality.overallScore)}%
                </div>
                <div className="text-gray-400">Overall Quality Score</div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Average Length</span>
                    <span className="text-sm font-semibold">{Math.round(quality.avgLength)} tokens</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(quality.avgLength / 200 * 100, 100)}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Diversity Score</span>
                    <span className="text-sm font-semibold">{Math.round(quality.diversity)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-secondary h-2 rounded-full transition-all"
                      style={{ width: `${quality.diversity}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Completeness</span>
                    <span className="text-sm font-semibold">{Math.round(quality.completeness)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${quality.completeness}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Shortest Example</div>
                <div className="text-2xl font-bold">
                  {Math.min(...examples.map(ex => calculateExampleTokens(ex)))} tokens
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Longest Example</div>
                <div className="text-2xl font-bold">
                  {Math.max(...examples.map(ex => calculateExampleTokens(ex)))} tokens
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Total Dataset</div>
                <div className="text-2xl font-bold">
                  {examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0).toLocaleString()}
                </div>
              </div>
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">💡</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Quality Tips</div>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Aim for 50+ diverse examples for best results</li>
                    <li>• Keep examples focused on your specific use case</li>
                    <li>• Balance example length (too short or too long can hurt performance)</li>
                    <li>• Include edge cases and challenging scenarios</li>
                  </ul>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={true}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                setQualityMetrics(quality);
                wizard.completeStep('quality');
                wizard.updateData('quality', quality);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'cost':
        const cost = calculateCost();
        const totalTokens = examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0);

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Cost Estimation</h2>
              <p className="text-gray-400">Estimate training costs and configure hyperparameters</p>
            </div>

            <div className="bg-gradient-to-br from-primary/20 to-secondary/20 p-6 rounded-lg border border-primary/50">
              <div className="text-center mb-4">
                <div className="text-sm text-gray-400 mb-1">Estimated Total Cost</div>
                <div className="text-4xl font-bold">${cost.total.toFixed(2)}</div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-sm text-gray-400">Training</div>
                  <div className="text-2xl font-semibold">${cost.training.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Monthly Inference</div>
                  <div className="text-2xl font-semibold">${cost.inference.toFixed(2)}</div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold mb-4">Training Configuration</h3>

              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm">Epochs</label>
                    <span className="text-sm font-semibold">{epochs}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={epochs}
                    onChange={(e) => setEpochs(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-xs text-gray-400 mt-1">
                    More epochs = better training but higher cost
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm">Learning Rate Multiplier</label>
                    <span className="text-sm font-semibold">{learningRate}</span>
                  </div>
                  <input
                    type="range"
                    min="0.00001"
                    max="0.001"
                    step="0.00001"
                    value={learningRate}
                    onChange={(e) => setLearningRate(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-xs text-gray-400 mt-1">
                    Typical range: 0.0001 to 0.001
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm">Batch Size</label>
                    <span className="text-sm font-semibold">{batchSize}</span>
                  </div>
                  <select
                    value={batchSize}
                    onChange={(e) => setBatchSize(Number(e.target.value))}
                    className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary"
                  >
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="4">4</option>
                    <option value="8">8</option>
                    <option value="16">16</option>
                  </select>
                  <div className="text-xs text-gray-400 mt-1">
                    Larger batch sizes train faster but use more memory
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <h3 className="font-semibold mb-3">Cost Breakdown</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total tokens:</span>
                  <span className="font-medium">{totalTokens.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Tokens with epochs:</span>
                  <span className="font-medium">{(totalTokens * epochs).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Cost per million tokens:</span>
                  <span className="font-medium">${getModel()?.trainCost.toFixed(2)}</span>
                </div>
                <div className="border-t border-gray-700 pt-2 mt-2 flex justify-between">
                  <span className="font-semibold">Training cost:</span>
                  <span className="font-semibold text-primary">${cost.training.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">⚠️</div>
                <div>
                  <div className="font-semibold text-yellow-400 mb-1">Cost Estimate Notice</div>
                  <div className="text-sm text-gray-300">
                    These are estimates based on current pricing. Actual costs may vary.
                    Inference costs assume 1,000 requests per month with 1,000 tokens each.
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={true}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('cost');
                wizard.updateData('cost', cost);
                wizard.updateData('epochs', epochs);
                wizard.updateData('learningRate', learningRate);
                wizard.updateData('batchSize', batchSize);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'export':
        const jsonlContent = generateJSONL();
        const configContent = JSON.stringify(generateConfig(), null, 2);

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Export Dataset</h2>
              <p className="text-gray-400">Download your formatted dataset and configuration</p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Export Summary</h3>
                <button
                  onClick={() => setShowOutput(!showOutput)}
                  className="text-sm text-primary hover:text-primary/80"
                >
                  {showOutput ? 'Hide' : 'Show'} Preview
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{examples.length}</div>
                  <div className="text-xs text-gray-400">Examples</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    {examples.reduce((sum, ex) => sum + calculateExampleTokens(ex), 0).toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-400">Tokens</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{qualityMetrics?.overallScore.toFixed(0)}%</div>
                  <div className="text-xs text-gray-400">Quality</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">${calculateCost().total.toFixed(2)}</div>
                  <div className="text-xs text-gray-400">Est. Cost</div>
                </div>
              </div>

              {showOutput && (
                <div className="space-y-3">
                  <div>
                    <div className="text-sm font-medium mb-2">Training Data (JSONL)</div>
                    <pre className="bg-gray-900 p-4 rounded text-xs overflow-x-auto max-h-48 overflow-y-auto">
                      {jsonlContent.split('\n').slice(0, 3).join('\n')}
                      {examples.length > 3 && '\n... (more examples)'}
                    </pre>
                  </div>
                  <div>
                    <div className="text-sm font-medium mb-2">Configuration (JSON)</div>
                    <pre className="bg-gray-900 p-4 rounded text-xs overflow-x-auto max-h-48 overflow-y-auto">
                      {configContent}
                    </pre>
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-3">
              <button
                onClick={() => {
                  const blob = new Blob([jsonlContent], { type: 'application/jsonl' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `training_data_${Date.now()}.jsonl`;
                  a.click();
                  toast.success('Training data downloaded');
                }}
                className="w-full px-6 py-3 bg-primary text-white hover:opacity-90 rounded-lg font-medium transition-opacity"
              >
                Download Training Data (JSONL)
              </button>

              <button
                onClick={() => {
                  const blob = new Blob([configContent], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `training_config_${Date.now()}.json`;
                  a.click();
                  toast.success('Configuration downloaded');
                }}
                className="w-full px-6 py-3 bg-secondary text-white hover:opacity-90 rounded-lg font-medium transition-opacity"
              >
                Download Configuration (JSON)
              </button>
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">📚</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Next Steps</div>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>1. Upload training_data.jsonl to your model provider</li>
                    <li>2. Configure training using the settings from the config file</li>
                    <li>3. Start the fine-tuning job and monitor progress</li>
                    <li>4. Test your fine-tuned model with validation examples</li>
                    <li>5. Deploy to production once performance is satisfactory</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => {
                  wizard.clearData();
                  setExamples([]);
                  setSelectedProvider('');
                  setSelectedModel('');
                  setValidationResult(null);
                  setQualityMetrics(null);
                  wizard.goToStep(0);
                  toast.success('Starting new fine-tuning preparation');
                }}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                Create Another Dataset
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('export');
                  toast.success('Fine-tuning preparation complete!');
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
