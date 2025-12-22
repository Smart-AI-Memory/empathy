'use client';

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface WorkflowData {
  name: string;
  runs: number;
  cost: number;
  savings: number;
}

interface WorkflowPieChartProps {
  data: WorkflowData[];
  dataKey?: 'runs' | 'cost' | 'savings';
  className?: string;
}

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#c084fc', '#d8b4fe'];

export default function WorkflowPieChart({
  data,
  dataKey = 'runs',
  className = '',
}: WorkflowPieChartProps) {
  // Format value based on data key
  const formatValue = (value: number) => {
    if (dataKey === 'runs') return `${value} runs`;
    return `$${value.toFixed(4)}`;
  };

  // Calculate total
  const total = data.reduce((sum, d) => sum + d[dataKey], 0);

  // Custom label - using any for recharts internal typing
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const renderCustomLabel = (props: any) => {
    const { cx, cy, midAngle, innerRadius, outerRadius, percent } = props;
    if (!percent || percent < 0.05) return null; // Don't show labels for small slices
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
        className="text-xs font-medium"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  const titles: Record<string, string> = {
    runs: 'Workflow Distribution (Runs)',
    cost: 'Cost by Workflow',
    savings: 'Savings by Workflow',
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{titles[dataKey]}</h3>
        <p className="text-sm text-gray-500">
          Total: {dataKey === 'runs' ? `${total} runs` : `$${total.toFixed(4)}`}
        </p>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data as unknown as Record<string, unknown>[]}
              dataKey={dataKey}
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={90}
              paddingAngle={2}
              labelLine={false}
              label={renderCustomLabel}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${entry.name}`}
                  fill={COLORS[index % COLORS.length]}
                  stroke="white"
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => formatValue(Number(value) || 0)}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}
            />
            <Legend
              layout="vertical"
              align="right"
              verticalAlign="middle"
              formatter={(value: string) => (
                <span className="text-sm text-gray-600">{value}</span>
              )}
              wrapperStyle={{ paddingLeft: '20px' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Legend with details */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="grid grid-cols-2 gap-2">
          {data.map((item, index) => (
            <div key={item.name} className="flex items-center gap-2 text-sm">
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              ></span>
              <span className="text-gray-600">{item.name}:</span>
              <span className="font-medium text-gray-900">{formatValue(item[dataKey])}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
