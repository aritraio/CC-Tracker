# CC Track — Product & Technical Blueprint

## 1. Product Overview

**CC Track** is a web application where users upload credit-card statements and receive a structured, visual, and personalized understanding of their spending.

The product should not stop at:

> "Here is a pie chart of your spending."

Its long-term goal is:

> "Here is what changed in your spending, why it matters, and what you can realistically do to spend less."

### Core product loop

```text
Upload Statement
       ↓
Extract Transactions
       ↓
Normalize + Validate
       ↓
Categorize Merchants
       ↓
Analyze Spending
       ↓
Detect Patterns / Anomalies
       ↓
Generate Personalized Recommendations
       ↓
Explain Findings Clearly
       ↓
User Takes Action
       ↓
Track Outcome
       ↓
Improve Personalization
```

---

# 2. Product Thesis

The basic statement analyzer is not a strong moat because PDF parsing, charts, categorization, recurring-payment detection, and AI summaries already exist in competing products.

The stronger opportunity is a **personal spending intelligence layer**.

### Product positioning

Instead of:

> Credit-card statement visualizer

Use the product concept:

> **CC Track turns a messy credit-card statement into actionable financial intelligence.**

### Primary user questions

CC Track should eventually answer:

1. Where did my money go?
2. What changed compared with previous months?
3. What spending patterns are hurting me?
4. Which purchases or subscriptions should I review?
5. Where can I realistically cut spending?
6. Did the recommendation actually help me spend less?

---

# 3. MVP Scope

The MVP should validate one hypothesis:

> **Users find personalized spending findings more useful than a normal spending chart.**

## MVP input

Support:

- PDF credit-card statements
- A limited set of common Indian card issuers initially
- One statement at a time

Do not initially support:

- Bank API integrations
- Account Aggregator integrations
- Mobile applications
- Multiple financial accounts
- Complex reward optimization
- Fully automated OCR for every document

## MVP output

### Overview

- Total spending
- Number of transactions
- Average transaction
- Largest transaction
- Statement period
- Amount due
- Minimum amount due
- Due date
- Credit limit / utilization when available

### Visualizations

- Spending by category
- Spending over time
- Top merchants
- Transaction distribution

### Key findings

Generate 5–10 useful findings such as:

- Food spending increased 32% month-over-month.
- Shopping represents 27% of total spend.
- A single transaction is unusually large compared with the user's history.
- Several recurring payments were detected.
- Weekend spending is significantly higher than weekday spending.
- Transaction frequency increased even though average transaction size stayed stable.

### Recommendations

For the first version, recommendations should come from deterministic rules and statistical analysis, not a trained ML model.

Example:

> Food delivery spending increased 38% this month and represents 21% of discretionary spending. Reducing food-delivery purchases by two orders per week could save approximately ₹1,000–₹1,500 per month.

Every recommendation should clearly show the evidence behind it.

---

# 4. Long-Term Product Vision

CC Track can evolve through four stages.

## Stage 1 — Statement Analyzer

```text
PDF → Transactions → Dashboard → Findings
```

## Stage 2 — Personal Spending Intelligence

```text
Historical statements
        ↓
Personal spending profile
        ↓
Pattern detection
        ↓
Personalized recommendations
```

## Stage 3 — Behavioral Coach

```text
Recommendation
      ↓
User action
      ↓
Next month's behavior
      ↓
Measure result
      ↓
Learn what works
```

## Stage 4 — Credit-Card Optimization

Eventually include:

- Credit utilization monitoring
- Annual-fee awareness
- Reward optimization
- EMI analysis
- Interest / finance-charge analysis
- Subscription cleanup
- Card-specific spending recommendations
- Cross-card comparisons

The product should only move into this area once the basic transaction pipeline is highly reliable.

---

