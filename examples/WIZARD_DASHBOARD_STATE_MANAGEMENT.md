# Wizard Dashboard - State Management & Implementation Plan

**Technology Stack & Design Decisions**

Version: 1.0
Date: 2025-11-25
Status: Ready for Development

---

## ✅ State Management: Zustand (Recommended)

### Why Zustand?

**YES, use Zustand by default.** Here's why it's perfect for this use case:

#### Advantages for Wizard Dashboard

```typescript
// 1. SIMPLE - No boilerplate like Redux
import create from 'zustand'

const useWizardStore = create((set) => ({
  // State
  selectedCategory: 'all',
  selectedIndustries: [],
  selectedCompliance: [],
  searchQuery: '',
  wizards: [],

  // Actions
  setCategory: (category) => set({ selectedCategory: category }),
  toggleIndustry: (industry) => set((state) => ({
    selectedIndustries: state.selectedIndustries.includes(industry)
      ? state.selectedIndustries.filter(i => i !== industry)
      : [...state.selectedIndustries, industry]
  })),
  setSearchQuery: (query) => set({ searchQuery: query }),
}))

// 2. PERFORMANT - No unnecessary re-renders
function WizardGrid() {
  const wizards = useWizardStore((state) => state.wizards)
  // Only re-renders when wizards change
}

// 3. DEVTOOLS - Easy debugging
import { devtools } from 'zustand/middleware'

const useWizardStore = create(
  devtools((set) => ({
    // ... state
  }))
)
```

#### Comparison: Zustand vs Redux vs Context

| Feature | Zustand | Redux Toolkit | Context API |
|---------|---------|---------------|-------------|
| **Bundle Size** | 1.2kb | 11kb | Built-in |
| **Boilerplate** | Minimal | Low | Minimal |
| **Learning Curve** | Easy | Medium | Easy |
| **DevTools** | ✅ | ✅ | ❌ |
| **Middleware** | ✅ | ✅ | ❌ |
| **Performance** | Excellent | Good | Poor (for frequent updates) |
| **TypeScript** | ✅ | ✅ | ✅ |
| **Async Support** | Native | Redux Thunk | Manual |

**Verdict:** Zustand is the sweet spot - simple like Context, powerful like Redux, but lightweight.

---

## 🎯 Wireframe Selection Confirmed

### Primary Layout: Wireframe 2 (Compact Filter Bar)
✅ **Chosen:** Mobile-friendly, clean, progressive disclosure

### Detail Page: Wireframe 3
✅ **Chosen:** Comprehensive wizard information

### Filter Interaction: Pattern 2 (Smart Filtering)
✅ **Chosen:** Auto-suggest related filters, not forced progressive layers

---

## 🔄 Pattern 2: Smart Filtering Implementation

### How It Works

```
User Action: Clicks "Healthcare"
       ↓
System Response:
1. Filters to Healthcare wizard
2. SUGGESTS (doesn't auto-apply) related filters:
   ┌─────────────────────────────────────────┐
   │ 💡 SUGGESTED FILTERS                    │
   │ Based on "Healthcare":                  │
   │   [+ HIPAA] [+ SENSITIVE] [+ 90 days]  │
   │                                         │
   │ Related Industries:                     │
   │   [Research] [Insurance] [Education]    │
   └─────────────────────────────────────────┘

3. User can click suggested filters to apply
4. OR ignore and browse manually
```

### Code Example

```typescript
// Store with smart suggestions
const useWizardStore = create(devtools((set, get) => ({
  // State
  selectedCategory: 'all',
  selectedIndustries: [],
  selectedCompliance: [],
  suggestedFilters: [],

  // Smart filter logic
  setIndustry: (industry) => {
    set({ selectedIndustries: [industry] })

    // Generate smart suggestions
    const suggestions = getSmartSuggestions(industry)
    set({ suggestedFilters: suggestions })
  },

  applySuggestedFilter: (filter) => {
    const { type, value } = filter
    if (type === 'compliance') {
      set((state) => ({
        selectedCompliance: [...state.selectedCompliance, value],
        suggestedFilters: state.suggestedFilters.filter(f => f.value !== value)
      }))
    }
  },

  dismissSuggestions: () => set({ suggestedFilters: [] }),
})))

// Smart suggestion generator
function getSmartSuggestions(industry: string) {
  const suggestionMap = {
    'Healthcare': [
      { type: 'compliance', value: 'HIPAA', label: 'HIPAA §164.312' },
      { type: 'classification', value: 'SENSITIVE', label: 'SENSITIVE' },
      { type: 'retention', value: '90', label: '90-day retention' },
      { type: 'related_industry', value: 'Research', label: 'Research (IRB)' },
      { type: 'related_industry', value: 'Insurance', label: 'Insurance' },
    ],
    'Finance': [
      { type: 'compliance', value: 'SOX', label: 'SOX §802' },
      { type: 'compliance', value: 'PCI-DSS', label: 'PCI-DSS v4.0' },
      { type: 'classification', value: 'SENSITIVE', label: 'SENSITIVE' },
      { type: 'retention', value: '2555', label: '7-year retention' },
      { type: 'related_industry', value: 'Accounting', label: 'Accounting' },
    ],
    // ... more mappings
  }

  return suggestionMap[industry] || []
}
```

