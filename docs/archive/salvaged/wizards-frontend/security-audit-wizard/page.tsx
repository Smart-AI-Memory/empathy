'use client';

import Link from 'next/link';

export default function SecurityAuditWizardPage() {
  return (
    <div className="min-h-screen bg-dark text-white">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="mb-8">
          <Link href="/wizards" className="text-primary hover:text-primary/80 transition-colors mb-4 inline-block">
            ← Back to Wizards
          </Link>
          <h1 className="text-4xl font-bold mb-4 flex items-center gap-3">
            <span className="text-5xl">🔒</span>
            Security Audit Wizard
          </h1>
          <p className="text-xl text-gray-400">
            Identify and fix security vulnerabilities with OWASP Top 10 analysis.
          </p>
        </div>

        <div className="bg-gradient-to-br from-slate-900/50 to-gray-900/50 border border-slate-500/30 rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-4">
            <div className="text-4xl">🚧</div>
            <div>
              <h2 className="text-2xl font-bold mb-2">Coming Soon</h2>
              <p className="text-gray-300 mb-4">
                This wizard is currently under development. It will help you audit security with:
              </p>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>OWASP Top 10 vulnerability scanning</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Dependency security analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Authentication and authorization review</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Penetration testing guidelines</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Security best practices checklist</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-3">In the meantime...</h3>
          <p className="text-gray-400 mb-4">
            You can use our General Wizard to get AI assistance with security audits right now.
          </p>
          <Link
            href="/wizard"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white px-6 py-3 rounded-lg font-semibold transition-all"
          >
            <span>Use General Wizard</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}
