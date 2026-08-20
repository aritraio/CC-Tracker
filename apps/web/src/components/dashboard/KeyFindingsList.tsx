'use client';

import React, { useState } from 'react';
import { AnomalyDetectionResult, Finding, FindingSeverity } from '@/types';
import { formatINR, formatPercent } from '@/lib/formatters';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  ChevronDown,
  ChevronUp,
  Flame,
  Zap,
  Tag,
  Store,
  Layers,
} from 'lucide-react';

export interface KeyFindingsListProps {
  anomalies: AnomalyDetectionResult;
  onFilterCategory?: (category: string) => void;
}

export const KeyFindingsList: React.FC<KeyFindingsListProps> = ({
  anomalies,
  onFilterCategory,
}) => {
  const [selectedSeverity, setSelectedSeverity] = useState<FindingSeverity | 'ALL'>('ALL');
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const getSeverityBadge = (severity: FindingSeverity) => {
    switch (severity) {
      case 'CRITICAL':
        return {
          bg: 'bg-bauhaus-red text-white',
          icon: <Flame className="w-3.5 h-3.5" />,
          label: 'CRITICAL',
        };
      case 'HIGH':
        return {
          bg: 'bg-bauhaus-red text-white',
          icon: <AlertTriangle className="w-3.5 h-3.5" />,
          label: 'HIGH SEVERITY',
        };
      case 'MEDIUM':
        return {
          bg: 'bg-bauhaus-yellow text-ink',
          icon: <AlertCircle className="w-3.5 h-3.5" />,
          label: 'MEDIUM',
        };
      case 'LOW':
        return {
          bg: 'bg-muted text-ink',
          icon: <Info className="w-3.5 h-3.5" />,
          label: 'LOW',
        };
      case 'INFO':
      default:
        return {
          bg: 'bg-bauhaus-blue text-white',
          icon: <Info className="w-3.5 h-3.5" />,
          label: 'INFORMATIONAL',
        };
    }
  };

  const filteredFindings = anomalies.findings.filter(
    (f) => selectedSeverity === 'ALL' || f.severity === selectedSeverity
  );

  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6">
      {/* Header & Severity Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-black gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-bauhaus-red" />
            <h3 className="font-black uppercase tracking-tight text-xl text-ink">
              Detected Spending Patterns & Anomalies
            </h3>
          </div>
          <p className="text-xs text-ink/75 font-medium mt-0.5">
            10 deterministic statistical & behavioral anomaly detectors audited your statements.
          </p>
        </div>

        {/* Severity Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 font-mono text-xs font-bold">
          <button
            onClick={() => setSelectedSeverity('ALL')}
            className={`px-2.5 py-1 border border-black transition-all ${
              selectedSeverity === 'ALL'
                ? 'bg-bauhaus-yellow text-ink shadow-bauhaus-xs'
                : 'bg-canvas text-ink/70 hover:text-ink'
            }`}
          >
            All ({anomalies.total_findings_count})
          </button>
          {anomalies.critical_count > 0 && (
            <button
              onClick={() => setSelectedSeverity('CRITICAL')}
              className={`px-2 py-1 border border-black transition-all ${
                selectedSeverity === 'CRITICAL'
                  ? 'bg-bauhaus-red text-white shadow-bauhaus-xs'
                  : 'bg-canvas text-bauhaus-red'
              }`}
            >
              Critical ({anomalies.critical_count})
            </button>
          )}
          {anomalies.high_count > 0 && (
            <button
              onClick={() => setSelectedSeverity('HIGH')}
              className={`px-2 py-1 border border-black transition-all ${
                selectedSeverity === 'HIGH'
                  ? 'bg-bauhaus-red text-white shadow-bauhaus-xs'
                  : 'bg-canvas text-bauhaus-red'
              }`}
            >
              High ({anomalies.high_count})
            </button>
          )}
          {anomalies.medium_count > 0 && (
            <button
              onClick={() => setSelectedSeverity('MEDIUM')}
              className={`px-2 py-1 border border-black transition-all ${
                selectedSeverity === 'MEDIUM'
                  ? 'bg-bauhaus-yellow text-ink shadow-bauhaus-xs'
                  : 'bg-canvas text-ink/80'
              }`}
            >
              Med ({anomalies.medium_count})
            </button>
          )}
        </div>
      </div>

      {/* Findings List */}
      {filteredFindings.length === 0 ? (
        <div className="p-8 text-center bg-canvas border-2 border-dashed border-black">
          <Info className="w-8 h-8 text-ink/40 mx-auto mb-2" />
          <p className="text-sm font-bold text-ink">
            No findings matching severity &quot;{selectedSeverity}&quot;.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredFindings.map((finding) => {
            const badge = getSeverityBadge(finding.severity);
            const isExpanded = expandedIds.has(finding.id);

            return (
              <div
                key={finding.id}
                className="border-2 md:border-3 border-black bg-paper shadow-bauhaus-xs transition-all duration-100 hover:shadow-bauhaus-sm"
              >
                {/* Finding Header Strip */}
                <div
                  onClick={() => toggleExpand(finding.id)}
                  className="p-3.5 sm:p-4 flex items-start sm:items-center justify-between gap-3 cursor-pointer select-none bg-canvas hover:bg-bauhaus-yellow-light transition-colors"
                >
                  <div className="flex items-start sm:items-center gap-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] sm:text-xs font-mono font-black uppercase border border-black shrink-0 ${badge.bg}`}
                    >
                      {badge.icon}
                      <span>{badge.label}</span>
                    </span>

                    <div>
                      <h4 className="font-bold text-sm sm:text-base text-ink uppercase tracking-tight">
                        {finding.title}
                      </h4>
                      <p className="text-xs text-ink/75 font-medium mt-0.5 line-clamp-1 sm:line-clamp-none">
                        {finding.description}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 sm:gap-3 shrink-0">
                    {finding.impact_amount && (
                      <span className="font-mono font-black text-xs sm:text-sm text-bauhaus-red bg-white px-2 py-0.5 border border-black shadow-bauhaus-xs">
                        {formatINR(finding.impact_amount)}
                      </span>
                    )}

                    <button
                      type="button"
                      aria-label="Toggle finding details"
                      className="p-1 border border-black bg-white hover:bg-muted"
                    >
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-ink" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-ink" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Expanded Detailed Evidence Panel */}
                {isExpanded && (
                  <div className="p-4 border-t-2 border-black bg-white space-y-3 font-mono text-xs animate-in fade-in duration-100">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-muted/40 p-3 border border-black">
                      <div>
                        <span className="block text-[10px] font-bold uppercase text-ink/60">
                          Observed Value
                        </span>
                        <span className="font-black text-sm text-ink">
                          {String(finding.evidence.current_value)}
                        </span>
                      </div>

                      {finding.evidence.threshold_or_baseline && (
                        <div>
                          <span className="block text-[10px] font-bold uppercase text-ink/60">
                            Baseline / Threshold
                          </span>
                          <span className="font-bold text-sm text-ink">
                            {String(finding.evidence.threshold_or_baseline)}
                          </span>
                        </div>
                      )}

                      {finding.evidence.delta_percentage !== undefined &&
                        finding.evidence.delta_percentage !== null && (
                          <div>
                            <span className="block text-[10px] font-bold uppercase text-ink/60">
                              Variance Delta
                            </span>
                            <span className="font-black text-sm text-bauhaus-red">
                              +{finding.evidence.delta_percentage.toFixed(1)}% Spike
                            </span>
                          </div>
                        )}
                    </div>

                    {/* Associated Category & Merchants */}
                    <div className="flex flex-wrap items-center gap-2 pt-1 font-sans">
                      {finding.evidence.related_category && (
                        <span
                          onClick={() =>
                            onFilterCategory?.(finding.evidence.related_category!)
                          }
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-bauhaus-blue text-white text-xs font-bold uppercase border border-black cursor-pointer hover:bg-bauhaus-blue-hover"
                        >
                          <Tag className="w-3 h-3" />
                          <span>Category: {finding.evidence.related_category}</span>
                        </span>
                      )}

                      {finding.evidence.related_merchants &&
                        finding.evidence.related_merchants.map((m) => (
                          <span
                            key={m}
                            className="inline-flex items-center gap-1 px-2 py-1 bg-canvas text-ink text-xs font-bold border border-black"
                          >
                            <Store className="w-3 h-3 text-ink/60" />
                            <span>{m}</span>
                          </span>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
