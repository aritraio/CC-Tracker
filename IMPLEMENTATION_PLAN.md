# AI Financial Journal — Implementation Plan

> Technical blueprint for building the MVP from scratch.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Phase 1: Backend — Stateless Parsing Engine](#phase-1-backend--stateless-parsing-engine)
- [Phase 2: Frontend — Upload, Decryption & Dashboard](#phase-2-frontend--upload-decryption--dashboard)
- [Phase 3: Integration & End-to-End Testing](#phase-3-integration--end-to-end-testing)
- [Phase 4: Database & Authentication (Optional Save)](#phase-4-database--authentication-optional-save)
- [Phase 5: Polish, Deploy & Ship](#phase-5-polish-deploy--ship)
- [API Contract](#api-contract)
- [Data Models](#data-models)
- [Testing Strategy](#testing-strategy)
- [Environment Variables](#environment-variables)

---

## Project Structure

```
CC-Tracker/
│
├── README.md
├── WORKFLOW.md
├── IMPLEMENTATION_PLAN.md
├── TODO.md
│
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Env var template
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routes.py            # POST /parse endpoint
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract base parser
│   │   ├── detector.py              # Bank detection logic
│   │   ├── hdfc.py                  # HDFC parser
│   │   ├── icici.py                 # ICICI parser
│   │   └── sbi.py                   # SBI parser
│   │
│   ├── categorization/
│   │   ├── __init__.py
│   │   ├── engine.py                # 3-tier categorization orchestrator
│   │   ├── merchant_dictionary.json # Top 200+ Indian merchants
│   │   ├── regex_rules.py           # Category regex patterns
│   │   └── llm_fallback.py          # Gemini Flash API integration
│   │
│   ├── insights/
│   │   ├── __init__.py
│   │   └── calculator.py            # Compute totals, anomalies, recurring
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic response/request models
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_parsers.py
│       ├── test_categorization.py
│       ├── test_insights.py
│       └── fixtures/                # Mock PDF data / extracted text samples
│           ├── hdfc_sample.txt
│           ├── icici_sample.txt
│           └── sbi_sample.txt
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── .env.local.example
│   │
│   ├── public/
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout (fonts, metadata)
│   │   │   ├── page.tsx             # Landing / Upload page
│   │   │   └── dashboard/
│   │   │       └── page.tsx         # Insights dashboard
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                  # Shadcn UI components
│   │   │   ├── upload/
│   │   │   │   ├── DropZone.tsx     # Drag & drop file upload
│   │   │   │   ├── PasswordModal.tsx # PDF password input
│   │   │   │   └── UploadProgress.tsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── OverviewCards.tsx      # Total, avg, largest, count
│   │   │   │   ├── CategoryChart.tsx      # Pie/donut chart
│   │   │   │   ├── SpendTimeline.tsx      # Daily spend line chart
│   │   │   │   ├── TopMerchants.tsx       # Bar chart
│   │   │   │   ├── RecurringCharges.tsx   # Subscription list
│   │   │   │   ├── AnomalyAlerts.tsx      # Flagged transactions
│   │   │   │   └── TransactionTable.tsx   # Full sortable table
│   │   │   │
│   │   │   └── shared/
│   │   │       ├── Header.tsx
│   │   │       ├── Footer.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── pdf-decrypt.ts       # pdf.js local decryption logic
│   │   │   ├── api-client.ts        # Fetch wrapper for backend
│   │   │   └── utils.ts             # Formatters, helpers
│   │   │
│   │   ├── hooks/
│   │   │   ├── useStatementUpload.ts
│   │   │   └── useDashboardData.ts
│   │   │
│   │   └── types/
│   │       └── index.ts             # TypeScript interfaces
│   │
│   └── tailwind.config.ts
│
└── docs/
    ├── sample-statements/           # Redacted sample PDFs for testing
    └── api-spec.md                  # API documentation
```

---

## Phase 1: Backend — Stateless Parsing Engine

### 1.1 Project Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pdfplumber python-multipart python-dotenv pydantic google-generativeai pytest httpx
pip freeze > requirements.txt
```

**Key Dependencies:**
| Package | Purpose |
|---------|---------|
| `fastapi` | API framework |
| `uvicorn` | ASGI server |
| `pdfplumber` | PDF table extraction |
| `python-multipart` | File upload handling |
| `python-dotenv` | Environment variables |
| `pydantic` | Request/response validation |
| `google-generativeai` | Gemini Flash LLM fallback |
| `pytest` + `httpx` | Testing |

---

### 1.2 Pydantic Models (`models/schemas.py`)

```python
from pydantic import BaseModel
from typing import Literal
from datetime import date

class Transaction(BaseModel):
    date: date
    description: str
    amount: float
    type: Literal["debit", "credit"]
    category: str | None = None

class RecurringCharge(BaseModel):
    merchant: str
    amount: float
    category: str

class Anomaly(BaseModel):
    transaction: Transaction
    reason: str  # e.g., "3.2x above your average spend"

class InsightsResponse(BaseModel):
    bank: str
    statement_period: str
    total_spend: float
    total_credits: float
    average_transaction: float
    largest_transaction: Transaction
    transaction_count: int
    category_breakdown: dict[str, float]   # { "Food": 12500.00, ... }
    recurring_charges: list[RecurringCharge]
    anomalies: list[Anomaly]
    transactions: list[Transaction]
```

---

### 1.3 Bank Detection (`parsers/detector.py`)

**Logic:**
1. Extract text from the first page of the PDF using `pdfplumber`.
2. Match against known bank signature strings.
3. Return the bank identifier or raise an error.

```python
BANK_SIGNATURES = {
    "hdfc": ["hdfc bank", "hdfc credit card"],
    "icici": ["icici bank", "icici credit card"],
    "sbi": ["sbi card", "state bank of india", "sbi credit card"],
}

def detect_bank(first_page_text: str) -> str:
    text_lower = first_page_text.lower()
    for bank, signatures in BANK_SIGNATURES.items():
        if any(sig in text_lower for sig in signatures):
            return bank
    raise ValueError("Unsupported bank statement")
```

---

### 1.4 Bank-Specific Parsers

Each parser inherits from `BaseParser` and implements:

```python
# parsers/base.py
from abc import ABC, abstractmethod
from models.schemas import Transaction

class BaseParser(ABC):
    @abstractmethod
    def extract_transactions(self, pdf_bytes: bytes) -> list[Transaction]:
        """Extract all transactions from the PDF bytes."""
        pass

    @abstractmethod
    def extract_statement_period(self, pdf_bytes: bytes) -> str:
        """Extract the billing period string."""
        pass
```

**HDFC Parser Implementation Notes:**
- HDFC statements typically have columns: `Date | Transaction Description | Amount (INR) | CR/DR`
- Table boundaries can be identified by header row text.
- Watch out for multi-line descriptions (wrapped text).
- Handle both domestic and international transactions.

**ICICI Parser Implementation Notes:**
- ICICI format differs: `Date | Mode | Particulars | Amount (₹) | Balance`
- Some statements use landscape orientation.
- EMI transactions appear as separate line items.

**SBI Parser Implementation Notes:**
- SBI statements: `Transaction Date | Details | Amount | Debit/Credit`
- Rewards points summary may appear inline and must be filtered out.

---

### 1.5 Categorization Engine (`categorization/engine.py`)

**Merchant Dictionary Structure (`merchant_dictionary.json`):**
```json
{
  "zomato": "Food & Dining",
  "swiggy": "Food & Dining",
  "netflix": "Entertainment",
  "spotify": "Entertainment",
  "amazon": "Shopping",
  "flipkart": "Shopping",
  "uber": "Transport",
  "ola": "Transport",
  "airtel": "Bills & Utilities",
  "reliance jio": "Bills & Utilities",
  "apollo pharmacy": "Healthcare",
  "makemytrip": "Travel",
  "irctc": "Travel",
  "shell": "Fuel",
  "indian oil": "Fuel"
}
```
> Build this out to 200+ merchants covering all major Indian brands.

**Regex Rules (`regex_rules.py`):**
```python
CATEGORY_PATTERNS = {
    "Food & Dining": r"(?i)(restaurant|cafe|pizza|biryani|food|kitchen|dhaba|bakery)",
    "Fuel": r"(?i)(petrol|diesel|fuel|hp\s|bpcl|iocl|shell|indian oil)",
    "Bills & Utilities": r"(?i)(airtel|jio|vodafone|electricity|water|broadband|wifi)",
    "Healthcare": r"(?i)(pharma|medic|hospital|clinic|diagnos|lab|apollo|fortis)",
    "Travel": r"(?i)(airways|airline|flight|hotel|resort|booking|makemytrip|irctc)",
    "Entertainment": r"(?i)(cinema|pvr|inox|multiplex|gaming|playstation|steam)",
    "Education": r"(?i)(school|college|university|course|udemy|coursera|academy)",
    "Shopping": r"(?i)(mall|store|mart|retail|fashion|clothing|myntra|ajio)",
}
```

**LLM Fallback (`llm_fallback.py`):**
```python
import google.generativeai as genai

CATEGORIES = [
    "Food & Dining", "Shopping", "Travel", "Bills & Utilities",
    "Entertainment", "Healthcare", "Fuel", "Education",
    "Transport", "Groceries", "Other"
]

async def categorize_with_llm(descriptions: list[str]) -> dict[str, str]:
    """
    Batch categorize unrecognized transaction descriptions.
    Returns: { "description": "category" }
    """
    prompt = f"""Categorize each of these Indian credit card transaction 
    descriptions into exactly ONE of these categories: {CATEGORIES}
    
    Transactions:
    {chr(10).join(f'- {d}' for d in descriptions)}
    
    Return JSON: [{{"description": "...", "category": "..."}}]"""
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )
    # Parse and return mapping
```

---

### 1.6 Insights Calculator (`insights/calculator.py`)

**Computed Metrics:**

| Metric | Calculation |
|--------|-------------|
| Total Spend | Sum of all debit transactions |
| Total Credits | Sum of all credit transactions (payments, refunds) |
| Average Transaction | Total spend / debit transaction count |
| Largest Transaction | Max amount debit transaction |
| Category Breakdown | Group by category → sum amounts |
| Recurring Charges | Identify merchants appearing in ≥2 consecutive months OR known subscription names |
| Anomalies | Transactions where `amount > mean + 2*stddev` of same category |

**Recurring Detection Logic:**
```python
def detect_recurring(transactions: list[Transaction]) -> list[RecurringCharge]:
    """
    A charge is "recurring" if:
    1. The same merchant appears with similar amounts (±10% variance)
    2. OR the merchant name matches known subscription services
    """
    KNOWN_SUBSCRIPTIONS = [
        "netflix", "spotify", "prime", "hotstar", "youtube",
        "icloud", "google one", "linkedin", "chatgpt"
    ]
    # ... implementation
```

---

### 1.7 API Endpoint (`api/v1/routes.py`)

```python
from fastapi import APIRouter, UploadFile, HTTPException
from io import BytesIO

router = APIRouter(prefix="/api/v1")

@router.post("/parse", response_model=InsightsResponse)
async def parse_statement(file: UploadFile):
    # 1. Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(400, "Only PDF files accepted")
    
    # 2. Read into memory (NO disk write)
    pdf_bytes = await file.read()
    
    try:
        # 3. Detect bank
        bank = detect_bank(pdf_bytes)
        
        # 4. Parse transactions
        parser = get_parser(bank)
        transactions = parser.extract_transactions(pdf_bytes)
        period = parser.extract_statement_period(pdf_bytes)
        
        # 5. Categorize
        transactions = await categorize_all(transactions)
        
        # 6. Calculate insights
        insights = calculate_insights(transactions, bank, period)
        
        return insights
    finally:
        # 7. Explicitly clear buffer
        del pdf_bytes
```

---

## Phase 2: Frontend — Upload, Decryption & Dashboard

### 2.1 Project Setup

```bash
cd frontend
npx -y create-next-app@latest ./ --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm
npx -y shadcn@latest init
npm install pdfjs-dist recharts lucide-react
```

**Install Shadcn Components:**
```bash
npx shadcn@latest add button card input dialog table badge alert progress
```

---

### 2.2 PDF Local Decryption (`lib/pdf-decrypt.ts`)

```typescript
import * as pdfjsLib from 'pdfjs-dist';

// Set worker source
pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

export async function decryptPDF(
  file: File,
  password?: string
): Promise<Blob> {
  const arrayBuffer = await file.arrayBuffer();
  
  const loadingTask = pdfjsLib.getDocument({
    data: arrayBuffer,
    password: password || '',
  });
  
  try {
    const pdfDoc = await loadingTask.promise;
    // PDF loaded successfully (was either unencrypted or password worked)
    // Return original file as blob for upload
    return new Blob([arrayBuffer], { type: 'application/pdf' });
  } catch (error: any) {
    if (error.name === 'PasswordException') {
      if (error.code === 1) {
        // NEED_PASSWORD — file is encrypted, no password provided
        throw new Error('PASSWORD_REQUIRED');
      }
      if (error.code === 2) {
        // INCORRECT_PASSWORD
        throw new Error('INCORRECT_PASSWORD');
      }
    }
    throw error;
  }
}
```

---

### 2.3 Key Frontend Components

#### DropZone Component
- Drag & drop area with visual feedback.
- Accepts only `.pdf` files.
- Max file size: 10MB (validated client-side).
- Shows file name and size after selection.

#### Password Modal
- Triggered when `PASSWORD_REQUIRED` error is caught.
- Hints: "Most banks use your PAN number or Date of Birth (DDMMYYYY) as the password."
- Shows error state for incorrect passwords.
- Auto-focuses the input field.

#### Dashboard Components
- **OverviewCards:** 4 metric cards with icons (Total Spend, Avg, Largest, Count).
- **CategoryChart:** Donut chart via `recharts` with category colors.
- **SpendTimeline:** Area/line chart showing daily spending.
- **TopMerchants:** Horizontal bar chart of top 10 merchants by spend.
- **RecurringCharges:** Card list with merchant name, amount, category badge.
- **AnomalyAlerts:** Warning-styled cards with transaction details and reason.
- **TransactionTable:** Full table with sorting, category filter, and search.

---

### 2.4 Design System

**Color Palette (Dark Mode First):**
```css
--background:    hsl(224, 30%, 8%);     /* Deep navy-black */
--surface:       hsl(224, 25%, 12%);    /* Card backgrounds */
--surface-hover: hsl(224, 25%, 16%);    /* Hover states */
--border:        hsl(224, 20%, 20%);    /* Subtle borders */
--text-primary:  hsl(210, 40%, 95%);    /* White-ish */
--text-secondary:hsl(215, 20%, 65%);    /* Muted text */
--accent:        hsl(250, 90%, 65%);    /* Electric indigo */
--accent-glow:   hsl(250, 90%, 65%, 0.15); /* Glow effects */
--success:       hsl(145, 65%, 50%);    /* Green for credits */
--danger:        hsl(0, 75%, 60%);      /* Red for anomalies */
--warning:       hsl(38, 90%, 55%);     /* Amber for alerts */
```

**Typography:**
```css
--font-heading: 'Outfit', sans-serif;   /* Modern geometric */
--font-body:    'Inter', sans-serif;    /* Clean readability */
--font-mono:    'JetBrains Mono', monospace; /* Numbers & amounts */
```

**Category Colors:**
```
Food & Dining    → hsl(15, 85%, 55%)    // Warm orange
Shopping         → hsl(280, 70%, 60%)   // Purple
Travel           → hsl(200, 80%, 55%)   // Blue
Bills & Utilities→ hsl(175, 60%, 45%)   // Teal
Entertainment    → hsl(340, 75%, 55%)   // Pink
Healthcare       → hsl(145, 60%, 50%)   // Green
Fuel             → hsl(45, 85%, 50%)    // Yellow
Transport        → hsl(220, 70%, 55%)   // Royal blue
Groceries        → hsl(100, 50%, 50%)   // Lime green
Education        → hsl(260, 50%, 55%)   // Lavender
Other            → hsl(215, 15%, 50%)   // Grey
```

---

## Phase 3: Integration & End-to-End Testing

### 3.1 Integration Checklist

- [ ] Frontend uploads decrypted PDF → Backend receives it correctly
- [ ] Backend returns valid `InsightsResponse` JSON
- [ ] Frontend renders all dashboard components without errors
- [ ] Error states display correctly (wrong password, unsupported bank, corrupted PDF)
- [ ] CORS configured correctly between frontend and backend
- [ ] File size limit enforced on both frontend and backend
- [ ] Loading states show during processing

### 3.2 Test with Real Statements

> **Critical:** Test with at least 3 real statements per supported bank.

| Bank | Variants to Test |
|------|-----------------|
| HDFC | Regalia, Millennia, Infinia |
| ICICI | Amazon Pay, Coral, Platinum |
| SBI  | SimplySave, IRCTC, Elite |

---

## Phase 4: Database & Authentication (Optional Save)

### 4.1 Supabase Setup

```sql
-- Users table (handled by Supabase Auth)

CREATE TABLE statements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    bank_name TEXT NOT NULL,
    statement_period TEXT NOT NULL,
    total_spend DECIMAL(12,2) NOT NULL,
    total_credits DECIMAL(12,2) DEFAULT 0,
    transaction_count INTEGER NOT NULL,
    category_breakdown JSONB NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    statement_id UUID REFERENCES statements(id) ON DELETE CASCADE,
    txn_date DATE NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    type TEXT CHECK (type IN ('debit', 'credit')) NOT NULL
);

-- Row Level Security
ALTER TABLE statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access own statements"
    ON statements FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access own transactions"
    ON transactions FOR ALL
    USING (statement_id IN (
        SELECT id FROM statements WHERE user_id = auth.uid()
    ));
```

---

## Phase 5: Polish, Deploy & Ship

### 5.1 Polish Checklist

- [ ] Dark mode is the default; light mode toggle available
- [ ] All charts have smooth entry animations
- [ ] Responsive layout works on mobile (min 375px width)
- [ ] Loading skeleton screens instead of blank states
- [ ] Empty states with helpful messaging
- [ ] SEO meta tags on all pages
- [ ] Favicon and Open Graph images

### 5.2 Deployment

| Component | Platform | Free Tier |
|-----------|----------|-----------|
| Frontend | Vercel | ✅ Generous |
| Backend | Railway / Render | ✅ (with sleep on inactivity) |
| Database | Supabase | ✅ 500MB, 50k rows |
| LLM | Google AI Studio | ✅ Free tier for Gemini Flash |

### 5.3 Performance Targets

| Metric | Target |
|--------|--------|
| PDF Parse Time | < 3 seconds for a typical 3-page statement |
| Dashboard Render | < 500ms after data received |
| Lighthouse Score | > 90 (Performance, Accessibility, SEO) |
| Bundle Size (Frontend) | < 500KB gzipped |

---

## API Contract

### `POST /api/v1/parse`

**Request:**
```
Content-Type: multipart/form-data
Body: file (PDF binary)
```

**Success Response (200):**
```json
{
  "bank": "hdfc",
  "statement_period": "May 2026",
  "total_spend": 45230.50,
  "total_credits": 5000.00,
  "average_transaction": 1507.68,
  "largest_transaction": {
    "date": "2026-05-15",
    "description": "AMAZON INDIA MARKETPLACE",
    "amount": 12499.00,
    "type": "debit",
    "category": "Shopping"
  },
  "transaction_count": 30,
  "category_breakdown": {
    "Food & Dining": 8500.00,
    "Shopping": 15200.00,
    "Travel": 6800.00,
    "Bills & Utilities": 4500.00,
    "Entertainment": 2999.00,
    "Fuel": 3500.00,
    "Other": 3731.50
  },
  "recurring_charges": [
    { "merchant": "Netflix", "amount": 649.00, "category": "Entertainment" },
    { "merchant": "Spotify", "amount": 119.00, "category": "Entertainment" }
  ],
  "anomalies": [
    {
      "transaction": {
        "date": "2026-05-15",
        "description": "AMAZON INDIA MARKETPLACE",
        "amount": 12499.00,
        "type": "debit",
        "category": "Shopping"
      },
      "reason": "This purchase is 3.2x your average transaction amount"
    }
  ],
  "transactions": [
    {
      "date": "2026-05-01",
      "description": "SWIGGY ORDER",
      "amount": 450.00,
      "type": "debit",
      "category": "Food & Dining"
    }
  ]
}
```

**Error Responses:**
| Code | Scenario | Body |
|------|----------|------|
| 400 | Invalid file type | `{ "detail": "Only PDF files accepted" }` |
| 400 | Unsupported bank | `{ "detail": "Unsupported bank. We support HDFC, ICICI, and SBI." }` |
| 422 | Parse failure | `{ "detail": "Could not extract transactions from this PDF." }` |
| 413 | File too large | `{ "detail": "File exceeds 10MB limit." }` |
| 500 | Server error | `{ "detail": "Internal server error. Please try again." }` |

---

## Testing Strategy

### Backend Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

| Test File | Coverage |
|-----------|----------|
| `test_parsers.py` | Bank detection, per-bank extraction accuracy |
| `test_categorization.py` | Dictionary lookup, regex matching, LLM fallback mocking |
| `test_insights.py` | Totals, averages, recurring detection, anomaly flagging |

### Frontend Tests

```bash
cd frontend
npm run test
```

- Component rendering tests (React Testing Library).
- PDF decryption error handling.
- API response rendering.

### Manual E2E Testing

Use real (redacted) statements from HDFC, ICICI, and SBI to validate full pipeline.

---

## Environment Variables

### Backend (`.env`)
```env
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:3000
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
```

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url  # Phase 4 only
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key  # Phase 4 only
```

---

*Last updated: June 2026*
