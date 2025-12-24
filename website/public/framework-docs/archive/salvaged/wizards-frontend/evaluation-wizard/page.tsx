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
  id: 'evaluation-metrics',
  title: 'Evaluation Metrics Wizard',
  description: 'Design comprehensive test suites and success criteria for AI models',
  icon: '📊',
  category: 'analysis',
  estimatedTime: '15-20 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Getting started', isComplete: false },
    { id: 'objectives', title: 'Objectives', description: 'Define goals', isComplete: false },
    { id: 'metrics', title: 'Metrics', description: 'Choose measures', isComplete: false },
    { id: 'test-cases', title: 'Test Cases', description: 'Create tests', isComplete: false },
    { id: 'benchmarks', title: 'Benchmarks', description: 'Set targets', isComplete: false },
    { id: 'implementation', title: 'Implementation', description: 'How to test', isComplete: false },
    { id: 'review', title: 'Review', description: 'Final plan', isComplete: false },
  ],
  exportFormats: [
    { id: 'markdown', label: 'Markdown', extension: 'md', mimeType: 'text/markdown' },
    { id: 'json', label: 'JSON Test Suite', extension: 'json', mimeType: 'application/json' },
    { id: 'yaml', label: 'YAML Config', extension: 'yaml', mimeType: 'text/yaml' },
  ],
};

const METRIC_TYPES = [
  {
    id: 'accuracy',
    name: 'Accuracy',
    description: 'Percentage of correct predictions',
    category: 'Performance',
  },
  {
    id: 'precision',
    name: 'Precision',
    description: 'Ratio of true positives to predicted positives',
    category: 'Performance',
  },
  {
    id: 'recall',
    name: 'Recall/Sensitivity',
    description: 'Ratio of true positives to actual positives',
    category: 'Performance',
  },
  {
    id: 'f1',
    name: 'F1 Score',
    description: 'Harmonic mean of precision and recall',
    category: 'Performance',
  },
  {
    id: 'latency',
    name: 'Response Latency',
    description: 'Time to generate response',
    category: 'Speed',
  },
  {
    id: 'throughput',
    name: 'Throughput',
    description: 'Requests processed per second',
    category: 'Speed',
  },
  {
    id: 'relevance',
    name: 'Response Relevance',
    description: 'How well responses address the query',
    category: 'Quality',
  },
  {
    id: 'coherence',
    name: 'Coherence',
    description: 'Logical flow and consistency',
    category: 'Quality',
  },
  {
    id: 'factuality',
    name: 'Factual Accuracy',
    description: 'Correctness of information',
    category: 'Quality',
  },
  {
    id: 'safety',
    name: 'Safety Score',
    description: 'Absence of harmful content',
    category: 'Safety',
  },
  {
    id: 'bias',
    name: 'Bias Detection',
    description: 'Fairness across demographics',
    category: 'Safety',
  },
  {
    id: 'cost',
    name: 'Cost per Request',
    description: 'API costs per interaction',
    category: 'Operations',
  },
];

const TEST_CASE_TYPES = [
  { id: 'happy-path', name: 'Happy Path', description: 'Normal expected usage' },
  { id: 'edge-case', name: 'Edge Cases', description: 'Boundary conditions' },
  { id: 'error-handling', name: 'Error Handling', description: 'Invalid inputs' },
  { id: 'stress-test', name: 'Stress Test', description: 'High load scenarios' },
  { id: 'adversarial', name: 'Adversarial', description: 'Attempts to break the system' },
];

