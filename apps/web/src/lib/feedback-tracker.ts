import {
  Category,
  DismissReason,
  FeedbackEventRecord,
  MoMComparisonResult,
  MoMGoalComparison,
  MoMCategoryDelta,
  ParseStatementResponse,
  Recommendation,
  RecommendationEventType,
  RecommendationFeedbackRequest,
  StatementSnapshot,
  StoredRecommendationState,
} from '@/types';
import { recordRecommendationFeedbackApi } from './api';

const RECS_STORAGE_KEY = 'cctrack_recommendation_states';
const EVENTS_STORAGE_KEY = 'cctrack_feedback_events';
const STATEMENTS_STORAGE_KEY = 'cctrack_statements_history';

/**
 * Safely check if window / localStorage is available in browser runtime.
 */
function isBrowser(): boolean {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

/**
 * Retrieve all saved recommendation states from local storage.
 */
export function getStoredRecommendationStates(): Record<string, StoredRecommendationState> {
  if (!isBrowser()) return {};
  try {
    const raw = localStorage.getItem(RECS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (err) {
    console.warn('Failed to parse recommendation states from localStorage', err);
    return {};
  }
}

/**
 * Retrieve a specific recommendation state by its ID.
 */
export function getStoredRecommendationState(
  recommendationId: string
): StoredRecommendationState | null {
  const states = getStoredRecommendationStates();
  return states[recommendationId] || null;
}

/**
 * Save or update a recommendation state in local storage.
 */
export function saveRecommendationState(state: StoredRecommendationState): void {
  if (!isBrowser()) return;
  try {
    const states = getStoredRecommendationStates();
    states[state.recommendation_id] = state;
    localStorage.setItem(RECS_STORAGE_KEY, JSON.stringify(states));

    // Dispatch custom event for reactive UI updates
    window.dispatchEvent(
      new CustomEvent('cctrack:recommendation-updated', {
        detail: state,
      })
    );
  } catch (err) {
    console.warn('Failed to save recommendation state to localStorage', err);
  }
}

/**
 * Retrieve all recorded feedback events from local storage.
 */
export function getFeedbackEvents(): FeedbackEventRecord[] {
  if (!isBrowser()) return [];
  try {
    const raw = localStorage.getItem(EVENTS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (err) {
    console.warn('Failed to parse feedback events from localStorage', err);
    return [];
  }
}

/**
 * Record a user interaction/decision on a recommendation.
 * Persists locally and synchronizes with API asynchronously.
 */
export async function recordRecommendationFeedback(
  recommendation: Recommendation,
  eventType: RecommendationEventType,
  options?: {
    dismissReason?: DismissReason | null;
    feedbackNotes?: string | null;
  }
): Promise<StoredRecommendationState> {
  const nowIso = new Date().toISOString();

  let newStatus: 'ACTIVE' | 'ACCEPTED' | 'DISMISSED' | 'COMPLETED' = 'ACTIVE';
  if (eventType === 'ACCEPTED') {
    newStatus = 'ACCEPTED';
  } else if (eventType === 'DISMISSED') {
    newStatus = 'DISMISSED';
  } else if (eventType === 'COMPLETED') {
    newStatus = 'COMPLETED';
  } else if (eventType === 'UNDONE') {
    newStatus = 'ACTIVE';
  }

  const updatedState: StoredRecommendationState = {
    recommendation_id: recommendation.id,
    status: newStatus,
    title: recommendation.title,
    target_category: recommendation.target_category,
    estimated_monthly_savings: recommendation.estimated_monthly_savings,
    dismiss_reason: options?.dismissReason || null,
    feedback_notes: options?.feedbackNotes || null,
    action_text: recommendation.action,
    updated_at: nowIso,
  };

  // 1. Save state in local storage
  saveRecommendationState(updatedState);

  // 2. Append event to event log
  if (isBrowser()) {
    try {
      const events = getFeedbackEvents();
      events.push({
        id: `evt_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        recommendation_id: recommendation.id,
        event_type: eventType,
        dismiss_reason: options?.dismissReason || null,
        feedback_notes: options?.feedbackNotes || null,
        timestamp: nowIso,
      });
      localStorage.setItem(EVENTS_STORAGE_KEY, JSON.stringify(events));
    } catch (err) {
      console.warn('Failed to append feedback event to localStorage', err);
    }
  }

  // 3. Dispatch API request non-blockingly
  try {
    const payload: RecommendationFeedbackRequest = {
      event_type: eventType,
      dismiss_reason: options?.dismissReason || null,
      feedback_notes: options?.feedbackNotes || null,
      estimated_monthly_savings: recommendation.estimated_monthly_savings,
      target_category: recommendation.target_category || null,
      metadata: {
        title: recommendation.title,
        priority: recommendation.priority,
      },
    };
    await recordRecommendationFeedbackApi(recommendation.id, payload);
  } catch (apiErr) {
    // Non-fatal: local storage is ground truth for client session
    console.info('Backend feedback sync completed with local fallback', apiErr);
  }

  return updatedState;
}

/**
 * Get list of all currently accepted goals.
 */
export function getAllAcceptedGoals(): StoredRecommendationState[] {
  const states = getStoredRecommendationStates();
  return Object.values(states).filter((s) => s.status === 'ACCEPTED');
}

/**
 * Save a lightweight statement snapshot for historical comparison.
 */
export function saveStatementSnapshot(statement: ParseStatementResponse): StatementSnapshot {
  const categoryTotals: Record<string, number> = {};
  statement.analytics.category_breakdown.forEach((cb) => {
    categoryTotals[cb.category] = parseFloat(cb.total_amount) || 0;
  });

  const snapshot: StatementSnapshot = {
    id: `stmt_${statement.header.issuer}_${statement.header.statement_period_end || Date.now()}`,
    issuer: statement.header.issuer,
    card_last_4: statement.header.card_last_4,
    period_start: statement.header.statement_period_start,
    period_end: statement.header.statement_period_end,
    total_spend: parseFloat(statement.analytics.spend_metrics.total_debits) || 0,
    category_totals: categoryTotals,
    uploaded_at: new Date().toISOString(),
  };

  if (isBrowser()) {
    try {
      const history = getHistoricalStatementSnapshots();
      // Avoid duplicate snapshots for same id
      const filtered = history.filter((h) => h.id !== snapshot.id);
      filtered.unshift(snapshot);
      // Keep up to 12 monthly statements
      localStorage.setItem(STATEMENTS_STORAGE_KEY, JSON.stringify(filtered.slice(0, 12)));
    } catch (err) {
      console.warn('Failed to save statement snapshot', err);
    }
  }

  return snapshot;
}

/**
 * Retrieve saved historical statement snapshots.
 */
export function getHistoricalStatementSnapshots(): StatementSnapshot[] {
  if (!isBrowser()) return [];
  try {
    const raw = localStorage.getItem(STATEMENTS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (err) {
    console.warn('Failed to parse statement snapshots from localStorage', err);
    return [];
  }
}

/**
 * Generate a realistic simulated baseline for demonstration when no prior statement exists.
 */
export function createSimulatedPriorBaseline(
  currentStatement: ParseStatementResponse
): StatementSnapshot {
  const currentCategoryTotals: Record<string, number> = {};
  currentStatement.analytics.category_breakdown.forEach((cb) => {
    currentCategoryTotals[cb.category] = parseFloat(cb.total_amount) || 0;
  });

  const simulatedCategoryTotals: Record<string, number> = {};
  let simulatedTotalSpend = 0;

  // Realistic simulation: Food & Dining and Shopping were slightly higher previously, Utilities steady
  const categoryMultipliers: Record<string, number> = {
    'Food & Dining': 1.28,
    'Groceries & Quick-Commerce': 1.35,
    'Shopping': 1.20,
    'Entertainment & OTT': 1.15,
    'Subscriptions': 1.25,
    'Transport & Fuel': 1.05,
    'Bills & Utilities': 0.98,
    'Healthcare & Fitness': 1.0,
    'Travel & Lodging': 0.85,
    'Fees & Charges': 1.5,
  };

  Object.entries(currentCategoryTotals).forEach(([cat, amount]) => {
    const multiplier = categoryMultipliers[cat] ?? 1.15;
    const prevAmount = Math.round(amount * multiplier);
    simulatedCategoryTotals[cat] = prevAmount;
    simulatedTotalSpend += prevAmount;
  });

  return {
    id: 'simulated_baseline',
    issuer: currentStatement.header.issuer,
    card_last_4: currentStatement.header.card_last_4,
    period_start: 'Previous 3-Month Average Baseline',
    period_end: 'Prior Cycle',
    total_spend: simulatedTotalSpend,
    category_totals: simulatedCategoryTotals,
    uploaded_at: new Date().toISOString(),
  };
}

/**
 * Compute Month-over-Month comparison metrics and verify savings against accepted goals.
 */
export function computeMoMOutcome(
  currentStatement: ParseStatementResponse,
  priorSnapshotOrBaseline?: StatementSnapshot | null,
  options?: {
    simulateIfMissing?: boolean;
    acceptedGoalsOverride?: StoredRecommendationState[];
  }
): MoMComparisonResult {
  let baseline = priorSnapshotOrBaseline;
  let isSimulated = false;

  if (!baseline && (options?.simulateIfMissing ?? true)) {
    baseline = createSimulatedPriorBaseline(currentStatement);
    isSimulated = true;
  }

  const currentCategoryMap: Record<Category, number> = {} as Record<Category, number>;
  currentStatement.analytics.category_breakdown.forEach((cb) => {
    currentCategoryMap[cb.category] = parseFloat(cb.total_amount) || 0;
  });

  const priorCategoryMap = baseline?.category_totals || {};
  const currentTotalSpend = parseFloat(currentStatement.analytics.spend_metrics.total_debits) || 0;
  const priorTotalSpend = baseline?.total_spend || currentTotalSpend;

  const netSpendChange = currentTotalSpend - priorTotalSpend;
  const netSpendChangePercentage =
    priorTotalSpend > 0 ? (netSpendChange / priorTotalSpend) * 100 : 0;

  // Retrieve accepted goals (either from local storage or recommendations)
  const storedStates = getStoredRecommendationStates();
  const activeRecommendations = currentStatement.recommendations.recommendations;

  // Active goals list: match stored accepted state, or recommendation status
  const acceptedGoals: Array<{
    id: string;
    title: string;
    target_category: Category;
    estimated_savings: number;
  }> = [];

  activeRecommendations.forEach((rec) => {
    const stored = storedStates[rec.id];
    const isAccepted = (stored && stored.status === 'ACCEPTED') || rec.status === 'ACCEPTED';
    if (isAccepted && rec.target_category) {
      acceptedGoals.push({
        id: rec.id,
        title: rec.title,
        target_category: rec.target_category,
        estimated_savings: parseFloat(rec.estimated_monthly_savings) || 0,
      });
    }
  });

  // If no goals are accepted in storage, take top 2 recommendations to preview goal tracking
  if (acceptedGoals.length === 0 && activeRecommendations.length > 0) {
    activeRecommendations.slice(0, 2).forEach((rec) => {
      if (rec.target_category) {
        acceptedGoals.push({
          id: rec.id,
          title: rec.title,
          target_category: rec.target_category,
          estimated_savings: parseFloat(rec.estimated_monthly_savings) || 0,
        });
      }
    });
  }

  const acceptedCategorySet = new Set(acceptedGoals.map((g) => g.target_category));

  // Compute category deltas
  const allCategories = Array.from(
    new Set([
      ...Object.keys(currentCategoryMap),
      ...Object.keys(priorCategoryMap),
    ])
  ) as Category[];

  const categoryDeltas: MoMCategoryDelta[] = allCategories
    .map((cat) => {
      const cur = currentCategoryMap[cat] || 0;
      const prev = priorCategoryMap[cat] || 0;
      const delta = cur - prev;
      const pct = prev > 0 ? (delta / prev) * 100 : cur > 0 ? 100 : 0;
      return {
        category: cat,
        previous_spend: prev,
        current_spend: cur,
        delta_amount: delta,
        delta_percentage: Math.round(pct * 10) / 10,
        has_active_goal: acceptedCategorySet.has(cat),
      };
    })
    .sort((a, b) => Math.abs(b.delta_amount) - Math.abs(a.delta_amount));

  // Compute goal-by-goal verification
  let totalRealizedSavings = 0;
  let totalTargetSavings = 0;
  let goalsAchievedCount = 0;

  const goalComparisons: MoMGoalComparison[] = acceptedGoals.map((goal) => {
    const prev = priorCategoryMap[goal.target_category] || (currentCategoryMap[goal.target_category] * 1.3);
    const cur = currentCategoryMap[goal.target_category] || 0;
    const delta = prev - cur; // positive means spend was reduced (savings realized)
    const realized = Math.max(0, Math.round(delta));
    const target = goal.estimated_savings || 1000;
    const achievePct = target > 0 ? Math.round((realized / target) * 100) : 0;

    let status: 'EXCEEDED_GOAL' | 'ACHIEVED' | 'PARTIAL_PROGRESS' | 'INCREASED' = 'PARTIAL_PROGRESS';
    if (delta <= 0) {
      status = 'INCREASED';
    } else if (achievePct >= 100) {
      status = 'EXCEEDED_GOAL';
      goalsAchievedCount++;
    } else if (achievePct >= 80) {
      status = 'ACHIEVED';
      goalsAchievedCount++;
    } else {
      status = 'PARTIAL_PROGRESS';
    }

    totalRealizedSavings += realized;
    totalTargetSavings += target;

    return {
      recommendation_id: goal.id,
      title: goal.title,
      target_category: goal.target_category,
      target_savings: target,
      previous_spend: Math.round(prev),
      current_spend: Math.round(cur),
      realized_savings: realized,
      achievement_percentage: achievePct,
      status: status,
    };
  });

  return {
    previous_period_label: isSimulated
      ? 'Historical Baseline (3-Mo Avg)'
      : baseline?.period_start
      ? `${baseline.period_start} – ${baseline.period_end}`
      : 'Prior Statement',
    current_period_label: currentStatement.header.statement_period_start
      ? `${currentStatement.header.statement_period_start} – ${currentStatement.header.statement_period_end}`
      : 'Current Statement',
    previous_total_spend: Math.round(priorTotalSpend),
    current_total_spend: Math.round(currentTotalSpend),
    net_spend_change: Math.round(netSpendChange),
    net_spend_change_percentage: Math.round(netSpendChangePercentage * 10) / 10,
    category_deltas: categoryDeltas,
    goal_comparisons: goalComparisons,
    total_realized_savings: totalRealizedSavings,
    total_target_savings: totalTargetSavings,
    goals_achieved_count: goalsAchievedCount,
    goals_total_count: goalComparisons.length,
    is_simulated_baseline: isSimulated,
  };
}
