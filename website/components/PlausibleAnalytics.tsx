'use client';

import Script from 'next/script';

interface PlausibleAnalyticsProps {
  domain?: string;
  apiHost?: string;
}

export default function PlausibleAnalytics({
  domain = process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN,
  apiHost = process.env.NEXT_PUBLIC_PLAUSIBLE_API_HOST || 'https://plausible.io',
}: PlausibleAnalyticsProps) {
  if (!domain) {
    console.warn('Plausible Analytics: NEXT_PUBLIC_PLAUSIBLE_DOMAIN is not set');
    return null;
  }

  return (
    <Script
      defer
      data-domain={domain}
      data-api={`${apiHost}/api/event`}
      src={`${apiHost}/js/script.js`}
      strategy="afterInteractive"
    />
  );
}

// Custom event tracking helper
export function trackEvent(eventName: string, props?: Record<string, string | number>) {
  if (typeof window !== 'undefined' && (window as any).plausible) {
    (window as any).plausible(eventName, { props });
  }
}

// Common event tracking functions
export const analytics = {
  trackDownload: (fileName: string) => {
    trackEvent('Download', { file: fileName });
  },

  trackSignup: (type: 'newsletter' | 'waitlist') => {
    trackEvent('Signup', { type });
  },

  trackContact: (topic: string) => {
    trackEvent('Contact', { topic });
  },

  trackOutboundLink: (url: string) => {
    trackEvent('Outbound Link', { url });
  },

  trackCTA: (name: string, location: string) => {
    trackEvent('CTA Click', { name, location });
  },
};
