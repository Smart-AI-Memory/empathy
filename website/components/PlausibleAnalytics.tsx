'use client';

import Script from 'next/script';

export default function PlausibleAnalytics() {
  return (
    <>
      <Script
        async
        src="https://plausible.io/js/pa-5FMhEzOX6RnEF6ncz16Tr.js"
        strategy="afterInteractive"
      />
      <Script
        id="plausible-init"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
            plausible.init()
          `,
        }}
      />
    </>
  );
}

// Declare plausible on the window object
declare global {
  interface Window {
    plausible?: (eventName: string, options?: { props?: Record<string, string | number> }) => void;
  }
}

// Custom event tracking helper
export function trackEvent(eventName: string, props?: Record<string, string | number>) {
  if (typeof window !== 'undefined' && window.plausible) {
    window.plausible(eventName, { props });
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