# 5. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      Next.js UI      │
                         │                      │
                         │ Upload               │
                         │ Dashboard            │
                         │ Transactions         │
                         │ Findings             │
                         │ Recommendations      │
                         └──────────┬───────────┘
                                    │ HTTPS / REST
                                    ↓
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │                      │
                         │ Auth / API           │
                         │ Upload handling      │
                         │ Analysis endpoints   │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼──────────────────────┐
              │                     │                      │
              ↓                     ↓                      ↓
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │ Document Pipeline │  │ PostgreSQL       │  │ Analytics Engine │
    │                  │  │                  │  │                  │
    │ PDF extraction   │  │ users            │  │ totals           │
    │ OCR fallback     │  │ cards            │  │ trends           │
    │ issuer detection │  │ statements       │  │ anomalies        │
    │ transaction parse│  │ transactions     │  │ recurring        │
    │ normalization    │  │ findings         │  │ patterns         │
    └────────┬─────────┘  │ recommendations  │  └────────┬─────────┘
             │            └──────────────────┘           │
             └──────────────────────┬────────────────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ Recommendation       │
                         │ Engine               │
                         │                      │
                         │ Rules                │
                         │ Statistics           │
                         │ User history         │
                         │ Confidence scoring   │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ LLM Explanation      │
                         │ Layer                │
                         │                      │
                         │ Explain facts        │
                         │ Summarize findings   │
                         │ Personalize language │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ Dashboard            │
                         └──────────────────────┘
```

---

# 6. Detailed Data Workflow

## Step 1 — Upload

User uploads a statement PDF.

Backend should immediately:

1. Validate file type.
2. Validate file size.
3. Generate a cryptographic file hash.
4. Store the file securely or process it temporarily.
5. Create a statement-processing job.

### Duplicate detection

Use a hash plus statement metadata to prevent accidental duplicate imports.

```text
SHA-256(file)
       ↓
Duplicate check
       ↓
Already exists? → Reject / offer reprocess
```

---

## Step 2 — Document extraction

### First attempt: text extraction

Use:

- PyMuPDF
- pdfplumber

Avoid OCR unless the PDF is actually scanned or text extraction fails.

### Fallback

```text
PDF
 ↓
Can extract useful text?
 ├── YES → structured parser
 └── NO  → render pages → OCR → parser
```

OCR should be isolated behind the same parser interface so the rest of the system does not care where the text came from.

---

# 7. Issuer Detection

The system should identify the statement format.

Example:

```text
HDFC
ICICI
SBI
Axis
American Express
```

Use template detection rather than an LLM whenever possible.

Possible signals:

- bank name
- statement terminology
- column headers
- known PDF text patterns
- page layout

Architecture:

```text
Raw PDF
   ↓
Issuer detector
   ↓
issuer = HDFC
   ↓
HDFC parser
```

Each issuer parser should implement a shared interface.

```python
class StatementParser:
    def detect(self, document) -> bool: ...
    def parse(self, document) -> ParsedStatement: ...
```

This makes adding issuers much easier later.

---

# 8. Transaction Parsing

Normalize every transaction into one internal schema.

```text
transaction_id
statement_id
date
posted_date
merchant_raw
merchant_normalized
amount
currency
transaction_type
category
subcategory
source_page
confidence
```

Possible transaction types:

```text
PURCHASE
REFUND
REVERSAL
PAYMENT
FEE
INTEREST
GST
EMI
CASH_WITHDRAWAL
REWARD
ADJUSTMENT
UNKNOWN
```

This classification is critical because credit-card statements contain many entries that are not actual purchases.

---

# 9. Merchant Normalization

Raw merchant descriptions are messy.

Example:

```text
AMZN Mktp IND Pvt Ltd
AMAZON PAY
AMAZON.IN
AMAZON SELLER SERVICES
```

Should potentially normalize to:

```text
Amazon
```

Create three levels:

```text
Raw merchant
      ↓
Normalized merchant
      ↓
