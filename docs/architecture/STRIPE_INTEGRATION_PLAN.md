# Stripe Integration Plan for Empathy Framework

**Prepared:** December 7, 2025
**Status:** Ready for implementation
**Estimated Time:** 2-4 hours for basic setup, 1-2 days for full integration

---

## Executive Summary

This plan covers setting up Stripe for three revenue streams:
1. **Book Sales** - $49 pre-order (one-time payment)
2. **Commercial License** - $99/developer/year (subscription)
3. **Contributions/Donations** - Variable amounts (one-time or recurring)

---

## Part 1: Stripe Dashboard Setup

### Step 1: Account Configuration

1. **Login to Stripe Dashboard**: https://dashboard.stripe.com
2. **Complete Business Profile** (Settings → Business settings):
   - Business name: Smart AI Memory, LLC
   - Business type: Software/SaaS
   - Support email: admin@smartaimemory.com
   - Website: https://smartaimemory.com

3. **Verify Bank Account** (if not already done):
   - Settings → Payouts → Add bank account

### Step 2: Create Products & Prices

**In Dashboard: Products → Create product**

#### Product 1: The Empathy Framework Book
```
Name: The Empathy Framework Book
Description: Complete guide to building Level 4 Anticipatory AI systems. Includes digital book (PDF, ePub, Mobi), first-year developer license ($49.99 value), and permanent access to all editions.

Price: $49.00 USD (one-time)
Tax behavior: Inclusive or Exclusive (configure based on your preference)
```

#### Product 2: Commercial Developer License
```
Name: Empathy Framework Commercial License
Description: Annual developer license for organizations with 6+ employees. Covers all environments (workstation, staging, production, CI/CD).

Price: $99.00 USD/year (recurring)
Billing period: Yearly
Tax behavior: Exclusive (tax added at checkout)
```

#### Product 3: Contribution/Sponsorship
```
Name: Support Empathy Development
Description: Support ongoing development of the Empathy Framework.

Prices (create multiple):
- $5/month (Coffee Supporter)
- $25/month (Star Supporter)
- $100/month (Rocket Supporter)
- $500/month (Diamond Supporter)
- Custom amount (one-time)
```

### Step 3: Configure Customer Portal

**Settings → Billing → Customer Portal**

Enable:
- [x] View invoices
- [x] Update payment method
- [x] Cancel subscription (with cancellation reasons)
- [x] View billing history

Branding:
- Logo: Upload Empathy Framework logo
- Accent color: Match your brand (#6366f1 or similar)
- Return URL: https://smartaimemory.com/account

---

## Part 2: Implementation Options

### Option A: Payment Links (Fastest - No Code)

**Best for:** Getting started TODAY

Payment Links are pre-built checkout URLs you can share anywhere. No code required.

**Setup:**
1. Go to: Products → [Select Product] → Create payment link
2. Configure options (quantity, promotion codes, etc.)
3. Copy the link
4. Add to your website buttons

**Pros:**
- Live in 5 minutes
- No code changes needed
- Stripe-hosted (secure, PCI compliant)
- Links never expire

**Cons:**
- Less customization
- Can't pass dynamic data (customer info, metadata)
- Limited to products created in Dashboard

### Option B: Checkout Sessions (Recommended for Production)

**Best for:** Full control and professional experience

**Pros:**
- Dynamic pricing and products
- Pass customer metadata
- Better analytics
- Can pre-fill customer email
- Custom success/cancel pages

**Cons:**
- Requires code changes
- Need webhook handling for fulfillment

---

## Part 3: Next.js Integration (Option B)

### Environment Variables

Add to `.env.local` (and Railway/production):

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_...  # From Dashboard → Developers → API keys
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...  # From Webhooks setup

# Product Price IDs (from Dashboard)
STRIPE_PRICE_BOOK=price_...
STRIPE_PRICE_LICENSE_YEARLY=price_...
STRIPE_PRICE_CONTRIB_5=price_...
STRIPE_PRICE_CONTRIB_25=price_...
STRIPE_PRICE_CONTRIB_100=price_...
STRIPE_PRICE_CONTRIB_500=price_...
```

### API Routes to Create

#### 1. `/app/api/stripe/checkout/route.ts`
```typescript
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-12-18.acacia',
});

