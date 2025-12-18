import { NextRequest, NextResponse } from 'next/server';
import { sendNewsletterConfirmation } from '@/lib/email/sendgrid';
import { subscribeToMailchimp } from '@/lib/email/mailchimp';
import { createSubscriber, updateSubscriberMailchimpId } from '@/lib/db';

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

    // Store in database
    let dbSuccess = false;
    try {
      const { subscriber, created } = await createSubscriber({
        email,
        source: 'website',
        tags: ['newsletter'],
      });
      dbSuccess = true;
      console.log(`Subscriber ${created ? 'created' : 'already exists'}:`, subscriber.email);
    } catch (dbError) {
      console.error('Database error (continuing anyway):', dbError);
    }

    // Sync to Mailchimp
    let mailchimpSuccess = false;
    const mailchimpResult = await subscribeToMailchimp({ email });
    if (mailchimpResult.success) {
      mailchimpSuccess = true;
      console.log('Mailchimp subscription successful');

      // Update subscriber with Mailchimp ID if we have it
      if (mailchimpResult.id && dbSuccess) {
        try {
          await updateSubscriberMailchimpId(email, mailchimpResult.id);
        } catch (updateError) {
          console.error('Failed to update Mailchimp ID:', updateError);
        }
      }
    } else {
      console.warn('Mailchimp subscription failed:', mailchimpResult.error);
    }

    // Send confirmation email via SendGrid
    const emailSent = await sendNewsletterConfirmation(email);
    if (!emailSent && process.env.SENDGRID_API_KEY) {
      console.warn('Failed to send newsletter confirmation email');
    }

    // Log summary
    console.log('Newsletter subscription complete:', {
      email,
      database: dbSuccess,
      mailchimp: mailchimpSuccess,
      confirmationEmail: emailSent,
    });

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
export async function OPTIONS(_request: NextRequest) {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
