import { HealthcareDemo } from './HealthcareDemo'
import { FinanceDemo } from './FinanceDemo'
import { LegalDemo } from './LegalDemo'
import { DebuggingDemo } from './DebuggingDemo'
import { TestingDemo } from './TestingDemo'
import { SecurityDemo } from './SecurityDemo'
import { APIDemo } from './APIDemo'
import { PromptEngineeringDemo } from './PromptEngineeringDemo'
import { EnhancedDomainDemo } from './EnhancedDomainDemo'
import { EnhancedCoachDemo } from './EnhancedCoachDemo'
import { EnhancedAIDemo } from './EnhancedAIDemo'
import { wizardsData } from '../../data/wizards'

interface WizardDemoProps {
  wizardId: string
}

// Map wizard IDs to their custom demo components (if available)
const CUSTOM_DEMO_COMPONENTS: Record<string, React.ComponentType> = {
  healthcare: HealthcareDemo,
  finance: FinanceDemo,
  legal: LegalDemo,
  debugging: DebuggingDemo,
  testing: TestingDemo,
  security_wizard: SecurityDemo,
  api_wizard: APIDemo,
  prompt_engineering: PromptEngineeringDemo,
}

export function WizardDemo({ wizardId }: WizardDemoProps) {
  // Check if there's a custom demo component
  const CustomDemoComponent = CUSTOM_DEMO_COMPONENTS[wizardId]
  if (CustomDemoComponent) {
    return <CustomDemoComponent />
  }

  // Find wizard data
  const wizard = wizardsData.find(w => w.id === wizardId)
  if (!wizard) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 text-center">
        <div className="text-4xl mb-3">⚠️</div>
        <h4 className="font-semibold text-red-900 mb-2">Wizard Not Found</h4>
        <p className="text-sm text-red-800">
          Could not find wizard with ID: {wizardId}
        </p>
      </div>
    )
  }

  // Use enhanced category-specific demo
  if (wizard.category === 'domain') {
    const complianceMap: Record<string, string> = {
      education: 'FERPA',
      customer_support: 'GDPR',
      hr: 'Employment Law',
      sales: 'CRM Compliance',
      real_estate: 'Fair Housing',
      insurance: 'State Regulations',
      accounting: 'GAAP/SOX',
      research: 'IRB/Ethics',
      government: 'FOIA',
      retail: 'PCI-DSS',
      manufacturing: 'ISO 9001',
      logistics: 'DOT Regulations',
      technology: 'SOC 2'
    }
    return (
      <EnhancedDomainDemo
        wizardId={wizard.id}
        wizardName={wizard.name}
        complianceFramework={complianceMap[wizard.id] || 'Compliance'}
        icon={wizard.icon}
      />
    )
  }

  if (wizard.category === 'software') {
    const focusMap: Record<string, string> = {
      documentation: 'Documentation',
      performance_wizard: 'Performance',
      refactoring: 'Code Quality',
      database: 'Database Design',
      compliance: 'Compliance',
      monitoring: 'Observability',
      cicd: 'CI/CD Pipeline',
      accessibility: 'Accessibility',
      localization: 'i18n/l10n',
      migration: 'Migration',
      observability: 'Monitoring',
      scaling: 'Scalability'
    }
    return (
      <EnhancedCoachDemo
        wizardId={wizard.id}
        wizardName={wizard.name}
        focusArea={focusMap[wizard.id] || 'Code Analysis'}
        icon={wizard.icon}
      />
    )
  }

  if (wizard.category === 'ai') {
    const capabilityMap: Record<string, string> = {
      multi_model: 'Multi-Model Orchestration',
      rag_pattern: 'RAG Architecture',
      ai_performance: 'ML Performance',
      ai_collaboration: 'Agent Collaboration',
      advanced_debugging: 'AI System Debugging',
      agent_orchestration: 'Agent Orchestration',
      enhanced_testing: 'AI-Powered Testing',
      ai_documentation: 'Auto-Documentation',
      ai_context: 'Context Optimization',
      security_analysis: 'AI Security'
    }
    return (
      <EnhancedAIDemo
        wizardId={wizard.id}
        wizardName={wizard.name}
        capability={capabilityMap[wizard.id] || 'AI System Analysis'}
        icon={wizard.icon}
      />
    )
  }

  // Fallback
  return (
    <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 text-center">
      <p className="text-gray-600">Demo loading...</p>
    </div>
  )
}

// Export individual demos for direct use
export {
  HealthcareDemo,
  FinanceDemo,
  LegalDemo,
  DebuggingDemo,
  TestingDemo,
  SecurityDemo,
  APIDemo,
  PromptEngineeringDemo,
  EnhancedDomainDemo,
  EnhancedCoachDemo,
  EnhancedAIDemo
}
