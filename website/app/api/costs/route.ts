/**
 * Cost Tracking API Route
 *
 * Returns recent API requests with cost savings data from the
 * Empathy Framework cost tracker.
 */

export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

interface CostRequest {
  timestamp: string;
  model: string;
  tier: string;
  task_type: string;
  input_tokens: number;
  output_tokens: number;
  actual_cost: number;
  baseline_cost: number;
  savings: number;
}

interface CostData {
  requests: CostRequest[];
  daily_totals: Record<string, {
    requests: number;
    input_tokens: number;
    output_tokens: number;
    actual_cost: number;
    baseline_cost: number;
    savings: number;
  }>;
  created_at: string;
  last_updated: string;
}

export async function GET(request: Request): Promise<Response> {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '10', 10);
    const days = parseInt(searchParams.get('days') || '7', 10);

    // Try to find .empathy/costs.json in the project root
    const possiblePaths = [
      path.join(process.cwd(), '..', '.empathy', 'costs.json'),
      path.join(process.cwd(), '.empathy', 'costs.json'),
      path.join(process.env.HOME || '', 'empathy_11_6_2025', 'Empathy-framework', '.empathy', 'costs.json'),
    ];

    let costsData: CostData | null = null;
    let loadedPath = '';

    for (const filePath of possiblePaths) {
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        costsData = JSON.parse(content);
        loadedPath = filePath;
        break;
      } catch {
        // Try next path
      }
    }

    if (!costsData) {
      // Return demo data if no real data found
      return NextResponse.json({
        success: true,
        data: {
          recent_requests: getDemoRequests(limit),
          summary: getDemoSummary(),
          source: 'demo',
        },
      });
    }

    // Get last N requests
    const recentRequests = costsData.requests
      .slice(-limit)
      .reverse()
      .map(req => ({
        ...req,
        timestamp_display: formatTimestamp(req.timestamp),
        savings_display: `$${req.savings.toFixed(4)}`,
        cost_display: `$${req.actual_cost.toFixed(4)}`,
      }));

    // Calculate summary for the period
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    const cutoffStr = cutoffDate.toISOString().split('T')[0];

    const summary = {
      total_requests: 0,
      total_savings: 0,
      total_cost: 0,
      baseline_cost: 0,
      savings_percent: 0,
      by_tier: { cheap: 0, capable: 0, premium: 0 } as Record<string, number>,
    };

    for (const [date, daily] of Object.entries(costsData.daily_totals)) {
      if (date >= cutoffStr) {
        summary.total_requests += daily.requests;
        summary.total_savings += daily.savings;
        summary.total_cost += daily.actual_cost;
        summary.baseline_cost += daily.baseline_cost;
      }
    }

    if (summary.baseline_cost > 0) {
      summary.savings_percent = Math.round((summary.total_savings / summary.baseline_cost) * 100);
    }

    // Count by tier
    for (const req of costsData.requests) {
      if (req.timestamp >= cutoffDate.toISOString()) {
        const tier = req.tier || 'capable';
        summary.by_tier[tier] = (summary.by_tier[tier] || 0) + 1;
      }
    }

    return NextResponse.json({
      success: true,
      data: {
        recent_requests: recentRequests,
        summary: {
          ...summary,
          total_savings_display: `$${summary.total_savings.toFixed(2)}`,
          total_cost_display: `$${summary.total_cost.toFixed(2)}`,
        },
        source: 'live',
        loaded_from: loadedPath,
        last_updated: costsData.last_updated,
      },
    });
  } catch (error) {
    console.error('Cost tracking API error:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Failed to retrieve cost data',
      },
      { status: 500 }
    );
  }
}

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

function getDemoRequests(limit: number) {
  const tasks = ['code_review', 'bug_analysis', 'docs_generation', 'refactor', 'test_generation'];
  const tiers = ['cheap', 'capable', 'premium'];
  const models: Record<string, string> = {
    cheap: 'claude-3-5-haiku-20241022',
    capable: 'claude-sonnet-4-20250514',
    premium: 'claude-opus-4-5-20251101',
  };

  return Array.from({ length: limit }, (_, i) => {
    const tier = tiers[Math.floor(Math.random() * 3)];
    const task = tasks[Math.floor(Math.random() * tasks.length)];
    const inputTokens = 500 + Math.floor(Math.random() * 2000);
    const outputTokens = 200 + Math.floor(Math.random() * 1000);

    const pricing: Record<string, { input: number; output: number }> = {
      cheap: { input: 0.80, output: 4.00 },
      capable: { input: 3.00, output: 15.00 },
      premium: { input: 15.00, output: 75.00 },
    };

    const p = pricing[tier];
    const actual = (inputTokens / 1000000) * p.input + (outputTokens / 1000000) * p.output;
    const baseline = (inputTokens / 1000000) * 15 + (outputTokens / 1000000) * 75;
    const savings = baseline - actual;

    return {
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      timestamp_display: i === 0 ? 'just now' : `${i}h ago`,
      model: models[tier],
      tier,
      task_type: task,
      input_tokens: inputTokens,
      output_tokens: outputTokens,
      actual_cost: actual,
      baseline_cost: baseline,
      savings,
      cost_display: `$${actual.toFixed(4)}`,
      savings_display: `$${savings.toFixed(4)}`,
    };
  });
}

function getDemoSummary() {
  return {
    total_requests: 127,
    total_savings: 2.34,
    total_cost: 0.89,
    baseline_cost: 3.23,
    savings_percent: 72,
    total_savings_display: '$2.34',
    total_cost_display: '$0.89',
    by_tier: { cheap: 89, capable: 31, premium: 7 },
  };
}
