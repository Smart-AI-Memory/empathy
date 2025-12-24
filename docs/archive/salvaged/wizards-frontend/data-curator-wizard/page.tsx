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
  id: 'data-curator',
  title: 'Training Data Curator Wizard',
  description: 'Organize and structure training datasets efficiently',
  icon: '📦',
  category: 'training',
  estimatedTime: '20-30 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Getting started', isComplete: false },
    { id: 'format', title: 'Data Format', description: 'Choose format', isComplete: false },
    { id: 'upload', title: 'Upload Data', description: 'Add your data', isComplete: false },
    { id: 'quality', title: 'Quality Check', description: 'Validate quality', isComplete: false },
    { id: 'deduplication', title: 'Deduplication', description: 'Remove duplicates', isComplete: false },
    { id: 'labeling', title: 'Labeling', description: 'Add labels/categories', isComplete: false },
    { id: 'export', title: 'Export', description: 'Download dataset', isComplete: false },
  ],
  exportFormats: [
    { id: 'jsonl', label: 'JSONL (OpenAI)', extension: 'jsonl', mimeType: 'application/jsonl' },
    { id: 'json', label: 'JSON Array', extension: 'json', mimeType: 'application/json' },
    { id: 'csv', label: 'CSV', extension: 'csv', mimeType: 'text/csv' },
    { id: 'parquet', label: 'Parquet', extension: 'parquet', mimeType: 'application/octet-stream' },
  ],
};

const DATA_FORMATS = [
  { id: 'conversation', name: 'Conversational', description: 'Chat messages with user/assistant turns', icon: '💬' },
  { id: 'qa', name: 'Question-Answer', description: 'Input-output pairs for supervised learning', icon: '❓' },
  { id: 'completion', name: 'Text Completion', description: 'Prompt and completion pairs', icon: '✍️' },
  { id: 'classification', name: 'Classification', description: 'Text with categorical labels', icon: '🏷️' },
  { id: 'custom', name: 'Custom Format', description: 'Define your own structure', icon: '⚙️' },
];

const QUALITY_CHECKS = [
  { id: 'length', name: 'Length Validation', description: 'Min/max character counts' },
  { id: 'language', name: 'Language Detection', description: 'Ensure consistent language' },
  { id: 'profanity', name: 'Profanity Filter', description: 'Flag inappropriate content' },
  { id: 'completeness', name: 'Completeness Check', description: 'No missing fields' },
  { id: 'diversity', name: 'Diversity Analysis', description: 'Measure topic variety' },
];

