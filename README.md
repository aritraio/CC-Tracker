# CC Track 💳

> **Transform unstructured credit card PDF statements into mathematically verified transactions and deterministic, evidence-based spending intelligence.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Tests](https://img.shields.io/badge/Tests-120%20Passed-brightgreen.svg?style=flat)]()
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg?style=flat)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. System Architecture

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                CLIENT-SIDE (Next.js 14)                                │
│                                                                                        │
│   [ Encrypted PDF ] ──> [ Browser Decryption ] ──> [ Ephemeral RAM Buffer ]            │
│   (DOB / PAN input)     (pdf.js in memory)          (Password never sent)              │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │ Decrypted Bytes
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               BACKEND API (FastAPI)                                    │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 1. Multi-Bank Signature Detection & Coordinate Extraction                     │   │
│   │    (HDFC Bank, ICICI Bank, SBI Card, Axis Bank, American Express)              │   │
│   └──────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                          ▼                                             │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 2. Mathematical Reconciliation & Line Integrity Validator                      │   │
│   │    (Reconciles extracted line items against statement debits: Δ ≤ ₹1.00)       │   │
│   └──────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                          ▼                                             │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 3. 3-Tier Categorization & Merchant Normalization Engine                       │   │
│   │    • Tier 1: 250+ Merchant Dictionary (Instant O(1))                           │   │
│   │    • Tier 2: Heuristic Regex & Substring Patterns                              │   │
│   │    • Tier 3: Batch LLM Fallback (Gemini 1.5 Flash)                             │   │
│   └──────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                          ▼                                             │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 4. Deterministic Analytics Engine                                              │   │
│   │    (Spend Totals, Daily Burn Rate, Weekend vs Weekday, Recurring Subscriptions)│   │
│   └──────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                          ▼                                             │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 5. 10 Pattern & Anomaly Detectors                                              │   │
│   │    (Spikes, Micro-spend leaks, Acceleration, Subscriptions, Utilization)       │   │
│   └──────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                          ▼                                             │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 6. Evidence-Based Recommendation Engine & LLM Explanation Layer                │   │
│   │    (Deterministic conservative math + Gemini coaching narrative)               │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              INSIGHTS & FEEDBACK LOOP                                  │
│                                                                                        │
│   • Executive Coaching & Visual Recharts (Donut, Daily Velocity, Top Merchants)        │
│   • Interactive Transaction Manager with Live Category Reclassification               │
│   • Closed-Loop Feedback: Accept Goals, Dismiss with Reasons, Track Outcomes           │
│   • Month-over-Month (MoM) Verified Savings vs Baseline Comparison                     │
│   • PostgreSQL / Supabase Persistence with Row Level Security (RLS)                    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Engineering Principles

1. **Correctness Beats AI:** Financial numbers require 100% mathematical integrity. AI is never allowed to calculate balances or extract numbers directly.
2. **Deterministic Rules Before ML:** All totals, category distributions, velocity metrics, and anomalies are computed deterministically in vectorized Python.
3. **LLM Explains, Analytics Computes:** The LLM layer strictly translates pre-calculated mathematical facts into clear, empathetic behavioral advice.
4. **Mandatory Reconciliation:** Every parsed statement compares extracted transactions against the printed statement total due. If discrepancy $> ₹1.00$, it is flagged as `REVIEW_REQUIRED`.
5. **Privacy by Architecture:**
   - Client-side decryption: Encrypted statements unlock in the browser. Passwords never travel over the network.
   - Ephemeral in-memory parsing: PDF streams are processed strictly in RAM (`io.BytesIO`) with zero temporary disk writes.
   - Minimal data exposure: Full 16-digit card numbers and CVVs are never extracted or stored (only masked `card_last_4`).

---

## 3. Supported Banks & Extraction Formats

| Issuer | Statement Formats | Features Supported |
|---|---|---|
| **HDFC Bank** | Regalia, Millennia, Infinia, Diners | Multi-page boundary stitching, `Cr`/`Dr` detection, reward summary rejection |
| **ICICI Bank** | Amazon Pay, Coral, Sapphiro, Emeralde | Multi-column layouts, landscape pages, EMI schedule handling |
| **SBI Card** | SimplyCLICK, SimplySAVE, Elite, Prime | Multi-page tables, finance charges, GST line items |
| **Axis Bank** | Magnus, Atlas, Flipkart, Neo | Summary table isolation, credit limit and available balance extraction |
| **American Express** | Platinum, Gold, MRCC, SmartEarn | Currency conversions, Membership Rewards credits, date-range headers |

---

## 4. Key Feature Modules

