'use client';

import React from 'react';
import {
  CheckCircle2,
  Loader2,
  AlertTriangle,
  FileSearch,
  Scale,
  Tags,
  Sparkles,
  Lock,
} from 'lucide-react';

export type ProcessingStepId =
  | 'unlocking'
  | 'extracting'
  | 'reconciling'
  | 'categorizing'
  | 'synthesizing';

export interface StepItem {
  id: ProcessingStepId;
  label: string;
  subtext: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const PROCESSING_STEPS: StepItem[] = [
  {
    id: 'unlocking',
    label: '1. Unlocking (Client)',
    subtext: 'Verifying client-side buffer in browser memory',
    icon: Lock,
  },
  {
    id: 'extracting',
    label: '2. Extracting Tables',
    subtext: 'Parsing multi-page PDF line items & coordinates',
    icon: FileSearch,
  },
  {
    id: 'reconciling',
    label: '3. Reconciling Dues',
    subtext: 'Verifying mathematical balance against statement summary',
    icon: Scale,
  },
  {
    id: 'categorizing',
    label: '4. Categorizing',
    subtext: 'Normalizing merchants & 3-tier classification',
    icon: Tags,
  },
  {
    id: 'synthesizing',
    label: '5. Synthesizing Intelligence',
    subtext: 'Detecting 10 anomalies & generating recommendations',
    icon: Sparkles,
  },
];

export interface ProcessingProgressProps {
  currentStep: ProcessingStepId;
  stepIndex: number;
  totalSteps?: number;
  isError?: boolean;
  errorMessage?: string;
  onRetry?: () => void;
}

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({
  currentStep,
  stepIndex,
  totalSteps = 5,
  isError = false,
  errorMessage,
  onRetry,
}) => {
  const percentComplete = Math.min(100, Math.round(((stepIndex + 1) / totalSteps) * 100));

  return (
    <div className="w-full bg-paper border-4 border-black shadow-[8px_8px_0px_0px_#121212] p-6 md:p-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 mb-6 border-b-4 border-black">
        <div className="flex items-center gap-3">
          <div className="w-4 h-4 rounded-full bg-bauhaus-red border-2 border-black" />
          <h3 className="font-black uppercase tracking-tight text-xl text-ink">
            {isError ? 'Processing Interrupted' : 'Parsing Statement in RAM'}
          </h3>
        </div>
        <div className="font-mono font-bold text-sm bg-bauhaus-yellow px-3 py-1 border-2 border-black shadow-[2px_2px_0px_0px_#121212] self-start sm:self-auto">
          {isError ? 'ERROR' : `${percentComplete}% COMPLETED`}
        </div>
      </div>

      {/* Stepped Progress Indicator */}
      <div className="space-y-3 mb-6">
        {PROCESSING_STEPS.map((step, idx) => {
          const isCurrent = step.id === currentStep && !isError;
          const isCompleted = idx < stepIndex || (idx === stepIndex && !isError && stepIndex === totalSteps - 1);
          const isFailed = step.id === currentStep && isError;
          const IconComponent = step.icon;

          let blockStyle = 'bg-canvas text-ink/60 border-2 border-black/30';
          if (isCompleted) {
            blockStyle = 'bg-bauhaus-blue text-white border-2 md:border-4 border-black shadow-[2px_2px_0px_0px_#121212]';
          } else if (isCurrent) {
            blockStyle = 'bg-bauhaus-yellow text-ink border-2 md:border-4 border-black shadow-[4px_4px_0px_0px_#121212] animate-pulse';
          } else if (isFailed) {
            blockStyle = 'bg-bauhaus-red text-white border-2 md:border-4 border-black shadow-[4px_4px_0px_0px_#121212]';
          }

          return (
            <div
              key={step.id}
              className={`p-3.5 flex items-center justify-between transition-all duration-200 ${blockStyle}`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`p-1.5 border-2 border-black ${
                    isCompleted
                      ? 'bg-white text-bauhaus-blue'
                      : isCurrent
                      ? 'bg-white text-ink'
                      : isFailed
                      ? 'bg-white text-bauhaus-red'
                      : 'bg-paper text-ink/40'
                  }`}
                >
                  <IconComponent className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-black uppercase tracking-tight text-xs sm:text-sm">
                    {step.label}
                  </h4>
                  <p
                    className={`text-[11px] font-medium leading-tight ${
                      isCompleted ? 'text-white/85' : isFailed ? 'text-white/90' : 'text-ink/70'
                    }`}
                  >
                    {step.subtext}
                  </p>
                </div>
              </div>

              <div className="shrink-0 ml-2">
                {isCompleted && <CheckCircle2 className="w-5 h-5 text-white" />}
                {isCurrent && <Loader2 className="w-5 h-5 animate-spin text-ink" />}
                {isFailed && <AlertTriangle className="w-5 h-5 text-white" />}
              </div>
            </div>
          );
        })}
      </div>

      {/* Error Message & Retry CTA */}
      {isError && (
        <div className="p-4 bg-bauhaus-red/10 border-4 border-bauhaus-red text-ink mb-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-bauhaus-red shrink-0 mt-0.5" />
            <div>
              <h5 className="font-black uppercase text-sm text-bauhaus-red">Processing Error</h5>
              <p className="text-xs font-medium text-ink/80 mt-1">
                {errorMessage || 'Failed to parse statement. Please ensure the document is a supported PDF credit card statement.'}
              </p>
            </div>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-4 px-4 py-2 bg-bauhaus-red text-white font-bold uppercase text-xs border-2 border-black shadow-[2px_2px_0px_0px_#121212] hover:bg-bauhaus-red-hover transition-colors"
            >
              Try Again
            </button>
          )}
        </div>
      )}

      {/* Ephemeral Notice */}
      <div className="text-center">
        <p className="text-[11px] font-mono text-ink/60 uppercase tracking-wider">
          ● Ephemeral Processing: Zero disk writes • Decrypted in RAM • Destroyed on complete
        </p>
      </div>
    </div>
  );
};
