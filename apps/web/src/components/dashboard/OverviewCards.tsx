'use client';

import React from 'react';
import { OverviewCard } from './OverviewCard';
import { StatementAnalytics, StatementHeader } from '@/types';
import { formatINR, formatPercent } from '@/lib/formatters';
import {
  CreditCard,
  TrendingDown,
  Layers,
  ArrowUpRight,
  PieChart,
  Percent,
  Receipt,
  Scale,
} from 'lucide-react';

export interface OverviewCardsProps {
  analytics: StatementAnalytics;
  header: StatementHeader;
}

export const OverviewCards: React.FC<OverviewCardsProps> = ({
  analytics,
  header,
}) => {
  const { spend_metrics, category_breakdown } = analytics;
  const topCategory = category_breakdown[0];

  // Credit Limit Utilization Calculation
  const totalDebitsNum = parseFloat(spend_metrics.total_debits || '0.00');
  const creditLimitNum = header.credit_limit
    ? parseFloat(header.credit_limit)
    : null;

  const utilizationPercent =
    creditLimitNum && creditLimitNum > 0
      ? (totalDebitsNum / creditLimitNum) * 100
      : null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      {/* 1. Total Spend (Debits) */}
      <OverviewCard
        title="Total Cycle Spend"
        value={formatINR(spend_metrics.total_debits)}
        subtitle={`${spend_metrics.total_transaction_count} total transactions`}
        badgeText={`${spend_metrics.debit_transaction_count} Debits`}
        badgeVariant="red"
        shape="circle"
        icon={Receipt}
      />

      {/* 2. Net Billed Spend */}
      <OverviewCard
        title="Net Statement Spend"
        value={formatINR(spend_metrics.net_spend)}
        subtitle={
          parseFloat(spend_metrics.total_credits) > 0
            ? `Includes ${formatINR(spend_metrics.total_credits)} credits`
            : 'Zero refunds/credits billed'
        }
        badgeText={
          parseFloat(spend_metrics.total_credits) > 0
            ? `${spend_metrics.credit_transaction_count} Credits`
            : 'Clean Debits'
        }
        badgeVariant="blue"
        shape="square"
        icon={Scale}
      />

      {/* 3. Average & Peak Transaction */}
      <OverviewCard
        title="Average Transaction"
        value={formatINR(spend_metrics.average_transaction_amount)}
        subtitle={`Max: ${formatINR(spend_metrics.max_transaction_amount)}`}
        badgeText={`Median: ${formatINR(spend_metrics.median_transaction_amount, { showDecimals: false })}`}
        badgeVariant="yellow"
        shape="triangle"
        icon={ArrowUpRight}
      />

      {/* 4. Top Category or Utilization */}
      {topCategory ? (
        <OverviewCard
          title="Top Category"
          value={topCategory.category}
          subtitle={`${formatINR(topCategory.total_amount)} spent`}
          badgeText={`${topCategory.percentage.toFixed(1)}% Share`}
          badgeVariant={topCategory.percentage > 40 ? 'red' : 'yellow'}
          shape="circle"
          icon={PieChart}
        />
      ) : utilizationPercent !== null ? (
        <OverviewCard
          title="Credit Utilization"
          value={formatPercent(utilizationPercent)}
          subtitle={`Limit: ${formatINR(creditLimitNum, { compact: true })}`}
          badgeText={utilizationPercent > 30 ? 'HIGH USAGE' : 'HEALTHY'}
          badgeVariant={utilizationPercent > 30 ? 'red' : 'green'}
          shape="circle"
          icon={Percent}
        />
      ) : (
        <OverviewCard
          title="Card Account"
          value={header.issuer}
          subtitle={`Card: •••• ${header.card_last_4 || 'XXXX'}`}
          badgeText="ACTIVE"
          badgeVariant="black"
          shape="circle"
          icon={CreditCard}
        />
      )}
    </div>
  );
};
