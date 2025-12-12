import type { Metadata } from 'next';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { generateMetadata } from '@/lib/metadata';
import CheckoutButton from '@/components/CheckoutButton';

export const metadata: Metadata = generateMetadata({
  title: 'Support Empathy Development',
  description: 'Support the ongoing development of Empathy. Every contribution helps make anticipatory AI accessible to everyone.',
  url: 'https://smartaimemory.com/contribute',
});

// Price IDs from Stripe Dashboard - update after creating products
const CONTRIB_5_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_PRICE_CONTRIB_5 || 'price_contrib_5_placeholder';
const CONTRIB_25_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_PRICE_CONTRIB_25 || 'price_contrib_25_placeholder';
const CONTRIB_100_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_PRICE_CONTRIB_100 || 'price_contrib_100_placeholder';
const CONTRIB_500_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_PRICE_CONTRIB_500 || 'price_contrib_500_placeholder';

export default function ContributePage() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-5xl font-bold mb-6">
                Support Empathy Development
              </h1>
              <p className="text-2xl mb-8 opacity-90">
                Help us build the future of anticipatory AI. Every contribution makes a difference.
              </p>
            </div>
          </div>
        </section>

        {/* Contribution Tiers */}
        <section className="py-20">
          <div className="container">
            <div className="max-w-5xl mx-auto">
              <h2 className="text-3xl font-bold text-center mb-12">
                Support Tiers
              </h2>

              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Coffee Supporter */}
                <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-6 hover:border-[var(--primary)] transition-all">
                  <div className="text-center mb-6">
                    <div className="text-4xl mb-3">☕</div>
                    <h3 className="text-xl font-bold mb-2">Coffee Supporter</h3>
                    <div className="mb-4">
                      <span className="text-4xl font-bold">$5</span>
                    </div>
                  </div>
                  <ul className="space-y-2 mb-6 text-sm text-[var(--text-secondary)]">
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Our heartfelt thanks</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Sponsor badge on GitHub</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Early release notifications</span>
                    </li>
                  </ul>
                  <CheckoutButton
                    priceId={CONTRIB_5_PRICE_ID}
                    mode="payment"
                    buttonText="Contribute $5"
                    className="btn btn-outline w-full"
                  />
                </div>

                {/* Star Supporter */}
                <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-6 hover:border-[var(--primary)] transition-all">
                  <div className="text-center mb-6">
                    <div className="text-4xl mb-3">⭐</div>
                    <h3 className="text-xl font-bold mb-2">Star Supporter</h3>
                    <div className="mb-4">
                      <span className="text-4xl font-bold">$25</span>
                    </div>
                  </div>
                  <ul className="space-y-2 mb-6 text-sm text-[var(--text-secondary)]">
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Everything in Coffee tier</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Name in README sponsors</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Access to sponsor-only updates</span>
                    </li>
                  </ul>
                  <CheckoutButton
                    priceId={CONTRIB_25_PRICE_ID}
                    mode="payment"
                    buttonText="Contribute $25"
                    className="btn btn-outline w-full"
                  />
                </div>

                {/* Rocket Supporter - Featured */}
                <div className="bg-[var(--background)] border-2 border-[var(--accent)] rounded-lg p-6 relative shadow-lg">
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-[var(--accent)] text-white px-3 py-1 rounded-full text-xs font-bold">
                      Popular
                    </span>
                  </div>
                  <div className="text-center mb-6">
                    <div className="text-4xl mb-3">🚀</div>
                    <h3 className="text-xl font-bold mb-2">Rocket Supporter</h3>
                    <div className="mb-4">
                      <span className="text-4xl font-bold">$100</span>
                    </div>
                  </div>
                  <ul className="space-y-2 mb-6 text-sm text-[var(--text-secondary)]">
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Everything in Star tier</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Priority issue handling</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Logo on website sponsors</span>
                    </li>
                  </ul>
                  <CheckoutButton
                    priceId={CONTRIB_100_PRICE_ID}
                    mode="payment"
                    buttonText="Contribute $100"
                    className="btn btn-primary w-full"
                  />
                </div>

                {/* Diamond Supporter */}
                <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-6 hover:border-[var(--primary)] transition-all">
                  <div className="text-center mb-6">
                    <div className="text-4xl mb-3">💎</div>
                    <h3 className="text-xl font-bold mb-2">Diamond Supporter</h3>
                    <div className="mb-4">
                      <span className="text-4xl font-bold">$500</span>
                    </div>
                  </div>
                  <ul className="space-y-2 mb-6 text-sm text-[var(--text-secondary)]">
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Everything in Rocket tier</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Monthly video call</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[var(--success)]">✓</span>
                      <span>Direct roadmap input</span>
                    </li>
                  </ul>
                  <CheckoutButton
                    priceId={CONTRIB_500_PRICE_ID}
                    mode="payment"
                    buttonText="Contribute $500"
                    className="btn btn-outline w-full"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How Your Support Helps */}
        <section className="py-20 bg-[var(--border)] bg-opacity-30">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold text-center mb-12">
                How Your Support Helps
              </h2>

              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="text-4xl mb-4">💻</div>
                  <h3 className="text-xl font-bold mb-3">Full-Time Development</h3>
                  <p className="text-[var(--text-secondary)]">
                    Your support enables dedicated work on the framework, faster releases, and better features.
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-4xl mb-4">📚</div>
                  <h3 className="text-xl font-bold mb-3">Better Documentation</h3>
                  <p className="text-[var(--text-secondary)]">
                    More examples, tutorials, and guides to help developers succeed with anticipatory AI.
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-4xl mb-4">🛡️</div>
                  <h3 className="text-xl font-bold mb-3">Security & Quality</h3>
                  <p className="text-[var(--text-secondary)]">
                    Professional security audits, comprehensive testing, and enterprise-grade reliability.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Alternative Ways to Support */}
        <section className="py-20">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-8">
                Other Ways to Support
              </h2>
              <div className="grid md:grid-cols-3 gap-8">
                <div className="p-6 bg-[var(--border)] bg-opacity-30 rounded-lg">
                  <div className="text-3xl mb-3">⭐</div>
                  <h3 className="font-bold mb-2">Star on GitHub</h3>
                  <p className="text-sm text-[var(--text-secondary)] mb-4">
                    Help others discover the framework
                  </p>
                  <a
                    href="https://github.com/Smart-AI-Memory/empathy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline btn-sm"
                  >
                    Star Repository
                  </a>
                </div>
                <div className="p-6 bg-[var(--border)] bg-opacity-30 rounded-lg">
                  <div className="text-3xl mb-3">🐛</div>
                  <h3 className="font-bold mb-2">Report Issues</h3>
                  <p className="text-sm text-[var(--text-secondary)] mb-4">
                    Help improve quality by reporting bugs
                  </p>
                  <a
                    href="https://github.com/Smart-AI-Memory/empathy/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline btn-sm"
                  >
                    Report Issue
                  </a>
                </div>
                <div className="p-6 bg-[var(--border)] bg-opacity-30 rounded-lg">
                  <div className="text-3xl mb-3">📣</div>
                  <h3 className="font-bold mb-2">Spread the Word</h3>
                  <p className="text-sm text-[var(--text-secondary)] mb-4">
                    Share with your network and community
                  </p>
                  <Link href="/contact" className="btn btn-outline btn-sm">
                    Contact Us
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Thank You */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-2xl mx-auto text-center">
              <h2 className="text-4xl font-bold mb-6">Thank You</h2>
              <p className="text-xl opacity-90">
                Every contribution, whether financial or through community involvement,
                helps make anticipatory AI accessible to developers everywhere.
                We&apos;re grateful for your support.
              </p>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
