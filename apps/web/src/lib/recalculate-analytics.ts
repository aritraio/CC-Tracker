import {
  CategorizedTransaction,
  Category,
  CategoryBreakdown,
  MerchantConcentration,
  MicroSpendMetrics,
  RecurringAnalysis,
  SpendMetrics,
  StatementAnalytics,
  TemporalMetrics,
  TransactionType,
} from '@/types';

const CREDIT_TYPES: Set<TransactionType> = new Set<TransactionType>([
  'REFUND',
  'REVERSAL',
  'PAYMENT',
  'REWARD',
  'ADJUSTMENT',
]);

/**
 * Recomputes all deterministic spend metrics, category breakdowns,
 * and merchant concentrations in real-time when transactions are reclassified.
 */
export function recalculateAnalytics(
  transactions: CategorizedTransaction[],
  originalAnalytics?: StatementAnalytics
): StatementAnalytics {
  let totalDebits = 0;
  let totalCredits = 0;
  let debitCount = 0;
  let creditCount = 0;
  const debitAmounts: number[] = [];

  const categoryMap = new Map<
    Category,
    { total: number; count: number; merchants: Map<string, number> }
  >();

  const merchantMap = new Map<
    string,
    { category: Category; total: number; count: number }
  >();

  const microMerchants = new Set<string>();
  let microCount = 0;
  let microTotal = 0;

  for (const txn of transactions) {
    const amount = parseFloat(txn.amount) || 0;
    const isCredit = CREDIT_TYPES.has(txn.transaction_type);

    if (isCredit) {
      totalCredits += amount;
      creditCount += 1;
    } else {
      totalDebits += amount;
      debitCount += 1;
      debitAmounts.push(amount);

      // Micro-spend calculation (< ₹250)
      if (amount < 250) {
        microCount += 1;
        microTotal += amount;
        microMerchants.add(txn.merchant_normalized || txn.merchant_raw);
      }

      // Category breakdown (Debits only)
      const cat = txn.category;
      if (!categoryMap.has(cat)) {
        categoryMap.set(cat, { total: 0, count: 0, merchants: new Map() });
      }
      const catData = categoryMap.get(cat)!;
      catData.total += amount;
      catData.count += 1;
      const mName = txn.merchant_normalized || txn.merchant_raw;
      catData.merchants.set(mName, (catData.merchants.get(mName) || 0) + amount);

      // Merchant concentration
      if (!merchantMap.has(mName)) {
        merchantMap.set(mName, { category: cat, total: 0, count: 0 });
      }
      const mData = merchantMap.get(mName)!;
      mData.total += amount;
      mData.count += 1;
    }
  }

  // Median & Average
  debitAmounts.sort((a, b) => a - b);
  const avgAmount = debitCount > 0 ? totalDebits / debitCount : 0;
  let medianAmount = 0;
  if (debitAmounts.length > 0) {
    const mid = Math.floor(debitAmounts.length / 2);
    medianAmount =
      debitAmounts.length % 2 !== 0
        ? debitAmounts[mid]
        : (debitAmounts[mid - 1] + debitAmounts[mid]) / 2;
  }
  const maxAmount = debitAmounts.length > 0 ? debitAmounts[debitAmounts.length - 1] : 0;
  const minAmount = debitAmounts.length > 0 ? debitAmounts[0] : 0;
  const netSpend = totalDebits - totalCredits;

  const spend_metrics: SpendMetrics = {
    total_debits: totalDebits.toFixed(2),
    total_credits: totalCredits.toFixed(2),
    net_spend: netSpend.toFixed(2),
    total_transaction_count: transactions.length,
    debit_transaction_count: debitCount,
    credit_transaction_count: creditCount,
    average_transaction_amount: avgAmount.toFixed(2),
    median_transaction_amount: medianAmount.toFixed(2),
    max_transaction_amount: maxAmount.toFixed(2),
    min_transaction_amount: minAmount.toFixed(2),
  };

  // Category breakdown list sorted by total desc
  const category_breakdown: CategoryBreakdown[] = Array.from(categoryMap.entries())
    .map(([cat, data]) => {
      const percentage = totalDebits > 0 ? (data.total / totalDebits) * 100 : 0;
      const sortedMerchants = Array.from(data.merchants.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map((m) => m[0]);

      return {
        category: cat,
        total_amount: data.total.toFixed(2),
        percentage: parseFloat(percentage.toFixed(2)),
        transaction_count: data.count,
        average_amount: data.count > 0 ? (data.total / data.count).toFixed(2) : '0.00',
        top_merchants: sortedMerchants,
      };
    })
    .sort((a, b) => parseFloat(b.total_amount) - parseFloat(a.total_amount));

  // Merchant concentration sorted by total desc
  const merchant_concentration: MerchantConcentration[] = Array.from(merchantMap.entries())
    .map(([mName, data]) => {
      const percentage = totalDebits > 0 ? (data.total / totalDebits) * 100 : 0;
      return {
        merchant_name: mName,
        category: data.category,
        total_amount: data.total.toFixed(2),
        percentage: parseFloat(percentage.toFixed(2)),
        transaction_count: data.count,
      };
    })
    .sort((a, b) => parseFloat(b.total_amount) - parseFloat(a.total_amount));

  const micro_spend_metrics: MicroSpendMetrics = {
    threshold: '250.00',
    count: microCount,
    total_amount: microTotal.toFixed(2),
    percentage_of_transactions:
      transactions.length > 0
        ? parseFloat(((microCount / transactions.length) * 100).toFixed(2))
        : 0,
    percentage_of_spend:
      totalDebits > 0
        ? parseFloat(((microTotal / totalDebits) * 100).toFixed(2))
        : 0,
    top_micro_merchants: Array.from(microMerchants).slice(0, 5),
  };

  // Recurring subscriptions
  const recurringItems = transactions
    .filter((t) => t.is_recurring)
    .map((t) => {
      const amt = parseFloat(t.amount) || 0;
      return {
        merchant_name: t.merchant_normalized || t.merchant_raw,
        category: t.category,
        amount: t.amount,
        frequency: 'Monthly',
        occurrences: 1,
        annualized_cost: (amt * 12).toFixed(2),
        transaction_dates: [t.transaction_date],
      };
    });

  const totalMonthlyRecurring = recurringItems.reduce(
    (acc, cur) => acc + (parseFloat(cur.amount) || 0),
    0
  );

  const recurring_analysis: RecurringAnalysis = {
    items: recurringItems,
    total_monthly_recurring: totalMonthlyRecurring.toFixed(2),
    total_annual_recurring: (totalMonthlyRecurring * 12).toFixed(2),
    recurring_percentage_of_spend:
      totalDebits > 0
        ? parseFloat(((totalMonthlyRecurring / totalDebits) * 100).toFixed(2))
        : 0,
  };

  return {
    spend_metrics,
    category_breakdown,
    merchant_concentration,
    temporal_metrics: originalAnalytics?.temporal_metrics || {
      daily_spending: [],
      weekday_spend: '0.00',
      weekend_spend: '0.00',
      weekday_percentage: 0,
      weekend_percentage: 0,
      avg_daily_burn_rate: '0.00',
      day_of_week_breakdown: {},
    },
    micro_spend_metrics,
    recurring_analysis,
  };
}
