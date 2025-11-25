import { useState } from 'react'

interface AIAnalysis {
  score: number
  issues: Array<{ severity: string; message: string }>
  predictions: Array<{ type: string; alert: string; probability: string }>
  recommendations: string[]
  confidence: number
  patterns: any[]
}

interface EnhancedAIDemoProps {
  wizardId: string
  wizardName: string
  capability: string
  icon: string
}

export function EnhancedAIDemo({ wizardId, wizardName, capability, icon }: EnhancedAIDemoProps) {
  const [input, setInput] = useState('')
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [sampleLoaded, setSampleLoaded] = useState(false)

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setAnalysis(null)
    setSampleLoaded(false)

    try {
      const response = await fetch(`http://localhost:8001/api/wizard/${wizardId}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: input,
          user_id: 'demo_user',
          context: {
            wizard_type: 'ai',
            capability: capability
          }
        })
      })

      const data = await response.json()

      if (data.success && data.analysis) {
        const issues = data.analysis.issues || []
        const score = Math.max(20, 100 - issues.length * 10)

        setAnalysis({
          score,
          issues: issues.slice(0, 5),
          predictions: data.analysis.predictions || [],
          recommendations: data.analysis.recommendations || ['Analysis complete'],
          confidence: data.analysis.confidence || 0.85,
          patterns: data.analysis.patterns || []
        })
      } else {
        // Fallback for basic response
        setAnalysis({
          score: 75,
          issues: [],
          predictions: [],
          recommendations: [data.output || 'Analysis complete'],
          confidence: 0.75,
          patterns: []
        })
      }
    } catch (error) {
      console.error(`${wizardName} API error:`, error)
      setAnalysis({
        score: 0,
        issues: [{ severity: 'error', message: 'API connection error' }],
        predictions: [],
        recommendations: ['Start backend: python backend/api/wizard_api.py'],
        confidence: 0,
        patterns: []
      })
    }

    setIsAnalyzing(false)
  }

  const loadSample = () => {
    const samples: Record<string, string> = {
      multi_model: 'Compare GPT-4 and Claude for code review tasks with emphasis on security analysis',
      rag_pattern: 'Implement a RAG system for customer support documentation with 10K+ articles',
      ai_performance: 'Optimize inference latency for a production ML model serving 1M requests/day',
      ai_collaboration: 'Design multi-agent system for automated code review and testing pipeline',
      advanced_debugging: 'Debug intermittent GPU memory errors in distributed training with PyTorch',
      agent_orchestration: 'Orchestrate 5 specialized agents for end-to-end data pipeline: ingestion, validation, transformation, analysis, reporting',
      enhanced_testing: 'Generate comprehensive test suite for authentication microservice with OAuth2 and JWT',
      ai_documentation: 'Auto-generate API documentation from FastAPI codebase with usage examples',
      ai_context: 'Optimize context window usage for 100K token documents while maintaining quality',
      security_analysis: 'Analyze AI model for prompt injection vulnerabilities and data leakage risks'
    }
    setInput(samples[wizardId] || `Sample query for ${wizardName}`)
    setAnalysis(null)
    setSampleLoaded(true)
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
          <span className="text-lg">{icon}</span> <strong>Level 4-5</strong> {capability}
        </span>
      </div>

      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">AI Task or Query</label>
          <button
            type="button"
            onClick={loadSample}
            className="text-xs text-primary-600 hover:text-primary-700 font-medium"
          >
            Load Sample
          </button>
        </div>
        <textarea
          value={input}
          onChange={(e) => {
            setInput(e.target.value)
            setSampleLoaded(false)
          }}
          className={`w-full h-40 px-3 py-2 border-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
            sampleLoaded ? 'border-primary-400 bg-primary-50' : 'border-gray-300'
          }`}
          placeholder="Describe your AI task or system..."
        />
        {sampleLoaded && (
          <div className="mt-1 text-xs text-primary-600 font-medium">
            ✓ Sample loaded - Click "Analyze System" to process
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={handleAnalyze}
        disabled={!input || isAnalyzing}
        className="w-full px-4 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {isAnalyzing ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Analyzing...
          </>
        ) : (
          `${icon} Analyze System`
        )}
      </button>

      {analysis && (
        <div className="space-y-4">
          {/* Score & Confidence */}
          <div className="bg-white border-2 border-gray-300 rounded-lg p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Analysis Score</div>
                <div className={`text-3xl font-bold ${getScoreColor(analysis.score)}`}>
                  {analysis.score}/100
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Confidence</div>
                <div className="text-3xl font-bold text-primary-600">
                  {Math.round(analysis.confidence * 100)}%
                </div>
              </div>
            </div>
          </div>

          {/* Issues */}
          {analysis.issues.length > 0 && (
            <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
              <h5 className="font-semibold text-yellow-900 mb-2">⚠️ Issues Detected</h5>
              <ul className="space-y-2">
                {analysis.issues.map((issue, i) => (
                  <li key={i} className="text-sm text-yellow-800 flex items-start gap-2">
                    <span className="text-yellow-600 mt-0.5">•</span>
                    <span>[{issue.severity.toUpperCase()}] {issue.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Predictions */}
          {analysis.predictions.length > 0 && (
            <div className="bg-purple-50 border-2 border-purple-300 rounded-lg p-4">
              <h5 className="font-semibold text-purple-900 mb-2">🔮 Predictive Insights</h5>
              <div className="space-y-3">
                {analysis.predictions.map((pred, i) => (
                  <div key={i} className="bg-white rounded p-3 border border-purple-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-purple-900">{pred.type}</span>
                      <span className="text-xs px-2 py-1 bg-purple-100 rounded text-purple-800">
                        {pred.probability} probability
                      </span>
                    </div>
                    <p className="text-sm text-purple-800">{pred.alert}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4">
            <h5 className="font-semibold text-green-900 mb-2">💡 Recommendations</h5>
            <ol className="space-y-2">
              {analysis.recommendations.slice(0, 5).map((rec, i) => (
                <li key={i} className="text-sm text-green-800 flex items-start gap-2">
                  <span className="text-green-600 font-bold">{i + 1}.</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Patterns */}
          {analysis.patterns.length > 0 && (
            <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
              <h5 className="font-semibold text-blue-900 mb-2">📊 Detected Patterns</h5>
              <div className="flex flex-wrap gap-2">
                {analysis.patterns.slice(0, 5).map((pattern, i) => (
                  <span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {pattern.pattern_type || 'Pattern ' + (i + 1)}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-3 text-xs text-purple-800">
        <strong>Level 4-5 Anticipatory:</strong> {capability} with predictive insights and cross-domain pattern recognition.
      </div>
    </div>
  )
}
