import Link from 'next/link';
import Image from 'next/image';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import GitHubStarsBadge from '@/components/GitHubStarsBadge';
import TestsBadge from '@/components/TestsBadge';
import PersonaCards from '@/components/PersonaCards';
import SocialProof from '@/components/SocialProof';
import LeadMagnet from '@/components/LeadMagnet';

const levels = [
  {
    level: 1,
    name: 'Reactive',
    description: 'Responds only when asked',
    example: 'Most current AI tools',
  },
  {
    level: 2,
    name: 'Guided',
    description: 'Asks clarifying questions',
    example: 'ChatGPT, basic assistants',
  },
  {
    level: 3,
    name: 'Proactive',
    description: 'Notices patterns and offers improvements',
    example: 'GitHub Copilot, advanced linters',
  },
  {
    level: 4,
    name: 'Anticipatory',
    description: 'Predicts future problems before they happen',
    example: 'Empathy',
    highlight: true,
  },
  {
    level: 5,
    name: 'Transformative',
    description: 'Reshapes workflows to prevent entire classes of problems',
    example: 'Our vision for the future',
    future: true,
  },
];

export default function Home() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-20 sm:py-28" aria-label="Hero">
          <div className="absolute inset-0" aria-hidden="true">
            <Image
              src="/images/AdobeStock_1773561909.jpeg"
              alt=""
              fill
              className="object-cover opacity-20"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-b from-[var(--background)] via-transparent to-[var(--background)]" />
          </div>
          <div className="container relative">
            <div className="max-w-4xl mx-auto text-center animate-fade-in">
              {/* Credibility Badges */}
              <div className="flex flex-wrap gap-3 justify-center mb-8">
                <GitHubStarsBadge />
                <TestsBadge />
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
                Build AI That Anticipates Problems{' '}
                <span className="text-gradient">Before They Happen</span>
              </h1>
              <p className="text-xl text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto">
                Production-ready frameworks for Level 4 Anticipatory Intelligence.
                Stop reacting. Start predicting.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link
                  href="/framework"
                  className="btn btn-primary text-lg px-8 py-4"
                  aria-label="Get started with the framework"
                >
                  Get Started Free
                </Link>
                <Link
                  href="/demo/distributed-memory"
                  className="btn btn-outline text-lg px-8 py-4"
                  aria-label="See a demo"
                >
                  See Demo
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Who This Is For */}
        <PersonaCards />

        {/* 5 Levels Section */}
        <section className="py-20" aria-label="The 5 levels of AI empathy">
          <div className="container">
            <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
              The 5 Levels of AI Intelligence
            </h2>
            <p className="text-center text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
              From reactive responses to anticipatory systems that predict problems 30-90 days ahead
            </p>

            <div className="max-w-4xl mx-auto grid gap-4">
              {levels.map((item) => (
                <div
                  key={item.level}
                  className={`p-6 rounded-lg border-2 transition-all ${
                    item.highlight
                      ? 'border-[var(--accent)] bg-[var(--accent)] text-white shadow-lg'
                      : item.future
                      ? 'border-dashed border-[var(--border)] opacity-60'
                      : 'border-[var(--border)] hover:border-[var(--primary)] hover:shadow-md'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div
                      className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl ${
                        item.highlight
                          ? 'bg-white text-[var(--accent)]'
                          : item.future
                          ? 'bg-[var(--border)] text-[var(--muted)] border-2 border-dashed'
                          : 'bg-[var(--border)] text-[var(--foreground)]'
                      }`}
                    >
                      {item.level}
                    </div>
                    <div className="flex-1">
                      <h3
                        className="text-xl font-bold mb-1"
                        style={{ color: item.highlight ? '#ffffff' : '#0F172A' }}
                      >
                        Level {item.level}: {item.name}
                        {item.highlight && (
                          <span className="ml-2 text-sm font-normal bg-white/20 px-2 py-0.5 rounded">
                            You are here
                          </span>
                        )}
                        {item.future && (
                          <span className="ml-2 text-sm font-normal" style={{ color: '#64748B' }}>
                            Coming soon
                          </span>
                        )}
                      </h3>
                      <p
                        className="mb-1"
                        style={{ color: item.highlight ? 'rgba(255,255,255,0.9)' : '#334155' }}
                      >
                        {item.description}
                      </p>
                      <p
                        className="text-sm"
                        style={{ color: item.highlight ? 'rgba(255,255,255,0.75)' : '#64748B' }}
                      >
                        Example: {item.example}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Products Section */}
        <section id="products" className="py-20 bg-[var(--border)] bg-opacity-30" aria-label="Our products">
          <div className="container">
            <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
              Complete AI Collaboration Platform
            </h2>
            <p className="text-center text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
              Intelligence + Memory + Coordination = Anticipatory AI
            </p>

            <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {/* Empathy */}
              <div className="bg-[var(--background)] p-6 rounded-xl border-2 border-[var(--primary)] border-opacity-30 hover:border-opacity-100 transition-all">
                <div className="text-4xl mb-4">🧠</div>
                <h3 className="text-xl font-bold mb-2">Empathy</h3>
                <p className="text-sm text-[var(--muted)] mb-3">The intelligence layer</p>
                <p className="text-[var(--text-secondary)] text-sm mb-4">
                  5-level maturity model with 44 specialized wizards for healthcare,
                  software development, and AI collaboration.
                </p>
                <div className="flex flex-wrap gap-1 mb-4">
                  <span className="text-xs bg-[var(--border)] px-2 py-1 rounded">Claude</span>
                  <span className="text-xs bg-[var(--border)] px-2 py-1 rounded">GPT-4</span>
                  <span className="text-xs bg-[var(--border)] px-2 py-1 rounded">Gemini</span>
                </div>
                <Link href="/framework" className="btn btn-primary w-full text-sm">
                  Explore Framework
                </Link>
              </div>

              {/* Long-Term Memory */}
              <div className="bg-[var(--background)] p-6 rounded-xl border-2 border-[var(--secondary)] border-opacity-30 hover:border-opacity-100 transition-all">
                <div className="text-4xl mb-4">📚</div>
                <h3 className="text-xl font-bold mb-2">Long-Term Memory</h3>
                <p className="text-sm text-[var(--muted)] mb-3">Built-in pattern storage</p>
                <p className="text-[var(--text-secondary)] text-sm mb-4">
                  Persistent project-specific context that carries across sessions.
                  Your AI remembers what matters.
                </p>
                <div className="flex flex-wrap gap-1 mb-4">
                  <span className="text-xs bg-[var(--border)] px-2 py-1 rounded">Cross-session</span>
                  <span className="text-xs bg-[var(--border)] px-2 py-1 rounded">Patterns</span>
                </div>
                <Link href="/framework#memory" className="btn btn-outline w-full text-sm">
                  Learn More
                </Link>
              </div>

              {/* Advanced Capabilities (Chapter 23) */}
              <div className="bg-[var(--background)] p-6 rounded-xl border-2 border-[var(--accent)] border-opacity-30 hover:border-opacity-100 transition-all">
                <div className="text-4xl mb-4">🔀</div>
                <h3 className="text-xl font-bold mb-2">Advanced Capabilities</h3>
                <p className="text-sm text-[var(--muted)] mb-3">Multi-Agent Coordination</p>
                <p className="text-[var(--text-secondary)] text-sm mb-4">
                  Distributed Memory Networks enable teams of AI agents to share patterns,
                  resolve conflicts, and collaborate.
                </p>
                <div className="flex flex-wrap gap-1 mb-4">
                  <span className="text-xs bg-[var(--border)] px-2 py-1 rounded">Ch. 23</span>
                  <span className="text-xs bg-[var(--border)] px-2 py-1 rounded">Free preview</span>
                </div>
                <div className="space-y-2">
                  <Link href="/demo/distributed-memory" className="btn btn-primary w-full text-sm">
                    Try Demo
                  </Link>
                  <Link
                    href="/chapter-23"
                    className="block text-center text-xs text-[var(--primary)] hover:underline"
                  >
                    Read Chapter 23 Free →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Social Proof */}
        <SocialProof />

        {/* Interactive Demos */}
        <section className="py-20 bg-[var(--border)] bg-opacity-30" aria-label="Interactive demos">
          <div className="container">
            <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
              Try It Live
            </h2>
            <p className="text-center text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
              No signup required. See Level 4 in action.
            </p>

            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {/* Healthcare */}
              <a
                href="https://healthcare.smartaimemory.com/static/dashboard.html"
                target="_blank"
                rel="noopener noreferrer"
                className="group bg-[var(--background)] rounded-xl overflow-hidden border-2 border-[var(--border)] hover:border-[var(--primary)] hover:shadow-lg transition-all"
              >
                <div className="aspect-video bg-[var(--border)] relative overflow-hidden">
                  <Image
                    src="/images/demo-placeholder-healthcare.svg"
                    alt="Healthcare Wizards Dashboard"
                    fill
                    className="object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Image
                      src="/images/icons/stethoscope.svg"
                      alt=""
                      width={24}
                      height={24}
                      className="text-[var(--primary)]"
                    />
                    <h3 className="text-lg font-bold group-hover:text-[var(--primary)] transition-colors">
                      Healthcare Wizards
                    </h3>
                  </div>
                  <p className="text-sm text-[var(--text-secondary)] mb-3">
                    14+ HIPAA-compliant clinical tools
                  </p>
                  <span className="text-sm font-medium text-[var(--primary)]">
                    Launch Demo →
                  </span>
                </div>
              </a>

              {/* Software */}
              <a
                href="https://wizards.smartaimemory.com"
                target="_blank"
                rel="noopener noreferrer"
                className="group bg-[var(--background)] rounded-xl overflow-hidden border-2 border-[var(--border)] hover:border-[var(--secondary)] hover:shadow-lg transition-all"
              >
                <div className="aspect-video bg-[var(--border)] relative overflow-hidden">
                  <Image
                    src="/images/demo-placeholder-software.svg"
                    alt="Software Development Wizards Dashboard"
                    fill
                    className="object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Image
                      src="/images/icons/file-terminal.svg"
                      alt=""
                      width={24}
                      height={24}
                    />
                    <h3 className="text-lg font-bold group-hover:text-[var(--secondary)] transition-colors">
                      Developer Wizards
                    </h3>
                  </div>
                  <p className="text-sm text-[var(--text-secondary)] mb-3">
                    16+ debugging & optimization tools
                  </p>
                  <span className="text-sm font-medium text-[var(--secondary)]">
                    Launch Demo →
                  </span>
                </div>
              </a>
            </div>
          </div>
        </section>

        {/* Lead Magnet CTA */}
        <LeadMagnet />
      </main>
      <Footer />
    </>
  );
}
