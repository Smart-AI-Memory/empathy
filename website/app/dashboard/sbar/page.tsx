'use client';

/**
 * SBAR Report Wizard - Restored from AI Nurse Florence
 * Full guided workflow with specific form fields per step
 */

import { useState } from 'react';
import Link from 'next/link';

interface WizardState {
  currentStep: number;
  completedSteps: number[];
  data: {
    // Step 1: Situation
    patientMrn: string;
    bloodPressure: string;
    heartRate: string;
    temperature: string;
    chiefComplaint: string;
    // Step 2: Background
    medicalHistory: string;
    medications: string;
    allergies: string;
    recentEvents: string;
    // Step 3: Assessment
    assessment: string;
    severity: 'routine' | 'concerning' | 'urgent';
    // Step 4: Recommendation
    recommendations: string;
    timeFrame: 'immediate' | 'within_hour' | 'within_shift' | 'routine';
  };
}

export default function SBARWizardPage() {
  const [state, setState] = useState<WizardState>({
    currentStep: 1,
    completedSteps: [],
    data: {
      patientMrn: '',
      bloodPressure: '',
      heartRate: '',
      temperature: '',
      chiefComplaint: '',
      medicalHistory: '',
      medications: '',
      allergies: '',
      recentEvents: '',
      assessment: '',
      severity: 'routine',
      recommendations: '',
      timeFrame: 'routine',
    },
  });

  const [finalReport, setFinalReport] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const updateField = (field: keyof WizardState['data'], value: string) => {
    setState(prev => ({
      ...prev,
      data: { ...prev.data, [field]: value },
    }));
  };

  const nextStep = async () => {
    if (state.currentStep < 5) {
      const newCompleted = [...state.completedSteps];
      if (!newCompleted.includes(state.currentStep)) {
        newCompleted.push(state.currentStep);
      }
      const nextStepNum = state.currentStep + 1;
      setState(prev => ({
        ...prev,
        currentStep: nextStepNum,
        completedSteps: newCompleted,
      }));

      // Auto-generate report when reaching Step 5
      if (nextStepNum === 5) {
        // Small delay to allow state to update
        setTimeout(() => {
          generateReport();
        }, 100);
      }
    }
  };

  const prevStep = () => {
    if (state.currentStep > 1) {
      setState(prev => ({ ...prev, currentStep: prev.currentStep - 1 }));
    }
  };

  const goToStep = (step: number) => {
    if (step <= state.currentStep || state.completedSteps.includes(step - 1)) {
      setState(prev => ({ ...prev, currentStep: step }));
    }
  };

  // Quick-fill templates
  const fillChestPain = () => {
    setState(prev => ({
      ...prev,
      data: {
        ...prev.data,
        chiefComplaint: "Patient reports chest pain, 7/10 severity, radiating to left arm. Diaphoretic, appears anxious.",
        bloodPressure: "140/90",
        heartRate: "98",
      },
    }));
  };

  const fillFall = () => {
    setState(prev => ({
      ...prev,
      data: {
        ...prev.data,
        chiefComplaint: "Patient found on floor next to bed. States slipped when attempting to go to bathroom unassisted.",
      },
    }));
  };

  const fillShortness = () => {
    setState(prev => ({
      ...prev,
      data: {
        ...prev.data,
        chiefComplaint: "Patient experiencing increased shortness of breath, O2 sat 88% on room air, using accessory muscles.",
        heartRate: "110",
      },
    }));
  };

  const generateReport = async () => {
    setIsGenerating(true);

    // Build the report
    const { data } = state;
    const now = new Date();

    let report = "=" + "=".repeat(59) + "\n";
    report += "SBAR CLINICAL COMMUNICATION REPORT\n";
    report += "=" + "=".repeat(59) + "\n\n";

    // Situation
    report += "SITUATION\n";
    report += "-" + "-".repeat(59) + "\n";
    if (data.chiefComplaint || data.bloodPressure || data.heartRate || data.temperature) {
      let situationText = '';
      if (data.patientMrn) situationText += `Patient MRN: ${data.patientMrn}. `;
      if (data.chiefComplaint) situationText += data.chiefComplaint + '. ';
      if (data.bloodPressure || data.heartRate || data.temperature) {
        situationText += 'Current vital signs: ';
        const vitals = [];
        if (data.bloodPressure) vitals.push(`BP ${data.bloodPressure}`);
        if (data.heartRate) vitals.push(`HR ${data.heartRate}`);
        if (data.temperature) vitals.push(`Temp ${data.temperature}°F`);
        situationText += vitals.join(', ') + '.';
      }
      report += situationText.trim() + "\n\n";
    } else {
      report += "No situation data provided.\n\n";
    }

    // Background
    report += "BACKGROUND\n";
    report += "-" + "-".repeat(59) + "\n";
    if (data.medicalHistory || data.medications || data.allergies || data.recentEvents) {
      let backgroundText = '';
      if (data.medicalHistory) backgroundText += 'Medical history: ' + data.medicalHistory + '. ';
      if (data.medications) backgroundText += 'Current medications: ' + data.medications + '. ';
      if (data.allergies) backgroundText += 'Allergies: ' + data.allergies + '. ';
      if (data.recentEvents) backgroundText += 'Recent events: ' + data.recentEvents + '.';
      report += backgroundText.trim() + "\n\n";
    } else {
      report += "No background data provided.\n\n";
    }

    // Assessment
    report += "ASSESSMENT\n";
    report += "-" + "-".repeat(59) + "\n";
    if (data.assessment) {
      report += 'Clinical assessment: ' + data.assessment + '. ';
      report += 'Severity: ' + data.severity.charAt(0).toUpperCase() + data.severity.slice(1) + '.\n\n';
    } else {
      report += "No assessment data provided.\n\n";
    }

    // Recommendation
    report += "RECOMMENDATION\n";
    report += "-" + "-".repeat(59) + "\n";
    if (data.recommendations) {
      const timeFrameText = data.timeFrame === 'immediate' ? 'Immediate attention needed' :
                            data.timeFrame === 'within_hour' ? 'Within 1 hour' :
                            data.timeFrame === 'within_shift' ? 'Within this shift' : 'Routine follow-up';
      report += 'Recommended interventions: ' + data.recommendations + '. ';
      report += 'Timeline: ' + timeFrameText + '.\n\n';
    } else {
      report += "No recommendations provided.\n\n";
    }

    report += "=" + "=".repeat(59) + "\n";
    report += "Educational use only — not medical advice. No PHI stored.\n";
    report += `Generated: ${now.toLocaleString()}\n`;
    report += "=" + "=".repeat(59);

    // Simulate generation delay
    await new Promise(resolve => setTimeout(resolve, 500));
    setFinalReport(report);
    setIsGenerating(false);
  };

  const copyReport = () => {
    if (finalReport) {
      navigator.clipboard.writeText(finalReport);
    }
  };

  const printReport = () => {
    window.print();
  };

  const resetWizard = () => {
    setState({
      currentStep: 1,
      completedSteps: [],
      data: {
        patientMrn: '',
        bloodPressure: '',
        heartRate: '',
        temperature: '',
        chiefComplaint: '',
        medicalHistory: '',
        medications: '',
        allergies: '',
        recentEvents: '',
        assessment: '',
        severity: 'routine',
        recommendations: '',
        timeFrame: 'routine',
      },
    });
    setFinalReport(null);
  };

  const progressPercent = Math.floor((state.currentStep / 5) * 100);

  // Step labels for indicators
  const stepLabels = ['Situation', 'Background', 'Assessment', 'Recommendation', 'Review'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-indigo-800 text-white shadow-lg">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <Link href="/dashboard" className="flex items-center gap-3 hover:opacity-80">
                <span className="text-2xl">🏥</span>
                <div>
                  <h1 className="text-xl font-bold">AI Nurse Florence</h1>
                  <p className="text-indigo-200 text-sm">SBAR Report Wizard</p>
                </div>
              </Link>
            </div>
            <Link href="/dashboard" className="text-indigo-200 hover:text-white text-sm">
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Info Banner */}
      <div className="bg-indigo-50 border-l-4 border-indigo-400 p-4">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <span className="text-indigo-500">ℹ️</span>
          <div>
            <h3 className="text-sm font-medium text-indigo-800">SBAR Report Wizard</h3>
            <p className="text-sm text-indigo-700">Document patient status using SBAR communication framework</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-xl">
          {/* Progress Bar */}
          <div className="bg-gray-200 h-2 rounded-t-lg overflow-hidden">
            <div
              className="bg-indigo-600 h-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Wizard Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">SBAR Report Wizard</h2>
                <p className="text-gray-600 mt-1">Document patient status using SBAR communication framework</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Step {state.currentStep} of 5</div>
                <div className="text-lg font-semibold text-indigo-600">{progressPercent}%</div>
              </div>
            </div>

            {/* Step Indicators */}
            <div className="flex items-center mt-6">
              {stepLabels.map((label, index) => {
                const stepNum = index + 1;
                const isActive = stepNum === state.currentStep;
                const isCompleted = state.completedSteps.includes(stepNum);

                return (
                  <div key={stepNum} className="flex items-center flex-1 last:flex-none">
                    <button
                      type="button"
                      onClick={() => goToStep(stepNum)}
                      className={`rounded-full w-10 h-10 flex items-center justify-center font-semibold transition-all flex-shrink-0 ${
                        isActive
                          ? 'bg-indigo-600 text-white'
                          : isCompleted
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {isCompleted ? '✓' : stepNum}
                    </button>
                    {index < stepLabels.length - 1 && (
                      <div className={`flex-1 h-1 mx-2 ${
                        state.completedSteps.includes(stepNum) ? 'bg-green-500' : 'bg-gray-300'
                      }`} />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Step Labels */}
            <div className="flex items-center mt-2 text-xs text-gray-700">
              {stepLabels.map((label, index) => (
                <div key={label} className={`text-center flex-1 last:flex-none ${index === stepLabels.length - 1 ? 'w-10' : ''}`}>
                  <span className="inline-block w-10">{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <div className="p-6">
            {/* Step 1: Situation */}
            {state.currentStep === 1 && (
              <div className="space-y-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-indigo-600">🩺</span>
                    Current Situation
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">Describe the patient's current condition and what brought them to your attention</p>

                  {/* Patient ID */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Patient MRN (optional)</label>
                    <input
                      type="text"
                      value={state.data.patientMrn}
                      onChange={(e) => updateField('patientMrn', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="12345678"
                    />
                  </div>

                  {/* Vital Signs */}
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">BP</label>
                      <input
                        type="text"
                        value={state.data.bloodPressure}
                        onChange={(e) => updateField('bloodPressure', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
                        placeholder="120/80"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">HR</label>
                      <input
                        type="text"
                        value={state.data.heartRate}
                        onChange={(e) => updateField('heartRate', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
                        placeholder="75"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Temp (°F)</label>
                      <input
                        type="text"
                        value={state.data.temperature}
                        onChange={(e) => updateField('temperature', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
                        placeholder="98.6"
                      />
                    </div>
                  </div>

                  {/* Chief Complaint */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Chief Complaint / Situation</label>
                    <textarea
                      rows={4}
                      value={state.data.chiefComplaint}
                      onChange={(e) => updateField('chiefComplaint', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="What is the patient's current condition? What brought them to your attention?"
                    />
                  </div>

                  {/* Quick-fill templates */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Quick-Fill Common Scenarios</label>
                    <div className="flex gap-2 flex-wrap">
                      <button
                        type="button"
                        onClick={fillChestPain}
                        className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded text-sm hover:bg-indigo-200"
                      >
                        ❤️ Chest Pain
                      </button>
                      <button
                        type="button"
                        onClick={fillFall}
                        className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded text-sm hover:bg-indigo-200"
                      >
                        ⚠️ Fall
                      </button>
                      <button
                        type="button"
                        onClick={fillShortness}
                        className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded text-sm hover:bg-indigo-200"
                      >
                        🫁 Shortness of Breath
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Background */}
            {state.currentStep === 2 && (
              <div className="space-y-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-indigo-600">📋</span>
                    Patient Background
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">Relevant medical history, current medications, and allergies</p>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Relevant Medical History</label>
                    <textarea
                      rows={3}
                      value={state.data.medicalHistory}
                      onChange={(e) => updateField('medicalHistory', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="e.g., CHF, COPD, diabetes..."
                    />
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Current Medications</label>
                    <textarea
                      rows={3}
                      value={state.data.medications}
                      onChange={(e) => updateField('medications', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="List current medications..."
                    />
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Allergies</label>
                    <input
                      type="text"
                      value={state.data.allergies}
                      onChange={(e) => updateField('allergies', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="e.g., Penicillin, Codeine"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Recent Events / Procedures</label>
                    <textarea
                      rows={2}
                      value={state.data.recentEvents}
                      onChange={(e) => updateField('recentEvents', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="What has happened recently that is relevant?"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Assessment */}
            {state.currentStep === 3 && (
              <div className="space-y-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-indigo-600">🔍</span>
                    Clinical Assessment
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">Your professional nursing judgment about the situation</p>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Assessment / Clinical Judgment</label>
                    <textarea
                      rows={5}
                      value={state.data.assessment}
                      onChange={(e) => updateField('assessment', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="What do you think is going on? What are your concerns?"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Severity Level</label>
                    <div className="flex gap-3">
                      {(['routine', 'concerning', 'urgent'] as const).map((level) => (
                        <label
                          key={level}
                          className={`flex items-center px-4 py-2 border-2 rounded-lg cursor-pointer transition-all ${
                            state.data.severity === level
                              ? level === 'routine'
                                ? 'border-green-500 bg-green-50'
                                : level === 'concerning'
                                ? 'border-yellow-500 bg-yellow-50'
                                : 'border-red-500 bg-red-50'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          <input
                            type="radio"
                            name="severity"
                            value={level}
                            checked={state.data.severity === level}
                            onChange={(e) => updateField('severity', e.target.value)}
                            className="mr-2"
                          />
                          <span className="text-sm capitalize">{level}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Recommendation */}
            {state.currentStep === 4 && (
              <div className="space-y-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-indigo-600">💡</span>
                    Recommendations & Actions
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">What do you recommend? What should be done?</p>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Recommendations</label>
                    <textarea
                      rows={5}
                      value={state.data.recommendations}
                      onChange={(e) => updateField('recommendations', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="What interventions or actions do you recommend?"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Time Frame</label>
                    <select
                      value={state.data.timeFrame}
                      onChange={(e) => updateField('timeFrame', e.target.value)}
                      title="Time Frame"
                      aria-label="Time Frame"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="immediate">Immediate attention needed</option>
                      <option value="within_hour">Within 1 hour</option>
                      <option value="within_shift">Within this shift</option>
                      <option value="routine">Routine follow-up</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Step 5: Generating indicator while report is being generated */}
            {state.currentStep === 5 && !finalReport && (
              <div className="space-y-6">
                <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm text-center">
                  <div className="text-4xl mb-4">⏳</div>
                  <h3 className="font-bold text-gray-900 text-lg mb-2">Generating Your SBAR Report...</h3>
                  <p className="text-gray-600">Please wait while we compile your clinical communication document.</p>
                </div>
              </div>
            )}

            {/* Final Report */}
            {finalReport && (
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-2xl text-green-600">✅</span>
                    <h3 className="font-bold text-green-900 text-lg">SBAR Report Generated!</h3>
                  </div>

                  <div className="bg-white p-4 rounded border border-green-200 mb-4">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">{finalReport}</pre>
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={copyReport}
                      className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                    >
                      📋 Copy to Clipboard
                    </button>
                    <button
                      type="button"
                      onClick={printReport}
                      className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                    >
                      🖨️ Print Report
                    </button>
                    <button
                      type="button"
                      onClick={resetWizard}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                    >
                      ➕ New Report
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Navigation Buttons - hide on Step 5 since report auto-generates */}
          {!finalReport && state.currentStep < 5 && (
            <div className="border-t border-gray-200 p-6 flex justify-between">
              <button
                type="button"
                onClick={prevStep}
                disabled={state.currentStep === 1}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ← Back
              </button>

              <button
                type="button"
                onClick={nextStep}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                {state.currentStep === 4 ? 'Generate Report →' : 'Next →'}
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
