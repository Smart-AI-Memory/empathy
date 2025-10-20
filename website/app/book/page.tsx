import Link from 'next/link';

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
              The Empathy Framework
            </h1>
            <p className="text-2xl mb-4 opacity-90">
              Transforming Software Development with Anticipatory AI
            </p>
            <p className="text-lg opacity-75">
              Early Access Edition - Available Now
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
                  <h2 className="text-3xl font-bold mb-2">The Empathy Framework</h2>
                  <p className="text-lg opacity-90">Anticipatory AI for Software Development</p>
                  <p className="text-sm mt-4 opacity-75">By Patrick Roebuck</p>
                </div>
              </div>

              <div className="w-full max-w-md bg-[var(--border)] bg-opacity-30 rounded-lg p-8">
                <div className="text-center mb-6">
                  <div className="text-5xl font-bold text-[var(--primary)] mb-2">$49</div>
                  <p className="text-[var(--muted)] text-sm">Early Access Price</p>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Digital book (PDF, ePub, Mobi)</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">1 Developer License</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Access to Software Development Plugin</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Access to Healthcare Plugin</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Free updates to this edition</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Lifetime access to purchased version</span>
                  </div>
                </div>

                <button className="btn btn-primary w-full text-lg mb-4">
                  Purchase Early Access
                </button>

                <p className="text-xs text-center text-[var(--muted)]">
                  Need team licenses? Purchase additional copies for more developer licenses.
                </p>
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

      {/* Early Access Benefits */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Early Access Benefits</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-4xl mb-4">💰</div>
                <h3 className="text-xl font-bold mb-3">Best Price</h3>
                <p className="text-[var(--text-secondary)]">
                  Get the lowest price available. Price will increase as content is completed.
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-4">📚</div>
                <h3 className="text-xl font-bold mb-3">Free Updates</h3>
                <p className="text-[var(--text-secondary)]">
                  Receive all updates and additional chapters as they're written at no extra cost.
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-4">🚀</div>
                <h3 className="text-xl font-bold mb-3">Start Now</h3>
                <p className="text-[var(--text-secondary)]">
                  Begin learning immediately with available chapters and working plugins.
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
                <h3 className="text-xl font-bold mb-3">What's included with early access?</h3>
                <p className="text-[var(--text-secondary)]">
                  You get immediate access to available chapters (theory and first implementation examples),
                  plus working Software and Healthcare plugins with 1 developer license. You'll receive all
                  future updates to this edition automatically.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">How does the developer license work?</h3>
                <p className="text-[var(--text-secondary)]">
                  Each book purchase includes one perpetual developer license. The license is tied to one
                  developer and covers the purchased version plus all minor updates. Need more licenses for
                  your team? Purchase additional copies of the book.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">Is the Core Framework free?</h3>
                <p className="text-[var(--text-secondary)]">
                  Yes! The Empathy Framework Core is Apache 2.0 licensed and completely free. The commercial
                  plugins (Software Development and Healthcare) require a license, which comes with the book.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">What if I need to change my developer license?</h3>
                <p className="text-[var(--text-secondary)]">
                  You can deactivate your license from one machine and activate it on another. Contact support
                  if you need assistance.
                </p>
              </div>

              <div className="pb-6">
                <h3 className="text-xl font-bold mb-3">When will the book be complete?</h3>
                <p className="text-[var(--text-secondary)]">
                  We're releasing chapters progressively. The theory section and first implementation examples
                  are available now. All core content will be completed by Q2 2026. You'll get all updates
                  automatically as they're released.
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
            <h2 className="text-4xl font-bold mb-6">Ready to Start?</h2>
            <p className="text-xl mb-8 opacity-90">
              Join the early access program and start building anticipatory AI systems today.
            </p>
            <button className="btn bg-white text-[var(--primary)] hover:bg-gray-100 text-lg px-8 py-4">
              Purchase for $49
            </button>
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
