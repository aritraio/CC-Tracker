# AGENTS.md — CC Track Engineering Guidelines & Agent Operating Manual

> **Mission:** CC Track transforms unstructured credit card PDF statements into structured, mathematically validated transactions and delivers deterministic, evidence-based spending intelligence and behavioral recommendations.

---

## 1. System Overview & Core Philosophy

Every AI agent working in this repository must operate according to the following fundamental principles:

1. **Correctness Beats AI:** Financial data requires 100% mathematical integrity. A single hallucinated number or incorrect transaction total destroys user trust.
2. **Rules & Statistics Before ML:** Always prefer deterministic rules, explicit regex patterns, hash maps, and verified statistical calculations (e.g., rolling averages, medians, z-scores) over machine learning models.
3. **LLM Explains, Analytics Computes:**
   - **Backend Analytics Engine:** Computes totals, category distributions, deltas, anomalies, recurring payments, and raw rule triggers.
   - **LLM Layer:** Formats validated structured facts into empathetic, concise, and actionable human explanations.
   - **NEVER** allow an LLM to calculate balances, extract transaction rows directly, or estimate financial savings without structured data evidence.
4. **Reconciliation is Mandatory:** Every parsed statement must compare its extracted line-item sum against the document's printed summary totals (e.g., total debits/credits or total amount due). If totals do not reconcile within an allowable rounding tolerance ($\le ₹1.00$), flag the statement as `REVIEW_REQUIRED`.
5. **Privacy by Architecture:**
   - Client-side decryption: Encrypted statements are unlocked in the user's browser using `pdf.js`. Passwords (PAN/DOB) must **never** be transmitted over the network or logged.
   - Ephemeral in-memory parsing: Backend processes PDFs strictly in RAM (`io.BytesIO`). Zero disk writes for raw statements unless explicitly stored in encrypted user vaults with user consent.
   - Data minimization: Never store full 16-digit PANs or CVVs. Only store masked identifiers (e.g., `last_4_digits`, issuer name).
   - Minimal LLM exposure: Send only anonymized merchant strings or aggregated category summaries to LLM endpoints.

---

## 2. Tech Stack Reference

| Subsystem | Technology | Version / Tooling | Purpose |
|---|---|---|---|
| **Frontend Web** | Next.js (App Router), TypeScript | Next.js 14+, React 18+, TS 5+ | Single Page / SSR Web Application |
| **Styling & UI** | Tailwind CSS, shadcn/ui, Lucide React | Tailwind v3+, Radix UI | Accessible, high-polish UI components |
| **Charts** | Recharts | Latest stable | Financial charts, timelines, breakdowns |
| **Client PDF** | `pdfjs-dist` | Latest stable | Client-side password unlocking & validation |
| **Backend API** | FastAPI (Python) | Python 3.11+, FastAPI 0.110+ | High-performance asynchronous REST API |
| **Data Validation** | Pydantic v2 | Pydantic 2.6+ | Strict typed request/response contracts |
| **PDF Extraction**| `pdfplumber`, `PyMuPDF` (fitz) | Latest stable | Coordinate-based PDF table & text extraction |
| **Data Processing**| `pandas`, `numpy` | Latest stable | Vectorized analytics, rolling aggregations |
| **Database** | PostgreSQL | PostgreSQL 15+ / Supabase | Relational store for users, cards, transactions |
| **AI / LLM** | Google Gemini API / OpenAI API | Gemini 1.5 Flash / GPT-4o-mini | Structured insight explanations & merchant fallback |

---

## 3. Project Directory Structure

