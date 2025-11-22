import type { Metadata } from 'next';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { generateMetadata, generateStructuredData } from '@/lib/metadata';

const faqData = [
  {
    category: 'General',
    questions: [
      {
        question: 'What is the Empathy Framework?',
        answer: 'The Empathy Framework is a production-ready 5-level maturity model for AI-human collaboration. It progresses from reactive responses (Level 1) to Level 4 Anticipatory Intelligence that predicts problems before they happen. It includes 30+ production wizards for software development and healthcare applications.',
      },
      {
        question: 'What are the 5 levels of AI empathy?',
        answer: 'Level 1: Reactive - Responds only when asked. Level 2: Guided - Asks clarifying questions. Level 3: Proactive - Notices patterns and offers improvements. Level 4: Anticipatory - Predicts future problems before they happen. Level 5: Transformative - Reshapes workflows to prevent entire classes of problems.',
      },
      {
        question: 'What is MemDocs?',
        answer: 'MemDocs is a persistent project-specific memory system that works seamlessly with the Empathy Framework. It enables AI to remember context, decisions, and patterns across sessions, creating true continuity in your AI-human collaboration and enabling Level 5 Transformative Intelligence.',
      },
    ],
  },
  {
    category: 'Licensing & Pricing',
    questions: [
      {
        question: 'How much does the Empathy Framework cost?',
        answer: 'The Empathy Framework is free for students, educators, and teams with 5 or fewer employees under the Fair Source License 0.9. For businesses with 6+ employees, commercial licensing starts at $99/developer/year, covering all environments (workstation, staging, production, CI/CD).',
      },
      {
        question: 'What is the Fair Source License?',
        answer: 'The Fair Source License 0.9 is a source-available license that provides free use for small teams (≤5 employees) while requiring commercial licenses for larger organizations. It allows you to read and modify the source code while supporting sustainable development.',
      },
      {
        question: 'Do I need separate licenses for different environments?',
        answer: 'No! One developer license covers all environments including development workstations, staging servers, production servers, and CI/CD pipelines. You only pay per human developer, not per installation.',
      },
    ],
  },
  {
    category: 'Technical',
    questions: [
      {
        question: 'Which LLM providers are supported?',
        answer: 'The Empathy Framework supports multiple LLM providers including Anthropic Claude, OpenAI GPT-4, Google Gemini, and local models via Ollama. The framework is designed to be provider-agnostic, allowing you to choose the best model for your use case.',
      },
      {
        question: 'What are wizards?',
        answer: 'Wizards are specialized AI agents in the Empathy Framework that anticipate needs and predict problems in specific domains. The framework includes 16+ software development wizards (security, testing, debugging, etc.) and 18+ healthcare wizards (patient monitoring, protocol compliance, etc.).',
      },
      {
        question: 'How is the framework tested?',
        answer: 'The Empathy Framework has 553 tests with 83.13% overall coverage and 95%+ coverage on core modules. It includes comprehensive unit tests, integration tests, and cross-platform compatibility testing.',
      },
      {
        question: 'What platforms are supported?',
        answer: 'The framework is cross-platform and runs on macOS, Linux, and Windows. It requires Python 3.8+ and works with all major development environments including VS Code, JetBrains IDEs, and terminal-based workflows.',
      },
    ],
  },
  {
    category: 'Use Cases',
    questions: [
      {
        question: 'What can I build with the Empathy Framework?',
        answer: 'You can build anticipatory AI systems for software development (bug prediction, security scanning, test generation), healthcare (patient monitoring, clinical decision support), and any domain where predicting problems before they happen adds value.',
      },
      {
        question: 'Can I use this for commercial projects?',
        answer: 'Yes! If your organization has 5 or fewer employees, you can use it for free under the Fair Source License. Larger organizations need a commercial license starting at $99/developer/year.',
      },
      {
        question: 'Is the framework production-ready?',
        answer: 'Yes! The framework is v1.7.0 Production/Stable with 1,489 tests (90.71% coverage), comprehensive documentation, and is being used in production applications including medical wizards dashboards and software development tools.',
      },
    ],
  },
  {
    category: 'Support & Community',
    questions: [
      {
        question: 'Where can I get help?',
        answer: 'Free users get community support via GitHub Discussions. Commercial users get email support and priority bug fixes. Enterprise users get dedicated support with SLA guarantees.',
      },
      {
        question: 'How do I report bugs?',
        answer: 'Report bugs via GitHub Issues at https://github.com/Smart-AI-Memory/empathy-framework/issues. Include your environment details, steps to reproduce, and expected vs actual behavior.',
      },
      {
        question: 'Can I contribute to the project?',
        answer: 'Yes! We welcome contributions. Check out our GitHub repository for contribution guidelines. The source code is available for reading and modification under the Fair Source License.',
      },
    ],
  },
];

export const metadata: Metadata = generateMetadata({
  title: 'FAQ',
  description: 'Frequently asked questions about the Empathy Framework, MemDocs, licensing, pricing, and technical details.',
  url: 'https://smartaimemory.com/faq',
});

export default function FAQPage() {
  const structuredData = generateStructuredData('faq', {
    questions: faqData.flatMap(category =>
      category.questions.map(q => ({
        question: q.question,
        answer: q.answer,
      }))
    ),
  });

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData),
        }}
      />
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-5xl font-bold mb-6">
                Frequently Asked Questions
              </h1>
              <p className="text-2xl mb-8 opacity-90">
                Everything you need to know about the Empathy Framework
              </p>
            </div>
          </div>
        </section>

        {/* FAQ Sections */}
        <section className="py-20">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              {faqData.map((category, categoryIndex) => (
                <div
                  key={categoryIndex}
                  className="mb-12"
                >
                  <h2 className="text-3xl font-bold mb-6 text-[var(--primary)]">
                    {category.category}
                  </h2>
                  <div className="space-y-6">
                    {category.questions.map((item, questionIndex) => (
                      <details
                        key={questionIndex}
                        className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-6 hover:border-[var(--primary)] transition-all group"
                      >
                        <summary className="text-xl font-bold cursor-pointer list-none flex justify-between items-center">
                          <span>{item.question}</span>
                          <span className="text-[var(--primary)] ml-4 group-open:rotate-180 transition-transform">
                            ▼
                          </span>
                        </summary>
                        <p className="mt-4 text-[var(--text-secondary)] leading-relaxed">
                          {item.answer}
                        </p>
                      </details>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Still Have Questions CTA */}
        <section className="py-20 bg-[var(--border)] bg-opacity-30">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-4xl font-bold mb-6">
                Still Have Questions?
              </h2>
              <p className="text-xl text-[var(--text-secondary)] mb-8">
                We're here to help. Reach out to our team or join the community.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="/contact"
                  className="btn btn-primary text-lg px-8 py-4"
                >
                  Contact Us
                </a>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework/discussions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline text-lg px-8 py-4"
                >
                  Join Community
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
