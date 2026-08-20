'use client';

import React, { useState } from 'react';
import { CategorizedTransaction, Category } from '@/types';
import { TransactionRow } from './TransactionRow';
import { SortField, SortDirection } from './FilterBar';
import { Button } from '@/components/ui/button';
import {
  Download,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  FileSpreadsheet,
  Layers,
} from 'lucide-react';

export interface TransactionTableProps {
  transactions: CategorizedTransaction[];
  onUpdateCategory: (index: number, newCategory: Category) => void;
  onToggleRecurring: (index: number, isRecurring: boolean) => void;
  sortField: SortField;
  sortDirection: SortDirection;
  onSortHeader: (field: SortField) => void;
  statementIssuer?: string;
}

export const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  onUpdateCategory,
  onToggleRecurring,
  sortField,
  sortDirection,
  onSortHeader,
  statementIssuer = 'Statement',
}) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);

  const totalPages = Math.ceil(transactions.length / pageSize) || 1;
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedTransactions = transactions.slice(startIndex, startIndex + pageSize);

  // CSV Exporter
  const handleExportCSV = () => {
    const headers = [
      'Transaction Date',
      'Post Date',
      'Merchant',
      'Raw Description',
      'Type',
      'Category',
      'Subcategory',
      'Amount (INR)',
      'Is Recurring',
      'Tier',
      'Confidence Score',
    ];

    const rows = transactions.map((t) => [
      `"${t.transaction_date}"`,
      `"${t.post_date || ''}"`,
      `"${(t.merchant_normalized || t.merchant_raw).replace(/"/g, '""')}"`,
      `"${t.merchant_raw.replace(/"/g, '""')}"`,
      `"${t.transaction_type}"`,
      `"${t.category}"`,
      `"${t.subcategory || ''}"`,
      `"${t.amount}"`,
      `"${t.is_recurring ? 'YES' : 'NO'}"`,
      `"${t.tier}"`,
      `"${t.confidence_score}"`,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute(
      'download',
      `${statementIssuer.replace(/\s+/g, '_')}_transactions.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderSortArrow = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3.5 h-3.5 opacity-40 ml-1 inline" />;
    }
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-3.5 h-3.5 text-bauhaus-yellow ml-1 inline" />
    ) : (
      <ArrowDown className="w-3.5 h-3.5 text-bauhaus-yellow ml-1 inline" />
    );
  };

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg flex flex-col">
      {/* Top Table Actions Bar */}
      <div className="p-4 bg-canvas border-b-2 md:border-b-4 border-black flex flex-col sm:flex-row sm:items-center justify-between gap-3 font-mono text-xs">
        <div className="flex items-center gap-2">
          <FileSpreadsheet className="w-4 h-4 text-ink" />
          <span className="font-bold text-ink uppercase">
            Showing {startIndex + 1}–{Math.min(startIndex + pageSize, transactions.length)} of{' '}
            {transactions.length} Transactions
          </span>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {/* Page size dropdown */}
          <div className="flex items-center gap-1.5">
            <span className="text-ink/70">Rows:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="bg-white border border-black px-2 py-1 font-bold text-ink cursor-pointer focus:outline-none"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          {/* CSV Export Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCSV}
            className="gap-1.5 text-xs py-1 px-3 bg-white"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </Button>
        </div>
      </div>

      {/* Responsive Table Scroll Viewport */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-[#121212] text-white font-bold text-xs uppercase tracking-wider divide-x divide-white/20 select-none">
            <tr>
              <th
                onClick={() => onSortHeader('date')}
                className="py-3 px-4 cursor-pointer hover:bg-black/80 transition-colors whitespace-nowrap"
              >
                <span>Date</span>
                {renderSortArrow('date')}
              </th>

              <th
                onClick={() => onSortHeader('merchant')}
                className="py-3 px-4 cursor-pointer hover:bg-black/80 transition-colors min-w-[200px]"
              >
                <span>Merchant / Raw Description</span>
                {renderSortArrow('merchant')}
              </th>

              <th className="py-3 px-4 whitespace-nowrap">Type</th>

              <th className="py-3 px-4 whitespace-nowrap">Category (Edit)</th>

              <th
                onClick={() => onSortHeader('amount')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-black/80 transition-colors whitespace-nowrap"
              >
                <span>Amount (INR)</span>
                {renderSortArrow('amount')}
              </th>

              <th className="py-3 px-4 text-center whitespace-nowrap">Provenance</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-black/10 bg-white">
            {paginatedTransactions.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-ink font-mono">
                  <div className="text-sm font-bold uppercase mb-1">
                    No transactions match your current search and filters.
                  </div>
                  <p className="text-xs text-ink/60">
                    Try adjusting your search term, preset chips, or category filters.
                  </p>
                </td>
              </tr>
            ) : (
              paginatedTransactions.map((txn, index) => {
                const globalIndex = startIndex + index;
                return (
                  <TransactionRow
                    key={`${txn.transaction_date}-${txn.merchant_raw}-${txn.amount}-${globalIndex}`}
                    transaction={txn}
                    index={globalIndex}
                    onUpdateCategory={onUpdateCategory}
                    onToggleRecurring={onToggleRecurring}
                  />
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="p-4 bg-canvas border-t-2 md:border-t-4 border-black flex flex-col sm:flex-row sm:items-center justify-between gap-3 font-mono text-xs">
          <span className="text-ink/75">
            Page <span className="font-bold text-ink">{currentPage}</span> of{' '}
            <span className="font-bold text-ink">{totalPages}</span>
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-black font-bold uppercase disabled:opacity-40 disabled:cursor-not-allowed hover:bg-muted shadow-bauhaus-xs"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>

            {/* Page number buttons */}
            <div className="hidden sm:flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(
                  (p) =>
                    p === 1 ||
                    p === totalPages ||
                    Math.abs(p - currentPage) <= 1
                )
                .map((p, idx, arr) => {
                  const showEllipsis = idx > 0 && p - arr[idx - 1] > 1;
                  return (
                    <React.Fragment key={p}>
                      {showEllipsis && <span className="px-1 text-ink/50">...</span>}
                      <button
                        onClick={() => setCurrentPage(p)}
                        className={`w-8 h-8 flex items-center justify-center border border-black font-bold transition-all ${
                          currentPage === p
                            ? 'bg-bauhaus-yellow text-ink font-black shadow-bauhaus-xs'
                            : 'bg-white hover:bg-muted text-ink'
                        }`}
                      >
                        {p}
                      </button>
                    </React.Fragment>
                  );
                })}
            </div>

            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-black font-bold uppercase disabled:opacity-40 disabled:cursor-not-allowed hover:bg-muted shadow-bauhaus-xs"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
