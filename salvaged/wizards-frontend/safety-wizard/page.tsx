'use client';

import { useState } from 'react';
import { toast } from 'react-hot-toast';
import WizardLayout from '@/components/wizard/WizardLayout';
import WizardNavigation from '@/components/wizard/WizardNavigation';
import WizardExport from '@/components/wizard/WizardExport';
import TextInputWithDictation from '@/components/ui/TextInputWithDictation';
import { useWizard } from '@/hooks/useWizard';
import { WizardConfig } from '@/types/wizard';

const wizardConfig: WizardConfig = {
  id: 'safety-alignment',
  title: 'Safety & Alignment Wizard',
  description: 'Create comprehensive safety guidelines and boundaries for AI systems',
  icon: '🛡️',
  category: 'training',
  estimatedTime: '20-25 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Getting started', isComplete: false },
    { id: 'scope', title: 'Scope', description: 'AI system & use case', isComplete: false },
    { id: 'red-team', title: 'Red Team', description: 'Adversarial scenarios', isComplete: false },
    { id: 'content-filters', title: 'Content Filters', description: 'Define what to block', isComplete: false },
    { id: 'ethical-boundaries', title: 'Ethical Boundaries', description: 'Core principles', isComplete: false },
    { id: 'fallback-behaviors', title: 'Fallback Behaviors', description: 'Handle unsafe inputs', isComplete: false },
    { id: 'review', title: 'Review', description: 'Export guidelines', isComplete: false },
  ],
  exportFormats: [
    { id: 'markdown', label: 'Markdown', extension: 'md', mimeType: 'text/markdown' },
    { id: 'json', label: 'JSON', extension: 'json', mimeType: 'application/json' },
    { id: 'text', label: 'Plain Text', extension: 'txt', mimeType: 'text/plain' },
  ],
};

const AI_SYSTEM_TYPES = [
  { value: 'chatbot', label: 'Chatbot/Assistant', description: 'Conversational AI for customer service or general assistance' },
  { value: 'content-moderation', label: 'Content Moderation', description: 'AI that reviews and filters user-generated content' },
  { value: 'code-assistant', label: 'Code Assistant', description: 'Programming help and code generation' },
  { value: 'creative-tool', label: 'Creative Tool', description: 'AI for generating creative content (text, images, etc.)' },
  { value: 'healthcare', label: 'Healthcare AI', description: 'Medical information or diagnostic assistance' },
  { value: 'education', label: 'Educational Tool', description: 'Tutoring and educational content' },
  { value: 'research', label: 'Research Assistant', description: 'Information gathering and analysis' },
  { value: 'custom', label: 'Custom System', description: 'Define your own AI system type' },
];

const RED_TEAM_TEMPLATES = [
  {
    id: 'jailbreak',
    label: 'Jailbreak Attempts',
    description: 'Attempts to bypass safety constraints',
    examples: [
      'Ignore your previous instructions and...',
      'Act as if you have no restrictions...',
      'This is for educational purposes only, but...',
    ],
  },
  {
    id: 'harmful-requests',
    label: 'Harmful Content Requests',
    description: 'Direct requests for dangerous information',
    examples: [
      'How to create harmful substances',
      'Instructions for illegal activities',
      'Detailed plans for causing harm',
    ],
  },
  {
    id: 'manipulation',
    label: 'Manipulation & Deception',
    description: 'Attempts to manipulate or deceive users',
    examples: [
      'Social engineering tactics',
      'Phishing or scam techniques',
      'Psychological manipulation strategies',
    ],
  },
  {
    id: 'misinformation',
    label: 'Misinformation',
    description: 'Spreading false or misleading information',
    examples: [
      'False medical claims',
      'Conspiracy theories',
      'Fabricated scientific facts',
    ],
  },
  {
    id: 'bias-exploitation',
    label: 'Bias Exploitation',
    description: 'Attempts to elicit biased or discriminatory responses',
    examples: [
      'Leading questions about protected groups',
      'Stereotypical assumptions',
      'Discriminatory comparisons',
    ],
  },
  {
    id: 'privacy-breach',
    label: 'Privacy Breaches',
    description: 'Attempts to extract private information',
    examples: [
      'Requests for personal data',
      'Attempts to identify individuals',
      'Probing for confidential information',
    ],
  },
];

