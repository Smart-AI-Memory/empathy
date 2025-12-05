/**
 * Wizards API Route - List all available wizard dashboards
 * Points to external dashboards with working wizards
 */

export const dynamic = 'force-dynamic';

export async function GET() {
  return Response.json({
    wizards: [
      {
        name: 'Healthcare Wizards',
        category: 'healthcare',
        external_url: 'https://healthcare.smartaimemory.com/static/dashboard.html',
        description: '23 clinical wizards for SBAR, patient assessment, medication safety, and more',
        count: 23,
        capabilities: ['clinical_communication', 'patient_handoff', 'medication_safety', 'risk_assessment'],
      },
      {
        name: 'Tech & AI Wizards',
        category: 'development',
        external_url: 'https://wizards.smartaimemory.com/',
        description: 'Software development, AI collaboration, debugging, testing, and performance wizards',
        count: 16,
        capabilities: ['debugging', 'testing', 'security_scanning', 'performance_optimization', 'ai_collaboration'],
      },
    ],
  });
}
