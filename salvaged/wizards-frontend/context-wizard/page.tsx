'use client';

import { useState, useMemo } from 'react';
import { toast } from 'react-hot-toast';
import WizardLayout from '@/components/wizard/WizardLayout';
import WizardNavigation from '@/components/wizard/WizardNavigation';
import WizardExport from '@/components/wizard/WizardExport';
import { useWizard } from '@/hooks/useWizard';
import { WizardConfig } from '@/types/wizard';
import TextInputWithDictation from '@/components/ui/TextInputWithDictation';

const wizardConfig: WizardConfig = {
  id: 'context-window-optimizer',
  title: 'Context Window Optimizer Wizard',
  description: 'Maximize token efficiency and reduce costs with intelligent text optimization',
  icon: '🎯',
  category: 'optimization',
  estimatedTime: '10-15 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Getting started', isComplete: false },
    { id: 'input', title: 'Input Text', description: 'Paste your text', isComplete: false },
    { id: 'analysis', title: 'Token Analysis', description: 'View breakdown', isComplete: false },
    { id: 'strategy', title: 'Strategy', description: 'Compression method', isComplete: false },
    { id: 'priority', title: 'Priority', description: 'Keep/cut decisions', isComplete: false },
    { id: 'output', title: 'Optimized Output', description: 'View results', isComplete: false },
    { id: 'comparison', title: 'Cost Comparison', description: 'Savings estimate', isComplete: false },
  ],
  exportFormats: [
    { id: 'text', label: 'Plain Text', extension: 'txt', mimeType: 'text/plain' },
    { id: 'markdown', label: 'Markdown', extension: 'md', mimeType: 'text/markdown' },
    { id: 'json', label: 'JSON', extension: 'json', mimeType: 'application/json' },
  ],
};

const SUMMARIZATION_STRATEGIES = [
  {
    value: 'extractive',
    label: 'Extractive Summarization',
    description: 'Select and preserve the most important sentences verbatim',
    compressionRate: 0.6,
  },
  {
    value: 'abstractive',
    label: 'Abstractive Summarization',
    description: 'Rewrite content in a more concise form while preserving meaning',
    compressionRate: 0.4,
  },
  {
    value: 'sliding-window',
    label: 'Sliding Window',
    description: 'Keep most recent content, useful for conversational contexts',
    compressionRate: 0.5,
  },
  {
    value: 'hierarchical',
    label: 'Hierarchical Compression',
    description: 'Create multi-level summaries with varying detail levels',
    compressionRate: 0.3,
  },
];

const MODEL_PRICING = {
  'gpt-4': { input: 0.03, output: 0.06, name: 'GPT-4' },
  'gpt-3.5-turbo': { input: 0.0015, output: 0.002, name: 'GPT-3.5 Turbo' },
  'claude-3-opus': { input: 0.015, output: 0.075, name: 'Claude 3 Opus' },
  'claude-3-sonnet': { input: 0.003, output: 0.015, name: 'Claude 3 Sonnet' },
  'claude-3-haiku': { input: 0.00025, output: 0.00125, name: 'Claude 3 Haiku' },
};

