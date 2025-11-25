import { useState, useEffect } from 'react'
import { useWizardStore } from '../stores/wizardStore'
import { FilterBar } from './FilterBar/FilterBar'
import { MobileFilterSheet } from './FilterBar/MobileFilterSheet'
import { WizardGrid } from './WizardGrid/WizardGrid'
import { SearchBar } from './Search/SearchBar'
import { FAQPage } from './FAQPage'

export function WizardDashboard() {
  const [isMobile, setIsMobile] = useState(false)
  const [showFAQ, setShowFAQ] = useState(false)
  const { filteredWizards, openFilterSheet, getActiveFilterCount } = useWizardStore()
  const activeFilters = getActiveFilterCount()

  useEffect(() => {
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
              <h1 className="ml-2 text-lg font-bold md:hidden">Empathy</h1>
            </div>

            {/* Desktop Search */}
            <div className="hidden md:block flex-1 max-w-lg mx-8">
              <SearchBar />
            </div>

            {/* Desktop Actions */}
            <div className="hidden md:flex items-center gap-3">
              <button
                onClick={() => setShowFAQ(true)}
                className="px-4 py-2 text-gray-700 hover:text-primary-600 font-medium text-sm flex items-center gap-2"
                title="Frequently Asked Questions"
              >
                <span>❓</span>
                <span>FAQ</span>
              </button>
            </div>

            {/* Mobile Actions */}
            {isMobile && (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowFAQ(true)}
                  className="px-3 py-2 text-gray-700 hover:text-primary-600 text-xl"
                  title="FAQ"
                  aria-label="Open FAQ"
                >
                  ❓
                </button>
                <button
                  onClick={openFilterSheet}
                  className="relative px-4 py-2 bg-gray-100 rounded-lg font-medium text-sm"
                >
                  Filter
                  {activeFilters > 0 && (
                    <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                      {activeFilters}
                    </span>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Mobile Search */}
          {isMobile && (
            <div className="pb-4">
              <SearchBar />
            </div>
          )}
        </div>
      </header>

      {/* Desktop Filter Bar */}
      {!isMobile && (
        <div className="bg-white border-b sticky top-16 z-30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <FilterBar />
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <WizardGrid wizards={filteredWizards} isMobile={isMobile} />
      </main>

      {/* Mobile Bottom Sheet */}
      {isMobile && <MobileFilterSheet />}

      {/* FAQ Modal */}
      {showFAQ && <FAQPage onClose={() => setShowFAQ(false)} />}
    </div>
  )
}