Merchant category
```

Start with a rule-based merchant dictionary.

Use LLM classification only for unknown merchants.

Cache the classification after the first successful resolution.

---

# 10. Category Classification

Recommended initial categories:

```text
Food & Dining
Shopping
Transport
Travel
Bills & Utilities
Entertainment
Healthcare
Education
Fuel
Subscriptions
Rent / Housing
Fees & Charges
Cash Withdrawal
Other
```

Use:

### Level 1 — Rules

Known merchant → known category.

### Level 2 — Heuristics

Use merchant text, transaction context, and recurring patterns.

### Level 3 — LLM fallback

Unknown merchant → structured classification request.

Return JSON only:

```json
{
  "merchant": "Example Merchant",
  "category": "Shopping",
  "subcategory": "Electronics",
  "confidence": 0.91
}
```

Do not send the entire statement to the LLM for every transaction.

Batch unknown merchants where useful and cache results.

---

# 11. Validation Layer

This should be a first-class component.

The system should compare parsed transactions against totals shown in the statement.

Example:

```text
Statement purchases:     ₹47,823
Parsed purchase total:   ₹47,823
Difference:                  ₹0
Status:                  VALIDATED
```

If they do not reconcile:

```text
Statement purchases:     ₹47,823
Parsed purchase total:   ₹46,987
Difference:                ₹836
Status:                   REVIEW REQUIRED
```

Never silently present potentially incorrect financial data as fact.

### Other validation checks

- duplicate transaction detection
- impossible dates
- negative values where unexpected
- missing amounts
- missing dates
- duplicated page headers
- repeated transactions across page boundaries
- statement balance mismatch

---

# 12. Analytics Engine

The analytics engine should be deterministic and independent of the LLM.

## Core metrics

```text
Total spend
Average transaction
Median transaction
Largest transaction
Transaction count
Category share
Merchant share
```

## Temporal metrics

```text
Daily spend
Weekly spend
Weekday vs weekend
Month-over-month change
Spending velocity
```

## Behavioral metrics

```text
Small transaction frequency
Large purchase frequency
Category concentration
Merchant concentration
Average transaction trend
```

## Recurring-payment analysis

Identify repeated merchant/amount patterns.

Signals:

- same merchant
- similar amount
- roughly regular interval

Output:

```text
merchant = Spotify
estimated_frequency = monthly
amount = ₹119
confidence = high
```

---

# 13. Personal Spending Profile

This is the foundation for personalization.

For every user, maintain a rolling profile.

```text
User Spending Profile

Monthly average spend
Monthly median spend
Category distribution
Merchant distribution
Average transaction size
Weekend spending ratio
Small transaction ratio
Recurring payment total
Discretionary spending ratio
Essential spending ratio
Utilization trend
Spending volatility
```

The most important principle:

> **Compare the user primarily against their own history.**

Do not initially rely on generic demographic benchmarks.

Example:

Bad:

> People your age spend 20% on food.

Better:

> Your food spending is 29% this month versus your three-month average of 20%.

---

# 14. Pattern Detection Engine

Create explicit detectors.

## Pattern 1 — Category spike

```text
IF
current_category_spend > historical_average × threshold

THEN
create category_spike finding
```

## Pattern 2 — Spending acceleration

```text
IF
current_month_spend > previous_month_spend × threshold

THEN
create spending_growth finding
```

## Pattern 3 — Excessive small transactions

```text
IF
small_transaction_count > historical_baseline × threshold

THEN
create frequent_small_spend finding
```

## Pattern 4 — Merchant concentration

```text
IF
single_merchant_share > threshold

THEN
create merchant_concentration finding
```

## Pattern 5 — Unusual purchase

Compare transaction amount with the user's historical transaction distribution.

Possible methods:

- z-score
- percentile
- median absolute deviation
- category-specific baseline

## Pattern 6 — Subscription burden

```text
IF
recurring_payment_total > configurable_share_of_spend