```text
CC-Tracker/
├── AGENTS.md                  # This file (Agent operating manual)
├── PRD.md                     # Product Requirements Document
├── tasks.md                   # Step-by-step ordered implementation plan
├── ideas.md                   # Core product blueprint and strategic vision
│
├── apps/
│   ├── web/                   # Next.js Frontend Application
│   │   ├── src/
│   │   │   ├── app/           # App Router pages & API routes
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx   # Landing / Upload view
│   │   │   │   └── dashboard/ # Analytics & recommendations dashboard
│   │   │   ├── components/
│   │   │   │   ├── ui/        # shadcn/ui components (button, card, dialog, etc.)
│   │   │   │   ├── upload/    # DropZone, DecryptModal, ProgressTracker
│   │   │   │   ├── dashboard/ # OverviewCards, Charts, AnomalyList
│   │   │   │   ├── insights/  # RecommendationCard, FeedbackActions
│   │   │   │   └── table/     # TransactionTable, FilterBar, CategorySelect
│   │   │   ├── lib/           # API client, formatting utils, client-side PDF tools
│   │   │   ├── types/         # TypeScript shared interfaces
│   │   │   └── hooks/         # Custom React hooks
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   └── package.json
│   │
│   └── api/                   # FastAPI Backend Application
│       ├── app/
│       │   ├── main.py        # FastAPI entrypoint, middleware, routers
│       │   ├── core/          # Config, security, exceptions, logging
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── router.py
│       │   │       └── endpoints/ # upload, statements, analytics, recommendations
│       │   ├── models/        # SQLAlchemy / SQLModel database entities
│       │   ├── schemas/       # Pydantic v2 schemas (requests & responses)
│       │   ├── parsers/       # Multi-bank statement extraction engine
│       │   │   ├── base.py    # BaseParser abstract interface
│       │   │   ├── detector.py# Bank signature detection
│       │   │   ├── hdfc.py    # HDFC statement parser
│       │   │   ├── icici.py   # ICICI statement parser
│       │   │   ├── sbi.py     # SBI statement parser
│       │   │   ├── axis.py    # Axis Bank parser
│       │   │   └── amex.py    # American Express parser
│       │   ├── categorization/# 3-tier categorization engine
│       │   │   ├── engine.py  # Orchestrator (Dictionary -> Regex -> LLM)
│       │   │   ├── dictionary.json # 250+ top Indian merchants
│       │   │   ├── regex_rules.py  # Heuristic regex patterns
│       │   │   └── llm_fallback.py # Batch LLM categorization client
│       │   ├── analytics/     # Deterministic computation engine
│       │   │   ├── calculator.py   # Spend totals, averages, velocity
│       │   │   ├── recurring.py    # Subscription & recurring detection
│       │   │   ├── anomalies.py    # Statistical anomaly & spike detection
│       │   │   └── profile.py      # Historical rolling user profiles
│       │   ├── recommendations/    # Rule-based recommendation engine
│       │   │   ├── engine.py       # Recommendation triggers & savings math
│       │   │   └── templates.py    # Evidence builders & prompt structures
│       │   └── services/      # Business logic orchestration
│       ├── tests/             # Backend test suite
│       │   ├── test_parsers.py
│       │   ├── test_reconciliation.py
│       │   ├── test_categorization.py
│       │   ├── test_analytics.py
│       │   ├── test_recommendations.py
│       │   └── fixtures/      # Anonymized sample text/PDF fixtures
│       ├── requirements.txt
│       └── Dockerfile
```

---

## 4. Code Style & Implementation Guidelines

### 4.1 Python / FastAPI Standards

- **Strict Type Annotations:** All function signatures, class methods, and return types must be fully typed. Use `typing` / Python 3.10+ native types (`list[str]`, `dict[str, Any]`, `str | None`).
- **Pydantic v2 Everywhere:** All request payloads, response schemas, and intermediate pipeline data structures must be Pydantic `BaseModel` classes with `ConfigDict(strict=True, from_attributes=True)`.
- **Stateless Buffer Processing:** Never write incoming statement files to local disk paths like `/tmp` or `./uploads`. Read `UploadFile.file` directly into `io.BytesIO`.
- **Clear Separation of Concerns:**
  - Parsers extract raw text/tables into `ParsedStatement`.
  - Normalizers clean merchant strings and assign `TransactionType`.
  - Categorizer assigns `category` and `subcategory`.
  - Validator checks arithmetic balance against statement headers.
  - Analytics computes metrics.
  - LLM layer formats human insights.

#### Python Code Example: Parser Abstraction

```python
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from enum import Enum
import io
from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    PURCHASE = "PURCHASE"
    REFUND = "REFUND"
    REVERSAL = "REVERSAL"
    PAYMENT = "PAYMENT"
    FEE = "FEE"
    INTEREST = "INTEREST"
    GST = "GST"
    EMI = "EMI"
    CASH_WITHDRAWAL = "CASH_WITHDRAWAL"
    REWARD = "REWARD"
    ADJUSTMENT = "ADJUSTMENT"
    UNKNOWN = "UNKNOWN"


class ExtractedTransaction(BaseModel):
    transaction_date: date
    post_date: date | None = None
    merchant_raw: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    transaction_type: TransactionType
    currency: str = "INR"
    source_page: int
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)


class StatementHeader(BaseModel):
    issuer: str
    card_last_4: str | None = None
    statement_period_start: date | None = None
    statement_period_end: date | None = None
    total_amount_due: Decimal | None = None
    minimum_amount_due: Decimal | None = None
    payment_due_date: date | None = None
    credit_limit: Decimal | None = None
    available_credit: Decimal | None = None
    opening_balance: Decimal | None = None
    total_debits: Decimal | None = None
    total_credits: Decimal | None = None


class ParsedStatement(BaseModel):
    header: StatementHeader
    transactions: list[ExtractedTransaction]
    raw_text_length: int
    reconciliation_status: str  # "VALIDATED" | "REVIEW_REQUIRED"
    reconciliation_discrepancy: Decimal = Decimal("0.00")


class BaseStatementParser(ABC):
    @abstractmethod
    def identify(self, first_page_text: str) -> bool:
        """Return True if this parser supports the given statement text signature."""
        pass

    @abstractmethod
    def parse(self, pdf_stream: io.BytesIO) -> ParsedStatement:
        """Extract header metadata and structured transactions from the PDF stream."""
        pass
```

