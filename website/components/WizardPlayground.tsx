'use client';

import { useState, useEffect } from 'react';

interface Wizard {
  name: string;
  category: string;
  description: string;
  capabilities?: string[];
}

interface WizardPlaygroundProps {
  category?: 'healthcare' | 'software';
}

export default function WizardPlayground({ category }: WizardPlaygroundProps) {
  const [wizards, setWizards] = useState<Wizard[]>([]);
  const [selectedWizard, setSelectedWizard] = useState<Wizard | null>(null);
  const [inputData, setInputData] = useState('');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingWizards, setIsLoadingWizards] = useState(true);
  const [error, setError] = useState('');

  // Fetch wizards on component mount
  useEffect(() => {
    fetchWizards();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category]);

  const fetchWizards = async () => {
    setIsLoadingWizards(true);
    try {
      const response = await fetch('/api/wizards');
      const data = await response.json();

      let allWizards = data.wizards || [];

      // Filter by category if specified
      if (category) {
        allWizards = allWizards.filter((w: Wizard) => w.category === category);
      }

      setWizards(allWizards);
      setError('');
    } catch (err) {
      console.error('Error fetching wizards:', err);
      setError('Failed to load wizards. Backend may be unavailable.');
    } finally {
      setIsLoadingWizards(false);
    }
  };

  const executeWizard = async () => {
    if (!selectedWizard || !inputData.trim()) {
      setError('Please select a wizard and provide input data');
      return;
    }

    setIsLoading(true);
    setError('');
    setOutput('');

    try {
      const response = await fetch('/api/wizards/invoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wizard_name: selectedWizard.name,
          input_data: inputData,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to execute wizard');
      }

      setOutput(JSON.stringify(data.result, null, 2));
    } catch (err) {
      console.error('Error executing wizard:', err);
      setError(err instanceof Error ? err.message : 'Failed to execute wizard');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Wizard Selection */}
      <div className="mb-8">
        <h3 className="text-2xl font-bold mb-4">Select a Wizard</h3>

        {isLoadingWizards ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--primary)]"></div>
            <p className="mt-2 text-[var(--text-secondary)]">Loading wizards...</p>
          </div>
        ) : wizards.length === 0 ? (
          <div className="bg-[var(--border)] bg-opacity-20 rounded-lg p-8 text-center">
            <p className="text-[var(--text-secondary)]">
              No wizards available. Make sure the backend is running.
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {wizards.map((wizard) => (
              <button
                key={wizard.name}
                onClick={() => setSelectedWizard(wizard)}
                className={`p-6 rounded-lg border-2 text-left transition-all ${
                  selectedWizard?.name === wizard.name
                    ? 'border-[var(--primary)] bg-[var(--primary)] bg-opacity-5'
                    : 'border-[var(--border)] hover:border-[var(--primary)] hover:border-opacity-50'
                }`}
              >
                <h4 className="font-bold mb-2">{wizard.name}</h4>
                <p className="text-sm text-[var(--text-secondary)] mb-3">
                  {wizard.description}
                </p>
                {wizard.capabilities && wizard.capabilities.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {wizard.capabilities.slice(0, 2).map((cap) => (
                      <span
                        key={cap}
                        className="px-2 py-1 bg-[var(--border)] bg-opacity-30 rounded text-xs"
                      >
                        {cap.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Wizard Execution */}
      {selectedWizard && (
        <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-8">
          <h3 className="text-2xl font-bold mb-4">
            Execute: {selectedWizard.name}
          </h3>

          {error && (
            <div className="mb-4 p-4 bg-[var(--error)] bg-opacity-10 border-2 border-[var(--error)] rounded-lg">
              <p className="text-[var(--error)]">{error}</p>
            </div>
          )}

          <div className="mb-6">
            <label htmlFor="input" className="block text-sm font-bold mb-2">
              Input Data
            </label>
            <textarea
              id="input"
              rows={8}
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              placeholder="Enter input data for the wizard (e.g., patient data, code snippet, etc.)"
              className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none font-mono text-sm"
            />
          </div>

          <button
            onClick={executeWizard}
            disabled={isLoading || !inputData.trim()}
            className="w-full btn btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
                Executing...
              </span>
            ) : (
              'Execute Wizard'
            )}
          </button>

          {output && (
            <div className="mt-6">
              <label className="block text-sm font-bold mb-2">Output</label>
              <pre className="w-full px-4 py-3 rounded-lg border-2 border-[var(--success)] bg-[var(--success)] bg-opacity-5 overflow-x-auto font-mono text-sm whitespace-pre-wrap">
                {output}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
