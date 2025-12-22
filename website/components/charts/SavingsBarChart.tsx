'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface WorkflowSavings {
  name: string;
  cost: number;
  savings: number;
  baseline: number;
  savingsPercent: number;
}

interface SavingsBarChartProps {
  data: WorkflowSavings[];
  className?: string;
}

export default function SavingsBarChart({ data, className = '' }: SavingsBarChartProps) {
  // Sort by savings percentage descending
  const sortedData = [...data].sort((a, b) => b.savingsPercent - a.savingsPercent);

  // Format currency
  const formatCurrency = (value: number) => `$${value.toFixed(4)}`;

  // Color based on savings percentage
  const getColor = (percent: number) => {
    if (percent >= 60) return '#10b981'; // Green
    if (percent >= 40) return '#3b82f6'; // Blue
    if (percent >= 20) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  // Custom tooltip
  const CustomTooltip = ({
    active,
    payload,
    label,
  }: {
    active?: boolean;
    payload?: Array<{ value: number; name: string }>;
    label?: string;
  }) => {
    if (!active || !payload || !payload.length) return null;

    const workflow = sortedData.find((d) => d.name === label);
    if (!workflow) return null;

    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        <div className="space-y-1 text-sm">
          <p className="text-gray-600">
            Actual Cost: <span className="font-medium text-indigo-600">{formatCurrency(workflow.cost)}</span>
          </p>
          <p className="text-gray-600">
            Baseline: <span className="font-medium text-gray-500">{formatCurrency(workflow.baseline)}</span>
          </p>
          <p className="text-gray-600">
            Savings: <span className="font-medium text-green-600">{formatCurrency(workflow.savings)}</span>
          </p>
          <p className="text-gray-600">
            Savings %: <span className="font-medium text-green-600">{workflow.savingsPercent.toFixed(0)}%</span>
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Savings by Workflow</h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={sortedData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={true} vertical={false} />
            <XAxis
              type="number"
              tickFormatter={formatCurrency}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
              width={75}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '10px' }}
              formatter={(value) => (
                <span className="text-sm text-gray-600">{value}</span>
              )}
            />
            <Bar
              dataKey="cost"
              name="Actual Cost"
              fill="#6366f1"
              radius={[0, 4, 4, 0]}
            />
            <Bar
              dataKey="savings"
              name="Savings"
              radius={[0, 4, 4, 0]}
            >
              {sortedData.map((entry) => (
                <Cell key={`cell-${entry.name}`} fill={getColor(entry.savingsPercent)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-500">Total Savings</p>
            <p className="text-xl font-semibold text-green-600">
              {formatCurrency(sortedData.reduce((sum, d) => sum + d.savings, 0))}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Average Savings</p>
            <p className="text-xl font-semibold text-green-600">
              {sortedData.length > 0
                ? (sortedData.reduce((sum, d) => sum + d.savingsPercent, 0) / sortedData.length).toFixed(0)
                : 0}
              %
            </p>
          </div>
        </div>
      </div>

      {/* Color Legend */}
      <div className="mt-4 flex justify-center gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 bg-green-500 rounded-full"></span> 60%+
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 bg-blue-500 rounded-full"></span> 40-59%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 bg-amber-500 rounded-full"></span> 20-39%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 bg-red-500 rounded-full"></span> &lt;20%
        </span>
      </div>
    </div>
  );
}