---

## ❓ Clarification Questions

### 🎯 PRIORITY 1: Core User Experience

#### 1. Smart Filter Behavior
When user selects "Healthcare" and suggestions appear:

**Option A: Highlighted Suggestions (Recommended)**
```
✓ User clicks "Healthcare"
✓ Sees Healthcare wizard immediately
✓ Suggestion bar appears: "💡 Add HIPAA | SENSITIVE | 90-day retention"
✓ User can click to add or ignore
```

**Option B: Recommended Section**
```
✓ User clicks "Healthcare"
✓ Sees Healthcare wizard + separate "Recommended" section
✓ Shows related wizards (Research, Insurance) as cards
```

**Question:** Which behavior do you prefer? (I recommend Option A)

---

#### 2. Initial View
When users first land on the dashboard:

**Option A: All Wizards with Popular Badge**
```
Shows all 44 wizards
Top 3 have "⭐ Popular" badge
Sorted by usage/popularity
```

**Option B: Featured Categories**
```
Shows 3 category cards:
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Domain/Industry │ │ Software Dev    │ │ AI Engineering  │
│ 16 wizards      │ │ 16 wizards      │ │ 12 wizards      │
└─────────────────┘ └─────────────────┘ └─────────────────┘

Click to explore category
```

**Option C: Smart Onboarding**
```
"What are you looking for?"
[ ] Industry-specific AI (Healthcare, Finance, etc.)
[ ] Software development tools
[ ] AI/ML engineering support

Filters to relevant category
```

**Question:** What should users see first?

---

#### 3. "Try Demo" Functionality
When user clicks "Try Demo" button:

**Option A: Inline Interactive Demo**
```
Card expands vertically
Shows interactive input/output demo
User can type queries and see responses
Expandable to full screen
```

**Option B: Navigate to Demo Page**
```
Full-page demo environment
More space for complex interactions
Back button returns to dashboard
URL: /wizards/healthcare/demo
```

**Option C: Modal/Drawer**
```
Overlay modal (80% screen width)
Interactive demo inside
"View Full Demo" → goes to dedicated page
```

**Question:** Which demo experience? (I recommend Option A for quick try, with "View Full Demo" → Option B)

---

### 🎯 PRIORITY 2: Technical Implementation

#### 4. URL Structure & Deep Linking
For sharing and bookmarking:

**Option A: Query Parameters**
```
/wizards?category=domain&industry=healthcare&compliance=hipaa

Pros: Flexible, all filters in URL
Cons: Long URLs
```

**Option B: Path-based**
```
/wizards/domain/healthcare
/wizards/ai-engineering

Pros: Clean URLs, SEO-friendly
Cons: Can't encode all filters
```

**Option C: Hybrid**
```
/wizards/healthcare?compliance=hipaa&level=3

Pros: Clean + flexible
Cons: More complex routing
```

**Question:** Preferred URL structure? (I recommend Option C)

---

#### 5. Filter Persistence
Should filters persist across:

**Browser Navigation:**
- ✅ Back/Forward buttons should restore filters
- Implementation: URL-based state (already handled)

**Browser Sessions:**
- ❓ Should filters save when user closes tab and returns?
- localStorage: `wizardFilters: { category: 'healthcare', ... }`
- Expires after: 7 days? 30 days? Never?

**User Accounts (if applicable):**
- ❓ Save favorite filters per user?
- "Save as preset" → "My HIPAA Setup"

**Question:** What should persist?

---

#### 6. Search Behavior
When user types in search box:

**Scope:**
- ❓ Search wizard name only?
- ❓ Search name + description + tags?
- ❓ Search compliance badges + capabilities?

**Timing:**
- ❓ Instant (as-you-type) results?
- ❓ Debounced (wait 300ms after typing stops)?
- ❓ Manual (press Enter or click Search)?

**Display:**
- ❓ Filter existing grid?
- ❓ Show dedicated search results page?
- ❓ Highlight matching text?

