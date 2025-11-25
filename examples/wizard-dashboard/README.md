# Empathy Wizard Dashboard

Interactive dashboard for exploring 44+ AI wizards with built-in security & compliance.

## Features

- **44+ AI Wizards** across 3 categories
- **Smart Filtering** with Pattern 2 (no forced progressive layers)
- **Responsive Design** - Desktop (full features) + Mobile (compact bottom sheet)
- **Real-time Search** with 300ms debouncing
- **Zustand State Management** - Lightweight & performant
- **Tailwind CSS** - Modern, responsive styling

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

## Project Structure

```
src/
├── components/
│   ├── FilterBar/           # Desktop & mobile filters
│   ├── WizardGrid/          # Card display
│   ├── Search/              # Search component
│   └── common/              # Badges, indicators
├── stores/
│   └── wizardStore.ts       # Zustand state management
├── types/
│   └── wizard.ts            # TypeScript types
├── data/
│   └── wizards.ts           # Wizard data
└── utils/
    └── smartSuggestions.ts  # Pattern 2 smart filtering
```

## Tech Stack

- **React 18** + **TypeScript**
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Headless UI** - Accessible components
- **Vite** - Build tool

## Features

### Desktop Experience
- Full filter bar with all options visible
- 2-4 column grid (responsive)
- Smart filter suggestions (Pattern 2)
- Inline expandable demos

### Mobile Experience
- Compact top bar
- Bottom sheet filters (swipe-to-dismiss)
- Single column grid
- Sticky category tabs

## Development

```bash
# Development
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## Backend API (Optional)

```bash
# Start Python FastAPI backend
cd ../..
python backend/api/wizards.py

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Deployment

```bash
# Build
npm run build

# Deploy dist/ folder to:
# - Vercel
# - Netlify
# - GitHub Pages
# - Any static hosting
```

## License

Fair Source 0.9
