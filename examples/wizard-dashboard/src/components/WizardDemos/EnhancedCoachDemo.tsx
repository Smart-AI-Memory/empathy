import { useState } from 'react'

interface CodeIssue {
  severity: string
  line: number
  message: string
  suggestion: string
}

interface CoachAnalysis {
  issuesFound: number
  issues: CodeIssue[]
  severityCounts: {
    error: number
    warning: number
    info: number
  }
  score: number
}

interface EnhancedCoachDemoProps {
  wizardId: string
  wizardName: string
  focusArea: string
  icon: string
}

export function EnhancedCoachDemo({ wizardId, wizardName, focusArea, icon }: EnhancedCoachDemoProps) {
  const [code, setCode] = useState('')
  const [analysis, setAnalysis] = useState<CoachAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [sampleLoaded, setSampleLoaded] = useState(false)
  const [fileName, setFileName] = useState('')

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setAnalysis(null)
    setSampleLoaded(false)

    try {
      const response = await fetch(`http://localhost:8001/api/wizard/${wizardId}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: code,
          user_id: 'demo_user',
          context: {
            file_path: 'demo.py',
            language: 'python'
          }
        })
      })

      const data = await response.json()

      if (data.success && data.analysis) {
        const issues = data.analysis.issues || []
        const errorCount = issues.filter((i: any) => i.severity === 'error').length
        const warningCount = issues.filter((i: any) => i.severity === 'warning').length
        const infoCount = issues.filter((i: any) => i.severity === 'info').length

        const score = Math.max(0, 100 - (errorCount * 20 + warningCount * 10 + infoCount * 5))

        setAnalysis({
          issuesFound: issues.length,
          issues: issues,
          severityCounts: {
            error: errorCount,
            warning: warningCount,
            info: infoCount
          },
          score
        })
      } else {
        setAnalysis({
          issuesFound: 0,
          issues: [],
          severityCounts: { error: 0, warning: 0, info: 0 },
          score: 100
        })
      }
    } catch (error) {
      console.error(`${wizardName} API error:`, error)
      setAnalysis({
        issuesFound: 1,
        issues: [{
          severity: 'error',
          line: 0,
          message: 'API connection error',
          suggestion: 'Start backend: python backend/api/wizard_api.py'
        }],
        severityCounts: { error: 1, warning: 0, info: 0 },
        score: 0
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
      setCode(content)
      setFileName(file.name)
      setSampleLoaded(false)
      setAnalysis(null)
    }
    reader.readAsText(file)
  }

  const loadSample = () => {
    const samples: Record<string, string> = {
      documentation: `def calculate_total(items):
    # Calculate total
    total = 0
    for item in items:
        total += item.price
    return total`,
      performance_wizard: `def process_data(data):
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            result.append(data[i] + data[j])
    return result`,
      refactoring: `def processUserData(u):
    if u['status'] == 'active':
        if u['age'] > 18:
            if u['verified'] == True:
                return True
    return False`,
      database: `query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
result = cursor.fetchall()`,
      compliance: `def store_user_data(data):
    # Save to database
    db.save(data)
    print(f"Saved data for {data['email']}")`,
      monitoring: `try:
    result = process_payment(amount)
except:
    pass`,
      cicd: `# Build script
npm install
npm run build
cp -r dist/* /var/www/`,
      accessibility: `<button onclick="submitForm()">
  Click here
</button>`,
      localization: `message = "Welcome to our app!"
error = "An error occurred"
print(message)`,
      migration: `# Old API version
response = requests.get('http://api.v1/users')
data = response.json()`,
      observability: `def critical_operation():
    result = expensive_calculation()
    return result`,
      scaling: `def handle_request(request):
    data = process(request)
    cache[request.id] = data
    return data`
    }
    setCode(samples[wizardId] || `def example_function():\n    # Sample code for ${wizardName}\n    pass`)
    setAnalysis(null)
    setSampleLoaded(true)
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      error: 'bg-red-50 border-red-300 text-red-900',
      warning: 'bg-yellow-50 border-yellow-300 text-yellow-900',
      info: 'bg-blue-50 border-blue-300 text-blue-900'
    }
    return colors[severity as keyof typeof colors] || colors.info
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
          <span className="text-lg">{icon}</span> <strong>{focusArea}</strong> Code Analysis
        </span>
      </div>

      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">Code to Analyze</label>
          <div className="flex gap-2">
            <label className="text-xs text-primary-600 hover:text-primary-700 font-medium cursor-pointer">
              📁 Upload File
              <input
                type="file"
                accept=".py,.js,.ts,.tsx,.jsx,.java,.cpp,.c,.h,.go,.rs,.rb,.php,.swift,.kt,.cs,.scala,.r,.m,.sh,.sql,.html,.css,.json,.xml,.yaml,.yml,.md,.txt"
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
          value={code}
          onChange={(e) => {
            setCode(e.target.value)
            setSampleLoaded(false)
            setFileName('')
          }}
          className={`w-full h-56 px-3 py-2 border-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono transition-colors ${
            sampleLoaded ? 'border-primary-400 bg-primary-50' : 'border-gray-300'
          }`}
          placeholder="Paste your code here or upload a file..."
        />
        {fileName && (
          <div className="mt-1 text-xs text-green-600 font-medium">
            📄 {fileName} loaded
          </div>
        )}
        {sampleLoaded && !fileName && (
          <div className="mt-1 text-xs text-primary-600 font-medium">
            ✓ Sample loaded - Click "Analyze Code" to process
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={handleAnalyze}
        disabled={!code || isAnalyzing}
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
          `${icon} Analyze Code`
        )}
      </button>

      {analysis && (
        <div className="space-y-4">
          {/* Score Card */}
          <div className="bg-white border-2 border-gray-300 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">Code Quality Score</h4>
              <span className={`text-3xl font-bold ${getScoreColor(analysis.score)}`}>
                {analysis.score}/100
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="text-center p-3 bg-red-50 border border-red-200 rounded">
                <div className="text-2xl font-bold text-red-700">{analysis.severityCounts.error}</div>
                <div className="text-xs text-red-600">Errors</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 border border-yellow-200 rounded">
                <div className="text-2xl font-bold text-yellow-700">{analysis.severityCounts.warning}</div>
                <div className="text-xs text-yellow-600">Warnings</div>
              </div>
              <div className="text-center p-3 bg-blue-50 border border-blue-200 rounded">
                <div className="text-2xl font-bold text-blue-700">{analysis.severityCounts.info}</div>
                <div className="text-xs text-blue-600">Info</div>
              </div>
            </div>
          </div>

          {/* Issues List */}
          {analysis.issues.length > 0 ? (
            <div className="space-y-2">
              <h5 className="font-semibold text-gray-900">Issues Found ({analysis.issuesFound})</h5>
              {analysis.issues.slice(0, 10).map((issue, i) => (
                <div key={i} className={`border-2 rounded-lg p-3 ${getSeverityColor(issue.severity)}`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium">
                      [{issue.severity.toUpperCase()}] Line {issue.line}
                    </div>
                    <span className={`px-2 py-1 text-xs rounded ${
                      issue.severity === 'error' ? 'bg-red-200 text-red-900' :
                      issue.severity === 'warning' ? 'bg-yellow-200 text-yellow-900' :
                      'bg-blue-200 text-blue-900'
                    }`}>
                      {issue.severity}
                    </span>
                  </div>
                  <p className="text-sm mb-2">{issue.message}</p>
                  {issue.suggestion && (
                    <div className="text-sm bg-white bg-opacity-50 rounded p-2 border-l-2 border-current">
                      <strong>💡 Suggestion:</strong> {issue.suggestion}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4 text-center">
              <div className="text-3xl mb-2">✅</div>
              <p className="font-semibold text-green-900">No issues found!</p>
              <p className="text-sm text-green-700">Your code looks good for {focusArea.toLowerCase()}.</p>
            </div>
          )}
        </div>
      )}

      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 text-xs text-gray-600">
        <strong>Live Analysis:</strong> Connected to production {wizardName} for {focusArea} best practices.
      </div>
    </div>
  )
}
