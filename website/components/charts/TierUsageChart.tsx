'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TierDataPoint {
  date: string;
  cheap: number;
  capable: number;
  premium: number;
}

interface TierUsageChartProps {
  data: TierDataPoint[];
  className?: string;
}

export default function TierUsageChart({ data, className = '' }: TierUsageChartProps) {
  // Format currency for tooltip
  const formatCurrency = (value: number) => `$${value.toFixed(4)}`;

  // Format date for axis
  const formatDate = (date: string) => {
    const d = new Date(date);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  };

  // Calculate totals
  const totals = data.reduce(
    (acc, d) => ({
      cheap: acc.cheap + d.cheap,
      capable: acc.capable + d.capable,
      premium: acc.premium + d.premium,
    }),
    { cheap: 0, capable: 0, premium: 0 }
  );

  const total = totals.cheap + totals.capable + totals.premium;

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Tier Usage Over Time</h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
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
              formatter={(value, name) => [
                formatCurrency(Number(value) || 0),
                String(name).charAt(0).toUpperCase() + String(name).slice(1),
              ]}
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
                <span className="text-sm text-gray-600">
                  {value.charAt(0).toUpperCase() + value.slice(1)}
                </span>
              )}
            />
            <Area
              type="monotone"
              dataKey="cheap"
              name="cheap"
              stackId="1"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="capable"
              name="capable"
              stackId="1"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="premium"
              name="premium"
              stackId="1"
              stroke="#8b5cf6"
              fill="#8b5cf6"
              fillOpacity={0.8}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Tier Legend with Percentages */}
      <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 bg-green-500 rounded-full"></span>
          <div>
            <p className="text-sm font-medium text-gray-900">Cheap</p>
            <p className="text-xs text-gray-500">
              {formatCurrency(totals.cheap)} ({total > 0 ? ((totals.cheap / total) * 100).toFixed(0) : 0}%)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
          <div>
            <p className="text-sm font-medium text-gray-900">Capable</p>
            <p className="text-xs text-gray-500">
              {formatCurrency(totals.capable)} ({total > 0 ? ((totals.capable / total) * 100).toFixed(0) : 0}%)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 bg-purple-500 rounded-full"></span>
          <div>
            <p className="text-sm font-medium text-gray-900">Premium</p>
            <p className="text-xs text-gray-500">
              {formatCurrency(totals.premium)} ({total > 0 ? ((totals.premium / total) * 100).toFixed(0) : 0}%)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
