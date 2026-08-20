'use client';

import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Line,
  ComposedChart,
  Bar,
} from 'recharts';
import { TemporalMetrics } from '@/types';
import { formatDate, formatINR, formatPercent } from '@/lib/formatters';
import { Activity, Calendar, Zap, Shield } from 'lucide-react';

export interface SpendingTimelineChartProps {
  temporalMetrics: TemporalMetrics;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    name: string;
    dataKey: string;
    payload: {
      date: string;
      amount: string;
      transaction_count: number;
      cumulative_amount: string;
    };
  }>;
  label?: string;
}

const CustomTimelineTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div className="bg-white border-3 border-black shadow-bauhaus-md p-3 font-mono text-xs text-ink z-50">
        <div className="flex items-center gap-2 mb-2 border-b border-black/20 pb-1">
          <Calendar className="w-3.5 h-3.5 text-bauhaus-blue" />
          <span className="font-bold uppercase">{formatDate(item.date, 'full')}</span>
        </div>
        <div className="space-y-1.5">
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Day Spend:</span>
            <span className="font-black text-bauhaus-red">{formatINR(item.amount)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Cumulative Total:</span>
            <span className="font-bold text-bauhaus-blue">
              {formatINR(item.cumulative_amount)}
            </span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Transactions:</span>
            <span className="font-bold">{item.transaction_count} txns</span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

export const SpendingTimelineChart: React.FC<SpendingTimelineChartProps> = ({
  temporalMetrics,
}) => {
  const [viewMode, setViewMode] = useState<'cumulative' | 'daily'>('daily');

  const {
    daily_spending,
    weekday_spend,
    weekend_spend,
    weekday_percentage,
    weekend_percentage,
    avg_daily_burn_rate,
  } = temporalMetrics;

  const chartData = daily_spending.map((item) => ({
    ...item,
    dailyNum: parseFloat(item.amount) || 0,
    cumulativeNum: parseFloat(item.cumulative_amount) || 0,
    formattedDate: formatDate(item.date, 'short'),
  }));

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6 flex flex-col justify-between h-full">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-black gap-3 mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-ink" />
          <h3 className="font-black uppercase tracking-tight text-lg text-ink">
            Daily Spending Timeline & Burn Rate
          </h3>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1 bg-muted p-1 border-2 border-black">
          <button
            onClick={() => setViewMode('daily')}
            className={`px-3 py-1 text-xs font-bold uppercase tracking-wider transition-all ${
              viewMode === 'daily'
                ? 'bg-bauhaus-yellow text-ink border border-black shadow-bauhaus-xs'
                : 'text-ink/70 hover:text-ink'
            }`}
          >
            Daily Spend
          </button>
          <button
            onClick={() => setViewMode('cumulative')}
            className={`px-3 py-1 text-xs font-bold uppercase tracking-wider transition-all ${
              viewMode === 'cumulative'
                ? 'bg-bauhaus-yellow text-ink border border-black shadow-bauhaus-xs'
                : 'text-ink/70 hover:text-ink'
            }`}
          >
            Cumulative Curve
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-64 sm:h-72 w-full my-2">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{ top: 10, right: 10, left: -15, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#E0E0E0"
              vertical={false}
            />
            <XAxis
              dataKey="formattedDate"
              tick={{ fill: '#121212', fontSize: 11, fontWeight: 700, fontFamily: 'monospace' }}
              tickLine={{ stroke: '#121212', strokeWidth: 1.5 }}
              axisLine={{ stroke: '#121212', strokeWidth: 2 }}
            />
            <YAxis
              tick={{ fill: '#121212', fontSize: 10, fontWeight: 700, fontFamily: 'monospace' }}
              tickLine={{ stroke: '#121212', strokeWidth: 1.5 }}
              axisLine={{ stroke: '#121212', strokeWidth: 2 }}
              tickFormatter={(val) => `₹${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
            />
            <Tooltip content={<CustomTimelineTooltip />} />

            {viewMode === 'daily' ? (
              <Bar
                dataKey="dailyNum"
                name="Daily Spend"
                fill="#F0C020"
                stroke="#121212"
                strokeWidth={2}
                radius={[0, 0, 0, 0]}
              />
            ) : (
              <Area
                type="monotone"
                dataKey="cumulativeNum"
                name="Cumulative Total"
                stroke="#1040C0"
                strokeWidth={3}
                fill="#FFF9C4"
                fillOpacity={0.8}
                dot={{
                  stroke: '#121212',
                  strokeWidth: 2,
                  fill: '#1040C0',
                  r: 4,
                }}
                activeDot={{
                  stroke: '#121212',
                  strokeWidth: 3,
                  fill: '#D02020',
                  r: 6,
                }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Behavioral Velocity Metrics Ribbon */}
      <div className="mt-4 pt-4 border-t-2 border-black grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
        {/* Avg Daily Burn */}
        <div className="bg-canvas border-2 border-black p-2.5">
          <div className="text-[10px] font-bold uppercase tracking-wider text-ink/70 flex items-center gap-1 mb-0.5">
            <Zap className="w-3 h-3 text-bauhaus-yellow" />
            <span>Avg Daily Burn Rate</span>
          </div>
          <div className="text-base font-black text-ink">
            {formatINR(avg_daily_burn_rate)} / day
          </div>
        </div>

        {/* Weekday Spend */}
        <div className="bg-canvas border-2 border-black p-2.5">
          <div className="text-[10px] font-bold uppercase tracking-wider text-ink/70 flex items-center justify-between mb-0.5">
            <span>Weekday Spend</span>
            <span className="font-bold bg-muted px-1 border border-black text-[9px]">
              {formatPercent(weekday_percentage)}
            </span>
          </div>
          <div className="text-base font-bold text-ink">
            {formatINR(weekday_spend)}
          </div>
        </div>

        {/* Weekend Spend */}
        <div className="bg-canvas border-2 border-black p-2.5">
          <div className="text-[10px] font-bold uppercase tracking-wider text-ink/70 flex items-center justify-between mb-0.5">
            <span className="text-bauhaus-red font-black">Weekend Spend</span>
            <span
              className={`font-black px-1 border border-black text-[9px] ${
                weekend_percentage > 50
                  ? 'bg-bauhaus-red text-white'
                  : 'bg-muted text-ink'
              }`}
            >
              {formatPercent(weekend_percentage)}
            </span>
          </div>
          <div className="text-base font-black text-bauhaus-red">
            {formatINR(weekend_spend)}
          </div>
        </div>
      </div>
    </div>
  );
};