### 🔍 10 Pattern & Anomaly Detectors
- **Category Spike:** Spend in a category $> 1.30\times$ historical average.
- **Spending Acceleration:** Spend velocity exceeds previous cycle baseline by $> 25\%$.
- **Frequent Small Spend Leak:** Micro-transactions $< ₹250$ causing quiet budget drain.
- **Merchant Concentration:** Over-reliance on a single merchant ($> 35\%$ of monthly spend).
- **Unusual Purchase:** Individual transactions exceeding statistical Z-score threshold ($Z > 2.5$).
- **Subscription Burden:** Recurring charges exceeding $10\%$ of total discretionary spend.
- **Weekend Spike:** Disproportionate weekend leisure spending ($> 55\%$ of cycle total).
- **Late-Night Spurt:** Cluster of late-night delivery or e-commerce purchases (11 PM – 4 AM).
- **Frequency Inflation:** Transaction count grew $> 30\%$ while average ticket size stayed constant.
- **Credit Utilization:** Billed balance exceeds recommended $30\%$ card limit.

### 🎯 Behavioral Feedback Loop & MoM Outcome Verification
- **Goal Commitment:** Accept evidence-based recommendations to set targeted monthly savings goals.
- **Structured Dismissal:** Capture rationale ("Already planned", "Too restrictive", "Fixed expense") to calibrate future suggestions.
- **Verified Outcome Engine:** Compare subsequent statement spend against prior accepted goals to measure exact **Realized Savings** vs. **Target Savings** ($89\%$ Goal Met, Target Exceeded).

### 🗄️ Persistence Layer (PostgreSQL / Supabase)
- Full SQL DDL with **Row Level Security (RLS)** in `apps/api/app/models/schema.sql`.
- Isolated user vaults for `statements`, `transactions`, `findings`, `recommendations`, and `events`.
- Instant session saving with `POST /api/v1/statements/save` and historical list with `GET /api/v1/statements/history`.

---

## 5. Quickstart Guide

### Prerequisites
- **Node.js**: v18.0+ / v20+
- **Python**: v3.11+
- **Docker** (Optional, for containerized run)

### Option A: Local Development Run

#### 1. Backend Setup (FastAPI)
```bash
cd apps/api

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

#### 2. Frontend Setup (Next.js)
```bash
cd apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```
Web application will be live at [http://localhost:3000](http://localhost:3000).

---

### Option B: Docker Compose (Full Stack)

```bash
# Build and run backend + frontend together
docker-compose up --build
```
- Web UI: [http://localhost:3000](http://localhost:3000)
- API Health: [http://localhost:8000/health](http://localhost:8000/health)

---

## 6. Testing & Quality Verification

### Run Backend Test Suite (120 Tests, 95% Coverage)
```bash
cd apps/api
source .venv/bin/activate

# Run all unit, integration, and regression tests
pytest --cov=app tests/

# Run performance benchmarks (< 2.0s SLA)
pytest tests/test_benchmarks.py -v

# Run privacy & security audit
pytest tests/test_security_privacy.py -v
```

### Run Frontend Typecheck & Build
```bash
cd apps/web

# Typecheck TypeScript
npm run typecheck

# Production Next.js build
npm run build
```

---

## 7. Project Structure

```text
CC-Tracker/
├── AGENTS.md                  # Agent operating manual & engineering guidelines
├── PRD.md                     # Product Requirements Document
├── DESIGN.md                  # Visual design system (Bauhaus brutalism)
├── tasks.md                   # Step-by-step ordered implementation roadmap
├── docker-compose.yml         # Container orchestration
│
├── apps/
│   ├── web/                   # Next.js 14 Frontend Application
│   │   ├── src/
│   │   │   ├── app/           # App Router pages & API routes
│   │   │   ├── components/
│   │   │   │   ├── dashboard/ # OverviewCards, Charts, MoMComparisonCard
│   │   │   │   ├── insights/  # RecommendationCard, DismissModal, Coaching
│   │   │   │   ├── table/     # TransactionManager, FilterControls, CategorySelect
│   │   │   │   ├── ui/        # Bauhaus-styled UI design system components
│   │   │   │   └── upload/    # DropZone, PasswordModal, ProgressTracker
│   │   │   ├── lib/           # API client, PDF unlocker, feedback tracker
│   │   │   └── types/         # TypeScript shared contracts
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   └── api/                   # FastAPI Backend Application
│       ├── app/
│       │   ├── main.py        # FastAPI entrypoint, CORS, exception handlers
│       │   ├── api/v1/        # REST routers (statements, recommendations, health)
│       │   ├── analytics/     # Deterministic spend calculators & anomaly detectors
│       │   ├── categorization/# 3-tier dictionary, regex rules & normalizer
│       │   ├── models/        # PostgreSQL schema.sql with RLS policies
│       │   ├── parsers/       # HDFC, ICICI, SBI, Axis, Amex coordinate parsers
│       │   ├── recommendations/# Rule-based recommendations & LLM explainer
│       │   ├── schemas/       # Strict Pydantic v2 data models
│       │   └── services/      # Storage service, validator, reconciler
│       ├── tests/             # Comprehensive 120-test test suite
│       ├── Dockerfile
│       └── requirements.txt
```

---

## 8. License

Distributed under the MIT License. See `LICENSE` for more information.