export default function ContextWizard() {
  const wizard = useWizard(wizardConfig);

  // Form data
  const [inputText, setInputText] = useState('');
  const [strategy, setStrategy] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo');
  const [priorities, setPriorities] = useState<Record<string, number>>({});
  const [optimizedText, setOptimizedText] = useState('');

  // Token counting function (estimate: words * 1.3)
  const countTokens = (text: string): number => {
    const words = text.trim().split(/\s+/).length;
    return Math.ceil(words * 1.3);
  };

  // Analyze text sections
  const textSections = useMemo(() => {
    if (!inputText) return [];

    const paragraphs = inputText.split('\n\n').filter(p => p.trim());
    return paragraphs.map((paragraph, index) => ({
      id: `section-${index}`,
      content: paragraph,
      tokens: countTokens(paragraph),
      priority: priorities[`section-${index}`] || 3,
    }));
  }, [inputText, priorities]);

  // Token analysis
  const tokenAnalysis = useMemo(() => {
    const total = countTokens(inputText);
    const sections = textSections.map(s => ({
      name: `Section ${textSections.indexOf(s) + 1}`,
      tokens: s.tokens,
      percentage: (s.tokens / total) * 100,
    }));

    return {
      total,
      sections,
      avgSectionSize: total / sections.length || 0,
    };
  }, [inputText, textSections]);

  // Generate optimized text based on strategy
  const generateOptimizedText = () => {
    const selectedStrategy = SUMMARIZATION_STRATEGIES.find(s => s.value === strategy);
    if (!selectedStrategy || !inputText) return '';

    const compressionRate = selectedStrategy.compressionRate;

    // Sort sections by priority (higher priority = keep)
    const sortedSections = [...textSections].sort((a, b) => b.priority - a.priority);

    let optimized = '';
    let currentTokens = 0;
    const targetTokens = Math.floor(tokenAnalysis.total * compressionRate);

    for (const section of sortedSections) {
      if (currentTokens + section.tokens <= targetTokens) {
        optimized += section.content + '\n\n';
        currentTokens += section.tokens;
      } else if (currentTokens < targetTokens) {
        // Partial inclusion for extractive
        if (strategy === 'extractive') {
          const sentences = section.content.split(/[.!?]+/).filter(s => s.trim());
          for (const sentence of sentences) {
            const sentenceTokens = countTokens(sentence);
            if (currentTokens + sentenceTokens <= targetTokens) {
              optimized += sentence.trim() + '. ';
              currentTokens += sentenceTokens;
            } else {
              break;
            }
          }
          optimized += '\n\n';
        }
        break;
      }
    }

    return optimized.trim();
  };

  // Calculate cost savings
  const calculateCosts = (tokens: number) => {
    const model = MODEL_PRICING[selectedModel as keyof typeof MODEL_PRICING];
    // Cost per 1K tokens
    return (tokens / 1000) * model.input;
  };

  const renderStep = () => {
    const currentStep = wizardConfig.steps[wizard.currentStep];

    switch (currentStep.id) {
      case 'welcome':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🎯</div>
              <h2 className="text-3xl font-bold mb-4">Context Window Optimizer</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Maximize your token efficiency and reduce AI costs. This wizard helps you compress
                and optimize text while preserving the most important information.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">📊</div>
                <h3 className="font-semibold mb-2">Token Analysis</h3>
                <p className="text-sm text-gray-400">Real-time token counting and breakdown</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">⚡</div>
                <h3 className="font-semibold mb-2">Smart Compression</h3>
                <p className="text-sm text-gray-400">Multiple optimization strategies</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">💰</div>
                <h3 className="font-semibold mb-2">Cost Savings</h3>
                <p className="text-sm text-gray-400">Calculate your API cost reduction</p>
              </div>
            </div>

            <button
              onClick={() => {
                wizard.completeStep('welcome');
                wizard.nextStep();
              }}
              className="w-full mt-8 px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-medium text-lg hover:opacity-90 transition-opacity"
            >
              Start Optimizing →
            </button>
          </div>
        );

      case 'input':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Input Your Text</h2>
              <p className="text-gray-400">Paste the text you want to optimize for token efficiency</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Text to Optimize *</label>
              <TextInputWithDictation
                multiline
                rows={15}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Paste your text here... This could be conversation history, documentation, context for a prompt, or any text you want to compress while preserving meaning."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none font-mono text-sm"
                enableDictation={true}
              />
              {inputText && (
                <div className="flex gap-4 mt-2 text-sm">
                  <span className="text-gray-400">
                    Characters: <span className="text-white font-semibold">{inputText.length}</span>
                  </span>
                  <span className="text-gray-400">
                    Words: <span className="text-white font-semibold">{inputText.trim().split(/\s+/).length}</span>
                  </span>
                  <span className="text-gray-400">
                    Est. Tokens: <span className="text-white font-semibold">{countTokens(inputText)}</span>
                  </span>
                </div>
              )}
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">💡</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Pro Tip</div>
                  <div className="text-sm text-gray-300">
                    Longer text provides better optimization opportunities. Include at least a few paragraphs for meaningful results.
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={inputText.length > 100}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('input');
                wizard.updateData('inputText', inputText);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'analysis':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Token Analysis</h2>
              <p className="text-gray-400">Detailed breakdown of your text's token usage</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Total Tokens</div>
                <div className="text-4xl font-bold text-primary">{tokenAnalysis.total}</div>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Sections</div>
                <div className="text-4xl font-bold">{textSections.length}</div>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Avg Section Size</div>
                <div className="text-4xl font-bold">{Math.round(tokenAnalysis.avgSectionSize)}</div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold mb-4">Section Breakdown</h3>
              <div className="space-y-3">
                {tokenAnalysis.sections.map((section, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{section.name}</span>
                      <span className="text-sm text-gray-400">
                        {section.tokens} tokens ({section.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-primary to-secondary h-2 rounded-full transition-all"
                        style={{ width: `${section.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold mb-3">Token Distribution Insights</h3>
              <div className="space-y-2 text-sm">
                {tokenAnalysis.sections.length > 10 && (
                  <div className="flex gap-2 text-yellow-400">
                    <span>⚠️</span>
                    <span>Many small sections detected. Consider combining related content.</span>
                  </div>
                )}
                {tokenAnalysis.total > 8000 && (
                  <div className="flex gap-2 text-yellow-400">
                    <span>⚠️</span>
                    <span>Large token count. This may exceed some model context windows.</span>
                  </div>
                )}
                {tokenAnalysis.avgSectionSize < 50 && (
                  <div className="flex gap-2 text-blue-400">
                    <span>ℹ️</span>
                    <span>Short sections provide fine-grained control over optimization.</span>
                  </div>
                )}
                {tokenAnalysis.total < 1000 && (
                  <div className="flex gap-2 text-green-400">
                    <span>✓</span>
                    <span>Token count is already efficient for most use cases.</span>
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
                wizard.completeStep('analysis');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'strategy':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Choose Optimization Strategy</h2>
              <p className="text-gray-400">Select how you want to compress your text</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {SUMMARIZATION_STRATEGIES.map((strat) => (
                <button
                  key={strat.value}
                  onClick={() => setStrategy(strat.value)}
                  className={`p-6 rounded-lg border-2 transition-all text-left ${
                    strategy === strat.value
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <div className="font-semibold text-lg mb-2">{strat.label}</div>
                  <div className="text-sm text-gray-400 mb-3">{strat.description}</div>
                  <div className="flex items-center gap-2">
                    <div className="text-xs text-gray-500">Target Compression:</div>
                    <div className="text-sm font-semibold text-primary">
                      {Math.round((1 - strat.compressionRate) * 100)}% reduction
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    ~{Math.round(tokenAnalysis.total * strat.compressionRate)} tokens after optimization
                  </div>
                </button>
              ))}
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold mb-3">Strategy Comparison</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-2">Strategy</th>
                      <th className="text-left py-2">Best For</th>
                      <th className="text-left py-2">Preservation</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-400">
                    <tr className="border-b border-gray-700">
                      <td className="py-2">Extractive</td>
                      <td className="py-2">Preserving exact wording</td>
                      <td className="py-2">High accuracy</td>
                    </tr>
                    <tr className="border-b border-gray-700">
                      <td className="py-2">Abstractive</td>
                      <td className="py-2">Maximum compression</td>
                      <td className="py-2">Meaning over form</td>
                    </tr>
                    <tr className="border-b border-gray-700">
                      <td className="py-2">Sliding Window</td>
                      <td className="py-2">Conversations</td>
                      <td className="py-2">Recent context</td>
                    </tr>
                    <tr>
                      <td className="py-2">Hierarchical</td>
                      <td className="py-2">Long documents</td>
                      <td className="py-2">Multi-level detail</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!strategy}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('strategy');
                wizard.updateData('strategy', strategy);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'priority':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Set Section Priorities</h2>
              <p className="text-gray-400">
                Indicate which sections are most important to keep (1 = low priority, 5 = high priority)
              </p>
            </div>

            <div className="space-y-4">
              {textSections.map((section, index) => (
                <div key={section.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex-1">
                      <div className="font-semibold mb-2">
                        Section {index + 1} ({section.tokens} tokens)
                      </div>
                      <div className="text-sm text-gray-400 line-clamp-2">
                        {section.content.substring(0, 150)}...
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-400 mb-1">Priority</div>
                      <div className="text-2xl font-bold text-primary">
                        {priorities[section.id] || 3}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500">Low</span>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={priorities[section.id] || 3}
                      onChange={(e) => {
                        setPriorities({
                          ...priorities,
                          [section.id]: parseInt(e.target.value),
                        });
                      }}
                      className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary"
                    />
                    <span className="text-xs text-gray-500">High</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">💡</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Priority Tips</div>
                  <div className="text-sm text-gray-300">
                    High priority sections will be preserved first. Set key information to 5,
                    supporting details to 3, and optional context to 1-2.
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
                wizard.completeStep('priority');
                wizard.updateData('priorities', priorities);
                const optimized = generateOptimizedText();
                setOptimizedText(optimized);
                wizard.updateData('optimizedText', optimized);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'output':
        const optimized = optimizedText || generateOptimizedText();
        const optimizedTokens = countTokens(optimized);
        const reduction = ((1 - optimizedTokens / tokenAnalysis.total) * 100).toFixed(1);

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Optimized Output</h2>
              <p className="text-gray-400">Review your compressed text</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Original Tokens</div>
                <div className="text-3xl font-bold">{tokenAnalysis.total}</div>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Optimized Tokens</div>
                <div className="text-3xl font-bold text-primary">{optimizedTokens}</div>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Reduction</div>
                <div className="text-3xl font-bold text-green-400">{reduction}%</div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Optimized Text</h3>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(optimized);
                    toast.success('Copied to clipboard!');
                  }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors"
                >
                  Copy
                </button>
              </div>
              <div className="bg-gray-900 p-4 rounded-lg max-h-96 overflow-y-auto">
                <pre className="text-sm whitespace-pre-wrap text-gray-300 font-mono">
                  {optimized}
                </pre>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold mb-4">Before / After Comparison</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-400 mb-2">Original</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Tokens:</span>
                      <span className="font-semibold">{tokenAnalysis.total}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Characters:</span>
                      <span className="font-semibold">{inputText.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Sections:</span>
                      <span className="font-semibold">{textSections.length}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-2">Optimized</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Tokens:</span>
                      <span className="font-semibold text-primary">{optimizedTokens}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Characters:</span>
                      <span className="font-semibold text-primary">{optimized.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Reduction:</span>
                      <span className="font-semibold text-green-400">{reduction}%</span>
                    </div>
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
                wizard.completeStep('output');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'comparison':
        const finalOptimized = optimizedText || generateOptimizedText();
        const finalOptimizedTokens = countTokens(finalOptimized);
        const originalCost = calculateCosts(tokenAnalysis.total);
        const optimizedCost = calculateCosts(finalOptimizedTokens);
        const costSavings = originalCost - optimizedCost;
        const savingsPercent = ((costSavings / originalCost) * 100).toFixed(1);

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Cost Comparison & Savings</h2>
              <p className="text-gray-400">See how much you can save on API costs</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Select Model for Cost Calculation</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
              >
                {Object.entries(MODEL_PRICING).map(([key, model]) => (
                  <option key={key} value={key}>
                    {model.name} (${model.input}/1K input tokens)
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Original Cost</div>
                <div className="text-3xl font-bold">${originalCost.toFixed(4)}</div>
                <div className="text-xs text-gray-500 mt-1">per request</div>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Optimized Cost</div>
                <div className="text-3xl font-bold text-primary">${optimizedCost.toFixed(4)}</div>
                <div className="text-xs text-gray-500 mt-1">per request</div>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Savings</div>
                <div className="text-3xl font-bold text-green-400">${costSavings.toFixed(4)}</div>
                <div className="text-xs text-gray-500 mt-1">{savingsPercent}% reduction</div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold mb-4">Projected Savings Calculator</h3>
              <div className="space-y-4">
                {[100, 1000, 10000, 100000].map((volume) => {
                  const originalTotal = originalCost * volume;
                  const optimizedTotal = optimizedCost * volume;
                  const totalSavings = originalTotal - optimizedTotal;

                  return (
                    <div key={volume} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-0">
                      <div>
                        <div className="font-medium">{volume.toLocaleString()} requests/month</div>
                        <div className="text-sm text-gray-400">
                          {(volume / 30).toFixed(0)} requests/day
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-green-400 text-lg">
                          ${totalSavings.toFixed(2)} saved
                        </div>
                        <div className="text-sm text-gray-400">
                          ${optimizedTotal.toFixed(2)} vs ${originalTotal.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-800 rounded-lg p-6">
              <div className="flex gap-4">
                <div className="text-4xl">💰</div>
                <div>
                  <div className="font-semibold text-green-400 text-lg mb-2">Cost Optimization Summary</div>
                  <div className="space-y-1 text-sm text-gray-300">
                    <div>
                      Token reduction: <span className="font-semibold text-white">
                        {tokenAnalysis.total} → {finalOptimizedTokens} tokens
                      </span>
                    </div>
                    <div>
                      Per-request savings: <span className="font-semibold text-white">
                        ${costSavings.toFixed(4)} ({savingsPercent}%)
                      </span>
                    </div>
                    <div>
                      At 1000 requests/month: <span className="font-semibold text-white">
                        ${(costSavings * 1000).toFixed(2)} saved monthly
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <WizardExport
              formats={wizardConfig.exportFormats}
              content={finalOptimized}
              filename={`optimized-text-${Date.now()}`}
            />

            <div className="flex gap-4">
              <button
                onClick={() => {
                  setInputText('');
                  setStrategy('');
                  setPriorities({});
                  setOptimizedText('');
                  wizard.clearData();
                  wizard.goToStep(0);
                }}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                Optimize Another Text
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('comparison');
                  toast.success('Optimization complete!');
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
