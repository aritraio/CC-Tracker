'use client';

import React, { useState, useEffect } from 'react';
import { Recommendation, DismissReason } from '@/types';
import { formatINR } from '@/lib/formatters';
import { Button } from '@/components/ui/button';
import { DismissReasonModal } from './DismissReasonModal';
import {
  getStoredRecommendationState,
  recordRecommendationFeedback,
} from '@/lib/feedback-tracker';
import {
  CheckCircle,
  XCircle,
  ArrowRight,
  TrendingDown,
  Lightbulb,
  RotateCcw,
  Sparkles,
  Search,
} from 'lucide-react';

export interface RecommendationCardProps {
  recommendation: Recommendation;
  onAccept?: (id: string) => void;
  onDismiss?: (id: string, reason?: DismissReason, notes?: string) => void;
  onShowTransactions?: (category?: string, merchants?: string[]) => void;
  onStateChange?: () => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onAccept,
  onDismiss,
  onShowTransactions,
  onStateChange,
}) => {
  const [status, setStatus] = useState<'ACTIVE' | 'ACCEPTED' | 'DISMISSED' | 'COMPLETED'>(
    recommendation.status || 'ACTIVE'
  );
  const [dismissReason, setDismissReason] = useState<DismissReason | null>(null);
  const [isDismissModalOpen, setIsDismissModalOpen] = useState(false);

  // Sync with persistent local state on mount
  useEffect(() => {
    const stored = getStoredRecommendationState(recommendation.id);
    if (stored) {
      setStatus(stored.status);
      setDismissReason(stored.dismiss_reason || null);
    }
  }, [recommendation.id]);

  const handleAccept = async () => {
    setStatus('ACCEPTED');
    await recordRecommendationFeedback(recommendation, 'ACCEPTED');
    onAccept?.(recommendation.id);
    onStateChange?.();
  };

  const handleDismissConfirm = async (reason: DismissReason, notes?: string) => {
    setStatus('DISMISSED');
    setDismissReason(reason);
    await recordRecommendationFeedback(recommendation, 'DISMISSED', {
      dismissReason: reason,
      feedbackNotes: notes,
    });
    onDismiss?.(recommendation.id, reason, notes);
    onStateChange?.();
  };

  const handleUndo = async () => {
    setStatus('ACTIVE');
    setDismissReason(null);
    await recordRecommendationFeedback(recommendation, 'UNDONE');
    onStateChange?.();
  };

  const handleExplore = async () => {
    await recordRecommendationFeedback(recommendation, 'EXPLORED_TRANSACTIONS');
    onShowTransactions?.(
      recommendation.target_category || undefined,
      recommendation.evidence?.top_merchants
    );
  };

  const isAccepted = status === 'ACCEPTED' || status === 'COMPLETED';
  const isDismissed = status === 'DISMISSED';

  const formatDismissLabel = (reason: DismissReason | null) => {
    switch (reason) {
      case 'ALREADY_PLANNED':
        return 'Already Planned';
      case 'NOT_APPLICABLE':
        return 'Not Applicable';
      case 'TOO_RESTRICTIVE':
        return 'Too Restrictive';
      case 'CANNOT_REDUCE':
        return 'Fixed Expense';
      default:
        return 'Dismissed';
    }
  };

  return (
    <>
      <div
        className={`border-2 md:border-4 border-black p-5 sm:p-6 relative transition-all duration-150 flex flex-col justify-between ${
          isAccepted
            ? 'bg-bauhaus-yellow-light opacity-95 shadow-bauhaus-sm border-bauhaus-green'
            : isDismissed
            ? 'bg-muted/50 opacity-70 shadow-none'
            : 'bg-white shadow-bauhaus-md hover:-translate-y-1'
        }`}
      >
        <div>
          {/* Top Header Strip */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="w-6 h-6 bg-ink text-white font-mono font-black text-xs flex items-center justify-center border border-black">
                #{recommendation.priority}
              </span>

              {recommendation.target_category && (
                <span className="px-2 py-0.5 bg-muted text-ink font-bold text-[10px] uppercase border border-black">
                  {recommendation.target_category}
                </span>
              )}

              {isAccepted && (
                <span className="px-2 py-0.5 bg-bauhaus-green text-white font-mono font-black text-[10px] uppercase border border-black flex items-center gap-1 shadow-bauhaus-xs">
                  <CheckCircle className="w-3 h-3" />
                  <span>Goal Active</span>
                </span>
              )}

              {isDismissed && (
                <span className="px-2 py-0.5 bg-muted text-ink/70 font-mono font-bold text-[10px] uppercase border border-black flex items-center gap-1">
                  <XCircle className="w-3 h-3" />
                  <span>{formatDismissLabel(dismissReason)}</span>
                </span>
              )}
            </div>

            {/* Monthly Savings Badge */}
            <div
              className={`border-2 border-black px-2.5 py-1 font-mono font-black text-xs sm:text-sm shadow-bauhaus-xs shrink-0 flex items-center gap-1.5 ${
                isAccepted
                  ? 'bg-bauhaus-green text-white'
                  : 'bg-bauhaus-yellow text-ink'
              }`}
            >
              <TrendingDown className="w-3.5 h-3.5" />
              <span>EST. SAVINGS: {formatINR(recommendation.estimated_monthly_savings)} / MO</span>
            </div>
          </div>

          {/* Title */}
          <h4
            className={`text-base sm:text-lg font-black uppercase tracking-tight text-ink mb-2 ${
              isDismissed ? 'line-through opacity-70' : ''
            }`}
          >
            {recommendation.title}
          </h4>

          {/* Behavioral Reason */}
          <p className="text-xs sm:text-sm text-ink/85 font-medium leading-relaxed mb-4">
            {recommendation.reason}
          </p>

          {/* Concrete Action Callout Box */}
          <div className="bg-canvas border-2 border-black p-3 mb-4 font-mono text-xs">
            <div className="flex items-center gap-1.5 font-bold uppercase text-ink/70 mb-1">
              <Lightbulb className="w-3.5 h-3.5 text-bauhaus-yellow" />
              <span>Recommended Action Step</span>
            </div>
            <p className="text-xs font-bold text-ink font-sans leading-snug">
              {recommendation.action}
            </p>
          </div>

          {/* Evidence Metadata */}
          {recommendation.evidence && (
            <div className="text-[11px] font-mono text-ink/70 space-y-1 mb-4 border-t border-black/10 pt-2">
              {recommendation.evidence.savings_calculation_basis && (
                <div>
                  <span className="font-bold text-ink/80">Calculation Basis: </span>
                  <span>{recommendation.evidence.savings_calculation_basis}</span>
                </div>
              )}
              {recommendation.evidence.top_merchants &&
                recommendation.evidence.top_merchants.length > 0 && (
                  <div className="flex items-center gap-1 flex-wrap pt-0.5">
                    <span className="font-bold text-ink/80">Impacted Merchants: </span>
                    {recommendation.evidence.top_merchants.map((m) => (
                      <span
                        key={m}
                        className="px-1.5 py-0.2 bg-muted text-ink border border-black font-bold text-[10px]"
                      >
                        {m}
                      </span>
                    ))}
                  </div>
                )}
            </div>
          )}
        </div>

        {/* Interactive Action Button Bar */}
        <div className="pt-3 border-t-2 border-black flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2 flex-wrap">
            {isAccepted ? (
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 text-xs font-bold font-mono text-bauhaus-green">
                  <Sparkles className="w-4 h-4" />
                  <span>Targeting {formatINR(recommendation.estimated_monthly_savings)}/mo</span>
                </span>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleUndo}
                  className="gap-1 text-[11px] py-1 px-2.5 bg-white"
                  title="Undo Goal Decision"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Change</span>
                </Button>
              </div>
            ) : isDismissed ? (
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold font-mono text-ink/60">
                  Dismissed
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleUndo}
                  className="gap-1 text-[11px] py-1 px-2.5 bg-white"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Reactivate</span>
                </Button>
              </div>
            ) : (
              <>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleAccept}
                  className="gap-1.5 text-xs py-1.5 px-3 bg-bauhaus-green hover:bg-emerald-700 text-white"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Accept Goal</span>
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsDismissModalOpen(true)}
                  className="gap-1 text-xs py-1.5 px-3 hover:bg-bauhaus-red hover:text-white"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  <span>Dismiss</span>
                </Button>
              </>
            )}
          </div>

          {onShowTransactions && (
            <button
              onClick={handleExplore}
              className="text-xs font-bold font-mono text-bauhaus-blue hover:underline flex items-center gap-1 shrink-0 ml-auto"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Inspect Txns</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Dismissal Reason Dialog */}
      <DismissReasonModal
        isOpen={isDismissModalOpen}
        recommendation={recommendation}
        onClose={() => setIsDismissModalOpen(false)}
        onConfirm={handleDismissConfirm}
      />
    </>
  );
};
