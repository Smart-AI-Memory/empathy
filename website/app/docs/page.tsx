'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function DocsPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to comprehensive documentation after 500ms
    const timer = setTimeout(() => {
      router.push('/framework-docs/index.html');
    }, 500);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="container max-w-2xl mx-auto text-center px-6">
        <div className="mb-8">
          <div className="text-6xl mb-6">📚</div>
          <h1 className="text-4xl font-bold mb-4">
            Empathy Framework Documentation
          </h1>
          <p className="text-xl text-[var(--text-secondary)] mb-8">
            Redirecting to comprehensive documentation...
          </p>
        </div>

        <Link
          href="/framework-docs/index.html"
          className="inline-flex items-center gap-2 px-8 py-4 bg-[var(--primary)] text-white rounded-lg hover:opacity-90 transition-all font-bold text-lg"
        >
          View Documentation Now
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>

        <p className="mt-6 text-sm text-[var(--muted)]">
          Version 1.8.0-beta • 45+ Specialized Wizards
        </p>
      </div>
    </div>
  );
}
