export type TransactionType =
  | 'PURCHASE'
  | 'REFUND'
  | 'REVERSAL'
  | 'PAYMENT'
  | 'FEE'
  | 'INTEREST'
  | 'GST'
  | 'EMI'
  | 'CASH_WITHDRAWAL'
  | 'REWARD'
  | 'ADJUSTMENT'
  | 'UNKNOWN';

export type Category =
  | 'Food & Dining'
  | 'Shopping'
  | 'Groceries & Quick-Commerce'
  | 'Transport & Fuel'
  | 'Travel & Lodging'
  | 'Bills & Utilities'
  | 'Entertainment & OTT'
  | 'Subscriptions'
  | 'Healthcare & Fitness'
  | 'Education'
  | 'Rent & Housing'
  | 'Fees & Charges'
  | 'Cash Withdrawal'
  | 'Other / Uncategorized';

export type FindingSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type DetectorType =
  | 'CATEGORY_SPIKE'
  | 'SPENDING_ACCELERATION'
  | 'FREQUENT_SMALL_SPEND'
  | 'MERCHANT_CONCENTRATION'
  | 'UNUSUAL_PURCHASE'
  | 'SUBSCRIPTION_BURDEN'
  | 'WEEKEND_SPIKE'
  | 'LATE_NIGHT_SPURT'
  | 'FREQUENCY_INFLATION'
  | 'HIGH_CREDIT_UTILIZATION';

export type RecommendationType =
  | 'CATEGORY_REDUCTION'
  | 'MICRO_SPEND_CONSOLIDATION'
  | 'SUBSCRIPTION_AUDIT'
  | 'MERCHANT_OPTIMIZATION'
  | 'UTILIZATION_MANAGEMENT'
  | 'BURN_RATE_CONTROL'
  | 'WEEKEND_PACING'
  | 'IMPULSE_CONTROL'
  | 'PURCHASE_REVIEW'
  | 'FREQUENCY_MANAGEMENT'
  | 'POSITIVE_REINFORCEMENT';

export interface StatementHeader {
  issuer: string;
  card_last_4?: string | null;
  statement_period_start?: string | null;
  statement_period_end?: string | null;
  total_amount_due?: string | null;
  minimum_amount_due?: string | null;
  payment_due_date?: string | null;
  credit_limit?: string | null;
  available_credit?: string | null;
  opening_balance?: string | null;
  total_debits?: string | null;
  total_credits?: string | null;
}

export interface CategorizedTransaction {
  transaction_date: string;
  post_date?: string | null;
  merchant_raw: string;
  merchant_normalized: string;
  amount: string;
  transaction_type: TransactionType;
  category: Category;
  subcategory?: string | null;
  tier: number;
  is_recurring: boolean;
  currency: string;
  source_page: number;
  confidence_score: number;
}

export interface ValidationIssue {
  issue_type: string;
  severity: string;
  message: string;
  transaction_index?: number | null;
  details?: Record<string, unknown>;
}

export interface ValidationResult {
  is_valid: boolean;
  issues: ValidationIssue[];
  duplicate_count: number;
  flagged_count: number;
}

export interface ReconciliationSummary {
  status: 'VALIDATED' | 'REVIEW_REQUIRED';
  discrepancy: string;
  extracted_debits: string;
  extracted_credits: string;
  statement_total_debits?: string | null;
  statement_total_credits?: string | null;
  statement_total_amount_due?: string | null;
  expected_total_due?: string | null;
  is_balanced: boolean;
  unparsed_lines_count: number;
  warnings: string[];
}

export interface CategorizationStats {
  total_transactions: number;
  tier1_matches: number;
  tier2_matches: number;
  tier3_matches: number;
  cached_matches: number;
  hit_rate: number;
}

export interface SpendMetrics {
  total_debits: string;
  total_credits: string;
  net_spend: string;
  total_transaction_count: number;
  debit_transaction_count: number;
  credit_transaction_count: number;
  average_transaction_amount: string;
  median_transaction_amount: string;
  max_transaction_amount: string;
  min_transaction_amount: string;
}