THEN
recommend subscription review
```

## Pattern 7 — Weekend spending

Compare weekend percentage against personal baseline.

## Pattern 8 — Late-night spending

If timestamps exist, detect unusual spending during user-defined late hours.

## Pattern 9 — Increasing transaction frequency

The user may spend more even when average transaction size stays similar.

## Pattern 10 — High utilization

When credit-limit information is available:

```text
utilization = outstanding_balance / credit_limit × 100
```

Use this as an informational metric, not as a claim about credit-score impact unless the specific claim is supported by authoritative evidence.

---

# 15. Recommendation Engine

The recommendation engine is the heart of the product.

Do not train a model first.

Start with:

```text
Rules + Statistics + User History
```

## Recommendation structure

Every recommendation should contain:

```text
type
title
reason
evidence
estimated_savings
confidence
action
```

Example:

```json
{
  "type": "food_delivery",
  "title": "Reduce food-delivery spending",
  "reason": "Food delivery increased 38% this month.",
  "evidence": {
    "current": 4200,
    "historical_average": 3040,
    "change_percent": 38
  },
  "estimated_monthly_savings": 1200,
  "confidence": 0.88,
  "action": "Reduce two delivery orders per week."
}
```

## Recommendation principles

1. Evidence first.
2. Personalized to the user's history.
3. Specific action rather than generic advice.
4. Estimate savings conservatively.
5. Show uncertainty where appropriate.
6. Never shame the user.

---

# 16. LLM Layer

The LLM should sit **after** the analytics engine.

### Bad architecture

```text
PDF → LLM → financial conclusions
```

### Good architecture

```text
PDF
 ↓
Structured transactions
 ↓
Deterministic calculations
 ↓
Validated findings
 ↓
LLM explanation
```

The LLM receives structured facts.

Example prompt input:

```json
{
  "finding_type": "category_spike",
  "category": "Food",
  "current_spend": 8420,
  "historical_average": 6100,
  "change_percent": 38,
  "share_of_total": 27.4,
  "top_merchants": ["Swiggy", "Zomato"]
}
```

The LLM's job is to create a concise explanation and recommendation.

### LLM constraints

Require:

- structured JSON output
- no invented numbers
- no unsupported financial claims
- reference provided evidence only
- concise output

The backend should validate the returned JSON before displaying it.

---

# 17. Recommendation Feedback Loop

This should eventually become the learning system.

```text
Recommendation
      ↓
User accepts / dismisses
      ↓
User takes action
      ↓
Next statement uploaded
      ↓
Measure behavior change
      ↓
Recommendation outcome
```

Possible feedback events:

```text
shown
clicked
accepted
dismissed
completed
ignored
```

Possible outcome metrics:

```text
category spending change
merchant spending change
transaction frequency change
monthly savings estimate
```

This creates valuable proprietary behavioral data without needing to start with a huge training dataset.

---

# 18. Future Machine Learning Roadmap

Do not build ML merely because the project contains AI.

Only introduce ML when there is evidence that a model improves the system.

## Phase 1 — Rules

No ML training required.

Use explicit detection rules.

## Phase 2 — Statistical personalization

Use:

- rolling averages
- percentiles
- anomaly scores
- clustering
- trend detection

## Phase 3 — ML classification

Potential use cases:

- merchant classification
- transaction category prediction
- anomaly detection
- spending forecasting

Possible techniques:

- Logistic Regression
- Gradient Boosting
- Random Forest
- Isolation Forest
- simple clustering

Deep learning is unlikely to be necessary initially.

## Phase 4 — Recommendation ranking

Once enough feedback data exists:

```text
User profile
+
Current findings
+
Past recommendation outcomes
        ↓
Recommendation ranking model
```

The model can learn which recommendations are more likely to produce useful outcomes for different spending profiles.

---

# 19. Data Model

Suggested PostgreSQL structure:

```text
users
 ├── id
 ├── email
 ├── created_at
 └── privacy_settings

cards
 ├── id
 ├── user_id
 ├── issuer
 ├── card_last4
 ├── card_name
 └── credit_limit

statements
 ├── id
 ├── user_id
 ├── card_id
 ├── file_hash
 ├── statement_period_start
 ├── statement_period_end
 ├── total_amount_due
 ├── minimum_amount_due
 ├── due_date
 ├── status
 └── created_at

transactions
 ├── id
 ├── statement_id
 ├── transaction_date
 ├── merchant_raw
 ├── merchant_normalized
 ├── amount
 ├── currency
 ├── transaction_type
 ├── category
 ├── subcategory
 ├── confidence
 └── metadata

findings
 ├── id
 ├── user_id
 ├── statement_id
 ├── finding_type
 ├── severity
 ├── title
 ├── evidence
 ├── confidence
 └── created_at

