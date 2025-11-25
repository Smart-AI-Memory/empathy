# Wizard Dashboard - Responsive Implementation Plan

**Tech Stack & Responsive Design Strategy**

Version: 1.0
Date: 2025-11-25
Status: Ready for Development

---

## ✅ Confirmed Design Decisions

### Desktop/Tablet (>768px)
- **Layout:** Wireframe 2 (Compact Filter Bar) with expanded features
- **Filters:** Horizontal filter bar with all options visible
- **Smart Suggestions:** Option A (highlighted suggestion pills)
- **Try Demo:** Inline expandable with "View Full Demo" link
- **Search:** All fields, debounced 300ms, filter grid + highlight

### Mobile/Phone (<768px)
- **Layout:** Ultra-compact with bottom sheet filters
- **Filters:** Icon button → Bottom sheet drawer
- **Grid:** Single column wizard cards
- **Navigation:** Sticky category tabs at top
- **Search:** Full-width with slide-in results

---

## 📐 Responsive Breakpoint Strategy

```typescript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',   // Large phones
      'md': '768px',   // Tablets
      'lg': '1024px',  // Laptops
      'xl': '1280px',  // Desktops
      '2xl': '1536px', // Large desktops
    },
  },
}

// Usage in components
<div className="
  grid
  grid-cols-1           // Mobile: 1 column
  md:grid-cols-2        // Tablet: 2 columns
  lg:grid-cols-3        // Desktop: 3 columns
  xl:grid-cols-4        // Large desktop: 4 columns
  gap-6
">
```

---

## 🎨 Desktop/Tablet Design (>768px)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧙 Empathy Wizards              [Search: "Type to search..."]  [?] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ FILTERS                                          [Clear All] │   │
│ ├──────────────────────────────────────────────────────────────┤   │
│ │                                                              │   │
│ │ Category: [All] [Domain] [Software] [AI]           44 total │   │
│ │                                                              │   │
│ │ Industry:                                                    │   │
│ │ [Healthcare] [Finance] [Legal] [Education] [+12 more ▼]     │   │
│ │                                                              │   │
│ │ Compliance:                                                  │   │
│ │ [HIPAA] [SOX] [PCI-DSS] [FERPA] [+5 more ▼]                │   │
│ │                                                              │   │
│ │ 💡 SUGGESTED: [+ HIPAA] [+ SENSITIVE]  (based on selection) │   │
│ │                                                              │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ Showing 16 wizards                          Sort: [Popular ▼]       │
│                                                                      │
│ ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐         │
│ │🏥 Health  │  │💰 Finance │  │⚖️ Legal   │  │🎓 Education│         │
│ │  care     │  │           │  │           │  │           │         │
│ │           │  │           │  │           │  │           │         │
│ │[HIPAA]    │  │[SOX]      │  │[Rule 502] │  │[FERPA]    │         │
│ │❤️ Lvl 3   │  │❤️ Lvl 3   │  │❤️ Lvl 3   │  │❤️ Lvl 3   │         │
│ │           │  │           │  │           │  │           │         │
│ │[Try Demo] │  │[Try Demo] │  │[Try Demo] │  │[Try Demo] │         │
│ └───────────┘  └───────────┘  └───────────┘  └───────────┘         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Mobile/Phone Design (<768px)

```
┌─────────────────────────────────┐
│ 🧙 Empathy    🔍 [Filter] [⋮]  │
├─────────────────────────────────┤
│                                 │
│ [All] [Domain] [Software] [AI]  │  ← Sticky tabs
│ ─────────────────────────────── │
│                                 │
│ Active Filters: 2               │
│ [Healthcare ×] [HIPAA ×]        │
│                                 │
│ 💡 Suggested: [+SENSITIVE]      │
│                                 │
│ ─────────────────────────────── │
│                                 │
│ 16 wizards · [Popular ▼]        │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 🏥 Healthcare Wizard        │ │
│ │ ─────────────────────────── │ │
│ │ HIPAA-compliant clinical AI │ │
│ │                             │ │
│ │ [HIPAA] [SENSITIVE]         │ │
│ │ ❤️ Level 3 · 90d retention  │ │
│ │                             │ │
│ │ [Try Demo ▼]                │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 💰 Finance Wizard           │ │
│ └─────────────────────────────┘ │
│                                 │
│         [Load More...]          │
│                                 │
└─────────────────────────────────┘

BOTTOM SHEET (when [Filter] clicked):
┌─────────────────────────────────┐
│         [Swipe down to close]   │
│ ─────────────────────────────── │
│ FILTERS                         │
│                                 │
│ ▼ Industry                      │
│   ☐ Healthcare                  │
│   ☐ Finance                     │
│   ☐ Legal                       │
│   ... (scrollable list)         │
│                                 │
│ ▼ Compliance                    │
│   ☐ HIPAA                       │
│   ☐ SOX                         │
│   ☐ PCI-DSS                     │
│                                 │
│ ▼ Empathy Level                 │
│   ☐ Level 3                     │
│   ☐ Level 4                     │
│   ☐ Level 5                     │
│                                 │
│ [Clear All]    [Apply Filters]  │
└─────────────────────────────────┘
```

