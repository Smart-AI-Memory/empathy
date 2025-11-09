/**
 * Wizards API Route - List all available wizards
 * Proxies requests to the backend FastAPI server
 */

export const dynamic = 'force-dynamic';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/wizards/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();

    return Response.json(data);
  } catch (error) {
    console.error('Error fetching wizards:', error);

    // Return mock data for development if backend is unavailable
    return Response.json({
      wizards: [
        {
          name: 'SBAR Wizard',
          category: 'healthcare',
          description: 'Situation-Background-Assessment-Recommendation clinical communication',
          capabilities: ['clinical_communication', 'patient_handoff'],
        },
        {
          name: 'SOAP Note Wizard',
          category: 'healthcare',
          description: 'Subjective-Objective-Assessment-Plan clinical documentation',
          capabilities: ['clinical_documentation', 'patient_notes'],
        },
        {
          name: 'Security Analysis Wizard',
          category: 'software',
          description: 'Analyzes code for security vulnerabilities and compliance',
          capabilities: ['security_scanning', 'vulnerability_detection'],
        },
        {
          name: 'Testing Wizard',
          category: 'software',
          description: 'Generates comprehensive test suites and coverage analysis',
          capabilities: ['test_generation', 'coverage_analysis'],
        },
      ],
    });
  }
}
