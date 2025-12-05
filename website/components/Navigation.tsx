'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useTheme } from '@/lib/theme-provider';

export default function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { setTheme, resolvedTheme } = useTheme();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-[var(--background)] backdrop-blur-md bg-opacity-90 border-b border-[var(--border)] shadow-sm'
          : 'bg-transparent'
      }`}
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="container">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            href="/"
            className="text-xl font-bold text-gradient hover:opacity-80 transition-opacity"
            aria-label="SmartAI Memory Home"
          >
            SmartAI Memory
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <Link
              href="/framework"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Framework
            </Link>
            <Link
              href="/pricing"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Pricing
            </Link>
            <Link
              href="/blog"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Blog
            </Link>
            <Link
              href="/framework-docs/"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Docs
            </Link>
            <a
              href="https://healthcare.smartaimemory.com/static/dashboard.html"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Healthcare Wizards
            </a>
            <a
              href="https://wizards.smartaimemory.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Dev Wizards
            </a>
            <Link
              href="/plugins"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Plugins
            </Link>
            <Link
              href="/faq"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              FAQ
            </Link>
            <Link
              href="/contact"
              className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
            >
              Contact
            </Link>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-[var(--border)] transition-colors"
              aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
              title={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {resolvedTheme === 'dark' ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="5" />
                  <line x1="12" y1="1" x2="12" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="23" />
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                  <line x1="1" y1="12" x2="3" y2="12" />
                  <line x1="21" y1="12" x2="23" y2="12" />
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              )}
            </button>

            {/* GitHub Link */}
            <a
              href="https://github.com/Smart-AI-Memory/empathy-framework"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg hover:bg-[var(--border)] transition-colors"
              aria-label="View Empathy Framework on GitHub"
              title="View on GitHub"
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

            {/* CTA Button */}
            <Link href="/framework" className="btn btn-primary text-sm">
              Get Started
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-[var(--border)] transition-colors"
            aria-label="Toggle mobile menu"
            aria-expanded={isMobileMenuOpen}
          >
            {isMobileMenuOpen ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-[var(--border)]">
            <div className="flex flex-col space-y-4">
              <Link
                href="/framework"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Framework
              </Link>
              <Link
                href="/pricing"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Pricing
              </Link>
              <Link
                href="/blog"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Blog
              </Link>
              <Link
                href="/framework-docs/"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Docs
              </Link>
              <a
                href="https://healthcare.smartaimemory.com/static/dashboard.html"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Healthcare Wizards
              </a>
              <a
                href="https://wizards.smartaimemory.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Dev Wizards
              </a>
              <Link
                href="/plugins"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Plugins
              </Link>
              <Link
                href="/faq"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                FAQ
              </Link>
              <Link
                href="/contact"
                className="text-sm font-medium hover:text-[var(--primary)] transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Contact
              </Link>
              <div className="flex items-center gap-4 pt-4 border-t border-[var(--border)]">
                <button
                  onClick={toggleTheme}
                  className="flex items-center gap-2 text-sm font-medium"
                  aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
                >
                  {resolvedTheme === 'dark' ? '☀️ Light' : '🌙 Dark'} Mode
                </button>
              </div>
              <Link
                href="/framework"
                className="btn btn-primary text-sm w-full"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Get Started
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
