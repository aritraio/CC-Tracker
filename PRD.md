# Product Requirements Document (PRD) — CC Track

**Product Name:** CC Track  
**Category:** Personal Spending Intelligence & Behavioral Financial Coach  
**Status:** In Development (Stage 1 / MVP)  
**Target Market:** Indian Credit Card Holders (HDFC, ICICI, SBI, Axis, American Express)  

---

## 1. Executive Summary & Product Vision

### 1.1 The Core Problem
Most credit card tools and personal finance apps are either:
1. **Dumb visualizers:** They parse a PDF and display a pie chart ("You spent 30% on Food"). They never explain *what changed, why it matters, or what the user can realistically do to spend less*.
2. **Privacy nightmares:** They demand open-ended Account Aggregator or NetBanking scraping access, storing full bank credentials and complete financial histories on unvetted servers.

### 1.2 Product Thesis & Value Proposition
> **"CC Track turns a messy credit-card statement into actionable financial intelligence."**

CC Track is a privacy-first web application where users upload monthly credit card statements and receive:
- **Flawless, reconciled extraction** with zero password transmission.
- **Deep behavioral insights** comparing spending against the user's historical personal baseline.
- **Evidence-based recommendations** with conservative, realistic savings estimates.
- **A closed-loop behavioral feedback system** that measures whether recommendations actually reduced spending next month.

---

## 2. Product Roadmap & Phasing

```text
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│        STAGE 1          │     │        STAGE 2          │     │        STAGE 3          │     │        STAGE 4          │
│   Statement Analyzer    │ ──> │  Spending Intelligence  │ ──> │    Behavioral Coach     │ ──> │   Card Optimization     │
│                         │     │                         │     │                         │     │                         │
│ • Multi-Bank Parsers    │     │ • Historical Profiles   │     │ • Actionable Feedback   │     │ • Utilization Alerts    │
│ • Deterministic Findings│     │ • MoM Trend Detection   │     │ • MoM Behavior Tracking │     │ • Reward Optimization   │
│ • 3-Tier Categorization │     │ • 10 Anomaly Detectors  │     │ • Verified Savings Log  │     │ • EMI & Fee Auditing    │
│ • Stateless In-Memory   │     │ • Rule Recommendations  │     │ • Personalized Habits   │     │ • Cross-Card Comparison │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

- **Stage 1 (Current MVP):** Single-statement ingestion, in-memory parsing for HDFC, ICICI, and SBI, strict balance reconciliation, 3-tier categorization, and core spending findings.
- **Stage 2:** Multi-statement upload, persistent user profile, historical baseline, and statistical pattern detection.
- **Stage 3:** Closed-loop feedback (Accept/Dismiss recommendations) and verifying if spending decreased in the subsequent statement.
- **Stage 4:** Advanced card features (EMI interest auditing, annual fee checks, reward point optimization, credit utilization guidance).

---

## 3. User Personas & Primary User Questions

### 3.1 Personas
1. **The Urban Professional ("Rohan", 28):** Holds 2-3 credit cards, frequently uses Swiggy/Zomato, Blinkit, and Uber. Wants to know where money is leaking without spending hours maintaining an Excel sheet.
2. **The Privacy-Conscious User ("Priya", 34):** Reluctant to share banking passwords with aggregators. Wants a standalone tool where she can drop a password-protected PDF, get insights, and know her document was processed in RAM and destroyed.
3. **The Credit Optimizer ("Amit", 31):** Wants to audit hidden fees, GST on charges, recurring subscription sprawl, and keep utilization in check.

### 3.2 Key Questions CC Track Must Answer
1. *Where exactly did my money go this billing cycle?*
2. *What changed significantly compared to my recent months?*
3. *Which recurring subscriptions or micro-transactions are quietly adding up?*
4. *Where can I realistically cut spending without drastic lifestyle sacrifices?*
5. *Did my changes last month actually save me money on this statement?*

---

## 4. Comprehensive Functional Requirements

### 4.1 Statement Ingestion & Client-Side Decryption
- **FR-1.1 File Dropzone:** Support drag-and-drop of `.pdf` statements up to 15MB.
- **FR-1.2 Client-Side Decryption:** For password-protected statements (common in India: DOB + PAN combination):
  - Detect encryption using `pdf.js` in the browser.
  - Prompt user with an inline dialog explaining the bank's password format.
  - Unlock the document in browser memory before transmitting decrypted bytes to the backend.
  - **Security Rule:** The raw password string must never be sent over the wire or stored.
- **FR-1.3 Duplicate Detection:** Compute SHA-256 hash of statement content combined with `card_last_4` and `billing_period` to prevent duplicate processing.

### 4.2 Multi-Bank Extraction Engine
- **FR-2.1 Issuer Detection:** Automatically detect the issuing bank from the first page text and layout:
  - Supported initial issuers: **HDFC Bank**, **ICICI Bank**, **State Bank of India (SBI)**, **Axis Bank**, and **American Express**.
- **FR-2.2 Statement Metadata Extraction:** Extract key header elements:
  - Statement Period (`start_date`, `end_date`), Due Date, Total Amount Due, Minimum Amount Due, Credit Limit, Available Credit, Opening/Closing Balance, Total Debits, Total Credits.
- **FR-2.3 Tabular Row Extraction:**
  - Extract `transaction_date`, `post_date`, `raw_merchant_description`, `amount`, `currency` (INR/forex), and `cr_dr_flag`.
  - Intelligently join multi-line merchant descriptions split across rows or page breaks.

### 4.3 Transaction Typing & Normalization
- **FR-3.1 Transaction Types:** Every row must be categorized into one of:
  - `PURCHASE` (Standard merchant buy)
  - `REFUND` (Merchant refund / return credit)
  - `REVERSAL` (Chargeback or failed transaction reversal)
  - `PAYMENT` (User payment toward credit card bill)
  - `FEE` (Annual fee, late fee, cash advance fee)
  - `INTEREST` (Finance charge on revolving balance)
  - `GST` (Goods & Services Tax on fees and interest)
  - `EMI` (Equal Monthly Installment line item or processing fee)
  - `CASH_WITHDRAWAL` (ATM cash advance)
  - `REWARD` (Cashback or reward redemption credit)
  - `ADJUSTMENT` (Bank manual credit/debit)
  - `UNKNOWN` (Requires manual classification)

### 4.4 3-Tier Categorization & Merchant Cleaning
```text
Raw Transaction String ("AMZN Mktp IND Pvt Ltd")
                  ↓
