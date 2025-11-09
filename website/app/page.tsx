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
              Building the Future of{' '}
              <span className="text-gradient">AI-Human Collaboration</span>
            </h1>
            <p className="text-xl sm:text-2xl text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto">
              Smart AI Memory creates production-ready frameworks and tools that enable
              AI systems to anticipate needs, predict problems, and transform workflows.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="#products" className="btn btn-primary text-lg px-8 py-4">
                Explore Our Products
              </Link>
              <Link href="#examples" className="btn btn-outline text-lg px-8 py-4">
                See Examples
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
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
      <section id="products" className="py-20">
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
                  href="https://github.com/Smart-AI-Memory/empathy"
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

              <div className="pt-6 border-t border-[var(--border)]">
                <p className="text-sm text-[var(--muted)] italic text-center">
                  "The framework transformed our AI development workflow. Instead of discovering
                  issues weeks later during debugging, the wizards alerted us to emerging problems
                  immediately. We shipped higher quality code, many times faster."
                </p>
                <p className="text-xs text-[var(--muted)] text-center mt-2">
                  — Development team using Empathy Framework in production
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Example Projects Section */}
      <section id="examples" className="py-20">
        <div className="container">
          <h2 className="text-4xl font-bold text-center mb-4">
            Example Projects
          </h2>
          <p className="text-xl text-center text-[var(--text-secondary)] mb-12 max-w-3xl mx-auto">
            Real-world applications built with our technology stack
          </p>

          <div className="max-w-5xl mx-auto grid gap-8">
            {/* Medical Wizards Dashboard */}
            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--border)] hover:border-[var(--accent)] transition-all">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-4xl">🏥</div>
                    <h3 className="text-2xl font-bold">Medical Wizards Dashboard</h3>
                  </div>
                  <p className="text-[var(--text-secondary)] mb-4">
                    Production healthcare application demonstrating Level 4 Anticipatory Intelligence
                    with clinical wizards. Features patient trajectory analysis, protocol compliance
                    monitoring, and predictive risk assessment.
                  </p>

                  <div className="space-y-2 mb-6">
                    <h4 className="text-sm font-bold text-[var(--muted)] uppercase">Built With:</h4>
                    <div className="flex flex-wrap gap-2">
                      <span className="px-3 py-1 bg-[var(--primary)] bg-opacity-10 text-[var(--primary)] rounded-full text-sm font-semibold">
                        Claude Code
                      </span>
                      <span className="px-3 py-1 bg-[var(--accent)] bg-opacity-10 text-[var(--accent)] rounded-full text-sm font-semibold">
                        Empathy Framework
                      </span>
                      <span className="px-3 py-1 bg-[var(--secondary)] bg-opacity-10 text-[var(--secondary)] rounded-full text-sm font-semibold">
                        MemDocs
                      </span>
                      <span className="px-3 py-1 bg-[var(--border)] text-[var(--muted)] rounded-full text-sm">
                        VS Code
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3 mb-6">
                    <div className="flex items-start gap-2">
                      <span className="text-[var(--success)] mt-1">✓</span>
                      <span className="text-sm"><strong>18+ Healthcare Wizards</strong> for clinical decision support</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-[var(--success)] mt-1">✓</span>
                      <span className="text-sm"><strong>Real-time trajectory analysis</strong> predicting patient deterioration</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-[var(--success)] mt-1">✓</span>
                      <span className="text-sm"><strong>HIPAA-compliant</strong> pattern detection and monitoring</span>
                    </div>
                  </div>

                  <a
                    href="/dashboard"
                    className="btn btn-primary"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Dashboard →
                  </a>
                </div>

                <div className="md:w-1/3">
                  <div className="bg-[var(--border)] bg-opacity-30 rounded-lg p-6 h-full flex flex-col justify-center">
                    <div className="text-6xl text-center mb-4">📊</div>
                    <p className="text-center text-sm text-[var(--muted)]">
                      Interactive dashboard showcasing Level 4 Anticipatory Intelligence in healthcare
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Software Development Dashboard */}
            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-4xl">💻</div>
                    <h3 className="text-2xl font-bold">Software Development Dashboard</h3>
                  </div>
                  <p className="text-[var(--text-secondary)] mb-4">
                    Development analytics platform powered by Level 4 Anticipatory Intelligence.
                    Predicts bugs before they happen, identifies security vulnerabilities, and
                    optimizes performance across your codebase.
                  </p>

                  <div className="space-y-2 mb-6">
                    <h4 className="text-sm font-bold text-[var(--muted)] uppercase">Built With:</h4>
                    <div className="flex flex-wrap gap-2">
                      <span className="px-3 py-1 bg-[var(--primary)] bg-opacity-10 text-[var(--primary)] rounded-full text-sm font-semibold">
                        Claude Code
                      </span>
                      <span className="px-3 py-1 bg-[var(--accent)] bg-opacity-10 text-[var(--accent)] rounded-full text-sm font-semibold">
                        Empathy Framework
                      </span>
                      <span className="px-3 py-1 bg-[var(--secondary)] bg-opacity-10 text-[var(--secondary)] rounded-full text-sm font-semibold">
                        MemDocs
                      </span>
                      <span className="px-3 py-1 bg-[var(--border)] text-[var(--muted)] rounded-full text-sm">
                        VS Code
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3 mb-6">
                    <div className="flex items-start gap-2">
                      <span className="text-[var(--success)] mt-1">✓</span>
                      <span className="text-sm"><strong>16+ Software Wizards</strong> for code analysis & optimization</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-[var(--success)] mt-1">✓</span>
                      <span className="text-sm"><strong>Predictive bug detection</strong> before code reaches production</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-[var(--success)] mt-1">✓</span>
                      <span className="text-sm"><strong>AI-powered test generation</strong> and coverage optimization</span>
                    </div>
                  </div>

                  <a
                    href="/dev-dashboard"
                    className="btn btn-primary"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Dashboard →
                  </a>
                </div>

                <div className="md:w-1/3">
                  <div className="bg-[var(--border)] bg-opacity-30 rounded-lg p-6 h-full flex flex-col justify-center">
                    <div className="text-6xl text-center mb-4">⚡</div>
                    <p className="text-center text-sm text-[var(--muted)]">
                      Real-time code intelligence preventing issues before deployment
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* More Examples Coming */}
            <div className="bg-[var(--background)] p-8 rounded-lg border-2 border-[var(--border)] border-dashed opacity-60">
              <div className="text-center">
                <div className="text-4xl mb-4">🚧</div>
                <h3 className="text-xl font-bold mb-2">More Examples Coming Soon</h3>
                <p className="text-[var(--text-secondary)]">
                  AI agent orchestration, multi-model workflows, and more demonstrations
                  of the transformative development stack.
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
                      <strong>Example:</strong> {item.example}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-primary text-white">
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
                href="https://github.com/Smart-AI-Memory/empathy"
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
              <Link href="/plugins" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Plugins
              </Link>
              <Link href="/contact" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Contact
              </Link>
              <a
                href="https://github.com/Smart-AI-Memory"
                className="text-sm text-[var(--muted)] hover:text-[var(--primary)]"
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
