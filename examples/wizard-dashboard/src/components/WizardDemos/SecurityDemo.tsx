import { useState } from 'react'

interface Vulnerability {
  id: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  title: string
  description: string
  line?: number
}

export function SecurityDemo() {
  const [code, setCode] = useState('')
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([])
  const [isScanning, setIsScanning] = useState(false)
  const [fileName, setFileName] = useState('')

  const handleScan = async () => {
    setIsScanning(true)

    try {
      // Call REAL Security Wizard API
      const response = await fetch('http://localhost:8001/api/wizard/security_wizard/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: code,
          user_id: 'demo_user',
          context: {
            file_path: 'code.js',
            language: 'javascript'
          }
        })
      })

      const data = await response.json()

      if (data.success && data.analysis) {
        const issues = data.analysis.issues || []

        // Convert wizard issues to vulnerabilities
        const found: Vulnerability[] = issues.map((issue: any, index: number) => ({
          id: `vuln-${index}`,
          severity: (issue.severity === 'error' ? 'critical' :
                    issue.severity === 'warning' ? 'high' :
                    issue.severity === 'info' ? 'medium' : 'low') as any,
          title: issue.message || 'Security Issue',
          description: issue.suggestion || 'Review this code for security concerns',
          line: issue.line
        }))

        setVulnerabilities(found)
      } else {
        setVulnerabilities([])
      }
    } catch (error) {
      console.error('Security Wizard API error:', error)
      setVulnerabilities([{
        id: 'api-error',
        severity: 'high',
        title: 'API Connection Error',
        description: 'Could not connect to Security Wizard. Make sure backend is running at http://localhost:8001'
      }])
    }

    setIsScanning(false)
  }

  const loadSample = () => {
    setCode(`// Sample code with vulnerabilities
const apiKey = "sk_live_123456789abcdef"

function searchUsers(query) {
  const sql = "SELECT * FROM users WHERE name = '" + query + "'"
  return database.query(sql)
}

function renderContent(userInput) {
  document.getElementById('content').innerHTML = userInput
}`)
    setVulnerabilities([])
    setFileName('')
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      setCode(content)
      setFileName(file.name)
      setVulnerabilities([])
    }
    reader.readAsText(file)
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-300'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="inline-flex items-center gap-1">
          🔒 <strong>SOC2 & ISO 27001</strong> Compliance Scanner
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
                accept=".py,.js,.ts,.tsx,.jsx,.java,.cpp,.c,.h,.go,.rs,.rb,.php,.swift,.kt,.cs,.scala,.r,.m,.sh,.sql,.html,.css,.json,.xml,.yaml,.yml,.txt,.config,.conf"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
            <button
              type="button"
              onClick={loadSample}
              className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              Load Vulnerable Sample
            </button>
          </div>
        </div>
        <textarea
          value={code}
          onChange={(e) => {
            setCode(e.target.value)
            setFileName('')
          }}
          className="w-full h-48 px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono"
          placeholder="Paste your code here for security analysis..."
        />
        {fileName && (
          <div className="mt-1 text-xs text-green-600 font-medium">
            📄 {fileName} loaded
          </div>
        )}
      </div>

      <button
        onClick={handleScan}
        disabled={!code || isScanning}
        className="w-full px-4 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {isScanning ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Scanning for vulnerabilities...
          </>
        ) : (
          '🔍 Scan for Vulnerabilities'
        )}
      </button>

      {vulnerabilities.length > 0 ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-gray-900">
              Found {vulnerabilities.length} {vulnerabilities.length === 1 ? 'vulnerability' : 'vulnerabilities'}
            </h4>
            <div className="flex gap-2">
              {vulnerabilities.filter(v => v.severity === 'critical').length > 0 && (
                <span className="text-xs px-2 py-1 bg-red-100 text-red-800 rounded-full font-medium">
                  {vulnerabilities.filter(v => v.severity === 'critical').length} Critical
                </span>
              )}
              {vulnerabilities.filter(v => v.severity === 'high').length > 0 && (
                <span className="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded-full font-medium">
                  {vulnerabilities.filter(v => v.severity === 'high').length} High
                </span>
              )}
            </div>
          </div>

          {vulnerabilities.map((vuln) => (
            <div
              key={vuln.id}
              className={`border-2 rounded-lg p-3 ${getSeverityColor(vuln.severity)}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase">{vuln.severity}</span>
                    {vuln.line !== undefined && (
                      <span className="text-xs">Line {vuln.line + 1}</span>
                    )}
                  </div>
                  <h5 className="font-semibold mt-1">{vuln.title}</h5>
                  <p className="text-sm mt-1">{vuln.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : code && !isScanning ? (
        <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4 text-center">
          <span className="text-green-700 font-medium">✅ No vulnerabilities detected</span>
        </div>
      ) : null}

      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3 text-xs text-blue-800">
        <strong>Demo Mode:</strong> Detects SQL injection, XSS, secrets, and eval() usage.
        Production version scans for 200+ vulnerability patterns and generates compliance reports.
      </div>
    </div>
  )
}