Tier 1: High-Speed Exact Dictionary (250+ Indian Merchants) ──> Matched? ──> "Amazon" / "Shopping"
                  ↓ No
Tier 2: Regex & Heuristic Rule Engine (Patterns, MCCs)     ──> Matched? ──> "Shopping"
                  ↓ No
Tier 3: Batch LLM Fallback (Gemini Flash)                  ──> Matched? ──> Cache Result in Dict
```
- **FR-4.1 Categories (14 Standard Buckets):**
  1. `Food & Dining` (Restaurants, Delivery: Swiggy, Zomato)
  2. `Shopping` (E-commerce, Clothing, Electronics)
  3. `Groceries & Quick-Commerce` (Blinkit, Zepto, DMart, Instamart)
  4. `Transport & Fuel` (Uber, Ola, Shell, HPCL, Metro)
  5. `Travel & Lodging` (Airlines, MakeMyTrip, IRCTC, Hotels)
  6. `Bills & Utilities` (Electricity, Water, Mobile, Broadband)
  7. `Entertainment & OTT` (Movies, BookMyShow, Gaming)
  8. `Subscriptions` (Netflix, Spotify, Prime, YouTube, Cloud)
  9. `Healthcare & Fitness` (Pharmacies, Cult.fit, Hospitals)
  10. `Education` (Courses, Books, School/College fees)
  11. `Rent & Housing` (Housing payments, Society maintenance)
  12. `Fees & Charges` (Card fees, GST, Surcharges)
  13. `Cash Withdrawal` (ATM transactions)
  14. `Other / Uncategorized`
- **FR-4.2 Merchant Normalization:** Normalize aliases to brand names (e.g. `PYTM*SWIGGY` $\rightarrow$ `Swiggy`).

### 4.5 Financial Reconciliation & Integrity Layer
- **FR-5.1 Mathematical Reconciliation Check:**
  $$\Delta = |\text{Statement Billed Debits} - \sum \text{Extracted Purchases & Debits}|$$
  - If $\Delta \le ₹1.00 \implies$ Status = `VALIDATED`.
  - If $\Delta > ₹1.00 \implies$ Status = `REVIEW_REQUIRED` with discrepancy amount surfaced.
- **FR-5.2 Validation Rules:**
  - Reject statements with impossible dates (future dates or dates outside statement cycle).
  - Detect duplicate transactions occurring on same day with identical amount and merchant.
  - Alert on missing mandatory fields (e.g. missing amount).

### 4.6 Deterministic Analytics Engine
- **FR-6.1 Core Metrics:** Total spend, Net spend (purchases minus refunds), average transaction amount, median transaction, max transaction, total transaction count.
- **FR-6.2 Temporal Analysis:** Weekday vs. weekend spend ratio, daily burn rate, spending velocity curve across the 30-day billing cycle.
- **FR-6.3 Recurring & Subscription Detection:**
  - Identify transactions occurring with regular periodicity (monthly/annual) and identical or near-identical amounts (e.g., Spotify ₹119, Netflix ₹649, iCloud ₹75).
- **FR-6.4 Personal Spending Profile:**
  - Build rolling baseline (3-month / 6-month trailing average) across categories, median purchase size, and discretionary ratio.

### 4.7 10 Pattern & Anomaly Detectors
1. **Category Spike:** Current category spend $> 1.30 \times$ historical average.
2. **Spending Acceleration:** Total spend $> 1.25 \times$ previous month.
3. **Frequent Small Spend Leak:** Transactions $< ₹250$ accounting for $> 25\%$ of transaction count and $> 15\%$ of discretionary total.
4. **Merchant Concentration:** Single merchant accounts for $> 35\%$ of total monthly spend.
5. **Statistical Anomaly:** Transaction amount with $Z\text{-score} > 2.5$ against personal distribution.
6. **Subscription Burden:** Total recurring payments $> 10\%$ of total monthly spend.
7. **Weekend Spike:** Weekend spend $> 55\%$ of total cycle spend.
8. **Late-Night Spurt:** Cluster of food delivery or e-commerce purchases between 11 PM and 4 AM.
9. **Frequency Inflation:** Transaction count grew $> 30\%$ while average ticket size stayed constant.
10. **High Credit Utilization:** Balance utilized $> 30\%$ of total card credit limit.

### 4.8 Evidence-Based Recommendation Engine
- **FR-8.1 Output Format:** Every recommendation must provide structured, auditable evidence:
  ```json
  {
    "id": "rec_food_01",
    "type": "CATEGORY_REDUCTION",
    "title": "Trim Quick-Commerce Orders",
    "reason": "Quick-commerce spend increased 42% this month across 18 transactions.",
    "evidence": {
      "current_spend": 5400,
      "historical_avg": 3800,
      "transaction_count": 18,
      "top_merchants": ["Blinkit", "Zepto"]
    },
    "estimated_monthly_savings": 1400,
    "confidence_score": 0.92,
    "action": "Consolidate small quick-commerce runs to reduce 3-4 impulse orders per week."
  }
  ```
- **FR-8.2 Guardrail Rules:**
  - No generic shaming ("Stop buying coffee").
  - Conservative savings estimates (calculated from actual delta, never exaggerated).
  - Explicit action step linked to transaction drill-down.

### 4.9 LLM Explanation Layer
- **FR-9.1 Role:** Generate concise, conversational, and empathetic explanations based **only** on the structured findings emitted by the analytics engine.
- **FR-9.2 Strict Output Contract:** LLM must return JSON only. If the LLM generates any metric not present in the input payload, the response is discarded and a deterministic fallback template is used.

### 4.10 Recommendation Feedback & Outcome Tracking Loop
- **FR-10.1 Interaction Events:** Capture user reactions (`ACCEPTED`, `DISMISSED`, `EXPLORED_TRANSACTIONS`).
- **FR-10.2 Outcome Verification (Stage 3):** When the next statement is uploaded, automatically measure:
  - Change in target category spending.
  - Actual realized savings vs. estimated savings.
  - Celebrate success banner: *"You reduced quick-commerce spend by ₹1,250 this month!"*

---

## 5. Data Architecture & Database Schema (PostgreSQL)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Credit Cards
CREATE TABLE cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    issuer VARCHAR(50) NOT NULL, -- HDFC, ICICI, SBI, AXIS, AMEX
    card_name VARCHAR(100),       -- Regalia, Millennia, Amazon Pay ICICI
    card_last_4 VARCHAR(4),
    credit_limit NUMERIC(12, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Statements
CREATE TABLE statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    card_id UUID REFERENCES cards(id) ON DELETE SET NULL,
    file_hash VARCHAR(64) NOT NULL,
    period_start DATE,
    period_end DATE,
    due_date DATE,
    total_amount_due NUMERIC(12, 2) NOT NULL,
    minimum_amount_due NUMERIC(12, 2),
    total_debits NUMERIC(12, 2),
    total_credits NUMERIC(12, 2),
    reconciliation_status VARCHAR(20) NOT NULL, -- VALIDATED, REVIEW_REQUIRED
    reconciliation_delta NUMERIC(10, 2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement_id UUID REFERENCES statements(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    post_date DATE,
    merchant_raw TEXT NOT NULL,
    merchant_normalized VARCHAR(150),
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    transaction_type VARCHAR(30) NOT NULL, -- PURCHASE, REFUND, FEE, GST, etc.
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    is_recurring BOOLEAN DEFAULT FALSE,
    is_anomaly BOOLEAN DEFAULT FALSE,
    source_page INT,
    confidence_score NUMERIC(3, 2) DEFAULT 1.00,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deterministic Findings
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement_id UUID REFERENCES statements(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    finding_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- INFO, WARNING, CRITICAL
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    evidence JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recommendations
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    finding_id UUID REFERENCES findings(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    action_text TEXT NOT NULL,
    estimated_savings NUMERIC(10, 2),
    confidence NUMERIC(3, 2),
    status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, ACCEPTED, DISMISSED, COMPLETED
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Feedback Events
CREATE TABLE recommendation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID REFERENCES recommendations(id) ON DELETE CASCADE,
    event_type VARCHAR(30) NOT NULL, -- VIEWED, CLICKED, ACCEPTED, DISMISSED
    event_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 6. API Specification (FastAPI REST Endpoints)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/statements/parse` | Parse uploaded PDF stream in RAM; return transactions & findings | Optional |
