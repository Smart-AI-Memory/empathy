import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className="border-t border-[var(--border)] bg-[var(--background)]"
      role="contentinfo"
    >
      <div className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Column */}
          <div className="md:col-span-1">
            <Link
              href="/"
              className="text-xl font-bold text-gradient hover:opacity-80 transition-opacity"
            >
              Smart AI Memory
            </Link>
            <p className="mt-4 text-sm text-[var(--text-secondary)]">
              Building the future of AI-human collaboration with production-ready frameworks.
            </p>
            <div className="flex gap-4 mt-4">
              <a
                href="https://github.com/Smart-AI-Memory"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--muted)] hover:text-[var(--primary)] transition-colors"
                aria-label="GitHub Organization"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Products Column */}
          <div>
            <h3 className="font-bold text-sm uppercase tracking-wide mb-4">Products</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/framework"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Empathy Framework
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/Smart-AI-Memory/MemDocs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  MemDocs
                </a>
              </li>
              <li>
                <Link
                  href="/plugins"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Plugins
                </Link>
              </li>
              <li>
                <Link
                  href="/pricing"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Pricing
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources Column */}
          <div>
            <h3 className="font-bold text-sm uppercase tracking-wide mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/docs"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Documentation
                </Link>
              </li>
              <li>
                <Link
                  href="/faq"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  FAQ
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework/discussions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Community
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Bug Reports
                </a>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h3 className="font-bold text-sm uppercase tracking-wide mb-4">Company</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/contact"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Contact
                </Link>
              </li>
              <li>
                <Link
                  href="/book"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Book
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework/blob/main/LICENSE-FAIR-SOURCE.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Fair Source License
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework/blob/main/LICENSE-COMMERCIAL.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors"
                >
                  Commercial License
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-[var(--border)] flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-[var(--muted)] text-center md:text-left">
            © {currentYear} Deep Study AI, LLC. All rights reserved.
          </div>
          <div className="flex gap-6 text-xs text-[var(--muted)]">
            <Link href="/privacy" className="hover:text-[var(--primary)] transition-colors">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-[var(--primary)] transition-colors">
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
