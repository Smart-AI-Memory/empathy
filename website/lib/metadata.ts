import type { Metadata } from 'next';

export interface SEOConfig {
  title?: string;
  description?: string;
  keywords?: string[];
  image?: string;
  url?: string;
  type?: 'website' | 'article';
  publishedTime?: string;
  modifiedTime?: string;
  author?: string;
  section?: string;
}

const defaultMetadata = {
  siteName: 'Smart AI Memory',
  title: 'Smart AI Memory - Building the Future of AI-Human Collaboration',
  description: 'Production-ready frameworks for building Level 4 Anticipatory AI systems. Empathy, MemDocs, and tools that enable AI to predict problems before they happen.',
  url: 'https://smartaimemory.com',
  image: '/og-image.png',
  twitterHandle: '@smartaimemory',
  keywords: [
    'AI Framework',
    'Anticipatory Intelligence',
    'AI-Human Collaboration',
    'Level 4 AI',
    'Empathy',
    'MemDocs',
    'Claude Code',
    'AI Development',
    'Machine Learning',
    'Predictive AI',
    'AI Wizards',
    'Software Development AI',
    'Healthcare AI',
    'Production AI',
  ],
};

export function generateMetadata(config?: SEOConfig): Metadata {
  const title = config?.title
    ? `${config.title} | ${defaultMetadata.siteName}`
    : defaultMetadata.title;

  const description = config?.description || defaultMetadata.description;
  const image = config?.image || defaultMetadata.image;
  const url = config?.url || defaultMetadata.url;
  const keywords = config?.keywords || defaultMetadata.keywords;

  return {
    metadataBase: new URL(defaultMetadata.url),
    title,
    description,
    keywords,
    authors: [
      { name: 'Deep Study AI, LLC' },
      ...(config?.author ? [{ name: config.author }] : []),
    ],
    creator: 'Deep Study AI, LLC',
    publisher: 'Deep Study AI, LLC',
    formatDetection: {
      email: false,
      address: false,
      telephone: false,
    },
    openGraph: {
      type: config?.type || 'website',
      locale: 'en_US',
      url,
      title,
      description,
      siteName: defaultMetadata.siteName,
      images: [
        {
          url: image,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
      ...(config?.publishedTime && { publishedTime: config.publishedTime }),
      ...(config?.modifiedTime && { modifiedTime: config.modifiedTime }),
      ...(config?.author && { authors: [config.author] }),
      ...(config?.section && { section: config.section }),
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [image],
      creator: defaultMetadata.twitterHandle,
      site: defaultMetadata.twitterHandle,
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
    alternates: {
      canonical: url,
    },
    icons: {
      icon: '/favicon.ico',
      apple: '/apple-touch-icon.png',
    },
    manifest: '/site.webmanifest',
    verification: {
      // Add when available
      // google: 'google-verification-code',
      // yandex: 'yandex-verification-code',
      // bing: 'bing-verification-code',
    },
  };
}

export function generateStructuredData(type: 'organization' | 'product' | 'article' | 'faq', data?: any) {
  switch (type) {
    case 'organization':
      return {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        name: 'Deep Study AI, LLC',
        alternateName: 'Smart AI Memory',
        url: defaultMetadata.url,
        logo: `${defaultMetadata.url}/logo.png`,
        description: defaultMetadata.description,
        sameAs: [
          'https://github.com/Smart-AI-Memory',
          'https://github.com/Smart-AI-Memory/empathy',
          'https://github.com/Smart-AI-Memory/MemDocs',
        ],
        contactPoint: {
          '@type': 'ContactPoint',
          email: 'patrick.roebuck@pm.me',
          contactType: 'Customer Service',
        },
      };

    case 'product':
      return {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: data?.name || 'Empathy',
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Cross-platform',
        description: data?.description || 'A 5-level maturity model for AI-human collaboration',
        url: data?.url || `${defaultMetadata.url}/framework`,
        author: {
          '@type': 'Organization',
          name: 'Deep Study AI, LLC',
        },
        offers: {
          '@type': 'Offer',
          price: data?.price || '0',
          priceCurrency: 'USD',
          availability: 'https://schema.org/InStock',
        },
        aggregateRating: {
          '@type': 'AggregateRating',
          ratingValue: data?.rating || '5',
          ratingCount: data?.ratingCount || '1',
        },
      };

    case 'article':
      return {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: data?.title,
        description: data?.description,
        image: data?.image || defaultMetadata.image,
        author: {
          '@type': 'Organization',
          name: data?.author || 'Deep Study AI, LLC',
        },
        publisher: {
          '@type': 'Organization',
          name: 'Deep Study AI, LLC',
          logo: {
            '@type': 'ImageObject',
            url: `${defaultMetadata.url}/logo.png`,
          },
        },
        datePublished: data?.publishedTime,
        dateModified: data?.modifiedTime || data?.publishedTime,
      };

    case 'faq':
      return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: (data?.questions || []).map((q: { question: string; answer: string }) => ({
          '@type': 'Question',
          name: q.question,
          acceptedAnswer: {
            '@type': 'Answer',
            text: q.answer,
          },
        })),
      };

    default:
      return null;
  }
}
