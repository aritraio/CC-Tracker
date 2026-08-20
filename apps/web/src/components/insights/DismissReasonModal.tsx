'use client';

import React, { useState } from 'react';
import { DismissReason, Recommendation } from '@/types';
import { Button } from '@/components/ui/button';
import { X, HelpCircle, XCircle, AlertCircle } from 'lucide-react';

export interface DismissReasonModalProps {
  isOpen: boolean;
  recommendation: Recommendation | null;
  onClose: () => void;
  onConfirm: (reason: DismissReason, notes?: string) => void;
}

const DISMISS_OPTIONS: Array<{
  id: DismissReason;
  label: string;
  description: string;
}> = [
  {
    id: 'ALREADY_PLANNED',
    label: 'Already planned or completed',
    description: 'I have already cancelled or budgeted for this item.',
  },
  {
    id: 'NOT_APPLICABLE',
    label: 'Not applicable to my lifestyle',
    description: 'This recommendation does not fit my spending preferences.',
  },
  {
    id: 'TOO_RESTRICTIVE',
    label: 'Too restrictive or impractical',
    description: 'The proposed reduction is unrealistic for my routine.',
  },
  {
    id: 'CANNOT_REDUCE',
    label: 'Essential expense / Fixed commitment',
    description: 'This is a mandatory cost (e.g. rent, medical, school).',
  },
  {
    id: 'OTHER',
    label: 'Other reason',
    description: 'Provide custom feedback below.',
  },
];

export const DismissReasonModal: React.FC<DismissReasonModalProps> = ({
  isOpen,
  recommendation,
  onClose,
  onConfirm,
}) => {
  const [selectedReason, setSelectedReason] = useState<DismissReason>('NOT_APPLICABLE');
  const [customNotes, setCustomNotes] = useState<string>('');

  if (!isOpen || !recommendation) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onConfirm(selectedReason, customNotes.trim() || undefined);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink/75 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-white border-4 border-black p-6 sm:p-7 shadow-bauhaus-xl max-w-lg w-full relative animate-in zoom-in-95 duration-150"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-headline"
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 bg-muted hover:bg-black hover:text-white border-2 border-black transition-colors"
          aria-label="Close dialog"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-9 h-9 bg-bauhaus-red text-white border-2 border-black flex items-center justify-center shadow-bauhaus-xs shrink-0">
            <XCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 id="modal-headline" className="text-xl font-black uppercase tracking-tight text-ink">
              Dismiss Recommendation
            </h3>
            <p className="text-xs font-mono text-ink/70">
              Help calibrate future behavioral advice
            </p>
          </div>
        </div>

        {/* Target Recommendation Badge */}
        <div className="bg-canvas border-2 border-black p-3 mb-5 font-mono text-xs">
          <span className="block text-[10px] uppercase font-bold text-ink/60">
            Recommendation:
          </span>
          <span className="font-bold text-ink text-sm">
            {recommendation.title}
          </span>
          {recommendation.target_category && (
            <span className="inline-block mt-1 px-1.5 py-0.2 bg-muted text-ink border border-black font-bold text-[10px]">
              {recommendation.target_category}
            </span>
          )}
        </div>

        {/* Form Options */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-ink">
              Why are you dismissing this?
            </label>
            <div className="space-y-2">
              {DISMISS_OPTIONS.map((opt) => (
                <label
                  key={opt.id}
                  className={`flex items-start gap-3 p-2.5 border-2 border-black cursor-pointer transition-all ${
                    selectedReason === opt.id
                      ? 'bg-bauhaus-yellow-light shadow-bauhaus-xs border-black'
                      : 'bg-white hover:bg-muted/40'
                  }`}
                >
                  <input
                    type="radio"
                    name="dismiss_reason"
                    value={opt.id}
                    checked={selectedReason === opt.id}
                    onChange={() => setSelectedReason(opt.id)}
                    className="mt-0.5 accent-black h-4 w-4 shrink-0"
                  />
                  <div className="text-xs leading-snug">
                    <span className="font-bold text-ink block">{opt.label}</span>
                    <span className="text-[11px] text-ink/70">{opt.description}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Optional Notes */}
          <div>
            <label
              htmlFor="dismiss-notes"
              className="block text-xs font-bold uppercase tracking-wider text-ink mb-1"
            >
              Additional Feedback (Optional)
            </label>
            <textarea
              id="dismiss-notes"
              value={customNotes}
              onChange={(e) => setCustomNotes(e.target.value)}
              rows={2}
              maxLength={300}
              placeholder="e.g., I need this cloud subscription for work projects..."
              className="w-full border-2 border-black p-2 text-xs font-mono bg-white focus:outline-hidden focus:ring-2 focus:ring-black"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t-2 border-black">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onClose}
              className="text-xs px-4"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              className="text-xs px-4 bg-bauhaus-red hover:bg-bauhaus-red-dark text-white border-2 border-black"
            >
              <XCircle className="w-3.5 h-3.5 mr-1" />
              <span>Confirm Dismissal</span>
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
