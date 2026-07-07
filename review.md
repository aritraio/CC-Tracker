# AI Financial Journal — Project Review

> Quick-reference review of the professor-approved project plan.

---

## What It Is

A **privacy-first credit card statement analyzer**. Users upload a bank PDF, it gets parsed in-memory, and an insights dashboard renders instantly — no data stored, no accounts required (optionally available).

**Tagline:** *Upload your statement. Understand your money.*

---

## Scope (Phase 1 MVP)

| Dimension | Boundary |
|-----------|----------|
| Banks supported | HDFC, ICICI, SBI (credit card only) |
| Input | Single PDF per upload |
| Output | JSON → rendered dashboard |
| Storage | Stateless by default; optional Supabase save |
| Auth | Optional (only needed to persist insights) |

---

## Architecture at a Glance

```
Browser (pdf.js decrypt) → POST /parse → FastAPI (RAM only) → JSON → Next.js Dashboard
```

- **Frontend:** Next.js + TypeScript, Tailwind CSS, Shadcn UI, Recharts, pdf.js
- **Backend:** FastAPI + Python, pdfplumber, Pydantic
- **LLM:** Gemini Flash (fallback categorization only)
- **DB (optional):** Supabase PostgreSQL with RLS
- **Deploy:** Vercel (FE) + Railway/Render (BE) + Supabase (DB)

---

## Core Pipeline

1. **Client-side PDF decryption** — password never leaves browser
2. **Bank detection** — regex on first-page text
3. **Table extraction** — pdfplumber, bank-specific parsers
4. **3-tier categorization:**
   - Tier 1: Merchant dictionary (200+ Indian vendors) → ~70% coverage
   - Tier 2: Regex pattern matching → ~15-20% more
   - Tier 3: Gemini Flash LLM batch call → remaining ~10%
5. **Insights computation** — totals, averages, recurring charges, anomalies (z-score)
6. **Dashboard render** — overview cards, charts, table, alerts

---

## Privacy Model

| Threat | Mitigation |
|--------|------------|
| Password leak | Decrypted locally via pdf.js, never sent to server |
| PDF on disk | Processed in RAM (BytesIO), cleared after response |
| Transaction logging | No PII in logs; structured error logging only |
| LLM data exposure | Only merchant name strings sent, no amounts/dates/user IDs |
| DB breach | Only anonymized data stored; opt-in only; RLS enforced |

---

## Dashboard Components

| Component | Visualization |
|-----------|--------------|
| Overview Cards | Total spend, avg txn, largest purchase, count |
| Category Breakdown | Donut/pie chart (recharts) |
| Spend Timeline | Daily area/line chart |
| Top Merchants | Horizontal bar chart (top 10) |
| Recurring Charges | Card list with category badges |
| Anomaly Alerts | Warning cards with reason text |
| Transaction Table | Sortable, filterable, searchable, paginated |

---

## Build Timeline

| Phase | Days | Focus |
|-------|------|-------|
| Week 1 (Days 1–5) | Backend | Scaffold, parsers (HDFC/ICICI/SBI), categorization, insights, API |
| Week 2 (Days 6–10) | Frontend | Design system, upload flow, dashboard, integration |
| Week 3 (Days 11–16) | Polish & Ship | Animations, auth/DB, testing, deploy, docs |
| **Total** | **16 days** | **~48–60 hours** |

---

## Key Technical Decisions

1. **pdfplumber over Tabula/Camelot** — pure Python, no Java dependency, better for Indian bank formats
2. **3-tier categorization** — deterministic layers first to minimize LLM cost (~$0.001–0.005/statement)
3. **Stateless backend** — zero disk writes, buffer cleared in `finally` block
4. **Client-side decryption** — shifts trust boundary to user's device
5. **Narrow bank scope** — 3 banks at 100% accuracy > 50 banks at 60%

---

## Risk Areas to Watch

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bank PDF format changes | Parsers break silently | Test with multiple card variants (Regalia, Millennia, etc.) |
| Multi-line descriptions in PDFs | Transactions split across rows | Handle in per-bank parser logic |
| Gemini API rate limits | Uncategorized fallback | Batch all unknowns in single call; graceful "Uncategorized" default |
| pdfplumber table detection failures | Missing transactions | Validate row count against expected patterns |
| CORS misconfiguration on deploy | Frontend can't reach backend | Test cross-origin in staging first |

---

## Post-MVP Stretch Goals

- Multi-statement MoM comparison
- CSV/Excel export
- Budget alerts per category
- PWA support
- More banks (Axis, Kotak, RBL, AMEX)
- CI/CD with GitHub Actions
- Docker Compose for local dev

---

## Deliverables Checklist

- [ ] Working backend with `/parse` endpoint
- [ ] Working frontend with upload + dashboard
- [ ] 3 bank parsers (HDFC, ICICI, SBI)
- [ ] 200+ merchant dictionary
- [ ] LLM fallback integration
- [ ] Supabase auth + save (optional flow)
- [ ] Deployed to Vercel + Railway
- [ ] README with architecture diagram + demo GIF
- [ ] Lighthouse > 90 (perf, a11y, SEO)

---

*Reviewed: July 2026*
