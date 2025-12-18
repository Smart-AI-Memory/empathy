import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

// Vercel webhook event types
interface VercelWebhookPayload {
  id: string;
  type: string;
  createdAt: number;
  payload: {
    deployment?: {
      id: string;
      name: string;
      url: string;
      meta?: Record<string, string>;
    };
    project?: {
      id: string;
      name: string;
    };
    team?: {
      id: string;
      name: string;
    };
    user?: {
      id: string;
      email: string;
    };
    target?: string;
    alias?: string[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
  };
}

export const runtime = 'nodejs';

function verifySignature(body: string, signature: string | null, secret: string): boolean {
  if (!signature) return false;

  const expectedSignature = crypto
    .createHmac('sha1', secret)
    .update(body)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

export async function POST(req: NextRequest) {
  const body = await req.text();
  const signature = req.headers.get('x-vercel-signature');

  const secret = process.env.VERCEL_WEBHOOK_SECRET;

  if (!secret) {
    console.error('VERCEL_WEBHOOK_SECRET not configured');
    return NextResponse.json(
      { error: 'Webhook secret not configured' },
      { status: 500 }
    );
  }

  // Verify the webhook signature
  if (!verifySignature(body, signature, secret)) {
    console.error('Invalid Vercel webhook signature');
    return NextResponse.json(
      { error: 'Invalid signature' },
      { status: 401 }
    );
  }

  let event: VercelWebhookPayload;

  try {
    event = JSON.parse(body);
  } catch {
    console.error('Failed to parse webhook body');
    return NextResponse.json(
      { error: 'Invalid JSON' },
      { status: 400 }
    );
  }

  console.log('Vercel webhook received:', {
    id: event.id,
    type: event.type,
    createdAt: new Date(event.createdAt).toISOString(),
  });

  try {
    switch (event.type) {
      case 'deployment.created': {
        console.log('Deployment created:', {
          id: event.payload.deployment?.id,
          name: event.payload.deployment?.name,
          url: event.payload.deployment?.url,
        });
        break;
      }

      case 'deployment.ready': {
        console.log('Deployment ready:', {
          id: event.payload.deployment?.id,
          url: event.payload.deployment?.url,
          aliases: event.payload.alias,
        });
        // Could trigger post-deployment tasks here
        // e.g., warm up caches, run smoke tests, notify team
        break;
      }

      case 'deployment.succeeded': {
        console.log('Deployment succeeded:', {
          id: event.payload.deployment?.id,
          url: event.payload.deployment?.url,
        });
        break;
      }

      case 'deployment.error': {
        console.error('Deployment failed:', {
          id: event.payload.deployment?.id,
          name: event.payload.deployment?.name,
        });
        // Could send alert to Slack/Discord/email here
        break;
      }

      case 'deployment.canceled': {
        console.log('Deployment canceled:', {
          id: event.payload.deployment?.id,
        });
        break;
      }

      case 'project.created': {
        console.log('Project created:', {
          id: event.payload.project?.id,
          name: event.payload.project?.name,
        });
        break;
      }

      case 'project.removed': {
        console.log('Project removed:', {
          id: event.payload.project?.id,
          name: event.payload.project?.name,
        });
        break;
      }

      default:
        console.log(`Unhandled Vercel webhook event: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Error processing Vercel webhook:', error);
    return NextResponse.json(
      { error: 'Webhook handler failed' },
      { status: 500 }
    );
  }
}

// Optionally handle GET for webhook verification (some services require this)
export async function GET() {
  return NextResponse.json({ status: 'Vercel webhook endpoint active' });
}
