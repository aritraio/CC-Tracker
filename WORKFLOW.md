# AI Financial Journal — System Workflow

> Complete data flow, architecture, and component interaction reference.

---

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Data Flow — End to End](#data-flow--end-to-end)
- [Component Workflows](#component-workflows)
  - [1. Frontend — PDF Upload & Local Decryption](#1-frontend--pdf-upload--local-decryption)
  - [2. Backend — Stateless Parsing Engine](#2-backend--stateless-parsing-engine)
  - [3. Categorization Engine](#3-categorization-engine)
  - [4. Dashboard Rendering](#4-dashboard-rendering)
  - [5. Optional — Persist to Database](#5-optional--persist-to-database)
- [Security & Privacy Workflow](#security--privacy-workflow)
- [Error Handling Workflow](#error-handling-workflow)
- [Deployment Workflow](#deployment-workflow)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                          │
│                                                                 │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │  Upload   │───▶│  pdf.js       │───▶│  Decrypted PDF Blob   │  │
│  │  Widget   │    │  (local       │    │  (in-memory only)     │  │
│  │          │    │  decryption)  │    │                       │  │
│  └──────────┘    └──────────────┘    └───────────┬───────────┘  │
│                                                   │              │
│                                    POST /parse (multipart/form) │
│                                                   │              │
└───────────────────────────────────────────────────┼──────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI Microservice)                │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────┐ │
│  │  Bank         │──▶│  pdfplumber   │──▶│  Transaction        │ │
│  │  Detector     │   │  Table        │   │  Objects List       │ │
│  │  (regex)      │   │  Extractor    │   │  (in RAM)           │ │
│  └──────────────┘   └──────────────┘   └──────────┬──────────┘ │
│                                                    │             │
│                                                    ▼             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              CATEGORIZATION ENGINE                          ││
│  │                                                             ││
│  │   Step 1: Merchant Dictionary Lookup (200+ Indian vendors) ││
│  │   Step 2: Regex Pattern Matching (fallback)                ││
│  │   Step 3: LLM API Call — Gemini Flash (final fallback)     ││
│  │                                                             ││
│  └─────────────────────────────────────┬───────────────────────┘│
│                                        │                        │
│                  JSON Response ◀───────┘                        │
│                  (Buffer cleared immediately after response)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   INSIGHTS DASHBOARD                     │   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │   │
│  │  │ Money       │  │ Category     │  │ Recurring      │  │   │
│  │  │ Overview    │  │ Breakdown    │  │ Charges        │  │   │
│  │  │ Cards       │  │ Pie/Bar      │  │ Detector       │  │   │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │   │
│  │                                                          │   │
│  │  ┌─────────────────────┐  ┌───────────────────────────┐  │   │
│  │  │ Anomaly Highlights  │  │ Transaction Table         │  │   │
│  │  │ (out-of-pattern)    │  │ (sortable, filterable)    │  │   │
│  │  └─────────────────────┘  └───────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│           ┌──────────────────────────────────────┐              │
│           │  [Optional] Save to Account          │              │
│           │  (Supabase/Neon PostgreSQL)           │              │
│           └──────────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow — End to End

### Step-by-Step Sequence

```
1. USER selects a credit card statement PDF from their device.
        │
        ▼
2. FRONTEND prompts for password (PAN number / DOB / custom).
        │
        ▼
3. pdf.js (running IN THE BROWSER) decrypts the PDF locally.
   ─── The password NEVER leaves the user's device. ───
        │
        ▼
4. FRONTEND sends the decrypted PDF blob to the backend
   via POST /api/v1/parse as multipart/form-data.
        │
        ▼
5. BACKEND receives the file as an in-memory buffer (BytesIO).
   ─── No disk write occurs at any point. ───
        │
        ▼
6. BANK DETECTOR examines the first page of the PDF.
   Uses regex patterns to identify the issuing bank
   (HDFC / ICICI / SBI) and selects the correct parser.
        │
        ▼
7. PARSER (bank-specific) uses pdfplumber to extract
   tabular transaction data from every page.
   Output: List of raw transaction dictionaries.
        │
        ├── { date, description, amount, type: debit/credit }
        ├── { date, description, amount, type: debit/credit }
        └── ...
        │
        ▼
8. CATEGORIZATION ENGINE processes each transaction:
   8a. Check merchant_dictionary.json → if match → assign category.
   8b. If no match → apply regex rules → if match → assign category.
   8c. If still no match → call Gemini Flash API → assign category.
        │
        ▼
9. INSIGHTS CALCULATOR computes:
   ─ Total spend, average transaction, largest purchase
   ─ Category-wise spend breakdown
   ─ Recurring charge detection (same merchant, similar amount, monthly)
   ─ Anomaly detection (z-score based or percentile threshold)
        │
        ▼
10. BACKEND returns a structured JSON response to the frontend.
    ─── In-memory PDF buffer is immediately deallocated. ───
        │
        ▼
11. FRONTEND renders the Insights Dashboard:
    ─ Money Overview cards
    ─ Category pie/bar charts (recharts)
    ─ Recurring charges list
    ─ Anomaly highlights
    ─ Full transaction table
        │
        ▼
12. [OPTIONAL] USER can create an account and save the
    extracted insights to PostgreSQL (Supabase/Neon).
    ─── Only anonymized transaction data is stored, NEVER the PDF. ───
```

---

## Component Workflows

### 1. Frontend — PDF Upload & Local Decryption

```
User Action                    System Response
───────────                    ───────────────
Click "Upload Statement"  ──▶  File picker opens (accept: .pdf only)
                               │
Select PDF file            ──▶  File is loaded into browser memory
                               │
                               ▼
                          ┌────────────────────────┐
                          │  Is the PDF encrypted?  │
                          └──────────┬─────────────┘
                                     │
                          ┌──── YES ─┴─ NO ────┐
                          │                     │
                          ▼                     ▼
                   Show password          Skip password
                   input modal            step entirely
                          │                     │
                          ▼                     │
                   pdf.js decrypts              │
                   locally in browser           │
                          │                     │
                          ├─────────────────────┘
                          │
                          ▼
                   Show loading spinner
                   "Analyzing your statement..."
                          │
                          ▼
                   POST decrypted blob to
                   backend /api/v1/parse
                          │
                          ▼
                   Receive JSON response
                          │
                          ▼
                   Render Dashboard
```

**Key Implementation Notes:**
- Use `pdfjs-dist` npm package.
- Load the PDF with `pdfjsLib.getDocument({ data: arrayBuffer, password: userPassword })`.
- If decryption fails, catch the `PasswordException` and re-prompt the user.
- Convert the decrypted document back to a `Blob` for upload.
- Show clear error states for wrong passwords, corrupted files, or unsupported banks.

---

### 2. Backend — Stateless Parsing Engine

```
Incoming Request: POST /api/v1/parse
                          │
                          ▼
              ┌───────────────────────┐
              │  Receive PDF as       │
              │  UploadFile (BytesIO) │
              │  ── NO DISK WRITE ──  │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  BANK DETECTION       │
              │                       │
              │  Read first page text │
              │  Match against known  │
              │  bank signatures:     │
              │                       │
              │  "HDFC Bank" → hdfc   │
              │  "ICICI Bank" → icici │
              │  "State Bank" → sbi   │
              └───────────┬───────────┘
                          │
               ┌──── MATCH? ────┐
               │                │
             YES               NO
               │                │
               ▼                ▼
        Select bank       Return 400:
        parser module     "Unsupported bank"
               │
               ▼
        ┌──────────────────────────┐
        │  BANK-SPECIFIC PARSER    │
        │                          │
        │  1. Identify table       │
        │     boundaries per page  │
        │  2. Extract rows via     │
        │     pdfplumber           │
        │  3. Clean & normalize    │
        │     (strip whitespace,   │
        │     parse dates,         │
        │     normalize amounts)   │
        │  4. Validate row         │
        │     integrity            │
        └──────────┬───────────────┘
                   │
                   ▼
        List[Transaction] passed
        to Categorization Engine
```

**Parser Module Structure:**
```
backend/
├── parsers/
│   ├── __init__.py
│   ├── base.py          # Abstract base parser class
│   ├── hdfc.py          # HDFC-specific extraction logic
│   ├── icici.py         # ICICI-specific extraction logic
│   ├── sbi.py           # SBI-specific extraction logic
│   └── detector.py      # Bank detection logic
```

---

### 3. Categorization Engine

```
For each Transaction(description, amount):
              │
              ▼
┌──────────────────────────────────┐
│  TIER 1: Merchant Dictionary     │
│                                  │
│  Load merchant_dictionary.json   │
│  Normalize description string    │
│  (lowercase, strip spaces)       │
│                                  │
│  Exact match or substring match  │
│  against 200+ known merchants   │
│                                  │
│  Example:                        │
│  "ZOMATO" → Food & Dining       │
│  "NETFLIX" → Entertainment      │
│  "UBER" → Transport             │
└──────────┬───────────────────────┘
           │
   ┌── MATCH? ──┐
   │             │
  YES           NO
   │             │
   ▼             ▼
  Done   ┌──────────────────────────────┐
         │  TIER 2: Regex Rules          │
         │                               │
         │  Apply category-specific      │
         │  regex patterns:              │
         │                               │
         │  r"(?i)fuel|petrol|hp|iocl"   │
         │    → Fuel & Transport         │
         │  r"(?i)pharma|medic|apollo"   │
         │    → Healthcare               │
         │  r"(?i)airtel|jio|vodafone"   │
         │    → Bills & Utilities        │
         └──────────┬────────────────────┘
                    │
            ┌── MATCH? ──┐
            │             │
           YES           NO
            │             │
            ▼             ▼
           Done    ┌────────────────────────────────┐
                   │  TIER 3: LLM Fallback           │
                   │                                  │
                   │  Batch unrecognized descriptions │
                   │  Send to Gemini Flash API with   │
                   │  structured output schema:       │
                   │                                  │
                   │  Prompt:                          │
                   │  "Categorize these Indian credit  │
                   │  card transactions into one of:   │
                   │  [Food, Shopping, Travel, Bills,  │
                   │   Entertainment, Healthcare,      │
                   │   Fuel, Education, Other]"        │
                   │                                  │
                   │  Response: JSON array of          │
                   │  { description, category }        │
                   └──────────────────────────────────┘
```

**Cost Optimization:**
- Tier 1 + 2 should handle ~85-90% of transactions (zero cost, <1ms latency).
- Tier 3 batches all remaining unknowns into a **single** LLM call per statement.
- Gemini Flash pricing is negligible: ~$0.001–0.005 per statement for fallback transactions.

---

### 4. Dashboard Rendering

```
JSON Response received by Frontend
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│                    STATE MANAGEMENT                      │
│                                                          │
│  Store parsed response in React state / Zustand store   │
│  Derive computed values (totals, percentages, flags)    │
└─────────────────────────┬────────────────────────────────┘
                          │
              ┌───────────┴───────────────┐
              │                           │
              ▼                           ▼
   ┌──────────────────┐       ┌──────────────────────┐
   │  OVERVIEW CARDS   │       │  CHARTS               │
   │                   │       │                       │
   │  • Total Spend    │       │  • Category Pie Chart │
   │  • Avg Txn        │       │  • Daily Spend Line   │
   │  • Largest Txn    │       │  • Top Merchants Bar  │
   │  • Txn Count      │       │                       │
   └──────────────────┘       └──────────────────────┘
              │                           │
              ▼                           ▼
   ┌──────────────────┐       ┌──────────────────────┐
   │  RECURRING LIST   │       │  ANOMALY ALERTS      │
   │                   │       │                       │
   │  Subscriptions    │       │  Unusually large      │
   │  detected in      │       │  purchases flagged    │
   │  this cycle       │       │  with explanations    │
   └──────────────────┘       └──────────────────────┘
              │
              ▼
   ┌───────────────────────────────────────────────┐
   │  FULL TRANSACTION TABLE                        │
   │                                                │
   │  Columns: Date | Description | Category |      │
   │           Amount | Type (Debit/Credit)         │
   │                                                │
   │  Features: Sort, Filter by category,           │
   │            Search by description                │
   └───────────────────────────────────────────────┘
```

---

### 5. Optional — Persist to Database

```
User clicks "Save Insights"
              │
              ▼
   ┌───────────────────────┐
   │  Is user logged in?    │
   └───────────┬────────────┘
               │
    ┌─── YES ──┴── NO ───┐
    │                     │
    ▼                     ▼
  Save to DB        Show Auth Modal
  via Supabase      (Sign up / Login)
  client                  │
    │                     ▼
    │               After auth → Save
    │                     │
    ├─────────────────────┘
    │
    ▼
  ┌────────────────────────────────────────┐
  │  TABLES                                 │
  │                                         │
  │  users                                  │
  │  ├── id (UUID)                          │
  │  ├── email                              │
  │  └── created_at                         │
  │                                         │
  │  statements                             │
  │  ├── id (UUID)                          │
  │  ├── user_id (FK)                       │
  │  ├── bank_name                          │
  │  ├── statement_month                    │
  │  ├── total_spend                        │
  │  └── uploaded_at                        │
  │                                         │
  │  transactions                           │
  │  ├── id (UUID)                          │
  │  ├── statement_id (FK)                  │
  │  ├── date                               │
  │  ├── description (anonymized)           │
  │  ├── category                           │
  │  ├── amount                             │
  │  └── type (debit/credit)                │
  └────────────────────────────────────────┘
```

---

## Security & Privacy Workflow

```
THREAT                           MITIGATION
─────────────────────────────    ──────────────────────────────────────
Password intercepted in          pdf.js decrypts LOCALLY in browser.
transit                          Password never sent to backend.

PDF stored on server disk        Backend uses BytesIO (RAM only).
                                 Zero disk writes. Buffer cleared
                                 immediately after response.

Transaction data logged          No logging of transaction strings.
in server logs                   Structured logging only for errors
                                 (no PII in log messages).

Man-in-the-middle attack         HTTPS enforced on all endpoints.
on PDF upload                    TLS 1.3 minimum.

Database breach exposes          Only anonymized, categorized data
raw statements                   stored. Original PDF is never saved.
                                 User must explicitly opt-in to save.

LLM provider sees                Only unrecognized merchant STRINGS
full financial data              are sent (not amounts, dates, or
                                 user identifiers).
```

---

## Error Handling Workflow

```
Error Scenario                   Handling
───────────────                  ─────────────────────────────────────
Wrong PDF password               pdf.js throws PasswordException.
                                 Frontend shows: "Incorrect password.
                                 Try your PAN or Date of Birth."

Unsupported bank statement       Bank detector returns no match.
                                 Backend returns 400 with message:
                                 "We currently support HDFC, ICICI,
                                 and SBI statements only."

Corrupted / non-statement PDF    pdfplumber extracts zero rows.
                                 Backend returns 422:
                                 "Could not extract transactions.
                                 Please ensure this is a valid
                                 credit card statement."

LLM API rate limit / timeout     Categorize remaining transactions
                                 as "Uncategorized" and proceed.
                                 Never block the full response.

File too large (>10MB)           Frontend validates before upload.
                                 Backend enforces max file size.

Network error during upload      Frontend shows retry button with
                                 exponential backoff (max 3 retries).
```

---

## Deployment Workflow

```
┌─────────────────────────────────────────────────────┐
│                  DEPLOYMENT TARGETS                  │
│                                                      │
│  FRONTEND (Next.js)         BACKEND (FastAPI)        │
│  ─────────────────          ─────────────────        │
│  Vercel                     Railway / Render         │
│  (Free tier: sufficient)    (Free tier: sufficient)  │
│                                                      │
│  DATABASE (PostgreSQL)                               │
│  ─────────────────────                               │
│  Supabase Free Tier / Neon Free Tier                 │
│                                                      │
└─────────────────────────────────────────────────────┘

Deployment Steps:
─────────────────
1. Push backend to GitHub → Connect to Railway/Render
   ─ Set env vars: GEMINI_API_KEY, ALLOWED_ORIGINS
   ─ Health check endpoint: GET /health

2. Push frontend to GitHub → Connect to Vercel
   ─ Set env vars: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL
   ─ Auto-deploy on push to main branch

3. Set up Supabase project
   ─ Run migration SQL scripts
   ─ Configure Row Level Security (RLS) policies

4. Configure CORS on backend
   ─ Allow only the Vercel frontend domain

5. Set up monitoring
   ─ Vercel Analytics (frontend)
   ─ Railway logs (backend)
```

---

*Last updated: June 2026*
