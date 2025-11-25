import { useState } from 'react'

interface DomainAnalysis {
  piiDetected: string[]
  classification: string
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  compliance: string[]
  recommendations: string[]
  confidence: number
}

interface EnhancedDomainDemoProps {
  wizardId: string
  wizardName: string
  complianceFramework: string
  icon: string
}

export function EnhancedDomainDemo({ wizardId, wizardName, complianceFramework, icon }: EnhancedDomainDemoProps) {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [analysis, setAnalysis] = useState<DomainAnalysis | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [sampleLoaded, setSampleLoaded] = useState(false)
  const [fileName, setFileName] = useState('')

  const handleProcess = async () => {
    setIsProcessing(true)
    setOutput('')
    setAnalysis(null)
    setSampleLoaded(false)

    try {
      const response = await fetch(`http://localhost:8001/api/wizard/${wizardId}/process`, {
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
        const piiTypes = piiDetected.map((p: any) => p.type || p.toString())

        const riskLevel: 'low' | 'medium' | 'high' | 'critical' =
          piiDetected.length === 0 ? 'low' :
          piiDetected.length >= 5 ? 'critical' :
          piiDetected.length >= 3 ? 'high' :
          piiDetected.length >= 2 ? 'medium' : 'low'

        const recommendations = [
          `Implement ${complianceFramework} data protection controls`,
          'Enable audit logging for all data access',
          'Use encryption at rest (AES-256-GCM)',
          'Apply role-based access controls (RBAC)',
          'Maintain compliance documentation'
        ]

        setOutput(data.output || 'Processing complete')
        setAnalysis({
          piiDetected: piiTypes,
          classification: data.analysis.classification || 'processed',
          riskLevel,
          compliance: data.analysis.compliance || [complianceFramework],
          recommendations,
          confidence: data.analysis.confidence || 0.85
        })
      } else {
        setOutput(data.error || 'Error processing')
      }
    } catch (error) {
      console.error(`${wizardName} API error:`, error)
      setOutput('Error: Could not connect to wizard API. Make sure backend is running at http://localhost:8001')
    }

    setIsProcessing(false)
  }

  const loadSample = () => {
    const samples: Record<string, string> = {
      education: 'Student Record:\nName: Sarah Johnson\nStudent ID: 20241234\nGrade: 10th\nGPA: 3.8\nParent Contact: (555) 123-4567',
      customer_support: 'Support Ticket #CS-2024-5678\nCustomer: John Smith\nEmail: john.smith@email.com\nIssue: Product not working\nAccount ID: ACC-123456',
      hr: 'Employee Record:\nName: Michael Chen\nEmployee ID: EMP-789\nSSN: 123-45-6789\nSalary: $85,000\nDepartment: Engineering',
      sales: 'Sales Lead:\nProspect: TechCorp Inc.\nContact: Jane Doe\nEmail: jane@techcorp.com\nPhone: (555) 987-6543\nDeal Value: $150,000',
      real_estate: 'Property Listing:\nAddress: 123 Main St, City, ST 12345\nOwner: Robert Williams\nPrice: $450,000\nAgent Contact: (555) 234-5678',
      insurance: 'Policy Application:\nApplicant: Lisa Anderson\nPolicy #: POL-2024-999\nSSN: 987-65-4321\nCoverage: $500,000\nBeneficiary: Spouse',
      accounting: 'Financial Transaction:\nAccount: ACC-456789\nAmount: $25,000.00\nRouting: 021000021\nDate: 2024-01-15\nDescription: Quarterly payment',
      research: 'Research Participant:\nSubject ID: P-2024-042\nAge: 34\nDiagnosis: Hypertension\nTrial: Phase III\nConsent Date: 2024-01-10',
      government: 'Citizen Record:\nName: David Martinez\nSSN: 456-78-9012\nAddress: 456 Oak Ave\nBenefit ID: GOV-2024-333\nProgram: Social Services',
      retail: 'Customer Purchase:\nName: Emily Brown\nCard: 5412-****-****-8901\nAmount: $234.56\nStore: Downtown Location\nDate: 2024-01-20',
      manufacturing: 'Quality Report:\nBatch ID: MFG-2024-Q1-789\nInspector: James Wilson\nEmployee ID: EMP-456\nDefect Rate: 0.02%\nFacility: Plant A',
      logistics: 'Shipment Tracking:\nDriver: Carlos Rodriguez\nLicense: DL-789456\nVehicle: VIN-1234567890\nRoute: NYC-BOS\nCargo Value: $75,000',
      technology: 'System Access Log:\nUser: admin@company.com\nIP: 192.168.1.100\nAPI Key: sk-1234567890abcdef\nSession: SES-2024-xyz\nTimestamp: 2024-01-20 14:30'
    }
    setInput(samples[wizardId] || `Sample data for ${wizardName}`)
    setOutput('')
    setAnalysis(null)
    setSampleLoaded(true)
    setFileName('')
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      setInput(content)
      setFileName(file.name)
      setSampleLoaded(false)
      setOutput('')
      setAnalysis(null)
    }
    reader.readAsText(file)
  }

  const getRiskColor = (risk: string) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-500',
      high: 'bg-orange-100 text-orange-800 border-orange-500',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-500',
      low: 'bg-green-100 text-green-800 border-green-500'
    }
    return colors[risk as keyof typeof colors] || colors.low
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="inline-flex items-center gap-1">
          <span className="text-lg">{icon}</span> <strong>{complianceFramework}</strong> Compliance & Data Protection
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">Input Data</label>
            <div className="flex gap-2">
              <label className="text-xs text-primary-600 hover:text-primary-700 font-medium cursor-pointer">
                📁 Upload File
                <input
                  type="file"
                  accept=".txt,.csv,.json,.xml,.pdf,.doc,.docx,.xls,.xlsx,.log,.md"
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
            value={input}
            onChange={(e) => {
              setInput(e.target.value)
              setSampleLoaded(false)
              setFileName('')
            }}
            className={`w-full h-48 px-3 py-2 border-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono transition-colors ${
              sampleLoaded ? 'border-primary-400 bg-primary-50' : 'border-gray-300'
            }`}
            placeholder="Enter sensitive data to analyze..."
          />
          {fileName && (
            <div className="mt-1 text-xs text-green-600 font-medium">
              📄 {fileName} loaded
            </div>
          )}
          {sampleLoaded && !fileName && (
            <div className="mt-1 text-xs text-primary-600 font-medium">
              ✓ Sample loaded - Click "Analyze & Protect" to process
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Protected Output</label>
          <div className="w-full h-40 px-3 py-2 border-2 border-green-300 bg-green-50 rounded-lg text-sm overflow-auto font-mono whitespace-pre-wrap">
            {output || 'Protected data will appear here...'}
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
          `${icon} Analyze & Protect`
        )}
      </button>

      {analysis && (
        <div className="space-y-4">
          {/* Risk Assessment */}
          <div className={`border-l-4 rounded p-4 ${getRiskColor(analysis.riskLevel)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h5 className="font-semibold">Data Risk Level</h5>
                <p className="text-sm mt-1">
                  {analysis.piiDetected.length} sensitive items detected • {Math.round(analysis.confidence * 100)}% confidence
                </p>
              </div>
              <span className="text-2xl font-bold uppercase">{analysis.riskLevel}</span>
            </div>
          </div>

          {/* PII Detection */}
          {analysis.piiDetected.length > 0 && (
            <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
              <h5 className="font-semibold text-blue-900 mb-2">🔍 Sensitive Data Detected</h5>
              <div className="flex flex-wrap gap-2">
                {analysis.piiDetected.map((pii, i) => (
                  <span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {pii}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Compliance */}
          <div className="bg-purple-50 border-2 border-purple-300 rounded-lg p-4">
            <h5 className="font-semibold text-purple-900 mb-2">📋 Compliance Requirements</h5>
            <div className="flex flex-wrap gap-2">
              {analysis.compliance.map((comp, i) => (
                <span key={i} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                  {comp}
                </span>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4">
            <h5 className="font-semibold text-green-900 mb-2">💡 Security Recommendations</h5>
            <ol className="space-y-2">
              {analysis.recommendations.slice(0, 4).map((rec, i) => (
                <li key={i} className="text-sm text-green-800 flex items-start gap-2">
                  <span className="text-green-600 font-bold">{i + 1}.</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}

      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 text-xs text-gray-600">
        <strong>Live Backend:</strong> Connected to production {wizardName} with {complianceFramework} compliance rules.
      </div>
    </div>
  )
}
