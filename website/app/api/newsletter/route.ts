import { NextRequest, NextResponse } from 'next/server';
import { sendNewsletterConfirmation } from '@/lib/email/sendgrid';
// Alternative: import { subscribeToMailchimp } from '@/lib/email/mailchimp';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email } = body;

    // Validate email
    if (!email) {
      return NextResponse.json(
        { error: 'Email is required' },
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

    // Log subscription
    console.log('Newsletter subscription:', {
      email,
      timestamp: new Date().toISOString(),
      source: 'website',
    });

    // Send confirmation email via SendGrid
    // Alternative: Use Mailchimp
    // const subscribed = await subscribeToMailchimp({ email });

    const emailSent = await sendNewsletterConfirmation(email);

    if (!emailSent && process.env.SENDGRID_API_KEY) {
      console.warn('Failed to send newsletter confirmation, but returning success to user');
    }

    // TODO: Store in database for your own newsletter management
    // await db.newsletterSubscribers.create({
    //   data: {
    //     email,
    //     subscribedAt: new Date(),
    //     source: 'website',
    //     confirmed: false,
    //   },
    // });

    return NextResponse.json(
      {
        success: true,
        message: 'Successfully subscribed! Check your email for confirmation.',
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Newsletter subscription error:', error);
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
