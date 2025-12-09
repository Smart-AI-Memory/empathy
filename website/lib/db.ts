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

    -- Create indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
    CREATE INDEX IF NOT EXISTS idx_customers_stripe_id ON customers(stripe_customer_id);
    CREATE INDEX IF NOT EXISTS idx_purchases_customer ON purchases(customer_id);
    CREATE INDEX IF NOT EXISTS idx_purchases_session ON purchases(stripe_session_id);
    CREATE INDEX IF NOT EXISTS idx_licenses_customer ON licenses(customer_id);
    CREATE INDEX IF NOT EXISTS idx_licenses_key ON licenses(license_key);
    CREATE INDEX IF NOT EXISTS idx_downloads_token ON downloads(download_token);
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
    // Update with any new info
    const customer = existing.rows[0];
    if (stripeCustomerId && !customer.stripe_customer_id) {
      await query(
        'UPDATE customers SET stripe_customer_id = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2',
        [stripeCustomerId, customer.id]
      );
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
