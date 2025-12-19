import { NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { storeWizardSession, type WizardSession } from '@/lib/redis';

export async function POST() {
  try {
    const wizardId = `wizard_${randomUUID()}`;
    const now = new Date();
    const expiresAt = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour expiry

    const sessionData: WizardSession = {
      wizard_id: wizardId,
      wizard_type: 'sbar',
      current_step: 1,
      total_steps: 4,
      collected_data: {},
      created_at: now.toISOString(),
      updated_at: now.toISOString(),
      expires_at: expiresAt.toISOString(),
    };

    // Store session in Redis (falls back to in-memory if unavailable)
    await storeWizardSession(sessionData);

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
