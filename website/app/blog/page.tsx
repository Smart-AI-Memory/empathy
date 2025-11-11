import type { Metadata } from 'next';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { generateMetadata } from '@/lib/metadata';
import { getAllPosts } from '@/lib/blog';

export const metadata: Metadata = generateMetadata({
  title: 'Blog',
  description: 'Insights on AI development, anticipatory intelligence, and the future of AI-human collaboration.',
  url: 'https://smartaimemory.com/blog',
});

export default function BlogPage() {
  const posts = getAllPosts();

  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-5xl font-bold mb-6">
                Blog
              </h1>
              <p className="text-2xl mb-8 opacity-90">
                Insights on AI development, anticipatory intelligence, and building the future
              </p>
            </div>
          </div>
        </section>

        {/* Blog Posts */}
        <section className="py-20">
          <div className="container">
            {posts.length === 0 ? (
              <div className="max-w-3xl mx-auto text-center">
                <div className="text-6xl mb-6">📝</div>
                <h2 className="text-3xl font-bold mb-4">
                  Coming Soon
                </h2>
                <p className="text-xl text-[var(--text-secondary)] mb-8">
                  We're working on exciting content about AI development, anticipatory intelligence,
                  and real-world case studies. Check back soon!
                </p>
                <Link href="/#newsletter" className="btn btn-primary">
                  Subscribe for Updates
                </Link>
              </div>
            ) : (
              <div className="max-w-5xl mx-auto grid gap-8">
                {posts.map((post) => (
                  <article
                    key={post.slug}
                    className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-8 hover:border-[var(--primary)] transition-all"
                  >
                    <div className="flex flex-col md:flex-row gap-6">
                      {post.coverImage && (
                        <div className="md:w-1/3">
                          <img
                            src={post.coverImage}
                            alt={post.title}
                            className="w-full h-48 object-cover rounded-lg"
                          />
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3 text-sm text-[var(--muted)]">
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

                        <Link href={`/blog/${post.slug}`}>
                          <h2 className="text-3xl font-bold mb-3 hover:text-[var(--primary)] transition-colors">
                            {post.title}
                          </h2>
                        </Link>

                        <p className="text-[var(--text-secondary)] mb-4">
                          {post.excerpt}
                        </p>

                        <div className="flex flex-wrap gap-2 mb-4">
                          {post.tags.map((tag) => (
                            <span
                              key={tag}
                              className="px-3 py-1 bg-[var(--border)] rounded-full text-sm"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>

                        <Link
                          href={`/blog/${post.slug}`}
                          className="text-[var(--primary)] font-semibold hover:underline"
                        >
                          Read more →
                        </Link>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
