import { notFound } from 'next/navigation';
import Link from 'next/link';
import type { Metadata } from 'next';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { getPostBySlug, getAllPosts } from '@/lib/blog';
import { generateMetadata as generateSEOMetadata } from '@/lib/metadata';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface PageProps {
  params: Promise<{
    slug: string;
  }>;
}

export async function generateStaticParams() {
  const posts = getAllPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = getPostBySlug(slug);

  if (!post) {
    return {
      title: 'Post Not Found',
    };
  }

  return generateSEOMetadata({
    title: post.title,
    description: post.excerpt,
    type: 'article',
    url: `https://smartaimemory.com/blog/${post.slug}`,
    image: post.coverImage,
    publishedTime: post.date,
    author: post.author,
  });
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = getPostBySlug(slug);

  if (!post) {
    notFound();
  }

  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        <article className="py-20">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              {/* Header */}
              <header className="mb-12">
                <Link
                  href="/blog"
                  className="text-[var(--primary)] hover:underline mb-6 inline-block"
                >
                  ← Back to Blog
                </Link>

                <h1 className="text-5xl font-bold mb-6">{post.title}</h1>

                <div className="flex flex-wrap items-center gap-4 text-[var(--muted)] mb-6">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-[var(--text-primary)]">
                      {post.author}
                    </span>
                  </div>
                  <span>•</span>
                  <time dateTime={post.date}>
                    {new Date(post.date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </time>
                  <span>•</span>
                  <span>{post.readingTime}</span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-[var(--border)] text-[var(--text-primary)] rounded-full text-sm font-semibold"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </header>

              {/* Cover Image */}
              {post.coverImage && (
                <div className="mb-12">
                  <img
                    src={post.coverImage}
                    alt={post.title}
                    className="w-full rounded-lg"
                  />
                </div>
              )}

              {/* Content */}
              <div className="prose prose-lg max-w-none prose-headings:font-bold prose-a:text-[var(--primary)] prose-a:no-underline hover:prose-a:underline prose-code:bg-[var(--border)] prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-[var(--border)] prose-pre:border prose-pre:border-[var(--border)]">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {post.content}
                </ReactMarkdown>
              </div>

              {/* Footer */}
              <footer className="mt-12 pt-12 border-t border-[var(--border)]">
                <div className="flex justify-between items-center">
                  <Link
                    href="/blog"
                    className="btn btn-outline"
                  >
                    ← Back to Blog
                  </Link>
                  <Link
                    href="/contact"
                    className="btn btn-primary"
                  >
                    Get in Touch
                  </Link>
                </div>
              </footer>
            </div>
          </div>
        </article>
      </main>
      <Footer />
    </>
  );
}
