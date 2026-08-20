'use client';

import React, { useState, useEffect } from 'react';
import { ParseStatementResponse, CategorizedTransaction, Category, StatementAnalytics } from '@/types';
import { ReconciliationBadge } from './ReconciliationBadge';
import { OverviewCards } from './OverviewCards';
import { CategoryDonutChart } from './CategoryDonutChart';
import { SpendingTimelineChart } from './SpendingTimelineChart';
import { TopMerchantsBarChart } from './TopMerchantsBarChart';
import { RecurringChargesCard } from './RecurringChargesCard';
import { MicroSpendCard } from './MicroSpendCard';
import { KeyFindingsList } from './KeyFindingsList';
import { MoMComparisonCard } from './MoMComparisonCard';
import { RecommendationsList } from '../insights/RecommendationsList';
import { ExecutiveCoachingCard } from '../insights/ExecutiveCoachingCard';
import { TransactionManager } from '../table/TransactionManager';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { formatDate, formatINR } from '@/lib/formatters';
import { saveStatementSnapshot } from '@/lib/feedback-tracker';
import {
  CreditCard,
  Calendar,
  RotateCcw,
  Printer,
  Sparkles,
  BarChart3,
  Zap,
  Target,
  FileSpreadsheet,
  Layers,
  History,
} from 'lucide-react';

export interface InsightsDashboardProps {
  data: ParseStatementResponse;
  onReset?: () => void;
  onShowTransactions?: (category?: string, merchants?: string[]) => void;
}

