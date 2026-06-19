Here is the README. It is stripped of marketing fluff and reflects the exact, pragmatic MVP we mapped out. It tells developers and users exactly what this is, how it handles their data, and why it was built this way.

---

# AI Financial Journal (MVP)

> **Upload your statement. Understand your money. No bullshit.**

Most personal finance apps are either glorified spreadsheets requiring hours of manual entry, or privacy nightmares that want eternal access to your bank accounts.

AI Financial Journal is a lean, strictly scoped extraction engine. You upload a credit card statement, and it instantly shows you your total spend, recurring charges, and anomalies. No "financial storytelling," no unnecessary AI chat features, and no saving your sensitive documents.

## 🚀 Core Philosophy

1. **Privacy by Architecture:** We don't ask for trust; we build a system that doesn't require it. PDFs are decrypted locally in the browser. The unencrypted file is sent to a stateless microservice, processed entirely in RAM, and immediately destroyed.
2. **Deterministic First:** We don't waste LLM tokens doing basic math or guessing if "ZOMATO" is food. We use a hardcoded merchant dictionary for the top 200 Indian vendors. AI is only used as a fallback for unstructured anomalies.
3. **Narrow Scope:** For Phase 1, we officially support only **HDFC, ICICI, and SBI** credit card statements. We'd rather be 100% accurate for three banks than 60% accurate for fifty.

## ✨ Features (Phase 1)

* **Client-Side Decryption:** Passwords (often PAN/DOB) never leave the user's device.
* **Stateless Parsing Engine:** Built with Python (`pdfplumber`) for accurate tabular data extraction.
* **Instant Dashboard:**
* **Money Overview:** Total spend, average transaction, largest purchase.
* **Categorization:** Food, Shopping, Travel, Bills, etc.
* **Recurring Charges Detected:** Identifies subscriptions (Netflix, Spotify, Prime) billed in the current cycle.
* **High-Signal Anomalies:** Highlights unusually large purchases or out-of-pattern spending.



## 🛠 Tech Stack

### Frontend (User Interface & Local Decryption)

* **Framework:** Next.js (TypeScript)
* **Styling:** Tailwind CSS + Shadcn UI
* **PDF Handling:** `pdf.js` (Strictly for local password unlocking and decryption before transmission)

### Backend (Stateless Parsing Service)

* **Framework:** FastAPI (Python)
* **Extraction:** `pdfplumber` / `regex`
* **Categorization Engine:** Hardcoded JSON/SQL Merchant Dictionary + Fast LLM API fallback (e.g., Gemini Flash) for unrecognized transaction strings.
* **Architecture:** In-memory processing only. Zero disk writes.

### Database (For Saved Insights)

* **PostgreSQL (Supabase/Neon):** Only stores extracted, anonymized transaction data *if* the user explicitly creates an account and saves it.

## 🔒 The Privacy Contract

If you deploy or fork this project, respect the privacy contract:

1. **No disk writes.** The backend must process the PDF as a buffer in memory.
2. **Instant deletion.** Once the JSON response is returned to the client, the memory buffer is cleared.
3. **No logging of transaction strings.** Do not pipe unrecognized strings to a centralized error log.

## 💻 Local Setup

### Prerequisites

* Node.js (v18+)
* Python (3.10+)
* Poetry or `pip`

### 1. Start the Parsing Microservice

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

```

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev

```

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

```

## 🗺 Roadmap

**Phase 1 (Current):** Prove the value. Single-statement PDF uploads, local decryption, and immediate insights for HDFC, ICICI, and SBI.
**Phase 2:** Account Aggregator (AA) Integration. Move from manual PDF uploads to frictionless, consent-based API syncing via India's AA ecosystem (e.g., Sahamati framework).
**Phase 3:** Multi-card intelligence and historical MoM (Month-over-Month) trend analysis.

## 🤝 Contributing

We are currently only accepting PRs for:

* Updating the `merchant_dictionary.json`
* Hardening the regex rules for HDFC, ICICI, and SBI parsers.

Do not submit PRs for new bank support unless you can guarantee 99% extraction accuracy across at least 5 different statement variations for that bank.