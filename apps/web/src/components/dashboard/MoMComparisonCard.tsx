'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  ParseStatementResponse,
  MoMComparisonResult,
  StatementSnapshot,
} from '@/types';
import { formatINR } from '@/lib/formatters';
import {
  computeMoMOutcome,
  getHistoricalStatementSnapshots,
  getStoredRecommendationStates,
} from '@/lib/feedback-tracker';
import { Button } from '@/components/ui/button';
import {
  Sparkles,
  TrendingDown,
  TrendingUp,
  Award,
  CheckCircle,
  AlertTriangle,
  History,
  Target,
  ArrowRight,
  BarChart2,
  Calendar,
  Layers,
} from 'lucide-react';

export interface MoMComparisonCardProps {
  currentStatement: ParseStatementResponse;
  onExploreCategory?: (category: string) => void;
}

export const MoMComparisonCard: React.FC<MoMComparisonCardProps> = ({
  currentStatement,
  onExploreCategory,
}) => {
  const [snapshots, setSnapshots] = useState<StatementSnapshot[]>([]);
  const [selectedSnapshotId, setSelectedSnapshotId] = useState<string>('baseline');
  const [momResult, setMomResult] = useState<MoMComparisonResult | null>(null);

  const refreshComparison = useCallback(() => {
    const history = getHistoricalStatementSnapshots();
    // Exclude current statement from prior snapshots list if present
    const priorStatements = history.filter(
      (h) => h.period_end !== currentStatement.header.statement_period_end
    );
    setSnapshots(priorStatements);

    let priorSnapshot: StatementSnapshot | null = null;
    if (selectedSnapshotId !== 'baseline' && selectedSnapshotId !== 'simulated') {
      priorSnapshot = priorStatements.find((s) => s.id === selectedSnapshotId) || null;
    }

    const result = computeMoMOutcome(
      currentStatement,
      priorSnapshot,
      { simulateIfMissing: true }
    );
    setMomResult(result);
  }, [currentStatement, selectedSnapshotId]);

  useEffect(() => {
    refreshComparison();

    const handleGoalUpdate = () => {
      refreshComparison();
    };

    window.addEventListener('cctrack:recommendation-updated', handleGoalUpdate);
    return () => window.removeEventListener('cctrack:recommendation-updated', handleGoalUpdate);
  }, [refreshComparison]);


  if (!momResult) return null;

  const isNetSavings = momResult.net_spend_change <= 0;
  const absNetChange = Math.abs(momResult.net_spend_change);

  return (
    <div className="bg-paper border-2 md:border-4 border-black p-5 sm:p-7 shadow-bauhaus-md md:shadow-bauhaus-lg space-y-6">
      {/* 1. Header & Comparison Baseline Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b-2 border-black">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-bauhaus-blue text-white border-2 border-black flex items-center justify-center shadow-bauhaus-xs shrink-0">
            <History className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.2 bg-bauhaus-yellow text-ink border border-black font-mono text-[10px] font-bold uppercase">
                Stage 3 Feature
              </span>
              <span className="text-xs font-mono font-bold text-ink/70">
                Closed-Loop Verification
              </span>
            </div>
            <h3 className="text-xl sm:text-2xl font-black uppercase tracking-tight text-ink">
              Month-over-Month Outcome Tracking
            </h3>
          </div>
        </div>

        {/* Comparison Selector Chips */}
        <div className="flex items-center gap-2 flex-wrap font-mono text-xs">
          <span className="font-bold uppercase text-ink/70 text-[11px]">Compare With:</span>
          <button
            onClick={() => setSelectedSnapshotId('baseline')}
            className={`px-2.5 py-1 border border-black font-bold uppercase text-xs transition-all ${
              selectedSnapshotId === 'baseline'
                ? 'bg-bauhaus-blue text-white shadow-bauhaus-xs'
                : 'bg-white text-ink/70 hover:text-ink'
            }`}
          >
            Historical Baseline
          </button>

          {snapshots.map((snap) => (
            <button
              key={snap.id}
              onClick={() => setSelectedSnapshotId(snap.id)}
              className={`px-2.5 py-1 border border-black font-bold uppercase text-xs transition-all ${
                selectedSnapshotId === snap.id
                  ? 'bg-bauhaus-blue text-white shadow-bauhaus-xs'
                  : 'bg-white text-ink/70 hover:text-ink'
              }`}
            >
              {snap.period_end || snap.issuer}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Top Outcome Celebration Ribbon */}
      <div
        className={`border-2 md:border-3 border-black p-5 shadow-bauhaus-sm flex flex-col md:flex-row md:items-center justify-between gap-4 ${
          isNetSavings ? 'bg-bauhaus-green-light' : 'bg-bauhaus-yellow-light'
        }`}
      >
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            {isNetSavings ? (
              <CheckCircle className="w-5 h-5 text-bauhaus-green" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-bauhaus-red" />
            )}
            <h4 className="text-lg font-black uppercase tracking-tight text-ink">
              {isNetSavings
                ? `Verified Savings: Reduced Total Spend by ${formatINR(absNetChange)}`
                : `Total Spend Increased by ${formatINR(absNetChange)} this Cycle`}
            </h4>
          </div>
          <p className="text-xs sm:text-sm font-medium text-ink/80 max-w-2xl">
            {isNetSavings
              ? `Comparing ${momResult.current_period_label} against ${momResult.previous_period_label}. Target behavioral changes resulted in lower discretionary drain.`
              : `Spend velocity increased compared to ${momResult.previous_period_label}. Review individual target categories below to locate cost spikes.`}
          </p>
        </div>

        {/* Key Metrics Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 shrink-0 font-mono text-center">
          <div className="bg-white border-2 border-black p-2 shadow-bauhaus-xs">
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Net Spend Delta
            </span>
            <span
              className={`text-sm font-black flex items-center justify-center gap-0.5 ${
                isNetSavings ? 'text-bauhaus-green' : 'text-bauhaus-red'
              }`}
            >
              {isNetSavings ? <TrendingDown className="w-3.5 h-3.5" /> : <TrendingUp className="w-3.5 h-3.5" />}
              <span>
                {isNetSavings ? '-' : '+'}
                {Math.abs(momResult.net_spend_change_percentage)}%
              </span>
            </span>
          </div>

          <div className="bg-white border-2 border-black p-2 shadow-bauhaus-xs">
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Realized Savings
            </span>
            <span className="text-sm font-black text-bauhaus-green">
              {formatINR(momResult.total_realized_savings)}
            </span>
          </div>

          <div className="bg-white border-2 border-black p-2 shadow-bauhaus-xs col-span-2 sm:col-span-1">
            <span className="block text-[10px] uppercase font-bold text-ink/60">
              Goals Achieved
            </span>
            <span className="text-sm font-black text-ink">
              {momResult.goals_achieved_count} / {momResult.goals_total_count}
            </span>
          </div>
        </div>
      </div>

      {/* 3. Goal-by-Goal Verification Cards */}
      {momResult.goal_comparisons.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold uppercase tracking-wider text-ink font-mono flex items-center gap-1.5">
              <Award className="w-4 h-4 text-bauhaus-yellow" />
              <span>Targeted Behavioral Goals & Realized Outcomes</span>
            </h4>
            <span className="text-xs font-mono text-ink/70">
              {momResult.goals_achieved_count} of {momResult.goals_total_count} targets on track
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {momResult.goal_comparisons.map((goal) => {
              const isExceeded = goal.status === 'EXCEEDED_GOAL';
              const isAchieved = goal.status === 'ACHIEVED';
              const isPartial = goal.status === 'PARTIAL_PROGRESS';
              const isIncreased = goal.status === 'INCREASED';

              return (
                <div
                  key={goal.recommendation_id}
                  className="bg-white border-2 border-black p-4 shadow-bauhaus-xs flex flex-col justify-between"
                >
                  <div>
                    {/* Top Goal Header */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="px-2 py-0.5 bg-muted text-ink font-mono font-bold text-[10px] uppercase border border-black">
                        {goal.target_category}
                      </span>

                      <span
                        className={`px-2 py-0.5 font-mono font-black text-[10px] uppercase border border-black ${
                          isExceeded || isAchieved
                            ? 'bg-bauhaus-green text-white'
                            : isPartial
                            ? 'bg-bauhaus-yellow text-ink'
                            : 'bg-bauhaus-red text-white'
                        }`}
                      >
                        {isExceeded
                          ? 'Target Exceeded'
                          : isAchieved
                          ? 'Goal Achieved'
                          : isPartial
                          ? 'Partial Progress'
                          : 'Spend Increased'}
                      </span>
                    </div>

                    <h5 className="font-black text-sm uppercase tracking-tight text-ink mb-2">
                      {goal.title}
                    </h5>

                    {/* Spend Comparison Figures */}
                    <div className="grid grid-cols-3 gap-2 bg-canvas border border-black p-2 font-mono text-center text-xs mb-3">
                      <div>
                        <span className="block text-[9px] uppercase font-bold text-ink/60">
                          Prior Spend
                        </span>
                        <span className="font-bold text-ink">
                          {formatINR(goal.previous_spend)}
                        </span>
                      </div>
                      <div>
                        <span className="block text-[9px] uppercase font-bold text-ink/60">
                          Current Spend
                        </span>
                        <span className="font-bold text-ink">
                          {formatINR(goal.current_spend)}
                        </span>
                      </div>
                      <div>
                        <span className="block text-[9px] uppercase font-bold text-ink/60">
                          Realized Savings
                        </span>
                        <span
                          className={`font-bold ${
                            goal.realized_savings > 0 ? 'text-bauhaus-green' : 'text-bauhaus-red'
                          }`}
                        >
                          {formatINR(goal.realized_savings)}
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="space-y-1 font-mono text-[11px]">
                      <div className="flex items-center justify-between text-ink/80 font-bold">
                        <span>Savings Goal: {formatINR(goal.target_savings)}/mo</span>
                        <span>{goal.achievement_percentage}% Met</span>
                      </div>
                      <div className="w-full bg-muted border border-black h-2.5 overflow-hidden">
                        <div
                          className={`h-full transition-all duration-300 ${
                            isExceeded || isAchieved
                              ? 'bg-bauhaus-green'
                              : isPartial
                              ? 'bg-bauhaus-yellow'
                              : 'bg-bauhaus-red'
                          }`}
                          style={{
                            width: `${Math.min(100, Math.max(0, goal.achievement_percentage))}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {onExploreCategory && (
                    <button
                      onClick={() => onExploreCategory(goal.target_category)}
                      className="mt-3 pt-2 border-t border-black/10 text-[11px] font-mono font-bold text-bauhaus-blue hover:underline flex items-center justify-end gap-1"
                    >
                      <span>Drill into {goal.target_category}</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 4. Category Spending Delta Matrix */}
      <div className="space-y-3 pt-2">
        <h4 className="text-sm font-bold uppercase tracking-wider text-ink font-mono flex items-center gap-1.5">
          <BarChart2 className="w-4 h-4 text-bauhaus-blue" />
          <span>Category-by-Category Spend Comparison</span>
        </h4>

        <div className="border-2 border-black overflow-x-auto bg-white shadow-bauhaus-xs">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-canvas border-b-2 border-black text-ink uppercase text-[11px]">
              <tr>
                <th className="p-2.5 font-bold">Category</th>
                <th className="p-2.5 font-bold text-right">Prior / Baseline</th>
                <th className="p-2.5 font-bold text-right">Current Spend</th>
                <th className="p-2.5 font-bold text-right">Delta Amount</th>
                <th className="p-2.5 font-bold text-right">Delta %</th>
                <th className="p-2.5 font-bold text-center">Goal Status</th>
              </tr>
            </thead>
            <tbody className="divide-y border-black">
              {momResult.category_deltas.map((cd) => {
                const isDecreased = cd.delta_amount < 0;
                const isZero = cd.delta_amount === 0;

                return (
                  <tr
                    key={cd.category}
                    className="hover:bg-muted/30 transition-colors"
                  >
                    <td className="p-2.5 font-bold text-ink flex items-center gap-1.5">
                      <span>{cd.category}</span>
                      {cd.has_active_goal && (
                        <span className="px-1.5 py-0.2 bg-bauhaus-yellow text-ink border border-black text-[9px] font-bold uppercase">
                          Goal
                        </span>
                      )}
                    </td>
                    <td className="p-2.5 text-right text-ink/75">
                      {formatINR(cd.previous_spend)}
                    </td>
                    <td className="p-2.5 text-right font-bold text-ink">
                      {formatINR(cd.current_spend)}
                    </td>
                    <td
                      className={`p-2.5 text-right font-bold ${
                        isDecreased
                          ? 'text-bauhaus-green'
                          : isZero
                          ? 'text-ink/60'
                          : 'text-bauhaus-red'
                      }`}
                    >
                      {isDecreased ? '-' : isZero ? '' : '+'}
                      {formatINR(Math.abs(cd.delta_amount))}
                    </td>
                    <td
                      className={`p-2.5 text-right font-bold ${
                        isDecreased
                          ? 'text-bauhaus-green'
                          : isZero
                          ? 'text-ink/60'
                          : 'text-bauhaus-red'
                      }`}
                    >
                      {isDecreased ? '-' : isZero ? '' : '+'}
                      {Math.abs(cd.delta_percentage)}%
                    </td>
                    <td className="p-2.5 text-center">
                      {cd.has_active_goal ? (
                        <span className="px-2 py-0.5 bg-bauhaus-green-light text-bauhaus-green border border-black font-bold text-[10px]">
                          Target Active
                        </span>
                      ) : (
                        <span className="text-ink/40 text-[10px]">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