---

## 🏗️ Component Architecture

### Main Layout Component

```typescript
// components/WizardDashboard.tsx
import { useState, useEffect } from 'react'
import { useWizardStore } from '../stores/wizardStore'
import { FilterBar } from './FilterBar/FilterBar'
import { MobileFilterSheet } from './FilterBar/MobileFilterSheet'
import { WizardGrid } from './WizardGrid/WizardGrid'
import { SearchBar } from './Search/SearchBar'

export function WizardDashboard() {
  const [isMobile, setIsMobile] = useState(false)
  const filteredWizards = useWizardStore(state => state.filteredWizards)

  useEffect(() => {
    // Detect mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <span className="text-2xl">🧙</span>
              <h1 className="ml-2 text-xl font-bold hidden md:block">
                Empathy Wizards
              </h1>
              <h1 className="ml-2 text-lg font-bold md:hidden">
                Empathy
              </h1>
            </div>

            {/* Desktop Search */}
            <div className="hidden md:block flex-1 max-w-lg mx-8">
              <SearchBar />
            </div>

            {/* Mobile Filter Button */}
            {isMobile && <MobileFilterButton />}
          </div>

          {/* Mobile Search */}
          {isMobile && (
            <div className="pb-4">
              <SearchBar />
            </div>
          )}
        </div>
      </header>

      {/* Desktop/Tablet Filter Bar */}
      {!isMobile && (
        <div className="bg-white border-b sticky top-16 z-30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <FilterBar />
          </div>
        </div>
      )}

      {/* Mobile Category Tabs */}
      {isMobile && <MobileCategoryTabs />}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <WizardGrid wizards={filteredWizards} isMobile={isMobile} />
      </main>

      {/* Mobile Bottom Sheet */}
      {isMobile && <MobileFilterSheet />}
    </div>
  )
}
```

---

## 🎯 Desktop Filter Bar Component

