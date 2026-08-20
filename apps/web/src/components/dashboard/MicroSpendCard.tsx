'use client';

import React from 'react';
import { MicroSpendMetrics } from '@/types';
import { formatINR, formatPercent } from '@/lib/formatters';
import { Coins, AlertTriangle, ArrowDownRight } from 'lucide-react';

export interface MicroSpendCardProps {
  microSpend: MicroSpendMetrics;
}

export const MicroSpendCard: React.FC<MicroSpendCardProps> = ({ microSpend }) => {
  const {
    threshold,
    count,
    total_amount,
    percentage_of_transactions,
    percentage_of_spend,
    top_micro_merchants,
  } = microSpend;

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6 flex flex-col justify-between h-full">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between pb-4 border-b-2 border-black mb-4">
          <div className="flex items-center gap-2">
            <Coins className="w-5 h-5 text-bauhaus-yellow" />
            <h3 className="font-black uppercase tracking-tight text-lg text-ink">
              Micro-Spending Leak Analysis
            </h3>
          </div>
          <span className="text-xs font-mono font-bold px-2 py-0.5 bg-muted border border-black">
            &lt; {formatINR(threshold, { showDecimals: false })} Purchases
          </span>
        </div>

        {/* Big Metrics Grid */}
        <div className="grid grid-cols-2 gap-3 mb-4 bg-canvas border-2 border-black p-3 font-mono">
          <div>
            <span className="block text-[10px] font-bold uppercase tracking-wider text-ink/70">
              Total Small Purchases
            </span>
            <span className="text-xl font-black text-ink">{count} Swipes</span>
            <span className="block text-[10px] font-bold text-ink/60 mt-0.5">
              {formatPercent(percentage_of_transactions)} of all transactions
            </span>
          </div>

          <div className="border-l border-black/30 pl-3">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-ink/70">
              Cumulative Leak
            </span>
            <span className="text-xl font-black text-bauhaus-red">
              {formatINR(total_amount)}
            </span>
            <span className="block text-[10px] text-ink/60 mt-0.5">
              {formatPercent(percentage_of_spend)} of total cycle spend
            </span>
          </div>
        </div>

        {/* Top Micro Merchants Chips */}
        {top_micro_merchants && top_micro_merchants.length > 0 ? (
          <div>
            <div className="text-xs font-bold uppercase tracking-widest text-ink/75 mb-2">
              Frequent Micro-Outlets
            </div>
            <div className="flex flex-wrap gap-2">
              {top_micro_merchants.map((merchant) => (
                <span
                  key={merchant}
                  className="px-2.5 py-1 bg-bauhaus-yellow-light border border-black font-mono text-xs font-bold text-ink shadow-bauhaus-xs"
                >
                  {merchant}
                </span>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-4 text-center text-xs font-medium text-ink/60 border border-dashed border-black">
            Zero low-ticket micro transactions detected in this billing cycle.
          </div>
        )}
      </div>

      {/* Behavioral Observation Tip */}
      <div className="mt-4 pt-3 border-t-2 border-black flex items-start gap-2 text-xs font-medium text-ink/80">
        <ArrowDownRight className="w-4 h-4 text-bauhaus-red shrink-0 mt-0.5" />
        <span>
          Micro-transactions often conceal recurring delivery convenience fees and impulse add-ons.
        </span>
      </div>
    </div>
  );
};
