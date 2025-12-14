import { Pool, QueryResult, QueryResultRow } from 'pg';

// Lazy initialization to avoid build-time errors
let pool: Pool | null = null;

function getPool(): Pool {
  if (!pool) {
    if (!process.env.DATABASE_URL) {
      throw new Error('DATABASE_URL is not configured');
    }
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
    });
  }
  return pool;
}

export async function query<T extends QueryResultRow = QueryResultRow>(text: string, params?: unknown[]): Promise<QueryResult<T>> {
  const client = await getPool().connect();
  try {
    return await client.query<T>(text, params);
  } finally {
    client.release();
  }
}

// Initialize database schema
export async function initializeDatabase(): Promise<void> {
  const schema = `
    -- Customers table
    CREATE TABLE IF NOT EXISTS customers (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) UNIQUE NOT NULL,
      stripe_customer_id VARCHAR(255) UNIQUE,
      name VARCHAR(255),
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Purchases table
    CREATE TABLE IF NOT EXISTS purchases (
      id SERIAL PRIMARY KEY,
      customer_id INTEGER REFERENCES customers(id),
      stripe_session_id VARCHAR(255) UNIQUE NOT NULL,
      stripe_payment_intent VARCHAR(255),
      product_type VARCHAR(50) NOT NULL, -- 'book', 'license', 'contribution'
      product_name VARCHAR(255),
      amount_cents INTEGER NOT NULL,
      currency VARCHAR(10) DEFAULT 'usd',
      status VARCHAR(50) DEFAULT 'completed',
      metadata JSONB,
      purchased_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Licenses table
    CREATE TABLE IF NOT EXISTS licenses (
      id SERIAL PRIMARY KEY,
      customer_id INTEGER REFERENCES customers(id),
      purchase_id INTEGER REFERENCES purchases(id),
      license_key VARCHAR(255) UNIQUE NOT NULL,
      product VARCHAR(100) NOT NULL, -- 'empathy-framework', 'book-access'
      status VARCHAR(50) DEFAULT 'active', -- 'active', 'expired', 'revoked'
      activated_at TIMESTAMP WITH TIME ZONE,
      expires_at TIMESTAMP WITH TIME ZONE,
      max_activations INTEGER DEFAULT 5,
      current_activations INTEGER DEFAULT 0,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- License activations (track where licenses are used)
    CREATE TABLE IF NOT EXISTS license_activations (
      id SERIAL PRIMARY KEY,
      license_id INTEGER REFERENCES licenses(id),
      machine_id VARCHAR(255),
      hostname VARCHAR(255),
      ip_address VARCHAR(45),
      activated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      is_active BOOLEAN DEFAULT true
    );

    -- Downloads table (track book downloads)
    CREATE TABLE IF NOT EXISTS downloads (
      id SERIAL PRIMARY KEY,
      customer_id INTEGER REFERENCES customers(id),
      purchase_id INTEGER REFERENCES purchases(id),
      file_type VARCHAR(50), -- 'pdf', 'epub', 'mobi'
      download_token VARCHAR(255) UNIQUE,
      download_count INTEGER DEFAULT 0,
      max_downloads INTEGER DEFAULT 10,
      expires_at TIMESTAMP WITH TIME ZONE,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      last_download_at TIMESTAMP WITH TIME ZONE
    );

    -- Newsletter subscribers table
    CREATE TABLE IF NOT EXISTS subscribers (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) UNIQUE NOT NULL,
      source VARCHAR(50) DEFAULT 'website', -- 'website', 'book_purchase', 'contact_form'
      status VARCHAR(50) DEFAULT 'active', -- 'active', 'unsubscribed', 'bounced'
      mailchimp_id VARCHAR(255),
      tags TEXT[], -- Array of tags like 'newsletter', 'book_buyer', etc.
      subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      unsubscribed_at TIMESTAMP WITH TIME ZONE,
      metadata JSONB
    );

    -- Contact form submissions table
    CREATE TABLE IF NOT EXISTS contacts (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      email VARCHAR(255) NOT NULL,
      company VARCHAR(255),
      topic VARCHAR(100) NOT NULL,
      message TEXT NOT NULL,
      status VARCHAR(50) DEFAULT 'new', -- 'new', 'read', 'replied', 'archived'
      submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      replied_at TIMESTAMP WITH TIME ZONE,
      notes TEXT,
      metadata JSONB
    );

    -- Create indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
    CREATE INDEX IF NOT EXISTS idx_customers_stripe_id ON customers(stripe_customer_id);
    CREATE INDEX IF NOT EXISTS idx_purchases_customer ON purchases(customer_id);
    CREATE INDEX IF NOT EXISTS idx_purchases_session ON purchases(stripe_session_id);
    CREATE INDEX IF NOT EXISTS idx_licenses_customer ON licenses(customer_id);
    CREATE INDEX IF NOT EXISTS idx_licenses_key ON licenses(license_key);
    CREATE INDEX IF NOT EXISTS idx_downloads_token ON downloads(download_token);
    CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
    CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);
    CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
    CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
  `;

  await query(schema);
  console.log('Database schema initialized');
}

