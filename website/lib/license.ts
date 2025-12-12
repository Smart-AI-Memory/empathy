import crypto from 'crypto';

// License key format: EMPATHY-XXXX-XXXX-XXXX-XXXX
// Where X is alphanumeric (excluding confusing chars like 0/O, 1/I/l)
const CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';

function generateSegment(length: number): string {
  let segment = '';
  const randomBytes = crypto.randomBytes(length);
  for (let i = 0; i < length; i++) {
    segment += CHARS[randomBytes[i] % CHARS.length];
  }
  return segment;
}

export function generateLicenseKey(prefix: string = 'EMPATHY'): string {
  const segments = [
    prefix,
    generateSegment(4),
    generateSegment(4),
    generateSegment(4),
    generateSegment(4),
  ];
  return segments.join('-');
}

export function generateDownloadToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

// Calculate expiration date (1 year from now for licenses)
export function calculateLicenseExpiration(yearsFromNow: number = 1): Date {
  const expiration = new Date();
  expiration.setFullYear(expiration.getFullYear() + yearsFromNow);
  return expiration;
}

// Calculate download token expiration (30 days for book downloads)
export function calculateDownloadExpiration(daysFromNow: number = 30): Date {
  const expiration = new Date();
  expiration.setDate(expiration.getDate() + daysFromNow);
  return expiration;
}

// Determine product type from Stripe price ID
export function getProductTypeFromPriceId(priceId: string): {
  type: 'book' | 'license' | 'contribution';
  name: string;
  includesLicense: boolean;
} {
  // Book price ID
  if (priceId === 'price_1Sbf3xAbABKRT84gGn7yaivw' || priceId.includes('BOOK')) {
    return {
      type: 'book',
      name: 'The Empathy Book + License',
      includesLicense: true, // Book includes 1-year license
    };
  }

  // License price ID
  if (priceId === 'price_1SbfCjAbABKRT84gSh7BoLAl' || priceId.includes('LICENSE')) {
    return {
      type: 'license',
      name: 'Empathy Commercial License',
      includesLicense: true,
    };
  }

  // Contribution (default)
  return {
    type: 'contribution',
    name: 'Contribution',
    includesLicense: false,
  };
}

// Validate license key format
export function isValidLicenseKeyFormat(key: string): boolean {
  const pattern = /^[A-Z]+-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/;
  return pattern.test(key);
}
