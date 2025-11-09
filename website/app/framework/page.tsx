import Link from 'next/link';

export default function FrameworkPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <nav className="border-b border-[var(--border)] py-4">
        <div className="container flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gradient">
            Empathy Framework
          </Link>
          <div className="flex gap-6">
            <Link href="/book" className="text-sm hover:text-[var(--primary)]">Book</Link>
            <Link href="/docs" className="text-sm hover:text-[var(--primary)]">Docs</Link>
            <Link href="/plugins" className="text-sm hover:text-[var(--primary)]">Plugins</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              Empathy Framework <span className="text-gradient">Core</span>
            </h1>
            <p className="text-2xl text-[var(--text-secondary)] mb-8">
              Fair Source foundation for building Level 4 Anticipatory AI systems
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://github.com/Smart-AI-Memory/empathy"
                className="btn btn-primary"
                target="_blank"
                rel="noopener noreferrer"
              >
                View on GitHub
              </a>
              <Link href="/docs" className="btn btn-outline">
                Read Documentation
              </Link>
            </div>
            <p className="mt-6 text-sm text-[var(--muted)]">
              Fair Source License 0.9 • Free for Students & Small Teams • Community Driven
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <h2 className="text-4xl font-bold text-center mb-12">Core Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-[var(--background)] p-6 rounded-lg">
              <div className="text-3xl mb-4">🧠</div>
              <h3 className="text-xl font-bold mb-3">5-Level Empathy System</h3>
              <p className="text-[var(--text-secondary)]">
                Built-in framework for creating AI that progresses from reactive to anticipatory intelligence.
              </p>
            </div>

            <div className="bg-[var(--background)] p-6 rounded-lg">
              <div className="text-3xl mb-4">🔌</div>
              <h3 className="text-xl font-bold mb-3">Plugin Architecture</h3>
              <p className="text-[var(--text-secondary)]">
                Extensible system for building domain-specific wizards and tools.
              </p>
            </div>

            <div className="bg-[var(--background)] p-6 rounded-lg">
              <div className="text-3xl mb-4">📊</div>
              <h3 className="text-xl font-bold mb-3">Pattern Recognition</h3>
              <p className="text-[var(--text-secondary)]">
                Advanced pattern matching and analysis for identifying trends and trajectories.
              </p>
            </div>

            <div className="bg-[var(--background)] p-6 rounded-lg">
              <div className="text-3xl mb-4">🔮</div>
              <h3 className="text-xl font-bold mb-3">Trajectory Prediction</h3>
              <p className="text-[var(--text-secondary)]">
                Core algorithms for predicting future states based on current trajectories.
              </p>
            </div>

            <div className="bg-[var(--background)] p-6 rounded-lg">
              <div className="text-3xl mb-4">⚡</div>
              <h3 className="text-xl font-bold mb-3">Async-First Design</h3>
              <p className="text-[var(--text-secondary)]">
                Built for modern Python with async/await support throughout.
              </p>
            </div>

            <div className="bg-[var(--background)] p-6 rounded-lg">
              <div className="text-3xl mb-4">🧪</div>
              <h3 className="text-xl font-bold mb-3">Fully Tested</h3>
              <p className="text-[var(--text-secondary)]">
                Comprehensive test coverage with pytest and type hints throughout.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-center mb-12">Quick Start</h2>

            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-bold mb-4">Installation</h3>
                <pre className="bg-[var(--foreground)] text-[var(--background)] p-4 rounded-lg overflow-x-auto">
                  <code>pip install empathy</code>
                </pre>
              </div>

              <div>
                <h3 className="text-2xl font-bold mb-4">Basic Usage</h3>
                <pre className="bg-[var(--foreground)] text-[var(--background)] p-6 rounded-lg overflow-x-auto text-sm">
{`from empathy_framework import BaseWizard

class MyWizard(BaseWizard):
    @property
    def name(self) -> str:
        return "My Custom Wizard"

    @property
    def level(self) -> int:
        return 4  # Level 4: Anticipatory

    async def analyze(self, context):
        # Your anticipatory logic here
        predictions = self.predict_future_issues(context)
        recommendations = self.generate_recommendations(predictions)

        return {
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": 0.85
        }

# Use your wizard
wizard = MyWizard()
result = await wizard.analyze({"data": your_data})`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="py-20 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-center mb-12">Architecture</h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-2xl font-bold mb-4">Core Components</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--primary)] font-mono text-sm mt-1">BaseWizard</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Abstract base class for all wizards
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--primary)] font-mono text-sm mt-1">PatternLibrary</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Pattern recognition and matching
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--primary)] font-mono text-sm mt-1">TrajectoryAnalyzer</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Trend analysis and prediction
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--primary)] font-mono text-sm mt-1">ContextManager</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Context handling and state management
                    </span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-2xl font-bold mb-4">Plugin System</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--secondary)] font-mono text-sm mt-1">PluginRegistry</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Discover and load plugins
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--secondary)] font-mono text-sm mt-1">WizardFactory</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Create wizard instances
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--secondary)] font-mono text-sm mt-1">ConfigManager</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Plugin configuration and settings
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--secondary)] font-mono text-sm mt-1">HookSystem</span>
                    <span className="text-[var(--text-secondary)] text-sm">
                      Event hooks and callbacks
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Community */}
      <section className="py-20">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">Join the Community</h2>
            <p className="text-xl text-[var(--text-secondary)] mb-12">
              The Empathy Framework is Fair Source licensed and welcomes contributions from developers worldwide.
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              <a
                href="https://github.com/Smart-AI-Memory/empathy"
                className="p-6 border-2 border-[var(--border)] rounded-lg hover:border-[var(--primary)] transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="text-3xl mb-3">💻</div>
                <h3 className="text-lg font-bold mb-2">Contribute on GitHub</h3>
                <p className="text-sm text-[var(--text-secondary)]">
                  Submit PRs, report issues, or help improve the docs
                </p>
              </a>

              <a
                href="https://github.com/Smart-AI-Memory/empathy/issues"
                className="p-6 border-2 border-[var(--border)] rounded-lg hover:border-[var(--primary)] transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="text-3xl mb-3">💬</div>
                <h3 className="text-lg font-bold mb-2">Get Support</h3>
                <p className="text-sm text-[var(--text-secondary)]">
                  Ask questions and get help from the community
                </p>
              </a>

              <Link
                href="/book"
                className="p-6 border-2 border-[var(--border)] rounded-lg hover:border-[var(--primary)] transition-colors"
              >
                <div className="text-3xl mb-3">📚</div>
                <h3 className="text-lg font-bold mb-2">Get the Book</h3>
                <p className="text-sm text-[var(--text-secondary)]">
                  Learn to build commercial-grade plugins
                </p>
              </Link>
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
              <Link href="/book" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Book
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