export default function DataCuratorWizard() {
  const wizard = useWizard(wizardConfig);

  const [selectedFormat, setSelectedFormat] = useState('');
  const [dataEntries, setDataEntries] = useState<any[]>([]);
  const [selectedQualityChecks, setSelectedQualityChecks] = useState<string[]>([]);
  const [qualityScore, setQualityScore] = useState(0);
  const [duplicatesFound, setDuplicatesFound] = useState(0);
  const [labels, setLabels] = useState<string[]>(['general']);
  const [newLabel, setNewLabel] = useState('');

  const addDataEntry = () => {
    if (selectedFormat === 'conversation') {
      setDataEntries([...dataEntries, { messages: [{ role: 'user', content: '' }, { role: 'assistant', content: '' }] }]);
    } else if (selectedFormat === 'qa') {
      setDataEntries([...dataEntries, { input: '', output: '' }]);
    } else if (selectedFormat === 'completion') {
      setDataEntries([...dataEntries, { prompt: '', completion: '' }]);
    } else if (selectedFormat === 'classification') {
      setDataEntries([...dataEntries, { text: '', label: '' }]);
    }
  };

  const updateDataEntry = (index: number, field: string, value: any) => {
    const updated = [...dataEntries];
    updated[index] = { ...updated[index], [field]: value };
    setDataEntries(updated);
  };

  const removeDataEntry = (index: number) => {
    setDataEntries(dataEntries.filter((_, i) => i !== index));
  };

  const runQualityCheck = () => {
    let score = 100;
    let issues = 0;

    dataEntries.forEach(entry => {
      if (selectedFormat === 'qa') {
        if (!entry.input || !entry.output) issues++;
        if (entry.input?.length < 10 || entry.output?.length < 10) issues++;
      }
    });

    score = Math.max(0, 100 - (issues * 5));
    setQualityScore(score);
  };

  const findDuplicates = () => {
    const seen = new Set();
    let dupes = 0;

    dataEntries.forEach(entry => {
      const key = JSON.stringify(entry);
      if (seen.has(key)) dupes++;
      seen.add(key);
    });

    setDuplicatesFound(dupes);
  };

  const generateExport = () => {
    return JSON.stringify(dataEntries, null, 2);
  };

  const renderStep = () => {
    const currentStep = wizardConfig.steps[wizard.currentStep];

    switch (currentStep.id) {
      case 'welcome':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="text-6xl mb-4">📦</div>
              <h2 className="text-3xl font-bold mb-4">Training Data Curator</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Organize, clean, and structure your training data for AI models. Ensure quality and consistency across your dataset.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">✅</div>
                <h3 className="font-semibold mb-2">Quality Validation</h3>
                <p className="text-sm text-gray-400">Automated checks for completeness and quality</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🔍</div>
                <h3 className="font-semibold mb-2">Deduplication</h3>
                <p className="text-sm text-gray-400">Identify and remove duplicate entries</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">📤</div>
                <h3 className="font-semibold mb-2">Multiple Formats</h3>
                <p className="text-sm text-gray-400">Export to JSONL, CSV, Parquet, and more</p>
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

      case 'format':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Choose Your Data Format</h2>
              <p className="text-gray-400">Select the format that matches your training data</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {DATA_FORMATS.map(format => (
                <button
                  key={format.id}
                  onClick={() => setSelectedFormat(format.id)}
                  className={`p-6 rounded-lg border-2 text-left transition-all ${
                    selectedFormat === format.id
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <div className="text-4xl mb-3">{format.icon}</div>
                  <div className="font-semibold text-lg mb-2">{format.name}</div>
                  <div className="text-sm text-gray-400">{format.description}</div>
                </button>
              ))}
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!selectedFormat}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('format');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'upload':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Add Your Training Data</h2>
              <p className="text-gray-400">Enter or paste your training examples</p>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <div className="text-sm text-gray-400">{dataEntries.length} entries</div>
                <button
                  onClick={addDataEntry}
                  className="px-4 py-2 bg-primary hover:bg-primary-dark rounded-lg text-sm font-medium transition-colors"
                >
                  + Add Entry
                </button>
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {dataEntries.map((entry, index) => (
                  <div key={index} className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium">Entry {index + 1}</span>
                      <button
                        onClick={() => removeDataEntry(index)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Remove
                      </button>
                    </div>

                    {selectedFormat === 'qa' && (
                      <div className="space-y-3">
                        <div>
                          <label className="block text-xs text-gray-400 mb-1">Input</label>
                          <TextInputWithDictation
                            multiline
                            rows={2}
                            value={entry.input || ''}
                            onChange={(e) => updateDataEntry(index, 'input', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                            enableDictation={true}
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-400 mb-1">Output</label>
                          <TextInputWithDictation
                            multiline
                            rows={2}
                            value={entry.output || ''}
                            onChange={(e) => updateDataEntry(index, 'output', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                            enableDictation={true}
                          />
                        </div>
                      </div>
                    )}

                    {selectedFormat === 'classification' && (
                      <div className="space-y-3">
                        <div>
                          <label className="block text-xs text-gray-400 mb-1">Text</label>
                          <TextInputWithDictation
                            multiline
                            rows={3}
                            value={entry.text || ''}
                            onChange={(e) => updateDataEntry(index, 'text', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-primary resize-none text-sm"
                            enableDictation={true}
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-400 mb-1">Label</label>
                          <select
                            value={entry.label || ''}
                            onChange={(e) => updateDataEntry(index, 'label', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-primary text-sm"
                          >
                            <option value="">Select label...</option>
                            {labels.map(label => (
                              <option key={label} value={label}>{label}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={dataEntries.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('upload');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'quality':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Quality Validation</h2>
              <p className="text-gray-400">Run automated quality checks on your dataset</p>
            </div>

            <div className="space-y-3">
              {QUALITY_CHECKS.map(check => (
                <button
                  key={check.id}
                  onClick={() => {
                    if (selectedQualityChecks.includes(check.id)) {
                      setSelectedQualityChecks(selectedQualityChecks.filter(id => id !== check.id));
                    } else {
                      setSelectedQualityChecks([...selectedQualityChecks, check.id]);
                    }
                  }}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                    selectedQualityChecks.includes(check.id)
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold mb-1">{check.name}</div>
                      <div className="text-sm text-gray-400">{check.description}</div>
                    </div>
                    {selectedQualityChecks.includes(check.id) && (
                      <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>

            <button
              onClick={() => {
                runQualityCheck();
                toast.success('Quality check complete!');
              }}
              className="w-full py-3 bg-primary text-white hover:bg-primary-dark rounded-lg font-medium transition-colors"
            >
              Run Quality Checks
            </button>

            {qualityScore > 0 && (
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-center">
                  <div className="text-sm text-gray-400 mb-2">Quality Score</div>
                  <div className={`text-5xl font-bold ${qualityScore >= 80 ? 'text-green-400' : qualityScore >= 60 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {qualityScore}%
                  </div>
                  <div className="text-sm text-gray-400 mt-2">
                    {qualityScore >= 80 ? 'Excellent quality!' : qualityScore >= 60 ? 'Good quality, some improvements possible' : 'Needs improvement'}
                  </div>
                </div>
              </div>
            )}

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={qualityScore > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('quality');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'deduplication':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Deduplication</h2>
              <p className="text-gray-400">Identify and remove duplicate entries</p>
            </div>

            <button
              onClick={() => {
                findDuplicates();
                toast.success('Deduplication check complete!');
              }}
              className="w-full py-3 bg-primary text-white hover:bg-primary-dark rounded-lg font-medium transition-colors"
            >
              Find Duplicates
            </button>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-2">Duplicates Found</div>
                <div className={`text-5xl font-bold ${duplicatesFound === 0 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {duplicatesFound}
                </div>
                <div className="text-sm text-gray-400 mt-2">
                  {duplicatesFound === 0 ? 'No duplicates detected!' : `${duplicatesFound} duplicate(s) found`}
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
                wizard.completeStep('deduplication');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'labeling':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Labeling & Categories</h2>
              <p className="text-gray-400">Organize your data with labels</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Available Labels</label>
              <div className="flex flex-wrap gap-2 mb-4">
                {labels.map(label => (
                  <span
                    key={label}
                    className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm font-medium"
                  >
                    {label}
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <TextInputWithDictation
                  value={newLabel}
                  onChange={(e) => setNewLabel(e.target.value)}
                  placeholder="New label name..."
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && newLabel) {
                      setLabels([...labels, newLabel]);
                      setNewLabel('');
                    }
                  }}
                  enableDictation={true}
                />
                <button
                  onClick={() => {
                    if (newLabel) {
                      setLabels([...labels, newLabel]);
                      setNewLabel('');
                    }
                  }}
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
              isCurrentStepComplete={true}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('labeling');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'export':
        const exportContent = generateExport();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Export Your Dataset</h2>
              <p className="text-gray-400">Download your curated training data</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Total Entries</div>
                <div className="text-2xl font-bold">{dataEntries.length}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Quality Score</div>
                <div className="text-2xl font-bold text-green-400">{qualityScore}%</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Labels</div>
                <div className="text-2xl font-bold">{labels.length}</div>
              </div>
            </div>

            <WizardExport
              formats={wizardConfig.exportFormats}
              content={exportContent}
              filename={`training-data-${Date.now()}`}
            />

            <div className="flex gap-4">
              <button
                onClick={() => wizard.goToStep(0)}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                Create Another Dataset
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('export');
                  toast.success('Dataset curation complete!');
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
