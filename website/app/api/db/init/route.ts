import { NextRequest, NextResponse } from 'next/server';
import { initializeDatabase } from '@/lib/db';

// This endpoint initializes the database schema
// Should only be called once during setup, protected by a secret
export async function POST(req: NextRequest) {
  try {
    // Check for admin secret
    const { secret } = await req.json();

    if (secret !== process.env.ADMIN_SECRET) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    if (!process.env.DATABASE_URL) {
      return NextResponse.json(
        { error: 'DATABASE_URL is not configured' },
        { status: 500 }
      );
    }

    await initializeDatabase();

    return NextResponse.json({
      success: true,
      message: 'Database schema initialized successfully',
    });
  } catch (error) {
    console.error('Database initialization error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
