import { NextRequest, NextResponse } from 'next/server';

// Demo endpoint for AI text enhancement
// Full implementation lives in empathy-healthcare-plugin (separate PyPI package)
export async function POST(request: NextRequest) {
  try {
    const { text, section } = await request.json();

    if (!text) {
      return NextResponse.json({ error: 'Text is required' }, { status: 400 });
    }

    // Demo: Return slightly enhanced version (real implementation uses Claude AI)
    const enhanced = text
      .replace(/pt\b/gi, 'patient')
      .replace(/hx\b/gi, 'history')
      .replace(/dx\b/gi, 'diagnosis')
      .replace(/tx\b/gi, 'treatment')
      .replace(/rx\b/gi, 'prescription')
      .replace(/sx\b/gi, 'symptoms')
      .replace(/sob\b/gi, 'shortness of breath')
      .replace(/bp\b/gi, 'blood pressure')
      .replace(/hr\b/gi, 'heart rate')
      .replace(/rr\b/gi, 'respiratory rate');

    return NextResponse.json({
      success: true,
      original: text,
      enhanced: enhanced,
      section: section,
      demo_note: 'This is a demo. Full AI enhancement available in empathy-healthcare-plugin.',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Enhancement failed', details: String(error) },
      { status: 500 }
    );
  }
}
