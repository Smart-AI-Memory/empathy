import type { Metadata } from 'next';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { generateMetadata } from '@/lib/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Terms of Service',
  description: 'Terms of service for Smart AI Memory and the Empathy Framework.',
  url: 'https://smartaimemory.com/terms',
});

export default function TermsPage() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-5xl font-bold mb-6">
                Terms of Service
              </h1>
              <p className="text-xl opacity-90">
                Last updated: January 10, 2025
              </p>
            </div>
          </div>
        </section>

        {/* Content */}
        <section className="py-20">
          <div className="container">
            <div className="max-w-4xl mx-auto prose prose-lg">
              <h2>1. Agreement to Terms</h2>
              <p>
                By accessing our website at smartaimemory.com or using the Empathy Framework
                ("Services"), you agree to be bound by these Terms of Service and our Privacy Policy.
                If you disagree with any part of these terms, you may not access our Services.
              </p>

              <h2>2. Licensing</h2>

              <h3>2.1 Fair Source License</h3>
              <p>
                The Empathy Framework is licensed under the Fair Source License 0.9. Key terms:
              </p>
              <ul>
                <li><strong>Free Tier:</strong> Free for students, educators, and organizations with ≤5 employees</li>
                <li><strong>Commercial Tier:</strong> $99/developer/year for organizations with 6+ employees</li>
                <li><strong>Source Available:</strong> You may read and modify the source code</li>
                <li><strong>Redistribution:</strong> Subject to license terms</li>
              </ul>
              <p>
                Full license terms available at: <a href="https://github.com/Smart-AI-Memory/empathy-framework/blob/main/LICENSE-FAIR-SOURCE.md">LICENSE-FAIR-SOURCE.md</a>
              </p>

              <h3>2.2 Commercial License</h3>
              <p>
                Commercial licenses are required for organizations with 6 or more employees.
                One license covers all developer environments (workstation, staging, production, CI/CD).
                See <a href="https://github.com/Smart-AI-Memory/empathy-framework/blob/main/LICENSE-COMMERCIAL.md">LICENSE-COMMERCIAL.md</a> for full terms.
              </p>

              <h2>3. Acceptable Use</h2>
              <p>You agree NOT to use our Services to:</p>
              <ul>
                <li>Violate any laws or regulations</li>
                <li>Infringe on intellectual property rights</li>
                <li>Transmit malicious code, viruses, or malware</li>
                <li>Harass, abuse, or harm others</li>
                <li>Attempt to gain unauthorized access to our systems</li>
                <li>Reverse engineer our services (except as permitted by license)</li>
                <li>Use for competing products without permission</li>
              </ul>

              <h2>4. User Accounts</h2>
              <p>When creating an account, you agree to:</p>
              <ul>
                <li>Provide accurate and complete information</li>
                <li>Maintain the security of your account credentials</li>
                <li>Promptly update any changes to your information</li>
                <li>Accept responsibility for all activities under your account</li>
                <li>Notify us immediately of unauthorized access</li>
              </ul>

              <h2>5. Intellectual Property</h2>

              <h3>5.1 Our Intellectual Property</h3>
              <p>
                The Empathy Framework, documentation, and website content are owned by
                Deep Study AI, LLC and protected by copyright, trademark, and other intellectual property laws.
              </p>

              <h3>5.2 Your Content</h3>
              <p>
                You retain all rights to content you create using the Empathy Framework.
                We claim no ownership over your code, data, or projects created with our tools.
              </p>

              <h2>6. Third-Party Services</h2>
              <p>
                The Empathy Framework integrates with third-party LLM providers (Anthropic, OpenAI, Google, etc.).
                You are responsible for:
              </p>
              <ul>
                <li>Obtaining necessary accounts and API keys</li>
                <li>Complying with their terms of service</li>
                <li>Paying their fees directly</li>
                <li>Understanding their data handling practices</li>
              </ul>

              <h2>7. Disclaimers and Limitations</h2>

              <h3>7.1 "As Is" Provision</h3>
              <p>
                Our Services are provided "AS IS" and "AS AVAILABLE" without warranties of any kind,
                either express or implied, including but not limited to:
              </p>
              <ul>
                <li>Merchantability</li>
                <li>Fitness for a particular purpose</li>
                <li>Non-infringement</li>
                <li>Accuracy, reliability, or completeness of results</li>
              </ul>

              <h3>7.2 AI-Generated Content</h3>
              <p>
                The Empathy Framework uses AI models that may produce:
              </p>
              <ul>
                <li>Inaccurate or incomplete information</li>
                <li>Code with bugs or security vulnerabilities</li>
                <li>Inappropriate or biased content</li>
              </ul>
              <p>
                <strong>You are responsible for reviewing, testing, and validating all AI-generated content
                before use in production.</strong>
              </p>

              <h3>7.3 Limitation of Liability</h3>
              <p>
                To the maximum extent permitted by law, Deep Study AI, LLC shall not be liable for:
              </p>
              <ul>
                <li>Indirect, incidental, special, or consequential damages</li>
                <li>Loss of profits, data, or business opportunities</li>
                <li>Damages exceeding the amount paid to us in the past 12 months</li>
              </ul>

              <h2>8. Indemnification</h2>
              <p>
                You agree to indemnify and hold harmless Deep Study AI, LLC from any claims, damages,
                or expenses arising from:
              </p>
              <ul>
                <li>Your use of our Services</li>
                <li>Violation of these Terms</li>
                <li>Infringement of third-party rights</li>
                <li>Your content or applications built with our Services</li>
              </ul>

              <h2>9. Healthcare and Regulated Industries</h2>
              <p>
                <strong>Important Notice:</strong> While the Empathy Framework includes healthcare wizards,
                it is NOT intended as a medical device or for direct clinical use. If you use our Services
                in healthcare or other regulated industries:
              </p>
              <ul>
                <li>You are responsible for regulatory compliance (HIPAA, FDA, etc.)</li>
                <li>You must validate all outputs for your specific use case</li>
                <li>You assume all liability for deployment decisions</li>
                <li>Additional terms may apply - contact us for guidance</li>
              </ul>

              <h2>10. Termination</h2>
              <p>We may terminate or suspend access to our Services immediately, without notice, for:</p>
              <ul>
                <li>Violation of these Terms</li>
                <li>Fraudulent or illegal activity</li>
                <li>Non-payment of commercial license fees</li>
                <li>At our sole discretion for any reason</li>
              </ul>
              <p>Upon termination, your right to use our Services ceases immediately.</p>

              <h2>11. Changes to Terms</h2>
              <p>
                We reserve the right to modify these Terms at any time. Material changes will be
                notified via email or website notice. Continued use after changes constitutes
                acceptance of new terms.
              </p>

              <h2>12. Governing Law</h2>
              <p>
                These Terms are governed by the laws of the United States and the State of [Your State],
                without regard to conflict of law provisions.
              </p>

              <h2>13. Dispute Resolution</h2>
              <p>
                Any disputes arising from these Terms or our Services will be resolved through:
              </p>
              <ol>
                <li>Good faith negotiations</li>
                <li>Mediation if negotiations fail</li>
                <li>Binding arbitration as a last resort</li>
              </ol>

              <h2>14. Severability</h2>
              <p>
                If any provision of these Terms is found to be unenforceable, the remaining
                provisions will continue in full force and effect.
              </p>

              <h2>15. Contact</h2>
              <p>Questions about these Terms? Contact us at:</p>
              <ul>
                <li><strong>Email:</strong> patrick.roebuck@pm.me</li>
                <li><strong>Website:</strong> smartaimemory.com/contact</li>
                <li><strong>Company:</strong> Deep Study AI, LLC</li>
              </ul>

              <hr />

              <p className="text-sm text-gray-600">
                By using the Empathy Framework or our Services, you acknowledge that you have read,
                understood, and agree to be bound by these Terms of Service.
              </p>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