```typescript
// components/FilterBar/FilterBar.tsx
import { useWizardStore } from '../../stores/wizardStore'
import { CategoryFilter } from './CategoryFilter'
import { IndustryFilter } from './IndustryFilter'
import { ComplianceFilter } from './ComplianceFilter'
import { SuggestedFilters } from './SuggestedFilters'

export function FilterBar() {
  const clearFilters = useWizardStore(state => state.clearFilters)
  const activeFilterCount = useWizardStore(state => state.getActiveFilterCount())

  return (
    <div className="space-y-4">
      {/* Top Row: Category + Clear */}
      <div className="flex items-center justify-between">
        <CategoryFilter />

        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Clear All ({activeFilterCount})
          </button>
        )}
      </div>

      {/* Second Row: Industry (if Domain category selected) */}
      <IndustryFilter />

      {/* Third Row: Compliance + Use Case */}
      <div className="flex gap-8">
        <div className="flex-1">
          <ComplianceFilter />
        </div>
        <div className="flex-1">
          <UseCaseFilter />
        </div>
      </div>

      {/* Smart Suggestions */}
      <SuggestedFilters />
    </div>
  )
}

// CategoryFilter.tsx
export function CategoryFilter() {
  const { selectedCategory, setCategory } = useWizardStore()

  const categories = [
    { id: 'all', label: 'All Wizards', count: 44 },
    { id: 'domain', label: 'Domain & Industry', count: 16 },
    { id: 'software', label: 'Software Development', count: 16 },
    { id: 'ai', label: 'AI & Engineering', count: 12 },
  ]

  return (
    <div className="flex gap-2">
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => setCategory(cat.id)}
          className={`
            px-4 py-2 rounded-lg font-medium transition-colors
            ${selectedCategory === cat.id
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }
          `}
        >
          {cat.label}
          <span className="ml-2 text-sm opacity-75">({cat.count})</span>
        </button>
      ))}
    </div>
  )
}

// IndustryFilter.tsx
export function IndustryFilter() {
  const { selectedCategory, selectedIndustries, toggleIndustry } = useWizardStore()

  if (selectedCategory !== 'domain') return null

  const industries = [
    { id: 'healthcare', label: '🏥 Healthcare', icon: '🏥' },
    { id: 'finance', label: '💰 Finance', icon: '💰' },
    { id: 'legal', label: '⚖️ Legal', icon: '⚖️' },
    { id: 'education', label: '🎓 Education', icon: '🎓' },
    // ... more industries
  ]

  const [showAll, setShowAll] = useState(false)
  const visibleIndustries = showAll ? industries : industries.slice(0, 8)

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-2">Industry:</h3>
      <div className="flex flex-wrap gap-2">
        {visibleIndustries.map((industry) => (
          <button
            key={industry.id}
            onClick={() => toggleIndustry(industry.id)}
            className={`
              px-3 py-1.5 rounded-full text-sm font-medium transition-colors
              ${selectedIndustries.includes(industry.id)
                ? 'bg-blue-100 text-blue-700 border-2 border-blue-500'
                : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-gray-400'
              }
            `}
          >
            {industry.label}
          </button>
        ))}

        {industries.length > 8 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-3 py-1.5 text-sm text-blue-600 hover:text-blue-700"
          >
            {showAll ? 'Show Less' : `+${industries.length - 8} more`}
          </button>
        )}
      </div>
    </div>
  )
}

// SuggestedFilters.tsx (Smart Pattern 2 Implementation)
export function SuggestedFilters() {
  const { suggestedFilters, applySuggestedFilter, dismissSuggestions } = useWizardStore()

  if (suggestedFilters.length === 0) return null

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">💡</span>
            <h3 className="text-sm font-medium text-blue-900">
              Suggested Filters
            </h3>
          </div>

          <div className="flex flex-wrap gap-2">
            {suggestedFilters.map((filter) => (
              <button
                key={filter.value}
                onClick={() => applySuggestedFilter(filter)}
                className="
                  px-3 py-1.5 bg-white border-2 border-blue-300
                  rounded-full text-sm font-medium text-blue-700
                  hover:bg-blue-100 hover:border-blue-500
                  transition-colors
                "
              >
                + {filter.label}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={dismissSuggestions}
          className="text-blue-600 hover:text-blue-800 text-sm ml-4"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
```

---

## 📱 Mobile Bottom Sheet Component

