import sgMail from '@sendgrid/mail';

// Initialize SendGrid with API key from environment variable
if (process.env.SENDGRID_API_KEY) {
  sgMail.setApiKey(process.env.SENDGRID_API_KEY);
}

export interface EmailOptions {
  to: string | string[];
  from?: string;
  subject: string;
  text?: string;
  html?: string;
  replyTo?: string;
}

export async function sendEmail(options: EmailOptions): Promise<boolean> {
  if (!process.env.SENDGRID_API_KEY) {
    console.error('SENDGRID_API_KEY is not set in environment variables');
    return false;
  }

  if (!process.env.SENDGRID_FROM_EMAIL) {
    console.error('SENDGRID_FROM_EMAIL is not set in environment variables');
    return false;
  }

  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const msg: any = {
      to: options.to,
      from: options.from || process.env.SENDGRID_FROM_EMAIL,
      subject: options.subject,
    };

    // Add text and/or html if provided
    if (options.text) {
      msg.text = options.text;
    }
    if (options.html) {
      msg.html = options.html;
    }
    if (options.replyTo) {
      msg.replyTo = options.replyTo;
    }

    // Ensure at least one of text or html is provided
    if (!msg.text && !msg.html) {
      console.error('Either text or html content must be provided');
      return false;
    }

    console.log('Sending email via SendGrid:', {
      to: msg.to,
      from: msg.from,
      subject: msg.subject,
      replyTo: msg.replyTo || 'none',
    });
    await sgMail.send(msg);
    console.log('Email sent successfully via SendGrid to:', msg.to);
    return true;
  } catch (error) {
    console.error('SendGrid error:', error);
    return false;
  }
}

export async function sendContactFormEmail(data: {
  name: string;
  email: string;
  company?: string;
  topic: string;
  message: string;
}): Promise<boolean> {
  const { name, email, company, topic, message } = data;

  const html = `
    <h2>New Contact Form Submission</h2>
    <p><strong>Name:</strong> ${name}</p>
    <p><strong>Email:</strong> ${email}</p>
    <p><strong>Company:</strong> ${company || 'Not provided'}</p>
    <p><strong>Topic:</strong> ${topic}</p>
    <p><strong>Message:</strong></p>
    <p>${message.replace(/\n/g, '<br>')}</p>
    <hr>
    <p><small>Sent from smartaimemory.com contact form</small></p>
  `;

  const text = `
New Contact Form Submission

Name: ${name}
Email: ${email}
Company: ${company || 'Not provided'}
Topic: ${topic}

Message:
${message}

---
Sent from smartaimemory.com contact form
  `;

  return sendEmail({
    to: process.env.CONTACT_EMAIL || 'patrick.roebuck@smartaimemory.com',
    subject: `[Smart AI Memory] Contact: ${topic} - ${name}`,
    text,
    html,
    replyTo: email,
  });
}

export async function sendNewsletterConfirmation(email: string): Promise<boolean> {
  const html = `
    <h2>Welcome to Smart AI Memory Newsletter!</h2>
    <p>Thank you for subscribing to our newsletter.</p>
    <p>You'll receive updates about:</p>
    <ul>
      <li>New Empathy releases and features</li>
      <li>AI development insights and best practices</li>
      <li>Community highlights and use cases</li>
      <li>Exclusive content and early access</li>
    </ul>
    <p>You can unsubscribe at any time by clicking the link at the bottom of our emails.</p>
    <hr>
    <p><small>Smart AI Memory - Building the Future of AI-Human Collaboration</small></p>
  `;

  const text = `
Welcome to Smart AI Memory Newsletter!

Thank you for subscribing to our newsletter.

You'll receive updates about:
- New Empathy releases and features
- AI development insights and best practices
- Community highlights and use cases
- Exclusive content and early access

You can unsubscribe at any time by clicking the link at the bottom of our emails.

---
Smart AI Memory - Building the Future of AI-Human Collaboration
  `;

  return sendEmail({
    to: email,
    subject: 'Welcome to Smart AI Memory Newsletter',
    text,
    html,
  });
}
