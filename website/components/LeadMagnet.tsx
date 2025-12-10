'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function LeadMagnet() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');

    try {
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: 'lead_magnet' }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setMessage('Check your inbox for the guide!');
        setEmail('');
      } else {
        setStatus('error');
        setMessage(data.error || 'Something went wrong');
      }
    } catch {
      setStatus('error');
      setMessage('Failed to submit. Please try again.');
    }
  };

  return (
    <section className="py-20 gradient-primary text-white">
      <div className="container">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Get the Level 4 Patterns Guide
          </h2>
          <p className="text-lg opacity-90 mb-8">
            7 essential patterns for building anticipatory AI systems — free.
          </p>

          {status === 'success' ? (
            <div className="bg-white rounded-lg p-6">
              <div className="text-2xl mb-2">🎉</div>
              <p className="text-lg font-medium" style={{ color: '#0F172A' }}>{message}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 justify-center max-w-md mx-auto">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                disabled={status === 'loading'}
                className="flex-1 px-4 py-3 rounded-lg bg-white
                           placeholder:text-gray-400 focus:ring-2 focus:ring-white focus:ring-opacity-50
                           outline-none disabled:opacity-50"
                style={{ color: '#0F172A' }}
              />
              <button
                type="submit"
                disabled={status === 'loading'}
                className="px-6 py-3 bg-white rounded-lg font-semibold
                           hover:bg-opacity-90 transition-colors disabled:opacity-50 whitespace-nowrap"
                style={{ color: '#2563EB' }}
              >
                {status === 'loading' ? 'Sending...' : 'Download Free Guide'}
              </button>
            </form>
          )}

          {status === 'error' && (
            <p className="mt-4 text-red-200">{message}</p>
          )}

          <p className="mt-6 text-sm">
            Or{' '}
            <Link
              href="https://smart-ai-memory.github.io/memdocs-empathy-book/chapters/part-6/23-distributed-memory.html"
              target="_blank"
              rel="noopener noreferrer"
              className="underline font-semibold hover:text-yellow-200"
              style={{ color: '#FEF08A' }}
            >
              read Chapter 23 free →
            </Link>
          </p>
        </div>
      </div>
    </section>
  );
}