```typescript
// components/FilterBar/MobileFilterSheet.tsx
import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { useWizardStore } from '../../stores/wizardStore'

export function MobileFilterSheet() {
  const { isFilterSheetOpen, closeFilterSheet } = useWizardStore()
  const { selectedIndustries, selectedCompliance, toggleIndustry, toggleCompliance } = useWizardStore()

  return (
    <Transition.Root show={isFilterSheetOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={closeFilterSheet}>
        {/* Backdrop */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        </Transition.Child>

        {/* Bottom Sheet */}
        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-x-0 bottom-0 flex max-h-[80vh]">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-300"
                enterFrom="translate-y-full"
                enterTo="translate-y-0"
                leave="transform transition ease-in-out duration-300"
                leaveFrom="translate-y-0"
                leaveTo="translate-y-full"
              >
                <Dialog.Panel className="pointer-events-auto w-full">
                  <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl rounded-t-2xl">
                    {/* Handle Bar */}
                    <div className="flex justify-center pt-3 pb-2">
                      <div className="w-12 h-1 bg-gray-300 rounded-full" />
                    </div>

                    {/* Header */}
                    <div className="border-b px-6 py-4">
                      <div className="flex items-center justify-between">
                        <Dialog.Title className="text-lg font-semibold">
                          Filters
                        </Dialog.Title>
                        <button
                          onClick={closeFilterSheet}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          ✕
                        </button>
                      </div>
                    </div>

                    {/* Filter Content */}
                    <div className="flex-1 px-6 py-4 space-y-6">
                      {/* Industry Section */}
                      <div>
                        <h3 className="font-medium mb-3">Industry</h3>
                        <div className="space-y-2">
                          {industries.map((industry) => (
                            <label
                              key={industry.id}
                              className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50"
                            >
                              <input
                                type="checkbox"
                                checked={selectedIndustries.includes(industry.id)}
                                onChange={() => toggleIndustry(industry.id)}
                                className="w-5 h-5 text-blue-600 rounded"
                              />
                              <span className="text-2xl">{industry.icon}</span>
                              <span className="flex-1">{industry.label}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      {/* Compliance Section */}
                      <div>
                        <h3 className="font-medium mb-3">Compliance</h3>
                        <div className="space-y-2">
                          {complianceOptions.map((option) => (
                            <label
                              key={option.id}
                              className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50"
                            >
                              <input
                                type="checkbox"
                                checked={selectedCompliance.includes(option.id)}
                                onChange={() => toggleCompliance(option.id)}
                                className="w-5 h-5 text-blue-600 rounded"
                              />
                              <span className="flex-1">{option.label}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      {/* Empathy Level Section */}
                      <div>
                        <h3 className="font-medium mb-3">Empathy Level</h3>
                        {/* ... similar checkbox list */}
                      </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="border-t px-6 py-4 bg-gray-50">
                      <div className="flex gap-3">
                        <button
                          onClick={clearFilters}
                          className="flex-1 px-4 py-3 bg-white border-2 border-gray-300 rounded-lg font-medium"
                        >
                          Clear All
                        </button>
                        <button
                          onClick={closeFilterSheet}
                          className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-medium"
                        >
                          Apply Filters
                        </button>
                      </div>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}

// Mobile Category Tabs
export function MobileCategoryTabs() {
  const { selectedCategory, setCategory } = useWizardStore()

  const categories = [
    { id: 'all', label: 'All' },
    { id: 'domain', label: 'Domain' },
    { id: 'software', label: 'Software' },
    { id: 'ai', label: 'AI' },
  ]

  return (
    <div className="bg-white border-b sticky top-16 z-30">
      <div className="flex overflow-x-auto no-scrollbar">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setCategory(cat.id)}
            className={`
              flex-1 min-w-[80px] px-4 py-3 text-sm font-medium border-b-2 transition-colors
              ${selectedCategory === cat.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600'
              }
            `}
          >
            {cat.label}
          </button>
        ))}
      </div>
    </div>
  )
}
```

---

## 🃏 Wizard Card Component (Responsive)

```typescript
// components/WizardGrid/WizardCard.tsx
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wizard } from '../../types/wizard'
import { ComplianceBadge } from '../common/ComplianceBadge'
import { EmpathyLevelIndicator } from '../common/EmpathyLevelIndicator'
import { InlineDemo } from './InlineDemo'

interface WizardCardProps {
  wizard: Wizard
  isMobile?: boolean
}

export function WizardCard({ wizard, isMobile }: WizardCardProps) {
  const [isDemoExpanded, setIsDemoExpanded] = useState(false)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`
        bg-white rounded-lg border-2 border-gray-200
        hover:border-blue-400 hover:shadow-lg
        transition-all duration-200
        ${isDemoExpanded ? 'col-span-full' : ''}
      `}
    >
      {/* Card Header */}
      <div className="p-4 md:p-6">
        <div className="flex items-start gap-3">
          <span className="text-3xl md:text-4xl">{wizard.icon}</span>
          <div className="flex-1">
            <h3 className="text-lg md:text-xl font-bold text-gray-900">
              {wizard.name}
            </h3>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {wizard.description}
            </p>
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mt-4">
          {wizard.compliance.map((comp) => (
            <ComplianceBadge key={comp} compliance={comp} />
          ))}
          <ClassificationBadge classification={wizard.classification} />
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 mt-4 text-sm text-gray-600">
          <EmpathyLevelIndicator level={wizard.empathyLevel} />
          <span>·</span>
          <span>📊 {wizard.retentionDays}d retention</span>
          {!isMobile && (
            <>
              <span>·</span>
              <span>🔒 {wizard.piiPatterns.length} PII patterns</span>
            </>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3 mt-4">
          <button
            onClick={() => setIsDemoExpanded(!isDemoExpanded)}
            className="
              flex-1 md:flex-none
              px-4 py-2 bg-blue-600 text-white rounded-lg
              font-medium hover:bg-blue-700 transition-colors
              flex items-center justify-center gap-2
            "
          >
            <span>Try Demo</span>
            <motion.span
              animate={{ rotate: isDemoExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              ▼
            </motion.span>
          </button>

          <a
            href={`/wizards/${wizard.id}`}
            className="
              flex-1 md:flex-none
              px-4 py-2 bg-white border-2 border-gray-300
              rounded-lg font-medium hover:border-gray-400
              transition-colors text-center
            "
          >
            View Docs
          </a>
        </div>
      </div>

      {/* Inline Demo (Expandable) */}
      <AnimatePresence>
        {isDemoExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t overflow-hidden"
          >
            <InlineDemo wizard={wizard} isMobile={isMobile} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
```

