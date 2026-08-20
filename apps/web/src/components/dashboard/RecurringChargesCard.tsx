'use client';

import React from 'react';
import { RecurringAnalysis } from '@/types';
import { formatINR, formatPercent } from '@/lib/formatters';
import { Repeat, Calendar, ShieldCheck, AlertCircle } from 'lucide-react';

export interface RecurringChargesCardProps {
  recurringAnalysis: RecurringAnalysis;
}

export const RecurringChargesCard: React.FC<RecurringChargesCardProps> = ({
  recurringAnalysis,
}) => {
  const { items, total_monthly_recurring, total_annual_recurring, recurring_percentage_of_spend } =
    recurringAnalysis;

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6 flex flex-col justify-between h-full">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between pb-4 border-b-2 border-black mb-4">
          <div className="flex items-center gap-2">
            <Repeat className="w-5 h-5 text-bauhaus-blue" />
            <h3 className="font-black uppercase tracking-tight text-lg text-ink">
              Subscriptions & Recurring Dues
            </h3>
          </div>
          <span className="text-xs font-mono font-bold px-2 py-0.5 bg-bauhaus-yellow border border-black">
            {items.length} Active
          </span>
        </div>

        {/* Big Numbers Banner */}
        <div className="grid grid-cols-2 gap-3 mb-4 bg-canvas border-2 border-black p-3 font-mono">
          <div>
            <span className="block text-[10px] font-bold uppercase tracking-wider text-ink/70">
              Monthly Recurring
            </span>
            <span className="text-xl font-black text-ink">
              {formatINR(total_monthly_recurring)}
            </span>
            <span className="block text-[10px] font-bold text-bauhaus-blue mt-0.5">
              {formatPercent(recurring_percentage_of_spend)} of cycle spend
            </span>
          </div>

          <div className="border-l border-black/30 pl-3">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-ink/70">
              Annualized Burden
            </span>
            <span className="text-xl font-black text-bauhaus-red">
              {formatINR(total_annual_recurring)}
            </span>
            <span className="block text-[10px] text-ink/60 mt-0.5">
              Projected 12-mo cost
            </span>
          </div>
        </div>

        {/* Subscriptions List */}
        {items.length === 0 ? (
          <div className="p-6 text-center text-sm font-medium text-ink/60 border border-dashed border-black">
            No recurring subscription charges detected in this billing statement.
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((item) => (
              <div
                key={item.merchant_name}
                className="flex items-center justify-between p-2.5 bg-paper border-2 border-black shadow-bauhaus-xs text-xs font-mono"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 bg-bauhaus-blue text-white border border-black flex items-center justify-center font-black">
                    {item.merchant_name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-bold text-ink text-sm">{item.merchant_name}</div>
                    <div className="text-[10px] text-ink/60 uppercase">
                      {item.category} • {item.frequency}
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="font-black text-sm text-ink">{formatINR(item.amount)}</div>
                  <div className="text-[10px] text-ink/70">
                    {formatINR(item.annualized_cost)} / yr
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Audit Insight Note */}
      <div className="mt-4 pt-3 border-t-2 border-black flex items-center gap-2 text-xs font-medium text-ink/80">
        <ShieldCheck className="w-4 h-4 text-bauhaus-green shrink-0" />
        <span>Audited against 40+ known Indian OTT & SaaS subscription billing patterns.</span>
      </div>
    </div>
  );
};
