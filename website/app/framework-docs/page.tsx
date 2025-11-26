'use client';

import { useEffect } from 'react';

export default function FrameworkDocsRedirect() {
  useEffect(() => {
    // Redirect to the static HTML documentation
    window.location.href = '/framework-docs/index.html';
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <p className="text-xl text-[var(--text-secondary)]">
          Redirecting to documentation...
        </p>
      </div>
    </div>
  );
}
