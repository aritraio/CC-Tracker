'use client';

import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getBackendHealth, HealthStatus } from '@/lib/api';
import {
  ShieldCheck,
  FileSpreadsheet,
  Calculator,
  Sparkles,
  ArrowRight,
  Upload,
  Lock,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';

export default function HomePage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  useEffect(() => {
    getBackendHealth()
      .then((data) => setHealth(data))
      .catch(() => setHealth(null))
      .finally(() => setLoadingHealth(false));
  }, []);

  return (
    <div className="flex flex-col">
      {/* 1. HERO SECTION */}
      <section className="border-b-2 md:border-b-4 border-black bg-canvas">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 border-x-0 lg:border-x-4 border-black">
          {/* Left Hero Column (7 Cols) */}
          <div className="lg:col-span-7 p-6 sm:p-10 md:p-14 lg:p-16 flex flex-col justify-between border-b-4 lg:border-b-0 lg:border-r-4 border-black bg-paper">
            <div>
              <div className="inline-flex items-center gap-2 mb-6">
                <Badge variant="yellow" className="text-xs">
                  STAGE 1: MVP IN DEVELOPMENT
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
                variant="outline"
                size="lg"
                className="gap-2"
                onClick={() => {
                  window.open('http://localhost:8000/api/v1/docs', '_blank');
                }}
              >
                <span>Explore API</span>
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
            <div className="text-4xl font-black font-mono tracking-tight">&lt; 1.5s</div>
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

          {/* Constructivist Dropzone Box */}
          <div className="bg-white border-4 border-dashed border-black shadow-bauhaus-lg p-8 sm:p-16 text-center relative transition-all hover:bg-bauhaus-yellow/10 bg-bauhaus-dots">
            <div className="w-16 h-16 rounded-full bg-bauhaus-red border-4 border-black mx-auto mb-6 flex items-center justify-center shadow-bauhaus-sm">
              <Upload className="w-8 h-8 text-white" />
            </div>

            <h3 className="text-xl sm:text-2xl font-black uppercase tracking-tight mb-2">
              DRAG & DROP STATEMENT PDF HERE
            </h3>
            <p className="text-sm font-medium text-ink/70 mb-6">
              Supports HDFC, ICICI, SBI, Axis, and Amex (Up to 15MB)
            </p>

            <div className="flex justify-center gap-4">
              <Button variant="primary" size="md">
                SELECT PDF FILE
              </Button>
            </div>

            <div className="mt-8 pt-6 border-t-2 border-black flex flex-wrap items-center justify-center gap-6 text-xs font-mono font-bold text-ink/70">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-bauhaus-green" />
                Zero Disk Persistence
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-bauhaus-blue" />
                SHA-256 Deduplication
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-bauhaus-red" />
                Line-Item Reconciliation
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 4. ARCHITECTURAL PILLARS */}
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
                  statement's printed summary dues. Any discrepancy ($\gt ₹1.00$) flags
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
