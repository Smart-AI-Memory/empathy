import { useState, useMemo } from 'react'
import { useWizardStore } from '../../stores/wizardStore'

const allIndustries = [
  { id: 'healthcare', label: 'Healthcare', icon: '🏥' },
  { id: 'finance', label: 'Finance', icon: '💰' },
  { id: 'legal', label: 'Legal', icon: '⚖️' },
  { id: 'education', label: 'Education', icon: '🎓' },
  { id: 'customer_support', label: 'Customer Support', icon: '🤝' },
  { id: 'hr', label: 'HR', icon: '👥' },
  { id: 'sales', label: 'Sales', icon: '📊' },
  { id: 'real_estate', label: 'Real Estate', icon: '🏠' },
  { id: 'insurance', label: 'Insurance', icon: '🛡️' },
  { id: 'accounting', label: 'Accounting', icon: '🧮' },
  { id: 'research', label: 'Research', icon: '🔬' },
  { id: 'government', label: 'Government', icon: '🏛️' },
  { id: 'retail', label: 'Retail', icon: '🛒' },
  { id: 'manufacturing', label: 'Manufacturing', icon: '🏭' },
  { id: 'logistics', label: 'Logistics', icon: '🚚' },
  { id: 'technology', label: 'Technology', icon: '💻' },
]

export function IndustryFilter() {
  const { wizards, selectedCategory, selectedIndustries, toggleIndustry } = useWizardStore()
  const [showAll, setShowAll] = useState(false)

  if (selectedCategory !== 'domain') return null

  // Only show industries that have wizards + include counts
  const availableIndustries = useMemo(() => {
    const industryCounts = new Map<string, number>()

    // Count wizards per industry
    wizards
      .filter((w) => w.category === 'domain' && w.industry)
      .forEach((w) => {
        const count = industryCounts.get(w.industry!) || 0
        industryCounts.set(w.industry!, count + 1)
      })

    // Return only industries with wizards, sorted by count
    return allIndustries
      .filter((ind) => industryCounts.get(ind.id)! > 0)
      .map((ind) => ({
        ...ind,
        count: industryCounts.get(ind.id)!,
      }))
      .sort((a, b) => b.count - a.count) // Most wizards first
  }, [wizards])

  const visibleIndustries = showAll ? availableIndustries : availableIndustries.slice(0, 8)

  if (availableIndustries.length === 0) return null

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-2">
        Industry ({availableIndustries.length} available):
      </h3>
      <div className="flex flex-wrap gap-2">
        {visibleIndustries.map((industry) => (
          <button
            key={industry.id}
            onClick={() => toggleIndustry(industry.id)}
            className={`
              px-3 py-1.5 rounded-full text-sm font-medium transition-colors
              ${
                selectedIndustries.includes(industry.id)
                  ? 'bg-primary-100 text-primary-700 border-2 border-primary-500'
                  : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-gray-400'
              }
            `}
          >
            <span className="mr-1">{industry.icon}</span>
            {industry.label}
            <span className="ml-1.5 text-xs opacity-75">({industry.count})</span>
          </button>
        ))}

        {availableIndustries.length > 8 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-3 py-1.5 text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            {showAll ? 'Show Less' : `+${availableIndustries.length - 8} more`}
          </button>
        )}
      </div>
    </div>
  )
}
