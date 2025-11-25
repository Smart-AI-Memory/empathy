import { Fragment, useMemo } from 'react'
import { Dialog, Transition } from '@headlessui/react'
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

export function MobileFilterSheet() {
  const {
    wizards,
    isFilterSheetOpen,
    closeFilterSheet,
    selectedIndustries,
    toggleIndustry,
    clearFilters,
  } = useWizardStore()

  // Only show industries that have wizards
  const availableIndustries = useMemo(() => {
    const industryCounts = new Map<string, number>()

    wizards
      .filter((w) => w.category === 'domain' && w.industry)
      .forEach((w) => {
        const count = industryCounts.get(w.industry!) || 0
        industryCounts.set(w.industry!, count + 1)
      })

    return allIndustries
      .filter((ind) => industryCounts.get(ind.id)! > 0)
      .map((ind) => ({
        ...ind,
        count: industryCounts.get(ind.id)!,
      }))
      .sort((a, b) => b.count - a.count)
  }, [wizards])

  return (
    <Transition.Root show={isFilterSheetOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={closeFilterSheet}>
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
                    <div className="flex justify-center pt-3 pb-2">
                      <div className="w-12 h-1 bg-gray-300 rounded-full" />
                    </div>

                    <div className="border-b px-6 py-4">
                      <Dialog.Title className="text-lg font-semibold">
                        Filters
                      </Dialog.Title>
                    </div>

                    <div className="flex-1 px-6 py-4 space-y-6">
                      {availableIndustries.length > 0 && (
                        <div>
                          <h3 className="font-medium mb-3">
                            Industry ({availableIndustries.length})
                          </h3>
                          <div className="space-y-2">
                            {availableIndustries.map((industry) => (
                              <label
                                key={industry.id}
                                className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50"
                              >
                                <input
                                  type="checkbox"
                                  checked={selectedIndustries.includes(industry.id)}
                                  onChange={() => toggleIndustry(industry.id)}
                                  className="w-5 h-5 text-primary-600 rounded"
                                />
                                <span className="text-2xl">{industry.icon}</span>
                                <span className="flex-1">{industry.label}</span>
                                <span className="text-sm text-gray-500">({industry.count})</span>
                              </label>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="border-t px-6 py-4 bg-gray-50">
                      <div className="flex gap-3">
                        <button
                          onClick={() => {
                            clearFilters()
                            closeFilterSheet()
                          }}
                          className="flex-1 px-4 py-3 bg-white border-2 border-gray-300 rounded-lg font-medium"
                        >
                          Clear All
                        </button>
                        <button
                          onClick={closeFilterSheet}
                          className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-lg font-medium"
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
