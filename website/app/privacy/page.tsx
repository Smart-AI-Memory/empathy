import type { Metadata } from 'next';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { generateMetadata } from '@/lib/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Privacy Policy',
  description: 'Privacy policy for Smart AI Memory and the Empathy Framework.',
  url: 'https://smartaimemory.com/privacy',
});

export default function PrivacyPage() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-5xl font-bold mb-6">
                Privacy Policy
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
              <h2>1. Introduction</h2>
              <p>
                Deep Study AI, LLC (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;) operates smartaimemory.com and the Empathy Framework.
                This Privacy Policy explains how we collect, use, disclose, and safeguard your information when
                you visit our website or use our products.
              </p>

              <h2>2. Information We Collect</h2>

              <h3>2.1 Information You Provide</h3>
              <p>We collect information you voluntarily provide when you:</p>
              <ul>
                <li>Contact us through our contact form</li>
                <li>Subscribe to our newsletter</li>
                <li>Create an account or register for services</li>
                <li>Participate in community discussions</li>
              </ul>
              <p>This information may include:</p>
              <ul>
                <li>Name and email address</li>
                <li>Company name and role</li>
                <li>Message content and inquiry details</li>
              </ul>

              <h3>2.2 Automatically Collected Information</h3>
              <p>We use privacy-friendly analytics (Plausible) that collect:</p>
              <ul>
                <li>Page views and navigation patterns</li>
                <li>Referrer information</li>
                <li>General location (country-level only)</li>
                <li>Device type and browser</li>
              </ul>
              <p>
                <strong>Important:</strong> We do NOT use cookies for tracking, do NOT collect personally
                identifiable information through analytics, and do NOT sell your data to third parties.
              </p>

              <h2>3. How We Use Your Information</h2>
              <p>We use collected information to:</p>
              <ul>
                <li>Respond to your inquiries and support requests</li>
                <li>Send newsletters and product updates (with your consent)</li>
                <li>Improve our website and products</li>
                <li>Analyze usage patterns to enhance user experience</li>
                <li>Comply with legal obligations</li>
              </ul>

              <h2>4. Information Sharing and Disclosure</h2>
              <p>We do NOT sell your personal information. We may share information with:</p>
              <ul>
                <li><strong>Service Providers:</strong> Email service providers (SendGrid), analytics (Plausible)</li>
                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
                <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
              </ul>

              <h2>5. Open Source Framework</h2>
              <p>
                The Empathy Framework is source-available software under the Fair Source License.
                When you use the framework locally:
              </p>
              <ul>
                <li>All processing happens on your machine or your chosen infrastructure</li>
                <li>We do NOT have access to your code, data, or projects</li>
                <li>You control which LLM providers you use and what data you send to them</li>
                <li>No telemetry or usage tracking is built into the framework</li>
              </ul>

              <h2>6. Third-Party Services</h2>
              <p>Our website and products may integrate with third-party services:</p>

              <h3>6.1 LLM Providers</h3>
              <p>
                The Empathy Framework supports multiple LLM providers (Anthropic, OpenAI, Google, etc.).
                You are responsible for understanding and complying with their respective privacy policies
                and terms of service.
              </p>

              <h3>6.2 GitHub</h3>
              <p>
                Our code is hosted on GitHub. When you interact with our repositories, you&apos;re subject
                to GitHub&apos;s privacy policy and terms.
              </p>

              <h2>7. Data Retention</h2>
              <p>We retain your information for as long as necessary to:</p>
              <ul>
                <li>Provide you with requested services</li>
                <li>Comply with legal obligations</li>
                <li>Resolve disputes and enforce agreements</li>
              </ul>
              <p>You may request deletion of your personal information at any time by contacting us.</p>

              <h2>8. Your Rights and Choices</h2>
              <p>You have the right to:</p>
              <ul>
                <li><strong>Access:</strong> Request a copy of your personal information</li>
                <li><strong>Correction:</strong> Request correction of inaccurate information</li>
                <li><strong>Deletion:</strong> Request deletion of your information</li>
                <li><strong>Opt-Out:</strong> Unsubscribe from marketing communications</li>
                <li><strong>Data Portability:</strong> Request your data in a machine-readable format</li>
              </ul>
              <p>Contact us at patrick.roebuck@pm.me to exercise these rights.</p>

              <h2>9. Security</h2>
              <p>
                We implement appropriate technical and organizational measures to protect your information.
                However, no method of transmission over the Internet is 100% secure, and we cannot
                guarantee absolute security.
              </p>

              <h2>10. Children&apos;s Privacy</h2>
              <p>
                Our services are not directed to children under 13. We do not knowingly collect information
                from children under 13. If you believe we have collected information from a child,
                please contact us immediately.
              </p>

              <h2>11. International Data Transfers</h2>
              <p>
                Your information may be transferred to and processed in the United States or other
                countries where our service providers operate. We ensure appropriate safeguards are
                in place for such transfers.
              </p>

              <h2>12. Changes to This Policy</h2>
              <p>
                We may update this Privacy Policy from time to time. We will notify you of material
                changes by posting the new policy on this page and updating the &quot;Last updated&quot; date.
              </p>

              <h2>13. Contact Us</h2>
              <p>If you have questions about this Privacy Policy, contact us at:</p>
              <ul>
                <li><strong>Email:</strong> patrick.roebuck@pm.me</li>
                <li><strong>Website:</strong> smartaimemory.com/contact</li>
                <li><strong>Company:</strong> Deep Study AI, LLC</li>
              </ul>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
