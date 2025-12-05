import { NextRequest, NextResponse } from 'next/server';

// Demo endpoint for medication interaction checking
// Full implementation lives in empathy-healthcare-plugin (separate PyPI package)
export async function POST(request: NextRequest) {
  try {
    const { medications } = await request.json();

    if (!medications) {
      return NextResponse.json({ error: 'Medications text required' }, { status: 400 });
    }

    const text = medications.toLowerCase();

    // Demo: Extract common medication names
    const commonMeds = [
      'metformin', 'lisinopril', 'amlodipine', 'metoprolol', 'atorvastatin',
      'omeprazole', 'aspirin', 'warfarin', 'heparin', 'insulin', 'prednisone',
      'furosemide', 'hydrochlorothiazide', 'levothyroxine', 'gabapentin',
    ];

    const found = commonMeds.filter(med => text.includes(med));

    // Demo interactions (educational only)
    const demoInteractions = [];

    if (text.includes('warfarin') && text.includes('aspirin')) {
      demoInteractions.push({
        drug1: 'Warfarin',
        drug2: 'Aspirin',
        severity: 'major' as const,
        description: 'Increased bleeding risk when combined',
      });
    }

    if (text.includes('metformin') && text.includes('contrast')) {
      demoInteractions.push({
        drug1: 'Metformin',
        drug2: 'IV Contrast',
        severity: 'major' as const,
        description: 'Risk of lactic acidosis; hold metformin before/after contrast',
      });
    }

    if (text.includes('lisinopril') && text.includes('potassium')) {
      demoInteractions.push({
        drug1: 'Lisinopril',
        drug2: 'Potassium',
        severity: 'moderate' as const,
        description: 'Risk of hyperkalemia; monitor potassium levels',
      });
    }

    return NextResponse.json({
      success: true,
      has_interactions: demoInteractions.length > 0,
      has_major_interactions: demoInteractions.some(i => i.severity === 'major'),
      total_interactions: demoInteractions.length,
      interactions: demoInteractions,
      medications_found: found,
      demo_note: 'This is a demo. Full drug interaction database available in empathy-healthcare-plugin.',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Medication check failed', details: String(error) },
      { status: 500 }
    );
  }
}
