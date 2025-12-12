const metrics = [
  { value: '1,954', label: 'Tests Passing' },
  { value: '90%', label: 'Code Coverage' },
  { value: '45+', label: 'Wizards Available' },
  { value: '5', label: 'LLMs Supported' },
];

interface SocialProofProps {
  showTestimonial?: boolean;
}

export default function SocialProof({ showTestimonial = true }: SocialProofProps) {
  return (
    <section className="py-16">
      <div className="container">
        <div className="max-w-4xl mx-auto">
          {/* Metrics Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
            {metrics.map((metric) => (
              <div key={metric.label} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-[var(--primary)] mb-1">
                  {metric.value}
                </div>
                <div className="text-sm text-[var(--text-secondary)]">
                  {metric.label}
                </div>
              </div>
            ))}
          </div>

          {/* Testimonial */}
          {showTestimonial && (
            <div className="bg-[var(--border)] bg-opacity-30 p-8 rounded-xl max-w-2xl mx-auto">
              <blockquote className="text-lg text-[var(--text-primary)] italic mb-4 text-center">
                &quot;Empathy transformed how our team approaches AI integration.
                Level 4 anticipatory intelligence catches issues we never would have found.&quot;
              </blockquote>
              <div className="text-center">
                <div className="text-sm text-[var(--muted)]">
                  — Testimonial Coming Soon
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
