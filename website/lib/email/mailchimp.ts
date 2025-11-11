// Alternative: Mailchimp integration
// Uncomment and configure if you prefer Mailchimp

export interface MailchimpSubscriber {
  email: string;
  firstName?: string;
  lastName?: string;
  tags?: string[];
}

export async function subscribeToMailchimp(subscriber: MailchimpSubscriber): Promise<boolean> {
  const apiKey = process.env.MAILCHIMP_API_KEY;
  const listId = process.env.MAILCHIMP_LIST_ID;
  const serverPrefix = process.env.MAILCHIMP_SERVER_PREFIX; // e.g., 'us1'

  if (!apiKey || !listId || !serverPrefix) {
    console.error('Mailchimp environment variables are not set');
    return false;
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

    if (response.ok) {
      console.log('Successfully subscribed to Mailchimp');
      return true;
    } else {
      const error = await response.json();
      console.error('Mailchimp error:', error);
      return false;
    }
  } catch (error) {
    console.error('Mailchimp subscription error:', error);
    return false;
  }
}
