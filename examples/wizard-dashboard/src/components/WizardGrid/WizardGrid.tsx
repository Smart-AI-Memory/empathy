import { motion, AnimatePresence } from 'framer-motion'
import { Wizard } from '../../types/wizard'
import { WizardCard } from './WizardCard'
import { useWizardStore } from '../../stores/wizardStore'

interface WizardGridProps {
  wizards: Wizard[]
  isMobile?: boolean
}

export function WizardGrid({ wizards, isMobile }: WizardGridProps) {
  const { sortBy, setSortBy } = useWizardStore()

  if (wizards.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          No wizards found
        </h3>
        <p className="text-gray-600 mb-6">
          Try adjusting your filters or search query
        </p>
        <button
          onClick={() => useWizardStore.getState().clearFilters()}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700"
        >
          Clear All Filters
        </button>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">
          Showing {wizards.length} wizard{wizards.length !== 1 ? 's' : ''}
        </h2>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) =>
            setSortBy(e.target.value as 'popularity' | 'alphabetical' | 'newest')
          }
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="popularity">Most Popular</option>
          <option value="alphabetical">A-Z</option>
          <option value="newest">Newest First</option>
        </select>
      </div>

      {/* Grid */}
      <motion.div
        layout
        className={`
          grid gap-6
          grid-cols-1
          ${isMobile ? '' : 'md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'}
        `}
      >
        <AnimatePresence mode="popLayout">
          {wizards.map((wizard) => (
            <WizardCard key={wizard.id} wizard={wizard} isMobile={isMobile} />
          ))}
        </AnimatePresence>
      </motion.div>
    </div>
  )
}
