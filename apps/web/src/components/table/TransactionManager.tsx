'use client';

import React, { useState, useMemo } from 'react';
import { CategorizedTransaction, Category, TransactionType, StatementAnalytics } from '@/types';
import { FilterBar, QuickPreset, SortField, SortDirection } from './FilterBar';
import { TransactionTable } from './TransactionTable';
import { recalculateAnalytics } from '@/lib/recalculate-analytics';
import { formatINR } from '@/lib/formatters';
import { CreditCard, Layers, Receipt, ShieldCheck, Undo2 } from 'lucide-react';

export interface TransactionManagerProps {
  initialTransactions: CategorizedTransaction[];
  originalAnalytics?: StatementAnalytics;
  statementIssuer?: string;
  initialCategory?: Category | 'ALL';
  initialMerchants?: string[];
  onTransactionsChange?: (
    updatedTransactions: CategorizedTransaction[],
    updatedAnalytics: StatementAnalytics
  ) => void;
}

const CREDIT_TYPES: Set<TransactionType> = new Set<TransactionType>([
  'REFUND',
  'REVERSAL',
  'PAYMENT',
  'REWARD',
  'ADJUSTMENT',
]);

export const TransactionManager: React.FC<TransactionManagerProps> = ({
  initialTransactions,
  originalAnalytics,
  statementIssuer = 'Statement',
  initialCategory = 'ALL',
  initialMerchants,
  onTransactionsChange,
}) => {
  const [transactions, setTransactions] = useState<CategorizedTransaction[]>(initialTransactions);
  const [searchQuery, setSearchQuery] = useState<string>(
    initialMerchants && initialMerchants.length > 0 ? initialMerchants[0] : ''
  );
  const [selectedCategory, setSelectedCategory] = useState<Category | 'ALL'>(initialCategory);
  const [selectedType, setSelectedType] = useState<TransactionType | 'ALL'>('ALL');
  const [quickPreset, setQuickPreset] = useState<QuickPreset>('ALL');
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [isModified, setIsModified] = useState<boolean>(false);

  // Handle inline category reclassification
  const handleUpdateCategory = (index: number, newCategory: Category) => {
    const updated = [...transactions];
    updated[index] = {
      ...updated[index],
      category: newCategory,
    };
    setTransactions(updated);
    setIsModified(true);

    // Dynamic analytics recalculation
    const updatedAnalytics = recalculateAnalytics(updated, originalAnalytics);
    onTransactionsChange?.(updated, updatedAnalytics);
  };

  // Handle toggling recurring flag
  const handleToggleRecurring = (index: number, isRecurring: boolean) => {
    const updated = [...transactions];
    updated[index] = {
      ...updated[index],
      is_recurring: isRecurring,
    };
    setTransactions(updated);
    setIsModified(true);

    const updatedAnalytics = recalculateAnalytics(updated, originalAnalytics);
    onTransactionsChange?.(updated, updatedAnalytics);
  };

  // Reset to original classifications
  const handleRevertAll = () => {
    setTransactions(initialTransactions);
    setIsModified(false);
    if (originalAnalytics) {
      onTransactionsChange?.(initialTransactions, originalAnalytics);
    }
  };

  // Handle column header sorting
  const handleSortHeader = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Filter & Sort Pipeline
  const filteredAndSortedTransactions = useMemo(() => {
    return transactions
      .filter((txn) => {
        const amountNum = parseFloat(txn.amount) || 0;
        const isCredit = CREDIT_TYPES.has(txn.transaction_type);

        // 1. Text Search Filter
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase().trim();
          const matchesRaw = txn.merchant_raw.toLowerCase().includes(q);
          const matchesNorm = (txn.merchant_normalized || '').toLowerCase().includes(q);
          const matchesCat = txn.category.toLowerCase().includes(q);
          if (!matchesRaw && !matchesNorm && !matchesCat) return false;
        }

        // 2. Category Filter
        if (selectedCategory !== 'ALL' && txn.category !== selectedCategory) {
          return false;
        }

        // 3. Transaction Type Filter
        if (selectedType !== 'ALL' && txn.transaction_type !== selectedType) {
          return false;
        }

        // 4. Quick Presets Filter
        if (quickPreset === 'MICRO_SPEND') {
          if (amountNum >= 250 || isCredit) return false;
        } else if (quickPreset === 'HIGH_TICKET') {
          if (amountNum < 5000 || isCredit) return false;
        } else if (quickPreset === 'SUBSCRIPTIONS') {
          if (!txn.is_recurring) return false;
        } else if (quickPreset === 'CREDITS_ONLY') {
          if (!isCredit) return false;
        }

        return true;
      })
      .sort((a, b) => {
        const amountA = parseFloat(a.amount) || 0;
        const amountB = parseFloat(b.amount) || 0;

        if (sortField === 'date') {
          const dateA = new Date(a.transaction_date).getTime() || 0;
          const dateB = new Date(b.transaction_date).getTime() || 0;
          return sortDirection === 'asc' ? dateA - dateB : dateB - dateA;
        }

        if (sortField === 'amount') {
          return sortDirection === 'asc' ? amountA - amountB : amountB - amountA;
        }

        if (sortField === 'merchant') {
          const nameA = (a.merchant_normalized || a.merchant_raw).toLowerCase();
          const nameB = (b.merchant_normalized || b.merchant_raw).toLowerCase();
          return sortDirection === 'asc'
            ? nameA.localeCompare(nameB)
            : nameB.localeCompare(nameA);
        }

        return 0;
      });
  }, [
    transactions,
    searchQuery,
    selectedCategory,
    selectedType,
    quickPreset,
    sortField,
    sortDirection,
  ]);

  // Active filter count
  const activeFilterCount =
    (searchQuery ? 1 : 0) +
    (selectedCategory !== 'ALL' ? 1 : 0) +
    (selectedType !== 'ALL' ? 1 : 0) +
    (quickPreset !== 'ALL' ? 1 : 0);

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('ALL');
    setSelectedType('ALL');
    setQuickPreset('ALL');
    setSortField('date');
    setSortDirection('desc');
  };

  // Filtered spend summary
  const filteredDebitsTotal = filteredAndSortedTransactions
    .filter((t) => !CREDIT_TYPES.has(t.transaction_type))
    .reduce((acc, t) => acc + (parseFloat(t.amount) || 0), 0);

  return (
    <div className="space-y-4">
      {/* Modification / Revert Notice Bar */}
      {isModified && (
        <div className="bg-bauhaus-yellow-light border-2 md:border-3 border-black p-3.5 flex items-center justify-between gap-3 font-mono text-xs shadow-bauhaus-xs">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-bauhaus-green" />
            <span className="font-bold text-ink">
              Custom category edits active. Dashboard analytics and charts recalculated dynamically.
            </span>
          </div>

          <button
            onClick={handleRevertAll}
            className="inline-flex items-center gap-1 px-2.5 py-1 bg-white hover:bg-muted text-ink border border-black font-bold uppercase shadow-bauhaus-xs"
          >
            <Undo2 className="w-3.5 h-3.5 text-bauhaus-red" />
            <span>Revert to Parsed</span>
          </button>
        </div>
      )}

      {/* Filter Controls Bar */}
      <FilterBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        quickPreset={quickPreset}
        onQuickPresetChange={setQuickPreset}
        sortField={sortField}
        sortDirection={sortDirection}
        onSortChange={(field, dir) => {
          setSortField(field);
          setSortDirection(dir);
        }}
        onResetFilters={resetFilters}
        activeFilterCount={activeFilterCount}
      />

      {/* Filtered Volume Summary Badge */}
      <div className="flex items-center justify-between px-1 text-xs font-mono">
        <span className="font-bold text-ink/75">
          Filtered Volume: {filteredAndSortedTransactions.length} of {transactions.length} items
        </span>
        <span className="font-black text-ink">
          Filtered Debits: {formatINR(filteredDebitsTotal)}
        </span>
      </div>

      {/* Main Table */}
      <TransactionTable
        transactions={filteredAndSortedTransactions}
        onUpdateCategory={handleUpdateCategory}
        onToggleRecurring={handleToggleRecurring}
        sortField={sortField}
        sortDirection={sortDirection}
        onSortHeader={handleSortHeader}
        statementIssuer={statementIssuer}
      />
    </div>
  );
};
