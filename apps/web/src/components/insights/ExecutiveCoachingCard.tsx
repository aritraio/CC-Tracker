'use client';

import React from 'react';
import { LLMExplanationResult } from '@/types';
import { Sparkles, CheckCircle, ArrowRight, ShieldCheck, Flame, Clock } from 'lucide-react';

export interface ExecutiveCoachingCardProps {
  explanation: LLMExplanationResult;
}

export const ExecutiveCoachingCard: React.FC<ExecutiveCoachingCardProps> = ({
  explanation,
}) => {
  const { executive_summary, what_stands_out, action_steps, generated_by, is_fallback } =
    explanation;

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case 'Immediate Action':
        return 'bg-bauhaus-red text-white';
      case 'This Month':
        return 'bg-bauhaus-yellow text-ink';
      case 'Good Habit':
      default:
        return 'bg-bauhaus-green text-white';
    }
  };

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 sm:p-7 relative">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-black gap-3 mb-5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-bauhaus-yellow text-ink border-2 border-black flex items-center justify-center shadow-bauhaus-xs">
            <Sparkles className="w-4 h-4 text-ink" />
          </div>
          <div>
            <h3 className="font-black uppercase tracking-tight text-xl text-ink">
              Executive Spending Intelligence
            </h3>
            <span className="text-[10px] font-mono font-bold uppercase text-ink/60">
              Deterministic Analytics + Structured Fact Explanation
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-canvas border border-black font-mono text-[10px] font-bold text-ink/75">
            {generated_by}
          </span>
        </div>
      </div>

      {/* Narrative Executive Summary */}
      <div className="bg-canvas border-2 border-black p-4 sm:p-5 mb-6">
        <p className="text-sm sm:text-base font-medium text-ink leading-relaxed">
          {executive_summary}
        </p>
      </div>

      {/* Two Column Grid: What Stands Out & Action Steps */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: What Stands Out (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-bold uppercase tracking-widest text-ink/70 flex items-center gap-1.5 pb-1 border-b border-black/20">
            <Flame className="w-3.5 h-3.5 text-bauhaus-red" />
            <span>Key Observations</span>
          </div>

          <div className="space-y-2.5">
            {what_stands_out.map((item, idx) => (
              <div
                key={idx}
                className="bg-paper border-2 border-black p-3 shadow-bauhaus-xs"
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-black text-xs uppercase text-ink tracking-tight">
                    {item.finding_title}
                  </span>
                  <span
                    className={`px-1.5 py-0.2 text-[9px] font-mono font-bold uppercase border border-black shrink-0 ${getUrgencyBadge(
                      item.urgency
                    )}`}
                  >
                    {item.urgency}
                  </span>
                </div>
                <p className="text-xs text-ink/80 leading-snug">{item.observation}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: 3-Step Action Roadmap (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <div className="text-xs font-bold uppercase tracking-widest text-ink/70 flex items-center gap-1.5 pb-1 border-b border-black/20">
            <Clock className="w-3.5 h-3.5 text-bauhaus-blue" />
            <span>3-Step Action Plan</span>
          </div>

          <div className="space-y-3">
            {action_steps.map((step) => (
              <div
                key={step.step_number}
                className="bg-paper border-2 border-black p-3.5 shadow-bauhaus-xs flex items-start gap-3"
              >
                <div className="w-7 h-7 bg-bauhaus-blue text-white font-mono font-black text-xs flex items-center justify-center border border-black shrink-0">
                  {step.step_number}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <h5 className="font-bold text-xs uppercase text-ink tracking-tight truncate">
                      {step.title}
                    </h5>
                    {step.estimated_impact && (
                      <span className="font-mono font-black text-[10px] bg-bauhaus-yellow px-1.5 py-0.5 border border-black shrink-0">
                        {step.estimated_impact}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-ink/75 leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