export async function POST(req: NextRequest) {
  const { priceId, mode, customerEmail } = await req.json();

  try {
    const session = await stripe.checkout.sessions.create({
      mode: mode || 'payment', // 'payment' or 'subscription'
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/pricing`,
      customer_email: customerEmail,
      allow_promotion_codes: true,
      billing_address_collection: 'required',
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Stripe checkout error:', error);
    return NextResponse.json({ error: 'Checkout failed' }, { status: 500 });
  }
}
```

#### 2. `/app/api/stripe/webhook/route.ts`
```typescript
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: NextRequest) {
  const body = await req.text();
  const sig = req.headers.get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object as Stripe.Checkout.Session;
      // Handle successful payment
      // - Send confirmation email
      // - Generate license key
      // - Add to customer database
      console.log('Payment successful:', session.id);
      break;

    case 'customer.subscription.created':
    case 'customer.subscription.updated':
      // Handle subscription changes
      break;

    case 'customer.subscription.deleted':
      // Handle cancellation
      break;
  }

  return NextResponse.json({ received: true });
}
```

#### 3. `/app/api/stripe/portal/route.ts`
```typescript
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: NextRequest) {
  const { customerId } = await req.json();

  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_SITE_URL}/account`,
  });

  return NextResponse.json({ url: session.url });
}
```

### Pages to Create/Update

#### 1. Update `/app/book/page.tsx`
Replace the disabled button with a working checkout button.

#### 2. Update `/app/pricing/page.tsx`
Replace "Contact Sales" links with checkout buttons for Commercial tier.

#### 3. Create `/app/success/page.tsx`
Thank you page after successful payment.

#### 4. Create `/app/account/page.tsx`
Customer dashboard with subscription management.

#### 5. Create `/app/contribute/page.tsx`
Donation/contribution page with tier selection.

---

## Part 4: Webhook Setup

### In Stripe Dashboard

1. Go to: **Developers → Webhooks → Add endpoint**
2. Endpoint URL: `https://smartaimemory.com/api/stripe/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`

4. Copy the signing secret → Add to `STRIPE_WEBHOOK_SECRET`

### Local Testing

Use Stripe CLI for local webhook testing:
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

---

## Part 5: Recommended Implementation Order

### Day 1 Morning (Quick Wins)

1. **[15 min]** Create products in Stripe Dashboard
2. **[10 min]** Create Payment Links for each product
3. **[15 min]** Update book page with Payment Link
4. **[15 min]** Update pricing page with Payment Link for Commercial
5. **[5 min]** Test purchases in test mode

**Result:** Working checkout by lunch, no code changes!

### Day 1 Afternoon (Full Integration)

6. **[30 min]** Add environment variables
7. **[45 min]** Create checkout API route
8. **[30 min]** Create webhook API route
9. **[30 min]** Create success page
10. **[30 min]** Update buttons to use API

### Day 2 (Polish & Launch)

11. **[1 hr]** Create contribution/donate page
12. **[30 min]** Configure Customer Portal
13. **[30 min]** Create account page with portal link
14. **[30 min]** Test end-to-end in test mode
15. **[15 min]** Switch to live mode
16. **[15 min]** Deploy to production

---

## Part 6: Testing Checklist

### Test Mode (Use test API keys)

- [ ] Book purchase completes successfully
- [ ] License subscription creates and bills
- [ ] Contribution payments work (all tiers)
- [ ] Webhooks fire correctly
- [ ] Success page shows order details
- [ ] Customer Portal accessible
- [ ] Cancellation works
- [ ] Payment method update works

### Test Card Numbers
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0025 0000 3155
```

---

## Part 7: Security Considerations

1. **Never expose secret key** - Only use `STRIPE_SECRET_KEY` server-side
2. **Verify webhook signatures** - Always validate with `constructEvent()`
3. **Don't trust client prices** - Always use server-side price IDs
4. **Use HTTPS** - Already handled by Railway/Vercel
5. **Rate limit API routes** - Consider adding rate limiting

---

## Part 8: Post-Launch Tasks

- [ ] Set up Stripe Tax for automatic tax collection
- [ ] Configure Stripe Radar for fraud protection
- [ ] Set up email notifications (or integrate with SendGrid)
- [ ] Create coupon codes for promotions
- [ ] Set up revenue reporting/analytics
- [ ] Consider Stripe Connect if adding marketplace features

---

## Quick Reference Links

- [Stripe Dashboard](https://dashboard.stripe.com)
- [Stripe API Docs](https://docs.stripe.com/api)
- [Payment Links](https://docs.stripe.com/payment-links)
- [Checkout Sessions](https://docs.stripe.com/payments/checkout)
- [Customer Portal](https://docs.stripe.com/customer-management)
- [Webhooks](https://docs.stripe.com/webhooks)
- [Test Cards](https://docs.stripe.com/testing)

---

## Questions to Discuss Tomorrow

1. **Payment Links vs Full Integration?** - Start with Payment Links for speed, or go straight to full integration?

2. **License Delivery** - How do you want to deliver license keys?
   - Email with unique key?
   - Customer portal download?
   - GitHub access grant?

3. **Tax Collection** - Enable Stripe Tax for automatic calculation?

4. **Promotion Codes** - Want to create launch discount codes?

5. **Book Pre-order** - Keep as pre-order, or enable immediate purchase?

---

**Ready to implement when you are! See you after 7 AM.**
# Stripe Integration - Sun Dec  7 10:11:08 EST 2025
