import { useState } from 'react'

interface FinancialData {
  sensitiveFound: string[]
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  complianceIssues: string[]
  recommendations: string[]
}

export function FinanceDemo() {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [analysis, setAnalysis] = useState<FinancialData | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleRedact = async () => {
    setIsProcessing(true)

    try {
      // Call REAL Finance Wizard API
      const response = await fetch('http://localhost:8001/api/wizard/finance/process', {
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
        const sensitiveFound = piiDetected.map((p: any) => p.type || p)

        // Determine risk level
        let riskLevel: 'low' | 'medium' | 'high' | 'critical' = piiDetected.length === 0 ? 'low' :
                      piiDetected.length >= 3 ? 'critical' :
                      piiDetected.length >= 2 ? 'high' : 'medium'

        const complianceIssues: string[] = []
        const recommendations: string[] = [
          'Use tokenization for sensitive financial data',
          'Implement SOX 7-year retention policy',
          'Enable audit logging for all data access',
          'Encrypt at rest with AES-256-GCM'
        ]

        setOutput(data.output || 'Processing complete')
        setAnalysis({
          sensitiveFound,
          riskLevel,
          complianceIssues,
          recommendations
        })
      } else {
        setOutput(data.error || 'Error processing')
        setAnalysis(null)
      }
    } catch (error) {
      console.error('Finance Wizard API error:', error)
      setOutput('Error: Could not connect to wizard API. Make sure backend is running at http://localhost:8001')
      setAnalysis(null)
    }

    setIsProcessing(false)
  }

  const loadSample = () => {
    setInput(`Transaction Record:
Customer: John Smith
Account: 1234567890
Routing: 021000021
Card: 4532123456789012
Amount: $15,234.50
Tax ID: 12-3456789`)
    setOutput('')
    setAnalysis(null)
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-500'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-500'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-500'
      case 'low': return 'bg-green-100 text-green-800 border-green-500'
      default: return 'bg-gray-100 text-gray-800 border-gray-500'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="inline-flex items-center gap-1">
          💰 <strong>SOX & PCI-DSS</strong> Compliant Data Protection
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Input */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">Input (with Financial Data)</label>
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
            placeholder="Enter financial transaction data..."
          />
        </div>

        {/* Output */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Output (Redacted)
          </label>
          <div className="w-full h-40 px-3 py-2 border-2 border-green-300 bg-green-50 rounded-lg text-sm overflow-auto font-mono whitespace-pre-wrap">
            {output || 'Redacted output will appear here...'}
          </div>
        </div>
      </div>

      <button
        onClick={handleRedact}
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
          '🔒 Redact Financial Data'
        )}
      </button>

      {analysis && (
        <div className="space-y-4">
          {/* Risk Level */}
          <div className={`border-l-4 rounded p-4 ${getRiskColor(analysis.riskLevel)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h5 className="font-semibold">Risk Level</h5>
                <p className="text-sm mt-1">
                  {analysis.sensitiveFound.length} sensitive {analysis.sensitiveFound.length === 1 ? 'item' : 'items'} detected
                </p>
              </div>
              <span className="text-2xl font-bold uppercase">{analysis.riskLevel}</span>
            </div>
          </div>

          {/* Detected */}
          {analysis.sensitiveFound.length > 0 && (
            <div className="bg-orange-50 border-2 border-orange-300 rounded-lg p-4">
              <h5 className="font-semibold text-orange-900 mb-2">🔍 Sensitive Data Detected</h5>
              <ul className="space-y-1">
                {analysis.sensitiveFound.map((item, i) => (
                  <li key={i} className="text-sm text-orange-800 flex items-center gap-2">
                    <span className="text-orange-600">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Compliance Issues */}
          {analysis.complianceIssues.length > 0 && (
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
              <h5 className="font-semibold text-red-900 mb-2">⚠️ Compliance Issues</h5>
              <ul className="space-y-1">
                {analysis.complianceIssues.map((issue, i) => (
                  <li key={i} className="text-sm text-red-800 flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">⚠</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {analysis.recommendations.length > 0 && (
            <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
              <h5 className="font-semibold text-blue-900 mb-2">💡 Security Recommendations</h5>
              <ol className="space-y-2">
                {analysis.recommendations.map((rec, i) => (
                  <li key={i} className="text-sm text-blue-800 flex items-start gap-2">
                    <span className="text-blue-600 font-bold">{i + 1}.</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3 text-xs text-blue-800">
        <strong>Demo Mode:</strong> Detects cards, accounts, routing numbers, and tax IDs.
        Production version includes 40+ financial PII patterns and maintains 7-year audit trails (SOX).
      </div>
    </div>
  )
}