recommendations
 ├── id
 ├── finding_id
 ├── user_id
 ├── title
 ├── action
 ├── estimated_savings
 ├── confidence
 └── created_at

recommendation_events
 ├── id
 ├── recommendation_id
 ├── event_type
 ├── created_at
 └── metadata
```

Use JSON/JSONB only where flexible metadata is genuinely useful. Keep important analytical fields normalized.

---

# 20. API Design

Possible FastAPI endpoints:

```text
POST   /api/statements/upload
GET    /api/statements/{id}
GET    /api/statements/{id}/transactions
GET    /api/statements/{id}/summary
GET    /api/statements/{id}/findings
GET    /api/statements/{id}/recommendations

GET    /api/users/me/profile
GET    /api/users/me/trends
GET    /api/users/me/insights

POST   /api/recommendations/{id}/feedback
PATCH  /api/transactions/{id}
```

Keep the API independent of the frontend so the data/analysis engine could later serve a mobile client.

---

# 21. Recommended Tech Stack

The stack should match the skills you already have rather than introducing unnecessary technologies.

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts

## Backend

- Python
- FastAPI
- Pydantic

## Data processing

- PyMuPDF
- pdfplumber
- OCR only as fallback
- pandas for analysis where useful
- NumPy
- scikit-learn later for ML use cases

## Database

- PostgreSQL
- Supabase for managed Postgres/Auth/storage if desired

## Storage

Use object storage only when statements must be retained.

Otherwise, for privacy, prefer temporary processing and delete the original file after successful extraction where product requirements allow it.

## AI

Use a hosted LLM API for:

- unknown merchant classification
- insight explanation
- recommendation wording

Potential providers:

- Gemini API
- OpenAI API

Use the model that provides the best combination of cost, structured-output reliability, latency, and privacy controls for the workload.

## Authentication

- Supabase Auth is sufficient for the MVP.

## Deployment

Suggested:

```text
Frontend → Vercel
Backend  → Google Cloud Run
Database → Supabase PostgreSQL
Storage  → Supabase Storage / cloud object storage
```

This fits a lightweight solo-developer architecture and avoids managing servers manually.

---

# 22. Security & Privacy Architecture

This is not optional because the application processes financial information.

## Minimum requirements

- HTTPS everywhere
- authentication
- authorization checks on every statement/resource
- encrypted storage when data is retained
- secure file upload validation
- file-size limits
- malware/content checks where appropriate
- no card CVV storage
- avoid storing full card numbers
- mask card identifiers
- secrets stored in environment/secret management
- strict database row-level access controls where applicable
- audit logs for sensitive operations

## Data minimization

Prefer storing:

```text
Card issuer
Last 4 digits
Transaction history
```

rather than:

```text
Full card number
CVV
Bank login credentials
```

Never ask users for online-banking credentials just to analyze a statement.

## LLM privacy

Decide explicitly:

- What transaction information is sent to the LLM.
- Whether raw merchant descriptions are sent.
- Whether identifying details are redacted.
- Whether provider data-retention policies meet your requirements.

A good design is to send only the **minimum structured facts necessary** for generating an insight.

---

# 23. Failure Handling

The product needs explicit failure states.

### Parser failure

```text
We couldn't confidently read this statement.
```

Do not fabricate results.

### Partial parsing

```text
72 of 74 transactions parsed successfully.
2 transactions require review.
```

### Validation failure

```text
The statement total does not reconcile with the transactions we extracted.
```

### Unknown merchant

```text
Merchant could not be confidently classified.
```

Allow manual correction.

### Low-confidence category

Store confidence and allow the user to change the category.

Corrections should become training/feedback data later.

---

# 24. UI / UX Flow

## Screen 1 — Landing

Simple explanation:

> Upload your credit-card statement. Understand where your money went and what you can change.

CTA:

**Analyze Statement**

## Screen 2 — Upload

Show:

- supported file types
- privacy explanation
- maximum file size
- expected processing time

## Screen 3 — Processing

Progress states:

```text
Uploading
Extracting statement
Detecting transactions
Categorizing spending
Analyzing patterns
Generating insights
```

## Screen 4 — Results

Start with findings, not charts.

```text
Your August spending

