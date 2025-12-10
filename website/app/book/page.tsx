import Link from 'next/link';
import CheckoutButton from '@/components/CheckoutButton';

// Price ID from Stripe Dashboard - hardcoded fallback for build-time reliability
const BOOK_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_PRICE_BOOK || 'price_1Sbf3xAbABKRT84gGn7yaivw';

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
              Coming December 2025
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
                  <p className="text-[var(--muted)] text-sm">Pre-order Price</p>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Digital book (PDF, ePub, Mobi)</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">First year developer license ($49.99 vs $99.99/year)</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Software Development Plugin access</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Healthcare Plugin access</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Permanent access to book (all editions)</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Renew license at $99.99/year after first year</span>
                  </div>
                </div>

                <CheckoutButton
                  priceId={BOOK_PRICE_ID}
                  mode="payment"
                  buttonText="Pre-order Now - $49"
                  className="btn btn-primary w-full text-lg mb-4"
                />

                <p className="text-xs text-center text-[var(--muted)]">
                  Secure checkout powered by Stripe. Available December 2025.
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
              <a
                href="https://smart-ai-memory.github.io/memdocs-empathy-book/chapters/part-6/23-distributed-memory.html"
                className="btn btn-primary"
                target="_blank"
                rel="noopener noreferrer"
              >
                Read Chapter 23 Free
              </a>
              <Link href="/demo/distributed-memory" className="btn btn-outline">
                Try Interactive Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Pre-order Benefits */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Pre-order Benefits</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-4xl mb-4">💰</div>
                <h3 className="text-xl font-bold mb-3">Best Price</h3>
                <p className="text-[var(--text-secondary)]">
                  Lock in the pre-order price of $49. Price will increase after December 2025 launch.
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-4">📚</div>
                <h3 className="text-xl font-bold mb-3">Complete Edition</h3>
                <p className="text-[var(--text-secondary)]">
                  Get the full book plus Software and Healthcare plugins when released in December 2025.
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-4">🚀</div>
                <h3 className="text-xl font-bold mb-3">December 2025</h3>
                <p className="text-[var(--text-secondary)]">
                  Immediate access to the complete book, plugins, and licenses upon release.
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
                  When released in December 2025, you'll get the complete book (theory and implementation examples),
                  plus working Software and Healthcare plugins with 1 developer license. All updates to this
                  edition are included.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">How does the developer license work?</h3>
                <p className="text-[var(--text-secondary)]">
                  Each book purchase includes a 1-year developer license at the special price of $49.99 (50% off
                  the regular $99.99/year). After the first year, you can renew at $99.99/year. The license covers
                  one developer across all their development environments. Need more licenses for your team? Each
                  team member needs their own book purchase and license.
                </p>
              </div>

              <div className="border-b border-[var(--border)] pb-6">
                <h3 className="text-xl font-bold mb-3">Is the Core Framework free?</h3>
                <p className="text-[var(--text-secondary)]">
                  The Empathy Framework uses Fair Source License 0.9. It's free for students, educators, and
                  companies with 5 or fewer employees. Commercial licensing is required for companies with 6+ employees.
                  The book includes your first year of commercial licensing at 50% off ($49.99 vs $99.99/year).
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
                <h3 className="text-xl font-bold mb-3">When will the book be available?</h3>
                <p className="text-[var(--text-secondary)]">
                  The complete book, including all theory, implementation examples, and commercial plugins,
                  will be released in December 2025. Pre-orders will be available soon to lock in the $49 price.
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
            <h2 className="text-4xl font-bold mb-6">Coming December 2025</h2>
            <p className="text-xl mb-8 opacity-90">
              The complete guide to building Level 4 Anticipatory AI systems with working commercial plugins.
            </p>
            <CheckoutButton
              priceId={BOOK_PRICE_ID}
              mode="payment"
              buttonText="Pre-order Now - $49"
              className="btn bg-white text-[var(--primary)] hover:bg-gray-100 text-lg px-8 py-4"
            />
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