### 4.2 TypeScript / Next.js Standards

- **App Router & Server/Client Components:** Mark client-interactive components explicitly with `'use client';`. Keep layout and static wrappers as Server Components.
- **Strict Typing:** No `any`. Define shared TypeScript types matching the backend Pydantic models.
- **Client-Side Decryption:**
  ```typescript
  import * as pdfjsLib from 'pdfjs-dist';

  export async function unlockAndExtractPdf(
    fileBuffer: ArrayBuffer,
    password?: string
  ): Promise<{ decryptedBuffer: ArrayBuffer; pageCount: number }> {
    const loadingTask = pdfjsLib.getDocument({
      data: new Uint8Array(fileBuffer),
      password: password || '',
    });
    const pdfDoc = await loadingTask.promise;
    // Process or forward unlocked document buffer
    return { decryptedBuffer: fileBuffer, pageCount: pdfDoc.numPages };
  }
  ```
- **shadcn/ui & Tailwind:** Use standard design tokens (CSS variables for colors, dark mode support, glassmorphism, responsive grids).

---

## 5. Explicit Agent Boundaries & Prohibited Behaviors

To maintain safety, privacy, and system integrity, agents **MUST NEVER**:

1. **NEVER** save or write unencrypted PDF files or passwords to local disk, temporary folders (`/tmp`), or system logs.
2. **NEVER** send full credit card numbers (16 digits), CVVs, user passwords, or bank account login credentials to any external API or LLM endpoint.
3. **NEVER** let an LLM perform mathematical arithmetic or determine financial summary totals. All calculations must be executed via deterministic Python code.
4. **NEVER** provide generalized, unsubstantiated advice (e.g. "people your age spend less on food"). Every recommendation must reference concrete user transactions with calculated savings.
5. **NEVER** present parsed statement totals to the user without running the reconciliation check. Discrepancies must be explicitly surfaced with a `REVIEW REQUIRED` status.
6. **NEVER** execute dangerous shell commands or modify files outside `/Users/aritra/Code/Projects/CC-Tracker`.
7. **NEVER** use Tailwind arbitrary class hacks where existing design system tokens are available.

---

## 6. Testing & Quality Verification Commands

Whenever you implement or modify features, you must run the following validation commands to verify correctness:

### Backend Verification (Python)

```bash
# Navigate to backend
cd /Users/aritra/Code/Projects/CC-Tracker/apps/api

# Run all unit and integration tests with coverage
pytest --cov=app --cov-report=term-missing tests/

# Test specific statement parsers
pytest tests/test_parsers.py -k "hdfc or icici or sbi"

# Run linter and formatter checks
ruff check app tests
black --check app tests

# Run strict static type checking
mypy app
```

### Frontend Verification (Next.js)

```bash
# Navigate to frontend
cd /Users/aritra/Code/Projects/CC-Tracker/apps/web

# Run TypeScript typecheck
npm run typecheck # or npx tsc --noEmit

# Run ESLint
npm run lint

# Run UI / Unit tests
npm run test

# Run Next.js production build check
npm run build
```

---

## 7. Error Handling & Structured Responses

All API endpoints must return structured JSON error responses conforming to standard RFC 7807 problem details:

```json
{
  "error_code": "STATEMENT_RECONCILIATION_FAILED",
  "message": "Extracted transaction total (₹46,987.00) does not match statement total debits (₹47,823.00). Discrepancy: ₹836.00.",
  "details": {
    "extracted_total": 46987.00,
    "statement_total": 47823.00,
    "discrepancy": 836.00,
    "unparsed_lines_count": 2
  }
}
```

Never fail silently or catch-all exceptions without logging structured context (excluding PII).
