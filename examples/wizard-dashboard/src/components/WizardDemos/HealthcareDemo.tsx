import { useState } from 'react'

export function HealthcareDemo() {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)

  const handleDeidentify = async () => {
    setIsProcessing(true)

    try {
      // Call REAL Healthcare Wizard API
      const response = await fetch('http://localhost:8001/api/wizard/healthcare/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: input,
          user_id: 'demo_user',
          context: {}
        })
      })

      const data = await response.json()

      if (data.success) {
        setOutput(data.output || 'Processing complete')
      } else {
        setOutput(`Error: ${data.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Wizard API error:', error)
      setOutput('Error: Could not connect to wizard API. Make sure backend is running at http://localhost:8001')
    }

    setIsProcessing(false)
  }

  const loadSample = () => {
    setInput(`Patient John Smith (MRN: 123456789) presented on 03/15/2024 with symptoms.
DOB: 05/12/1985, SSN: 123-45-6789
Insurance: Blue Cross policy #987654321`)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="inline-flex items-center gap-1">
          🔒 <strong>HIPAA-Compliant</strong> PHI De-identification
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Input */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">Input (with PHI)</label>
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
            placeholder="Enter clinical notes with PHI..."
          />
        </div>

        {/* Output */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Output (De-identified)
          </label>
          <div className="w-full h-40 px-3 py-2 border-2 border-green-300 bg-green-50 rounded-lg text-sm overflow-auto font-mono whitespace-pre-wrap">
            {output || 'Processed output will appear here...'}
          </div>
        </div>
      </div>

      <button
        onClick={handleDeidentify}
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
          <>
            🏥 De-identify PHI
          </>
        )}
      </button>

      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3 text-xs text-blue-800">
        <strong>Demo Mode:</strong> This detects MRN, DOB, SSN, patient names, and dates.
        Production version includes 50+ PHI patterns and HIPAA audit logging.
      </div>
    </div>
  )
}
