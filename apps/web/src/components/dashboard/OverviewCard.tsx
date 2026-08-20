'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';

export interface OverviewCardProps {
  title: string;
  value: string;
  subtitle?: string;
  changePercent?: number;
  changeLabel?: string;
  shape: 'circle' | 'square' | 'triangle';
  icon?: LucideIcon;
  badgeText?: string;
  badgeVariant?: 'red' | 'blue' | 'yellow' | 'green' | 'black';
}

export const OverviewCard: React.FC<OverviewCardProps> = ({
  title,
  value,
  subtitle,
  changePercent,
  changeLabel,
  shape,
  icon: Icon,
  badgeText,
  badgeVariant = 'yellow',
}) => {
  const badgeColorMap = {
    red: 'bg-bauhaus-red text-white',
    blue: 'bg-bauhaus-blue text-white',
    yellow: 'bg-bauhaus-yellow text-ink',
    green: 'bg-bauhaus-green text-white',
    black: 'bg-ink text-white',
  };

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6 relative transition-transform duration-150 hover:-translate-y-1 flex flex-col justify-between">
      {/* Top Right Bauhaus Geometric Marker */}
      <div className="absolute top-4 right-4" aria-hidden="true">
        {shape === 'circle' && (
          <div className="w-4 h-4 rounded-full bg-bauhaus-red border-2 border-black" />
        )}
        {shape === 'square' && (
          <div className="w-4 h-4 rounded-none bg-bauhaus-blue border-2 border-black" />
        )}
        {shape === 'triangle' && (
          <div className="w-4 h-4 bg-bauhaus-yellow bauhaus-clip-triangle" />
        )}
      </div>

      <div>
        {/* Header Label */}
        <div className="flex items-center gap-2 mb-2 pr-6">
          {Icon && <Icon className="w-4 h-4 text-ink shrink-0" />}
          <span className="text-xs font-bold uppercase tracking-widest text-ink/75 truncate">
            {title}
          </span>
        </div>

        {/* Main Metric Value */}
        <div className="text-3xl sm:text-4xl font-black font-mono tracking-tight text-ink my-2 break-words">
          {value}
        </div>
      </div>

      {/* Footer / Subtitle & Badges */}
      <div>
        {/* Divider */}
        <div className="h-0.5 bg-black/30 my-3 w-full" />

        <div className="flex items-center justify-between gap-2 text-xs flex-wrap">
          {subtitle && (
            <span className="text-ink/80 font-medium truncate">{subtitle}</span>
          )}

          {badgeText && (
            <span
              className={`font-bold font-mono px-2 py-0.5 border-2 border-black text-[11px] shrink-0 ${badgeColorMap[badgeVariant]}`}
            >
              {badgeText}
            </span>
          )}

          {changePercent !== undefined && (
            <span
              className={`font-bold font-mono px-2 py-0.5 border-2 border-black text-[11px] shrink-0 ${
                changePercent > 0
                  ? 'bg-bauhaus-red text-white'
                  : 'bg-bauhaus-yellow text-ink'
              }`}
            >
              {changePercent > 0 ? `+${changePercent}%` : `${changePercent}%`}{' '}
              {changeLabel && <span className="opacity-80 font-normal">{changeLabel}</span>}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
