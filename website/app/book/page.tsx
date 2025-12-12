import Link from 'next/link';

// Gumroad product URL for pay-what-you-want book
const GUMROAD_BOOK_URL = 'https://roebucksmith.gumroad.com/l/empathy-book';

export default function BookPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <nav className="border-b border-[var(--border)] py-4">
        <div className="container flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gradient">
            Empathy Framework
          </Link>
          <div className="flex gap-6">
            <Link href="/framework" className="text-sm hover:text-[var(--primary)]">Framework</Link>
            <Link href="/docs" className="text-sm hover:text-[var(--primary)]">Docs</Link>
            <Link href="/plugins" className="text-sm hover:text-[var(--primary)]">Plugins</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-20 gradient-primary text-white">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              Empathy
            </h1>
            <p className="text-2xl mb-4 opacity-90">
              Multi-Agent Coordination with Persistent and Short-Term Memory
            </p>
            <p className="text-lg opacity-75">
              Available Now
            </p>
          </div>
        </div>
      </section>

      {/* Book Details */}
      <section className="py-20">
        <div className="container">
          <div className="grid md:grid-cols-2 gap-12 max-w-6xl mx-auto">
            {/* Left Column - Book Cover & Purchase */}
            <div className="flex flex-col items-center">
              <div className="w-full max-w-md aspect-[3/4] gradient-accent rounded-lg shadow-2xl mb-8 flex items-center justify-center">
                <div className="text-center text-white p-8">
                  <div className="text-6xl mb-4">📖</div>
                  <h2 className="text-3xl font-bold mb-2">Empathy</h2>
                  <p className="text-lg opacity-90">Multi-Agent Coordination with Persistent and Short-Term Memory</p>
                  <p className="text-sm mt-4 opacity-75">By Patrick Roebuck</p>
                </div>
              </div>

              <div className="w-full max-w-md bg-[var(--border)] bg-opacity-30 rounded-lg p-8">
                <div className="text-center mb-6">
                  <div className="text-4xl font-bold text-[var(--primary)] mb-2">$5+</div>
                  <p className="text-[var(--muted)] text-sm">Pay what you want (min $5)</p>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Digital book (PDF)</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Complete guide to multi-agent coordination</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Philosophy of anticipatory AI</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Implementation patterns with code</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Lifetime access to all updates</span>
                  </div>
                </div>

                <a
                  href={GUMROAD_BOOK_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary w-full text-lg mb-4 block text-center"
                >
                  Get the Book
                </a>

                <p className="text-xs text-center text-[var(--muted)]">
                  Your support helps development. Pay more if you find value!
                </p>

                <div className="mt-6 pt-6 border-t border-[var(--border)]">
                  <p className="text-sm text-center text-[var(--text-secondary)] mb-3">
                    Company with 6+ employees?
                  </p>
                  <Link href="/pricing" className="btn btn-outline w-full text-sm">
                    Commercial License - $99/dev/year
                  </Link>
                </div>
              </div>
            </div>

            {/* Right Column - Description */}
            <div>
              <h2 className="text-3xl font-bold mb-6">What You'll Learn</h2>

              <div className="space-y-6 mb-8">
                <div>
                  <h3 className="text-xl font-bold mb-3 text-[var(--primary)]">Part 1: The Theory</h3>
                  <p className="text-[var(--text-secondary)] mb-3">
                    Understand the 5 Levels of AI Empathy and why Level 4 (Anticipatory)
                    represents a paradigm shift in how we build software.
                  </p>
                  <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span>From Reactive to Anticipatory intelligence</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span>Pattern recognition vs. trajectory prediction</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span>Building systems that predict future problems</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-3 text-[var(--primary)]">Part 2: Implementation</h3>
                  <p className="text-[var(--text-secondary)] mb-3">
                    Three detailed case studies showing how to build Level 4 systems:
                  </p>
                  <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span><strong>Enhanced Testing Wizard:</strong> Predict which untested code will cause bugs</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span><strong>Performance Profiling Wizard:</strong> Forecast performance degradation</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span><strong>Security Analysis Wizard:</strong> Identify exploitable vulnerabilities</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-3 text-[var(--primary)]">Part 3: Reference</h3>
                  <p className="text-[var(--text-secondary)] mb-3">
                    Complete catalog of 20+ wizards with descriptions, use cases, and access to the GitHub repository.
                  </p>
                  <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span>3 wizards with deep implementation details</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span>17+ additional wizards available via GitHub</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--accent)]">•</span>
                      <span>API reference and integration guides</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="bg-[var(--border)] bg-opacity-30 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-3">Who This Book Is For</h3>
                <ul className="space-y-2 text-[var(--text-secondary)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span><strong>Students:</strong> Learn cutting-edge AI concepts</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span><strong>Developers:</strong> Build anticipatory systems</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span><strong>Senior Engineers:</strong> Transform your development process</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--success)]">✓</span>
                    <span><strong>Tech Leaders:</strong> Understand the future of software</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Chapter 23 Preview */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <span className="text-xs px-3 py-1 bg-[var(--primary)] bg-opacity-20 text-[var(--primary)] rounded-full">
                FREE PREVIEW
              </span>
            </div>
            <h2 className="text-3xl font-bold text-center mb-6">Chapter 23: Distributed Memory Networks</h2>
            <p className="text-center text-[var(--text-secondary)] mb-8 max-w-2xl mx-auto">
              Learn how multiple AI agents coordinate through shared pattern libraries, resolve conflicts,
              and collaborate efficiently. This chapter covers the ConflictResolver, AgentMonitor, and
              team coordination patterns.
            </p>
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="bg-[var(--background)] p-6 rounded-lg text-center">
                <div className="text-3xl mb-3">🔀</div>
                <h3 className="font-bold mb-2">Conflict Resolution</h3>
                <p className="text-sm text-[var(--text-secondary)]">
                  5 strategies for resolving pattern conflicts between agents
                </p>
              </div>
              <div className="bg-[var(--background)] p-6 rounded-lg text-center">
                <div className="text-3xl mb-3">📊</div>
                <h3 className="font-bold mb-2">Team Monitoring</h3>
                <p className="text-sm text-[var(--text-secondary)]">
                  Track collaboration efficiency and agent performance
                </p>
              </div>
              <div className="bg-[var(--background)] p-6 rounded-lg text-center">
                <div className="text-3xl mb-3">🤝</div>
                <h3 className="font-bold mb-2">Pattern Sharing</h3>
                <p className="text-sm text-[var(--text-secondary)]">
                  Agents learn from each other through shared pattern libraries
                </p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/chapter-23"
                className="btn btn-primary"
              >
                Read Chapter 23 Free
              </Link>
              <Link href="/demo/distributed-memory" className="btn btn-outline">
                Try Interactive Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* What's Inside */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">What's Inside</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-4xl mb-4">🧠</div>
                <h3 className="text-xl font-bold mb-3">Philosophy</h3>
                <p className="text-[var(--text-secondary)]">
                  Data sovereignty, trust as earned, and the six foundational principles of multi-agent coordination.
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-4">⚙️</div>
                <h3 className="text-xl font-bold mb-3">Implementation</h3>
                <p className="text-[var(--text-secondary)]">
                  Step-by-step guides to building short-term memory, agent coordination, and pattern staging.
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-xl font-bold mb-3">Practical Patterns</h3>
                <p className="text-[var(--text-secondary)]">
                  5 production-ready patterns with measurable benefits: 3x faster reviews, 68% auto-resolution.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
            <div className="space-y-6">
              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">What's included with the book?</h3>
                <p className="text-[var(--text-secondary)]">
                  The complete book covering multi-agent coordination philosophy, implementation guides, and
                  production-ready patterns. Digital formats (PDF, ePub, Mobi) with lifetime access to updates.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">Do I need the book to use the framework?</h3>
                <p className="text-[var(--text-secondary)]">
                  No. The Empathy Framework is open source and documented online. The book provides deeper
                  coverage of the philosophy, implementation details, and patterns that aren't in the docs.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">Who is the book for?</h3>
                <p className="text-[var(--text-secondary)]">
                  The book is for students, academics, solo developers, and small teams (≤5 employees) who
                  already have free commercial use rights under Fair Source 0.9. You can use the framework
                  and learn from the book at no additional licensing cost.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">What about larger companies?</h3>
                <p className="text-[var(--text-secondary)]">
                  Companies with 6+ employees need the Commercial License ($99/dev/year) to use the framework.
                  Visit our <Link href="/pricing" className="text-[var(--primary)] underline">pricing page</Link> for details.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">Is the Core Framework free?</h3>
                <p className="text-[var(--text-secondary)]">
                  The Empathy Framework uses Fair Source License 0.9. It's free for students, educators, and
                  companies with 5 or fewer employees. Commercial licensing ($99/year per developer) is required
                  for companies with 6+ employees.
                </p>
              </div>

              <div className="pb-6">
                <h3 className="text-xl font-bold mb-3">What format is the book?</h3>
                <p className="text-[var(--text-secondary)]">
                  Instant digital delivery in PDF, ePub, and Mobi formats. Read on any device.
                  You get lifetime access to all updates to this edition.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 gradient-primary text-white">
        <div className="container">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">Ready to Build Anticipatory AI?</h2>
            <p className="text-xl mb-8 opacity-90">
              The complete guide to building Level 4 Anticipatory AI systems with multi-agent coordination.
            </p>
            <a
              href={GUMROAD_BOOK_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="btn bg-white text-[var(--primary)] hover:bg-gray-100 text-lg px-8 py-4 inline-block"
            >
              Get the Book - $5+
            </a>
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
              <Link href="/docs" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Docs
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