| `POST` | `/api/v1/statements/save` | Persist parsed statement & transactions to user profile | Yes |
| `GET` | `/api/v1/statements` | List statements for authenticated user | Yes |
| `GET` | `/api/v1/statements/{id}` | Get statement summary & full transaction list | Yes |
| `GET` | `/api/v1/analytics/profile` | Get rolling personal spending profile & MoM trends | Yes |
| `GET` | `/api/v1/recommendations/active` | Get active recommendations for user | Yes |
| `POST` | `/api/v1/recommendations/{id}/feedback` | Record user interaction (Accept/Dismiss/Complete) | Yes |
| `PATCH` | `/api/v1/transactions/{id}` | Manually override category or merchant | Yes |

---

## 7. UI / UX Specifications & Screen Flow

1. **Screen 1: Clean Landing & Upload Area:**
   - Drag & drop PDF card with issuer logos (HDFC, ICICI, SBI, Axis, Amex).
   - "Privacy Promise" badge: *100% In-Memory Processing. Passwords never leave your device.*
2. **Screen 2: Password Decryption Modal:**
   - Triggers automatically if PDF is encrypted. Explains format (e.g., "HDFC: First 4 chars of name in uppercase + DOB as DDMM").
3. **Screen 3: Processing State:**
   - Animated stepped progress: *Decrypting $\rightarrow$ Parsing Tables $\rightarrow$ Categorizing Merchants $\rightarrow$ Reconciling Balance $\rightarrow$ Generating Intelligence*.