**Question:** Search behavior preferences? (I recommend: All fields, debounced 300ms, filter grid + highlight)

---

### 🎯 PRIORITY 3: Enhanced Features

#### 7. Wizard Combinations
Some users may need multiple wizards:

**Option A: Multi-Select Mode**
```
[Toggle: Compare Mode]
Check boxes appear on wizard cards
Select 2-3 wizards → "Compare" button
Side-by-side comparison view
```

**Option B: Wizard Bundles**
```
Pre-configured bundles:
"Healthcare Stack" → Healthcare + Research + Insurance
"FinTech Stack" → Finance + Accounting + Legal
"Dev Tools" → Debugging + Testing + Performance
```

**Option C: No Multi-Select**
```
Keep it simple - one wizard at a time
Related wizards shown on detail page
```

**Question:** Should we support multi-select/bundles? (Recommend start with Option C, add bundles later)

---

#### 8. Mobile Experience (Wireframe 2)
For mobile devices, filter bar should:

**Option A: Bottom Sheet**
```
Filter icon in top bar
Tapping opens bottom sheet (slides up)
Filters inside sheet
Swipe down to close
```

**Option B: Full-Screen Modal**
```
Filter icon → full screen modal
All filters visible
"Apply Filters" button
```

**Option C: Expandable Accordion**
```
Compact filter bar stays on top
Each filter type expands accordion-style
Inline filtering
```

**Question:** Mobile filter UI? (I recommend Option A - Bottom Sheet)

---

#### 9. Results Display
When filters are applied:

**Empty State:**
```
No wizards match your filters.
[Clear Filters] [Adjust Filters]

Or try these similar wizards: [Healthcare] [Research]
```

**Sorting Options:**
- Popularity (most used)
- Alphabetical
- Newest first
- Empathy level (3 → 5)
- Retention period (shortest → longest)

**Question:** Default sort order? (I recommend Popularity)

---

#### 10. Analytics & Tracking
What should we track?

**Suggested Events:**
```typescript
// User interactions
trackEvent('filter_applied', {
  filterType: 'industry',
  value: 'healthcare'
})

trackEvent('wizard_card_clicked', {
  wizardId: 'healthcare',
  source: 'grid'
})

trackEvent('demo_launched', {
  wizardId: 'healthcare'
})

trackEvent('suggestion_applied', {
  industry: 'healthcare',
  suggestion: 'HIPAA'
})

// Failed searches (important for UX improvements)
trackEvent('search_no_results', {
  query: 'medical records',
  filtersActive: ['healthcare']
})
```

**Question:** Any specific metrics you want to track?

---

## 🏗️ Proposed Tech Stack (Updated)

### Frontend
```json
{
  "react": "^18.2.0",
  "typescript": "^5.0.0",
  "zustand": "^4.4.0",
  "react-router-dom": "^6.20.0",
  "tailwindcss": "^3.3.0",
  "@headlessui/react": "^1.7.0",  // Accessible UI components
  "framer-motion": "^10.16.0",    // Smooth animations
  "meilisearch": "^0.35.0"        // Fast search
}
```

### State Management Architecture

