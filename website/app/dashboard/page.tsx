import Link from 'next/link';
import WizardPlayground from '@/components/WizardPlayground';

export default function MedicalDashboard() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <nav className="border-b border-[var(--border)] py-4 bg-[var(--background)]">
        <div className="container flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gradient">
            Smart AI Memory
          </Link>
          <div className="flex gap-6 items-center">
            <Link href="/" className="text-sm hover:text-[var(--primary)]">Home</Link>
            <Link href="/framework" className="text-sm hover:text-[var(--primary)]">Framework</Link>
            <Link href="/dev-dashboard" className="text-sm hover:text-[var(--primary)]">Dev Dashboard</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-12 bg-gradient-to-b from-[var(--border)] to-transparent">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-6xl mb-6">🏥</div>
            <h1 className="text-4xl font-bold mb-4">
              Medical Wizards <span className="text-gradient">Dashboard</span>
            </h1>
            <p className="text-xl text-[var(--text-secondary)] mb-6">
              Level 4 Anticipatory Intelligence for Clinical Wizards
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              <span className="px-3 py-1 bg-[var(--primary)] text-white rounded-full text-sm font-semibold">
                Claude Code
              </span>
              <span className="px-3 py-1 bg-[var(--accent)] text-white rounded-full text-sm font-semibold">
                Empathy Framework
              </span>
              <span className="px-3 py-1 bg-[var(--secondary)] text-white rounded-full text-sm font-semibold">
                MemDocs
              </span>
              <span className="px-3 py-1 bg-[var(--muted)] text-white rounded-full text-sm font-semibold">
                VS Code
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Overview */}
      <section className="py-12">
        <div className="container">
          <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <div className="bg-[var(--background)] border-2 border-[var(--border)] p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-[var(--primary)] mb-2">14+</div>
              <div className="text-sm text-[var(--text-secondary)]">Clinical Monitors</div>
            </div>
            <div className="bg-[var(--background)] border-2 border-[var(--border)] p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-[var(--success)] mb-2">Level 4</div>
              <div className="text-sm text-[var(--text-secondary)]">Anticipatory AI</div>
            </div>
            <div className="bg-[var(--background)] border-2 border-[var(--border)] p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-[var(--accent)] mb-2">Real-time</div>
              <div className="text-sm text-[var(--text-secondary)]">Patient Monitoring</div>
            </div>
            <div className="bg-[var(--background)] border-2 border-[var(--border)] p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-[var(--secondary)] mb-2">Predictive</div>
              <div className="text-sm text-[var(--text-secondary)]">Risk Assessment</div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Wizard Playground */}
      <section className="py-12 bg-[var(--border)] bg-opacity-20">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-4">Try Healthcare Wizards</h2>
          <p className="text-center text-[var(--text-secondary)] mb-12 max-w-3xl mx-auto">
            Select a wizard below and provide patient data or clinical information to see
            Level 4 Anticipatory Intelligence in action.
          </p>
          <WizardPlayground category="healthcare" />
        </div>
      </section>

      {/* Clinical Monitoring Features */}
      <section className="py-12">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">Clinical Monitoring Capabilities</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {/* Patient Trajectory Analysis */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">📊</div>
                <h3 className="text-lg font-bold">Patient Trajectory Analysis</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Predicts patient trajectory based on vital signs, lab results, and historical patterns.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Multi-parameter trend analysis</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Early deterioration warnings</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Automated risk scoring</span>
                </div>
              </div>
            </div>

            {/* Protocol Compliance Monitor */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">📋</div>
                <h3 className="text-lg font-bold">Protocol Compliance Monitor</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Ensures adherence to clinical protocols and best practices in real-time.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Real-time protocol checking</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Deviation alerts</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Best practice recommendations</span>
                </div>
              </div>
            </div>

            {/* Vital Signs Monitoring */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">💓</div>
                <h3 className="text-lg font-bold">Vital Signs Monitoring</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Continuous monitoring with predictive alerts before critical events occur.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Pattern recognition</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Predictive alerting</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Multi-parameter correlation</span>
                </div>
              </div>
            </div>

            {/* Medication Safety */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">💊</div>
                <h3 className="text-lg font-bold">Medication Safety</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Identifies potential drug interactions and contraindications before administration.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Drug interaction checking</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Allergy alerts</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Dosage recommendations</span>
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">⚠️</div>
                <h3 className="text-lg font-bold">Risk Assessment</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Predictive risk scoring for complications, readmissions, and adverse events.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Multi-factor risk modeling</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Readmission prediction</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Complication forecasting</span>
                </div>
              </div>
            </div>

            {/* Lab Results Analyzer */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🔬</div>
                <h3 className="text-lg font-bold">Lab Results Analyzer</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Automated interpretation of lab results with trend analysis and clinical insights.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Automated interpretation</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Historical trend analysis</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Critical value alerting</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-12">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">How Level 4 Anticipatory Intelligence Works</h2>

          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex gap-6 items-start">
              <div className="flex-shrink-0 w-12 h-12 bg-[var(--primary)] bg-opacity-10 rounded-full flex items-center justify-center text-[var(--primary)] font-bold text-xl">
                1
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Continuous Monitoring</h3>
                <p className="text-[var(--text-secondary)]">
                  Empathy Framework monitors patient data streams in real-time, tracking vital signs,
                  lab results, medications, and clinical notes continuously.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="flex-shrink-0 w-12 h-12 bg-[var(--primary)] bg-opacity-10 rounded-full flex items-center justify-center text-[var(--primary)] font-bold text-xl">
                2
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Pattern Recognition</h3>
                <p className="text-[var(--text-secondary)]">
                  AI wizards identify patterns and trajectories that indicate potential issues before
                  they become critical, using historical data and clinical protocols.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="flex-shrink-0 w-12 h-12 bg-[var(--primary)] bg-opacity-10 rounded-full flex items-center justify-center text-[var(--primary)] font-bold text-xl">
                3
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Predictive Alerts</h3>
                <p className="text-[var(--text-secondary)]">
                  The system generates anticipatory alerts with actionable recommendations,
                  enabling clinical teams to intervene before problems escalate.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="flex-shrink-0 w-12 h-12 bg-[var(--primary)] bg-opacity-10 rounded-full flex items-center justify-center text-[var(--primary)] font-bold text-xl">
                4
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Continuous Learning</h3>
                <p className="text-[var(--text-secondary)]">
                  MemDocs integration ensures the system learns from each case, improving predictions
                  and recommendations over time with project-specific memory.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-b from-transparent to-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-6">
              Build Your Own Medical Wizards
            </h2>
            <p className="text-xl text-[var(--text-secondary)] mb-8">
              The Empathy Framework is Fair Source licensed and production-ready.
              Start building anticipatory AI for healthcare today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/framework" className="btn btn-primary">
                View Framework
              </Link>
              <a
                href="https://github.com/Smart-AI-Memory/empathy"
                className="btn btn-outline"
                target="_blank"
                rel="noopener noreferrer"
              >
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-[var(--border)]">
        <div className="container">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="text-sm text-[var(--muted)]">
              © 2025 Deep Study AI, LLC. All rights reserved.
            </div>
            <div className="flex gap-6">
              <Link href="/" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Home
              </Link>
              <Link href="/framework" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Framework
              </Link>
              <Link href="/dev-dashboard" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Dev Dashboard
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
