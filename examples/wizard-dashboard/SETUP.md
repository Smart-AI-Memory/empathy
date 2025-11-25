# Wizard Dashboard Setup Guide

Complete setup instructions for the Empathy Wizard Dashboard.

## Installation

### 1. Install Dependencies

```bash
cd examples/wizard-dashboard
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 3. (Optional) Start Backend API

```bash
cd ../../backend/api
pip install -r requirements.txt
python wizards.py
```

API available at [http://localhost:8000](http://localhost:8000)

## What Was Built

✅ **React + TypeScript** project structure
✅ **Zustand** state management with smart filtering
✅ **Tailwind CSS** responsive design
✅ **Framer Motion** smooth animations
✅ **Headless UI** accessible components
✅ **Desktop** full filter bar (Wireframe 2)
✅ **Mobile** bottom sheet filters
✅ **Search** with 300ms debouncing
✅ **Smart Suggestions** (Pattern 2)
✅ **Wizard Cards** with inline demos
✅ **Backend API** (FastAPI)

## Project Structure

```
wizard-dashboard/
├── src/
│   ├── components/
│   │   ├── FilterBar/
│   │   │   ├── CategoryFilter.tsx
│   │   │   ├── IndustryFilter.tsx
│   │   │   ├── SuggestedFilters.tsx
│   │   │   ├── FilterBar.tsx
│   │   │   └── MobileFilterSheet.tsx
│   │   ├── WizardGrid/
│   │   │   ├── WizardCard.tsx
│   │   │   └── WizardGrid.tsx
│   │   ├── Search/
│   │   │   └── SearchBar.tsx
│   │   ├── common/
│   │   │   ├── ComplianceBadge.tsx
│   │   │   ├── ClassificationBadge.tsx
│   │   │   └── EmpathyLevelIndicator.tsx
│   │   └── WizardDashboard.tsx
│   ├── stores/
│   │   └── wizardStore.ts (Zustand)
│   ├── types/
│   │   └── wizard.ts
│   ├── data/
│   │   └── wizards.ts (10 sample wizards)
│   ├── utils/
│   │   └── smartSuggestions.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

## Features

### Smart Filtering (Pattern 2)
- Select "Healthcare" → Suggests HIPAA, SENSITIVE, Related industries
- No forced progressive layers
- User can apply or ignore suggestions

### Responsive Design
- **Desktop (>768px):** Full horizontal filter bar, 2-4 column grid
- **Mobile (<768px):** Compact with bottom sheet, single column

### Search
- Real-time with 300ms debouncing
- Searches: name, description, tags, compliance, features

### State Management
- Zustand for lightweight state
- Filter persistence in localStorage
- URL-based deep linking (ready)

## Next Steps

### Add More Wizards
Edit `src/data/wizards.ts` to add all 44 wizards

### Connect to Real API
Update `src/App.tsx`:
```typescript
useEffect(() => {
  fetch('/api/wizards')
    .then(res => res.json())
    .then(data => setWizards(data.wizards))
}, [])
```

### Deploy
```bash
npm run build
# Deploy dist/ to Vercel/Netlify/etc.
```

## Commands

```bash
npm run dev          # Start dev server
npm run build        # Production build
npm run preview      # Preview build
npm run lint         # Lint code
npm run type-check   # Check TypeScript
```

## Tech Stack

- React 18.2 + TypeScript 5.2
- Zustand 4.4 (state)
- Tailwind CSS 3.3 (styling)
- Framer Motion 10.16 (animations)
- Headless UI 1.7 (components)
- Vite 5.0 (build tool)
- FastAPI (backend)

---

**Ready to use!** 🚀

Run `npm run dev` and visit http://localhost:3000
