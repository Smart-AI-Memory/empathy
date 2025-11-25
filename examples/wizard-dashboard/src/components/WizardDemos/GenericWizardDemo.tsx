import { useState } from 'react'

interface GenericWizardDemoProps {
  wizardId: string
  wizardName: string
  wizardType: 'domain' | 'coach' | 'ai'
  description: string
}

interface WizardResult {
  success: boolean
  output: string
  analysis?: any
  error?: string
}

export function GenericWizardDemo({ wizardId, wizardName, wizardType, description }: GenericWizardDemoProps) {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [analysisData, setAnalysisData] = useState<any>(null)

  const handleProcess = async () => {
    setIsProcessing(true)
    setOutput('')
    setAnalysisData(null)

    try {
      // Call the wizard API
      const response = await fetch(`http://localhost:8001/api/wizard/${wizardId}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: input,
          user_id: 'demo_user',
          context: wizardType === 'coach' ? {
            file_path: 'demo.py',
            language: 'python'
          } : {}
        })
      })

      const data: WizardResult = await response.json()

      if (data.success) {
        setOutput(data.output || 'Processing complete')
        setAnalysisData(data.analysis)
      } else {
        setOutput(`Error: ${data.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error(`${wizardName} API error:`, error)
      setOutput(`Error: Could not connect to wizard API. Make sure backend is running at http://localhost:8001`)
    }

    setIsProcessing(false)
  }

  const loadSample = () => {
    if (wizardType === 'domain') {
      setInput(`Sample input for ${wizardName}:\nThis is a demonstration of the wizard functionality.`)
    } else if (wizardType === 'coach') {
      setInput(`def example_function():
    # Sample code for ${wizardName}
    result = some_operation()
    return result`)
    } else {
      setInput(`Sample prompt for ${wizardName} analysis`)
    }
    setOutput('')
    setAnalysisData(null)
  }

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3 text-sm text-blue-800">
        <strong>{wizardName}</strong>: {description}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Input */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">
              {wizardType === 'domain' ? 'Input Text' : wizardType === 'coach' ? 'Code' : 'Prompt'}
            </label>
            <button
              onClick={loadSample}
              className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              Load Sample
            </button>
          </div>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full h-40 px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono"
            placeholder={`Enter ${wizardType === 'domain' ? 'text' : wizardType === 'coach' ? 'code' : 'prompt'} here...`}
          />
        </div>

        {/* Output */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Output</label>
          <div className="w-full h-40 px-3 py-2 border-2 border-green-300 bg-green-50 rounded-lg text-sm overflow-auto font-mono whitespace-pre-wrap">
            {output || 'Output will appear here...'}
          </div>
        </div>
      </div>

      <button
        onClick={handleProcess}
        disabled={!input || isProcessing}
        className="w-full px-4 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {isProcessing ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Processing...
          </>
        ) : (
          `🚀 Process with ${wizardName}`
        )}
      </button>

      {/* Analysis Section */}
      {analysisData && (
        <div className="bg-white border-2 border-gray-300 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-3">Analysis Results</h4>

          {/* Domain wizard analysis */}
          {wizardType === 'domain' && analysisData.pii_detected && (
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">PII Detected:</span> {analysisData.pii_detected.length} items
              </div>
              <div className="text-sm">
                <span className="font-medium">Classification:</span> {analysisData.classification || 'N/A'}
              </div>
              <div className="text-sm">
                <span className="font-medium">Confidence:</span> {Math.round((analysisData.confidence || 0) * 100)}%
              </div>
            </div>
          )}

          {/* Coach wizard analysis */}
          {wizardType === 'coach' && analysisData.issues && (
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">Issues Found:</span> {analysisData.issues_found || 0}
              </div>
              {analysisData.issues.slice(0, 3).map((issue: any, i: number) => (
                <div key={i} className="text-sm bg-yellow-50 border border-yellow-200 rounded p-2">
                  <div className="font-medium text-yellow-900">[{issue.severity}] Line {issue.line}</div>
                  <div className="text-yellow-800">{issue.message}</div>
                </div>
              ))}
            </div>
          )}

          {/* AI wizard analysis */}
          {wizardType === 'ai' && (
            <div className="space-y-2">
              {analysisData.issues && analysisData.issues.length > 0 && (
                <div className="text-sm">
                  <span className="font-medium">Issues:</span> {analysisData.issues.length}
                </div>
              )}
              {analysisData.predictions && analysisData.predictions.length > 0 && (
                <div className="text-sm">
                  <span className="font-medium">Predictions:</span> {analysisData.predictions.length}
                </div>
              )}
              {analysisData.recommendations && analysisData.recommendations.length > 0 && (
                <div className="text-sm">
                  <span className="font-medium">Recommendations:</span> {analysisData.recommendations.length}
                </div>
              )}
              {analysisData.confidence !== undefined && (
                <div className="text-sm">
                  <span className="font-medium">Confidence:</span> {Math.round((analysisData.confidence || 0) * 100)}%
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 text-xs text-gray-600">
        <strong>Backend Integration:</strong> This wizard is connected to the live Python implementation
        at <code>http://localhost:8001/api/wizard/{wizardId}</code>
      </div>
    </div>
  )
}
