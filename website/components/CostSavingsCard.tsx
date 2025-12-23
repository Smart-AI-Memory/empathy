'use client';

/**
 * Cost Savings Card Component
 *
 * Displays recent API requests with cost savings from model routing.
 * Shows how much money was saved by using appropriate model tiers.
 */

import { useEffect, useState } from 'react';

interface CostRequest {
  timestamp: string;
  timestamp_display: string;
  model: string;
  tier: string;
  task_type: string;
  input_tokens: number;
  output_tokens: number;
  actual_cost: number;
  baseline_cost: number;
  savings: number;
  cost_display: string;
  savings_display: string;
}

interface CostSummary {
  total_requests: number;
  total_savings: number;
  total_cost: number;
  baseline_cost: number;
  savings_percent: number;
  total_savings_display: string;
  total_cost_display: string;
  by_tier: Record<string, number>;
}

interface CostData {
  recent_requests: CostRequest[];
  summary: CostSummary;
  source: string;
  last_updated?: string;
}

const tierColors: Record<string, string> = {
  cheap: 'bg-green-100 text-green-700',
  capable: 'bg-blue-100 text-blue-700',
  premium: 'bg-purple-100 text-purple-700',
};

const tierIcons: Record<string, string> = {
  cheap: '\u26A1', // Lightning
  capable: '\u2699', // Gear
  premium: '\u2B50', // Star
};

export default function CostSavingsCard() {
  const [data, setData] = useState<CostData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCosts() {
      try {
        const response = await fetch('/api/costs?limit=10&days=7');
        const result = await response.json();

        if (result.success) {
          setData(result.data);
        } else {
          setError(result.error || 'Failed to load cost data');
        }
      } catch {
        setError('Failed to connect to cost tracking API');
      } finally {
        setLoading(false);
      }
    }

    fetchCosts();
    // Refresh every 30 seconds
    const interval = setInterval(fetchCosts, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-12 bg-gray-100 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[var(--background)] border-2 border-red-200 rounded-lg p-6">
        <div className="text-red-600 text-sm">{error}</div>
      </div>
    );
  }

  if (!data) return null;

  const { recent_requests, summary, source } = data;

  return (
    <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg overflow-hidden">
      {/* Header with summary */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-4 text-white">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-bold text-lg flex items-center gap-2">
            <span>\uD83D\uDCB0</span> Cost Savings
          </h3>
          {source === 'demo' && (
            <span className="text-xs bg-white/20 px-2 py-0.5 rounded">Demo Data</span>
          )}
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold">{summary.total_savings_display}</div>
            <div className="text-xs opacity-80">Saved (7d)</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{summary.savings_percent}%</div>
            <div className="text-xs opacity-80">Reduction</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{summary.total_requests}</div>
            <div className="text-xs opacity-80">Requests</div>
          </div>
        </div>
      </div>

      {/* Tier breakdown */}
      <div className="px-4 py-3 bg-gray-50 border-b border-[var(--border)]">
        <div className="flex gap-3 justify-center">
          {Object.entries(summary.by_tier).map(([tier, count]) => (
            <div
              key={tier}
              className={`px-3 py-1 rounded-full text-xs font-medium ${tierColors[tier] || 'bg-gray-100'}`}
            >
              {tierIcons[tier]} {tier}: {count}
            </div>
          ))}
        </div>
      </div>

      {/* Recent requests list */}
      <div className="divide-y divide-[var(--border)]">
        <div className="px-4 py-2 bg-gray-50 text-xs font-semibold text-gray-500 grid grid-cols-12 gap-2">
          <div className="col-span-3">Task</div>
          <div className="col-span-2">Tier</div>
          <div className="col-span-2 text-right">Cost</div>
          <div className="col-span-3 text-right">Saved</div>
          <div className="col-span-2 text-right">When</div>
        </div>
        {recent_requests.slice(0, 10).map((req, idx) => (
          <div
            key={idx}
            className="px-4 py-3 grid grid-cols-12 gap-2 items-center text-sm hover:bg-gray-50 transition-colors"
          >
            <div className="col-span-3 truncate font-medium text-gray-900">
              {formatTaskName(req.task_type)}
            </div>
            <div className="col-span-2">
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${tierColors[req.tier] || 'bg-gray-100'}`}>
                {tierIcons[req.tier]} {req.tier}
              </span>
            </div>
            <div className="col-span-2 text-right text-gray-600">
              {req.cost_display}
            </div>
            <div className="col-span-3 text-right">
              <span className="text-green-600 font-semibold">
                +{req.savings_display}
              </span>
            </div>
            <div className="col-span-2 text-right text-gray-400 text-xs">
              {req.timestamp_display}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 text-center">
        <p className="text-xs text-gray-500">
          Smart model routing uses cheaper models for simple tasks
        </p>
      </div>
    </div>
  );
}

function formatTaskName(task: string): string {
  return task
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}
