import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { patient_id, situation, background, assessment, recommendation, care_setting = 'med-surg' } = body;

    // Validate required fields
    if (!situation || !background || !assessment || !recommendation) {
      return NextResponse.json(
        {
          success: false,
          error: 'All SBAR components (situation, background, assessment, recommendation) are required.',
        },
        { status: 400 }
      );
    }

    // Care setting context
    const careSettingContext: Record<string, string> = {
      'icu': 'critical care setting with focus on hemodynamic stability and ventilator management',
      'emergency': 'emergency department with focus on rapid assessment and triage',
      'home-health': 'home health setting with focus on patient/caregiver education and safety',
      'med-surg': 'medical-surgical unit with focus on routine monitoring and care coordination',
    };

    const context = careSettingContext[care_setting] || 'general clinical setting';

    // Generate SBAR report (basic version without AI)
    const timestamp = new Date().toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    const sbarReport = `SBAR Clinical Handoff Report
Patient ID: ${patient_id}
Care Setting: ${context.toUpperCase()}
Generated: ${timestamp}

═══════════════════════════════════════════════════════

SITUATION
${situation}

BACKGROUND
${background}

ASSESSMENT
${assessment}

RECOMMENDATION
${recommendation}

═══════════════════════════════════════════════════════

Report Type: SBAR (Situation, Background, Assessment, Recommendation)
Framework: Empathy Framework v1.8.0-beta
Compliance: HIPAA-ready (PHI should be de-identified before LLM processing)

This report follows standardized clinical communication protocols for
safe and effective patient handoffs in a ${context}.
`;

    return NextResponse.json({
      success: true,
      sbar_report: sbarReport,
      care_setting,
      patient_id,
      generated_at: timestamp,
    });
  } catch (error) {
    console.error('Error generating SBAR report:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to generate SBAR report',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