export interface CategoryBreakdown {
  category: Category;
  total_amount: string;
  percentage: number;
  transaction_count: number;
  average_amount: string;
  top_merchants: string[];
}

export interface MerchantConcentration {
  merchant_name: string;
  category: Category;
  total_amount: string;
  percentage: number;
  transaction_count: number;
}

export interface DailySpend {
  date: string;
  amount: string;
  transaction_count: number;
  cumulative_amount: string;
}

export interface TemporalMetrics {
  daily_spending: DailySpend[];
  weekday_spend: string;
  weekend_spend: string;
  weekday_percentage: number;
  weekend_percentage: number;
  avg_daily_burn_rate: string;
  day_of_week_breakdown: Record<string, string>;
}

export interface MicroSpendMetrics {
  threshold: string;
  count: number;
  total_amount: string;
  percentage_of_transactions: number;
  percentage_of_spend: number;
  top_micro_merchants: string[];
}

export interface RecurringItem {
  merchant_name: string;
  category: Category;
  amount: string;
  frequency: string;
  occurrences: number;
  annualized_cost: string;
  transaction_dates: string[];
}

export interface RecurringAnalysis {
  items: RecurringItem[];
  total_monthly_recurring: string;
  total_annual_recurring: string;
  recurring_percentage_of_spend: number;
}

export interface StatementAnalytics {
  spend_metrics: SpendMetrics;
  category_breakdown: CategoryBreakdown[];
  merchant_concentration: MerchantConcentration[];
  temporal_metrics: TemporalMetrics;
  micro_spend_metrics: MicroSpendMetrics;
  recurring_analysis: RecurringAnalysis;
}

export interface FindingEvidence {
  current_value: string | number;
  threshold_or_baseline?: string | number | null;
  delta_percentage?: number | null;
  related_category?: Category | null;
  related_merchants: string[];
  transaction_count?: number | null;
  context_data?: Record<string, unknown>;
}

export interface Finding {
  id: string;
  detector_type: DetectorType;
  severity: FindingSeverity;
  title: string;
  description: string;
  evidence: FindingEvidence;
  impact_amount?: string | null;
  actionable: boolean;
}

