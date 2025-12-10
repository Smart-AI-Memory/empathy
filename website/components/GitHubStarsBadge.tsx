'use client';

import { useEffect, useState } from 'react';

interface GitHubStarsBadgeProps {
  repo?: string;
}

export default function GitHubStarsBadge({
  repo = 'Smart-AI-Memory/empathy-framework'
}: GitHubStarsBadgeProps) {
  const [stars, setStars] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStars() {
      try {
        const response = await fetch(`https://api.github.com/repos/${repo}`, {
          headers: {
            Accept: 'application/vnd.github.v3+json',
          },
          next: { revalidate: 3600 },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch');
        }

        const data = await response.json();
        setStars(data.stargazers_count || 0);
      } catch {
        setStars(null);
      } finally {
        setLoading(false);
      }
    }

    fetchStars();
  }, [repo]);

  if (loading) {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-[#1E40AF] text-white">
        <svg
          className="animate-pulse"
          xmlns="http://www.w3.org/2000/svg"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="white"
          aria-hidden="true"
        >
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
        <span className="w-8 h-4 bg-white/30 rounded animate-pulse"></span>
      </span>
    );
  }

  if (stars === null) {
    return null;
  }

  return (
    <a
      href={`https://github.com/${repo}`}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-[#1E40AF] text-white hover:bg-[#1E3A8A] transition-colors"
      aria-label={`${stars.toLocaleString()} GitHub stars`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="white"
        aria-hidden="true"
      >
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
      <span className="text-white">{stars.toLocaleString()} stars</span>
    </a>
  );
}