---

## 📊 Zustand Store (Final Implementation)

```typescript
// stores/wizardStore.ts
import create from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { Wizard, WizardFilters, SuggestedFilter } from '../types/wizard'
import { smartSuggestions } from '../utils/smartSuggestions'

interface WizardState {
  // Data
  wizards: Wizard[]
  filteredWizards: Wizard[]

  // Filters
  selectedCategory: 'all' | 'domain' | 'software' | 'ai'
  selectedIndustries: string[]
  selectedCompliance: string[]
  selectedEmpathyLevels: number[]
  selectedClassifications: string[]
  searchQuery: string

  // Smart suggestions
  suggestedFilters: SuggestedFilter[]

  // UI State
  isFilterSheetOpen: boolean
  viewMode: 'grid' | 'list'
  sortBy: 'popularity' | 'alphabetical' | 'newest'

  // Actions
  setCategory: (category: string) => void
  toggleIndustry: (industry: string) => void
  toggleCompliance: (compliance: string) => void
  setSearchQuery: (query: string) => void
  applySuggestedFilter: (filter: SuggestedFilter) => void
  dismissSuggestions: () => void
  clearFilters: () => void
  openFilterSheet: () => void
  closeFilterSheet: () => void

  // Computed
  getActiveFilterCount: () => number
  filterWizards: () => void
}

export const useWizardStore = create<WizardState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        wizards: [],
        filteredWizards: [],
        selectedCategory: 'all',
        selectedIndustries: [],
        selectedCompliance: [],
        selectedEmpathyLevels: [],
        selectedClassifications: [],
        searchQuery: '',
        suggestedFilters: [],
        isFilterSheetOpen: false,
        viewMode: 'grid',
        sortBy: 'popularity',

        // Actions
        setCategory: (category) => {
          set({ selectedCategory: category })
          get().filterWizards()
        },

        toggleIndustry: (industry) => {
          const current = get().selectedIndustries
          const newIndustries = current.includes(industry)
            ? current.filter(i => i !== industry)
            : [...current, industry]

          set({ selectedIndustries: newIndustries })

          // Generate smart suggestions for single industry
          if (newIndustries.length === 1) {
            const suggestions = smartSuggestions[newIndustries[0]] || []
            set({ suggestedFilters: suggestions })
          } else {
            set({ suggestedFilters: [] })
          }

          get().filterWizards()
        },

        toggleCompliance: (compliance) => {
          const current = get().selectedCompliance
          const newCompliance = current.includes(compliance)
            ? current.filter(c => c !== compliance)
            : [...current, compliance]

          set({ selectedCompliance: newCompliance })
          get().filterWizards()
        },

        setSearchQuery: (query) => {
          set({ searchQuery: query })
          // Debounce is handled in the component
          get().filterWizards()
        },

        applySuggestedFilter: (filter) => {
          const { type, value } = filter

          switch (type) {
            case 'compliance':
              get().toggleCompliance(value)
              break
            case 'classification':
              // Add classification filter
              break
            case 'related_industry':
              get().toggleIndustry(value)
              break
          }

          // Remove from suggestions
          set((state) => ({
            suggestedFilters: state.suggestedFilters.filter(
              f => f.value !== value
            )
          }))
        },

        dismissSuggestions: () => {
          set({ suggestedFilters: [] })
        },

        clearFilters: () => {
          set({
            selectedCategory: 'all',
            selectedIndustries: [],
            selectedCompliance: [],
            selectedEmpathyLevels: [],
            selectedClassifications: [],
            searchQuery: '',
            suggestedFilters: [],
          })
          get().filterWizards()
        },

        openFilterSheet: () => set({ isFilterSheetOpen: true }),
        closeFilterSheet: () => set({ isFilterSheetOpen: false }),

        getActiveFilterCount: () => {
          const state = get()
          return (
            (state.selectedCategory !== 'all' ? 1 : 0) +
            state.selectedIndustries.length +
            state.selectedCompliance.length +
            state.selectedEmpathyLevels.length +
            state.selectedClassifications.length +
            (state.searchQuery ? 1 : 0)
          )
        },

        filterWizards: () => {
          const state = get()
          let filtered = [...state.wizards]

          // Category filter
          if (state.selectedCategory !== 'all') {
            filtered = filtered.filter(w => w.category === state.selectedCategory)
          }

          // Industry filter
          if (state.selectedIndustries.length > 0) {
            filtered = filtered.filter(w =>
              state.selectedIndustries.includes(w.industry)
            )
          }

          // Compliance filter
          if (state.selectedCompliance.length > 0) {
            filtered = filtered.filter(w =>
              w.compliance.some(c => state.selectedCompliance.includes(c))
            )
          }

          // Search filter
          if (state.searchQuery) {
            const query = state.searchQuery.toLowerCase()
            filtered = filtered.filter(w =>
              w.name.toLowerCase().includes(query) ||
              w.description.toLowerCase().includes(query) ||
              w.tags.some(tag => tag.toLowerCase().includes(query)) ||
              w.compliance.some(c => c.toLowerCase().includes(query))
            )
          }

          // Sort
          filtered.sort((a, b) => {
            switch (state.sortBy) {
              case 'popularity':
                return b.popularity - a.popularity
              case 'alphabetical':
                return a.name.localeCompare(b.name)
              case 'newest':
                return b.createdAt - a.createdAt
              default:
                return 0
            }
          })

          set({ filteredWizards: filtered })
        },
      }),
      {
        name: 'wizard-filters',
        partialize: (state) => ({
          selectedCategory: state.selectedCategory,
          viewMode: state.viewMode,
          sortBy: state.sortBy,
        }),
      }
    )
  )
)
```

