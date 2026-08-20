'use client';

import React, { useState } from 'react';
import {
  BANK_PASSWORD_HINTS,
  BankPasswordHint,
} from '@/lib/pdf-unlocker';
import { Button } from '@/components/ui/button';
import {
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  AlertCircle,
  X,
  Info,
} from 'lucide-react';

export interface PasswordModalProps {
  isOpen: boolean;
  fileName: string;
  detectedBankCode?: 'HDFC' | 'ICICI' | 'SBI' | 'AXIS' | 'AMEX' | 'OTHER';
  onUnlock: (password: string) => Promise<void>;
  onCancel: () => void;
  errorMessage?: string | null;
  isUnlocking?: boolean;
}

export const PasswordModal: React.FC<PasswordModalProps> = ({
  isOpen,
  fileName,
  detectedBankCode = 'HDFC',
  onUnlock,
  onCancel,
  errorMessage,
  isUnlocking = false,
}) => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [selectedBank, setSelectedBank] = useState<string>(detectedBankCode);

  if (!isOpen) return null;

  const currentHint =
    BANK_PASSWORD_HINTS.find((b) => b.code === selectedBank) ||
    BANK_PASSWORD_HINTS[0];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim() || isUnlocking) return;
    await onUnlock(password.trim());
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-none animate-in fade-in duration-150">
      {/* Bauhaus Modal Container */}
      <div className="relative w-full max-w-lg bg-paper border-4 border-black shadow-[10px_10px_0px_0px_#121212] overflow-hidden">
        {/* Modal Header Banner */}
        <div className="bg-bauhaus-blue text-white p-4 border-b-4 border-black flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-bauhaus-yellow border-2 border-black" />
            <h3 className="font-black uppercase tracking-tight text-lg">
              Password-Protected Statement
            </h3>
          </div>
          <button
            onClick={onCancel}
            disabled={isUnlocking}
            className="p-1 text-white hover:bg-black/20 transition-colors focus:outline-none"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {/* Privacy Guarantee Eyebrow */}
          <div className="flex items-center gap-2 bg-bauhaus-yellow-light p-3 border-2 border-black mb-5 shadow-[2px_2px_0px_0px_#121212]">
            <ShieldCheck className="w-5 h-5 text-bauhaus-blue shrink-0" />
            <p className="text-xs font-bold text-ink leading-tight">
              100% Client-Side Decryption. Your password is processed purely in browser memory
              and is <span className="underline">never sent over the network</span>.
            </p>
          </div>

          <p className="text-sm font-medium text-ink/80 mb-4">
            <span className="font-bold text-ink">File:</span> {fileName}
          </p>

          {/* Bank Selector Tabs */}
          <div className="mb-4">
            <label className="block text-xs font-bold uppercase tracking-widest text-ink/70 mb-1.5">
              Select Your Issuing Bank For Password Hint
            </label>
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-1 border-2 border-black p-1 bg-canvas">
              {BANK_PASSWORD_HINTS.map((hint) => (
                <button
                  key={hint.code}
                  type="button"
                  onClick={() => setSelectedBank(hint.code)}
                  className={`py-1.5 px-2 text-xs font-bold uppercase transition-all ${
                    selectedBank === hint.code
                      ? 'bg-bauhaus-red text-white border-2 border-black shadow-[2px_2px_0px_0px_#121212]'
                      : 'bg-paper text-ink hover:bg-muted'
                  }`}
                >
                  {hint.code}
                </button>
              ))}
            </div>
          </div>

          {/* Contextual Password Formula Box */}
          <div className="bg-canvas border-2 border-black p-3.5 mb-5">
            <div className="flex items-center gap-1.5 mb-1 text-xs font-bold uppercase tracking-wider text-bauhaus-blue">
              <Info className="w-4 h-4 shrink-0" />
              <span>{currentHint.bankName} Formula</span>
            </div>
            <p className="text-xs font-bold text-ink mb-1">{currentHint.format}</p>
            <p className="text-xs text-ink/80 font-mono bg-paper px-2 py-1 border border-black/30 inline-block mb-1">
              Example: {currentHint.example}
            </p>
            <p className="text-[11px] text-ink/70 italic">{currentHint.notes}</p>
          </div>

          {/* Password Input Field */}
          <div className="mb-6">
            <label
              htmlFor="statement-password"
              className="block text-xs font-bold uppercase tracking-widest text-ink mb-2"
            >
              Enter Statement Password
            </label>
            <div className="relative">
              <input
                id="statement-password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="e.g. ROHA1504"
                disabled={isUnlocking}
                autoFocus
                className="w-full bg-paper border-4 border-black px-4 py-3 font-mono text-lg font-bold tracking-widest text-ink placeholder:text-ink/30 placeholder:font-sans placeholder:text-sm placeholder:tracking-normal focus:outline-none focus:ring-4 focus:ring-bauhaus-yellow shadow-[4px_4px_0px_0px_#121212]"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-ink/70 hover:text-ink transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>

            {/* Error Message */}
            {errorMessage && (
              <div className="flex items-center gap-2 mt-3 p-2.5 bg-bauhaus-red/10 border-2 border-bauhaus-red text-bauhaus-red text-xs font-bold animate-in fade-in">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>
                  {errorMessage === 'INCORRECT_PASSWORD'
                    ? 'Incorrect password. Please verify the formula above and try again.'
                    : errorMessage}
                </span>
              </div>
            )}
          </div>

          {/* Modal Actions */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <Button
              type="submit"
              variant="yellow"
              size="lg"
              disabled={!password.trim() || isUnlocking}
              className="w-full sm:flex-1 justify-center gap-2"
            >
              <Lock className="w-4 h-4" />
              <span>{isUnlocking ? 'Unlocking in RAM...' : 'Unlock & Process'}</span>
            </Button>
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={onCancel}
              disabled={isUnlocking}
              className="w-full sm:w-auto"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
