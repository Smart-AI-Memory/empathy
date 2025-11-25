import { useState } from 'react'

interface FAQItem {
  question: string
  answer: string
  category: string
}

const faqData: FAQItem[] = [
  // General Questions
  {
    category: 'General',
    question: 'What is the Empathy Wizard Dashboard?',
    answer: 'The Empathy Wizard Dashboard showcases 43 specialized AI wizards across domain, software, and AI categories. Each wizard provides intelligent analysis for specific use cases - from healthcare compliance to code security to AI system optimization.'
  },
  {
    category: 'General',
    question: 'What makes these wizards unique?',
    answer: 'Each wizard combines Level 4-5 Anticipatory Empathy with domain-specific expertise. They predict problems 30-90 days ahead, learn your patterns, and provide actionable recommendations - not just generic AI responses.'
  },
  {
    category: 'General',
    question: 'How many wizards are available?',
    answer: '43 wizards total: 16 domain-specific wizards (healthcare, finance, education, etc.), 16 software development wizards (security, testing, debugging, etc.), and 11 advanced AI wizards (multi-model, RAG, agent orchestration, etc.).'
  },

  // Using the Dashboard
  {
    category: 'Using the Dashboard',
    question: 'How do I try a wizard demo?',
    answer: 'Click "Try Demo" on any wizard card. Each demo is interactive - you can upload your own files, paste code or data, or load sample data. The wizard will analyze your input and provide detailed insights.'
  },
  {
    category: 'Using the Dashboard',
    question: 'Can I upload my own files?',
    answer: 'Yes! Most wizards support file upload. Click the "📁 Upload File" button in the demo area. Supported file types vary by wizard - code files (.py, .js, .ts, etc.) for software wizards, documents (.txt, .csv, .pdf, etc.) for domain wizards.'
  },
  {
    category: 'Using the Dashboard',
    question: 'How do I filter wizards?',
    answer: 'Use the filter bar (desktop) or Filter button (mobile) to narrow by category, empathy level, or compliance requirements. You can also search for specific wizards using the search bar.'
  },
  {
    category: 'Using the Dashboard',
    question: 'What are empathy levels?',
    answer: 'Level 1: Responsive (simple Q&A), Level 2: Adaptive (learns preferences), Level 3: Proactive (suggests improvements), Level 4: Anticipatory (predicts problems 30-90 days ahead), Level 5: Systems Empathy (cross-domain pattern recognition).'
  },

  // Technical Details
  {
    category: 'Technical',
    question: 'Is the backend API required?',
    answer: 'Yes. The dashboard connects to a FastAPI backend running at http://localhost:8001. Start it with: python backend/api/wizard_api.py'
  },
  {
    category: 'Technical',
    question: 'What LLM providers are supported?',
    answer: 'Anthropic Claude (recommended), OpenAI GPT-4, and local models via Ollama. Set your API key: export ANTHROPIC_API_KEY=your-key-here'
  },
  {
    category: 'Technical',
    question: 'How accurate are Level 4 predictions?',
    answer: '70-85% accuracy for security predictions, 65-80% for performance predictions. Accuracy improves with more context (code patterns, metrics, team size, growth rate).'
  },
  {
    category: 'Technical',
    question: 'Can I customize the wizards?',
    answer: 'Yes! All wizards are extensible. You can modify patterns, add custom rules, or create entirely new wizards using the BaseWizard class. See the Empathy Framework documentation for details.'
  },

  // Security & Privacy
  {
    category: 'Security & Privacy',
    question: 'Is my data secure?',
    answer: 'Yes. Domain wizards use enterprise-grade security with PII detection, secrets scrubbing, and audit logging. Data is processed locally by default - nothing is stored or transmitted without your control.'
  },
  {
    category: 'Security & Privacy',
    question: 'Do domain wizards store sensitive data?',
    answer: 'No. Domain wizards (healthcare, finance, HR, etc.) detect and redact PII before processing. All sensitive data is scrubbed using advanced pattern matching and entropy analysis.'
  },
  {
    category: 'Security & Privacy',
    question: 'Can I use this with confidential code?',
    answer: 'Yes. Use local LLMs (Ollama) to ensure code never leaves your machine. Or use cloud LLMs with enterprise tiers that guarantee no training on your data.'
  },

  // Troubleshooting
  {
    category: 'Troubleshooting',
    question: 'Wizard demos show "API connection error" - what should I do?',
    answer: 'The backend API is not running. Start it with: python backend/api/wizard_api.py. Make sure you are in the correct directory and have all dependencies installed.'
  },
  {
    category: 'Troubleshooting',
    question: 'File upload is not working - why?',
    answer: 'Check that: 1) File type is supported for that wizard, 2) File size is reasonable (<10MB), 3) Browser allows file reading (check permissions).'
  },
  {
    category: 'Troubleshooting',
    question: 'Analysis is taking too long - how can I speed it up?',
    answer: 'Use a faster model (Claude Haiku instead of Sonnet, or GPT-3.5 instead of GPT-4), reduce input size, or enable caching in the backend configuration.'
  },
  {
    category: 'Troubleshooting',
    question: 'Where can I get help?',
    answer: 'Check the documentation at docs/USER_GUIDE.md, search GitHub issues, or contact support@deepstudyai.com for commercial support.'
  },

  // Pricing & Licensing
  {
    category: 'Pricing & Licensing',
    question: 'Is this free to use?',
    answer: 'Yes! The Empathy Framework is Fair Source 0.9 licensed - completely free forever with no usage limits. You only pay for LLM API costs (if using cloud providers).'
  },
  {
    category: 'Pricing & Licensing',
    question: 'How much do LLM API calls cost?',
    answer: 'Anthropic Claude: ~$5-20/month for active development. OpenAI GPT-4: ~$15-50/month. Local models (Ollama): $0 - completely free.'
  },
  {
    category: 'Pricing & Licensing',
    question: 'Can I use this commercially?',
    answer: 'Yes! Fair Source 0.9 allows commercial use without restrictions. Build products, charge customers, keep modifications private - no copyleft requirements.'
  }
]

