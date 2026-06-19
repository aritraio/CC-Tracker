# AI Financial Journal — Day-by-Day TODO

> A structured 16-day build plan. Each day has a clear goal, concrete deliverables, and a definition of "done."
> Estimated effort: ~3-4 focused hours per day.

---

## Legend

- `[ ]` — Not started
- `[/]` — In progress
- `[x]` — Completed

---

## Week 1: Backend Core (Days 1–5)

---

### Day 1 — Project Scaffolding & Backend Setup

**Goal:** Get the backend skeleton running with a health check endpoint.

- [ ] Initialize the project structure (see `IMPLEMENTATION_PLAN.md` for directory layout)
- [ ] Set up Python virtual environment
- [ ] Install core dependencies: `fastapi`, `uvicorn`, `pdfplumber`, `python-multipart`, `pydantic`, `python-dotenv`
- [ ] Create `main.py` with FastAPI app instance, CORS middleware, and health check route
- [ ] Create `.env.example` with placeholder values
- [ ] Create Pydantic models in `models/schemas.py` (`Transaction`, `InsightsResponse`, etc.)
- [ ] Create `requirements.txt`
- [ ] Verify: `uvicorn main:app --reload` starts cleanly and `GET /health` returns `200`

**Definition of Done:** Backend server runs, health endpoint responds, all Pydantic models defined.

---

### Day 2 — Bank Detection & HDFC Parser

**Goal:** Detect the bank from a PDF and parse HDFC statements.

- [ ] Implement `parsers/detector.py` — extract first-page text and match bank signatures
- [ ] Implement `parsers/base.py` — abstract `BaseParser` class
- [ ] Implement `parsers/hdfc.py`:
  - [ ] Identify table boundaries on each page
  - [ ] Extract rows using `pdfplumber`
  - [ ] Parse date strings into `datetime.date` objects
  - [ ] Normalize amounts (handle commas, CR/DR indicators)
  - [ ] Handle multi-line transaction descriptions
  - [ ] Extract statement period (billing dates)
- [ ] Create test fixture: `tests/fixtures/hdfc_sample.txt` (copy-pasted text from a real HDFC statement)
- [ ] Write unit tests in `tests/test_parsers.py` for HDFC parsing
- [ ] Verify: Parser correctly extracts all transactions from an HDFC sample

**Definition of Done:** Given HDFC PDF bytes, parser returns a complete list of `Transaction` objects.

---

### Day 3 — ICICI & SBI Parsers

**Goal:** Complete all three bank parsers.

- [ ] Implement `parsers/icici.py`:
  - [ ] Handle ICICI-specific column layout
  - [ ] Parse EMI line items correctly
  - [ ] Handle landscape-oriented statements
  - [ ] Extract statement period
- [ ] Implement `parsers/sbi.py`:
  - [ ] Handle SBI-specific format
  - [ ] Filter out reward points summary rows
  - [ ] Extract statement period
- [ ] Create test fixtures: `tests/fixtures/icici_sample.txt`, `tests/fixtures/sbi_sample.txt`
- [ ] Write unit tests for ICICI and SBI parsers
- [ ] Verify: All three parsers pass their respective test suites

**Definition of Done:** All 3 parsers extract transactions accurately from sample data.

---

### Day 4 — Categorization Engine

**Goal:** Build the 3-tier categorization pipeline.

