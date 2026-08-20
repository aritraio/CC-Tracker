import React from 'react';
import Link from 'next/link';

export interface BauhausLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showSubtitle?: boolean;
}

export const BauhausLogo: React.FC<BauhausLogoProps> = ({
  size = 'md',
  showSubtitle = true,
}) => {
  const shapeSizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl',
  };

  return (
    <Link href="/" className="inline-flex items-center gap-3 group select-none">
      {/* 3 Primitives */}
      <div className="flex items-center gap-1.5" aria-hidden="true">
        {/* Red Circle */}
        <div
          className={`${shapeSizes[size]} rounded-full bg-bauhaus-red border-2 border-black shadow-[2px_2px_0px_0px_#121212] group-hover:scale-110 transition-transform`}
        />
        {/* Blue Square */}
        <div
          className={`${shapeSizes[size]} rounded-none bg-bauhaus-blue border-2 border-black shadow-[2px_2px_0px_0px_#121212] group-hover:rotate-12 transition-transform`}
        />
        {/* Yellow Triangle */}
        <div
          className={`${shapeSizes[size]} bg-bauhaus-yellow bauhaus-clip-triangle group-hover:-translate-y-1 transition-transform`}
        />
      </div>

      {/* Wordmark */}
      <div className="flex flex-col">
        <span
          className={`font-black uppercase tracking-tighter text-ink ${textSizes[size]} leading-none`}
        >
          CC TRACK
        </span>
        {showSubtitle && (
          <span className="font-bold text-[9px] uppercase tracking-[0.25em] text-ink/80 leading-tight mt-0.5">
            Spending Intelligence
          </span>
        )}
      </div>
    </Link>
  );
};
