/**
 * Wizard Invocation API Route
 * Handles wizard execution requests
 */

export const dynamic = 'force-dynamic';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { wizard_name, input_data } = body;

    if (!wizard_name) {
      return Response.json(
        { error: 'wizard_name is required' },
        { status: 400 }
      );
    }

    const response = await fetch(`${BACKEND_URL}/api/wizards/${wizard_name}/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input_data }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return Response.json(
        { error: errorData.detail || 'Failed to invoke wizard' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return Response.json(data);
  } catch (error) {
    console.error('Error invoking wizard:', error);

    // Return mock response for development
    return Response.json({
      result: {
        output: 'This is a demo response. Connect to the backend API for real wizard execution.',
        status: 'demo',
        wizard_name: 'Demo Wizard',
      },
    });
  }
}
