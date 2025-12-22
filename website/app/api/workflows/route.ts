import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

interface WorkflowRun {
  workflow: string;
  provider: string;
  success: boolean;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  cost: number;
  baseline_cost: number;
  savings: number;
  savings_percent: number;
  stages: Array<{
    name: string;
    tier: string;
    skipped: boolean;
    cost: number;
    duration_ms: number;
  }>;
  error: string | null;
}

interface WorkflowStats {
  total_runs: number;
  successful_runs: number;
  by_workflow: Record<string, {
    runs: number;
    cost: number;
    savings: number;
    success: number;
  }>;
  by_provider: Record<string, {
    runs: number;
    cost: number;
  }>;
  by_tier: {
    cheap: number;
    capable: number;
    premium: number;
  };
  recent_runs: WorkflowRun[];
  total_cost: number;
  total_savings: number;
  avg_savings_percent: number;
}

// Available workflows (static data)
const AVAILABLE_WORKFLOWS = [
  {
    name: 'research',
    class: 'ResearchSynthesisWorkflow',
    description: 'Cost-optimized research synthesis pipeline',
    stages: ['summarize', 'analyze', 'synthesize'],
    tier_map: { summarize: 'cheap', analyze: 'capable', synthesize: 'premium' },
  },
  {
    name: 'code-review',
    class: 'CodeReviewWorkflow',
    description: 'Tiered code analysis with conditional premium review',
    stages: ['classify', 'scan', 'architect_review'],
    tier_map: { classify: 'cheap', scan: 'capable', architect_review: 'premium' },
  },
  {
    name: 'doc-gen',
    class: 'DocumentGenerationWorkflow',
    description: 'Cost-optimized documentation generation pipeline',
    stages: ['outline', 'write', 'polish'],
    tier_map: { outline: 'cheap', write: 'capable', polish: 'premium' },
  },
];

async function loadWorkflowHistory(): Promise<WorkflowRun[]> {
  try {
    // Try to read from the project root's .empathy directory
    const historyPath = path.join(process.cwd(), '..', '.empathy', 'workflow_runs.json');
    const data = await fs.readFile(historyPath, 'utf-8');
    return JSON.parse(data);
  } catch {
    // Return empty array if file doesn't exist
    return [];
  }
}

function calculateStats(history: WorkflowRun[]): WorkflowStats {
  if (history.length === 0) {
    return {
      total_runs: 0,
      successful_runs: 0,
      by_workflow: {},
      by_provider: {},
      by_tier: { cheap: 0, capable: 0, premium: 0 },
      recent_runs: [],
      total_cost: 0,
      total_savings: 0,
      avg_savings_percent: 0,
    };
  }

  const by_workflow: WorkflowStats['by_workflow'] = {};
  const by_provider: WorkflowStats['by_provider'] = {};
  const by_tier: WorkflowStats['by_tier'] = { cheap: 0, capable: 0, premium: 0 };
  let total_cost = 0;
  let total_savings = 0;
  let successful_runs = 0;

  for (const run of history) {
    const wf_name = run.workflow || 'unknown';
    const provider = run.provider || 'unknown';
    const cost = run.cost || 0;
    const savings = run.savings || 0;

    // By workflow
    if (!by_workflow[wf_name]) {
      by_workflow[wf_name] = { runs: 0, cost: 0, savings: 0, success: 0 };
    }
    by_workflow[wf_name].runs += 1;
    by_workflow[wf_name].cost += cost;
    by_workflow[wf_name].savings += savings;
    if (run.success) {
      by_workflow[wf_name].success += 1;
    }

    // By provider
    if (!by_provider[provider]) {
      by_provider[provider] = { runs: 0, cost: 0 };
    }
    by_provider[provider].runs += 1;
    by_provider[provider].cost += cost;

    // By tier (from stages)
    for (const stage of run.stages || []) {
      if (!stage.skipped) {
        const tier = stage.tier as keyof typeof by_tier;
        if (tier in by_tier) {
          by_tier[tier] += stage.cost || 0;
        }
      }
    }

    total_cost += cost;
    total_savings += savings;
    if (run.success) {
      successful_runs += 1;
    }
  }

  // Calculate average savings percent
  const savings_percents = history
    .filter(r => r.success)
    .map(r => r.savings_percent || 0);
  const avg_savings_percent = savings_percents.length > 0
    ? savings_percents.reduce((a, b) => a + b, 0) / savings_percents.length
    : 0;

  return {
    total_runs: history.length,
    successful_runs,
    by_workflow,
    by_provider,
    by_tier,
    recent_runs: history.slice(-10).reverse(),
    total_cost,
    total_savings,
    avg_savings_percent,
  };
}

// Generate time-series data for charts
function generateTimeSeriesData(history: WorkflowRun[], days: number = 30) {
  const now = new Date();
  const startDate = new Date(now);
  startDate.setDate(startDate.getDate() - days);

  // Initialize daily data
  const dailyData: Record<string, {
    date: string;
    cost: number;
    savings: number;
    baseline: number;
    cheap: number;
    capable: number;
    premium: number;
  }> = {};

  // Fill in all dates
  for (let i = 0; i <= days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    const dateStr = date.toISOString().split('T')[0];
    dailyData[dateStr] = {
      date: dateStr,
      cost: 0,
      savings: 0,
      baseline: 0,
      cheap: 0,
      capable: 0,
      premium: 0,
    };
  }

  // Aggregate history data by day
  for (const run of history) {
    if (!run.started_at) continue;
    const dateStr = run.started_at.split('T')[0];
    if (dailyData[dateStr]) {
      dailyData[dateStr].cost += run.cost || 0;
      dailyData[dateStr].savings += run.savings || 0;
      dailyData[dateStr].baseline += run.baseline_cost || 0;

      // Aggregate tier costs from stages
      for (const stage of run.stages || []) {
        if (!stage.skipped) {
          const tier = stage.tier as 'cheap' | 'capable' | 'premium';
          if (tier in dailyData[dateStr]) {
            dailyData[dateStr][tier] += stage.cost || 0;
          }
        }
      }
    }
  }

  return Object.values(dailyData).sort((a, b) => a.date.localeCompare(b.date));
}

// Generate workflow comparison data for charts
function generateWorkflowComparison(by_workflow: WorkflowStats['by_workflow']) {
  return Object.entries(by_workflow).map(([name, data]) => ({
    name,
    runs: data.runs,
    cost: data.cost,
    savings: data.savings,
    baseline: data.cost + data.savings,
    savingsPercent: data.cost + data.savings > 0
      ? (data.savings / (data.cost + data.savings)) * 100
      : 0,
  }));
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const days = parseInt(searchParams.get('days') || '30', 10);

    const history = await loadWorkflowHistory();
    const stats = calculateStats(history);

    // Generate chart data
    const timeSeries = generateTimeSeriesData(history, days);
    const workflowComparison = generateWorkflowComparison(stats.by_workflow);

    return NextResponse.json({
      ...stats,
      available_workflows: AVAILABLE_WORKFLOWS,
      // Chart data
      chart_data: {
        time_series: timeSeries,
        workflow_comparison: workflowComparison,
      },
    });
  } catch (error) {
    console.error('Error loading workflow stats:', error);
    return NextResponse.json(
      { error: 'Failed to load workflow stats' },
      { status: 500 }
    );
  }
}
