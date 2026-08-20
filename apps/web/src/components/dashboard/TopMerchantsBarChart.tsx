'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { MerchantConcentration } from '@/types';
import { formatINR, formatPercent } from '@/lib/formatters';
import { Store, TrendingUp } from 'lucide-react';

export interface TopMerchantsBarChartProps {
  merchants: MerchantConcentration[];
  totalSpend: string | number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: MerchantConcentration;
  }>;
}

const CustomMerchantTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div className="bg-white border-3 border-black shadow-bauhaus-md p-3 font-mono text-xs text-ink z-50">
        <div className="flex items-center gap-2 mb-1.5 border-b border-black/20 pb-1">
          <Store className="w-3.5 h-3.5 text-bauhaus-blue" />
          <span className="font-bold uppercase text-sm">{item.merchant_name}</span>
        </div>
        <div className="space-y-1">
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Category:</span>
            <span className="font-bold">{item.category}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Total Spend:</span>
            <span className="font-black text-bauhaus-red">{formatINR(item.total_amount)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-ink/70">Cycle Share:</span>
            <span className="font-bold">{formatPercent(item.percentage)}</span>
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

export const TopMerchantsBarChart: React.FC<TopMerchantsBarChartProps> = ({
  merchants,
  totalSpend,
}) => {
  // Take top 8 or 10 merchants
  const topMerchants = merchants.slice(0, 8);
  const chartData = topMerchants.map((item) => ({
    ...item,
    amountNum: parseFloat(item.total_amount) || 0,
  }));

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6 flex flex-col justify-between h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b-2 border-black mb-4">
        <div className="flex items-center gap-2">
          <Store className="w-5 h-5 text-ink" />
          <h3 className="font-black uppercase tracking-tight text-lg text-ink">
            Top Merchant Concentration
          </h3>
        </div>
        <span className="text-xs font-mono font-bold px-2 py-0.5 bg-muted border border-black">
          Top {chartData.length} Outflows
        </span>
      </div>

      {/* Bar Chart Canvas */}
      <div className="h-64 sm:h-72 w-full my-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={chartData}
            margin={{ top: 5, right: 30, left: 25, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#E0E0E0"
              horizontal={false}
            />
            <XAxis
              type="number"
              tick={{ fill: '#121212', fontSize: 10, fontWeight: 700, fontFamily: 'monospace' }}
              tickLine={{ stroke: '#121212', strokeWidth: 1.5 }}
              axisLine={{ stroke: '#121212', strokeWidth: 2 }}
              tickFormatter={(val) => `₹${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
            />
            <YAxis
              type="category"
              dataKey="merchant_name"
              tick={{ fill: '#121212', fontSize: 11, fontWeight: 700 }}
              tickLine={{ stroke: '#121212', strokeWidth: 1.5 }}
              axisLine={{ stroke: '#121212', strokeWidth: 2 }}
              width={75}
            />
            <Tooltip content={<CustomMerchantTooltip />} />
            <Bar
              dataKey="amountNum"
              name="Spend Amount"
              stroke="#121212"
              strokeWidth={2}
              radius={[0, 0, 0, 0]}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`merchant-bar-${index}`}
                  fill={
                    index === 0
                      ? '#D02020'
                      : index === 1
                      ? '#1040C0'
                      : index === 2
                      ? '#F0C020'
                      : '#121212'
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top 3 Merchant Share Summary */}
      <div className="mt-4 pt-4 border-t-2 border-black grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs font-mono">
        {chartData.slice(0, 3).map((item, idx) => (
          <div key={item.merchant_name} className="bg-canvas border border-black p-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-ink truncate">
                #{idx + 1} {item.merchant_name}
              </span>
              <span className="text-[10px] font-bold bg-bauhaus-yellow px-1 border border-black">
                {formatPercent(item.percentage)}
              </span>
            </div>
            <div className="text-sm font-black text-ink mt-1">
              {formatINR(item.total_amount)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
