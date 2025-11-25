import { useState, useEffect } from 'react'
import { useWizardStore } from '../../stores/wizardStore'

export function SearchBar() {
  const { setSearchQuery, searchQuery } = useWizardStore()
  const [localQuery, setLocalQuery] = useState(searchQuery)

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchQuery(localQuery)
    }, 300)

    return () => clearTimeout(timer)
  }, [localQuery, setSearchQuery])

  return (
    <div className="relative">
      <input
        type="text"
        value={localQuery}
        onChange={(e) => setLocalQuery(e.target.value)}
        placeholder="Search wizards..."
        className="
          w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
          text-sm
        "
      />
      <svg
        className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      {localQuery && (
        <button
          onClick={() => setLocalQuery('')}
          className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      )}
    </div>
  )
}
