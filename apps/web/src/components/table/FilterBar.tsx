'use client';

import React from 'react';
import { Category, TransactionType } from '@/types';
import { ALL_CATEGORIES } from './CategorySelectPopover';
import {
  Search,
  X,
  Filter,
  ArrowUpDown,
  Tag,
  CreditCard,
  Zap,
  Repeat,
  RotateCcw,
} from 'lucide-react';

export type SortField = 'date' | 'amount' | 'merchant';
export type SortDirection = 'asc' | 'desc';

export type QuickPreset =
  | 'ALL'
  | 'MICRO_SPEND'
  | 'HIGH_TICKET'
  | 'SUBSCRIPTIONS'
  | 'CREDITS_ONLY';

export interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (val: string) => void;
  selectedCategory: Category | 'ALL';
  onCategoryChange: (cat: Category | 'ALL') => void;
  selectedType: TransactionType | 'ALL';
  onTypeChange: (type: TransactionType | 'ALL') => void;
  quickPreset: QuickPreset;
  onQuickPresetChange: (preset: QuickPreset) => void;
  sortField: SortField;
  sortDirection: SortDirection;
  onSortChange: (field: SortField, dir: SortDirection) => void;
  onResetFilters: () => void;
  activeFilterCount: number;
}

const TRANSACTION_TYPES: TransactionType[] = [
  'PURCHASE',
  'PAYMENT',
  'REFUND',
  'REVERSAL',
  'FEE',
  'INTEREST',
  'GST',
  'EMI',
  'CASH_WITHDRAWAL',
  'REWARD',
  'ADJUSTMENT',
];

export const FilterBar: React.FC<FilterBarProps> = ({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  selectedType,
  onTypeChange,
  quickPreset,
  onQuickPresetChange,
  sortField,
  sortDirection,
  onSortChange,
  onResetFilters,
  activeFilterCount,
}) => {
  return (
    <div className="bg-canvas border-2 md:border-4 border-black p-4 sm:p-5 shadow-bauhaus-sm space-y-4">
      {/* 1. Main Search & Dropdown Controls Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3">
        {/* Search Input (5 Cols) */}
        <div className="lg:col-span-5 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-ink/60">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search merchant, description, or city..."
            className="w-full pl-9 pr-8 py-2.5 bg-white border-2 border-black font-mono text-xs sm:text-sm font-bold text-ink placeholder:text-ink/40 focus:outline-none focus:ring-2 focus:ring-bauhaus-yellow shadow-bauhaus-xs"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute inset-y-0 right-0 pr-2.5 flex items-center text-ink/60 hover:text-ink"
              title="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Dropdown (3 Cols) */}
        <div className="lg:col-span-3">
          <select
            value={selectedCategory}
            onChange={(e) => onCategoryChange(e.target.value as Category | 'ALL')}
            className="w-full px-3 py-2.5 bg-white border-2 border-black font-mono text-xs sm:text-sm font-bold text-ink focus:outline-none focus:ring-2 focus:ring-bauhaus-yellow shadow-bauhaus-xs cursor-pointer"
          >
            <option value="ALL">ALL CATEGORIES</option>
            {ALL_CATEGORIES.map((c) => (
              <option key={c.name} value={c.name}>
                {c.name.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Transaction Type Dropdown (2 Cols) */}
        <div className="lg:col-span-2">
          <select
            value={selectedType}
            onChange={(e) =>
              onTypeChange(e.target.value as TransactionType | 'ALL')
            }
            className="w-full px-3 py-2.5 bg-white border-2 border-black font-mono text-xs sm:text-sm font-bold text-ink focus:outline-none focus:ring-2 focus:ring-bauhaus-yellow shadow-bauhaus-xs cursor-pointer"
          >
            <option value="ALL">ALL TYPES</option>
            {TRANSACTION_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {/* Sort Selector (2 Cols) */}
        <div className="lg:col-span-2">
          <select
            value={`${sortField}-${sortDirection}`}
            onChange={(e) => {
              const [field, dir] = e.target.value.split('-') as [
                SortField,
                SortDirection
              ];
              onSortChange(field, dir);
            }}
            className="w-full px-3 py-2.5 bg-white border-2 border-black font-mono text-xs sm:text-sm font-bold text-ink focus:outline-none focus:ring-2 focus:ring-bauhaus-yellow shadow-bauhaus-xs cursor-pointer"
          >
            <option value="date-desc">DATE (NEWEST)</option>
            <option value="date-asc">DATE (OLDEST)</option>
            <option value="amount-desc">AMOUNT (HIGH-LOW)</option>
            <option value="amount-asc">AMOUNT (LOW-HIGH)</option>
            <option value="merchant-asc">MERCHANT (A-Z)</option>
          </select>
        </div>
      </div>

      {/* 2. Quick Presets & Reset Filter Strip */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-black/20 text-xs font-mono">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="font-bold uppercase text-ink/70 mr-1 flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 text-bauhaus-yellow" />
            <span>Presets:</span>
          </span>

          <button
            onClick={() => onQuickPresetChange('ALL')}
            className={`px-2.5 py-1 border border-black font-bold uppercase transition-all ${
              quickPreset === 'ALL'
                ? 'bg-bauhaus-yellow text-ink shadow-bauhaus-xs'
                : 'bg-white text-ink/80 hover:text-ink'
            }`}
          >
            All
          </button>

          <button
            onClick={() => onQuickPresetChange('MICRO_SPEND')}
            className={`px-2.5 py-1 border border-black font-bold uppercase transition-all ${
              quickPreset === 'MICRO_SPEND'
                ? 'bg-bauhaus-yellow text-ink shadow-bauhaus-xs'
                : 'bg-white text-ink/80 hover:text-ink'
            }`}
          >
            Micro (&lt; ₹250)
          </button>

          <button
            onClick={() => onQuickPresetChange('HIGH_TICKET')}
            className={`px-2.5 py-1 border border-black font-bold uppercase transition-all ${
              quickPreset === 'HIGH_TICKET'
                ? 'bg-bauhaus-red text-white shadow-bauhaus-xs'
                : 'bg-white text-ink/80 hover:text-ink'
            }`}
          >
            High Ticket (&gt; ₹5k)
          </button>

          <button
            onClick={() => onQuickPresetChange('SUBSCRIPTIONS')}
            className={`px-2.5 py-1 border border-black font-bold uppercase transition-all ${
              quickPreset === 'SUBSCRIPTIONS'
                ? 'bg-bauhaus-blue text-white shadow-bauhaus-xs'
                : 'bg-white text-ink/80 hover:text-ink'
            }`}
          >
            Subscriptions
          </button>

          <button
            onClick={() => onQuickPresetChange('CREDITS_ONLY')}
            className={`px-2.5 py-1 border border-black font-bold uppercase transition-all ${
              quickPreset === 'CREDITS_ONLY'
                ? 'bg-bauhaus-green text-white shadow-bauhaus-xs'
                : 'bg-white text-ink/80 hover:text-ink'
            }`}
          >
            Credits / Refunds
          </button>
        </div>

        {/* Clear All Filters Button */}
        {activeFilterCount > 0 && (
          <button
            onClick={onResetFilters}
            className="inline-flex items-center gap-1.5 px-3 py-1 bg-white hover:bg-muted text-bauhaus-red border border-black font-bold uppercase shadow-bauhaus-xs self-start sm:self-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset ({activeFilterCount} Active)</span>
          </button>
        )}
      </div>
    </div>
  );
};
