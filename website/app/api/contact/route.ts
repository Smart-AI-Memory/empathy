import { NextRequest, NextResponse } from 'next/server';
import { sendContactFormEmail } from '@/lib/email/sendgrid';
import { createContact } from '@/lib/db';

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

    // Store in database
    let dbSuccess = false;
    let contactId: number | null = null;
    try {
      const contact = await createContact({
        name,
        email,
        company,
        topic,
        message,
        metadata: {
          userAgent: request.headers.get('user-agent'),
          ip: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
        },
      });
      dbSuccess = true;
      contactId = contact.id;
      console.log('Contact saved to database:', contact.id);
    } catch (dbError) {
      console.error('Database error (continuing anyway):', dbError);
    }

    // Send email via SendGrid
    const emailSent = await sendContactFormEmail({
      name,
      email,
      company,
      topic,
      message,
    });

    if (!emailSent && process.env.SENDGRID_API_KEY) {
      console.warn('Failed to send contact form email, but returning success to user');
    }

    // Log summary
    console.log('Contact form complete:', {
      contactId,
      database: dbSuccess,
      emailNotification: emailSent,
    });

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
