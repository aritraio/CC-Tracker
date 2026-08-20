'use client';

import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldAlert, Sparkles } from 'lucide-react';
import { ReconciliationSummary } from '@/types';
import { formatINR } from '@/lib/formatters';

export interface ReconciliationBadgeProps {
  reconciliation: ReconciliationSummary;
  issuer?: string;
}

export const ReconciliationBadge: React.FC<ReconciliationBadgeProps> = ({
  reconciliation,
  issuer = 'Credit Card Statement',
}) => {
  const isValidated = reconciliation.status === 'VALIDATED';
  const discrepancyNum = parseFloat(reconciliation.discrepancy || '0.00');
  const extractedDebitsNum = parseFloat(reconciliation.extracted_debits || '0.00');
  const statementDueNum = parseFloat(
    reconciliation.statement_total_amount_due ||
      reconciliation.statement_total_debits ||
      reconciliation.extracted_debits ||
      '0.00'
  );

  return (
    <div
      className={`border-2 md:border-4 border-black p-4 sm:p-6 shadow-bauhaus-md md:shadow-bauhaus-lg transition-all duration-200 ${
        isValidated ? 'bg-bauhaus-yellow text-ink' : 'bg-bauhaus-red text-white'
      }`}
    >
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left Status Stamp */}
        <div className="flex items-start sm:items-center gap-3.5">
          {isValidated ? (
            <div className="w-12 h-12 bg-white text-ink border-2 md:border-3 border-black flex items-center justify-center shadow-bauhaus-xs shrink-0">
              <CheckCircle2 className="w-7 h-7 text-ink" />
            </div>
          ) : (
            <div className="w-12 h-12 bg-black text-white border-2 md:border-3 border-white flex items-center justify-center shadow-bauhaus-xs shrink-0">
              <AlertTriangle className="w-7 h-7 text-bauhaus-yellow animate-bounce" />
            </div>
          )}

          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] sm:text-xs font-bold uppercase tracking-widest opacity-85">
                Deterministic Mathematical Audit Stamp
              </span>
              <span className="inline-block px-1.5 py-0.2 text-[9px] font-mono font-bold uppercase bg-black text-white border border-black">
                {issuer}
              </span>
            </div>
            <div className="text-xl sm:text-2xl lg:text-3xl font-black uppercase tracking-tight leading-none mt-1">
              {isValidated
                ? 'RECONCILIATION PASSED: 100% MATCH'
                : 'REVIEW REQUIRED: DISCREPANCY DETECTED'}
            </div>
            <div className="text-xs sm:text-sm font-medium mt-1 opacity-90">
              {isValidated
                ? 'Extracted transaction line items mathematically match printed statement debits within ₹1.00 tolerance.'
                : `Discrepancy of ${formatINR(discrepancyNum)} detected between parsed table rows and statement header dues.`}
            </div>
          </div>
        </div>

        {/* Right Financial Calculation Table */}
        <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 sm:gap-4 bg-white text-ink p-3 sm:p-4 border-2 md:border-3 border-black shadow-bauhaus-xs font-mono text-xs sm:text-sm">
          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Extracted Debits
            </span>
            <span className="font-bold text-sm sm:text-base">
              {formatINR(extractedDebitsNum)}
            </span>
          </div>

          <div className="hidden sm:block w-px h-8 bg-black/40" />

          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Statement Billed
            </span>
            <span className="font-bold text-sm sm:text-base">
              {formatINR(statementDueNum)}
            </span>
          </div>

          <div className="hidden sm:block w-px h-8 bg-black/40" />

          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Delta Variance
            </span>
            <span
              className={`font-black text-sm sm:text-base ${
                discrepancyNum === 0 ? 'text-ink' : 'text-bauhaus-red'
              }`}
            >
              {discrepancyNum === 0 ? '₹ 0.00' : formatINR(discrepancyNum)}
            </span>
          </div>

          {reconciliation.unparsed_lines_count > 0 && (
            <>
              <div className="hidden sm:block w-px h-8 bg-black/40" />
              <div>
                <span className="block text-[10px] uppercase font-bold text-bauhaus-red">
                  Unparsed Lines
                </span>
                <span className="font-bold text-bauhaus-red">
                  {reconciliation.unparsed_lines_count} Rows
                </span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
