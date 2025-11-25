import { useState } from 'react'

interface APIAnalysis {
  score: number
  restCompliance: number
  versioning: boolean
  errorHandling: boolean
  authentication: boolean
  issues: string[]
  recommendations: string[]
}

export function APIDemo() {
  const [apiSpec, setApiSpec] = useState('')
  const [analysis, setAnalysis] = useState<APIAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [fileName, setFileName] = useState('')

  const handleAnalyze = async () => {
    setIsAnalyzing(true)

    try {
      // Call REAL API Wizard API
      const response = await fetch('http://localhost:8001/api/wizard/api_wizard/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: apiSpec,
          user_id: 'demo_user',
          context: {
            file_path: 'api_spec.txt',
            language: 'text'
          }
        })
      })

      const data = await response.json()

      const issues = data.analysis?.issues || []
      const issueMessages = issues.map((i: any) => i.message || 'API design issue')
      const recommendations = issues.map((i: any) => i.suggestion || 'Review API design')

      // Calculate metrics
      const hasProperVerbs = /\b(GET|POST|PUT|DELETE|PATCH)\b/.test(apiSpec)
      const versioning = /\/v\d+\//.test(apiSpec)
      const errorHandling = /error|40\d|50\d/.test(apiSpec.toLowerCase())
      const authentication = /auth|token|bearer/i.test(apiSpec)

      const score = Math.round(
        ((hasProperVerbs ? 50 : 0) +
        (versioning ? 20 : 0) +
        (errorHandling ? 15 : 0) +
        (authentication ? 15 : 0)) / 1.5
      )

      setAnalysis({
        score,
        restCompliance: hasProperVerbs ? 80 : 40,
        versioning,
        errorHandling,
        authentication,
        issues: issueMessages.length > 0 ? issueMessages : ['Review REST principles'],
        recommendations: recommendations.length > 0 ? recommendations : ['Follow API best practices']
      })
    } catch (error) {
      console.error('API Wizard error:', error)
      setAnalysis({
        score: 0,
        restCompliance: 0,
        versioning: false,
        errorHandling: false,
        authentication: false,
        issues: ['API connection error'],
        recommendations: ['Start backend: python backend/api/wizard_api.py']
      })
    }

    setIsAnalyzing(false)
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      setApiSpec(content)
      setFileName(file.name)
      setAnalysis(null)
    }
    reader.readAsText(file)
  }

  const loadSample = () => {
    setApiSpec(`# User API Endpoints

GET /users
POST /users
GET /user/{id}
DELETE /user/{id}

# Authentication
Header: Authorization: Bearer token

# Response: 200 OK
{
  "id": 123,
  "name": "John Doe"
}`)
    setAnalysis(null)
    setFileName('')
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="inline-flex items-center gap-1">
          🔌 <strong>REST/GraphQL</strong> API Design Best Practices
        </span>
      </div>

      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">API Specification</label>
          <div className="flex gap-2">
            <label className="text-xs text-primary-600 hover:text-primary-700 font-medium cursor-pointer">
              📁 Upload File
              <input
                type="file"
                accept=".json,.yaml,.yml,.txt,.md,.openapi,.swagger"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
            <button
              type="button"
              onClick={loadSample}
              className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              Load Sample
            </button>
          </div>
        </div>
        <textarea
          value={apiSpec}
          onChange={(e) => {
            setApiSpec(e.target.value)
            setFileName('')
          }}
          className="w-full h-48 px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono"
          placeholder="Paste your API specification or upload a file..."
        />
        {fileName && (
          <div className="mt-1 text-xs text-green-600 font-medium">
            📄 {fileName} loaded
          </div>
        )}
      </div>

      <button
        onClick={handleAnalyze}
        disabled={!apiSpec || isAnalyzing}
        className="w-full px-4 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {isAnalyzing ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Analyzing design...
          </>
        ) : (
          '🔍 Analyze API Design'
        )}
      </button>

      {analysis && (
        <div className="space-y-4">
          {/* Score */}
          <div className="bg-white border-2 border-gray-300 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">API Design Score</h4>
              <span className={`text-3xl font-bold ${getScoreColor(analysis.score)}`}>
                {analysis.score}/100
              </span>
            </div>

            <div className="space-y-3">
              {[
                { label: 'REST Compliance', value: analysis.restCompliance, checked: analysis.restCompliance >= 80 },
                { label: 'Versioning Strategy', value: analysis.versioning ? 100 : 0, checked: analysis.versioning },
                { label: 'Error Handling', value: analysis.errorHandling ? 100 : 0, checked: analysis.errorHandling },
                { label: 'Authentication', value: analysis.authentication ? 100 : 0, checked: analysis.authentication }
              ].map((metric) => (
                <div key={metric.label} className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                    metric.checked ? 'bg-green-500' : 'bg-red-500'
                  }`}>
                    <span className="text-white text-sm">{metric.checked ? '✓' : '✗'}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">{metric.label}</span>
                      <span className="font-medium">{metric.checked ? '✓ Pass' : '✗ Fail'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Issues */}
          {analysis.issues.length > 0 && (
            <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
              <h5 className="font-semibold text-yellow-900 mb-2">⚠️ Issues Found</h5>
              <ul className="space-y-1">
                {analysis.issues.map((issue, i) => (
                  <li key={i} className="text-sm text-yellow-800 flex items-start gap-2">
                    <span className="text-yellow-600 mt-0.5">•</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
            <h5 className="font-semibold text-blue-900 mb-2">💡 Recommendations</h5>
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

      <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-3 text-xs text-purple-800">
        <strong>Level 3:</strong> Validates REST principles, versioning strategies, and security patterns.
        Production version includes OpenAPI/Swagger validation and GraphQL schema analysis.
      </div>
    </div>
  )
}
