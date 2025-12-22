'use client';

import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface CostDataPoint {
  date: string;
  cost: number;
  savings: number;
  baseline: number;
}

interface CostTrendChartProps {
  data: CostDataPoint[];
  className?: string;
}

export default function CostTrendChart({ data, className = '' }: CostTrendChartProps) {
  const [timeRange, setTimeRange] = useState<7 | 30 | 90>(7);

  // Filter data based on time range
  const filteredData = data.slice(-timeRange);

  // Format currency for tooltip
  const formatCurrency = (value: number) => `$${value.toFixed(4)}`;

  // Format date for axis
  const formatDate = (date: string) => {
    const d = new Date(date);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Cost Trend</h3>
        <div className="flex gap-1">
          {([7, 30, 90] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                timeRange === range
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {range}d
            </button>
          ))}
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={filteredData}
            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              tickFormatter={formatCurrency}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
              width={70}
            />
            <Tooltip
              formatter={(value) => formatCurrency(Number(value) || 0)}
              labelFormatter={(label) => `Date: ${label}`}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}
            />
            <Legend
              wrapperStyle={{ paddingTop: '10px' }}
              formatter={(value) => (
                <span className="text-sm text-gray-600">{value}</span>
              )}
            />
            <Line
              type="monotone"
              dataKey="cost"
              name="Actual Cost"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ fill: '#6366f1', strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="baseline"
              name="Baseline (Premium)"
              stroke="#9ca3af"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="savings"
              name="Savings"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ fill: '#10b981', strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
        <div className="text-center">
          <p className="text-sm text-gray-500">Total Cost</p>
          <p className="text-lg font-semibold text-indigo-600">
            {formatCurrency(filteredData.reduce((sum, d) => sum + d.cost, 0))}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500">Total Savings</p>
          <p className="text-lg font-semibold text-green-600">
            {formatCurrency(filteredData.reduce((sum, d) => sum + d.savings, 0))}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500">Avg Savings %</p>
          <p className="text-lg font-semibold text-green-600">
            {(
              (filteredData.reduce((sum, d) => sum + d.savings, 0) /
                Math.max(filteredData.reduce((sum, d) => sum + d.baseline, 0), 0.0001)) *
              100
            ).toFixed(0)}
            %
          </p>
        </div>
      </div>
    </div>
  );
}