// Customer operations
export interface Customer {
  id: number;
  email: string;
  stripe_customer_id: string | null;
  name: string | null;
  created_at: Date;
  updated_at: Date;
}

export async function findOrCreateCustomer(
  email: string,
  stripeCustomerId?: string,
  name?: string
): Promise<Customer> {
  // Try to find existing customer
  const existing = await query<Customer>(
    'SELECT * FROM customers WHERE email = $1 OR stripe_customer_id = $2',
    [email, stripeCustomerId]
  );

  if (existing.rows.length > 0) {
    // Update with any new/missing info
    const customer = existing.rows[0];
    const updates: string[] = [];
    const values: unknown[] = [];
    let paramIndex = 1;

    // Update email if it was null (fix for earlier bug)
    if (email && !customer.email) {
      updates.push(`email = $${paramIndex++}`);
      values.push(email);
    }
    // Update stripe_customer_id if missing
    if (stripeCustomerId && !customer.stripe_customer_id) {
      updates.push(`stripe_customer_id = $${paramIndex++}`);
      values.push(stripeCustomerId);
    }
    // Update name if missing
    if (name && !customer.name) {
      updates.push(`name = $${paramIndex++}`);
      values.push(name);
    }

    if (updates.length > 0) {
      updates.push(`updated_at = CURRENT_TIMESTAMP`);
      values.push(customer.id);
      const result = await query<Customer>(
        `UPDATE customers SET ${updates.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
        values
      );
      return result.rows[0];
    }
    return customer;
  }

  // Create new customer
  const result = await query<Customer>(
    'INSERT INTO customers (email, stripe_customer_id, name) VALUES ($1, $2, $3) RETURNING *',
    [email, stripeCustomerId, name]
  );

  return result.rows[0];
}

// Purchase operations
export interface Purchase {
  id: number;
  customer_id: number;
  stripe_session_id: string;
  stripe_payment_intent: string | null;
  product_type: string;
  product_name: string | null;
  amount_cents: number;
  currency: string;
  status: string;
  metadata: Record<string, unknown> | null;
  purchased_at: Date;
}

export async function findPurchaseBySessionId(sessionId: string): Promise<Purchase | null> {
  const result = await query<Purchase>(
    'SELECT * FROM purchases WHERE stripe_session_id = $1',
    [sessionId]
  );
  return result.rows[0] || null;
}

export async function findOrCreatePurchase(data: {
  customerId: number;
  stripeSessionId: string;
  stripePaymentIntent?: string;
  productType: string;
  productName?: string;
  amountCents: number;
  currency?: string;
  metadata?: Record<string, unknown>;
}): Promise<{ purchase: Purchase; created: boolean }> {
  // Check if purchase already exists (idempotency for webhook retries)
  const existing = await findPurchaseBySessionId(data.stripeSessionId);
  if (existing) {
    return { purchase: existing, created: false };
  }

  // Create new purchase
  const result = await query<Purchase>(
    `INSERT INTO purchases
     (customer_id, stripe_session_id, stripe_payment_intent, product_type, product_name, amount_cents, currency, metadata)
     VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
     RETURNING *`,
    [
      data.customerId,
      data.stripeSessionId,
      data.stripePaymentIntent,
      data.productType,
      data.productName,
      data.amountCents,
      data.currency || 'usd',
      data.metadata ? JSON.stringify(data.metadata) : null,
    ]
  );

  return { purchase: result.rows[0], created: true };
}

export async function createPurchase(data: {
  customerId: number;
  stripeSessionId: string;
  stripePaymentIntent?: string;
  productType: string;
  productName?: string;
  amountCents: number;
  currency?: string;
  metadata?: Record<string, unknown>;
}): Promise<Purchase> {
  const result = await query<Purchase>(
    `INSERT INTO purchases
     (customer_id, stripe_session_id, stripe_payment_intent, product_type, product_name, amount_cents, currency, metadata)
     VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
     RETURNING *`,
    [
      data.customerId,
      data.stripeSessionId,
      data.stripePaymentIntent,
      data.productType,
      data.productName,
      data.amountCents,
      data.currency || 'usd',
      data.metadata ? JSON.stringify(data.metadata) : null,
    ]
  );

  return result.rows[0];
}

// License operations
export interface License {
  id: number;
  customer_id: number;
  purchase_id: number;
  license_key: string;
  product: string;
  status: string;
  activated_at: Date | null;
  expires_at: Date | null;
  max_activations: number;
  current_activations: number;
  created_at: Date;
}

export async function createLicense(data: {
  customerId: number;
  purchaseId: number;
  licenseKey: string;
  product: string;
  expiresAt?: Date;
}): Promise<License> {
  const result = await query<License>(
    `INSERT INTO licenses
     (customer_id, purchase_id, license_key, product, expires_at)
     VALUES ($1, $2, $3, $4, $5)
     RETURNING *`,
    [data.customerId, data.purchaseId, data.licenseKey, data.product, data.expiresAt]
  );

  return result.rows[0];
}

export async function findLicenseByKey(licenseKey: string): Promise<License | null> {
  const result = await query<License>(
    'SELECT * FROM licenses WHERE license_key = $1',
    [licenseKey]
  );
  return result.rows[0] || null;
}

export async function findLicenseByPurchaseId(purchaseId: number): Promise<License | null> {
  const result = await query<License>(
    'SELECT * FROM licenses WHERE purchase_id = $1',
    [purchaseId]
  );
  return result.rows[0] || null;
}

export async function getCustomerLicenses(customerId: number): Promise<License[]> {
  const result = await query<License>(
    'SELECT * FROM licenses WHERE customer_id = $1 ORDER BY created_at DESC',
    [customerId]
  );
  return result.rows;
}

// Download operations
export interface Download {
  id: number;
  customer_id: number;
  purchase_id: number;
  file_type: string;
  download_token: string;
  download_count: number;
  max_downloads: number;
  expires_at: Date | null;
  created_at: Date;
  last_download_at: Date | null;
}

export async function createDownloadToken(data: {
  customerId: number;
  purchaseId: number;
  fileType: string;
  token: string;
  expiresAt?: Date;
}): Promise<Download> {
  const result = await query<Download>(
    `INSERT INTO downloads
     (customer_id, purchase_id, file_type, download_token, expires_at)
     VALUES ($1, $2, $3, $4, $5)
     RETURNING *`,
    [data.customerId, data.purchaseId, data.fileType, data.token, data.expiresAt]
  );

  return result.rows[0];
}

export async function validateAndIncrementDownload(token: string): Promise<Download | null> {
  const result = await query<Download>(
    `UPDATE downloads
     SET download_count = download_count + 1, last_download_at = CURRENT_TIMESTAMP
     WHERE download_token = $1
       AND download_count < max_downloads
       AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
     RETURNING *`,
    [token]
  );
  return result.rows[0] || null;
}

// Subscriber operations
export interface Subscriber {
  id: number;
  email: string;
  source: string;
  status: string;
  mailchimp_id: string | null;
  tags: string[] | null;
  subscribed_at: Date;
  unsubscribed_at: Date | null;
  metadata: Record<string, unknown> | null;
}

export async function createSubscriber(data: {
  email: string;
  source?: string;
  tags?: string[];
  mailchimpId?: string;
  metadata?: Record<string, unknown>;
}): Promise<{ subscriber: Subscriber; created: boolean }> {
  // Check if already exists
  const existing = await query<Subscriber>(
    'SELECT * FROM subscribers WHERE email = $1',
    [data.email.toLowerCase()]
  );

  if (existing.rows.length > 0) {
    // Update if resubscribing
    const subscriber = existing.rows[0];
    if (subscriber.status === 'unsubscribed') {
      const result = await query<Subscriber>(
        `UPDATE subscribers
         SET status = 'active', unsubscribed_at = NULL, subscribed_at = CURRENT_TIMESTAMP
         WHERE id = $1
         RETURNING *`,
        [subscriber.id]
      );
      return { subscriber: result.rows[0], created: false };
    }
    return { subscriber, created: false };
  }

  // Create new subscriber
  const result = await query<Subscriber>(
    `INSERT INTO subscribers (email, source, tags, mailchimp_id, metadata)
     VALUES ($1, $2, $3, $4, $5)
     RETURNING *`,
    [
      data.email.toLowerCase(),
      data.source || 'website',
      data.tags || ['newsletter'],
      data.mailchimpId,
      data.metadata ? JSON.stringify(data.metadata) : null,
    ]
  );

  return { subscriber: result.rows[0], created: true };
}

export async function updateSubscriberMailchimpId(email: string, mailchimpId: string): Promise<void> {
  await query(
    'UPDATE subscribers SET mailchimp_id = $1 WHERE email = $2',
    [mailchimpId, email.toLowerCase()]
  );
}

export async function unsubscribe(email: string): Promise<boolean> {
  const result = await query(
    `UPDATE subscribers
     SET status = 'unsubscribed', unsubscribed_at = CURRENT_TIMESTAMP
     WHERE email = $1 AND status = 'active'`,
    [email.toLowerCase()]
  );
  return (result.rowCount ?? 0) > 0;
}

export async function getAllSubscribers(status?: string): Promise<Subscriber[]> {
  const whereClause = status ? 'WHERE status = $1' : '';
  const params = status ? [status] : [];
  const result = await query<Subscriber>(
    `SELECT * FROM subscribers ${whereClause} ORDER BY subscribed_at DESC`,
    params
  );
  return result.rows;
}

// Contact operations
export interface Contact {
  id: number;
  name: string;
  email: string;
  company: string | null;
  topic: string;
  message: string;
  status: string;
  submitted_at: Date;
  replied_at: Date | null;
  notes: string | null;
  metadata: Record<string, unknown> | null;
}

export async function createContact(data: {
  name: string;
  email: string;
  company?: string;
  topic: string;
  message: string;
  metadata?: Record<string, unknown>;
}): Promise<Contact> {
  const result = await query<Contact>(
    `INSERT INTO contacts (name, email, company, topic, message, metadata)
     VALUES ($1, $2, $3, $4, $5, $6)
     RETURNING *`,
    [
      data.name,
      data.email.toLowerCase(),
      data.company,
      data.topic,
      data.message,
      data.metadata ? JSON.stringify(data.metadata) : null,
    ]
  );

  return result.rows[0];
}

export async function getAllContacts(status?: string): Promise<Contact[]> {
  const whereClause = status ? 'WHERE status = $1' : '';
  const params = status ? [status] : [];
  const result = await query<Contact>(
    `SELECT * FROM contacts ${whereClause} ORDER BY submitted_at DESC`,
    params
  );
  return result.rows;
}

export async function updateContactStatus(id: number, status: string, notes?: string): Promise<Contact | null> {
  const result = await query<Contact>(
    `UPDATE contacts
     SET status = $1, notes = COALESCE($2, notes), replied_at = CASE WHEN $1 = 'replied' THEN CURRENT_TIMESTAMP ELSE replied_at END
     WHERE id = $3
     RETURNING *`,
    [status, notes, id]
  );
  return result.rows[0] || null;
}