---

## 🚀 Next Steps

### Phase 1: Setup (Week 1)
```bash
# 1. Initialize project
npx create-react-app wizard-dashboard --template typescript
cd wizard-dashboard

# 2. Install dependencies
npm install zustand react-router-dom
npm install -D tailwindcss postcss autoprefixer
npm install @headlessui/react framer-motion
npm install meilisearch

# 3. Initialize Tailwind
npx tailwindcss init -p

# 4. Project structure
mkdir -p src/{components/{FilterBar,WizardGrid,Search,common},stores,hooks,utils,types}
```

### Phase 2: Core Components (Week 1-2)
- ✅ Set up Zustand store
- ✅ Build FilterBar (desktop)
- ✅ Build MobileFilterSheet (mobile)
- ✅ Build WizardCard component
- ✅ Build WizardGrid component
- ✅ Implement smart suggestions

### Phase 3: Features (Week 2-3)
- ✅ Add search functionality
- ✅ Implement inline demo
- ✅ Build wizard detail page
- ✅ Add URL-based routing
- ✅ Mobile responsive testing

### Phase 4: Polish (Week 3-4)
- ✅ Add analytics tracking
- ✅ Performance optimization
- ✅ Accessibility audit
- ✅ User testing
- ✅ Deploy to production

---

**Ready to start building! 🚀**

**Tech Stack Confirmed:**
- React + TypeScript
- Zustand (state management)
- Tailwind CSS (styling)
- Headless UI (accessible components)
- Framer Motion (animations)
- React Router (routing)
- MeiliSearch (search)

**Design Confirmed:**
- Desktop/Tablet: Wireframe 2 with smart suggestions
- Mobile: Compact with bottom sheet
- Pattern 2: Smart filtering (no forced progressive disclosure)
