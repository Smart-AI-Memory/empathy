import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import GitHubStarsBadge from '@/components/GitHubStarsBadge';
import TestsBadge from '@/components/TestsBadge';

const features = [
  {
    icon: '⚡',
    title: '10 Integrated Workflows',
    description: 'Research topics deeply, review code for bugs and style, debug errors with context, refactor safely, generate tests, write docs, scan for vulnerabilities, optimize performance, explain complex code, and get daily briefings—all from your IDE.',
    link: '/workflows',
  },
  {
    icon: '🤖',
    title: '20+ Specialized Agents',
    description: 'Pre-built agent crews for code review, security audits, health checks, and refactoring. Built with Agent Factory for LangGraph, CrewAI, and more.',
    link: '/framework-docs/',
  },
  {
    icon: '🎛️',
    title: 'VSCode Dashboard',
    description: 'Real-time health scores, cost tracking, workflow monitoring, and quick actions. See your AI collaboration at a glance.',
    link: '/framework-docs/',
  },
  {
    icon: '🧠',
    title: 'Long-Term Memory',
    description: 'Your AI remembers patterns, decisions, and context across sessions. No more repeating yourself.',
    link: '/framework-docs/',
  },
  {
    icon: '🔌',
    title: 'Multi-Provider Support',
    description: 'Works with Anthropic, OpenAI, Gemini, and Ollama. Smart tier routing saves 80-96% on costs.',
    link: '/framework-docs/',
  },
  {
    icon: '🔒',
    title: 'Enterprise Security',
    description: 'Built-in PII scrubbing, secrets detection, and audit logging. SOC2 and HIPAA-ready.',
    link: '/framework-docs/',
  },
  {
    icon: '🧙',
    title: '44+ AI Wizards',
    description: 'Pre-built, specialized AI assistants for debugging, code review, security scanning, refactoring, and more.',
    link: '/wizards',
  },
];

const codeExample = `from empathy_os import EmpathyLLM
from empathy_os.workflows import ResearchWorkflow, DebugWorkflow

# Initialize with smart tier routing (80-96% cost savings)
llm = EmpathyLLM(provider="anthropic")

# Run a research workflow
research = ResearchWorkflow(llm)
result = await research.run(
    topic="WebSocket authentication patterns",
    depth="comprehensive"
)

# Or debug with full context
debug = DebugWorkflow(llm)
fix = await debug.analyze(error_log, project_context="React app")

print(fix.root_cause)
print(fix.suggested_fix)`;


export default function Home() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-20 sm:py-28" aria-label="Hero">
          <div className="absolute inset-0" aria-hidden="true">
            <div className="absolute inset-0 bg-gradient-to-br from-[var(--primary)] via-transparent to-[var(--secondary)] opacity-5" />
          </div>
          <div className="container relative">
            <div className="max-w-4xl mx-auto text-center animate-fade-in">
              {/* Credibility Badges */}
              <div className="flex flex-wrap gap-3 justify-center mb-8">
                <GitHubStarsBadge />
                <TestsBadge />
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[var(--border)] text-sm font-medium">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  v3.5.6 Stable
                </span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
                AI Framework for{' '}
                <span className="text-gradient">Production Apps</span>
              </h1>
              <p className="text-xl text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto">
                10 integrated workflows, 20+ specialized agents, VSCode dashboard, and multi-provider support.
                Agent Factory uses CrewAI and LangGraph by default—build smarter AI features in a fraction of the time.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link
                  href="/framework-docs/tutorials/quickstart/"
                  className="btn btn-primary text-lg px-8 py-4"
                  aria-label="Get started with the framework"
                >
                  pip install empathy-framework
                </Link>
                <Link
                  href="/workflows"
                  className="btn btn-outline text-lg px-8 py-4"
                  aria-label="Explore Workflows"
                >
                  Explore Workflows
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Code Example */}
        <section className="py-16 bg-[var(--border)] bg-opacity-30" aria-label="Code example">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold text-center mb-8">
                Get Started in 5 Lines of Code
              </h2>
              <div className="bg-[#1e1e1e] rounded-xl overflow-hidden shadow-2xl">
                <div className="flex items-center gap-2 px-4 py-3 bg-[#2d2d2d] border-b border-[#3d3d3d]">
                  <div className="w-3 h-3 rounded-full bg-[#ff5f56]"></div>
                  <div className="w-3 h-3 rounded-full bg-[#ffbd2e]"></div>
                  <div className="w-3 h-3 rounded-full bg-[#27ca40]"></div>
                  <span className="ml-2 text-sm text-gray-400">main.py</span>
                </div>
                <pre className="p-6 overflow-x-auto text-sm">
                  <code className="text-gray-300">{codeExample}</code>
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-20" aria-label="Features">
          <div className="container">
            <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
              Everything You Need for Production AI
            </h2>
            <p className="text-center text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
              Stop building AI infrastructure from scratch. Focus on your product.
            </p>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {features.map((feature) => (
                <Link
                  key={feature.title}
                  href={feature.link}
                  className="group bg-[var(--background)] p-6 rounded-xl border-2 border-[var(--border)] hover:border-[var(--primary)] hover:shadow-lg transition-all"
                >
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-bold mb-2 group-hover:text-[var(--primary)] transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    {feature.description}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        </section>


        {/* Case Study Teaser */}
        <section className="py-20" aria-label="Case study">
          <div className="container">
            <div className="max-w-4xl mx-auto bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] rounded-2xl p-8 md:p-12 text-white">
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="flex-1">
                  <p className="text-sm font-medium opacity-80 mb-2">CASE STUDY</p>
                  <h3 className="text-2xl md:text-3xl font-bold mb-4">
                    Healthcare AI in Production
                  </h3>
                  <p className="opacity-90 mb-6">
                    See how we built 14+ HIPAA-compliant clinical AI tools using Empathy Framework,
                    including automated SBAR reports and diagnostic assistance.
                  </p>
                  <a
                    href="https://healthcare.smartaimemory.com/static/dashboard.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 bg-white text-[var(--primary)] px-6 py-3 rounded-lg font-medium hover:bg-opacity-90 transition-colors"
                  >
                    View Live Demo
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                      <polyline points="15 3 21 3 21 9" />
                      <line x1="10" y1="14" x2="21" y2="3" />
                    </svg>
                  </a>
                </div>
                <div className="flex-shrink-0">
                  <div className="w-32 h-32 md:w-40 md:h-40 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center">
                    <span className="text-6xl md:text-7xl">🏥</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 bg-[var(--border)] bg-opacity-30" aria-label="Call to action">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Ready to Build Smarter AI?
              </h2>
              <p className="text-xl text-[var(--text-secondary)] mb-8">
                Join developers shipping production AI with Empathy Framework.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/framework-docs/tutorials/quickstart/"
                  className="btn btn-primary text-lg px-8 py-4"
                >
                  Read the Docs
                </Link>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline text-lg px-8 py-4"
                >
                  Star on GitHub
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