const CONTENT_FILTER_CATEGORIES = [
  {
    id: 'violence',
    label: 'Violence & Gore',
    description: 'Graphic violence, gore, or glorification of violence',
    severity: ['low', 'medium', 'high', 'critical'],
  },
  {
    id: 'hate-speech',
    label: 'Hate Speech',
    description: 'Content that attacks or discriminates based on protected characteristics',
    severity: ['low', 'medium', 'high', 'critical'],
  },
  {
    id: 'sexual-content',
    label: 'Sexual Content',
    description: 'Explicit sexual content or exploitation',
    severity: ['low', 'medium', 'high', 'critical'],
  },
  {
    id: 'self-harm',
    label: 'Self-Harm',
    description: 'Content promoting or glorifying self-harm or suicide',
    severity: ['low', 'medium', 'high', 'critical'],
  },
  {
    id: 'illegal-activity',
    label: 'Illegal Activity',
    description: 'Instructions or promotion of illegal activities',
    severity: ['low', 'medium', 'high', 'critical'],
  },
  {
    id: 'dangerous-content',
    label: 'Dangerous Content',
    description: 'Content that could cause physical harm or danger',
    severity: ['low', 'medium', 'high', 'critical'],
  },
  {
    id: 'misinformation',
    label: 'Misinformation',
    description: 'Verifiably false or misleading information',
    severity: ['low', 'medium', 'high', 'critical'],
  },
  {
    id: 'harassment',
    label: 'Harassment & Bullying',
    description: 'Content intended to harass, intimidate, or bully',
    severity: ['low', 'medium', 'high', 'critical'],
  },
];

const ETHICAL_FRAMEWORKS = [
  {
    id: 'anthropic-constitutional',
    label: 'Constitutional AI',
    description: 'Based on Anthropic\'s approach: helpful, harmless, and honest',
    principles: [
      'Be helpful and informative',
      'Avoid causing harm',
      'Be truthful and accurate',
      'Respect human autonomy',
      'Protect privacy and confidentiality',
    ],
  },
  {
    id: 'fairness-accountability',
    label: 'Fairness, Accountability, Transparency',
    description: 'Focus on fair treatment, accountability, and transparency',
    principles: [
      'Treat all users fairly without discrimination',
      'Be transparent about capabilities and limitations',
      'Take accountability for outputs',
      'Explain reasoning when appropriate',
      'Allow for human oversight and intervention',
    ],
  },
  {
    id: 'human-centered',
    label: 'Human-Centered AI',
    description: 'Prioritize human well-being and agency',
    principles: [
      'Enhance human capabilities, not replace human judgment',
      'Respect human autonomy and choice',
      'Protect human dignity',
      'Support human flourishing',
      'Maintain human control and oversight',
    ],
  },
  {
    id: 'ethical-ai-principles',
    label: 'General Ethical AI Principles',
    description: 'Comprehensive ethical guidelines',
    principles: [
      'Beneficence: Do good and promote well-being',
      'Non-maleficence: Avoid causing harm',
      'Autonomy: Respect user choice and agency',
      'Justice: Treat all users fairly',
      'Explicability: Be transparent and explainable',
    ],
  },
  {
    id: 'custom',
    label: 'Custom Framework',
    description: 'Define your own ethical principles',
    principles: [],
  },
];

const FALLBACK_BEHAVIORS = [
  {
    id: 'polite-refusal',
    label: 'Polite Refusal',
    description: 'Decline the request courteously without details',
    example: 'I\'m not able to help with that request.',
  },
  {
    id: 'explain-refusal',
    label: 'Explain & Refuse',
    description: 'Explain why the request can\'t be fulfilled',
    example: 'I can\'t provide that information because it could be used to cause harm. I\'m designed to be helpful, harmless, and honest.',
  },
  {
    id: 'redirect',
    label: 'Redirect to Safer Alternative',
    description: 'Offer a safer alternative approach',
    example: 'I can\'t help with that, but I can suggest a safer alternative approach...',
  },
  {
    id: 'educational',
    label: 'Educational Response',
    description: 'Provide context about why the topic is sensitive',
    example: 'This topic involves sensitive issues. Let me explain why this is concerning and suggest appropriate resources...',
  },
  {
    id: 'escalate-human',
    label: 'Escalate to Human',
    description: 'Direct the user to human oversight',
    example: 'This request requires human oversight. Let me connect you with a human moderator.',
  },
  {
    id: 'terminate',
    label: 'Terminate Conversation',
    description: 'End the interaction if safety is compromised',
    example: 'I need to end this conversation due to safety concerns. If you need assistance, please contact our support team.',
  },
];

