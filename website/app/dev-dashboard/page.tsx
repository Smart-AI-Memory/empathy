import Link from 'next/link';
import WizardPlayground from '@/components/WizardPlayground';

export default function DevDashboard() {
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
            <Link href="/dashboard" className="text-sm hover:text-[var(--primary)]">Medical Dashboard</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-12 bg-gradient-to-b from-[var(--border)] to-transparent">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-6xl mb-6">💻</div>
            <h1 className="text-4xl font-bold mb-4">
              Software Development <span className="text-gradient">Dashboard</span>
            </h1>
            <p className="text-xl text-[var(--text-secondary)] mb-6">
              Level 4 Anticipatory Intelligence for Software Engineering
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
              <div className="text-3xl font-bold text-[var(--primary)] mb-2">16+</div>
              <div className="text-sm text-[var(--text-secondary)]">Software Wizards</div>
            </div>
            <div className="bg-[var(--background)] border-2 border-[var(--border)] p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-[var(--success)] mb-2">Level 4</div>
              <div className="text-sm text-[var(--text-secondary)]">Anticipatory AI</div>
            </div>
            <div className="bg-[var(--background)] border-2 border-[var(--border)] p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-[var(--accent)] mb-2">Proactive</div>
              <div className="text-sm text-[var(--text-secondary)]">Bug Detection</div>
            </div>
            <div className="bg-[var(--background)] border-2 border-[var(--border)] p-6 rounded-lg text-center">
              <div className="text-3xl font-bold text-[var(--secondary)] mb-2">10x</div>
              <div className="text-sm text-[var(--text-secondary)]">Faster Development</div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Wizard Playground */}
      <section className="py-12 bg-[var(--border)] bg-opacity-20">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-4">Try Software Wizards</h2>
          <p className="text-center text-[var(--text-secondary)] mb-12 max-w-3xl mx-auto">
            Select a wizard below and provide code or requirements to see
            Level 4 Anticipatory Intelligence in action.
          </p>
          <WizardPlayground category="software" />
        </div>
      </section>

      {/* Software Development Wizards */}
      <section className="py-12">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">Development Intelligence Wizards</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {/* Advanced Debugging */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🐛</div>
                <h3 className="text-lg font-bold">Advanced Debugging</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Predicts bugs before they manifest in production with trajectory-based analysis.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Bug risk pattern analysis</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Automated fix suggestions</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Root cause identification</span>
                </div>
              </div>
            </div>

            {/* Security Analysis */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🔒</div>
                <h3 className="text-lg font-bold">Security Analysis</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Identifies vulnerabilities and security risks across your entire codebase.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>OWASP Top 10 scanning</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Vulnerability assessment</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Exploit analysis</span>
                </div>
              </div>
            </div>

            {/* Performance Profiling */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">⚡</div>
                <h3 className="text-lg font-bold">Performance Profiling</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Predicts performance bottlenecks and optimization opportunities before deployment.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Bottleneck detection</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Performance trajectory analysis</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Optimization recommendations</span>
                </div>
              </div>
            </div>

            {/* AI Documentation */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">📝</div>
                <h3 className="text-lg font-bold">AI Documentation</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Automatically generates and maintains comprehensive code documentation.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Auto-generated docstrings</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>API documentation</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Usage examples</span>
                </div>
              </div>
            </div>

            {/* AI Collaboration */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🤝</div>
                <h3 className="text-lg font-bold">AI Collaboration</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Multi-agent system for complex development tasks with coordinated AI assistants.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Multi-agent orchestration</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Task delegation</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Coordinated problem-solving</span>
                </div>
              </div>
            </div>

            {/* Agent Orchestration */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🎭</div>
                <h3 className="text-lg font-bold">Agent Orchestration</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Coordinates multiple AI agents for complex, multi-step development workflows.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Multi-wizard coordination</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Agent orchestration</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Task parallelization</span>
                </div>
              </div>
            </div>

            {/* RAG Pattern Wizard */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🔍</div>
                <h3 className="text-lg font-bold">RAG Pattern Wizard</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Implements Retrieval-Augmented Generation patterns for context-aware AI responses.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Context retrieval</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Knowledge integration</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Semantic search</span>
                </div>
              </div>
            </div>

            {/* Prompt Engineering */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">💡</div>
                <h3 className="text-lg font-bold">Prompt Engineering</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Optimizes prompts for maximum effectiveness with LLMs and AI models.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Prompt optimization</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Template generation</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Best practice validation</span>
                </div>
              </div>
            </div>

            {/* Multi-Model Wizard */}
            <div className="bg-[var(--background)] p-6 rounded-lg border-2 border-[var(--border)] hover:border-[var(--primary)] transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🔄</div>
                <h3 className="text-lg font-bold">Multi-Model Wizard</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Orchestrates multiple AI models for optimal results across different tasks.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Model selection</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Fallback strategies</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--success)]">✓</span>
                  <span>Cost optimization</span>
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
                <h3 className="text-xl font-bold mb-2">Codebase Analysis</h3>
                <p className="text-[var(--text-secondary)]">
                  Empathy Framework continuously analyzes your codebase, tracking changes, patterns,
                  dependencies, and code quality metrics in real-time.
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
                  AI wizards identify code patterns, anti-patterns, and trajectories that indicate
                  potential bugs, security vulnerabilities, or performance issues before they occur.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="flex-shrink-0 w-12 h-12 bg-[var(--primary)] bg-opacity-10 rounded-full flex items-center justify-center text-[var(--primary)] font-bold text-xl">
                3
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Predictive Recommendations</h3>
                <p className="text-[var(--text-secondary)]">
                  The system generates proactive recommendations with code fixes, optimizations,
                  and best practice suggestions before issues reach production.
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
                  MemDocs integration enables the system to learn from your project's history,
                  improving predictions and adapting to your team's coding patterns over time.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Real-World Impact */}
      <section className="py-12 bg-[var(--border)] bg-opacity-20">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">Real-World Impact</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="text-4xl font-bold text-[var(--primary)] mb-2">87%</div>
              <div className="text-sm text-[var(--text-secondary)]">Fewer bugs reaching production</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-[var(--success)] mb-2">10x</div>
              <div className="text-sm text-[var(--text-secondary)]">Faster development velocity</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-[var(--accent)] mb-2">95%</div>
              <div className="text-sm text-[var(--text-secondary)]">Security vulnerabilities caught early</div>
            </div>
          </div>

          <div className="mt-12 max-w-3xl mx-auto">
            <blockquote className="text-center">
              <p className="text-lg italic text-[var(--text-secondary)] mb-4">
                "The framework transformed our development workflow. Instead of discovering issues
                weeks later during debugging, the wizards alerted us to emerging problems immediately.
                We shipped higher quality code, many times faster."
              </p>
              <footer className="text-sm text-[var(--muted)]">
                — Development team using Empathy Framework in production
              </footer>
            </blockquote>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-b from-transparent to-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-6">
              Build Your Own Development Intelligence
            </h2>
            <p className="text-xl text-[var(--text-secondary)] mb-8">
              The Empathy Framework is Fair Source licensed and production-ready.
              Start building anticipatory AI for software development today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/framework" className="btn btn-primary">
                View Framework
              </Link>
              <a
                href="https://github.com/Smart-AI-Memory/empathy-framework"
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
              <Link href="/dashboard" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Medical Dashboard
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
