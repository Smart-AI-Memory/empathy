import Link from 'next/link';

export default function PluginsPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <nav className="border-b border-[var(--border)] py-4">
        <div className="container flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gradient">
            Empathy
          </Link>
          <div className="flex gap-6">
            <Link href="/framework" className="text-sm hover:text-[var(--primary)]">Framework</Link>
            <Link href="/book" className="text-sm hover:text-[var(--primary)]">Book</Link>
            <Link href="/docs" className="text-sm hover:text-[var(--primary)]">Docs</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-20 gradient-primary text-white">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              Commercial Plugins
            </h1>
            <p className="text-2xl mb-8 opacity-90">
              Production-ready Level 4 Anticipatory AI for Software Development and Healthcare
            </p>
            <Link href="/book" className="btn bg-white text-[var(--primary)] hover:bg-gray-100">
              Get Access - $49
            </Link>
          </div>
        </div>
      </section>

      {/* Software Development Plugin */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <div className="text-6xl mb-4">💻</div>
              <h2 className="text-4xl font-bold mb-4">Software Development Plugin</h2>
              <p className="text-xl text-[var(--text-secondary)]">
                Transform how you build software with anticipatory intelligence
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 mb-12">
              <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">Enhanced Testing Wizard</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  Goes beyond code coverage to predict which untested code will cause bugs.
                </p>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Test quality analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Bug-risk prediction</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Brittle test detection</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Smart test suggestions</span>
                  </li>
                </ul>
              </div>

              <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">Performance Profiling Wizard</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  Predicts performance degradation before it becomes critical.
                </p>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Trajectory analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Bottleneck prediction</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>N+1 query detection</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Performance forecasting</span>
                  </li>
                </ul>
              </div>

              <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">Security Analysis Wizard</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  Identifies which vulnerabilities will actually be exploited.
                </p>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>OWASP pattern detection</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Exploit likelihood scoring</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Attack surface analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Prioritized remediation</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="bg-[var(--primary)] bg-opacity-10 border-l-4 border-[var(--primary)] p-6 rounded-r-lg">
              <h3 className="text-xl font-bold mb-2">20+ Total Wizards</h3>
              <p className="text-[var(--text-secondary)]">
                The Software Development Plugin includes over 20 specialized wizards in total. The book provides
                deep dives into 3 core wizards, while 17+ additional wizards are available via the GitHub repository—covering
                debugging, code review, deployment analysis, refactoring suggestions, and more.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Healthcare Plugin */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <div className="text-6xl mb-4">🏥</div>
              <h2 className="text-4xl font-bold mb-4">Healthcare Plugin</h2>
              <p className="text-xl text-[var(--text-secondary)]">
                Anticipatory intelligence for patient care and clinical decision support
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 mb-12">
              <div className="bg-[var(--background)] p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">Patient Trajectory Wizard</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  Predicts patient deterioration before clinical crisis occurs.
                </p>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Vital sign trend analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Early warning scores</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Deterioration prediction</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Intervention recommendations</span>
                  </li>
                </ul>
              </div>

              <div className="bg-[var(--background)] p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">Treatment Optimization Wizard</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  Anticipates medication interactions and treatment complications.
                </p>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Drug interaction prediction</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Adverse event forecasting</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Dosage optimization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Treatment trajectory analysis</span>
                  </li>
                </ul>
              </div>

              <div className="bg-[var(--background)] p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">Risk Assessment Wizard</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  Identifies high-risk patients proactively for early intervention.
                </p>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Multi-factor risk scoring</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Readmission prediction</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Complication forecasting</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Resource allocation guidance</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="bg-[var(--secondary)] bg-opacity-10 border-l-4 border-[var(--secondary)] p-6 rounded-r-lg">
              <h3 className="text-xl font-bold mb-2">Clinical Grade Predictions</h3>
              <p className="text-[var(--text-secondary)]">
                The Healthcare Plugin is designed for clinical decision support, built with medical
                professionals and validated against real-world patient data.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Licensing */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Licensing</h2>

            <div className="space-y-6">
              <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">What&apos;s Included</h3>
                <ul className="space-y-2 text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Both Software Development and Healthcare plugins</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>1 developer license (per book purchase)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Perpetual license for purchased version</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Free minor updates (bug fixes, improvements)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span>Technical validation system (license key required)</span>
                  </li>
                </ul>
              </div>

              <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-3">Team Licensing</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  Need licenses for your team? Each additional book purchase includes another developer license.
                </p>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span>•</span>
                    <span>1 developer: $49 (1 book)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span>
                    <span>5 developers: $245 (5 books)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span>
                    <span>10 developers: $490 (10 books)</span>
                  </li>
                </ul>
              </div>

              <div className="bg-[var(--accent)] bg-opacity-10 border-l-4 border-[var(--accent)] p-6 rounded-r-lg">
                <h3 className="text-xl font-bold mb-2">Major Version Updates</h3>
                <p className="text-[var(--text-secondary)]">
                  Major version releases (2.0, 3.0, etc.) are sold separately. Your license covers
                  the version you purchased plus all minor updates (1.1, 1.2, etc.).
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 gradient-primary text-white">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">
              Get Both Plugins with the Book
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Learn the theory, see the implementation, and get production-ready plugins
              for just $49.
            </p>
            <Link href="/book" className="btn bg-white text-[var(--primary)] hover:bg-gray-100 text-lg px-8 py-4">
              Purchase Early Access
            </Link>
            <p className="mt-6 text-sm opacity-75">
              Includes: Book (digital) + 1 Developer License + Both Plugins
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white border-opacity-20">
        <div className="container">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 text-white">
            <div className="text-sm opacity-75">
              © 2025 Deep Study AI, LLC. All rights reserved.
            </div>
            <div className="flex gap-6">
              <Link href="/" className="text-sm opacity-75 hover:opacity-100">
                Home
              </Link>
              <Link href="/framework" className="text-sm opacity-75 hover:opacity-100">
                Framework
              </Link>
              <Link href="/book" className="text-sm opacity-75 hover:opacity-100">
                Book
              </Link>
              <Link href="/docs" className="text-sm opacity-75 hover:opacity-100">
                Docs
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