export const InsightsDashboard: React.FC<InsightsDashboardProps> = ({
  data,
  onReset,
}) => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [currentTransactions, setCurrentTransactions] = useState<CategorizedTransaction[]>(
    data.transactions
  );
  const [currentAnalytics, setCurrentAnalytics] = useState<StatementAnalytics>(
    data.analytics
  );

  // Deep-linking filter targets
  const [filterCategory, setFilterCategory] = useState<Category | 'ALL'>('ALL');
  const [filterMerchants, setFilterMerchants] = useState<string[] | undefined>(undefined);

  // Save statement snapshot on initial load for historical comparison
  useEffect(() => {
    saveStatementSnapshot(data);
  }, [data]);

  const {
    header,
    reconciliation,
    anomalies,
    recommendations,
    explanation,
  } = data;

  const handlePrint = () => {
    window.print();
  };

  const handleInspectTransactions = (category?: string, merchants?: string[]) => {
    if (category) {
      setFilterCategory(category as Category);
    } else {
      setFilterCategory('ALL');
    }
    setFilterMerchants(merchants);
    setActiveTab('transactions');

    setTimeout(() => {
      const tabEl = document.getElementById('transaction-manager-section');
      tabEl?.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  const handleTransactionsUpdated = (
    updatedTxns: CategorizedTransaction[],
    updatedAnalytics: StatementAnalytics
  ) => {
    setCurrentTransactions(updatedTxns);
    setCurrentAnalytics(updatedAnalytics);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 1. STATEMENT HEADER BANNER */}
      <div className="bg-paper border-2 md:border-4 border-black p-5 sm:p-6 shadow-bauhaus-md md:shadow-bauhaus-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b-2 border-black">
          {/* Card & Period Identity */}
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 bg-bauhaus-blue text-white border-2 border-black flex items-center justify-center shadow-bauhaus-xs shrink-0">
              <CreditCard className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-widest text-ink/70">
                  Verified Statement Account
                </span>
                <span className="px-1.5 py-0.2 bg-bauhaus-yellow text-ink border border-black font-mono text-[10px] font-bold">
                  •••• {header.card_last_4 || 'XXXX'}
                </span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-black uppercase tracking-tight text-ink">
                {header.issuer}
              </h2>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
              className="gap-1.5 text-xs bg-canvas"
            >
              <Printer className="w-4 h-4" />
              <span>Print Report</span>
            </Button>

            {onReset && (
              <Button
                variant="primary"
                size="sm"
                onClick={onReset}
                className="gap-1.5 text-xs"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Upload Another</span>
              </Button>
            )}
          </div>
        </div>

        {/* Statement Timeline & Limit Details */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 font-mono text-xs">
          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Statement Period
            </span>
            <span className="font-bold text-ink text-sm">
              {header.statement_period_start && header.statement_period_end
                ? `${formatDate(header.statement_period_start, 'short')} – ${formatDate(
                    header.statement_period_end,
                    'short'
                  )}`
                : 'Current Cycle'}
            </span>
          </div>

          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Payment Due Date
            </span>
            <span className="font-bold text-bauhaus-red text-sm">
              {formatDate(header.payment_due_date, 'medium') || 'N/A'}
            </span>
          </div>

          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Total Amount Due
            </span>
            <span className="font-bold text-ink text-sm">
              {formatINR(header.total_amount_due || currentAnalytics.spend_metrics.total_debits)}
            </span>
          </div>

          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Credit Limit
            </span>
            <span className="font-bold text-ink text-sm">
              {header.credit_limit ? formatINR(header.credit_limit) : 'Not Specified'}
            </span>
          </div>
        </div>
      </div>

      {/* 2. MATHEMATICAL RECONCILIATION STAMP BANNER */}
      <ReconciliationBadge
        reconciliation={reconciliation}
        issuer={header.issuer}
      />

      {/* 3. EXECUTIVE METRICS CARDS (Dynamic with State) */}
      <OverviewCards analytics={currentAnalytics} header={header} />

      {/* 4. TABBED DEEP-DIVE SECTIONS */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full space-y-6"
      >
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="overview" className="gap-2">
            <Sparkles className="w-4 h-4" />
            <span>Executive Coaching</span>
          </TabsTrigger>

          <TabsTrigger value="visuals" className="gap-2">
            <BarChart3 className="w-4 h-4" />
            <span>Visual Analytics</span>
          </TabsTrigger>

          <TabsTrigger value="anomalies" className="gap-2">
            <Zap className="w-4 h-4" />
            <span>Anomalies & Patterns ({anomalies.total_findings_count})</span>
          </TabsTrigger>

          <TabsTrigger value="recommendations" className="gap-2">
            <Target className="w-4 h-4" />
            <span>Recommendations ({recommendations.recommendations_count})</span>
          </TabsTrigger>

          <TabsTrigger value="mom" className="gap-2">
            <History className="w-4 h-4" />
            <span>Outcome Tracking (MoM)</span>
          </TabsTrigger>

          <TabsTrigger value="transactions" className="gap-2">
            <FileSpreadsheet className="w-4 h-4" />
            <span>Transactions ({currentTransactions.length})</span>
          </TabsTrigger>
        </TabsList>

        {/* TAB 1: EXECUTIVE OVERVIEW & COACHING */}
        <TabsContent value="overview" className="space-y-6">
          <ExecutiveCoachingCard explanation={explanation} />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6">
              <CategoryDonutChart
                data={currentAnalytics.category_breakdown}
                totalSpend={currentAnalytics.spend_metrics.total_debits}
              />
            </div>
            <div className="lg:col-span-6">
              <SpendingTimelineChart
                temporalMetrics={currentAnalytics.temporal_metrics}
              />
            </div>
          </div>

          <MoMComparisonCard
            currentStatement={data}
            onExploreCategory={(cat) => handleInspectTransactions(cat)}
          />

          <KeyFindingsList
            anomalies={anomalies}
            onFilterCategory={(cat) => handleInspectTransactions(cat)}
          />
        </TabsContent>

        {/* TAB 2: FINANCIAL VISUAL ANALYTICS */}
        <TabsContent value="visuals" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Category Donut (6 cols) */}
            <div className="lg:col-span-6">
              <CategoryDonutChart
                data={currentAnalytics.category_breakdown}
                totalSpend={currentAnalytics.spend_metrics.total_debits}
              />
            </div>

            {/* Daily Timeline (6 cols) */}
            <div className="lg:col-span-6">
              <SpendingTimelineChart
                temporalMetrics={currentAnalytics.temporal_metrics}
              />
            </div>

            {/* Top Merchants (12 cols) */}
            <div className="lg:col-span-12">
              <TopMerchantsBarChart
                merchants={currentAnalytics.merchant_concentration}
                totalSpend={currentAnalytics.spend_metrics.total_debits}
              />
            </div>
          </div>
        </TabsContent>

        {/* TAB 3: ANOMALIES & BEHAVIORAL PATTERNS */}
        <TabsContent value="anomalies" className="space-y-6">
          <KeyFindingsList
            anomalies={anomalies}
            onFilterCategory={(cat) => handleInspectTransactions(cat)}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <MicroSpendCard microSpend={currentAnalytics.micro_spend_metrics} />
            <RecurringChargesCard
              recurringAnalysis={currentAnalytics.recurring_analysis}
            />
          </div>
        </TabsContent>

        {/* TAB 4: RECOMMENDATIONS & SUBSCRIPTIONS */}
        <TabsContent value="recommendations" className="space-y-6">
          <RecommendationsList
            recommendationResult={recommendations}
            onShowTransactions={handleInspectTransactions}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <RecurringChargesCard
              recurringAnalysis={currentAnalytics.recurring_analysis}
            />
            <MicroSpendCard microSpend={currentAnalytics.micro_spend_metrics} />
          </div>
        </TabsContent>

        {/* TAB 5: MONTH-OVER-MONTH OUTCOME VERIFICATION (STAGE 3) */}
        <TabsContent value="mom" className="space-y-6">
          <MoMComparisonCard
            currentStatement={data}
            onExploreCategory={(cat) => handleInspectTransactions(cat)}
          />
        </TabsContent>

        {/* TAB 6: INTERACTIVE TRANSACTION MANAGER & FILTER CONTROLS */}
        <TabsContent value="transactions" id="transaction-manager-section" className="space-y-6">
          <TransactionManager
            initialTransactions={currentTransactions}
            originalAnalytics={data.analytics}
            statementIssuer={header.issuer}
            initialCategory={filterCategory}
            initialMerchants={filterMerchants}
            onTransactionsChange={handleTransactionsUpdated}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};
