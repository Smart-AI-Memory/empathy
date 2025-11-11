import { NextRequest, NextResponse } from 'next/server';
import { sendContactFormEmail } from '@/lib/email/sendgrid';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, company, topic, message } = body;

    // Validate required fields
    if (!name || !email || !topic || !message) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      );
    }

    // Log submission
    console.log('Contact form submission:', {
      name,
      email,
      company,
      topic,
      message,
      timestamp: new Date().toISOString(),
    });

    // Send email via SendGrid
    // If SendGrid is not configured, it will log an error but still return success
    const emailSent = await sendContactFormEmail({
      name,
      email,
      company,
      topic,
      message,
    });

    if (!emailSent && process.env.SENDGRID_API_KEY) {
      // If SendGrid is configured but email failed, log warning
      console.warn('Failed to send contact form email, but returning success to user');
    }

    return NextResponse.json(
      {
        success: true,
        message: 'Thank you! We will get back to you within 24-48 hours.',
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Contact form error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Handle OPTIONS for CORS if needed
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
