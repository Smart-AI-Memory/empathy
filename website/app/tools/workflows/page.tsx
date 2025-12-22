import { Metadata } from 'next';
import Link from 'next/link';
import WorkflowDashboard from '@/components/workflows/WorkflowDashboard';

export const metadata: Metadata = {
  title: 'Multi-Model Workflow Dashboard | Empathy Framework',
  description:
    'Monitor and analyze cost-optimized multi-model workflows. Track savings from 3-tier model routing with Haiku, Sonnet, and Opus.',
  keywords: [
    'multi-model',
    'workflow',
    'cost optimization',
    'LLM routing',
    'model tiers',
    'AI costs',
    'Claude',
    'GPT',
  ],
  openGraph: {
    title: 'Multi-Model Workflow Dashboard | Empathy Framework',
    description:
      'Track cost savings from intelligent model routing. Optimize AI spend with 3-tier workflows.',
    type: 'website',
  },
};

export default function WorkflowsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <Link href="/" className="flex items-center gap-3 hover:opacity-80">
                <span className="text-2xl font-bold">W</span>
                <div>
                  <h1 className="text-xl font-bold">Empathy Framework</h1>
                  <p className="text-white/80 text-sm">Multi-Model Workflows</p>
                </div>
              </Link>
            </div>
            <nav className="flex items-center gap-6">
              <Link href="/docs" className="text-white/80 hover:text-white text-sm">
                Docs
              </Link>
              <Link href="/tools/debug-wizard" className="text-white/80 hover:text-white text-sm">
                Debug Wizard
              </Link>
              <Link
                href="/docs/installation"
                className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-medium"
              >
                Get Started
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white pb-12 pt-6">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold mb-2">Workflow Dashboard</h2>
          <p className="text-white/80 max-w-2xl">
            Monitor your multi-model workflows. Track cost savings from intelligent 3-tier
            routing: cheap models for summarization, capable for analysis, premium for synthesis.
          </p>
          <div className="mt-6 flex gap-3">
            <div className="bg-white/10 rounded-lg px-4 py-2">
              <span className="text-sm text-white/60">Cheap Tier</span>
              <p className="font-semibold">Haiku / GPT-4o-mini</p>
            </div>
            <div className="bg-white/10 rounded-lg px-4 py-2">
              <span className="text-sm text-white/60">Capable Tier</span>
              <p className="font-semibold">Sonnet / GPT-4o</p>
            </div>
            <div className="bg-white/10 rounded-lg px-4 py-2">
              <span className="text-sm text-white/60">Premium Tier</span>
              <p className="font-semibold">Opus 4.5 / GPT-5.2</p>
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard */}
      <main className="max-w-6xl mx-auto px-4 py-8 -mt-4">
        <WorkflowDashboard />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              Empathy Framework - Cost-optimized AI workflows
            </p>
            <div className="flex gap-6">
              <Link href="/docs" className="text-sm text-gray-500 hover:text-gray-700">
                Documentation
              </Link>
              <Link href="https://github.com/Smart-AI-Memory/empathy-framework" className="text-sm text-gray-500 hover:text-gray-700">
                GitHub
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
