import { SuggestedFilter } from '../types/wizard'

export const smartSuggestions: Record<string, SuggestedFilter[]> = {
  // Domain wizards
  healthcare: [
    { type: 'compliance', value: 'HIPAA', label: 'HIPAA §164.312', icon: '🏥' },
    { type: 'classification', value: 'SENSITIVE', label: 'SENSITIVE', icon: '🔴' },
    { type: 'retention', value: '90', label: '90-day retention', icon: '📅' },
    { type: 'related_industry', value: 'research', label: 'Research (IRB)', icon: '🔬' },
    { type: 'related_industry', value: 'insurance', label: 'Insurance', icon: '🛡️' },
  ],

  finance: [
    { type: 'compliance', value: 'SOX', label: 'SOX §802', icon: '💼' },
    { type: 'compliance', value: 'PCI-DSS', label: 'PCI-DSS v4.0', icon: '💳' },
    { type: 'classification', value: 'SENSITIVE', label: 'SENSITIVE', icon: '🔴' },
    { type: 'retention', value: '2555', label: '7-year retention', icon: '📅' },
    { type: 'related_industry', value: 'accounting', label: 'Accounting', icon: '🧮' },
  ],

  legal: [
    { type: 'compliance', value: 'Rule 502', label: 'Fed. Rules 502', icon: '⚖️' },
    { type: 'classification', value: 'SENSITIVE', label: 'SENSITIVE', icon: '🔴' },
    { type: 'retention', value: '2555', label: '7-year retention', icon: '📅' },
  ],

  education: [
    { type: 'compliance', value: 'FERPA', label: 'FERPA', icon: '🎓' },
    { type: 'classification', value: 'SENSITIVE', label: 'SENSITIVE', icon: '🔴' },
    { type: 'retention', value: '1825', label: '5-year retention', icon: '📅' },
    { type: 'related_industry', value: 'research', label: 'Research', icon: '🔬' },
  ],

  // Software development wizards
  debugging: [
    { type: 'use_case', value: 'performance', label: 'Performance', icon: '⚡' },
    { type: 'use_case', value: 'testing', label: 'Testing', icon: '🧪' },
    { type: 'related_industry', value: 'advanced_debugging', label: 'Advanced Debugging (AI)', icon: '🤖' },
  ],

  security: [
    { type: 'compliance', value: 'SOC2', label: 'SOC2', icon: '🛡️' },
    { type: 'use_case', value: 'compliance', label: 'Compliance', icon: '📋' },
    { type: 'related_industry', value: 'security_analysis', label: 'Security Analysis (AI)', icon: '🤖' },
  ],
}

export function getSuggestionsForIndustry(industry: string): SuggestedFilter[] {
  return smartSuggestions[industry.toLowerCase()] || []
}

export function getSuggestionsForMultiple(industries: string[]): SuggestedFilter[] {
  // If multiple industries selected, don't show suggestions
  if (industries.length !== 1) return []

  return getSuggestionsForIndustry(industries[0])
}
