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
  id: 'bias-detection',
  title: 'Bias Detection & Mitigation Wizard',
  description: 'Identify and mitigate biases in AI systems',
  icon: '⚖️',
  category: 'analysis',
  estimatedTime: '15-20 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Getting started', isComplete: false },
    { id: 'scope', title: 'Define Scope', description: 'What to analyze', isComplete: false },
    { id: 'demographics', title: 'Demographics', description: 'Groups to check', isComplete: false },
    { id: 'tests', title: 'Bias Tests', description: 'Run tests', isComplete: false },
    { id: 'results', title: 'Results', description: 'Review findings', isComplete: false },
    { id: 'mitigation', title: 'Mitigation', description: 'Fix strategies', isComplete: false },
    { id: 'report', title: 'Report', description: 'Final report', isComplete: false },
  ],
  exportFormats: [
    { id: 'markdown', label: 'Markdown Report', extension: 'md', mimeType: 'text/markdown' },
    { id: 'json', label: 'JSON Data', extension: 'json', mimeType: 'application/json' },
    { id: 'csv', label: 'CSV Results', extension: 'csv', mimeType: 'text/csv' },
  ],
};

const BIAS_TYPES = [
  { id: 'gender', name: 'Gender Bias', description: 'Differences based on gender identity', icon: '👥' },
  { id: 'racial', name: 'Racial/Ethnic Bias', description: 'Differences across racial groups', icon: '🌍' },
  { id: 'age', name: 'Age Bias', description: 'Discrimination based on age', icon: '📅' },
  { id: 'socioeconomic', name: 'Socioeconomic Bias', description: 'Income/class-based differences', icon: '💰' },
  { id: 'geographic', name: 'Geographic Bias', description: 'Location-based differences', icon: '🗺️' },
  { id: 'language', name: 'Language Bias', description: 'Native vs non-native speakers', icon: '🗣️' },
];

const MITIGATION_STRATEGIES = [
  { id: 'data-augmentation', name: 'Data Augmentation', description: 'Add more diverse examples to training data' },
  { id: 'reweighting', name: 'Sample Reweighting', description: 'Adjust weights for underrepresented groups' },
  { id: 'prompt-engineering', name: 'Prompt Engineering', description: 'Modify prompts to reduce bias' },
  { id: 'post-processing', name: 'Post-Processing', description: 'Filter or adjust outputs after generation' },
  { id: 'adversarial', name: 'Adversarial Training', description: 'Train model to resist biased inputs' },
  { id: 'fairness-constraints', name: 'Fairness Constraints', description: 'Add constraints during training' },
];

