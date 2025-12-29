import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';

const wizardCategories = [
  {
    name: 'Development',
    description: 'Debug, refactor, and optimize your code',
    wizards: [
      {
        name: 'DebugWizard',
        description: 'Analyzes errors and suggests fixes with root cause analysis',
        tier: 'capable',
      },
      {
        name: 'CodeReviewWizard',
        description: 'Comprehensive code review with security and performance checks',
        tier: 'capable',
      },
      {
        name: 'RefactorWizard',
        description: 'Identifies refactoring opportunities and generates improved code',
        tier: 'capable',
      },
      {
        name: 'TestGeneratorWizard',
        description: 'Generates unit tests, integration tests, and test fixtures',
        tier: 'cheap',
      },
      {
        name: 'PerformanceWizard',
        description: 'Profiles code and identifies optimization opportunities',
        tier: 'premium',
      },
      {
        name: 'DependencyWizard',
        description: 'Analyzes dependencies, finds vulnerabilities, suggests updates',
        tier: 'cheap',
      },
    ],
  },
  {
    name: 'Security',
    description: 'Scan, audit, and secure your applications',
    wizards: [
      {
        name: 'SecurityWizard',
        description: 'OWASP Top 10 scanning, vulnerability detection, fix suggestions',
        tier: 'capable',
      },
      {
        name: 'SecretsWizard',
        description: 'Detects hardcoded secrets, API keys, and credentials',
        tier: 'cheap',
      },
      {
        name: 'PIIScrubberWizard',
        description: 'Identifies and redacts PII from logs, data, and code',
        tier: 'cheap',
      },
      {
        name: 'ComplianceWizard',
        description: 'SOC2, HIPAA, GDPR compliance checking and remediation',
        tier: 'premium',
      },
    ],
  },
  {
    name: 'Documentation',
    description: 'Generate and maintain documentation',
    wizards: [
      {
        name: 'DocStringWizard',
        description: 'Generates comprehensive docstrings for functions and classes',
        tier: 'cheap',
      },
      {
        name: 'ReadmeWizard',
        description: 'Creates and updates README files with usage examples',
        tier: 'cheap',
      },
      {
        name: 'APIDocWizard',
        description: 'Generates OpenAPI specs and API documentation',
        tier: 'capable',
      },
      {
        name: 'ChangelogWizard',
        description: 'Generates changelogs from git history and PR descriptions',
        tier: 'cheap',
      },
    ],
  },
  {
    name: 'Architecture',
    description: 'Design and analyze system architecture',
    wizards: [
      {
        name: 'ArchitectureWizard',
        description: 'Analyzes codebase structure and suggests improvements',
        tier: 'premium',
      },
      {
        name: 'MigrationWizard',
        description: 'Plans and executes database and framework migrations',
        tier: 'premium',
      },
      {
        name: 'APIDesignWizard',
        description: 'Designs RESTful and GraphQL APIs following best practices',
        tier: 'capable',
      },
      {
        name: 'SchemaWizard',
        description: 'Generates and validates database schemas',
        tier: 'capable',
      },
    ],
  },
  {
    name: 'DevOps',
    description: 'CI/CD, deployment, and infrastructure',
    wizards: [
      {
        name: 'CIWizard',
        description: 'Generates GitHub Actions, GitLab CI, and Jenkins pipelines',
        tier: 'cheap',
      },
      {
        name: 'DockerWizard',
        description: 'Creates optimized Dockerfiles and compose configurations',
        tier: 'cheap',
      },
      {
        name: 'KubernetesWizard',
        description: 'Generates K8s manifests, Helm charts, and deployment configs',
        tier: 'capable',
      },
      {
        name: 'MonitoringWizard',
        description: 'Sets up logging, metrics, and alerting configurations',
        tier: 'capable',
      },
    ],
  },
  {
    name: 'Healthcare',
    description: 'HIPAA-compliant clinical AI tools',
    wizards: [
      {
        name: 'SBARWizard',
        description: 'Generates SBAR reports for clinical handoffs',
        tier: 'capable',
      },
      {
        name: 'ClinicalProtocolWizard',
        description: 'Analyzes clinical protocols and suggests improvements',
        tier: 'premium',
      },
      {
        name: 'MedicalCodingWizard',
        description: 'Assists with ICD-10, CPT, and diagnosis coding',
        tier: 'premium',
      },
      {
        name: 'PHIDetectorWizard',
        description: 'Identifies and protects Protected Health Information',
        tier: 'cheap',
      },
    ],
  },
];

