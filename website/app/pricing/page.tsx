import type { Metadata } from 'next';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { generateMetadata } from '@/lib/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Pricing',
  description: 'Fair Source License 0.9 - Free for students & small teams. Commercial pricing for businesses with 6+ employees starting at $99/developer/year.',
  url: 'https://smartaimemory.com/pricing',
});

export default function PricingPage() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-5xl font-bold mb-6">
                Simple, Fair Pricing
              </h1>
              <p className="text-2xl mb-8 opacity-90">
                Fair Source License 0.9 — Free for students & small teams. Commercial for 6+ employees.
              </p>
            </div>
          </div>
        </section>

        {/* Pricing Tiers */}
        <section className="py-20">
          <div className="container">
            <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {/* Free Tier */}
              <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-8 hover:border-[var(--primary)] transition-all">
                <div className="text-center">
                  <h2 className="text-2xl font-bold mb-2">Free</h2>
                  <div className="mb-6">
                    <span className="text-5xl font-bold">$0</span>
                    <span className="text-[var(--muted)]">/forever</span>
                  </div>
                  <p className="text-[var(--text-secondary)] mb-6">
                    For students, educators, and teams with ≤5 employees
                  </p>
                </div>

                <div className="space-y-3 mb-8">
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Full Empathy Framework access</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">30+ production wizards</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Multi-LLM support</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Community support</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">GitHub access</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Fair Source License 0.9</span>
                  </div>
                </div>

                <a
                  href="https://github.com/Smart-AI-Memory/empathy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline w-full"
                >
                  Get Started
                </a>
              </div>

              {/* Commercial Tier - Featured */}
              <div className="bg-[var(--background)] border-2 border-[var(--accent)] rounded-lg p-8 relative shadow-lg transform md:scale-105">
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-[var(--accent)] text-white px-4 py-1 rounded-full text-sm font-bold">
                    Most Popular
                  </span>
                </div>

                <div className="text-center">
                  <h2 className="text-2xl font-bold mb-2">Commercial</h2>
                  <div className="mb-6">
                    <span className="text-5xl font-bold">$99</span>
                    <span className="text-[var(--muted)]">/dev/year</span>
                  </div>
                  <p className="text-[var(--text-secondary)] mb-6">
                    For businesses with 6+ employees
                  </p>
                </div>

                <div className="space-y-3 mb-8">
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm"><strong>Everything in Free</strong></span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">One license covers all environments</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Workstation, staging, production, CI/CD</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Commercial use rights</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Email support</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Priority bug fixes</span>
                  </div>
                </div>

                <Link
                  href="/contact?topic=business"
                  className="btn btn-primary w-full"
                >
                  Contact Sales
                </Link>
              </div>

              {/* Enterprise Tier */}
              <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-8 hover:border-[var(--primary)] transition-all">
                <div className="text-center">
                  <h2 className="text-2xl font-bold mb-2">Enterprise</h2>
                  <div className="mb-6">
                    <span className="text-5xl font-bold">Custom</span>
                  </div>
                  <p className="text-[var(--text-secondary)] mb-6">
                    For organizations with custom needs
                  </p>
                </div>

                <div className="space-y-3 mb-8">
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm"><strong>Everything in Commercial</strong></span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Volume licensing discounts</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Custom wizard development</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Dedicated support</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">SLA guarantees</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">On-premises deployment</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-[var(--success)] mt-1">✓</span>
                    <span className="text-sm">Training & consulting</span>
                  </div>
                </div>

                <Link
                  href="/contact?topic=volume"
                  className="btn btn-outline w-full"
                >
                  Contact Sales
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="py-20 bg-[var(--border)] bg-opacity-30">
          <div className="container">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-4xl font-bold text-center mb-12">
                Pricing FAQ
              </h2>

              <div className="space-y-6">
                <div className="bg-[var(--background)] border border-[var(--border)] rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-3">
                    What counts as a "developer"?
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    A developer is anyone who uses the Empathy Framework in their development environment.
                    One license covers all environments for that developer (workstation, staging, production, CI/CD).
                  </p>
                </div>

                <div className="bg-[var(--background)] border border-[var(--border)] rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-3">
                    How is the Free tier enforced?
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    The Free tier operates on an honor system. If your organization has 5 or fewer employees,
                    you're eligible for free use. If you grow beyond 5 employees, we ask that you upgrade to
                    the Commercial tier to support continued development.
                  </p>
                </div>

                <div className="bg-[var(--background)] border border-[var(--border)] rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-3">
                    Can I use the Free tier for commercial projects?
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    Yes! If your organization has 5 or fewer employees, you can use the framework for commercial
                    projects at no cost. This includes startups, solo developers, and small agencies.
                  </p>
                </div>

                <div className="bg-[var(--background)] border border-[var(--border)] rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-3">
                    What about students and educators?
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    Students and educators always get free access, regardless of organization size.
                    We believe in supporting education and the next generation of AI developers.
                  </p>
                </div>

                <div className="bg-[var(--background)] border border-[var(--border)] rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-3">
                    Do I need a license for CI/CD servers?
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    No! One developer license covers all environments including CI/CD, staging, and production
                    servers. You only pay per human developer, not per installation.
                  </p>
                </div>

                <div className="bg-[var(--background)] border border-[var(--border)] rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-3">
                    What's the Fair Source License?
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    The Fair Source License 0.9 provides free use for small teams (≤5 employees) while requiring
                    commercial licenses for larger organizations. It's source-available, allowing you to read and
                    modify the code, while supporting sustainable development.
                  </p>
                </div>

                <div className="bg-[var(--background)] border border-[var(--border)] rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-3">
                    Can I get volume discounts?
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    Yes! We offer volume discounts for teams of 50+ developers. Contact our sales team for
                    custom pricing and enterprise licensing options.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-4xl font-bold mb-6">
                Ready to Get Started?
              </h2>
              <p className="text-xl text-[var(--text-secondary)] mb-8">
                Start using the Empathy Framework today. Free for small teams, fair pricing for everyone else.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="https://github.com/Smart-AI-Memory/empathy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary text-lg px-8 py-4"
                >
                  Get Started Free
                </a>
                <Link
                  href="/contact"
                  className="btn btn-outline text-lg px-8 py-4"
                >
                  Contact Sales
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