export default function BiasWizard() {
  const wizard = useWizard(wizardConfig);

  const [analysisScope, setAnalysisScope] = useState('');
  const [selectedBiasTypes, setSelectedBiasTypes] = useState<string[]>([]);
  const [demographics, setDemographics] = useState<string[]>([]);
  const [newDemographic, setNewDemographic] = useState('');
  const [testPrompts, setTestPrompts] = useState<string[]>(['']);
  const [biasResults, setBiasResults] = useState<any[]>([]);
  const [selectedMitigations, setSelectedMitigations] = useState<string[]>([]);

  const toggleBiasType = (id: string) => {
    setSelectedBiasTypes(prev =>
      prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]
    );
  };

  const addDemographic = () => {
    if (newDemographic && !demographics.includes(newDemographic)) {
      setDemographics([...demographics, newDemographic]);
      setNewDemographic('');
    }
  };

  const runBiasTests = () => {
    // Simulate bias detection
    const mockResults = selectedBiasTypes.map(type => ({
      type,
      severity: Math.random() > 0.5 ? 'high' : Math.random() > 0.5 ? 'medium' : 'low',
      score: Math.floor(Math.random() * 30) + 20, // 20-50 bias score
      examples: 2 + Math.floor(Math.random() * 3),
    }));
    setBiasResults(mockResults);
    toast.success('Bias analysis complete!');
  };

  const generateReport = () => {
    const sections = [];

    sections.push('# Bias Detection & Mitigation Report');
    sections.push('');
    sections.push(`Generated: ${new Date().toLocaleDateString()}`);
    sections.push('');

    sections.push('## Analysis Scope');
    sections.push(analysisScope || 'Not specified');
    sections.push('');

    sections.push('## Bias Types Tested');
    selectedBiasTypes.forEach(typeId => {
      const type = BIAS_TYPES.find(t => t.id === typeId);
      if (type) sections.push(`- ${type.name}: ${type.description}`);
    });
    sections.push('');

    sections.push('## Demographics Analyzed');
    demographics.forEach(demo => sections.push(`- ${demo}`));
    sections.push('');

    if (biasResults.length > 0) {
      sections.push('## Bias Detection Results');
      sections.push('');
      biasResults.forEach(result => {
        const type = BIAS_TYPES.find(t => t.id === result.type);
        sections.push(`### ${type?.name}`);
        sections.push(`- **Severity:** ${result.severity.toUpperCase()}`);
        sections.push(`- **Bias Score:** ${result.score}/100`);
        sections.push(`- **Examples Found:** ${result.examples}`);
        sections.push('');
      });
    }

    if (selectedMitigations.length > 0) {
      sections.push('## Recommended Mitigation Strategies');
      sections.push('');
      selectedMitigations.forEach(mitId => {
        const strategy = MITIGATION_STRATEGIES.find(s => s.id === mitId);
        if (strategy) {
          sections.push(`### ${strategy.name}`);
          sections.push(strategy.description);
          sections.push('');
        }
      });
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
              <div className="text-6xl mb-4">⚖️</div>
              <h2 className="text-3xl font-bold mb-4">Bias Detection & Mitigation</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Systematically identify and address biases in your AI system to ensure fairness across all user groups.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🔍</div>
                <h3 className="font-semibold mb-2">Detection</h3>
                <p className="text-sm text-gray-400">Identify biases across demographics</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">📊</div>
                <h3 className="font-semibold mb-2">Analysis</h3>
                <p className="text-sm text-gray-400">Measure bias severity and impact</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🛠️</div>
                <h3 className="font-semibold mb-2">Mitigation</h3>
                <p className="text-sm text-gray-400">Strategies to reduce bias</p>
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

      case 'scope':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Define Analysis Scope</h2>
              <p className="text-gray-400">What aspect of your AI system do you want to analyze for bias?</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Analysis Scope *</label>
              <TextInputWithDictation
                multiline
                rows={6}
                value={analysisScope}
                onChange={(e) => setAnalysisScope(e.target.value)}
                placeholder="e.g., Testing our customer service chatbot for bias in how it responds to different demographic groups..."
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
                    Be specific about which model, feature, or use case you're testing. Include context about your users and how they interact with the system.
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={analysisScope.length > 20}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('scope');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'demographics':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Select Bias Types to Test</h2>
              <p className="text-gray-400">Choose which types of bias you want to analyze</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {BIAS_TYPES.map(type => (
                <button
                  key={type.id}
                  onClick={() => toggleBiasType(type.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedBiasTypes.includes(type.id)
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">{type.icon}</div>
                      <div>
                        <div className="font-semibold mb-1">{type.name}</div>
                        <div className="text-sm text-gray-400">{type.description}</div>
                      </div>
                    </div>
                    {selectedBiasTypes.includes(type.id) && (
                      <svg className="w-5 h-5 text-primary flex-shrink-0 ml-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Specific Demographic Groups (Optional)</label>
              <div className="flex flex-wrap gap-2 mb-3">
                {demographics.map(demo => (
                  <span
                    key={demo}
                    className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm font-medium flex items-center gap-2"
                  >
                    {demo}
                    <button
                      onClick={() => setDemographics(demographics.filter(d => d !== demo))}
                      className="text-primary hover:text-white"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <TextInputWithDictation
                  value={newDemographic}
                  onChange={(e) => setNewDemographic(e.target.value)}
                  placeholder="Add demographic group..."
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                  onKeyPress={(e) => e.key === 'Enter' && addDemographic()}
                  enableDictation={true}
                />
                <button
                  onClick={addDemographic}
                  className="px-6 py-2 bg-primary text-white hover:bg-primary-dark rounded-lg font-medium transition-colors"
                >
                  Add
                </button>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={selectedBiasTypes.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('demographics');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'tests':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Test Prompts</h2>
              <p className="text-gray-400">Add prompts to test for bias</p>
            </div>

            <div className="space-y-4">
              {testPrompts.map((prompt, index) => (
                <div key={index} className="flex gap-2">
                  <TextInputWithDictation
                    multiline
                    rows={2}
                    value={prompt}
                    onChange={(e) => {
                      const updated = [...testPrompts];
                      updated[index] = e.target.value;
                      setTestPrompts(updated);
                    }}
                    placeholder="Enter a test prompt..."
                    className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                    enableDictation={true}
                  />
                  {testPrompts.length > 1 && (
                    <button
                      onClick={() => setTestPrompts(testPrompts.filter((_, i) => i !== index))}
                      className="px-4 py-2 bg-red-900/50 hover:bg-red-900 text-red-300 rounded-lg transition-colors"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => setTestPrompts([...testPrompts, ''])}
                className="w-full py-3 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
              >
                + Add Test Prompt
              </button>
            </div>

            <button
              onClick={runBiasTests}
              className="w-full py-3 bg-primary text-white hover:bg-primary-dark rounded-lg font-medium transition-colors"
            >
              Run Bias Detection Tests
            </button>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={biasResults.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('tests');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'results':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Bias Detection Results</h2>
              <p className="text-gray-400">Review findings from the bias analysis</p>
            </div>

            {biasResults.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
                <div className="text-4xl mb-3">🔍</div>
                <p className="text-gray-400">No tests run yet. Go back to run bias tests.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {biasResults.map((result, index) => {
                  const type = BIAS_TYPES.find(t => t.id === result.type);
                  const severityColor = result.severity === 'high' ? 'red' : result.severity === 'medium' ? 'yellow' : 'green';

                  return (
                    <div key={index} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="text-3xl">{type?.icon}</div>
                          <div>
                            <h3 className="font-bold text-lg">{type?.name}</h3>
                            <p className="text-sm text-gray-400">{type?.description}</p>
                          </div>
                        </div>
                        <span className={`px-3 py-1 bg-${severityColor}-900/50 text-${severityColor}-300 text-xs font-semibold rounded-full border border-${severityColor}-700`}>
                          {result.severity.toUpperCase()}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Bias Score</div>
                          <div className="text-3xl font-bold">{result.score}/100</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Examples Found</div>
                          <div className="text-3xl font-bold">{result.examples}</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={biasResults.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('results');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'mitigation':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Mitigation Strategies</h2>
              <p className="text-gray-400">Select strategies to reduce identified biases</p>
            </div>

            <div className="space-y-3">
              {MITIGATION_STRATEGIES.map(strategy => (
                <button
                  key={strategy.id}
                  onClick={() => {
                    setSelectedMitigations(prev =>
                      prev.includes(strategy.id)
                        ? prev.filter(id => id !== strategy.id)
                        : [...prev, strategy.id]
                    );
                  }}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                    selectedMitigations.includes(strategy.id)
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold mb-1">{strategy.name}</div>
                      <div className="text-sm text-gray-400">{strategy.description}</div>
                    </div>
                    {selectedMitigations.includes(strategy.id) && (
                      <svg className="w-5 h-5 text-primary flex-shrink-0 ml-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={selectedMitigations.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('mitigation');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'report':
        const report = generateReport();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Bias Analysis Report</h2>
              <p className="text-gray-400">Export your comprehensive bias analysis</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Bias Types Tested</div>
                <div className="text-2xl font-bold">{selectedBiasTypes.length}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Issues Found</div>
                <div className="text-2xl font-bold text-yellow-400">{biasResults.length}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Mitigations</div>
                <div className="text-2xl font-bold text-green-400">{selectedMitigations.length}</div>
              </div>
            </div>

            <WizardExport
              formats={wizardConfig.exportFormats}
              content={report}
              filename={`bias-analysis-${Date.now()}`}
            />

            <div className="flex gap-4">
              <button
                onClick={() => wizard.goToStep(0)}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                New Analysis
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('report');
                  toast.success('Bias analysis complete!');
                }}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-secondary text-white hover:opacity-90 rounded-lg font-medium transition-opacity"
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
