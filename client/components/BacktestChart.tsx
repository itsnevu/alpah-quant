"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Props {
  data: { timestamp: string; value: number }[];
}

export default function BacktestChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 10, bottom: 5, left: 0 }}>
        <defs>
          <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10B981" stopOpacity={0.2}/>
            <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(75, 85, 99, 0.2)" vertical={false} />
        <XAxis 
          dataKey="timestamp" 
          stroke="#6B7280" 
          fontSize={10}
          tickLine={false}
          axisLine={false}
          dy={10}
        />
        <YAxis 
          stroke="#6B7280" 
          fontSize={10}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `$${value.toLocaleString()}`}
          domain={['auto', 'auto']}
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#030712', border: '1px solid #1F2937', borderRadius: '0.75rem', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)' }}
          itemStyle={{ color: '#34D399', fontSize: '12px' }}
          labelStyle={{ color: '#9CA3AF', fontSize: '11px', marginBottom: '0.25rem' }}
          formatter={(value: number) => [`$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`, 'Portfolio Equity']}
        />
        <Area 
          type="monotone" 
          dataKey="value" 
          stroke="#10B981" 
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorEquity)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
