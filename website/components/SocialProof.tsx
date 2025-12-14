const metrics = [
  { value: '2,249', label: 'Tests Passing' },
  { value: '81%', label: 'Code Coverage' },
  { value: '44', label: 'Wizards Available' },
  { value: '5', label: 'LLMs Supported' },
];

export default function SocialProof() {
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

        </div>
      </div>
    </section>
  );
}
