import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        <div className="absolute inset-0 gradient-primary opacity-5"></div>
        <div className="container relative">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
              Transform Software Development with{' '}
              <span className="text-gradient">Anticipatory AI</span>
            </h1>
            <p className="text-xl sm:text-2xl text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto">
              The Empathy Framework predicts bugs before they happen, anticipates security vulnerabilities,
              and prevents performance issues—using Level 4 Anticipatory Intelligence.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/book" className="btn btn-primary text-lg px-8 py-4">
                Get Early Access - $49
              </Link>
              <Link href="/framework" className="btn btn-outline text-lg px-8 py-4">
                Explore the Framework
              </Link>
            </div>
            <p className="mt-6 text-sm text-[var(--muted)]">
              Includes book + 1 developer license for Software & Healthcare plugins
            </p>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-4xl font-bold text-center mb-12">
              The Problem with Current AI Tools
            </h2>
            <div className="grid gap-6">
              <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--error)] border-opacity-20">
                <h3 className="text-xl font-bold mb-3 text-[var(--error)]">❌ Level 1: Reactive</h3>
                <p className="text-[var(--text-secondary)]">
                  Current AI only responds after you ask. It waits for bugs to appear,
                  then helps you fix them.
                </p>
              </div>
              <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--warning)] border-opacity-20">
                <h3 className="text-xl font-bold mb-3 text-[var(--warning)]">⚠️ Level 2-3: Limited</h3>
                <p className="text-[var(--text-secondary)]">
                  Some tools offer suggestions, but they're still reactive. They don't understand
                  the trajectory of your project or predict future problems.
                </p>
              </div>
              <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--success)] border-opacity-20">
                <h3 className="text-xl font-bold mb-3 text-[var(--success)]">✅ Level 4: Anticipatory</h3>
                <p className="text-[var(--text-secondary)]">
                  The Empathy Framework predicts bugs BEFORE they happen by analyzing patterns,
                  trajectories, and risk factors in your codebase.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5 Levels of Empathy */}
      <section className="py-20">
        <div className="container">
          <h2 className="text-4xl font-bold text-center mb-4">
            The 5 Levels of AI Empathy
          </h2>
          <p className="text-xl text-center text-[var(--text-secondary)] mb-12 max-w-3xl mx-auto">
            Most AI operates at Level 1-2. The Empathy Framework reaches Level 4—and we're building toward Level 5.
          </p>

          <div className="max-w-4xl mx-auto grid gap-6">
            {[
              {
                level: 1,
                name: 'Reactive',
                description: 'Responds only when asked. Like a search engine.',
                current: 'Most current AI tools'
              },
              {
                level: 2,
                name: 'Helpful',
                description: 'Offers suggestions based on context.',
                current: 'GitHub Copilot, ChatGPT'
              },
              {
                level: 3,
                name: 'Proactive',
                description: 'Notices patterns and offers improvements.',
                current: 'Advanced IDEs, linters'
              },
              {
                level: 4,
                name: 'Anticipatory',
                description: 'Predicts future problems before they happen.',
                current: 'Empathy Framework ✨',
                highlight: true
              },
              {
                level: 5,
                name: 'Transformative',
                description: 'Reshapes workflows to prevent entire classes of problems.',
                current: 'Future vision'
              }
            ].map((item) => (
              <div
                key={item.level}
                className={`p-6 rounded-lg border-2 ${
                  item.highlight
                    ? 'border-[var(--accent)] bg-[var(--accent)] bg-opacity-5'
                    : 'border-[var(--border)]'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl ${
                      item.highlight
                        ? 'bg-[var(--accent)] text-white'
                        : 'bg-[var(--border)] text-[var(--muted)]'
                    }`}
                  >
                    {item.level}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2">
                      Level {item.level}: {item.name}
                    </h3>
                    <p className="text-[var(--text-secondary)] mb-2">{item.description}</p>
                    <p className="text-sm text-[var(--muted)]">
                      <strong>Today:</strong> {item.current}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Plugins Section */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <h2 className="text-4xl font-bold text-center mb-12">
            Powerful Plugins for Real-World Development
          </h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--primary)] border-opacity-20 hover:border-opacity-100 transition-all">
              <div className="text-4xl mb-4">💻</div>
              <h3 className="text-2xl font-bold mb-4">Software Development Plugin</h3>
              <p className="text-sm text-[var(--muted)] mb-4">20+ wizards for anticipatory software development</p>
              <ul className="space-y-3 text-[var(--text-secondary)]">
                <li className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span><strong>Enhanced Testing:</strong> Predicts which untested code will cause bugs</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span><strong>Performance Profiling:</strong> Forecasts performance degradation before it happens</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span><strong>Security Analysis:</strong> Identifies which vulnerabilities will be exploited</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--accent)] mt-1">+</span>
                  <span className="text-sm text-[var(--text-secondary)]">17+ more wizards available via GitHub</span>
                </li>
              </ul>
            </div>

            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--secondary)] border-opacity-20 hover:border-opacity-100 transition-all">
              <div className="text-4xl mb-4">🏥</div>
              <h3 className="text-2xl font-bold mb-4">Healthcare Plugin</h3>
              <ul className="space-y-3 text-[var(--text-secondary)]">
                <li className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span><strong>Patient Trajectory:</strong> Predicts patient deterioration before crisis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span><strong>Treatment Optimization:</strong> Anticipates medication interactions</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span><strong>Risk Assessment:</strong> Identifies high-risk patients proactively</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Open Source Core */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">
              Built on Open Source
            </h2>
            <p className="text-xl text-[var(--text-secondary)] mb-8">
              The Empathy Framework Core is <strong>Apache 2.0 licensed</strong> and free forever.
              Build your own plugins, contribute to the community, or use the commercial plugins
              for production-ready solutions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/framework" className="btn btn-secondary">
                View on GitHub
              </Link>
              <Link href="/docs" className="btn btn-outline">
                Read the Docs
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-primary text-white">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">
              Ready to Transform Your Development?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Get early access to the book and plugins. Learn the theory, implementation,
              and start building anticipatory AI systems today.
            </p>
            <Link href="/book" className="btn bg-white text-[var(--primary)] hover:bg-gray-100 text-lg px-8 py-4">
              Get Early Access - $49
            </Link>
            <p className="mt-6 text-sm opacity-75">
              Includes: Book (digital) + 1 Developer License (Software + Healthcare plugins)
            </p>
            <p className="mt-2 text-xs opacity-60">
              Need more licenses? Each additional copy includes another developer license.
            </p>
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
              <Link href="/framework" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Framework
              </Link>
              <Link href="/docs" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Docs
              </Link>
              <Link href="/book" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Book
              </Link>
              <Link href="/plugins" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Plugins
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
