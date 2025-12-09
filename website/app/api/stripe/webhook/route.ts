import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import {
  initializeDatabase,
  findOrCreateCustomer,
  createPurchase,
  createLicense,
  createDownloadToken,
} from '@/lib/db';
import {
  generateLicenseKey,
  generateDownloadToken,
  calculateLicenseExpiration,
  calculateDownloadExpiration,
  getProductTypeFromPriceId,
} from '@/lib/license';
import {
  sendLicenseEmail,
  sendBookEmail,
  sendContributionEmail,
} from '@/lib/email';

// Lazy initialization to avoid build-time errors
let stripe: Stripe | null = null;
let dbInitialized = false;

function getStripe(): Stripe {
  if (!stripe) {
    if (!process.env.STRIPE_SECRET_KEY) {
      throw new Error('STRIPE_SECRET_KEY is not configured');
    }
    stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  }
  return stripe;
}

async function ensureDbInitialized(): Promise<void> {
  if (!dbInitialized && process.env.DATABASE_URL) {
    await initializeDatabase();
    dbInitialized = true;
  }
}

// Disable body parsing - we need the raw body for signature verification
export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  const body = await req.text();
  const sig = req.headers.get('stripe-signature');

  if (!sig) {
    console.error('Missing stripe-signature header');
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  let event: Stripe.Event;

  try {
    event = getStripe().webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('Webhook signature verification failed:', errorMessage);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  // Handle the event
  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;

        console.log('Payment successful:', {
          sessionId: session.id,
          customerEmail: session.customer_email,
          amountTotal: session.amount_total,
          paymentStatus: session.payment_status,
        });

        // Only process if payment was successful
        if (session.payment_status !== 'paid') {
          console.log('Payment not yet completed, skipping fulfillment');
          break;
        }

        // Get line items to determine what was purchased
        const lineItems = await getStripe().checkout.sessions.listLineItems(session.id);
        const priceId = lineItems.data[0]?.price?.id;

        if (!priceId) {
          console.error('No price ID found in session');
          break;
        }

        const productInfo = getProductTypeFromPriceId(priceId);

        // Check if database is configured
        if (!process.env.DATABASE_URL) {
          console.log('DATABASE_URL not configured - logging only, no persistence');
          console.log('Product purchased:', productInfo);
          // Still try to send emails if Resend is configured
          if (process.env.RESEND_API_KEY && session.customer_email) {
            await handleEmailOnlyFulfillment(session, productInfo);
          }
          break;
        }

        // Initialize database if needed
        await ensureDbInitialized();

        // Get customer email - check both locations
        const customerEmail = session.customer_email || session.customer_details?.email;
        if (!customerEmail) {
          console.error('No customer email found in session');
          break;
        }

        // Create or find customer
        const customer = await findOrCreateCustomer(
          customerEmail,
          session.customer as string,
          session.customer_details?.name || undefined
        );

        // Create purchase record
        const purchase = await createPurchase({
          customerId: customer.id,
          stripeSessionId: session.id,
          stripePaymentIntent: session.payment_intent as string,
          productType: productInfo.type,
          productName: productInfo.name,
          amountCents: session.amount_total!,
          currency: session.currency || 'usd',
          metadata: {
            priceId,
            customerName: session.customer_details?.name,
          },
        });

        console.log('Purchase recorded:', purchase.id);

        // Handle fulfillment based on product type
        if (productInfo.type === 'book') {
          await handleBookPurchase(customer, purchase, session);
        } else if (productInfo.type === 'license') {
          await handleLicensePurchase(customer, purchase, session);
        } else if (productInfo.type === 'contribution') {
          await handleContribution(customer, purchase, session);
        }

        break;
      }

      case 'customer.subscription.created': {
        const subscription = event.data.object as Stripe.Subscription;
        console.log('Subscription created:', {
          subscriptionId: subscription.id,
          customerId: subscription.customer,
          status: subscription.status,
        });
        // Subscription handling could be added here
        break;
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;
        console.log('Subscription updated:', {
          subscriptionId: subscription.id,
          status: subscription.status,
        });
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;
        console.log('Subscription cancelled:', {
          subscriptionId: subscription.id,
          customerId: subscription.customer,
        });
        // Could mark licenses as expired here
        break;
      }

      case 'invoice.paid': {
        const invoice = event.data.object as Stripe.Invoice;
        console.log('Invoice paid:', {
          invoiceId: invoice.id,
          customerId: invoice.customer,
          amountPaid: invoice.amount_paid,
        });
        // Could extend license period here for subscription renewals
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice;
        console.log('Invoice payment failed:', {
          invoiceId: invoice.id,
          customerId: invoice.customer,
        });
        // Could send payment failed notification
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Error processing webhook:', error);
    return NextResponse.json({ error: 'Webhook handler failed' }, { status: 500 });
  }
}