const tierColors = {
  cheap: 'bg-green-100 text-green-800 border-green-200',
  capable: 'bg-blue-100 text-blue-800 border-blue-200',
  premium: 'bg-purple-100 text-purple-800 border-purple-200',
};

const tierLabels = {
  cheap: 'Fast & Affordable',
  capable: 'Balanced',
  premium: 'Most Capable',
};

export default function WizardsPage() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero */}
        <section className="py-16 sm:py-20 bg-gradient-to-b from-[var(--border)] to-transparent">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl sm:text-5xl font-bold mb-6">
                44+ AI Wizards for Every Task
              </h1>
              <p className="text-xl text-[var(--text-secondary)] mb-8">
                Pre-built, specialized AI assistants that understand your codebase.
                Each wizard is optimized for specific tasks with built-in best practices.
              </p>
              <div className="flex flex-wrap gap-4 justify-center">
                <Link
                  href="/framework-docs/tutorials/quickstart/"
                  className="btn btn-primary"
                >
                  Get Started
                </Link>
                <a
                  href="https://wizards.smartaimemory.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline"
                >
                  Try Live Demo
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Tier Legend */}
        <section className="py-8 border-b border-[var(--border)]">
          <div className="container">
            <div className="flex flex-wrap gap-6 justify-center items-center">
              <span className="text-sm text-[var(--muted)]">Model Tiers:</span>
              {Object.entries(tierLabels).map(([tier, label]) => (
                <div key={tier} className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded border ${tierColors[tier as keyof typeof tierColors]}`}>
                    {tier}
                  </span>
                  <span className="text-sm text-[var(--text-secondary)]">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Wizard Categories */}
        <section className="py-16">
          <div className="container">
            <div className="space-y-16">
              {wizardCategories.map((category) => (
                <div key={category.name}>
                  <div className="mb-8">
                    <h2 className="text-2xl sm:text-3xl font-bold mb-2">
                      {category.name}
                    </h2>
                    <p className="text-[var(--text-secondary)]">
                      {category.description}
                    </p>
                  </div>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {category.wizards.map((wizard) => (
                      <div
                        key={wizard.name}
                        className="bg-[var(--background)] p-5 rounded-xl border border-[var(--border)] hover:border-[var(--primary)] hover:shadow-md transition-all"
                      >
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <h3 className="font-bold text-lg">{wizard.name}</h3>
                          <span className={`flex-shrink-0 px-2 py-0.5 text-xs font-medium rounded border ${tierColors[wizard.tier as keyof typeof tierColors]}`}>
                            {wizard.tier}
                          </span>
                        </div>
                        <p className="text-sm text-[var(--text-secondary)]">
                          {wizard.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Usage Example */}
        <section className="py-16 bg-[var(--border)] bg-opacity-30">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8">
                Using Wizards is Simple
              </h2>
              <div className="bg-[#1e1e1e] rounded-xl overflow-hidden shadow-2xl">
                <div className="flex items-center gap-2 px-4 py-3 bg-[#2d2d2d] border-b border-[#3d3d3d]">
                  <div className="w-3 h-3 rounded-full bg-[#ff5f56]"></div>
                  <div className="w-3 h-3 rounded-full bg-[#ffbd2e]"></div>
                  <div className="w-3 h-3 rounded-full bg-[#27ca40]"></div>
                  <span className="ml-2 text-sm text-gray-400">security_scan.py</span>
                </div>
                <pre className="p-6 overflow-x-auto text-sm">
                  <code className="text-gray-300">{`from empathy_os import EmpathyLLM
from empathy_os.wizards import SecurityWizard

# Initialize with your preferred provider
llm = EmpathyLLM(provider="anthropic")

# Create the wizard
wizard = SecurityWizard(llm)

# Scan your codebase
result = await wizard.scan(
    path="./src",
    checks=["owasp-top-10", "secrets", "dependencies"]
)

# Get actionable results
for vulnerability in result.vulnerabilities:
    print(f"[{vulnerability.severity}] {vulnerability.file}:{vulnerability.line}")
    print(f"  Issue: {vulnerability.description}")
    print(f"  Fix: {vulnerability.suggested_fix}")
`}</code>
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Build Your Own Wizards
              </h2>
              <p className="text-xl text-[var(--text-secondary)] mb-8">
                Extend the framework with custom wizards tailored to your workflow.
                Full documentation and examples included.
              </p>
              <Link
                href="/framework-docs/"
                className="btn btn-primary text-lg px-8 py-4"
              >
                Read the Documentation
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
