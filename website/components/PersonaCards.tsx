import Link from 'next/link';

const personas = [
  {
    emoji: '👨‍💻',
    title: 'Developers',
    description: 'Ship faster with AI that catches bugs before they happen',
    cta: 'Start Building',
    href: '/framework',
  },
  {
    emoji: '🏢',
    title: 'Engineering Teams',
    description: 'Reduce incidents with predictive alerts across your codebase',
    cta: 'See Enterprise',
    href: '/pricing',
  },
  {
    emoji: '🎓',
    title: 'Students & Researchers',
    description: 'Learn cutting-edge AI collaboration patterns',
    cta: 'Read the Book',
    href: '/book',
  },
];

export default function PersonaCards() {
  return (
    <section className="py-16 bg-[var(--border)] bg-opacity-30">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-4">Who This Is For</h2>
        <p className="text-center text-[var(--text-secondary)] mb-10 max-w-2xl mx-auto">
          Whether you&apos;re building production systems or learning AI fundamentals,
          the Empathy Framework meets you where you are.
        </p>

        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {personas.map((persona) => (
            <Link
              key={persona.title}
              href={persona.href}
              className="group bg-[var(--background)] p-6 rounded-xl border-2 border-[var(--border)]
                         hover:border-[var(--primary)] hover:shadow-lg transition-all text-center"
            >
              <div className="text-4xl mb-4">{persona.emoji}</div>
              <h3 className="text-xl font-bold mb-2 group-hover:text-[var(--primary)] transition-colors">
                {persona.title}
              </h3>
              <p className="text-[var(--text-secondary)] text-sm mb-4">
                {persona.description}
              </p>
              <span className="text-sm font-medium text-[var(--primary)]">
                {persona.cta} →
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