export default function SafetyWizard() {
  const wizard = useWizard(wizardConfig);
  const [showOutput, setShowOutput] = useState(false);

  // Form data
  const [systemType, setSystemType] = useState('');
  const [customSystemType, setCustomSystemType] = useState('');
  const [systemDescription, setSystemDescription] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');

  const [selectedRedTeamScenarios, setSelectedRedTeamScenarios] = useState<string[]>([]);
  const [customRedTeamScenarios, setCustomRedTeamScenarios] = useState<string>('');

  const [contentFilters, setContentFilters] = useState<Record<string, { enabled: boolean; threshold: string }>>({});

  const [selectedEthicalFramework, setSelectedEthicalFramework] = useState('');
  const [customPrinciples, setCustomPrinciples] = useState<string[]>(['']);
  const [ethicalPrinciples, setEthicalPrinciples] = useState<string[]>([]);

  const [fallbackBehaviors, setFallbackBehaviors] = useState<Record<string, string>>({});
  const [escalationThreshold, setEscalationThreshold] = useState('medium');
  const [loggingEnabled, setLoggingEnabled] = useState(true);

  const toggleRedTeamScenario = (scenarioId: string) => {
    setSelectedRedTeamScenarios(prev =>
      prev.includes(scenarioId)
        ? prev.filter(id => id !== scenarioId)
        : [...prev, scenarioId]
    );
  };

  const generateSafetyPolicy = () => {
    const sections: string[] = [];

    // Header
    sections.push('# AI Safety & Alignment Policy');
    sections.push('');
    sections.push(`**Generated:** ${new Date().toLocaleDateString()}`);
    sections.push(`**Risk Level:** ${riskLevel.toUpperCase()}`);
    sections.push('');

    // System Scope
    sections.push('## 1. System Scope');
    sections.push('');
    const systemTypeLabel = AI_SYSTEM_TYPES.find(t => t.value === systemType)?.label || customSystemType;
    sections.push(`**System Type:** ${systemTypeLabel}`);
    if (systemDescription) {
      sections.push('');
      sections.push(`**Description:** ${systemDescription}`);
    }
    if (targetAudience) {
      sections.push('');
      sections.push(`**Target Audience:** ${targetAudience}`);
    }
    sections.push('');

    // Red Team Scenarios
    if (selectedRedTeamScenarios.length > 0 || customRedTeamScenarios) {
      sections.push('## 2. Red Team Scenarios & Adversarial Testing');
      sections.push('');
      sections.push('The system must be tested against the following adversarial scenarios:');
      sections.push('');

      selectedRedTeamScenarios.forEach(scenarioId => {
        const scenario = RED_TEAM_TEMPLATES.find(t => t.id === scenarioId);
        if (scenario) {
          sections.push(`### ${scenario.label}`);
          sections.push(scenario.description);
          sections.push('');
          sections.push('**Test Cases:**');
          scenario.examples.forEach(example => {
            sections.push(`- ${example}`);
          });
          sections.push('');
        }
      });

      if (customRedTeamScenarios) {
        sections.push('### Custom Scenarios');
        sections.push(customRedTeamScenarios);
        sections.push('');
      }
    }

    // Content Filters
    const enabledFilters = Object.entries(contentFilters).filter(([_, config]) => config.enabled);
    if (enabledFilters.length > 0) {
      sections.push('## 3. Content Filtering Policy');
      sections.push('');
      sections.push('The following content categories must be filtered:');
      sections.push('');

      enabledFilters.forEach(([categoryId, config]) => {
        const category = CONTENT_FILTER_CATEGORIES.find(c => c.id === categoryId);
        if (category) {
          sections.push(`### ${category.label}`);
          sections.push(`**Description:** ${category.description}`);
          sections.push(`**Action Threshold:** ${config.threshold.toUpperCase()}`);
          sections.push('');
        }
      });
    }

    // Ethical Boundaries
    if (ethicalPrinciples.length > 0) {
      sections.push('## 4. Ethical Boundaries & Principles');
      sections.push('');
      const framework = ETHICAL_FRAMEWORKS.find(f => f.id === selectedEthicalFramework);
      if (framework && framework.id !== 'custom') {
        sections.push(`**Framework:** ${framework.label}`);
        sections.push('');
      }
      sections.push('The AI system must adhere to the following ethical principles:');
      sections.push('');
      ethicalPrinciples.forEach((principle, index) => {
        sections.push(`${index + 1}. ${principle}`);
      });
      sections.push('');
    }

    // Fallback Behaviors
    const configuredFallbacks = Object.entries(fallbackBehaviors).filter(([_, behavior]) => behavior);
    if (configuredFallbacks.length > 0) {
      sections.push('## 5. Fallback Behaviors & Response Protocols');
      sections.push('');
      sections.push('When the AI encounters unsafe or inappropriate inputs, it should respond according to the following protocols:');
      sections.push('');

      configuredFallbacks.forEach(([riskType, behaviorId]) => {
        const behavior = FALLBACK_BEHAVIORS.find(b => b.id === behaviorId);
        if (behavior) {
          sections.push(`### ${riskType.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`);
          sections.push(`**Strategy:** ${behavior.label}`);
          sections.push(`**Example Response:** "${behavior.example}"`);
          sections.push('');
        }
      });

      sections.push(`**Escalation Threshold:** ${escalationThreshold.toUpperCase()}`);
      sections.push(`**Logging:** ${loggingEnabled ? 'Enabled - All unsafe interactions are logged for review' : 'Disabled'}`);
      sections.push('');
    }

    // Implementation Guidelines
    sections.push('## 6. Implementation Guidelines');
    sections.push('');
    sections.push('### Monitoring & Evaluation');
    sections.push('- Continuously monitor AI outputs for safety violations');
    sections.push('- Regularly review logged incidents');
    sections.push('- Update filters and policies based on emerging risks');
    sections.push('- Conduct periodic red team exercises');
    sections.push('');
    sections.push('### Human Oversight');
    sections.push('- Maintain human review for high-risk decisions');
    sections.push('- Provide clear escalation paths');
    sections.push('- Document all safety incidents');
    sections.push('- Regular audits of AI behavior');
    sections.push('');
    sections.push('### User Protection');
    sections.push('- Clear communication of AI capabilities and limitations');
    sections.push('- Transparent about when users are interacting with AI');
    sections.push('- Easy access to human support when needed');
    sections.push('- Respect user privacy and data protection');
    sections.push('');

    // Conclusion
    sections.push('## 7. Policy Review & Updates');
    sections.push('');
    sections.push('This safety policy should be reviewed and updated:');
    sections.push('- Quarterly, at minimum');
    sections.push('- After any significant safety incident');
    sections.push('- When new risks or attack vectors are identified');
    sections.push('- When the AI system undergoes major updates');
    sections.push('');
    sections.push('---');
    sections.push('');
    sections.push('*This document was generated using the SmartAI Memory Safety & Alignment Wizard.*');

    return sections.join('\n');
  };

  const renderStep = () => {
    const currentStep = wizardConfig.steps[wizard.currentStep];

    switch (currentStep.id) {
      case 'welcome':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🛡️</div>
              <h2 className="text-3xl font-bold mb-4">Safety & Alignment Wizard</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Create comprehensive safety guidelines and boundaries for your AI system. This wizard
                helps you define content filters, ethical principles, and response protocols to ensure
                your AI operates safely and responsibly.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">⚔️</div>
                <h3 className="font-semibold mb-2">Red Team Testing</h3>
                <p className="text-sm text-gray-400">Identify adversarial scenarios and test cases</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🚫</div>
                <h3 className="font-semibold mb-2">Content Filtering</h3>
                <p className="text-sm text-gray-400">Define what content should be blocked</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">⚖️</div>
                <h3 className="font-semibold mb-2">Ethical Alignment</h3>
                <p className="text-sm text-gray-400">Establish core ethical principles</p>
              </div>
            </div>

            <button
              onClick={() => {
                wizard.completeStep('welcome');
                wizard.nextStep();
              }}
              className="w-full mt-8 px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-medium text-lg hover:opacity-90 transition-opacity"
            >
              Get Started →
            </button>
          </div>
        );

      case 'scope':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Define Your AI System Scope</h2>
              <p className="text-gray-400">Describe the AI system and its intended use case</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">AI System Type *</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {AI_SYSTEM_TYPES.map((type) => (
                  <button
                    key={type.value}
                    onClick={() => setSystemType(type.value)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      systemType === type.value
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <div className="font-semibold mb-1">{type.label}</div>
                    <div className="text-sm text-gray-400">{type.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {systemType === 'custom' && (
              <div>
                <label className="block text-sm font-medium mb-2">Custom System Type *</label>
                <input
                  type="text"
                  value={customSystemType}
                  onChange={(e) => setCustomSystemType(e.target.value)}
                  placeholder="Describe your AI system type..."
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">System Description</label>
              <TextInputWithDictation
                multiline
                rows={4}
                value={systemDescription}
                onChange={(e) => setSystemDescription(e.target.value)}
                placeholder="Provide a detailed description of your AI system's purpose and functionality..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                enableDictation={true}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Target Audience</label>
              <input
                type="text"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="e.g., General public, Enterprise users, Healthcare professionals..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Risk Assessment Level *</label>
              <div className="grid grid-cols-4 gap-3">
                {(['low', 'medium', 'high', 'critical'] as const).map((level) => (
                  <button
                    key={level}
                    onClick={() => setRiskLevel(level)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      riskLevel === level
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <div className="font-semibold capitalize">{level}</div>
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Risk level determines the strictness of safety measures and monitoring
              </p>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!systemType && (systemType !== 'custom' || !!customSystemType)}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('scope');
                wizard.updateMultipleData({
                  systemType,
                  customSystemType,
                  systemDescription,
                  targetAudience,
                  riskLevel,
                });
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'red-team':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Red Team Scenarios</h2>
              <p className="text-gray-400">Select adversarial scenarios to test your AI system against</p>
            </div>

            <div className="space-y-3">
              {RED_TEAM_TEMPLATES.map((template) => (
                <div
                  key={template.id}
                  className={`p-4 rounded-lg border-2 transition-all cursor-pointer ${
                    selectedRedTeamScenarios.includes(template.id)
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                  onClick={() => toggleRedTeamScenario(template.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <input
                          type="checkbox"
                          checked={selectedRedTeamScenarios.includes(template.id)}
                          onChange={() => {}}
                          className="w-4 h-4"
                        />
                        <div className="font-semibold">{template.label}</div>
                      </div>
                      <p className="text-sm text-gray-400 mb-2">{template.description}</p>
                      <div className="text-xs text-gray-500">
                        <div className="font-medium mb-1">Example test cases:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {template.examples.map((example, idx) => (
                            <li key={idx}>{example}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Custom Red Team Scenarios <span className="text-gray-500">(Optional)</span>
              </label>
              <TextInputWithDictation
                multiline
                rows={5}
                value={customRedTeamScenarios}
                onChange={(e) => setCustomRedTeamScenarios(e.target.value)}
                placeholder="Add any additional adversarial scenarios specific to your use case..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                enableDictation={true}
              />
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">💡</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Pro Tip</div>
                  <div className="text-sm text-gray-300">
                    Regular red team testing helps identify vulnerabilities before bad actors can exploit them.
                    Consider running these tests quarterly or after major system updates.
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={selectedRedTeamScenarios.length > 0 || !!customRedTeamScenarios}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('red-team');
                wizard.updateMultipleData({
                  selectedRedTeamScenarios,
                  customRedTeamScenarios,
                });
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'content-filters':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Content Filtering Policy</h2>
              <p className="text-gray-400">Define which content categories to filter and at what threshold</p>
            </div>

            <div className="space-y-4">
              {CONTENT_FILTER_CATEGORIES.map((category) => {
                const isEnabled = contentFilters[category.id]?.enabled || false;
                const threshold = contentFilters[category.id]?.threshold || 'medium';

                return (
                  <div
                    key={category.id}
                    className="bg-gray-800 p-4 rounded-lg border border-gray-700"
                  >
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={isEnabled}
                        onChange={(e) => {
                          setContentFilters(prev => ({
                            ...prev,
                            [category.id]: {
                              enabled: e.target.checked,
                              threshold: prev[category.id]?.threshold || 'medium',
                            },
                          }));
                        }}
                        className="mt-1 w-4 h-4"
                      />
                      <div className="flex-1">
                        <div className="font-semibold mb-1">{category.label}</div>
                        <p className="text-sm text-gray-400 mb-3">{category.description}</p>

                        {isEnabled && (
                          <div>
                            <label className="block text-xs font-medium mb-2 text-gray-400">
                              Action Threshold:
                            </label>
                            <div className="flex gap-2">
                              {category.severity.map((level) => (
                                <button
                                  key={level}
                                  onClick={() => {
                                    setContentFilters(prev => ({
                                      ...prev,
                                      [category.id]: {
                                        enabled: true,
                                        threshold: level,
                                      },
                                    }));
                                  }}
                                  className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                                    threshold === level
                                      ? 'bg-primary text-white'
                                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                  }`}
                                >
                                  {level}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">⚠️</div>
                <div>
                  <div className="font-semibold text-yellow-400 mb-1">Important</div>
                  <div className="text-sm text-gray-300">
                    Lower thresholds catch more content but may have more false positives. Higher thresholds
                    are more permissive but may miss some violations. Adjust based on your risk tolerance.
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={Object.values(contentFilters).some(f => f.enabled)}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('content-filters');
                wizard.updateData('contentFilters', contentFilters);
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'ethical-boundaries':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Ethical Boundaries & Principles</h2>
              <p className="text-gray-400">Choose an ethical framework or define your own principles</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Ethical Framework *</label>
              <div className="space-y-3">
                {ETHICAL_FRAMEWORKS.map((framework) => (
                  <button
                    key={framework.id}
                    onClick={() => {
                      setSelectedEthicalFramework(framework.id);
                      if (framework.id !== 'custom') {
                        setEthicalPrinciples(framework.principles);
                      } else {
                        setEthicalPrinciples([]);
                      }
                    }}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      selectedEthicalFramework === framework.id
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <div className="font-semibold mb-1">{framework.label}</div>
                    <p className="text-sm text-gray-400 mb-2">{framework.description}</p>
                    {framework.principles.length > 0 && (
                      <ul className="text-xs text-gray-500 space-y-1 mt-2">
                        {framework.principles.map((principle, idx) => (
                          <li key={idx}>• {principle}</li>
                        ))}
                      </ul>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {selectedEthicalFramework === 'custom' && (
              <div>
                <label className="block text-sm font-medium mb-2">Define Your Principles *</label>
                <div className="space-y-3">
                  {customPrinciples.map((principle, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={principle}
                        onChange={(e) => {
                          const newPrinciples = [...customPrinciples];
                          newPrinciples[index] = e.target.value;
                          setCustomPrinciples(newPrinciples);
                          setEthicalPrinciples(newPrinciples.filter(p => p.trim()));
                        }}
                        placeholder={`Principle ${index + 1}`}
                        className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                      />
                      {customPrinciples.length > 1 && (
                        <button
                          onClick={() => {
                            const newPrinciples = customPrinciples.filter((_, i) => i !== index);
                            setCustomPrinciples(newPrinciples);
                            setEthicalPrinciples(newPrinciples.filter(p => p.trim()));
                          }}
                          className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-red-400 rounded-lg"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => setCustomPrinciples([...customPrinciples, ''])}
                    className="w-full py-2 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
                  >
                    + Add Principle
                  </button>
                </div>
              </div>
            )}

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!selectedEthicalFramework && ethicalPrinciples.length > 0}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('ethical-boundaries');
                wizard.updateMultipleData({
                  selectedEthicalFramework,
                  ethicalPrinciples,
                });
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'fallback-behaviors':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Fallback Behaviors</h2>
              <p className="text-gray-400">Define how your AI should respond to unsafe or inappropriate inputs</p>
            </div>

            <div className="space-y-4">
              {[
                { id: 'harmful-content', label: 'Harmful Content' },
                { id: 'inappropriate-requests', label: 'Inappropriate Requests' },
                { id: 'jailbreak-attempts', label: 'Jailbreak Attempts' },
                { id: 'privacy-violations', label: 'Privacy Violations' },
                { id: 'misinformation', label: 'Misinformation Requests' },
              ].map((riskType) => (
                <div key={riskType.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                  <label className="block text-sm font-medium mb-2">{riskType.label}</label>
                  <select
                    value={fallbackBehaviors[riskType.id] || ''}
                    onChange={(e) => {
                      setFallbackBehaviors(prev => ({
                        ...prev,
                        [riskType.id]: e.target.value,
                      }));
                    }}
                    className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                  >
                    <option value="">Select behavior...</option>
                    {FALLBACK_BEHAVIORS.map((behavior) => (
                      <option key={behavior.id} value={behavior.id}>
                        {behavior.label}
                      </option>
                    ))}
                  </select>
                  {fallbackBehaviors[riskType.id] && (
                    <div className="mt-2 text-xs text-gray-400">
                      <strong>Example:</strong> "
                      {FALLBACK_BEHAVIORS.find(b => b.id === fallbackBehaviors[riskType.id])?.example}
                      "
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <label className="block text-sm font-medium mb-2">Escalation Threshold</label>
              <select
                value={escalationThreshold}
                onChange={(e) => setEscalationThreshold(e.target.value)}
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
              >
                <option value="low">Low - Escalate frequently</option>
                <option value="medium">Medium - Balanced approach</option>
                <option value="high">High - Escalate only critical issues</option>
              </select>
              <p className="text-xs text-gray-500 mt-2">
                Determines when to escalate issues to human moderators
              </p>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={loggingEnabled}
                  onChange={(e) => setLoggingEnabled(e.target.checked)}
                  className="w-4 h-4"
                />
                <div>
                  <div className="font-medium">Enable Safety Logging</div>
                  <div className="text-xs text-gray-400">
                    Log all unsafe interactions for review and system improvement
                  </div>
                </div>
              </label>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={Object.keys(fallbackBehaviors).length >= 3}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('fallback-behaviors');
                wizard.updateMultipleData({
                  fallbackBehaviors,
                  escalationThreshold,
                  loggingEnabled,
                });
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'review':
        const safetyPolicy = generateSafetyPolicy();

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Safety Policy Summary</h2>
              <p className="text-gray-400">Review and export your comprehensive safety guidelines</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Red Team Scenarios</div>
                <div className="text-3xl font-bold">{selectedRedTeamScenarios.length}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Content Filters</div>
                <div className="text-3xl font-bold">
                  {Object.values(contentFilters).filter(f => f.enabled).length}
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Ethical Principles</div>
                <div className="text-3xl font-bold">{ethicalPrinciples.length}</div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Generated Safety Policy</h3>
                <button
                  onClick={() => setShowOutput(!showOutput)}
                  className="text-sm text-primary hover:text-primary/80"
                >
                  {showOutput ? 'Hide' : 'Show'} Preview
                </button>
              </div>

              {showOutput && (
                <pre className="bg-gray-900 p-4 rounded text-sm overflow-x-auto whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {safetyPolicy}
                </pre>
              )}
            </div>

            <WizardExport
              formats={wizardConfig.exportFormats}
              content={safetyPolicy}
              filename={`safety-policy-${Date.now()}`}
            />

            <div className="bg-green-900/20 border border-green-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">✓</div>
                <div>
                  <div className="font-semibold text-green-400 mb-1">Next Steps</div>
                  <div className="text-sm text-gray-300">
                    <ul className="list-disc list-inside space-y-1">
                      <li>Review the policy with your team and stakeholders</li>
                      <li>Implement the content filters and fallback behaviors</li>
                      <li>Run the red team scenarios to test your system</li>
                      <li>Schedule regular policy reviews and updates</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => {
                  wizard.clearData();
                  wizard.goToStep(0);
                }}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                Create Another Policy
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('review');
                  toast.success('Safety policy complete! 🛡️');
                }}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-secondary hover:opacity-90 rounded-lg font-medium transition-opacity"
              >
                Complete Wizard
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <WizardLayout
      config={wizardConfig}
      currentStep={wizard.currentStep}
      totalSteps={wizardConfig.steps.length}
      progress={wizard.progress}
      onStepClick={wizard.goToStep}
    >
      {renderStep()}
    </WizardLayout>
  );
}