4. **Screen 4: Executive Insights Dashboard:**
   - Top banner: Statement Period, Net Spend, Reconciliation Badge (`Reconciled: 0 discrepancy`).
   - "Top 5 Discoveries" cards (Key findings with delta badges).
   - "Actionable Changes" carousel (Evidence-backed savings cards with "Show Transactions" CTA).
   - Charts: Spend Over Time, Category Donut, Top 10 Merchants bar chart.
5. **Screen 5: Interactive Transaction Table:**
   - Search by merchant, filter by category/type, sort by amount/date.
   - Inline category correction dropdown (updates local state immediately).

---

## 8. Success Metrics & Key Performance Indicators (KPIs)

1. **Extraction Accuracy Rate:** $> 99.0\%$ transaction line item extraction across supported bank statements.
2. **Reconciliation Success Rate:** $> 95.0\%$ of uploaded statements pass mathematical reconciliation with $\le ₹1.00$ discrepancy.
3. **LLM Fallback Rate:** $< 10\%$ of transactions require LLM classification (Tier 1 & 2 handle $\ge 90\%$).
4. **Recommendation Acceptance Rate:** $> 30\%$ of users click "Accept" or "Show Transactions" on surfaced recommendations.
5. **Verified Behavior Change (Stage 3):** Measurable reduction in target category spending across $40\%+$ of returning users.