```typescript
// stores/wizardStore.ts
import create from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface WizardFilters {
  category: 'all' | 'domain' | 'software' | 'ai'
  industries: string[]
  compliance: string[]
  empathyLevels: number[]
  useCases: string[]
  classification: string[]
  searchQuery: string
}

interface WizardState {
  // Data
  wizards: Wizard[]
  filteredWizards: Wizard[]

  // Filters
  filters: WizardFilters
  suggestedFilters: SuggestedFilter[]

  // UI State
  isLoading: boolean
  viewMode: 'grid' | 'list'
  sortBy: 'popularity' | 'alphabetical' | 'newest'

  // Actions
  setCategory: (category: string) => void
  toggleIndustry: (industry: string) => void
  toggleCompliance: (compliance: string) => void
  setSearchQuery: (query: string) => void
  applySuggestedFilter: (filter: SuggestedFilter) => void
  clearFilters: () => void

  // Computed
  getFilteredWizards: () => Wizard[]
  getSuggestions: (industry: string) => SuggestedFilter[]
}

const useWizardStore = create<WizardState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        wizards: [],
        filteredWizards: [],
        filters: {
          category: 'all',
          industries: [],
          compliance: [],
          empathyLevels: [],
          useCases: [],
          classification: [],
          searchQuery: '',
        },
        suggestedFilters: [],
        isLoading: false,
        viewMode: 'grid',
        sortBy: 'popularity',

        // Actions
        setCategory: (category) => {
          set({ filters: { ...get().filters, category } })
          // Trigger filter update
          get().getFilteredWizards()
        },

        toggleIndustry: (industry) => {
          const industries = get().filters.industries
          const newIndustries = industries.includes(industry)
            ? industries.filter(i => i !== industry)
            : [...industries, industry]

          set({ filters: { ...get().filters, industries: newIndustries } })

          // Generate smart suggestions
          if (newIndustries.length === 1) {
            const suggestions = get().getSuggestions(newIndustries[0])
            set({ suggestedFilters: suggestions })
          }

          // Trigger filter update
          get().getFilteredWizards()
        },

        // ... more actions

        // Computed/derived state
        getFilteredWizards: () => {
          const { wizards, filters } = get()
          let filtered = wizards

          // Apply category filter
          if (filters.category !== 'all') {
            filtered = filtered.filter(w => w.category === filters.category)
          }

          // Apply industry filter
          if (filters.industries.length > 0) {
            filtered = filtered.filter(w =>
              filters.industries.includes(w.industry)
            )
          }

          // Apply search
          if (filters.searchQuery) {
            const query = filters.searchQuery.toLowerCase()
            filtered = filtered.filter(w =>
              w.name.toLowerCase().includes(query) ||
              w.description.toLowerCase().includes(query) ||
              w.tags.some(tag => tag.toLowerCase().includes(query))
            )
          }

          set({ filteredWizards: filtered })
          return filtered
        },

        getSuggestions: (industry) => {
          // Smart suggestion logic
          return smartSuggestions[industry] || []
        },
      }),
      {
        name: 'wizard-filters',
        partialize: (state) => ({
          filters: state.filters,
          viewMode: state.viewMode,
          sortBy: state.sortBy,
        }),
      }
    )
  )
)
```

### Component Structure

```
src/
├── components/
│   ├── WizardDashboard.tsx          # Main container
│   ├── FilterBar/
│   │   ├── FilterBar.tsx            # Wireframe 2 compact bar
│   │   ├── CategoryFilter.tsx
│   │   ├── IndustryFilter.tsx
│   │   ├── ComplianceFilter.tsx
│   │   └── SuggestedFilters.tsx     # Smart suggestions
│   ├── WizardGrid/
│   │   ├── WizardGrid.tsx
│   │   ├── WizardCard.tsx
│   │   └── EmptyState.tsx
│   ├── WizardDetail/
│   │   ├── WizardDetail.tsx         # Wireframe 3
│   │   ├── ComplianceSection.tsx
│   │   ├── DemoSection.tsx
│   │   └── RelatedWizards.tsx
│   ├── Search/
│   │   ├── SearchBar.tsx
│   │   └── SearchResults.tsx
│   └── common/
│       ├── Badge.tsx
│       ├── EmpathyLevelIndicator.tsx
│       └── ClassificationBadge.tsx
├── stores/
│   └── wizardStore.ts               # Zustand store
├── hooks/
│   ├── useWizards.ts
│   ├── useFilters.ts
│   └── useSearch.ts
├── utils/
│   ├── smartSuggestions.ts
│   └── analytics.ts
└── types/
    └── wizard.ts
```

---

## 📋 Summary of Questions

### Must Answer (Priority 1):
1. **Smart Filter Behavior:** Option A (highlighted suggestions) or Option B (recommended section)?
2. **Initial View:** Show all wizards, category cards, or onboarding prompt?
3. **Try Demo:** Inline expandable, navigate to page, or modal?

### Should Answer (Priority 2):
4. **URL Structure:** Query params, path-based, or hybrid?
5. **Filter Persistence:** What should persist across sessions?
6. **Search Behavior:** Scope, timing, and display preferences?

### Nice to Have (Priority 3):
7. **Wizard Combinations:** Support multi-select/bundles?
8. **Mobile Filters:** Bottom sheet, full-screen, or accordion?
9. **Default Sort:** Popularity, alphabetical, or newest?
10. **Analytics:** Any specific events to track?

---

## ✅ Next Steps After Clarification

1. **Finalize wireframe details** based on answers
2. **Create high-fidelity Figma mockups**
3. **Set up project structure**
   ```bash
   npx create-react-app wizard-dashboard --template typescript
   npm install zustand react-router-dom tailwindcss
   ```
4. **Implement Zustand store** with confirmed behavior
5. **Build core components** (FilterBar, WizardGrid, WizardCard)
6. **Add smart filtering logic**
7. **Implement search** (MeiliSearch integration)
8. **Add analytics tracking**
9. **Mobile responsive testing**
10. **Deploy MVP**

---

**Ready to proceed once you answer the clarification questions!**

**Recommendation:** Start with Priority 1 questions to unlock development. Priority 2/3 can be decided during implementation.
