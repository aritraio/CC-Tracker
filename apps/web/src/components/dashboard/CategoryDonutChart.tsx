'use client';

import React, { useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { CategoryBreakdown } from '@/types';
import { formatINR, formatPercent } from '@/lib/formatters';
import { PieChart as PieIcon, Layers } from 'lucide-react';

export interface CategoryDonutChartProps {
  data: CategoryBreakdown[];
  totalSpend: string | number;
}

// Curated Bauhaus Constructivist Palette for Financial Categories
const BAUHAUS_CATEGORY_COLORS: Record<string, string> = {
  'Food & Dining': '#D02020', // Bauhaus Red
  Shopping: '#1040C0', // Bauhaus Blue
  'Groceries & Quick-Commerce': '#F0C020', // Bauhaus Yellow
  'Transport & Fuel': '#121212', // Stark Black
  'Travel & Lodging': '#008844', // Bauhaus Green
  'Bills & Utilities': '#8E44AD', // Deep Purple
  'Entertainment & OTT': '#E67E22', // Orange
  Subscriptions: '#2980B9', // Steel Blue
  'Healthcare & Fitness': '#27AE60', // Emerald Green
  Education: '#34495E', // Slate
  'Rent & Housing': '#D35400', // Rust
  'Fees & Charges': '#C0392B', // Dark Crimson
  'Cash Withdrawal': '#7F8C8D', // Neutral Grey
  'Other / Uncategorized': '#95A5A6', // Light Slate
};

const FALLBACK_COLORS = [
  '#D02020',
  '#1040C0',
  '#F0C020',
  '#121212',
  '#008844',
  '#8E44AD',
  '#E67E22',
  '#2980B9',
  '#27AE60',
  '#34495E',
];

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    payload: {
      category: string;
      total_amount: string;
      percentage: number;
      transaction_count: number;
      top_merchants: string[];
      fill: string;
    };
  }>;
}

const CustomDonutTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div className="bg-white border-3 border-black shadow-bauhaus-md p-3 font-mono text-xs text-ink z-50">
        <div className="flex items-center gap-2 mb-1.5 border-b border-black/20 pb-1">
          <span
            className="w-3 h-3 border border-black inline-block"
            style={{ backgroundColor: item.fill }}
          />
          <span className="font-bold text-sm uppercase tracking-tight">{item.category}</span>
        </div>
        <div className="space-y-1">
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Amount:</span>
            <span className="font-bold">{formatINR(item.total_amount)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Share:</span>
            <span className="font-bold">{formatPercent(item.percentage)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Transactions:</span>
            <span className="font-bold">{item.transaction_count}</span>
          </div>
          {item.top_merchants && item.top_merchants.length > 0 && (
            <div className="pt-1 text-[10px] text-ink/60 border-t border-black/10">
              Merchants: {item.top_merchants.join(', ')}
            </div>
          )}
        </div>
      </div>
    );
  }
  return null;
};

export const CategoryDonutChart: React.FC<CategoryDonutChartProps> = ({
  data,
  totalSpend,
}) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const chartData = data.map((item, index) => ({
    ...item,
    value: parseFloat(item.total_amount) || 0,
    fill:
      BAUHAUS_CATEGORY_COLORS[item.category] ||
      FALLBACK_COLORS[index % FALLBACK_COLORS.length],
  }));

  const activeCategory = activeIndex !== null ? chartData[activeIndex] : null;

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6 flex flex-col justify-between h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b-2 border-black mb-4">
        <div className="flex items-center gap-2">
          <PieIcon className="w-5 h-5 text-ink" />
          <h3 className="font-black uppercase tracking-tight text-lg text-ink">
            Category Breakdown
          </h3>
        </div>
        <span className="text-xs font-mono font-bold px-2 py-0.5 bg-muted border border-black">
          {data.length} Categories
        </span>
      </div>

      {/* Donut Visualizer Area */}
      <div className="relative h-64 w-full flex items-center justify-center my-2">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomDonutTooltip />} />
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={95}
              paddingAngle={2}
              dataKey="value"
              nameKey="category"
              stroke="#121212"
              strokeWidth={3}
              onMouseEnter={(_, index) => setActiveIndex(index)}
              onMouseLeave={() => setActiveIndex(null)}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.fill}
                  className="transition-all duration-150 cursor-pointer"
                  opacity={activeIndex === null || activeIndex === index ? 1 : 0.4}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center Constructivist Label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center p-2">
          {activeCategory ? (
            <div className="animate-in fade-in zoom-in-95 duration-100 max-w-[120px]">
              <span className="block text-[10px] font-bold uppercase tracking-widest text-ink/70 truncate">
                {activeCategory.category}
              </span>
              <span className="block text-sm sm:text-base font-black font-mono text-ink">
                {formatINR(activeCategory.total_amount, { showDecimals: false })}
              </span>
              <span className="inline-block text-[10px] font-mono font-bold bg-bauhaus-yellow px-1 py-0.2 border border-black mt-0.5">
                {formatPercent(activeCategory.percentage)}
              </span>
            </div>
          ) : (
            <div>
              <span className="block text-[10px] font-bold uppercase tracking-widest text-ink/60">
                Total Spend
              </span>
              <span className="block text-sm sm:text-base font-black font-mono text-ink">
                {formatINR(totalSpend, { showDecimals: false })}
              </span>
              <span className="block text-[9px] font-bold uppercase text-ink/50 mt-0.5">
                {data.length} Categories
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Category Breakdown Table / Legend */}
      <div className="mt-4 pt-4 border-t-2 border-black max-h-56 overflow-y-auto space-y-2 pr-1">
        {chartData.map((cat, idx) => (
          <div
            key={cat.category}
            onMouseEnter={() => setActiveIndex(idx)}
            onMouseLeave={() => setActiveIndex(null)}
            className={`flex items-center justify-between p-2 text-xs border border-black cursor-pointer transition-all duration-100 ${
              activeIndex === idx
                ? 'bg-bauhaus-yellow-light border-2 border-black translate-x-1 shadow-bauhaus-xs'
                : 'bg-canvas hover:bg-white'
            }`}
          >
            <div className="flex items-center gap-2 min-w-0 pr-2">
              <span
                className="w-3 h-3 border border-black shrink-0"
                style={{ backgroundColor: cat.fill }}
              />
              <span className="font-bold text-ink truncate">{cat.category}</span>
              <span className="text-[10px] font-mono text-ink/60 hidden sm:inline">
                ({cat.transaction_count} txns)
              </span>
            </div>

            <div className="flex items-center gap-3 shrink-0 font-mono">
              <span className="font-bold text-ink">{formatINR(cat.total_amount)}</span>
              <span className="w-12 text-right text-[11px] font-bold bg-muted px-1.5 py-0.5 border border-black">
                {formatPercent(cat.percentage)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