export interface AnomalyDetectionResult {
  findings: Finding[];
  total_findings_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

export interface RecommendationEvidence {
  current_spend?: string | null;
  historical_avg?: string | null;
  transaction_count?: number | null;
  top_merchants: string[];
  excess_amount?: string | null;
  savings_calculation_basis?: string | null;
  context_data?: Record<string, unknown>;
}

export interface Recommendation {
  id: string;
  finding_id?: string | null;
  type: RecommendationType;
  title: string;
  reason: string;
  evidence: RecommendationEvidence;
  estimated_monthly_savings: string;
  confidence_score: number;
  action: string;
  priority: number;
  target_category?: Category | null;
  status: 'ACTIVE' | 'ACCEPTED' | 'DISMISSED' | 'COMPLETED';
}

export interface RecommendationResult {
  recommendations: Recommendation[];
  total_potential_monthly_savings: string;
  recommendations_count: number;
  high_impact_count: number;
}

export interface ActionStep {
  step_number: number;
  title: string;
  description: string;
  estimated_impact?: string | null;
}

export interface FindingHighlight {
  finding_title: string;
  observation: string;
  urgency: 'Immediate Action' | 'This Month' | 'Good Habit';
}

export interface LLMExplanationResult {
  executive_summary: string;
  what_stands_out: FindingHighlight[];
  action_steps: ActionStep[];
  coaching_tone_note: string;
  generated_by: string;
  is_fallback: boolean;
}

export interface ParseStatementResponse {
  header: StatementHeader;
  transactions: CategorizedTransaction[];
  raw_text_length: number;
  reconciliation_status: string;
  reconciliation_discrepancy: string;
  reconciliation: ReconciliationSummary;
  validation: ValidationResult;
  categorization_stats: CategorizationStats;
  analytics: StatementAnalytics;
  anomalies: AnomalyDetectionResult;
  recommendations: RecommendationResult;
  explanation: LLMExplanationResult;
  unparsed_lines: string[];
}

export type RecommendationEventType =
  | 'VIEWED'
  | 'EXPLORED_TRANSACTIONS'
  | 'ACCEPTED'
  | 'DISMISSED'
  | 'COMPLETED'
  | 'UNDONE';

export type DismissReason =
  | 'ALREADY_PLANNED'
  | 'NOT_APPLICABLE'
  | 'TOO_RESTRICTIVE'
  | 'CANNOT_REDUCE'
  | 'OTHER';

export interface RecommendationFeedbackRequest {
  event_type: RecommendationEventType;
  dismiss_reason?: DismissReason | null;
  feedback_notes?: string | null;
  estimated_monthly_savings?: string | number | null;
  target_category?: Category | null;
  metadata?: Record<string, unknown>;
}

export interface RecommendationFeedbackResponse {
  success: boolean;
  recommendation_id: string;
  current_status: 'ACTIVE' | 'ACCEPTED' | 'DISMISSED' | 'COMPLETED';
  recorded_event_id: string;
  timestamp: string;
  message: string;
}

export interface StoredRecommendationState {
  recommendation_id: string;
  status: 'ACTIVE' | 'ACCEPTED' | 'DISMISSED' | 'COMPLETED';
  title: string;
  target_category?: Category | null;
  estimated_monthly_savings: string;
  dismiss_reason?: DismissReason | null;
  feedback_notes?: string | null;
  action_text?: string;
  updated_at: string;
}

export interface FeedbackEventRecord {
  id: string;
  recommendation_id: string;
  event_type: RecommendationEventType;
  dismiss_reason?: DismissReason | null;
  feedback_notes?: string | null;
  timestamp: string;
}

export interface StatementSnapshot {
  id: string;
  issuer: string;
  card_last_4?: string | null;
  period_start?: string | null;
  period_end?: string | null;
  total_spend: number;
  category_totals: Record<string, number>;
  uploaded_at: string;
}

export interface MoMCategoryDelta {
  category: Category;
  previous_spend: number;
  current_spend: number;
  delta_amount: number; // positive = spent more, negative = saved
  delta_percentage: number;
  has_active_goal: boolean;
}

export interface MoMGoalComparison {
  recommendation_id: string;
  title: string;
  target_category: Category;
  target_savings: number;
  previous_spend: number;
  current_spend: number;
  realized_savings: number;
  achievement_percentage: number;
  status: 'EXCEEDED_GOAL' | 'ACHIEVED' | 'PARTIAL_PROGRESS' | 'INCREASED';
}

export interface MoMComparisonResult {
  previous_period_label: string;
  current_period_label: string;
  previous_total_spend: number;
  current_total_spend: number;
  net_spend_change: number;
  net_spend_change_percentage: number;
  category_deltas: MoMCategoryDelta[];
  goal_comparisons: MoMGoalComparison[];
  total_realized_savings: number;
  total_target_savings: number;
  goals_achieved_count: number;
  goals_total_count: number;
  is_simulated_baseline?: boolean;
}

export interface StatementSaveRequest {
  statement_data: ParseStatementResponse;
  user_id?: string | null;
  card_name?: string | null;
  save_transactions?: boolean;
  save_findings?: boolean;
  save_recommendations?: boolean;
}

export interface StatementSaveResponse {
  success: boolean;
  statement_id: string;
  card_id?: string | null;
  saved_transactions_count: number;
  saved_findings_count: number;
  saved_recommendations_count: number;
  saved_at: string;
  message: string;
}

export interface StatementHistoryItem {
  id: string;
  issuer: string;
  card_last_4?: string | null;
  card_name?: string | null;
  period_start?: string | null;
  period_end?: string | null;
  due_date?: string | null;
  total_amount_due: string;
  total_debits: string;
  reconciliation_status: string;
  transaction_count: number;
  findings_count: number;
  recommendations_count: number;
  created_at: string;
}

export interface StatementHistoryResponse {
  statements: StatementHistoryItem[];
  total_count: number;
}