// Handle book purchase - includes license + download links
async function handleBookPurchase(
  customer: { id: number; email: string; name: string | null },
  purchase: { id: number },
  session: Stripe.Checkout.Session
): Promise<void> {
  // Generate license key
  const licenseKey = generateLicenseKey('EMPATHY');
  const licenseExpiration = calculateLicenseExpiration(1); // 1 year

  // Create license record
  const license = await createLicense({
    customerId: customer.id,
    purchaseId: purchase.id,
    licenseKey,
    product: 'empathy-framework-book',
    expiresAt: licenseExpiration,
  });

  console.log('License created:', license.license_key);

  // Create download token
  const downloadToken = generateDownloadToken();
  const downloadExpiration = calculateDownloadExpiration(30); // 30 days

  await createDownloadToken({
    customerId: customer.id,
    purchaseId: purchase.id,
    fileType: 'all',
    token: downloadToken,
    expiresAt: downloadExpiration,
  });

  console.log('Download token created');

  // Send email with license and download links
  if (process.env.RESEND_API_KEY) {
    const result = await sendBookEmail({
      to: customer.email,
      customerName: customer.name ?? session.customer_details?.name ?? undefined,
      licenseKey,
      downloadToken,
      expiresAt: licenseExpiration,
      amountPaid: session.amount_total!,
    });

    if (result.success) {
      console.log('Book email sent:', result.id);
    } else {
      console.error('Failed to send book email:', result.error);
    }
  } else {
    console.log('RESEND_API_KEY not configured - email not sent');
  }
}

// Handle license-only purchase
async function handleLicensePurchase(
  customer: { id: number; email: string; name: string | null },
  purchase: { id: number },
  session: Stripe.Checkout.Session
): Promise<void> {
  // Generate license key
  const licenseKey = generateLicenseKey('EMPATHY');
  const licenseExpiration = calculateLicenseExpiration(1); // 1 year

  // Create license record
  const license = await createLicense({
    customerId: customer.id,
    purchaseId: purchase.id,
    licenseKey,
    product: 'empathy-framework-commercial',
    expiresAt: licenseExpiration,
  });

  console.log('License created:', license.license_key);

  // Send email with license key
  if (process.env.RESEND_API_KEY) {
    const result = await sendLicenseEmail({
      to: customer.email,
      customerName: customer.name ?? session.customer_details?.name ?? undefined,
      licenseKey,
      productName: 'Empathy Framework Commercial License',
      expiresAt: licenseExpiration,
      amountPaid: session.amount_total!,
    });

    if (result.success) {
      console.log('License email sent:', result.id);
    } else {
      console.error('Failed to send license email:', result.error);
    }
  } else {
    console.log('RESEND_API_KEY not configured - email not sent');
  }
}

// Handle contribution (no license, just thank you)
async function handleContribution(
  customer: { id: number; email: string; name: string | null },
  _purchase: { id: number },
  session: Stripe.Checkout.Session
): Promise<void> {
  // Send thank you email
  if (process.env.RESEND_API_KEY) {
    const result = await sendContributionEmail({
      to: customer.email,
      customerName: customer.name ?? session.customer_details?.name ?? undefined,
      amountPaid: session.amount_total!,
    });

    if (result.success) {
      console.log('Contribution email sent:', result.id);
    } else {
      console.error('Failed to send contribution email:', result.error);
    }
  } else {
    console.log('RESEND_API_KEY not configured - email not sent');
  }
}

// Fallback: Send emails without database persistence
async function handleEmailOnlyFulfillment(
  session: Stripe.Checkout.Session,
  productInfo: { type: string; name: string; includesLicense: boolean }
): Promise<void> {
  const email = session.customer_email;
  if (!email) return;

  const customerName = session.customer_details?.name;

  if (productInfo.type === 'book' && productInfo.includesLicense) {
    // Generate temporary license key (not persisted)
    const licenseKey = generateLicenseKey('EMPATHY');
    const downloadToken = generateDownloadToken();
    const expiration = calculateLicenseExpiration(1);

    await sendBookEmail({
      to: email,
      customerName: customerName || undefined,
      licenseKey,
      downloadToken,
      expiresAt: expiration,
      amountPaid: session.amount_total!,
    });

    console.log('Book email sent (no DB persistence)');
  } else if (productInfo.type === 'license') {
    const licenseKey = generateLicenseKey('EMPATHY');
    const expiration = calculateLicenseExpiration(1);

    await sendLicenseEmail({
      to: email,
      customerName: customerName || undefined,
      licenseKey,
      productName: productInfo.name,
      expiresAt: expiration,
      amountPaid: session.amount_total!,
    });

    console.log('License email sent (no DB persistence)');
  } else if (productInfo.type === 'contribution') {
    await sendContributionEmail({
      to: email,
      customerName: customerName || undefined,
      amountPaid: session.amount_total!,
    });

    console.log('Contribution email sent');
  }
}
