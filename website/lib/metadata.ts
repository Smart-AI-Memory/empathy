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
  description: 'Production-ready framework for building Level 4 Anticipatory AI systems. Empathy Framework enables AI to predict problems before they happen.',
  url: 'https://smartaimemory.com',
  image: '/og-image.png',
  twitterHandle: '@smartaimemory',
  keywords: [
    'AI Framework',
    'Anticipatory Intelligence',
    'AI-Human Collaboration',
    'Level 4 AI',
    'Empathy Framework',
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

interface ProductData {
  name?: string;
  description?: string;
  url?: string;
  price?: string;
  rating?: string;
  ratingCount?: string;
}

interface ArticleData {
  title?: string;
  description?: string;
  image?: string;
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
}

interface FAQData {
  questions?: Array<{ question: string; answer: string }>;
}

type StructuredData = ProductData | ArticleData | FAQData | undefined;

export function generateStructuredData(type: 'organization' | 'product' | 'article' | 'faq', data?: StructuredData) {
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
        ],
        contactPoint: {
          '@type': 'ContactPoint',
          email: 'patrick.roebuck@pm.me',
          contactType: 'Customer Service',
        },
      };

    case 'product': {
      const productData = data as ProductData | undefined;
      return {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: productData?.name || 'Empathy',
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Cross-platform',
        description: productData?.description || 'A 5-level maturity model for AI-human collaboration',
        url: productData?.url || `${defaultMetadata.url}/framework`,
        author: {
          '@type': 'Organization',
          name: 'Deep Study AI, LLC',
        },
        offers: {
          '@type': 'Offer',
          price: productData?.price || '0',
          priceCurrency: 'USD',
          availability: 'https://schema.org/InStock',
        },
        aggregateRating: {
          '@type': 'AggregateRating',
          ratingValue: productData?.rating || '5',
          ratingCount: productData?.ratingCount || '1',
        },
      };
    }

    case 'article': {
      const articleData = data as ArticleData | undefined;
      return {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: articleData?.title,
        description: articleData?.description,
        image: articleData?.image || defaultMetadata.image,
        author: {
          '@type': 'Organization',
          name: articleData?.author || 'Deep Study AI, LLC',
        },
        publisher: {
          '@type': 'Organization',
          name: 'Deep Study AI, LLC',
          logo: {
            '@type': 'ImageObject',
            url: `${defaultMetadata.url}/logo.png`,
          },
        },
        datePublished: articleData?.publishedTime,
        dateModified: articleData?.modifiedTime || articleData?.publishedTime,
      };
    }

    case 'faq': {
      const faqData = data as FAQData | undefined;
      return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: (faqData?.questions || []).map((q) => ({
          '@type': 'Question',
          name: q.question,
          acceptedAnswer: {
            '@type': 'Answer',
            text: q.answer,
          },
        })),
      };
    }

    default:
      return null;
  }
}
