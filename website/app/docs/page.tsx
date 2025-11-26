'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function DocsRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the new documentation after a short delay
    const timer = setTimeout(() => {
      router.push('/framework-docs/');
    }, 500);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
      <div className="container max-w-2xl text-center">
        <div className="mb-8">
          <div className="text-6xl mb-4">📚</div>
          <h1 className="text-4xl font-bold mb-4">Documentation Moved</h1>
          <p className="text-xl text-[var(--text-secondary)] mb-6">
            Our documentation has been upgraded to a comprehensive MkDocs site with 45+ wizard guides.
          </p>
          <p className="text-[var(--text-secondary)] mb-8">
            Redirecting you to the new documentation...
          </p>
        </div>

        <div className="space-y-4">
          <Link
            href="/framework-docs/"
            className="inline-flex items-center gap-2 px-8 py-4 bg-[var(--primary)] text-white rounded-lg hover:bg-opacity-90 transition-all font-semibold text-lg"
          >
            Go to Documentation Now
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>

          <div>
            <Link
              href="/"
              className="text-sm text-[var(--muted)] hover:text-[var(--primary)] transition-colors"
            >
              ← Return to Home
            </Link>
          </div>
        </div>

        <div className="mt-12 p-6 bg-[var(--border)] bg-opacity-20 rounded-lg text-left">
          <h3 className="font-bold mb-3">What's New in the Documentation:</h3>
          <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
            <li className="flex items-start gap-2">
              <span className="text-[var(--success)] mt-1">✓</span>
              <span><strong>45+ Wizard Guides</strong> - Comprehensive documentation for all wizards</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--success)] mt-1">✓</span>
              <span><strong>Healthcare Section</strong> - 18 HIPAA-compliant wizards with clinical examples</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--success)] mt-1">✓</span>
              <span><strong>Software Development</strong> - 12 wizards for debugging, testing, and security</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--success)] mt-1">✓</span>
              <span><strong>Searchable</strong> - Full-text search across all documentation</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--success)] mt-1">✓</span>
              <span><strong>Navigation</strong> - Improved table of contents and cross-references</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
