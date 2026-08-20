'use client';

import React from 'react';
import { CategorizedTransaction, Category, TransactionType } from '@/types';
import { formatDate, formatINR } from '@/lib/formatters';
import { CategorySelectPopover } from './CategorySelectPopover';
import { Repeat, ShieldCheck, Cpu, BookOpen, AlertCircle } from 'lucide-react';

export interface TransactionRowProps {
  transaction: CategorizedTransaction;
  index: number;
  onUpdateCategory: (index: number, newCategory: Category) => void;
  onToggleRecurring: (index: number, isRecurring: boolean) => void;
}

const CREDIT_TYPES: Set<TransactionType> = new Set<TransactionType>([
  'REFUND',
  'REVERSAL',
  'PAYMENT',
  'REWARD',
  'ADJUSTMENT',
]);

export const TransactionRow: React.FC<TransactionRowProps> = ({
  transaction,
  index,
  onUpdateCategory,
  onToggleRecurring,
}) => {
  const isCredit = CREDIT_TYPES.has(transaction.transaction_type);
  const amountNum = parseFloat(transaction.amount) || 0;

  const getTypeBadge = (type: TransactionType) => {
    switch (type) {
      case 'PURCHASE':
        return 'bg-canvas text-ink border-black';
      case 'PAYMENT':
        return 'bg-bauhaus-blue text-white border-black';
      case 'REFUND':
      case 'REVERSAL':
        return 'bg-bauhaus-green text-white border-black';
      case 'FEE':
      case 'INTEREST':
      case 'GST':
        return 'bg-bauhaus-red text-white border-black';
      case 'EMI':
        return 'bg-bauhaus-yellow text-ink border-black';
      default:
        return 'bg-muted text-ink border-black';
    }
  };

  const getTierBadge = (tier: number) => {
    switch (tier) {
      case 1:
        return {
          label: 'T1: Dictionary',
          icon: <BookOpen className="w-3 h-3 text-bauhaus-green" />,
          title: 'Direct 100% dictionary match',
        };
      case 2:
        return {
          label: 'T2: Regex',
          icon: <ShieldCheck className="w-3 h-3 text-bauhaus-blue" />,
          title: 'Deterministic regex rule match',
        };
      case 3:
      default:
        return {
          label: 'T3: LLM',
          icon: <Cpu className="w-3 h-3 text-bauhaus-yellow" />,
          title: 'Structured LLM categorization fallback',
        };
    }
  };

  const tierInfo = getTierBadge(transaction.tier);

  return (
    <tr className="border-b-2 border-black hover:bg-bauhaus-yellow-light transition-colors duration-100 font-mono text-xs select-text">
      {/* 1. Date */}
      <td className="py-3.5 px-4 font-bold text-ink whitespace-nowrap">
        <div>{formatDate(transaction.transaction_date, 'medium')}</div>
        {transaction.post_date && transaction.post_date !== transaction.transaction_date && (
          <div className="text-[10px] text-ink/50 font-normal">
            Post: {formatDate(transaction.post_date, 'short')}
          </div>
        )}
      </td>

      {/* 2. Merchant & Raw Description */}
      <td className="py-3.5 px-4">
        <div className="flex items-center gap-2">
          <span className="font-bold text-ink text-sm sm:text-base font-sans">
            {transaction.merchant_normalized || transaction.merchant_raw}
          </span>
          {transaction.is_recurring && (
            <span
              className="inline-flex items-center gap-0.5 px-1.5 py-0.2 bg-bauhaus-blue text-white text-[9px] font-mono font-bold uppercase border border-black shadow-bauhaus-xs"
              title="Recurring monthly subscription"
            >
              <Repeat className="w-2.5 h-2.5" />
              <span>SUB</span>
            </span>
          )}
        </div>
        <div className="text-[11px] text-ink/65 truncate max-w-xs sm:max-w-md font-mono mt-0.5">
          {transaction.merchant_raw}
        </div>
      </td>

      {/* 3. Transaction Type */}
      <td className="py-3.5 px-4 whitespace-nowrap">
        <span
          className={`inline-block px-2 py-0.5 text-[10px] font-bold uppercase border shadow-bauhaus-xs ${getTypeBadge(
            transaction.transaction_type
          )}`}
        >
          {transaction.transaction_type}
        </span>
      </td>

      {/* 4. Category (Interactive Reclassification Popover) */}
      <td className="py-3.5 px-4 whitespace-nowrap">
        <CategorySelectPopover
          currentCategory={transaction.category}
          isRecurring={transaction.is_recurring}
          onSelectCategory={(newCat) => onUpdateCategory(index, newCat)}
          onToggleRecurring={(isRec) => onToggleRecurring(index, isRec)}
        />
      </td>

      {/* 5. Amount (INR) */}
      <td className="py-3.5 px-4 text-right whitespace-nowrap">
        <div
          className={`font-black text-sm sm:text-base ${
            isCredit ? 'text-bauhaus-green' : 'text-ink'
          }`}
        >
          {isCredit ? `- ${formatINR(amountNum)}` : formatINR(amountNum)}
        </div>
        {amountNum < 250 && !isCredit && (
          <div className="text-[9px] text-bauhaus-yellow font-bold bg-black px-1 py-0.2 inline-block border border-black mt-0.5">
            MICRO SPEND
          </div>
        )}
      </td>

      {/* 6. Classification Provenance / Tier */}
      <td className="py-3.5 px-4 text-center whitespace-nowrap">
        <div
          className="inline-flex items-center gap-1 px-2 py-0.5 bg-canvas border border-black text-[10px] font-bold text-ink shadow-bauhaus-xs"
          title={tierInfo.title}
        >
          {tierInfo.icon}
          <span>{tierInfo.label}</span>
        </div>
      </td>
    </tr>
  );
};