export default function EvaluationWizard() {
  const wizard = useWizard(wizardConfig);

  // State
  const [objective, setObjective] = useState('');
  const [useCaseDescription, setUseCaseDescription] = useState('');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [customMetric, setCustomMetric] = useState({ name: '', description: '', target: '' });
  const [testCases, setTestCases] = useState<Array<{
    type: string;
    name: string;
    input: string;
    expectedOutput: string;
    successCriteria: string;
  }>>([]);
  const [benchmarks, setBenchmarks] = useState<Record<string, string>>({});
  const [testingApproach, setTestingApproach] = useState('');
  const [automationLevel, setAutomationLevel] = useState('');

  const toggleMetric = (metricId: string) => {
    setSelectedMetrics(prev =>
      prev.includes(metricId)
        ? prev.filter(id => id !== metricId)
        : [...prev, metricId]
    );
  };

  const generateEvaluationPlan = () => {
    const sections = [];

    sections.push('# AI Evaluation Plan');
    sections.push('');
    sections.push(`Generated: ${new Date().toLocaleDateString()}`);
    sections.push('');

    // Objectives
    sections.push('## Objectives');
    sections.push(objective || 'Define your evaluation objectives...');
    sections.push('');
    if (useCaseDescription) {
      sections.push('### Use Case');
      sections.push(useCaseDescription);
      sections.push('');
    }

    // Metrics
    if (selectedMetrics.length > 0) {
      sections.push('## Evaluation Metrics');
      sections.push('');

      const metricsByCategory: Record<string, typeof METRIC_TYPES> = {};
      selectedMetrics.forEach(id => {
        const metric = METRIC_TYPES.find(m => m.id === id);
        if (metric) {
          if (!metricsByCategory[metric.category]) {
            metricsByCategory[metric.category] = [];
          }
          metricsByCategory[metric.category].push(metric);
        }
      });

      Object.entries(metricsByCategory).forEach(([category, metrics]) => {
        sections.push(`### ${category} Metrics`);
        metrics.forEach(metric => {
          const benchmark = benchmarks[metric.id];
          sections.push(`- **${metric.name}**: ${metric.description}`);
          if (benchmark) {
            sections.push(`  - Target: ${benchmark}`);
          }
        });
        sections.push('');
      });
    }

    // Test Cases
    if (testCases.length > 0) {
      sections.push('## Test Cases');
      sections.push('');

      const casesByType: Record<string, typeof testCases> = {};
      testCases.forEach(tc => {
        if (!casesByType[tc.type]) {
          casesByType[tc.type] = [];
        }
        casesByType[tc.type].push(tc);
      });

      Object.entries(casesByType).forEach(([type, cases]) => {
        const typeInfo = TEST_CASE_TYPES.find(t => t.id === type);
        sections.push(`### ${typeInfo?.name || type}`);
        cases.forEach((tc, index) => {
          sections.push(`#### Test ${index + 1}: ${tc.name}`);
          sections.push(`**Input:** ${tc.input}`);
          sections.push(`**Expected Output:** ${tc.expectedOutput}`);
          sections.push(`**Success Criteria:** ${tc.successCriteria}`);
          sections.push('');
        });
      });
    }

    // Implementation
    if (testingApproach || automationLevel) {
      sections.push('## Implementation');
      if (testingApproach) {
        sections.push('### Testing Approach');
        sections.push(testingApproach);
        sections.push('');
      }
      if (automationLevel) {
        sections.push('### Automation Level');
        sections.push(automationLevel);
        sections.push('');
      }
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
              <div className="text-6xl mb-4">📊</div>
              <h2 className="text-3xl font-bold mb-4">Evaluation Metrics Wizard</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Design a comprehensive evaluation framework to measure and improve your AI model's performance.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🎯</div>
                <h3 className="font-semibold mb-2">Clear Metrics</h3>
                <p className="text-sm text-gray-400">Define measurable success criteria</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🧪</div>
                <h3 className="font-semibold mb-2">Test Cases</h3>
                <p className="text-sm text-gray-400">Create comprehensive test scenarios</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">📈</div>
                <h3 className="font-semibold mb-2">Benchmarks</h3>
                <p className="text-sm text-gray-400">Set performance targets</p>
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

      case 'objectives':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Define Your Objectives</h2>
              <p className="text-gray-400">What are you trying to evaluate and why?</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Primary Evaluation Goal *</label>
              <textarea
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                placeholder="e.g., Measure the accuracy and response quality of our customer support chatbot..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                rows={4}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Use Case Description <span className="text-gray-500">(Optional)</span>
              </label>
              <textarea
                value={useCaseDescription}
                onChange={(e) => setUseCaseDescription(e.target.value)}
                placeholder="Describe how the AI system is used, who uses it, and what it needs to accomplish..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                rows={5}
              />
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={objective.length > 10}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('objectives');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'metrics':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Select Evaluation Metrics</h2>
              <p className="text-gray-400">Choose the metrics that matter for your use case</p>
            </div>

            <div className="space-y-6">
              {['Performance', 'Speed', 'Quality', 'Safety', 'Operations'].map(category => {
                const categoryMetrics = METRIC_TYPES.filter(m => m.category === category);
                if (categoryMetrics.length === 0) return null;

                return (
                  <div key={category}>
                    <h3 className="font-semibold mb-3">{category}</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {categoryMetrics.map(metric => (
                        <button
                          key={metric.id}
                          onClick={() => toggleMetric(metric.id)}
                          className={`p-4 rounded-lg border-2 text-left transition-all ${
                            selectedMetrics.includes(metric.id)
                              ? 'border-primary bg-primary/10'
                              : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="font-semibold mb-1">{metric.name}</div>
                              <div className="text-sm text-gray-400">{metric.description}</div>
                            </div>
                            {selectedMetrics.includes(metric.id) && (
                              <svg className="w-5 h-5 text-primary flex-shrink-0 ml-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={selectedMetrics.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('metrics');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'test-cases':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Create Test Cases</h2>
              <p className="text-gray-400">Define specific scenarios to evaluate your AI</p>
            </div>

            {testCases.map((testCase, index) => (
              <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-3">
                <div className="flex items-center justify-between">
                  <select
                    value={testCase.type}
                    onChange={(e) => {
                      const newCases = [...testCases];
                      newCases[index].type = e.target.value;
                      setTestCases(newCases);
                    }}
                    className="px-3 py-1.5 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary text-sm"
                  >
                    {TEST_CASE_TYPES.map(type => (
                      <option key={type.id} value={type.id}>{type.name}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => setTestCases(testCases.filter((_, i) => i !== index))}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Remove
                  </button>
                </div>

                <input
                  type="text"
                  value={testCase.name}
                  onChange={(e) => {
                    const newCases = [...testCases];
                    newCases[index].name = e.target.value;
                    setTestCases(newCases);
                  }}
                  placeholder="Test case name"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary"
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Input</label>
                    <textarea
                      value={testCase.input}
                      onChange={(e) => {
                        const newCases = [...testCases];
                        newCases[index].input = e.target.value;
                        setTestCases(newCases);
                      }}
                      className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Expected Output</label>
                    <textarea
                      value={testCase.expectedOutput}
                      onChange={(e) => {
                        const newCases = [...testCases];
                        newCases[index].expectedOutput = e.target.value;
                        setTestCases(newCases);
                      }}
                      className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                      rows={3}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-gray-400 mb-1">Success Criteria</label>
                  <input
                    type="text"
                    value={testCase.successCriteria}
                    onChange={(e) => {
                      const newCases = [...testCases];
                      newCases[index].successCriteria = e.target.value;
                      setTestCases(newCases);
                    }}
                    placeholder="How to determine if this test passes..."
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary text-sm"
                  />
                </div>
              </div>
            ))}

            <button
              onClick={() => setTestCases([...testCases, {
                type: 'happy-path',
                name: '',
                input: '',
                expectedOutput: '',
                successCriteria: '',
              }])}
              className="w-full py-3 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
            >
              + Add Test Case
            </button>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={testCases.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('test-cases');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'benchmarks':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Set Performance Benchmarks</h2>
              <p className="text-gray-400">Define target values for your selected metrics</p>
            </div>

            <div className="space-y-4">
              {selectedMetrics.map(metricId => {
                const metric = METRIC_TYPES.find(m => m.id === metricId);
                if (!metric) return null;

                return (
                  <div key={metricId} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <div className="font-semibold">{metric.name}</div>
                        <div className="text-sm text-gray-400">{metric.description}</div>
                      </div>
                    </div>
                    <input
                      type="text"
                      value={benchmarks[metricId] || ''}
                      onChange={(e) => setBenchmarks({ ...benchmarks, [metricId]: e.target.value })}
                      placeholder="e.g., >95%, <200ms, 4/5 stars"
                      className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary"
                    />
                  </div>
                );
              })}
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">💡</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Pro Tip</div>
                  <div className="text-sm text-gray-300">
                    Set realistic but ambitious targets. Consider having minimum, target, and stretch goals.
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={Object.keys(benchmarks).length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('benchmarks');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'implementation':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Implementation Plan</h2>
              <p className="text-gray-400">How will you conduct these evaluations?</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Testing Approach</label>
              <textarea
                value={testingApproach}
                onChange={(e) => setTestingApproach(e.target.value)}
                placeholder="Describe your testing methodology, tools, frequency, and process..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                rows={5}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Automation Level</label>
              <div className="space-y-2">
                {[
                  { value: 'manual', label: 'Manual Testing', description: 'Human evaluation for each test' },
                  { value: 'semi', label: 'Semi-Automated', description: 'Automated collection, manual review' },
                  { value: 'automated', label: 'Fully Automated', description: 'Continuous automated testing' },
                ].map(option => (
                  <button
                    key={option.value}
                    onClick={() => setAutomationLevel(option.value)}
                    className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                      automationLevel === option.value
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <div className="font-semibold mb-1">{option.label}</div>
                    <div className="text-sm text-gray-400">{option.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!testingApproach && !!automationLevel}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('implementation');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'review':
        const finalPlan = generateEvaluationPlan();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Your Evaluation Plan</h2>
              <p className="text-gray-400">Review and export your comprehensive evaluation framework</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Metrics</div>
                <div className="text-2xl font-bold">{selectedMetrics.length}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Test Cases</div>
                <div className="text-2xl font-bold">{testCases.length}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Benchmarks</div>
                <div className="text-2xl font-bold">{Object.keys(benchmarks).length}</div>
              </div>
            </div>

            <WizardExport
              formats={wizardConfig.exportFormats}
              content={finalPlan}
              filename={`evaluation-plan-${Date.now()}`}
            />

            <div className="flex gap-4">
              <button
                onClick={() => wizard.goToStep(0)}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                Create Another Plan
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('review');
                  toast.success('Evaluation plan complete!');
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
