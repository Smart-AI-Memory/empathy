// Mailchimp integration for newsletter subscriber management

export interface MailchimpSubscriber {
  email: string;
  firstName?: string;
  lastName?: string;
  tags?: string[];
}

export interface MailchimpResult {
  success: boolean;
  id?: string;
  status?: string;
  error?: string;
  alreadySubscribed?: boolean;
}

export async function subscribeToMailchimp(subscriber: MailchimpSubscriber): Promise<MailchimpResult> {
  const apiKey = process.env.MAILCHIMP_API_KEY;
  const listId = process.env.MAILCHIMP_LIST_ID;
  const serverPrefix = process.env.MAILCHIMP_SERVER_PREFIX; // e.g., 'us1'

  if (!apiKey || !listId || !serverPrefix) {
    console.log('Mailchimp not configured (missing env vars)');
    return { success: false, error: 'Mailchimp not configured' };
  }

  try {
    const response = await fetch(
      `https://${serverPrefix}.api.mailchimp.com/3.0/lists/${listId}/members`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_address: subscriber.email,
          status: 'subscribed',
          merge_fields: {
            FNAME: subscriber.firstName || '',
            LNAME: subscriber.lastName || '',
          },
          tags: subscriber.tags || [],
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      console.log('Successfully subscribed to Mailchimp:', data.id);
      return {
        success: true,
        id: data.id,
        status: data.status,
      };
    } else {
      // Handle already subscribed case
      if (data.title === 'Member Exists') {
        console.log('Subscriber already exists in Mailchimp');
        return {
          success: true,
          alreadySubscribed: true,
          error: 'Already subscribed',
        };
      }

      console.error('Mailchimp error:', data);
      return {
        success: false,
        error: data.detail || data.title || 'Unknown error',
      };
    }
  } catch (error) {
    console.error('Mailchimp subscription error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

export async function getMailchimpSubscriber(email: string): Promise<MailchimpResult> {
  const apiKey = process.env.MAILCHIMP_API_KEY;
  const listId = process.env.MAILCHIMP_LIST_ID;
  const serverPrefix = process.env.MAILCHIMP_SERVER_PREFIX;

  if (!apiKey || !listId || !serverPrefix) {
    return { success: false, error: 'Mailchimp not configured' };
  }

  // Mailchimp uses MD5 hash of lowercase email as subscriber ID
  const crypto = await import('crypto');
  const emailHash = crypto.createHash('md5').update(email.toLowerCase()).digest('hex');

  try {
    const response = await fetch(
      `https://${serverPrefix}.api.mailchimp.com/3.0/lists/${listId}/members/${emailHash}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        id: data.id,
        status: data.status,
      };
    } else {
      return { success: false, error: 'Subscriber not found' };
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

export async function unsubscribeFromMailchimp(email: string): Promise<MailchimpResult> {
  const apiKey = process.env.MAILCHIMP_API_KEY;
  const listId = process.env.MAILCHIMP_LIST_ID;
  const serverPrefix = process.env.MAILCHIMP_SERVER_PREFIX;

  if (!apiKey || !listId || !serverPrefix) {
    return { success: false, error: 'Mailchimp not configured' };
  }

  const crypto = await import('crypto');
  const emailHash = crypto.createHash('md5').update(email.toLowerCase()).digest('hex');

  try {
    const response = await fetch(
      `https://${serverPrefix}.api.mailchimp.com/3.0/lists/${listId}/members/${emailHash}`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: 'unsubscribed',
        }),
      }
    );

    if (response.ok) {
      return { success: true, status: 'unsubscribed' };
    } else {
      const data = await response.json();
      return { success: false, error: data.detail || 'Failed to unsubscribe' };
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}