₹42,680
67 transactions

What stands out

1. Food spending increased 32%
2. Weekend spending is unusually high
3. ₹2,100 in recurring subscriptions detected
4. One ₹7,999 purchase is unusually large
5. Shopping is now your second-largest category
```

Then show charts supporting the findings.

## Screen 5 — Transactions

Allow:

- search
- filter
- edit category
- edit merchant
- mark transaction type

Corrections should feed the personalization pipeline.

---

# 25. Recommendation UX

Avoid generic advice like:

> "Try to spend less on food."

Instead:

> **Reduce food-delivery spending**
>
> You spent ₹4,200 on food delivery this month, 38% more than your three-month average. Cutting two orders per week could save roughly ₹1,200/month.
>
> **[Show transactions] [Dismiss]**

Every recommendation should answer:

```text
What is happening?
Why does it matter?
What can I change?
How much could that change save?
```

---

# 26. Recommendation Quality Rules

Never generate recommendations that:

- invent transaction details
- claim guaranteed savings
- give tax/legal/financial advice without proper evidence
- shame the user
- use unsupported demographic comparisons
- pretend estimates are exact

Use language such as:

- "appears to"
- "based on your recent spending"
- "estimated"
- "could save"
- "worth reviewing"

when uncertainty exists.

---

# 27. Testing Strategy

The highest-risk component is not the frontend. It is document correctness.

Build a test corpus of statements from different issuers and layouts.

Test:

```text
Normal statement
Multi-page statement
Refund-heavy statement
EMI statement
Statement with fees
Statement with reversals
Statement with international transactions
Scanned PDF
Password-protected PDF
Malformed PDF
Duplicate upload
```

For each sample, verify:

- transaction count
- transaction amounts
- transaction types
- category accuracy
- statement total reconciliation

Create automated regression tests so adding a parser does not break another issuer.

---

# 28. Scalability Considerations

MVP can process synchronously for simplicity.

As volume grows:

```text
Upload API
   ↓
Job queue
   ↓
Document worker
   ↓
Analytics worker
   ↓
LLM worker
   ↓
Database
```

Possible later components:

- Redis
- Celery / RQ / cloud-native job queues
- asynchronous workers

Do not introduce a queue just because production architecture diagrams contain queues. Add one when processing time and concurrency justify it.

---

# 29. Cost Control

Potential expensive operations:

- OCR
- LLM calls
- storing PDFs
- repeated merchant classification

### Cost strategy

```text
Known merchant
   ↓
No LLM

Unknown merchant
   ↓
LLM classification
   ↓
Cache result
```

For insights:

```text
Raw transactions
   ↓
Deterministic analytics
   ↓
5–10 structured findings
   ↓
