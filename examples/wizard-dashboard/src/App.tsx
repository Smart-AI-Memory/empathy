import { useEffect } from 'react'
import { WizardDashboard } from './components/WizardDashboard'
import { useWizardStore } from './stores/wizardStore'
import { wizardsData } from './data/wizards'

function App() {
  const setWizards = useWizardStore((state) => state.setWizards)

  useEffect(() => {
    // Load wizards on mount
    // In production, this would fetch from API
    setWizards(wizardsData)
  }, [setWizards])

  return <WizardDashboard />
}

export default App
