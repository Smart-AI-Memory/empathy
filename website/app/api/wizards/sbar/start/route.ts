import { NextResponse } from 'next/server';

export async function POST() {
  try {
    const wizardId = `wizard_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const sessionData = {
      wizard_id: wizardId,
      wizard_type: 'sbar',
      current_step: 1,
      total_steps: 4,
      collected_data: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return NextResponse.json({
      success: true,
      data: {
        wizard_session: sessionData,
        current_step: {
          step_number: 1,
          step_name: 'Situation',
          title: 'Current Situation',
          description: 'Describe the current patient situation and immediate concerns',
        },
        progress: {
          current: 1,
          total: 4,
          percentage: 25,
        },
      },
      message: 'SBAR documentation wizard started successfully',
    });
  } catch (error) {
    console.error('Error starting SBAR wizard:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to start SBAR wizard',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
