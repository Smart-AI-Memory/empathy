import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { Wizard, WizardCategory, DataClassification, SuggestedFilter } from '../types/wizard'
import { getSuggestionsForMultiple } from '../utils/smartSuggestions'

interface WizardState {
  // Data
  wizards: Wizard[]
  filteredWizards: Wizard[]

  // Filters
  selectedCategory: 'all' | WizardCategory
  selectedIndustries: string[]
  selectedCompliance: string[]
  selectedUseCases: string[]
  selectedEmpathyLevels: number[]
  selectedClassifications: DataClassification[]
  searchQuery: string

  // Smart suggestions
  suggestedFilters: SuggestedFilter[]

  // UI State
  isFilterSheetOpen: boolean
  viewMode: 'grid' | 'list'
  sortBy: 'popularity' | 'alphabetical' | 'newest'
  isLoading: boolean

  // Actions
  setWizards: (wizards: Wizard[]) => void
  setCategory: (category: 'all' | WizardCategory) => void
  toggleIndustry: (industry: string) => void
  toggleCompliance: (compliance: string) => void
  toggleUseCase: (useCase: string) => void
  toggleEmpathyLevel: (level: number) => void
  toggleClassification: (classification: DataClassification) => void
  setSearchQuery: (query: string) => void
  applySuggestedFilter: (filter: SuggestedFilter) => void
  dismissSuggestions: () => void
  clearFilters: () => void
  openFilterSheet: () => void
  closeFilterSheet: () => void
  setViewMode: (mode: 'grid' | 'list') => void
  setSortBy: (sort: 'popularity' | 'alphabetical' | 'newest') => void

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
        selectedUseCases: [],
        selectedEmpathyLevels: [],
        selectedClassifications: [],
        searchQuery: '',
        suggestedFilters: [],
        isFilterSheetOpen: false,
        viewMode: 'grid',
        sortBy: 'popularity',
        isLoading: false,

        // Actions
        setWizards: (wizards) => {
          set({ wizards, isLoading: false })
          get().filterWizards()
        },

        setCategory: (category) => {
          set({
            selectedCategory: category,
            // Clear industry filters if switching from domain category
            selectedIndustries: category === 'domain' ? get().selectedIndustries : [],
          })
          get().filterWizards()
        },

        toggleIndustry: (industry) => {
          const current = get().selectedIndustries
          const newIndustries = current.includes(industry)
            ? current.filter((i) => i !== industry)
            : [...current, industry]

          set({ selectedIndustries: newIndustries })

          // Generate smart suggestions for single industry
          const suggestions = getSuggestionsForMultiple(newIndustries)
          set({ suggestedFilters: suggestions })

          get().filterWizards()
        },

        toggleCompliance: (compliance) => {
          const current = get().selectedCompliance
          const newCompliance = current.includes(compliance)
            ? current.filter((c) => c !== compliance)
            : [...current, compliance]

          set({ selectedCompliance: newCompliance })
          get().filterWizards()
        },

        toggleUseCase: (useCase) => {
          const current = get().selectedUseCases
          const newUseCases = current.includes(useCase)
            ? current.filter((uc) => uc !== useCase)
            : [...current, useCase]

          set({ selectedUseCases: newUseCases })
          get().filterWizards()
        },

        toggleEmpathyLevel: (level) => {
          const current = get().selectedEmpathyLevels
          const newLevels = current.includes(level)
            ? current.filter((l) => l !== level)
            : [...current, level]

          set({ selectedEmpathyLevels: newLevels })
          get().filterWizards()
        },

        toggleClassification: (classification) => {
          const current = get().selectedClassifications
          const newClassifications = current.includes(classification)
            ? current.filter((c) => c !== classification)
            : [...current, classification]

          set({ selectedClassifications: newClassifications })
          get().filterWizards()
        },

        setSearchQuery: (query) => {
          set({ searchQuery: query })
          get().filterWizards()
        },

        applySuggestedFilter: (filter) => {
          const { type, value } = filter

          switch (type) {
            case 'compliance':
              get().toggleCompliance(value)
              break
            case 'classification':
              get().toggleClassification(value as DataClassification)
              break
            case 'related_industry':
              get().toggleIndustry(value)
              break
            case 'use_case':
              get().toggleUseCase(value)
              break
          }

          // Remove from suggestions
          set((state) => ({
            suggestedFilters: state.suggestedFilters.filter(
              (f) => f.value !== value
            ),
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
            selectedUseCases: [],
            selectedEmpathyLevels: [],
            selectedClassifications: [],
            searchQuery: '',
            suggestedFilters: [],
          })
          get().filterWizards()
        },

        openFilterSheet: () => set({ isFilterSheetOpen: true }),
        closeFilterSheet: () => set({ isFilterSheetOpen: false }),

        setViewMode: (mode) => set({ viewMode: mode }),
        setSortBy: (sort) => {
          set({ sortBy: sort })
          get().filterWizards()
        },

        getActiveFilterCount: () => {
          const state = get()
          return (
            (state.selectedCategory !== 'all' ? 1 : 0) +
            state.selectedIndustries.length +
            state.selectedCompliance.length +
            state.selectedUseCases.length +
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
            filtered = filtered.filter((w) => w.category === state.selectedCategory)
          }

          // Industry filter (for domain wizards)
          if (state.selectedIndustries.length > 0) {
            filtered = filtered.filter(
              (w) => w.industry && state.selectedIndustries.includes(w.industry)
            )
          }

          // Use case filter (for software/ai wizards)
          if (state.selectedUseCases.length > 0) {
            filtered = filtered.filter(
              (w) => w.useCase && state.selectedUseCases.includes(w.useCase)
            )
          }

          // Compliance filter
          if (state.selectedCompliance.length > 0) {
            filtered = filtered.filter((w) =>
              w.compliance.some((c) => state.selectedCompliance.includes(c))
            )
          }

          // Empathy level filter
          if (state.selectedEmpathyLevels.length > 0) {
            filtered = filtered.filter((w) =>
              state.selectedEmpathyLevels.includes(w.empathyLevel)
            )
          }

          // Classification filter
          if (state.selectedClassifications.length > 0) {
            filtered = filtered.filter((w) =>
              state.selectedClassifications.includes(w.classification)
            )
          }

          // Search filter
          if (state.searchQuery) {
            const query = state.searchQuery.toLowerCase()
            filtered = filtered.filter(
              (w) =>
                w.name.toLowerCase().includes(query) ||
                w.description.toLowerCase().includes(query) ||
                w.tags.some((tag) => tag.toLowerCase().includes(query)) ||
                w.compliance.some((c) => c.toLowerCase().includes(query)) ||
                w.features.some((f) => f.toLowerCase().includes(query))
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
