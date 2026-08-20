'use client';

import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getBackendHealth, HealthStatus } from '@/lib/api';
import { DropZone } from '@/components/upload/DropZone';
import { InsightsDashboard } from '@/components/dashboard/InsightsDashboard';
import { SAMPLE_STATEMENT_DATA } from '@/lib/sample-data';
import { ParseStatementResponse } from '@/types';
import {
  ShieldCheck,
  FileSpreadsheet,
  Calculator,
  Sparkles,
  ArrowRight,
  Upload,
  Lock,
  RotateCcw,
  Play,
  Eye,
  CheckCircle2,
  TrendingDown,
} from 'lucide-react';

export default function HomePage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [parsedStatement, setParsedStatement] = useState<ParseStatementResponse | null>(null);

  useEffect(() => {
    getBackendHealth()
      .then((data) => setHealth(data))
      .catch(() => setHealth(null))
      .finally(() => setLoadingHealth(false));
  }, []);

  const handleStatementParsed = (data: ParseStatementResponse) => {
    setParsedStatement(data);
    setTimeout(() => {
      const summaryEl = document.getElementById('dashboard-view');
      summaryEl?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleLoadDemo = () => {
    setParsedStatement(SAMPLE_STATEMENT_DATA);
    setTimeout(() => {
      const summaryEl = document.getElementById('dashboard-view');
      summaryEl?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleReset = () => {
    setParsedStatement(null);
    const dropzone = document.getElementById('dropzone');
    dropzone?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="flex flex-col">
      {/* 1. HERO SECTION */}
      <section className="border-b-2 md:border-b-4 border-black bg-canvas">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 border-x-0 lg:border-x-4 border-black">
          {/* Left Hero Column (7 Cols) */}
          <div className="lg:col-span-7 p-6 sm:p-10 md:p-14 lg:p-16 flex flex-col justify-between border-b-4 lg:border-b-0 lg:border-r-4 border-black bg-paper">
            <div>
              <div className="inline-flex items-center gap-2 mb-6 flex-wrap">
                <Badge variant="yellow" className="text-xs">
                  STAGE 1: MVP OPERATIONAL
                </Badge>
                <Badge variant="outline" className="text-xs">
                  HDFC • ICICI • SBI • AXIS • AMEX
                </Badge>
              </div>

              <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter text-ink leading-[0.88] mb-8">
                DISSECT <br />
                YOUR SPEND <br />
                <span className="text-bauhaus-red">WITH RIGOR.</span>
              </h1>

              <p className="text-base sm:text-lg md:text-xl text-ink/80 font-medium leading-relaxed max-w-xl mb-10">
                Transform unstructured PDF credit card statements into reconciled,
                mathematically verified transactions with zero password transmission and
                deterministic spending intelligence.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-4 pt-4">
              <Button
                variant="primary"
                size="lg"
                className="gap-2"
                onClick={() => {
                  const dropzone = document.getElementById('dropzone');
                  dropzone?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                <Upload className="w-5 h-5" />
                <span>Upload Statement</span>
              </Button>

              <Button
                variant="yellow"
                size="lg"
                className="gap-2"
                onClick={handleLoadDemo}
              >
                <Eye className="w-5 h-5" />
                <span>Explore Demo Report</span>
              </Button>

              <Button
                variant="outline"
                size="lg"
                className="gap-2"
                onClick={() => {
                  window.open('http://localhost:8000/api/v1/docs', '_blank');
                }}
              >
                <span>API Docs</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Right Hero Column: Bauhaus Composition (5 Cols) */}
          <div className="lg:col-span-5 bg-bauhaus-blue p-8 sm:p-12 flex flex-col justify-between relative overflow-hidden text-white">
            <div className="absolute top-0 right-0 w-48 h-48 bg-white/10 rounded-full -mr-16 -mt-16 pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-36 h-36 bg-bauhaus-yellow/20 bauhaus-clip-triangle -ml-12 -mb-12 pointer-events-none" />

            <div className="relative z-10">
              <div className="text-xs font-bold uppercase tracking-widest text-bauhaus-yellow mb-2">
                SYSTEM TELEMETRY
              </div>
              <h2 className="text-2xl sm:text-3xl font-black uppercase tracking-tight leading-tight">
                BACKEND STATUS & AUDIT RUNTIME
              </h2>
            </div>

            {/* Live Backend Connection Card */}
            <div className="bg-white text-ink border-4 border-black shadow-bauhaus-md p-6 my-8 relative z-10">
              <div className="flex items-center justify-between mb-4 border-b-2 border-black pb-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-3 h-3 rounded-full border border-black ${
                      health?.status === 'healthy'
                        ? 'bg-bauhaus-green animate-ping'
                        : 'bg-bauhaus-red'
                    }`}
                  />
                  <span className="font-bold text-xs uppercase tracking-wider">
                    FASTAPI ENGINE (RAM WORKER)
                  </span>
                </div>
                <Badge variant={health?.status === 'healthy' ? 'green' : 'red'}>
                  {loadingHealth
                    ? 'CONNECTING...'
                    : health?.status === 'healthy'
                    ? 'OPERATIONAL'
                    : 'OFFLINE'}
                </Badge>
              </div>

              <div className="space-y-2 font-mono text-xs">
                <div className="flex justify-between">
                  <span className="text-ink/60">Service:</span>
                  <span className="font-bold">{health?.service || 'CC Track API'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink/60">Version:</span>
                  <span className="font-bold">{health?.version || '0.1.0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink/60">Environment:</span>
                  <span className="font-bold uppercase">
                    {health?.environment || 'Development'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink/60">Decryption Mode:</span>
                  <span className="font-bold text-bauhaus-blue">
                    Client-Side WebAssembly (pdf.js)
                  </span>
                </div>
              </div>
            </div>

            <div className="text-xs font-mono text-white/90 relative z-10 flex items-center gap-2">
              <Lock className="w-4 h-4 text-bauhaus-yellow" />
              <span>Zero credentials or unencrypted PDF files written to disk.</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. SOLID BAUHAUS YELLOW STATS RIBBON */}
      <section className="bg-bauhaus-yellow border-b-4 border-black text-ink py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-center sm:text-left divide-y-2 sm:divide-y-0 sm:divide-x-2 divide-black">
          <div className="px-4 py-2">
            <div className="text-4xl font-black font-mono tracking-tight">100%</div>
            <div className="text-xs font-bold uppercase tracking-widest mt-1">
              Mathematical Balance Reconciliation
            </div>
          </div>

          <div className="px-4 py-2">
            <div className="text-4xl font-black font-mono tracking-tight">0 BYTES</div>
            <div className="text-xs font-bold uppercase tracking-widest mt-1">
              Password Sent Over Network
            </div>
          </div>

          <div className="px-4 py-2">
            <div className="text-4xl font-black font-mono tracking-tight">5 MAJOR</div>
            <div className="text-xs font-bold uppercase tracking-widest mt-1">
              Supported Indian Card Issuers
            </div>
          </div>

          <div className="px-4 py-2">
            <div className="text-4xl font-black font-mono tracking-tight">&lt; 0.5s</div>
            <div className="text-xs font-bold uppercase tracking-widest mt-1">
              In-Memory Vectorized Parsing
            </div>
          </div>
        </div>
      </section>

      {/* 3. STATEMENT DROPZONE WORKSPACE */}
      <section id="dropzone" className="py-16 md:py-24 px-4 sm:px-6 lg:px-8 bg-canvas">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <Badge variant="blue" className="mb-3">
              CLIENT-SIDE SECURE INGESTION
            </Badge>
            <h2 className="text-3xl sm:text-5xl font-black uppercase tracking-tight text-ink">
              DROP YOUR STATEMENT PDF
            </h2>
            <p className="text-base text-ink/75 font-medium mt-2">
              Password-protected statements are unlocked directly in your browser using{' '}
              <span className="font-bold text-ink">pdf.js</span> before RAM processing.
            </p>
          </div>

          {/* Interactive Bauhaus DropZone Component */}
          <DropZone onStatementParsed={handleStatementParsed} />

          {/* Quick Demo Trigger */}
          <div className="mt-8 text-center">
            <span className="text-xs font-bold uppercase tracking-wider text-ink/60 mr-2">
              Don&apos;t have a statement handy?
            </span>
            <button
              onClick={handleLoadDemo}
              className="text-xs font-black uppercase tracking-widest text-bauhaus-blue underline hover:text-bauhaus-blue-hover"
            >
              Load Sample Reconciled Statement (₹45,230 HDFC)
            </button>
          </div>
        </div>
      </section>

      {/* 4. MASTER INSIGHTS DASHBOARD (Shown when statement is parsed or demo is loaded) */}
      {parsedStatement && (
        <section
          id="dashboard-view"
          className="py-12 md:py-16 px-4 sm:px-6 lg:px-8 bg-canvas border-y-4 border-black"
        >
          <div className="max-w-7xl mx-auto">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <Badge variant="yellow" className="mb-2">
                  FINANCIAL INTELLIGENCE ENGINE
                </Badge>
                <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-ink">
                  STATEMENT INSIGHTS & AUDIT DASHBOARD
                </h2>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                className="hidden sm:flex gap-1.5"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Upload New Statement</span>
              </Button>
            </div>

            <InsightsDashboard
              data={parsedStatement}
              onReset={handleReset}
              onShowTransactions={(category, merchants) => {
                console.log('Filter transactions for:', category, merchants);
              }}
            />
          </div>
        </section>
      )}

      {/* 5. ARCHITECTURAL PILLARS */}
      <section id="features" className="py-16 md:py-24 px-4 sm:px-6 lg:px-8 bg-paper border-t-4 border-black">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <div className="text-xs font-bold uppercase tracking-widest text-bauhaus-red mb-2">
              FOUNDATIONAL ARCHITECTURE
            </div>
            <h2 className="text-3xl sm:text-5xl font-black uppercase tracking-tight text-ink">
              FOUR PILLARS OF FINANCIAL INTEGRITY
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Card 1 */}
            <Card shapeCorner="circle">
              <CardHeader>
                <div className="w-10 h-10 bg-bauhaus-red text-white border-2 border-black flex items-center justify-center shadow-bauhaus-xs mb-3">
                  <Calculator className="w-5 h-5" />
                </div>
                <CardTitle>Mandatory Reconciliation</CardTitle>
                <CardDescription>
                  Extracted line-item totals are strictly verified against the
                  statement&apos;s printed summary dues. Any discrepancy (&gt; ₹1.00) flags
                  `REVIEW_REQUIRED`.
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Card 2 */}
            <Card shapeCorner="square">
              <CardHeader>
                <div className="w-10 h-10 bg-bauhaus-blue text-white border-2 border-black flex items-center justify-center shadow-bauhaus-xs mb-3">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <CardTitle>Zero-Knowledge Privacy</CardTitle>
                <CardDescription>
                  Password unlocking executes locally via client-side WebAssembly. Raw
                  passwords never touch the network or application logs.
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Card 3 */}
            <Card shapeCorner="triangle">
              <CardHeader>
                <div className="w-10 h-10 bg-bauhaus-yellow text-black border-2 border-black flex items-center justify-center shadow-bauhaus-xs mb-3">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <CardTitle>3-Tier Categorizer</CardTitle>
                <CardDescription>
                  Deterministic top-250 Indian merchant dictionary first, regex heuristic
                  rules second, and structured batch LLM fallback only when necessary.
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Card 4 */}
            <Card shapeCorner="circle">
              <CardHeader>
                <div className="w-10 h-10 bg-ink text-white border-2 border-black flex items-center justify-center shadow-bauhaus-xs mb-3">
                  <Sparkles className="w-5 h-5 text-bauhaus-yellow" />
                </div>
                <CardTitle>Evidence Savings</CardTitle>
                <CardDescription>
                  No generalized advice. Every recommendation references concrete user
                  transactions and calculates verifiable monthly ₹ savings.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
}
