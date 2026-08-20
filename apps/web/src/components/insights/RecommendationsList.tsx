'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { RecommendationResult, Recommendation, Category } from '@/types';
import { RecommendationCard } from './RecommendationCard';
import { formatINR } from '@/lib/formatters';
import {
  getStoredRecommendationStates,
  getAllAcceptedGoals,
} from '@/lib/feedback-tracker';
import {
  Sparkles,
  TrendingDown,
  Target,
  CheckCircle2,
  Filter,
  Layers,
  Award,
} from 'lucide-react';

export interface RecommendationsListProps {
  recommendationResult: RecommendationResult;
  onShowTransactions?: (category?: string, merchants?: string[]) => void;
  onGoalsUpdated?: () => void;
}

export const RecommendationsList: React.FC<RecommendationsListProps> = ({
  recommendationResult,
  onShowTransactions,
  onGoalsUpdated,
}) => {
  const { recommendations, total_potential_monthly_savings, recommendations_count, high_impact_count } =
    recommendationResult;

  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ACTIVE' | 'ACCEPTED' | 'DISMISSED'>('ALL');
  const [acceptedGoalsCount, setAcceptedGoalsCount] = useState<number>(0);
  const [acceptedSavingsTarget, setAcceptedSavingsTarget] = useState<number>(0);
  const [dismissedCount, setDismissedCount] = useState<number>(0);

  const refreshFeedbackStats = useCallback(() => {
    const states = getStoredRecommendationStates();
    let accepted = 0;
    let savings = 0;
    let dismissed = 0;

    recommendations.forEach((rec) => {
      const st = states[rec.id];
      const currentStatus = st?.status || rec.status || 'ACTIVE';
      if (currentStatus === 'ACCEPTED' || currentStatus === 'COMPLETED') {
        accepted++;
        savings += parseFloat(rec.estimated_monthly_savings) || 0;
      } else if (currentStatus === 'DISMISSED') {
        dismissed++;
      }
    });

    setAcceptedGoalsCount(accepted);
    setAcceptedSavingsTarget(savings);
    setDismissedCount(dismissed);
    onGoalsUpdated?.();
  }, [recommendations, onGoalsUpdated]);

  useEffect(() => {
    refreshFeedbackStats();

    const handleUpdate = () => {
      refreshFeedbackStats();
    };

    window.addEventListener('cctrack:recommendation-updated', handleUpdate);
    return () => window.removeEventListener('cctrack:recommendation-updated', handleUpdate);
  }, [refreshFeedbackStats]);


  const categories: Category[] = Array.from(
    new Set(
      recommendations
        .map((r) => r.target_category)
        .filter((c): c is Category => Boolean(c))
    )
  );

  const states = getStoredRecommendationStates();

  const filteredRecs = recommendations.filter((r) => {
    const st = states[r.id]?.status || r.status || 'ACTIVE';
    const matchesCategory = filterCategory === 'ALL' || r.target_category === filterCategory;
    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'ACTIVE' && st === 'ACTIVE') ||
      (statusFilter === 'ACCEPTED' && (st === 'ACCEPTED' || st === 'COMPLETED')) ||
      (statusFilter === 'DISMISSED' && st === 'DISMISSED');

    return matchesCategory && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Top Behavioral Savings Header Ribbon */}
      <div className="bg-bauhaus-yellow border-2 md:border-4 border-black p-5 sm:p-6 shadow-bauhaus-md md:shadow-bauhaus-lg text-ink flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-ink" />
            <h3 className="font-black uppercase tracking-tight text-xl sm:text-2xl">
              Deterministic Spending Recommendations
            </h3>
          </div>
          <p className="text-xs sm:text-sm font-medium mt-1 text-ink/90 max-w-2xl">
            Derived strictly from statistical pattern detection. Zero generic AI advice — each
            recommendation is paired with concrete transaction evidence and conservative savings math.
          </p>
        </div>

        {/* Big Total Savings Badge */}
        <div className="bg-white text-ink border-2 md:border-3 border-black p-3 sm:p-4 shadow-bauhaus-xs shrink-0 font-mono">
          <span className="block text-[10px] uppercase font-bold text-ink/70">
            Total Potential Monthly Savings
          </span>
          <span className="text-2xl sm:text-3xl font-black text-bauhaus-red flex items-center gap-1.5">
            <TrendingDown className="w-6 h-6 text-bauhaus-red" />
            <span>{formatINR(total_potential_monthly_savings)} / mo</span>
          </span>
          <span className="block text-[10px] font-bold text-ink/60 mt-0.5">
            {recommendations_count} Actionable Ideas • {high_impact_count} High Priority
          </span>
        </div>
      </div>

      {/* Goal Tracking Ribbon */}
      <div className="bg-paper border-2 md:border-3 border-black p-4 shadow-bauhaus-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 font-mono text-xs">
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="w-8 h-8 bg-bauhaus-green text-white border-2 border-black flex items-center justify-center shrink-0 shadow-bauhaus-xs">
            <Award className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold uppercase tracking-wider text-ink block text-xs">
              Your Active Goal Commitments
            </span>
            <span className="text-ink/75 text-[11px]">
              {acceptedGoalsCount > 0
                ? `${acceptedGoalsCount} active goal${acceptedGoalsCount > 1 ? 's' : ''} committed • Targeting ${formatINR(acceptedSavingsTarget)}/mo savings`
                : 'No active goals selected yet. Click "Accept Goal" below to track savings in your next statement.'}
            </span>
          </div>
        </div>

        {/* Status Filter Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setStatusFilter('ALL')}
            className={`px-2.5 py-1 border border-black font-bold uppercase text-[11px] transition-all ${
              statusFilter === 'ALL'
                ? 'bg-ink text-white shadow-bauhaus-xs'
                : 'bg-white text-ink/70 hover:text-ink'
            }`}
          >
            All ({recommendations.length})
          </button>
          <button
            onClick={() => setStatusFilter('ACCEPTED')}
            className={`px-2.5 py-1 border border-black font-bold uppercase text-[11px] transition-all ${
              statusFilter === 'ACCEPTED'
                ? 'bg-bauhaus-green text-white shadow-bauhaus-xs'
                : 'bg-white text-ink/70 hover:text-ink'
            }`}
          >
            Goals ({acceptedGoalsCount})
          </button>
          <button
            onClick={() => setStatusFilter('ACTIVE')}
            className={`px-2.5 py-1 border border-black font-bold uppercase text-[11px] transition-all ${
              statusFilter === 'ACTIVE'
                ? 'bg-bauhaus-yellow text-ink shadow-bauhaus-xs'
                : 'bg-white text-ink/70 hover:text-ink'
            }`}
          >
            Pending ({recommendations.length - acceptedGoalsCount - dismissedCount})
          </button>
          {dismissedCount > 0 && (
            <button
              onClick={() => setStatusFilter('DISMISSED')}
              className={`px-2.5 py-1 border border-black font-bold uppercase text-[11px] transition-all ${
                statusFilter === 'DISMISSED'
                  ? 'bg-muted text-ink shadow-bauhaus-xs'
                  : 'bg-white text-ink/70 hover:text-ink'
              }`}
            >
              Dismissed ({dismissedCount})
            </button>
          )}
        </div>
      </div>

      {/* Category Filter Pills (if multiple categories) */}
      {categories.length > 1 && (
        <div className="flex items-center gap-2 flex-wrap font-mono text-xs">
          <span className="font-bold uppercase text-ink/70 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Category:</span>
          </span>
          <button
            onClick={() => setFilterCategory('ALL')}
            className={`px-3 py-1 border border-black font-bold uppercase transition-all ${
              filterCategory === 'ALL'
                ? 'bg-bauhaus-yellow text-ink shadow-bauhaus-xs'
                : 'bg-canvas text-ink/70 hover:text-ink'
            }`}
          >
            All ({recommendations.length})
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-3 py-1 border border-black font-bold uppercase transition-all ${
                filterCategory === cat
                  ? 'bg-bauhaus-blue text-white shadow-bauhaus-xs'
                  : 'bg-canvas text-ink/70 hover:text-ink'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Recommendations Cards Grid */}
      {filteredRecs.length === 0 ? (
        <div className="bg-white border-2 border-black p-8 text-center font-mono">
          <Target className="w-8 h-8 text-ink/40 mx-auto mb-2" />
          <p className="font-bold text-ink">No recommendations match the current filter.</p>
          <button
            onClick={() => {
              setFilterCategory('ALL');
              setStatusFilter('ALL');
            }}
            className="mt-3 text-xs font-bold text-bauhaus-blue underline"
          >
            Clear all filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRecs.map((rec) => (
            <RecommendationCard
              key={rec.id}
              recommendation={rec}
              onShowTransactions={onShowTransactions}
              onStateChange={refreshFeedbackStats}
            />
          ))}
        </div>
      )}
    </div>
  );
};
