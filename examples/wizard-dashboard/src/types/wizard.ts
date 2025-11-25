export type WizardCategory = 'domain' | 'software' | 'ai'

export type DataClassification = 'SENSITIVE' | 'INTERNAL' | 'PUBLIC'

export interface Wizard {
  id: string
  name: string
  description: string
  icon: string
  category: WizardCategory
  industry?: string // For domain wizards
  useCase?: string // For software/ai wizards

  // Compliance & Security
  compliance: string[] // e.g., ['HIPAA', 'SOX']
  classification: DataClassification
  retentionDays: number
  piiPatterns: string[]

  // Features
  empathyLevel: 3 | 4 | 5
  features: string[]
  tags: string[]

  // Metadata
  popularity: number // For sorting
  createdAt: number
  updatedAt: number

  // Links
  demoUrl?: string
  docsUrl?: string
  exampleUrl?: string
}

export interface SuggestedFilter {
  type: 'compliance' | 'classification' | 'retention' | 'related_industry' | 'use_case'
  value: string
  label: string
  icon?: string
}

export interface WizardFilters {
  category: 'all' | WizardCategory
  industries: string[]
  compliance: string[]
  useCases: string[]
  empathyLevels: number[]
  classifications: DataClassification[]
  searchQuery: string
}
