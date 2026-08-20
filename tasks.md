# tasks.md — CC Track Step-by-Step Implementation Roadmap

> **Target:** A fully functional, production-grade CC Track platform implementing the specifications from [PRD.md](file:///Users/aritra/Code/Projects/CC-Tracker/PRD.md) and adhering to the guidelines in [AGENTS.md](file:///Users/aritra/Code/Projects/CC-Tracker/AGENTS.md).

---

## Task Progress Overview

- [x] **Phase 0: Workspace Setup & Monorepo Scaffolding**
- [x] **Phase 1: PDF Document Extraction & Multi-Bank Parsers**
- [x] **Phase 2: Financial Reconciliation & Validation Layer**
- [ ] **Phase 3: 3-Tier Categorization & Merchant Normalization Engine**
- [ ] **Phase 4: Deterministic Analytics & Metric Engine**
- [ ] **Phase 5: Pattern & Anomaly Detectors (10 Detectors)**
- [ ] **Phase 6: Recommendation Engine & LLM Explanation Layer**
- [ ] **Phase 7: FastAPI REST Backend Implementation & Testing**
- [ ] **Phase 8: Next.js Frontend — Client Decryption & Upload Experience**
- [ ] **Phase 9: Next.js Frontend — Insights Dashboard & Visualizations**
- [ ] **Phase 10: Next.js Frontend — Transaction Manager & Filter Controls**
- [ ] **Phase 11: Behavioral Feedback Loop & Recommendation Tracking**
- [ ] **Phase 12: Persistence Layer (Supabase / PostgreSQL Integration)**
- [ ] **Phase 13: End-to-End Testing, Polish, Benchmarking & Deployment**

---

## Phase 0: Workspace Setup & Monorepo Scaffolding

### Task 0.1: Initialize Monorepo Structure
- [x] Create frontend directory: `apps/web` (Next.js 14+ App Router, TypeScript, Tailwind CSS)
- [x] Create backend directory: `apps/api` (FastAPI, Python 3.11+, Pydantic v2)
- [x] Set up root `.gitignore` ignoring `.env`, `node_modules`, `__pycache__`, `.venv`, `.pytest_cache`
- [x] Configure root documentation and script shortcuts
- **Definition of Done:** Both `apps/web` and `apps/api` exist with their respective configuration files.

### Task 0.2: Configure Python Backend Environment
- [x] Create `apps/api/requirements.txt` with:
  - `fastapi>=0.110.0`, `uvicorn[standard]>=0.28.0`
  - `pdfplumber>=0.10.3`, `pymupdf>=1.23.0`
  - `pydantic>=2.6.0`, `pydantic-settings>=2.2.0`
  - `pandas>=2.2.0`, `numpy>=1.26.0`
  - `google-generativeai>=0.4.0` (or `openai>=1.14.0`)
  - `pytest>=8.0.0`, `pytest-cov>=4.1.0`, `httpx>=0.27.0`
  - `ruff>=0.3.0`, `mypy>=1.9.0`
- [x] Set up virtual environment `.venv` and verify clean installation
- [x] Create `apps/api/app/core/config.py` using `pydantic-settings`
- [x] Create `apps/api/app/main.py` with CORS middleware, structured exception handlers, and `/health` route
- **Verification:** `curl http://localhost:8000/health` returns `{"status": "healthy"}`.

### Task 0.3: Configure Next.js Frontend Environment
- [x] Initialize `apps/web` with Next.js 14 App Router, TypeScript, Tailwind CSS
- [x] Install UI dependencies: `clsx`, `tailwind-merge`, `lucide-react`, `recharts`, `framer-motion`
- [x] Install PDF handling library: `pdfjs-dist`
- [x] Initialize shadcn/ui components (`button`, `card`, `dialog`, `badge`, `tabs`, `progress`, `tooltip`, `dropdown-menu`)
- [x] Create `apps/web/src/lib/api.ts` with Axios/Fetch HTTP client
- **Verification:** `npm run dev` in `apps/web` serves starter page at `http://localhost:3000`.

---

## Phase 1: PDF Document Extraction & Multi-Bank Parsers

### Task 1.1: Core Data Models & Base Parser Interface
- [x] Create `apps/api/app/schemas/statement.py` defining:
  - `TransactionType` (Enum: `PURCHASE`, `REFUND`, `REVERSAL`, `PAYMENT`, `FEE`, `INTEREST`, `GST`, `EMI`, `CASH_WITHDRAWAL`, `REWARD`, `ADJUSTMENT`, `UNKNOWN`)
  - `ExtractedTransaction` (Pydantic model with strict validation)
  - `StatementHeader` (Issuer, Period, Balances, Due Date, Limit)
  - `ParsedStatement` (Header, Transactions list, Reconciliation metadata)
- [x] Create `apps/api/app/parsers/base.py` defining `BaseStatementParser` ABC:
  - `identify(first_page_text: str) -> bool`
  - `parse(pdf_stream: io.BytesIO) -> ParsedStatement`
- **Definition of Done:** Pydantic schemas compile and base class passes linting.

### Task 1.2: Bank Signature Detector
- [x] Create `apps/api/app/parsers/detector.py`
- [x] Implement signature rules and regex for:
  - HDFC Bank (e.g. "HDFC Bank Credit Card", "Card No.", "Billing Cycle")
  - ICICI Bank (e.g. "ICICI Bank Credit Card Statement", "Customer ID")
  - SBI Card (e.g. "SBI Cards and Payment Services", "Statement Period")
  - Axis Bank (e.g. "Axis Bank Credit Card", "Summary of Card Account")
  - American Express (e.g. "American Express Banking Corp.", "Membership Rewards")
- [x] Write unit tests in `apps/api/tests/test_detector.py`
- **Verification:** `pytest apps/api/tests/test_detector.py` passes 100%.

### Task 1.3: HDFC Bank Parser
- [x] Create `apps/api/app/parsers/hdfc.py`
- [x] Implement table boundary detection and multi-line row stitching
- [x] Parse transaction dates (`DD/MM/YYYY`), merchant descriptions, amounts, and `CR`/`DR` markers
- [x] Extract header metadata: Total Amount Due, Minimum Amount Due, Billing Period, Credit Limit
- [x] Create fixture: `apps/api/tests/fixtures/sample_texts.py`
- [x] Write unit tests in `apps/api/tests/test_hdfc_parser.py`
- **Verification:** Successfully extracts all rows from HDFC test statements without dropping lines.

### Task 1.4: ICICI Bank Parser
- [x] Create `apps/api/app/parsers/icici.py`
- [x] Handle ICICI multi-column layouts, landscape pages, and EMI schedule rows
- [x] Extract header metadata: Statement Date, Payment Due Date, Total Dues, Available Credit
- [x] Create fixture: `apps/api/tests/fixtures/sample_texts.py`
- [x] Write unit tests in `apps/api/tests/test_icici_parser.py`
- **Verification:** Extracts all ICICI transactions and ignores reward summaries.

### Task 1.5: SBI Card Parser
- [x] Create `apps/api/app/parsers/sbi.py`
- [x] Handle SBI Card tabular layout, filtering out reward point tables and finance charge disclosures
- [x] Extract header metadata: Statement Date, Total Amount Due, Min Amount Due
- [x] Create fixture: `apps/api/tests/fixtures/sample_texts.py`
- [x] Write unit tests in `apps/api/tests/test_sbi_parser.py`
- **Verification:** Correctly parses SBI Card statements with 100% row matching.

### Task 1.6: Axis Bank & American Express Parsers
- [x] Create `apps/api/app/parsers/axis.py` and `apps/api/app/parsers/amex.py`
- [x] Extract transactions and headers for Axis and AMEX statements
- [x] Write unit tests in `apps/api/tests/test_additional_parsers.py`
- **Verification:** Full bank parser suite runs cleanly via `pytest tests/test_parsers.py`.

---

## Phase 2: Financial Reconciliation & Validation Layer

### Task 2.1: Mathematical Reconciliation Engine
- [x] Create `apps/api/app/services/reconciliation.py`
- [x] Implement arithmetic checking:
  - $\sum \text{Debits} - \sum \text{Credits}$ compared with Statement Net Billed Change
  - Flag status as `VALIDATED` if $|\Delta| \le ₹1.00$; else `REVIEW_REQUIRED`
- [x] Compute exact discrepancy amount and unparsed row candidates
- [x] Write unit tests verifying edge cases (refunds, reversals, roundoff)
- **Definition of Done:** Reconciliation service correctly catches missing transactions or duplicate rows.

### Task 2.2: Transaction Sanity & Anomaly Filter
- [x] Create `apps/api/app/services/validator.py`
- [x] Check for:
  - Impossible dates (dates outside the billing window or future dates)
  - Zero or negative amount values in purchase fields
  - Exact duplicate transactions (same date, same merchant, same amount)
- **Verification:** Unit tests in `apps/api/tests/test_reconciliation.py` and `apps/api/tests/test_validator.py` pass.

---

## Phase 3: 3-Tier Categorization & Merchant Normalization Engine

### Task 3.1: Merchant Dictionary & Alias Normalizer
- [ ] Create `apps/api/app/categorization/dictionary.json` containing 250+ top Indian merchants:
  - Quick Commerce: Blinkit, Zepto, Instamart, DMart Ready
  - Food & Dining: Swiggy, Zomato, McDonald's, Starbucks, Domino's
  - Shopping: Amazon, Flipkart, Myntra, Ajio, Nykaa, Tata CLiQ
  - Transport & Fuel: Uber, Ola, Rapido, HPCL, BPCL, IOCL, Shell
  - Travel: MakeMyTrip, IRCTC, IndiGo, Air India, Yatra, OYO
  - Subscriptions & OTT: Netflix, Spotify, Disney+ Hotstar, Prime, YouTube
  - Utilities & Telecom: Airtel, Jio, VI, Tata Power, BESCOM, Adani Electricity
- [ ] Create `apps/api/app/categorization/normalizer.py` mapping raw merchant strings to standard brand names
- **Definition of Done:** 250+ merchants mapped with accurate canonical names and primary categories.

### Task 3.2: Regex & Heuristic Categorization Rules
- [ ] Create `apps/api/app/categorization/regex_rules.py`
- [ ] Define high-precision regex patterns for fuel, hospital/medical, grocery, rent, utilities, and education keywords
- [ ] Implement fallback to category heuristics based on keywords in description

### Task 3.3: LLM Batch Categorization Fallback & In-Memory Cache
- [ ] Create `apps/api/app/categorization/llm_fallback.py` using Google Gemini 1.5 Flash
- [ ] Implement batch prompt format: send unknown merchant strings only (no PII, no amounts)
- [ ] Add in-memory LRU cache / JSON cache so identical unknown merchants are only categorized once
- [ ] Create orchestrator `apps/api/app/categorization/engine.py` coordinating Tier 1 $\rightarrow$ Tier 2 $\rightarrow$ Tier 3
- **Verification:** Unit tests in `apps/api/tests/test_categorization.py` verify 90%+ hit rate without LLM.

---

## Phase 4: Deterministic Analytics & Metric Engine

### Task 4.1: Spend Totals & Averages Calculator
- [ ] Create `apps/api/app/analytics/calculator.py`
- [ ] Implement calculation of:
  - Total debits, total credits, net spend
  - Average transaction size, median transaction size, max transaction
  - Total transaction count, category spend breakdown (amounts and percentages)
  - Top 10 merchant concentration breakdown

### Task 4.2: Temporal & Behavioral Metrics
- [ ] Implement daily spending distribution and burn-rate velocity curve
- [ ] Implement weekday vs. weekend spend ratios and day-of-week trends
- [ ] Implement small transaction frequency metrics (purchases $< ₹250$)

### Task 4.3: Recurring Charges & Subscription Detector
- [ ] Create `apps/api/app/analytics/recurring.py`
- [ ] Detect recurring subscriptions based on:
  - Known subscription merchant names (Netflix, Spotify, Apple, Google)
  - Fixed recurring amount patterns at consistent intervals
- **Verification:** Unit tests in `apps/api/tests/test_analytics.py` confirm accurate metric output.

---

## Phase 5: Pattern & Anomaly Detectors (10 Detectors)

### Task 5.1: Implement Core Pattern Detectors
- [ ] Create `apps/api/app/analytics/anomalies.py`
- [ ] Implement 10 explicit detector functions:
  1. `detect_category_spike`: Category $> 1.30 \times$ baseline
  2. `detect_spending_acceleration`: Total spend $> 1.25 \times$ previous cycle
  3. `detect_frequent_small_spend`: Micro-spending leak analysis
  4. `detect_merchant_concentration`: Single merchant $> 35\%$ share
  5. `detect_unusual_purchase`: Z-score $> 2.5$ or percentile $> 98\%$
  6. `detect_subscription_burden`: Recurring $> 10\%$ of total spend
  7. `detect_weekend_spike`: Weekend spend $> 55\%$ of total
  8. `detect_late_night_spurt`: Purchases between 11 PM and 4 AM
  9. `detect_frequency_inflation`: Count grew $> 30\%$ with stable avg amount
  10. `detect_high_utilization`: Balance $> 30\%$ of card limit
- **Definition of Done:** Each detector returns a structured `Finding` model with severity, evidence, and title.

---

## Phase 6: Recommendation Engine & LLM Explanation Layer

### Task 6.1: Rule-Based Recommendation Generator
- [ ] Create `apps/api/app/recommendations/engine.py`
- [ ] Map detected findings to actionable recommendations:
  - Food & Dining reduction $\rightarrow$ compute realistic ₹ savings by cutting 2 orders/week
  - Micro-spend consolidation $\rightarrow$ calculate monthly savings
  - Subscription audit $\rightarrow$ list unused/redundant recurring charges
- [ ] Ensure all savings calculations are conservative and evidence-based
- [ ] Generate structured `Recommendation` objects

### Task 6.2: LLM Structured Explanation Formatter
- [ ] Create `apps/api/app/recommendations/llm_explainer.py`
- [ ] Formulate prompt: Pass structured facts (no user PII, only summary numbers)
- [ ] Enforce strict JSON output schema: `summary`, `what_stands_out`, `action_steps`
- [ ] Implement JSON validation fallback: If LLM fails or hallucinates, use deterministic template
- **Verification:** Unit tests in `apps/api/tests/test_recommendations.py` verify 100% valid JSON responses.

---

## Phase 7: FastAPI REST Backend Implementation & Testing

### Task 7.1: Statement Parse & Analyze Endpoint
- [ ] Create `apps/api/app/api/v1/endpoints/statements.py`
- [ ] Implement `POST /api/v1/statements/parse`:
  - Accepts `UploadFile` (multipart/form-data)
  - Processes file in RAM (`io.BytesIO`)
  - Detects bank, parses statement, runs reconciliation, categorizes transactions
  - Computes analytics, detects patterns, generates recommendations
  - Returns `ParseStatementResponse` JSON
- [ ] Implement global error handler catching parser exceptions and returning RFC 7807 problem JSON

### Task 7.2: Backend Integration & Performance Testing
- [ ] Write integration test in `apps/api/tests/test_api_integration.py` simulating full upload flow
- [ ] Benchmark parsing speed: ensure 5-page PDF parses in $< 2.0$ seconds
- **Verification:** `pytest apps/api/tests/` passes with $\ge 85\%$ test coverage.

---

## Phase 8: Next.js Frontend — Client Decryption & Upload Experience

### Task 8.1: Client-Side PDF Decryption Utility
- [ ] Create `apps/web/src/lib/pdf-unlocker.ts` using `pdfjs-dist`
- [ ] Detect if PDF is password-protected
- [ ] Unlock PDF in browser memory with user-provided password
- [ ] Export unlocked `ArrayBuffer` for backend transmission (raw password never leaves browser)

### Task 8.2: Dropzone & Upload State Machine
- [ ] Create `apps/web/src/components/upload/DropZone.tsx` with drag-and-drop support
- [ ] Create `apps/web/src/components/upload/PasswordModal.tsx` with bank-specific password hints
- [ ] Create `apps/web/src/components/upload/ProcessingProgress.tsx` with stepped animation:
  - *Decrypting $\rightarrow$ Extracting Tables $\rightarrow$ Categorizing $\rightarrow$ Reconciling $\rightarrow$ Finalizing*
- [ ] Create `apps/web/src/app/page.tsx` integrating upload flow
- **Verification:** Uploading encrypted HDFC statement prompts for password, unlocks client-side, and initiates parse.

---

## Phase 9: Next.js Frontend — Insights Dashboard & Visualizations

### Task 9.1: Executive Summary & Reconciliation Banner
- [ ] Create `apps/web/src/components/dashboard/OverviewCards.tsx` (Total spend, Net spend, Avg txn, Max purchase)
- [ ] Create `apps/web/src/components/dashboard/ReconciliationBadge.tsx` (Shows `Reconciled` or `Review Required` with delta)
- [ ] Create `apps/web/src/components/dashboard/KeyFindingsList.tsx` (Top 5 discoveries with severity icons)

### Task 9.2: Financial Charts with Recharts
- [ ] Create `apps/web/src/components/dashboard/CategoryDonutChart.tsx` (Interactive category distribution)
- [ ] Create `apps/web/src/components/dashboard/SpendingTimelineChart.tsx` (Daily spend line/area chart)
- [ ] Create `apps/web/src/components/dashboard/TopMerchantsBarChart.tsx` (Top 10 merchant horizontal bar chart)
- [ ] Ensure all charts support dark mode, responsive resizing, and custom tooltips with INR formatting (`₹`)

### Task 9.3: Actionable Recommendations Carousel
- [ ] Create `apps/web/src/components/insights/RecommendationCard.tsx`
- [ ] Display title, reason, evidence stats, estimated monthly savings badge, and action CTA
- [ ] Add "Show Transactions" button linking directly to filtered transaction table

---

## Phase 10: Next.js Frontend — Transaction Manager & Filter Controls

### Task 10.1: Interactive Transaction Table
- [ ] Create `apps/web/src/components/table/TransactionTable.tsx`
- [ ] Columns: Date, Merchant, Type Badge, Category, Amount (INR), Confidence / Action
- [ ] Implement search bar (filters by merchant name or description in real-time)
- [ ] Implement category and transaction type dropdown filters
- [ ] Implement sorting by Date (asc/desc) and Amount (high/low)

### Task 10.2: Inline Category & Merchant Correction
- [ ] Allow user to click category badge to reclassify transaction
- [ ] Dynamically recalculate category totals and charts in frontend state upon manual reclassification
- **Verification:** Table handles 300+ transactions with smooth 60fps scrolling and instant filtering.

---

## Phase 11: Behavioral Feedback Loop & Recommendation Tracking

### Task 11.1: Recommendation Action Controls
- [ ] Add `Accept`, `Dismiss`, and `Explore` buttons to `RecommendationCard.tsx`
- [ ] Store recommendation interaction events in client state / local storage
- [ ] Provide dismiss reason modal ("Already planned", "Not applicable", "Too restrictive")

### Task 11.2: Month-over-Month Outcome Verification (Stage 3 Preview)
- [ ] Create `apps/web/src/components/dashboard/MoMComparisonCard.tsx`
- [ ] When a subsequent statement is loaded, show verified savings comparison against prior recommendations

---

## Phase 12: Persistence Layer (Supabase / PostgreSQL Integration)

### Task 12.1: Supabase Database Migration & Schema
- [ ] Create SQL migration script in `apps/api/app/models/schema.sql` matching PRD Section 5
- [ ] Apply Row Level Security (RLS) policies on `statements`, `transactions`, `findings`, and `recommendations`

### Task 12.2: Save & History Endpoints
- [ ] Implement `POST /api/v1/statements/save` to persist current session to Supabase
- [ ] Implement `GET /api/v1/statements/history` to load past statements for authenticated users
- [ ] Add optional "Save Session" button in dashboard header

---

## Phase 13: End-to-End Testing, Polish, Benchmarking & Deployment

### Task 13.1: Test Corpus & Regression Suite
- [ ] Create statement test corpus covering:
  - Multi-page statements (3-8 pages)
  - Statements with refund credits and reversals
  - Statements with EMI installment lines and GST line items
  - Scanned / malformed edge case PDFs
- [ ] Run full automated test suite: `pytest` and Next.js test runner

### Task 13.2: Security & Privacy Audit
- [ ] Verify zero disk writes occur during backend execution
- [ ] Verify no raw password or 16-digit PAN is logged or stored
- [ ] Run `npm audit` and `pip-audit` to ensure zero critical vulnerabilities

### Task 13.3: Deployment Configuration
- [ ] Create `apps/api/Dockerfile` for containerized deployment (Cloud Run / Railway)
- [ ] Configure `apps/web` for Vercel deployment with environment variables
- [ ] Write clear `README.md` with system overview, architecture diagram, and local setup instructions
- **Final Definition of Done:** Complete project runs locally and deploys cleanly to staging with 100% test pass rate.
