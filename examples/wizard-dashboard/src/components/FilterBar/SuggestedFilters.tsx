import { useWizardStore } from '../../stores/wizardStore'

export function SuggestedFilters() {
  const { suggestedFilters, applySuggestedFilter, dismissSuggestions } = useWizardStore()

  if (suggestedFilters.length === 0) return null

  return (
    <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">💡</span>
            <h3 className="text-sm font-medium text-primary-900">
              Suggested Filters
            </h3>
          </div>

          <div className="flex flex-wrap gap-2">
            {suggestedFilters.map((filter) => (
              <button
                key={filter.value}
                onClick={() => applySuggestedFilter(filter)}
                className="
                  px-3 py-1.5 bg-white border-2 border-primary-300
                  rounded-full text-sm font-medium text-primary-700
                  hover:bg-primary-100 hover:border-primary-500
                  transition-colors flex items-center gap-1
                "
              >
                {filter.icon && <span>{filter.icon}</span>}
                <span>+ {filter.label}</span>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={dismissSuggestions}
          className="text-primary-600 hover:text-primary-800 text-sm ml-4"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
