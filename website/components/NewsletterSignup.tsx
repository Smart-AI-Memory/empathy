'use client';

import { useState, FormEvent } from 'react';

interface NewsletterSignupProps {
  inline?: boolean;
}

export default function NewsletterSignup({ inline = false }: NewsletterSignupProps) {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    setMessage('');

    try {
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setMessage(data.message || 'Successfully subscribed!');
        setEmail('');
      } else {
        setStatus('error');
        setMessage(data.error || 'Failed to subscribe. Please try again.');
      }
    } catch {
      setStatus('error');
      setMessage('Network error. Please try again.');
    }
  };

  if (inline) {
    return (
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
          disabled={status === 'loading' || status === 'success'}
          className="flex-1 px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none disabled:opacity-50"
          aria-label="Email address"
        />
        <button
          type="submit"
          disabled={status === 'loading' || status === 'success'}
          className="btn btn-primary whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'loading' && 'Subscribing...'}
          {status === 'success' && '✓ Subscribed!'}
          {status === 'idle' && 'Subscribe'}
          {status === 'error' && 'Try Again'}
        </button>
        {message && (
          <p
            className={`text-sm ${
              status === 'success' ? 'text-[var(--success)]' : 'text-[var(--error)]'
            }`}
          >
            {message}
          </p>
        )}
      </form>
    );
  }

  return (
    <div className="bg-[var(--border)] bg-opacity-30 rounded-lg p-8">
      <div className="max-w-2xl mx-auto text-center">
        <div className="text-4xl mb-4">📬</div>
        <h3 className="text-2xl font-bold mb-3">
          Stay Updated
        </h3>
        <p className="text-[var(--text-secondary)] mb-6">
          Get the latest updates on new features, releases, and AI development insights
          delivered to your inbox.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
            disabled={status === 'loading' || status === 'success'}
            className="flex-1 px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none disabled:opacity-50"
            aria-label="Email address"
          />
          <button
            type="submit"
            disabled={status === 'loading' || status === 'success'}
            className="btn btn-primary whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {status === 'loading' && 'Subscribing...'}
            {status === 'success' && '✓ Subscribed!'}
            {status === 'idle' && 'Subscribe'}
            {status === 'error' && 'Try Again'}
          </button>
        </form>

        {message && (
          <p
            className={`mt-4 text-sm ${
              status === 'success' ? 'text-[var(--success)]' : 'text-[var(--error)]'
            }`}
          >
            {message}
          </p>
        )}

        <p className="mt-4 text-xs text-[var(--muted)]">
          We respect your privacy. Unsubscribe at any time.
        </p>
      </div>
    </div>
  );
}
