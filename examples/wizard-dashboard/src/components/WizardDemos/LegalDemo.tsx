import { useState } from 'react'

interface LegalAnalysis {
  privilegeViolations: string[]
  confidentialityRisk: 'low' | 'medium' | 'high'
  recommendations: string[]
  redactedCount: number
}

export function LegalDemo() {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [analysis, setAnalysis] = useState<LegalAnalysis | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleProcess = async () => {
    setIsProcessing(true)

    try {
      // Call REAL Legal Wizard API
      const response = await fetch('http://localhost:8001/api/wizard/legal/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: input,
          user_id: 'demo_user',
          context: {}
        })
      })

      const data = await response.json()

      if (data.success && data.analysis) {
        const piiDetected = data.analysis.pii_detected || []
        const redactedCount = piiDetected.length

        const violations = piiDetected.length > 2 ?
          ['Multiple sensitive legal identifiers detected', 'Attorney-client privilege review required'] : []

        const risk: 'low' | 'medium' | 'high' =
          redactedCount >= 3 ? 'high' :
          redactedCount >= 2 ? 'medium' : 'low'

        const recommendations = [
          'Add "ATTORNEY-CLIENT PRIVILEGED" header',
          'Implement Fed. Rules 502 protections',
          'Use encrypted channels for communications',
          'Maintain privilege log for protected documents'
        ]

        setOutput(data.output || 'Processing complete')
        setAnalysis({
          privilegeViolations: violations,
          confidentialityRisk: risk,
          recommendations,
          redactedCount
        })
      } else {
        setOutput(data.error || 'Error processing')
        setAnalysis(null)
      }
    } catch (error) {
      console.error('Legal Wizard API error:', error)
      setOutput('Error: Could not connect to wizard API. Make sure backend is running at http://localhost:8001')
      setAnalysis(null)
    }

    setIsProcessing(false)
  }

  const loadSample = () => {
    setInput(`Attorney-client communication regarding Case #2024-12345
Client: John Anderson
Docket #CV-2024-001

Discussion of litigation strategy for upcoming trial.
Work product analysis of defendant's arguments.
Confidential settlement negotiations in progress.`)
    setOutput('')
    setAnalysis(null)
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'bg-red-100 text-red-800 border-red-500'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-500'
      case 'low': return 'bg-green-100 text-green-800 border-green-500'
      default: return 'bg-gray-100 text-gray-800 border-gray-500'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="inline-flex items-center gap-1">
          ⚖️ <strong>Fed. Rules 502</strong> Attorney-Client Privilege Protection
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Input */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">Legal Document</label>
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
            placeholder="Enter legal document or communication..."
          />
        </div>

        {/* Output */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Protected Output
          </label>
          <div className="w-full h-40 px-3 py-2 border-2 border-green-300 bg-green-50 rounded-lg text-sm overflow-auto font-mono whitespace-pre-wrap">
            {output || 'Protected output will appear here...'}
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
            Analyzing...
          </>
        ) : (
          '⚖️ Analyze & Protect'
        )}
      </button>

      {analysis && (
        <div className="space-y-4">
          {/* Summary */}
          <div className={`border-l-4 rounded p-4 ${getRiskColor(analysis.confidentialityRisk)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h5 className="font-semibold">Confidentiality Risk</h5>
                <p className="text-sm mt-1">
                  {analysis.redactedCount} items redacted, {analysis.privilegeViolations.length} violations found
                </p>
              </div>
              <span className="text-2xl font-bold uppercase">{analysis.confidentialityRisk}</span>
            </div>
          </div>

          {/* Violations */}
          {analysis.privilegeViolations.length > 0 && (
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
              <h5 className="font-semibold text-red-900 mb-2">⚠️ Privilege Violations Detected</h5>
              <ul className="space-y-1">
                {analysis.privilegeViolations.map((violation, i) => (
                  <li key={i} className="text-sm text-red-800 flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>
                    <span>{violation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
            <h5 className="font-semibold text-blue-900 mb-2">💡 Best Practices</h5>
            <ol className="space-y-2">
              {analysis.recommendations.map((rec, i) => (
                <li key={i} className="text-sm text-blue-800 flex items-start gap-2">
                  <span className="text-blue-600 font-bold">{i + 1}.</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}

      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3 text-xs text-blue-800">
        <strong>Demo Mode:</strong> Protects case numbers, dockets, client names, and privilege markers.
        Production version includes Rule 502(b) inadvertent disclosure protection and privilege log generation.
      </div>
    </div>
  )
}
