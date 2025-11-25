import { useWizardStore } from '../../stores/wizardStore'

export function CategoryFilter() {
  const { selectedCategory, setCategory, wizards } = useWizardStore()

  const categories = [
    {
      id: 'all' as const,
      label: 'All Wizards',
      count: wizards.length,
    },
    {
      id: 'domain' as const,
      label: 'Domain & Industry',
      count: wizards.filter((w) => w.category === 'domain').length,
    },
    {
      id: 'software' as const,
      label: 'Software Development',
      count: wizards.filter((w) => w.category === 'software').length,
    },
    {
      id: 'ai' as const,
      label: 'AI & Engineering',
      count: wizards.filter((w) => w.category === 'ai').length,
    },
  ]

  return (
    <div className="flex flex-wrap gap-2">
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => setCategory(cat.id)}
          className={`
            px-4 py-2 rounded-lg font-medium transition-colors text-sm md:text-base
            ${
              selectedCategory === cat.id
                ? 'bg-primary-600 text-white'
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