One small LLM request
```

Do not send thousands of raw transactions to the model when a compact analytical summary is sufficient.

---

# 30. Metrics to Measure Product Success

Don't only measure page views.

Track:

### Parsing quality

- parse success rate
- reconciliation success rate
- category correction rate
- unknown merchant rate

### Product engagement

- statement upload completion
- dashboard completion
- findings viewed
- recommendations viewed
- transaction corrections

### Recommendation usefulness

- recommendation accepted
- recommendation dismissed
- user-reported usefulness
- measurable spending change after recommendation

The most valuable metric eventually becomes:

> **How often did a recommendation produce a measurable improvement in the user's spending behavior?**

---

# 31. Suggested Development Phases

## Phase 0 — Validation

Goal: prove people care.

Build:

- basic landing page
- one statement parser
- simple dashboard
- manual/demo data if necessary

Test with 10–20 real users.

Ask:

> What did you learn from this analysis that you didn't already know?

Do not ask only:

> Did you like the UI?

---

## Phase 1 — Technical MVP

Build:

- upload
- PDF parser
- transactions
- category rules
- database
- charts
- deterministic findings
- basic recommendations
- validation

Target: 1–2 weeks of focused development.

---

## Phase 2 — Robust MVP

Add:

- more issuers
- merchant normalization
- corrections
- recurring-payment detection
- anomaly detection
- authentication
- privacy controls
- better error handling

Target: 3–5 weeks total.

---

## Phase 3 — Personalization

Add:

- historical profile
- month-to-month analysis
- personalized recommendation engine
- feedback events
- recommendation outcome tracking

---

## Phase 4 — ML

Only after enough data exists.

Potential ML tasks:

- category classification
- anomaly detection
- spend forecasting
- recommendation ranking

---

## Phase 5 — Credit Card Intelligence

Potential features:

- rewards optimization
- annual-fee analysis
- EMI cost analysis
- subscription management
- multi-card optimization
- utilization monitoring

---

# 32. Suggested Repository Structure

```text
cc-track/
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   │
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   ├── core/
│       │   ├── models/
│       │   ├── schemas/
│       │   └── services/
│       │
│       └── tests/
│
├── packages/
│   └── shared-types/
│
├── parsers/
│   ├── base.py
│   ├── hdfc.py
│   ├── icici.py
│   ├── sbi.py
│   ├── axis.py
│   └── detector.py
│
├── analytics/
│   ├── metrics.py
│   ├── trends.py
│   ├── anomalies.py
│   ├── recurring.py
│   └── profile.py
│
├── recommendations/
│   ├── rules.py
│   ├── scoring.py
│   └── templates.py
│
├── ml/
│   ├── features.py
│   ├── training/
│   └── inference/
│
├── prompts/
│   └── insights/
│
├── test-data/
│   └── statements/
│
├── docs/
│
└── README.md
```

For a very small MVP, this can be simplified. Do not create dozens of packages before there is code that needs them.

---

# 33. Recommended Final Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js + TypeScript | Familiar, strong web ecosystem |
| UI | Tailwind + shadcn/ui | Fast polished UI |
| Charts | Recharts | Enough for financial dashboards |
| Backend | FastAPI | Excellent fit for Python/data workflows |
| Validation | Pydantic | Typed request/response schemas |
| PDF | PyMuPDF + pdfplumber | Good starting point for statement extraction |
| OCR | Add only when necessary | Avoid unnecessary complexity |
| Data | PostgreSQL | Strong relational model for transactions |
| Managed DB/Auth | Supabase | Fast solo-dev setup |
| Analytics | Python + pandas/NumPy | Straightforward analysis |
| ML later | scikit-learn | Enough for initial ML use cases |
| LLM | Gemini/OpenAI API | Insight explanation / classification fallback |
| Frontend deploy | Vercel | Low operational overhead |
| Backend deploy | Cloud Run | Simple Python deployment and scaling |
| Storage | Supabase Storage / object storage | Secure file storage when needed |

---

# 34. Most Important Engineering Principles

## Principle 1

**Correctness beats AI.**

A beautiful AI insight based on incorrect transactions destroys trust.

## Principle 2

**Rules before ML.**

You need to understand the problem before training a model.

## Principle 3

**Personal history beats generic benchmarks.**

Compare users primarily with themselves.

## Principle 4

**LLM explains; analytics computes.**

Never let the model silently become the financial calculator.

## Principle 5

**Every recommendation needs evidence.**

The user should be able to trace a recommendation back to actual transactions.

## Principle 6

**Privacy is a product feature.**

Financial data requires data minimization, secure handling, and transparent retention policies.

## Principle 7

**Do not build features before proving usefulness.**

The first thing to validate is whether users actually change their spending after reading CC Track's recommendations.

---

# 35. North-Star Product Experience

The ideal experience should be:

```text
Upload statement
       ↓
Wait while CC Track processes it
       ↓
"Your August statement, decoded."
       ↓
₹42,680 spent
       ↓
"Here are the 5 things you should know."
       ↓
Personalized findings
       ↓
"Here are 3 changes that could save you ~₹2,100/month."
       ↓
User chooses one
       ↓
Next month
       ↓
"You reduced food-delivery spending by 24%."
```

That final step is the long-term differentiator.

**CC Track should eventually optimize for behavior change, not merely better dashboards.**
