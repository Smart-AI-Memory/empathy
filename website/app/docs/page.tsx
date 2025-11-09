import Link from 'next/link';

export default function DocsPage() {
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
            <Link href="/book" className="text-sm hover:text-[var(--primary)]">Book</Link>
            <Link href="/plugins" className="text-sm hover:text-[var(--primary)]">Plugins</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-12 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <h1 className="text-4xl font-bold mb-4">Documentation</h1>
          <p className="text-xl text-[var(--text-secondary)]">
            Complete guide to building with the Empathy Framework
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="py-12">
        <div className="container">
          <div className="grid lg:grid-cols-4 gap-12">
            {/* Sidebar */}
            <aside className="lg:col-span-1">
              <nav className="sticky top-4 space-y-6">
                <div>
                  <h3 className="font-bold mb-3 text-sm uppercase text-[var(--muted)]">Getting Started</h3>
                  <ul className="space-y-2">
                    <li><a href="#introduction" className="text-sm hover:text-[var(--primary)]">Introduction</a></li>
                    <li><a href="#installation" className="text-sm hover:text-[var(--primary)]">Installation</a></li>
                    <li><a href="#quickstart" className="text-sm hover:text-[var(--primary)]">Quick Start</a></li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-bold mb-3 text-sm uppercase text-[var(--muted)]">Core Concepts</h3>
                  <ul className="space-y-2">
                    <li><a href="#levels" className="text-sm hover:text-[var(--primary)]">5 Levels of Empathy</a></li>
                    <li><a href="#wizards" className="text-sm hover:text-[var(--primary)]">Wizards</a></li>
                    <li><a href="#patterns" className="text-sm hover:text-[var(--primary)]">Pattern Recognition</a></li>
                    <li><a href="#trajectories" className="text-sm hover:text-[var(--primary)]">Trajectory Analysis</a></li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-bold mb-3 text-sm uppercase text-[var(--muted)]">Plugins</h3>
                  <ul className="space-y-2">
                    <li><a href="#software" className="text-sm hover:text-[var(--primary)]">Software Development</a></li>
                    <li><a href="#healthcare" className="text-sm hover:text-[var(--primary)]">Healthcare</a></li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-bold mb-3 text-sm uppercase text-[var(--muted)]">API Reference</h3>
                  <ul className="space-y-2">
                    <li><a href="#base-wizard" className="text-sm hover:text-[var(--primary)]">BaseWizard</a></li>
                    <li><a href="#pattern-library" className="text-sm hover:text-[var(--primary)]">PatternLibrary</a></li>
                    <li><a href="#trajectory-analyzer" className="text-sm hover:text-[var(--primary)]">TrajectoryAnalyzer</a></li>
                  </ul>
                </div>
              </nav>
            </aside>

            {/* Main Content */}
            <main className="lg:col-span-3 prose prose-slate max-w-none">
              <section id="introduction" className="mb-12">
                <h2 className="text-3xl font-bold mb-4">Introduction</h2>
                <p className="text-[var(--text-secondary)] mb-4">
                  The Empathy Framework is an open-source Python framework for building AI systems that
                  can anticipate problems before they occur. Unlike traditional reactive AI, the framework
                  enables you to create Level 4 (Anticipatory) intelligence.
                </p>
                <p className="text-[var(--text-secondary)]">
                  This documentation covers the Core framework. For information on commercial plugins,
                  see the <Link href="/book" className="text-[var(--primary)]">book</Link>.
                </p>
              </section>

              <section id="installation" className="mb-12">
                <h2 className="text-3xl font-bold mb-4">Installation</h2>
                <p className="text-[var(--text-secondary)] mb-4">
                  Install the Empathy Framework using pip:
                </p>
                <pre className="bg-[var(--foreground)] text-[var(--background)] p-4 rounded-lg mb-4">
                  <code>pip install empathy</code>
                </pre>
                <p className="text-[var(--text-secondary)]">
                  Or install from source:
                </p>
                <pre className="bg-[var(--foreground)] text-[var(--background)] p-4 rounded-lg">
{`git clone https://github.com/Smart-AI-Memory/empathy.git
cd empathy
pip install -e .`}
                </pre>
              </section>

              <section id="quickstart" className="mb-12">
                <h2 className="text-3xl font-bold mb-4">Quick Start</h2>
                <p className="text-[var(--text-secondary)] mb-4">
                  Create your first wizard in 5 minutes:
                </p>
                <pre className="bg-[var(--foreground)] text-[var(--background)] p-6 rounded-lg mb-4 overflow-x-auto text-sm">
{`from empathy_framework import BaseWizard
from typing import Dict, Any

class SimpleWizard(BaseWizard):
    @property
    def name(self) -> str:
        return "Simple Prediction Wizard"

    @property
    def level(self) -> int:
        return 4  # Level 4: Anticipatory

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Analyze current state
        data = context.get('data', [])

        # Predict future issues
        predictions = self._predict_issues(data)

        # Generate recommendations
        recommendations = self._generate_recommendations(predictions)

        return {
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": 0.85
        }

    def _predict_issues(self, data):
        # Your prediction logic here
        return []

    def _generate_recommendations(self, predictions):
        # Your recommendation logic here
        return []

# Use the wizard
async def main():
    wizard = SimpleWizard()
    result = await wizard.analyze({
        'data': your_data
    })
    print(result)

import asyncio
asyncio.run(main())`}
                </pre>
              </section>

              <section id="levels" className="mb-12">
                <h2 className="text-3xl font-bold mb-4">The 5 Levels of Empathy</h2>
                <p className="text-[var(--text-secondary)] mb-6">
                  The framework is built around five levels of AI empathy:
                </p>

                <div className="space-y-4">
                  <div className="border-l-4 border-[var(--muted)] pl-4">
                    <h3 className="text-xl font-bold mb-2">Level 1: Reactive</h3>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Responds only when asked. Like a search engine or basic chatbot.
                    </p>
                  </div>

                  <div className="border-l-4 border-[var(--muted)] pl-4">
                    <h3 className="text-xl font-bold mb-2">Level 2: Helpful</h3>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Offers suggestions based on immediate context. Like code completion.
                    </p>
                  </div>

                  <div className="border-l-4 border-[var(--muted)] pl-4">
                    <h3 className="text-xl font-bold mb-2">Level 3: Proactive</h3>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Notices patterns and offers improvements. Like advanced linters.
                    </p>
                  </div>

                  <div className="border-l-4 border-[var(--primary)] pl-4">
                    <h3 className="text-xl font-bold mb-2">Level 4: Anticipatory ⭐</h3>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Predicts future problems before they happen. This is the framework's focus.
                    </p>
                  </div>

                  <div className="border-l-4 border-[var(--muted)] pl-4">
                    <h3 className="text-xl font-bold mb-2">Level 5: Transformative</h3>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Reshapes workflows to prevent entire classes of problems. Future vision.
                    </p>
                  </div>
                </div>
              </section>

              <section id="wizards" className="mb-12">
                <h2 className="text-3xl font-bold mb-4">Wizards</h2>
                <p className="text-[var(--text-secondary)] mb-4">
                  Wizards are the core abstraction in the Empathy Framework. Each wizard implements
                  a specific type of anticipatory analysis.
                </p>

                <h3 className="text-2xl font-bold mb-3">BaseWizard</h3>
                <p className="text-[var(--text-secondary)] mb-4">
                  All wizards inherit from <code>BaseWizard</code>:
                </p>
                <pre className="bg-[var(--foreground)] text-[var(--background)] p-6 rounded-lg text-sm">
{`class BaseWizard(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Wizard name"""
        pass

    @property
    @abstractmethod
    def level(self) -> int:
        """Empathy level (1-5)"""
        pass

    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis and return predictions"""
        pass`}
                </pre>
              </section>

              <section id="software" className="mb-12">
                <h2 className="text-3xl font-bold mb-4">Software Development Plugin</h2>
                <p className="text-[var(--text-secondary)] mb-4">
                  The commercial Software Development Plugin includes three powerful wizards:
                </p>

                <div className="grid gap-4 mb-6">
                  <div className="bg-[var(--border)] bg-opacity-30 p-4 rounded-lg">
                    <h3 className="text-lg font-bold mb-2">Enhanced Testing Wizard</h3>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Predicts which untested code will cause bugs in production.
                    </p>
                  </div>

                  <div className="bg-[var(--border)] bg-opacity-30 p-4 rounded-lg">
                    <h3 className="text-lg font-bold mb-2">Performance Profiling Wizard</h3>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Forecasts performance degradation before it becomes critical.
                    </p>
                  </div>

                  <div className="bg-[var(--border)] bg-opacity-30 p-4 rounded-lg">
                    <h3 className="text-lg font-bold mb-2">Security Analysis Wizard</h3>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Identifies which vulnerabilities will actually be exploited.
                    </p>
                  </div>
                </div>

                <p className="text-[var(--text-secondary)]">
                  <Link href="/book" className="text-[var(--primary)]">Purchase the book</Link> to
                  get access to these plugins with 1 developer license.
                </p>
              </section>

              <section id="base-wizard" className="mb-12">
                <h2 className="text-3xl font-bold mb-4">API Reference: BaseWizard</h2>
                <p className="text-[var(--text-secondary)] mb-4">
                  Complete API reference for the BaseWizard class.
                </p>

                <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg">
                  <h3 className="text-lg font-bold mb-3">Properties</h3>
                  <ul className="space-y-3 text-sm">
                    <li>
                      <code className="text-[var(--primary)]">name: str</code>
                      <p className="text-[var(--text-secondary)] mt-1">The wizard's display name</p>
                    </li>
                    <li>
                      <code className="text-[var(--primary)]">level: int</code>
                      <p className="text-[var(--text-secondary)] mt-1">Empathy level (1-5)</p>
                    </li>
                  </ul>

                  <h3 className="text-lg font-bold mt-6 mb-3">Methods</h3>
                  <ul className="space-y-3 text-sm">
                    <li>
                      <code className="text-[var(--primary)]">async analyze(context: Dict[str, Any]) → Dict[str, Any]</code>
                      <p className="text-[var(--text-secondary)] mt-1">
                        Performs analysis on the provided context and returns predictions and recommendations.
                      </p>
                    </li>
                  </ul>
                </div>
              </section>

              <div className="mt-12 p-6 bg-[var(--primary)] bg-opacity-10 border-l-4 border-[var(--primary)] rounded-r-lg">
                <h3 className="text-xl font-bold mb-2">Ready to dive deeper?</h3>
                <p className="mb-4">
                  Get the book to learn how to build production-ready Level 4 systems with detailed
                  implementation examples and access to commercial plugins.
                </p>
                <Link href="/book" className="btn btn-primary">
                  Get the Book - $49
                </Link>
              </div>
            </main>
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
