import { NextRequest, NextResponse } from 'next/server';

// Demo endpoint for priority suggestion
// Full implementation lives in empathy-healthcare-plugin (separate PyPI package)
export async function POST(request: NextRequest) {
  try {
    const { vital_signs, clinical_concerns } = await request.json();

    const text = `${vital_signs || ''} ${clinical_concerns || ''}`.toLowerCase();

    // Demo priority logic based on keywords
    let suggested_priority: 'stat' | 'urgent' | 'routine' = 'routine';
    let reasoning = 'Based on clinical assessment, routine monitoring appropriate.';

    // STAT indicators
    const statKeywords = ['unresponsive', 'cardiac arrest', 'not breathing', 'code', 'emergency', 'critical'];
    if (statKeywords.some(kw => text.includes(kw))) {
      suggested_priority = 'stat';
      reasoning = 'Critical indicators detected. Immediate intervention required.';
    }
    // Urgent indicators
    else if (text.includes('chest pain') || text.includes('difficulty breathing') ||
             text.includes('severe') || text.includes('acute') || text.includes('deteriorat') ||
             text.includes('distress') || text.includes('altered mental')) {
      suggested_priority = 'urgent';
      reasoning = 'Significant clinical concerns identified. Prompt evaluation recommended.';
    }

    return NextResponse.json({
      success: true,
      suggested_priority,
      reasoning,
      demo_note: 'This is a demo. Full AI priority assessment available in empathy-healthcare-plugin.',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Priority check failed', details: String(error) },
      { status: 500 }
    );
  }
}