- [ ] Create `categorization/merchant_dictionary.json` with 200+ Indian merchant entries
  - [ ] Food & Dining (Zomato, Swiggy, Dominos, McDonald's, Starbucks, etc.)
  - [ ] Shopping (Amazon, Flipkart, Myntra, Ajio, Meesho, etc.)
  - [ ] Travel (MakeMyTrip, IRCTC, Yatra, OYO, Airbnb, etc.)
  - [ ] Bills & Utilities (Airtel, Jio, Vodafone, BSNL, Electricity boards, etc.)
  - [ ] Entertainment (Netflix, Hotstar, Spotify, PVR, Inox, etc.)
  - [ ] Healthcare (Apollo, Fortis, 1mg, PharmEasy, etc.)
  - [ ] Fuel (HP, BPCL, IOCL, Shell, etc.)
  - [ ] Transport (Uber, Ola, Rapido, Metro, etc.)
  - [ ] Groceries (BigBasket, Blinkit, Zepto, DMart, etc.)
  - [ ] Education (Udemy, Coursera, Unacademy, BYJU'S, etc.)
- [ ] Implement `categorization/regex_rules.py` — category regex patterns as fallback
- [ ] Implement `categorization/engine.py` — orchestrator that runs Tier 1 → Tier 2 → Tier 3
- [ ] Write unit tests in `tests/test_categorization.py`
- [ ] Verify: Known merchants categorize instantly; unknown strings fall through correctly

**Definition of Done:** Categorization engine correctly categorizes 90%+ of common Indian transactions.

---

### Day 5 — LLM Fallback, Insights Calculator & API Endpoint

**Goal:** Complete the backend pipeline end-to-end.

- [ ] Implement `categorization/llm_fallback.py`:
  - [ ] Set up Gemini Flash API client
  - [ ] Batch unrecognized descriptions into a single prompt
  - [ ] Parse structured JSON response
  - [ ] Handle API errors gracefully (timeout → mark as "Uncategorized")
- [ ] Implement `insights/calculator.py`:
  - [ ] `calculate_total_spend()` — sum of debits
  - [ ] `calculate_total_credits()` — sum of credits
  - [ ] `calculate_average_transaction()` — mean of debit amounts
  - [ ] `find_largest_transaction()` — max debit
  - [ ] `calculate_category_breakdown()` — group by category, sum amounts
  - [ ] `detect_recurring_charges()` — known subscriptions + same-merchant detection
  - [ ] `detect_anomalies()` — z-score or percentile-based flagging
- [ ] Implement `api/v1/routes.py` — `POST /parse` endpoint (full pipeline)
- [ ] Wire everything together in `main.py`
- [ ] Write unit tests in `tests/test_insights.py`
- [ ] **End-to-End Test:** Upload a real PDF via `curl` or Swagger UI → get full JSON response
- [ ] Verify: Complete JSON response with all fields populated

**Definition of Done:** `POST /api/v1/parse` accepts a PDF and returns a complete `InsightsResponse`.

---

## Week 2: Frontend Build (Days 6–10)

---

### Day 6 — Frontend Setup & Design System

**Goal:** Set up Next.js with Tailwind, Shadcn, and establish the design system.

- [ ] Initialize Next.js project with TypeScript, Tailwind, App Router
- [ ] Install and initialize Shadcn UI
- [ ] Install additional dependencies: `pdfjs-dist`, `recharts`, `lucide-react`
- [ ] Set up Google Fonts: `Outfit` (headings) + `Inter` (body) + `JetBrains Mono` (numbers)
- [ ] Define CSS custom properties in `globals.css`:
  - [ ] Dark mode color palette
  - [ ] Category-specific colors
  - [ ] Typography scale
  - [ ] Spacing and border radius tokens
- [ ] Build `Header.tsx` — app logo, tagline, dark/light toggle
- [ ] Build `Footer.tsx` — privacy notice, GitHub link
- [ ] Create `layout.tsx` with fonts, metadata, and shared layout
- [ ] Verify: App loads with correct fonts, dark background, and styled header/footer

**Definition of Done:** Clean, dark-mode shell with design system fully configured.

---

### Day 7 — Upload Page & PDF Decryption

**Goal:** Build the landing page with drag-and-drop upload and local PDF decryption.

- [ ] Implement `lib/pdf-decrypt.ts` — pdf.js local decryption logic
- [ ] Configure pdf.js web worker (copy `pdf.worker.min.js` to `public/`)
- [ ] Build `DropZone.tsx`:
  - [ ] Drag & drop area with animated border
  - [ ] File type validation (`.pdf` only)
  - [ ] File size validation (max 10MB)
  - [ ] Visual feedback on drag-over
  - [ ] Display file name and size after selection
- [ ] Build `PasswordModal.tsx`:
  - [ ] Modal dialog (Shadcn Dialog)
  - [ ] Password input with show/hide toggle
  - [ ] Hint text: "Try your PAN number or Date of Birth (DDMMYYYY)"
  - [ ] Error state for incorrect passwords
  - [ ] Loading state while attempting decryption
- [ ] Build `UploadProgress.tsx`:
  - [ ] Progress bar during upload
  - [ ] "Analyzing your statement..." text with animated dots
- [ ] Build landing `page.tsx`:
  - [ ] Hero section with tagline and value proposition
  - [ ] Upload widget centered on page
  - [ ] Privacy badges ("Local Decryption", "No Storage", "Instant Delete")
- [ ] Implement `lib/api-client.ts` — fetch wrapper to POST PDF to backend
- [ ] Implement `hooks/useStatementUpload.ts` — manages upload state machine
- [ ] Verify: Can select a PDF, enter password, see it decrypt locally, and upload to backend

**Definition of Done:** Full upload flow works: select → decrypt → upload → receive response.

---

### Day 8 — Dashboard: Overview Cards & Charts

**Goal:** Build the top section of the insights dashboard.

- [ ] Define TypeScript interfaces in `types/index.ts` matching backend response
- [ ] Build `dashboard/page.tsx` — layout with grid system for dashboard widgets
- [ ] Build `OverviewCards.tsx`:
  - [ ] Total Spend card (with rupee formatting)
  - [ ] Average Transaction card
  - [ ] Largest Purchase card
  - [ ] Transaction Count card
  - [ ] Animated count-up effect on numbers
  - [ ] Appropriate icons from Lucide
- [ ] Build `CategoryChart.tsx`:
  - [ ] Donut/pie chart using `recharts`
  - [ ] Category colors matching design system
  - [ ] Interactive tooltips showing amount and percentage
  - [ ] Legend with category labels
- [ ] Build `SpendTimeline.tsx`:
  - [ ] Area chart showing daily spending
  - [ ] Gradient fill under the line
  - [ ] Responsive to container width
- [ ] Build `TopMerchants.tsx`:
  - [ ] Horizontal bar chart of top 10 merchants
  - [ ] Amount labels on bars
- [ ] Verify: Dashboard renders with mock data, all charts display correctly

**Definition of Done:** Overview cards and all 3 charts render beautifully with real or mock data.

---

### Day 9 — Dashboard: Tables, Recurring & Anomalies

**Goal:** Complete the remaining dashboard components.

- [ ] Build `RecurringCharges.tsx`:
  - [ ] Card list layout
  - [ ] Each card: merchant name, amount (in monospace font), category badge
  - [ ] Empty state if no recurring charges detected
  - [ ] Subtle animation on card appearance
- [ ] Build `AnomalyAlerts.tsx`:
  - [ ] Warning-styled alert cards (amber/red accent)
  - [ ] Transaction details: date, merchant, amount
  - [ ] Reason text explaining why it's flagged
  - [ ] Empty state: "No anomalies detected — your spending looks normal!"
- [ ] Build `TransactionTable.tsx`:
  - [ ] Full sortable table (Shadcn Table)
  - [ ] Columns: Date, Description, Category (badge), Amount, Type (Debit/Credit)
  - [ ] Sort by any column (click header)
  - [ ] Filter by category (dropdown)
  - [ ] Search by description (text input)
  - [ ] Alternating row colors
  - [ ] Pagination (if > 50 transactions)
- [ ] Wire all components together in `dashboard/page.tsx`
- [ ] Implement `hooks/useDashboardData.ts` — state management for dashboard
- [ ] Verify: All components render, sort/filter/search work on the table

**Definition of Done:** Complete dashboard with all widgets functional and interactive.

---

### Day 10 — Frontend-Backend Integration

**Goal:** Connect frontend to live backend and test the full flow.

- [ ] Configure `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Test full flow: Upload → Decrypt → Parse → Dashboard
- [ ] Handle and display all error states:
  - [ ] Wrong password → show error in PasswordModal
  - [ ] Unsupported bank → show error message on upload page
  - [ ] Parse failure → show error message with retry option
  - [ ] Network error → show retry button
  - [ ] Server error → show generic error with retry
- [ ] Add loading skeleton screens on dashboard while data loads
- [ ] Test with real HDFC statement end-to-end
- [ ] Test with real ICICI statement end-to-end
- [ ] Test with real SBI statement end-to-end
- [ ] Fix any bugs discovered during integration testing
- [ ] Verify: Complete end-to-end flow works for all 3 banks

**Definition of Done:** A user can upload any supported bank statement and see their insights.

---

## Week 3: Polish, Database & Deploy (Days 11–16)

---

### Day 11 — UI Polish & Animations

**Goal:** Make the UI feel premium, polished, and production-ready.

- [ ] Add micro-animations:
  - [ ] Fade-in on dashboard cards (staggered)
  - [ ] Chart entry animations
  - [ ] Smooth transitions between upload and dashboard views
  - [ ] Hover effects on interactive elements
  - [ ] Button click feedback (scale/color)
- [ ] Add glassmorphism effect on key cards (backdrop-blur)
- [ ] Implement proper dark/light mode toggle with `prefers-color-scheme` detection
- [ ] Add responsive design breakpoints:
  - [ ] Desktop (1200px+): 3-column dashboard grid
  - [ ] Tablet (768px–1199px): 2-column grid
  - [ ] Mobile (375px–767px): Single column, stacked layout
- [ ] Ensure all text is readable, no overflow issues
- [ ] Add smooth scroll behavior
- [ ] Test on Chrome, Safari, and Firefox
- [ ] Verify: UI feels premium and professional across all screen sizes

**Definition of Done:** The app looks and feels like a production-quality product.

---

### Day 12 — Database & Authentication Setup

**Goal:** Set up Supabase for optional account creation and data persistence.

- [ ] Create Supabase project
- [ ] Run SQL migration scripts (create `statements` and `transactions` tables)
- [ ] Enable Row Level Security (RLS) policies
- [ ] Install `@supabase/supabase-js` in frontend
- [ ] Configure Supabase client in `lib/supabase.ts`
- [ ] Implement authentication:
  - [ ] Sign up with email/password
  - [ ] Login
  - [ ] Logout
  - [ ] Auth state management (React context or Zustand)
- [ ] Build auth UI:
  - [ ] Login/Sign up modal (Shadcn Dialog)
  - [ ] Auth state in Header (show user email or "Sign In" button)
- [ ] Verify: Users can sign up, log in, and see their auth state reflected in the UI

**Definition of Done:** Authentication works end-to-end with Supabase.

---

### Day 13 — Save & View History

**Goal:** Allow logged-in users to save insights and view past statements.

- [ ] Add "Save Insights" button on dashboard
  - [ ] If not logged in → show auth modal first
  - [ ] If logged in → save statement summary + transactions to Supabase
- [ ] Build history page (`/history`):
  - [ ] List of past uploaded statements
  - [ ] Each row: bank name, period, total spend, date uploaded
  - [ ] Click to view → re-render dashboard with saved data
- [ ] Add navigation between Upload, Dashboard, and History
- [ ] Handle duplicate detection (same bank + same period = update, not duplicate)
- [ ] Test save and retrieval flow
- [ ] Verify: Users can save, navigate to history, and view past insights

**Definition of Done:** Full save/view cycle works for authenticated users.

---

### Day 14 — Testing & Bug Fixes

**Goal:** Comprehensive testing and bug fixing.

- [ ] Run full backend test suite: `pytest tests/ -v`
- [ ] Fix any failing tests
- [ ] Test with at least 2 real statements per bank (6 total minimum)
- [ ] Document any parsing edge cases discovered and fix them
- [ ] Test error handling paths:
  - [ ] Upload a non-PDF file
  - [ ] Upload a PDF from an unsupported bank
  - [ ] Upload a corrupted PDF
  - [ ] Enter wrong password 3 times
  - [ ] Kill backend while frontend is uploading
- [ ] Test responsive design on actual mobile device (or device emulator)
- [ ] Run Lighthouse audit and fix issues:
  - [ ] Performance score > 90
  - [ ] Accessibility score > 90
  - [ ] SEO score > 90
- [ ] Fix all discovered bugs
- [ ] Verify: All tests pass, no known bugs remain

**Definition of Done:** App is stable, well-tested, and ready for deployment.

---

### Day 15 — Deployment

**Goal:** Deploy the full stack to production.

- [ ] **Backend → Railway / Render:**
  - [ ] Push backend code to GitHub
  - [ ] Connect repo to Railway/Render
  - [ ] Set environment variables (`GEMINI_API_KEY`, `ALLOWED_ORIGINS`)
  - [ ] Verify health endpoint responds on production URL
  - [ ] Test `POST /parse` on production
- [ ] **Frontend → Vercel:**
  - [ ] Push frontend code to GitHub
  - [ ] Connect repo to Vercel
  - [ ] Set environment variables (`NEXT_PUBLIC_API_URL`, Supabase vars)
  - [ ] Verify production build deploys successfully
  - [ ] Test full flow on production URL
- [ ] **Configure CORS:**
  - [ ] Update `ALLOWED_ORIGINS` to include Vercel production domain
  - [ ] Verify cross-origin requests work
- [ ] **Custom domain (optional):**
  - [ ] Configure custom domain on Vercel if available
- [ ] **Smoke test on production:**
  - [ ] Upload a real statement on the live URL
  - [ ] Verify complete flow works
  - [ ] Test on mobile browser
- [ ] Verify: App is live and functional on production URLs

**Definition of Done:** App is deployed, live, and working on the internet.

---

### Day 16 — Documentation, README & Portfolio Polish

**Goal:** Final documentation, README update, and portfolio-ready polish.

- [ ] Update `README.md`:
  - [ ] Add system architecture diagram (Mermaid)
  - [ ] Add screenshots/GIFs of the app in action
  - [ ] Update tech stack section with final choices
  - [ ] Add live demo link
  - [ ] Add "What I Learned" section (great for resume conversations)
- [ ] Write `docs/api-spec.md` — formal API documentation
- [ ] Add inline code comments for complex logic (parsers, categorization)
- [ ] Create a compelling demo:
  - [ ] Record a 30-second screen recording of the full flow
  - [ ] Convert to GIF for the README
- [ ] Clean up code:
  - [ ] Remove any `console.log` / `print` debug statements
  - [ ] Ensure consistent code formatting
  - [ ] Remove unused dependencies
- [ ] Add project to resume:
  - [ ] 2-3 bullet points highlighting key technical decisions
  - [ ] Example: "Built a privacy-first financial analytics engine with zero-disk-write architecture, processing credit card PDFs entirely in RAM"
  - [ ] Example: "Designed a hybrid ML categorization pipeline (dictionary + regex + LLM fallback) that reduced API costs by ~90%"
- [ ] Pin the repo on GitHub profile
- [ ] Verify: README is polished, demo works, code is clean

**Definition of Done:** Project is portfolio-ready and resume-worthy.

---

## Post-MVP Stretch Goals (Optional)

After the 16-day core build, consider these enhancements:

- [ ] **Multi-statement comparison:** Upload 2+ months and show MoM trends
- [ ] **Export to CSV/Excel:** Let users download their categorized transactions
- [ ] **Budget alerts:** Set spending limits per category
- [ ] **Dark/Light mode persistence:** Save preference in localStorage
- [ ] **PWA support:** Installable on mobile with offline capability
- [ ] **CI/CD pipeline:** GitHub Actions for automated testing on push
- [ ] **Docker Compose:** One-command local setup for contributors
- [ ] **More banks:** Axis, Kotak, RBL, AMEX (after validating 99% accuracy)

---

## Quick Reference — Daily Time Estimates

| Day | Focus Area | Estimated Hours |
|-----|-----------|----------------|
| 1 | Backend scaffolding | 2–3h |
| 2 | Bank detection + HDFC parser | 3–4h |
| 3 | ICICI + SBI parsers | 3–4h |
| 4 | Categorization engine | 3–4h |
| 5 | LLM fallback + Insights + API | 3–4h |
| 6 | Frontend setup + Design system | 3–4h |
| 7 | Upload page + PDF decryption | 3–4h |
| 8 | Dashboard: Cards + Charts | 3–4h |
| 9 | Dashboard: Table + Recurring + Anomalies | 3–4h |
| 10 | Frontend-Backend integration | 3–4h |
| 11 | UI polish + Animations | 3–4h |
| 12 | Database + Authentication | 3–4h |
| 13 | Save + History feature | 3–4h |
| 14 | Testing + Bug fixes | 3–4h |
| 15 | Deployment | 2–3h |
| 16 | Documentation + Portfolio polish | 2–3h |
| **Total** | | **~48–60 hours** |

---

*Start date: ___________*
*Target completion: 16 days from start*

---

*Last updated: June 2026*
