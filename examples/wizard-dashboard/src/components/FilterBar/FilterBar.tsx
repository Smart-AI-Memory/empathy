import { useWizardStore } from '../../stores/wizardStore'
import { CategoryFilter } from './CategoryFilter'
import { IndustryFilter } from './IndustryFilter'
import { SuggestedFilters } from './SuggestedFilters'

export function FilterBar() {
  const { clearFilters, getActiveFilterCount } = useWizardStore()
  const activeCount = getActiveFilterCount()

  return (
    <div className="space-y-4">
      {/* Top Row: Category + Clear */}
      <div className="flex items-center justify-between">
        <CategoryFilter />

        {activeCount > 0 && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-600 hover:text-gray-900 font-medium"
          >
            Clear All ({activeCount})
          </button>
        )}
      </div>

      {/* Industry Filter (conditional) */}
      <IndustryFilter />

      {/* Smart Suggestions */}
      <SuggestedFilters />
    </div>
  )
}