export function FAQPage({ onClose }: { onClose: () => void }) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  const categories = ['all', ...Array.from(new Set(faqData.map(item => item.category)))]

  const filteredFAQs = selectedCategory === 'all'
    ? faqData
    : faqData.filter(item => item.category === selectedCategory)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
          <div className="flex items-center gap-3">
            <span className="text-2xl">❓</span>
            <h2 className="text-2xl font-bold text-gray-900">Frequently Asked Questions</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
            aria-label="Close FAQ"
          >
            ×
          </button>
        </div>

        {/* Category Filter */}
        <div className="px-6 py-4 border-b bg-gray-50 overflow-x-auto">
          <div className="flex gap-2 flex-wrap">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap ${
                  selectedCategory === category
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                {category === 'all' ? 'All Questions' : category}
              </button>
            ))}
          </div>
        </div>

        {/* FAQ List */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-3">
            {filteredFAQs.map((faq, index) => (
              <div
                key={index}
                className="border-2 border-gray-200 rounded-lg overflow-hidden hover:border-primary-400 transition-colors"
              >
                <button
                  onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                  className="w-full px-4 py-3 text-left flex items-center justify-between gap-3 bg-white hover:bg-gray-50 transition-colors"
                >
                  <span className="font-medium text-gray-900">{faq.question}</span>
                  <span className={`text-2xl text-primary-600 transform transition-transform ${
                    expandedIndex === index ? 'rotate-180' : ''
                  }`}>
                    ▼
                  </span>
                </button>
                {expandedIndex === index && (
                  <div className="px-4 py-3 bg-gray-50 border-t-2 border-gray-200">
                    <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                    {faq.category !== 'General' && (
                      <div className="mt-2">
                        <span className="inline-block px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
                          {faq.category}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50">
          <p className="text-sm text-gray-600 text-center">
            Still have questions? Contact us at{' '}
            <a href="mailto:support@deepstudyai.com" className="text-primary-600 hover:text-primary-700 font-medium">
              support@deepstudyai.com
            </a>
            {' '}or check the{' '}
            <a
              href="https://github.com/Deep-Study-AI/Empathy/tree/main/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              full documentation
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
