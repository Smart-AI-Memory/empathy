'use client';

import { useEffect, useState } from 'react';

interface GitHubStats {
  stars: number;
  forks: number;
  openIssues: number;
  watchers: number;
  lastUpdated: string;
}

interface GitHubStatsProps {
  repo?: string;
  compact?: boolean;
}

export default function GitHubStats({ repo = 'Smart-AI-Memory/empathy', compact = false }: GitHubStatsProps) {
  const [stats, setStats] = useState<GitHubStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch(`https://api.github.com/repos/${repo}`, {
          headers: {
            Accept: 'application/vnd.github.v3+json',
          },
          // Cache for 5 minutes
          next: { revalidate: 300 },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch GitHub stats');
        }

        const data = await response.json();
        setStats({
          stars: data.stargazers_count || 0,
          forks: data.forks_count || 0,
          openIssues: data.open_issues_count || 0,
          watchers: data.watchers_count || 0,
          lastUpdated: data.updated_at,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [repo]);

  if (loading) {
    return (
      <div className="flex items-center gap-4">
        <div className="animate-pulse bg-[var(--border)] h-8 w-24 rounded"></div>
        <div className="animate-pulse bg-[var(--border)] h-8 w-24 rounded"></div>
        <div className="animate-pulse bg-[var(--border)] h-8 w-24 rounded"></div>
      </div>
    );
  }

  if (error || !stats) {
    return null;
  }

  if (compact) {
    return (
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
          <span className="font-bold">{stats.stars.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="1" />
            <circle cx="19" cy="12" r="1" />
            <circle cx="5" cy="12" r="1" />
            <path d="M12 19.5V11" />
            <path d="M5 12v7" />
            <path d="M19 12v7" />
          </svg>
          <span className="font-bold">{stats.forks.toLocaleString()}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-4 text-center hover:border-[var(--primary)] transition-all">
        <div className="text-3xl font-bold text-[var(--primary)] mb-1">
          {stats.stars.toLocaleString()}
        </div>
        <div className="text-sm text-[var(--muted)] flex items-center justify-center gap-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
          Stars
        </div>
      </div>

      <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-4 text-center hover:border-[var(--secondary)] transition-all">
        <div className="text-3xl font-bold text-[var(--secondary)] mb-1">
          {stats.forks.toLocaleString()}
        </div>
        <div className="text-sm text-[var(--muted)] flex items-center justify-center gap-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="1" />
            <circle cx="19" cy="12" r="1" />
            <circle cx="5" cy="12" r="1" />
            <path d="M12 19.5V11" />
            <path d="M5 12v7" />
            <path d="M19 12v7" />
          </svg>
          Forks
        </div>
      </div>

      <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-4 text-center hover:border-[var(--accent)] transition-all">
        <div className="text-3xl font-bold text-[var(--accent)] mb-1">
          {stats.watchers.toLocaleString()}
        </div>
        <div className="text-sm text-[var(--muted)] flex items-center justify-center gap-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
          Watching
        </div>
      </div>

      <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-4 text-center hover:border-[var(--warning)] transition-all">
        <div className="text-3xl font-bold text-[var(--warning)] mb-1">
          {stats.openIssues.toLocaleString()}
        </div>
        <div className="text-sm text-[var(--muted)] flex items-center justify-center gap-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4" />
            <path d="M12 8h.01" />
          </svg>
          Open Issues
        </div>
      </div>
    </div>
  );
}
