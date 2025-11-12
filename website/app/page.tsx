import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import GitHubStats from '@/components/GitHubStats';
import NewsletterSignup from '@/components/NewsletterSignup';

export default function Home() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32" aria-label="Hero">
        <div className="absolute inset-0 gradient-primary opacity-5" aria-hidden="true"></div>
        <div className="container relative">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
              Building the Future of{' '}
              <span className="text-gradient">AI-Human Collaboration</span>
            </h1>
            <p className="text-xl sm:text-2xl text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto">
              Smart AI Memory creates production-ready frameworks and tools that enable
              AI systems to anticipate needs, predict problems, and transform workflows.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="#products" className="btn btn-primary text-lg px-8 py-4" aria-label="Explore our products">
                Explore Our Products
              </Link>
              <Link href="#examples" className="btn btn-outline text-lg px-8 py-4" aria-label="See example projects">
                See Examples
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30" aria-label="Our mission">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">
              Our Mission
            </h2>
            <p className="text-xl text-[var(--text-secondary)] leading-relaxed">
              We build AI systems that don't just respond to requests—they anticipate needs,
              predict problems before they occur, and learn from patterns across domains.
              Our frameworks enable developers to create Level 4 Anticipatory Intelligence
              that transforms how humans and AI collaborate.
            </p>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section id="products" className="py-20" aria-label="Our products">
        <div className="container">
          <h2 className="text-4xl font-bold text-center mb-4">
            Our Products
          </h2>
          <p className="text-xl text-center text-[var(--text-secondary)] mb-12 max-w-3xl mx-auto">
            Production-ready frameworks for building anticipatory AI systems
          </p>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Empathy Framework */}
            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--primary)] border-opacity-20 hover:border-opacity-100 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-4xl">🧠</div>
                <h3 className="text-2xl font-bold">Empathy Framework</h3>
              </div>
              <p className="text-sm text-[var(--muted)] mb-4">v1.6.0 Production/Stable</p>
              <p className="text-[var(--text-secondary)] mb-6">
                A 5-level maturity model for AI-human collaboration, progressing from reactive
                responses to Level 4 Anticipatory Intelligence. Includes 30+ production wizards
                for software development and healthcare.
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span className="text-sm"><strong>553 tests</strong>, 63.87% coverage, 95%+ on core modules</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span className="text-sm"><strong>Fair Source License</strong> - Free for students & small teams</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span className="text-sm"><strong>Multi-LLM support</strong> - Claude, GPT-4, Gemini, local models</span>
                </div>
              </div>
              <div className="flex gap-3">
                <Link href="/framework" className="btn btn-primary flex-1">
                  Learn More
                </Link>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework"
                  className="btn btn-outline flex-1"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub
                </a>
              </div>
            </div>

            {/* MemDocs */}
            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--secondary)] border-opacity-20 hover:border-opacity-100 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-4xl">📚</div>
                <h3 className="text-2xl font-bold">MemDocs</h3>
              </div>
              <p className="text-sm text-[var(--muted)] mb-4">Project-Specific Memory System</p>
              <p className="text-[var(--text-secondary)] mb-6">
                Persistent project-specific memory that works seamlessly with Empathy Framework.
                MemDocs enables AI to remember context, decisions, and patterns across sessions,
                creating true continuity in your AI-human collaboration.
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span className="text-sm"><strong>Project-specific memories</strong> that persist across sessions</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span className="text-sm"><strong>Integrated with Empathy Framework</strong> for Level 5 intelligence</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span className="text-sm"><strong>Pattern learning</strong> from historical interactions</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[var(--success)] mt-1">✓</span>
                  <span className="text-sm"><strong>Context continuity</strong> across development sessions</span>
                </div>
              </div>
              <div className="flex gap-3">
                <a
                  href="https://github.com/Smart-AI-Memory/MemDocs"
                  className="btn btn-secondary flex-1"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on GitHub
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Transformative Stack */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-center mb-6">
              The Transformative Development Stack
            </h2>
            <p className="text-xl text-center text-[var(--text-secondary)] mb-12">
              Claude Code + VS Code + MemDocs + Empathy Framework
            </p>

            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--accent)] border-opacity-20">
              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <span>🚀</span> Development Velocity
                  </h3>
                  <p className="text-[var(--text-secondary)] mb-4">
                    Build production-quality applications <strong>10x faster</strong> with AI that
                    anticipates your needs, prevents bugs before they happen, and maintains context
                    across sessions with MemDocs.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <span>✨</span> Quality & Reliability
                  </h3>
                  <p className="text-[var(--text-secondary)] mb-4">
                    Ship <strong>higher quality code</strong> with built-in security scanning,
                    performance optimization, and comprehensive testing—all guided by Level 4
                    Anticipatory Intelligence.
                  </p>
                </div>
              </div>

              <div className="mb-6 p-6 bg-[var(--border)] bg-opacity-20 rounded-lg">
                <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span>📚</span> How MemDocs & Empathy Work Together
                </h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-[var(--text-secondary)]">
                      <strong>Empathy Framework</strong> provides the intelligence levels—from reactive
                      to anticipatory AI that predicts problems before they happen.
                    </p>
                  </div>
                  <div>
                    <p className="text-[var(--text-secondary)]">
                      <strong>MemDocs</strong> provides persistent project-specific memory, enabling
                      the framework to remember context, patterns, and decisions across sessions.
                    </p>
                  </div>
                </div>
                <p className="text-sm text-[var(--muted)] mt-4 text-center">
                  Together, they create <strong>Level 5 Transformative Intelligence</strong> that learns and evolves with your projects.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <h2 className="text-4xl font-bold text-center mb-12">
            The 5 Levels of AI Empathy
          </h2>

          <div className="max-w-4xl mx-auto grid gap-4">
            {[
              {
                level: 1,
                name: 'Reactive',
                description: 'Responds only when asked',
                example: 'Most current AI tools'
              },
              {
                level: 2,
                name: 'Guided',
                description: 'Asks clarifying questions',
                example: 'ChatGPT, basic assistants'
              },
              {
                level: 3,
                name: 'Proactive',
                description: 'Notices patterns and offers improvements',
                example: 'GitHub Copilot, advanced linters'
              },
              {
                level: 4,
                name: 'Anticipatory',
                description: 'Predicts future problems before they happen',
                example: 'Empathy Framework ✨',
                highlight: true
              },
              {
                level: 5,
                name: 'Transformative',
                description: 'Reshapes workflows to prevent entire classes of problems',
                example: 'Our vision for the future'
              }
            ].map((item) => (
              <div
                key={item.level}
                className={`p-6 rounded-lg border-2 ${
                  item.highlight
                    ? 'border-[var(--accent)] bg-[var(--accent)] text-white'
                    : 'border-[var(--border)]'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl ${
                      item.highlight
                        ? 'bg-white text-[var(--accent)]'
                        : 'bg-[var(--border)] text-[var(--muted)]'
                    }`}
                  >
                    {item.level}
                  </div>
                  <div className="flex-1">
                    <h3 className={`text-xl font-bold mb-2 ${item.highlight ? 'text-white' : ''}`}>
                      Level {item.level}: {item.name}
                    </h3>
                    <p className={`mb-2 ${item.highlight ? 'text-white opacity-90' : 'text-[var(--text-secondary)]'}`}>{item.description}</p>
                    <p className={`text-sm ${item.highlight ? 'text-white opacity-75' : 'text-[var(--muted)]'}`}>
                      <strong>Example:</strong> {item.example}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* GitHub Stats Section */}
      <section className="py-20" aria-label="GitHub statistics">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              Open Source & Community-Driven
            </h2>
            <p className="text-xl text-[var(--text-secondary)]">
              Join the growing community building the future of AI-human collaboration
            </p>
          </div>
          <div className="max-w-5xl mx-auto">
            <GitHubStats />
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30" aria-label="Newsletter signup">
        <div className="container">
          <NewsletterSignup />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-primary text-white" aria-label="Call to action">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">
              Ready to Build Anticipatory AI?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Get started with the Empathy Framework and join the community building
              the future of AI-human collaboration.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/framework" className="btn bg-white text-[var(--primary)] hover:bg-gray-100 text-lg px-8 py-4">
                Explore the Framework
              </Link>
              <a
                href="https://github.com/Smart-AI-Memory/empathy-framework"
                className="btn bg-transparent border-2 border-white text-white hover:bg-white hover:text-[var(--primary)] text-lg px-8 py-4"
                target="_blank"
                rel="noopener noreferrer"
              >
                View on GitHub
              </a>
            </div>
            <p className="mt-6 text-sm opacity-75">
              Fair Source License 0.9 • Free for students & small teams • Commercial for 6+ employees
            </p>
          </div>
        </div>
      </section>
      </main>
      <Footer />
    </>
  );
}
