# DESIGN.md — CC Track Bauhaus Design System & UI/UX Specification

> **Aesthetic Archetype:** Constructivist Bauhaus Modernism  
> **Core Motto:** *Form Follows Financial Function* — Mathematical Truth Expressed Through Geometric Purity  
> **Target Platform:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts, Lucide React  

---

## 1. Executive Philosophy & Constructivist Vision

CC Track rejects the soft, blurry gradients and generic SaaS templates of contemporary fintech apps. Because CC Track is built on **100% mathematical integrity, deterministic reconciliation, and zero-hallucination spending intelligence**, its visual design directly reflects this rigor.

We adopt the **Bauhaus Constructivist Modernism** design language:
- **Geometric Purity**: Every UI primitive is derived strictly from circles, squares, and triangles.
- **Architectural Honesty**: Thick structural borders ($2\text{px}$ and $4\text{px}$ stark black), zero blur, crisp $90^\circ$ angles, and raw hard-offset drop shadows.
- **Primary Color Blocking**: High-energy primary colors (**Bauhaus Red `#D02020`**, **Bauhaus Blue `#1040C0`**, and **Bauhaus Yellow `#F0C020`**) set against an off-white canvas (`#F0F0F0`) and stark black ink (`#121212`).
- **Constructivist Poster Typography**: Massive uppercase headlines with tight tracking and heavy geometric letterforms powered by Google's **Outfit** typeface.
- **Tactile & Mechanical Micro-Interactions**: Snappy, physical button depressions (`active:translate-x-[2px] active:translate-y-[2px] active:shadow-none`) and crisp hover elevations.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CC TRACK BAUHAUS                               │
│                                                                             │
│   ● RED (#D02020)       ■ BLUE (#1040C0)        ▲ YELLOW (#F0C020)          │
│   Urgency, Expense,     Structural, Stable,     Warnings, Discoveries,      │
│   Anomalies, Actions    Intelligence, Data      Savings, Opportunities      │
│                                                                             │
│   Canvas: #F0F0F0 (Off-White)   │   Ink / Structural Border: #121212 (Black)│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Design Token System (The DNA)

### 2.1 Color Palette

The palette is strictly restricted to primary Bauhaus pigments, high-contrast neutrals, and semantic financial mappings. No pastels, no vague gradients, no semi-transparent blur washes.

```text
HEX / Token Reference:
├── Canvas & Background:   #F0F0F0  (Off-White Paper Canvas)
├── Ink & Structure:       #121212  (Stark Black / Borders / Typography)
├── Pure Surface:          #FFFFFF  (Card / Modal / Surface Background)
├── Muted Surface:         #E0E0E0  (Dividers / Table Headers / Neutral Chips)
│
├── Bauhaus Red:           #D02020  (Primary Accent / Expense / Critical Review)
├── Bauhaus Blue:          #1040C0  (Secondary Accent / Analytics / Informational)
├── Bauhaus Yellow:        #F0C020  (Highlight / Warnings / Verified Savings)
│
└── Semantic Financial Tints (Accent & Status):
    ├── Debit / Outflow:        #D02020 (Red)
    ├── Credit / Payment / In:  #1040C0 (Blue) or #008844 (Deep Bauhaus Green)
    ├── Reconciled / Safe:      #121212 on #F0C020 / #FFFFFF with Black Border
    ├── Discrepancy / Review:   #FFFFFF on #D02020 with 4px Black Border
    └── Accordion Detail Fill:  #FFF9C4 (Warm Sunlight Bauhaus Yellow)
```

#### Tailwind Color Token Mapping (`tailwind.config.ts`)

```typescript
// apps/web/tailwind.config.ts
export const colors = {
  canvas: '#F0F0F0',
  ink: '#121212',
  paper: '#FFFFFF',
  muted: '#E0E0E0',
  bauhaus: {
    red: '#D02020',
    'red-hover': '#B81B1B',
    blue: '#1040C0',
    'blue-hover': '#0C3299',
    yellow: '#F0C020',
    'yellow-hover': '#D9AC1A',
    'yellow-light': '#FFF9C4',
    green: '#008844',
  },
  border: '#121212',
};
```

---

### 2.2 Typography System

The primary typeface is **Outfit** (Google Fonts), selected for its pure geometric circles, stark vertical stems, and constructivist character. For precise tabular financial numbers, amounts, and dates, we pair it with monospace styling or tabular numerals (`font-mono` / `tabular-nums`).

#### Font Import
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
```

#### Type Hierarchy & Scale

| Style Level | Class Name | Weight | Tracking | Line Height | Case | Usage |
|---|---|---|---|---|---|---|
| **Poster Display** | `text-6xl md:text-8xl` | 900 (`font-black`) | `tracking-tighter` | `leading-[0.88]` | UPPERCASE | Landing Hero, Statement Total Spend |
| **Headline 1** | `text-4xl md:text-5xl` | 900 (`font-black`) | `tracking-tight` | `leading-[0.95]` | UPPERCASE | Section Titles, Executive Metric Figures |
| **Headline 2** | `text-2xl md:text-3xl` | 700 (`font-bold`) | `tracking-tight` | `leading-tight` | UPPERCASE | Card Headers, Module Headings |
| **Subheading** | `text-lg md:text-xl` | 700 (`font-bold`) | `tracking-normal` | `leading-snug` | Mixed / Sentence | Card Subheads, Finding Titles |
| **Body Large** | `text-base md:text-lg` | 500 (`font-medium`)| `tracking-normal` | `leading-relaxed` | Sentence | Explanations, Recommendation Copy |
| **Body Regular**| `text-sm md:text-base` | 400 (`font-normal`)| `tracking-normal` | `leading-relaxed` | Sentence | Table Rows, Secondary Descriptions |
| **Label / Eyebrow**| `text-xs md:text-sm` | 700 (`font-bold`) | `tracking-widest` | `leading-none` | UPPERCASE | Badges, Table Headers, Metric Tags |
| **Financial Monospace**| `font-mono text-sm md:text-base` | 700 (`font-bold`)| `tracking-tight` | `leading-none` | Tabular | INR Amounts (`₹ 48,250.00`), Txn Dates |

---

### 2.3 Radius & Border Rules

Bauhaus adheres strictly to **binary geometry**:
- **Rectangles & Squares:** `rounded-none` ($0\text{px}$). Zero soft rounded corners on standard cards, tables, inputs, or banners.
- **Circles & Cylinders:** `rounded-full` ($9999\text{px}$). Used intentionally for circular badges, pill tags, icon containers, and avatars.
- **Never Use:** `rounded-sm`, `rounded-md`, `rounded-lg`, or `rounded-xl`.

#### Border Thickness & Rules
- **Mobile**: `border-2 border-black` ($2\text{px}$)
- **Desktop**: `border-4 border-black` ($4\text{px}$)
- **Dividers & Structural Sections**: `border-b-4 border-black` or `border-r-4 border-black`
- **Internal Table Borders**: `border-2 border-black`
- **Border Color**: Uniformly `#121212` (`border-black`) across light canvas and surfaces.

---

### 2.4 Hard Offset Shadows & Elevation

Depth in Bauhaus is created through **physical graphic layering**, not diffused gaussian shadows.

```text
Shadow Tokens:
├── Shadow XS (Badges / Small Inputs):   shadow-[2px_2px_0px_0px_#121212]
├── Shadow SM (Buttons / Form Fields):   shadow-[4px_4px_0px_0px_#121212]
├── Shadow MD (Standard Cards / Popups): shadow-[6px_6px_0px_0px_#121212]
├── Shadow LG (Hero Panels / Modals):    shadow-[8px_8px_0px_0px_#121212]
└── Shadow XL (Floating Focal Display):  shadow-[12px_12px_0px_0px_#121212]
```

#### Physical Button Depression Mechanism
```css
/* Active / Pressed State simulates tactile mechanical depression */
.bauhaus-button {
  transform: translate(0, 0);
  box-shadow: 4px 4px 0px 0px #121212;
  transition: transform 100ms ease-out, box-shadow 100ms ease-out;
}
.bauhaus-button:hover {
  transform: translate(-1px, -1px);
  box-shadow: 5px 5px 0px 0px #121212;
}
.bauhaus-button:active {
  transform: translate(4px, 4px);
  box-shadow: 0px 0px 0px 0px #121212;
}
```

---

### 2.5 Geometric Textures & Surface Patterns

To create visual depth without gradients, use pure CSS geometric background patterns:

1. **Constructivist Dot Grid**:
   ```css
   .bg-bauhaus-dots {
     background-image: radial-gradient(#121212 1.5px, transparent 1.5px);
     background-size: 24px 24px;
   }
   ```
2. **Diagonal Hatching (Caution / Striped Accent)**:
   ```css
   .bg-bauhaus-stripes {
     background: repeating-linear-gradient(
       45deg,
       #121212,
       #121212 4px,
       #F0C020 4px,
       #F0C020 16px
     );
   }
   ```
3. **Primary Corner Marks**:
   Every card features a geometric accent shape in its top-right corner:
   - **Red Circle**: `w-4 h-4 rounded-full bg-[#D02020] border-2 border-black`
   - **Blue Square**: `w-4 h-4 rounded-none bg-[#1040C0] border-2 border-black`
   - **Yellow Triangle**: `w-4 h-4 bg-[#F0C020] [clip-path:polygon(50%_0%,0%_100%,100%_100%)]`

---

## 3. Brand Identity & Logo Construction

The CC Track logo is an architectural composition of the three Bauhaus foundational shapes paired with brutalist typography:

```text
┌─────────────────────────────────────────────────────────────┐
│  ● [Red Circle]  ■ [Blue Square]  ▲ [Yellow Triangle]       │
│  CC TRACK                                                   │
│  SPENDING INTELLIGENCE ENGINE                               │
└─────────────────────────────────────────────────────────────┘
```

- **Mark Components**:
  1. Solid Red Circle (`#D02020`, $24\text{px} \times 24\text{px}$, `border-2 border-black`)
  2. Solid Blue Square (`#1040C0`, $24\text{px} \times 24\text{px}$, `border-2 border-black`)
  3. Solid Yellow Triangle (`#F0C020`, $24\text{px} \times 24\text{px}$, `border-2 border-black`)
- **Wordmark**: `font-black text-2xl uppercase tracking-tighter text-[#121212]`
- **Subline**: `font-bold text-[10px] uppercase tracking-[0.25em] text-[#121212]`

---

## 4. Component Design Specifications

### 4.1 Buttons & Interactive Controls

Buttons are tactile blocks with thick borders and hard drop shadows.

```text
┌──────────────────────────────────────────────────────────┐
│                   BUTTON VARIANT MATRIX                  │
├─────────────────┬─────────────────┬──────────────────────┤
│ Variant         │ Visual Style    │ Tailwind Utility     │
├─────────────────┼─────────────────┼──────────────────────┤
│ Primary Action  │ Bauhaus Red     │ bg-[#D02020] text-white border-2 md:border-4 border-black shadow-[4px_4px_0px_0px_#121212] │
│ Secondary Data  │ Bauhaus Blue    │ bg-[#1040C0] text-white border-2 md:border-4 border-black shadow-[4px_4px_0px_0px_#121212] │
│ Highlight CTA   │ Bauhaus Yellow  │ bg-[#F0C020] text-black border-2 md:border-4 border-black shadow-[4px_4px_0px_0px_#121212] │
│ Stark Outline   │ Pure Paper      │ bg-white text-black border-2 md:border-4 border-black shadow-[4px_4px_0px_0px_#121212]     │
│ Dark Brutalist  │ Stark Black     │ bg-[#121212] text-white border-2 md:border-4 border-black shadow-[4px_4px_0px_0px_#D02020] │
└─────────────────┴─────────────────┴──────────────────────┘
```

#### Shared Button Classes
```text
px-6 py-3 font-bold uppercase tracking-wider text-sm md:text-base 
rounded-none transition-all duration-150 
hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[6px_6px_0px_0px_#121212] 
active:translate-x-1 active:translate-y-1 active:shadow-none 
focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[#F0C020]
```

---

### 4.2 Statement Dropzone & Upload State Machine

The statement upload zone is the central hero interactive piece of the landing interface.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────────────┐ │
│ │  ▲ CLIENT-SIDE ZERO-KNOWLEDGE DECRYPTION                             │ │
│ │                                                                      │ │
│ │    ┌────────┐                                                        │ │
│ │    │  PDF   │   DRAG & DROP YOUR CREDIT CARD STATEMENT               │ │
│ │    │  ICON  │   HDFC • ICICI • SBI • AXIS • AMEX                     │ │
│ │    └────────┘                                                        │ │
│ │                                                                      │ │
│ │    [ SELECT PDF FILE FROM DEVICE ]                                   │ │
│ │                                                                      │ │
│ │  ■ 100% IN-MEMORY PARSING   ● ZERO PASSWORD TRANSMISSION             │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

#### DropZone Visual States:
- **Idle State**: White surface (`bg-white`), `border-4 border-dashed border-black`, `shadow-[8px_8px_0px_0px_#121212]`, subtle background dot grid.
- **Drag-Over Active State**: Solid Yellow background (`bg-[#F0C020]`), `border-4 border-solid border-black`, scaled corner geometric markers.
- **Client Decryption Modal (Password Prompt)**:
  - Header with solid Blue banner (`bg-[#1040C0] text-white`).
  - Bank detection badge (`HDFC BANK DETECTED`).
  - Educational helper box explaining bank password formula (`e.g., First 4 chars of Name + DOB DDMM`).
  - Masked input field: `bg-white border-4 border-black font-mono text-xl tracking-widest`.
  - Action button: Yellow Primary (`UNLOCK & PROCESS IN RAM`).
- **Processing State Machine (5 Stepped Stages)**:
  Thick stepped horizontal progress blocks:
  1. `[1] UNLOCKING (CLIENT)` $\rightarrow$
  2. `[2] EXTRACTING TABLES` $\rightarrow$
  3. `[3] RECONCILING DUES` $\rightarrow$
  4. `[4] CATEGORIZING` $\rightarrow$
  5. `[5] SYNTHESIZING INSIGHTS`
  - Active step pulses with Bauhaus Yellow background and black border.
  - Completed steps display solid Bauhaus Blue with white check icon.

---

### 4.3 Financial Reconciliation Stamp & Status Banners

Reconciliation is the core guarantee of CC Track. The status badge is styled like a brutalist official verification stamp.

```text
RECONCILED STATE (MATHEMATICAL INTEGRITY = 100%):
┌──────────────────────────────────────────────────────────────────────────┐
│  ■ RECONCILIATION AUDIT: VALIDATED                                       │
│  Extracted Sum: ₹ 48,250.00  │ Statement Due: ₹ 48,250.00 │ Discrepancy: ₹ 0.00 │
└──────────────────────────────────────────────────────────────────────────┘

REVIEW REQUIRED STATE (DISCREPANCY DETECTED):
┌──────────────────────────────────────────────────────────────────────────┐
│  ▲ RECONCILIATION AUDIT: REVIEW REQUIRED                                 │
│  Extracted Sum: ₹ 47,414.00  │ Statement Due: ₹ 48,250.00 │ Discrepancy: ₹ 836.00 │
│  [2 UNPARSED ROWS FLAGGED FOR MANUAL INSPECTION]                         │
└──────────────────────────────────────────────────────────────────────────┘
```

- **Validated Style**: `bg-[#F0C020] text-black border-4 border-black shadow-[6px_6px_0px_0px_#121212]` with geometric check mark mark.
- **Review Required Style**: `bg-[#D02020] text-white border-4 border-black shadow-[6px_6px_0px_0px_#121212]` with blinking warning triangle.

---

### 4.4 Executive Metric Cards (OverviewCards)

Overview cards display core statement numbers (Total Spend, Net Spend, Top Category, Max Transaction, Card Utilization).

```text
┌───────────────────────────┐  ┌───────────────────────────┐
│ TOTAL SPEND             ● │  │ TOP CATEGORY            ■ │
│ ₹ 48,250.00               │  │ FOOD & DINING             │
│ ───────────────────────── │  │ ───────────────────────── │
│ ▲ +18.4% vs 3-Mo Baseline │  │ ₹ 16,840.00 (34.9% of total)│
└───────────────────────────┘  └───────────────────────────┘
```

- **Card Container**: `bg-white border-4 border-black shadow-[8px_8px_0px_0px_#121212] p-6 relative`
- **Corner Accent Mark**: Rotates through Circle (`#D02020`), Square (`#1040C0`), Triangle (`#F0C020`) across cards.
- **Label / Eyebrow**: `text-xs font-bold tracking-widest text-[#121212]/70 uppercase`
- **Main Value**: `text-4xl md:text-5xl font-black font-mono tracking-tight text-[#121212]`
- **Comparison Pill**: Bordered chip with black stroke:
  - Spike / Increased spend: `bg-[#D02020] text-white border-2 border-black px-2 py-0.5 text-xs font-bold`
  - Decreased spend / Savings: `bg-[#F0C020] text-black border-2 border-black px-2 py-0.5 text-xs font-bold`
- **Hover Lift**: `transition-transform duration-150 hover:-translate-y-1`

---

### 4.5 Financial Charts (Recharts Bauhaus Theming)

All financial visualizations must avoid muted pastels and use crisp primary colors, solid fills, thick black outlines, and high-contrast tooltip overlays.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ CATEGORY BREAKDOWN (DONUT)               DAILY SPEND TIMELINE (AREA)    │
│                                                                          │
│       ████ #D02020 (Dining)                   ▲ ₹8,400 (Weekend Spike)   │
│     ██    ██ #1040C0 (Grocery)               / \                         │
│     ██    ██ #F0C020 (Shopping)             /   \      /\                │
│       ████ #121212 (Bills)             ____/     \____/  \_______        │
│                                        1   5   10   15   20   25   30    │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Chart Theme Palette:
- Category 1 (Food & Dining): `#D02020` (Bauhaus Red)
- Category 2 (Groceries / Quick-Comm): `#1040C0` (Bauhaus Blue)
- Category 3 (Shopping / E-Comm): `#F0C020` (Bauhaus Yellow)
- Category 4 (Bills & Utilities): `#121212` (Stark Black)
- Category 5 (Travel & Fuel): `#E0E0E0` (Muted Grey with thick black stroke)
- Category 6 (Entertainment / Subs): `#008844` (Deep Bauhaus Green)

#### Chart Component Styling Rules:
- **Donut / Pie Chart**: `stroke="#121212"` and `strokeWidth={3}` between segments. Inner radius `60%`, outer radius `85%`.
- **Bar Chart**: Solid fill colors, `stroke="#121212"`, `strokeWidth={2}`, `radius={[0, 0, 0, 0]}` (zero rounded corners).
- **Line / Area Chart**: Line stroke `#121212` ($3\text{px}$ width), fill `#F0C020` with 100% opacity or solid hatch pattern. Dots: $6\text{px}$ black squares (`shape="rect"`).
- **Custom Tooltip**:
  - `bg-white border-4 border-black shadow-[4px_4px_0px_0px_#121212] p-3`
  - Font: `font-mono text-sm font-bold`
  - Total and category labeled with primary color indicator swatch ($8\text{px} \times 8\text{px}$ square).

---

### 4.6 Anomaly & Spending Pattern Alerts

Detected anomalies (Weekend Spikes, Recurring Creep, Micro-Spend Leaks, High Utilization) are structured as constructivist discovery cards.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ ▲ PATTERN DETECTED: WEEKEND SPENDING INFLATION           SEVERITY: HIGH  │
│ ──────────────────────────────────────────────────────────────────────── │
│ 58.4% of your total discretionary spend occurred on Saturdays & Sundays. │
│ Evidence: 14 transactions totaling ₹ 28,190.00 across 4 weekends.       │
│                                                                          │
│ [ VIEW 14 TRANSACTIONS ]                       [ SIMULATE ₹ 4,200 SAVING ]│
└──────────────────────────────────────────────────────────────────────────┘
```

- **Severity Indicators**:
  - `HIGH`: Header bar in `bg-[#D02020] text-white border-b-4 border-black`
  - `MEDIUM`: Header bar in `bg-[#F0C020] text-black border-b-4 border-black`
  - `INFO`: Header bar in `bg-[#1040C0] text-white border-b-4 border-black`
- **Body**: White canvas, `p-5`, leading-relaxed Outfit typography, `border-4 border-black shadow-[6px_6px_0px_0px_#121212]`.

---

### 4.7 Actionable Recommendation Cards & Behavioral Savings

Recommendations present verified, deterministic mathematical savings rather than generalized advice.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  ■ BEHAVIORAL RECOMMENDATION #01                   EST. SAVINGS / MO     │
│    CONSOLIDATE QUICK-COMMERCE ORDERS              [ ₹ 2,450.00 / MO ]    │
│ ──────────────────────────────────────────────────────────────────────── │
│  You placed 23 Blinkit/Zepto orders under ₹ 250 this cycle. Small delivery│
│  fees and impulse additions totaled ₹ 2,450.00 in avoidable overhead.    │
│                                                                          │
│  Action: Shift to 2 scheduled weekly bulk orders over ₹ 1,000.           │
│                                                                          │
│  [ ✓ ACCEPT GOAL ]      [ ✕ DISMISS ]      [ SHOW 23 TRANSACTIONS ]      │
└──────────────────────────────────────────────────────────────────────────┘
```

- **Savings Badge**: Prominent yellow box (`bg-[#F0C020] text-black font-black font-mono px-3 py-1 border-2 border-black shadow-[2px_2px_0px_0px_#121212]`).
- **Interactive Action Buttons**:
  - Accept Goal: Red Button (`bg-[#D02020] text-white border-2 border-black`)
  - Dismiss: Outline Button (`bg-white text-black border-2 border-black`)
  - Show Transactions: Blue link button (`text-[#1040C0] font-bold underline`)

---

### 4.8 Interactive Transaction Table (TransactionManager)

The transaction table is built for high-density legibility and rapid financial inspection.

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SEARCH: [ Zomato...              ]   TYPE: [ ALL ▼ ]   CATEGORY: [ FOOD & DINING ▼ ]  SORT: [ DATE ▼ ]│
├────────────┬────────────────────────────┬──────────────┬──────────────────┬──────────────┬────────────┤
│ DATE       │ MERCHANT / DESCRIPTION     │ TYPE         │ CATEGORY         │ AMOUNT (INR) │ ACTION     │
├────────────┼────────────────────────────┼──────────────┼──────────────────┼──────────────┼────────────┤
│ 14/08/2026 │ ZOMATO BANGALORE IND       │ PURCHASE     │ FOOD & DINING    │ ₹   1,240.00 │ [EDIT]     │
│ 12/08/2026 │ BLINKIT GROCERY NEW DELHI  │ PURCHASE     │ QUICK-COMMERCE   │ ₹     349.00 │ [EDIT]     │
│ 08/08/2026 │ NETFLIX ENTERTAINMENT      │ RECURRING    │ SUBSCRIPTIONS    │ ₹     649.00 │ [EDIT]     │
│ 04/08/2026 │ HDFC CC PAYMENT RECVD      │ PAYMENT      │ PAYMENT/CREDIT   │ -₹ 35,000.00 │ [LOCKED]   │
└────────────┴────────────────────────────┴──────────────┴──────────────────┴──────────────┴────────────┘
```

#### Table Component Specifications:
- **Table Container**: `bg-white border-4 border-black shadow-[8px_8px_0px_0px_#121212] overflow-x-auto`
- **Table Header (`thead`)**: `bg-[#121212] text-white font-bold text-xs uppercase tracking-widest divide-x-2 divide-white`
- **Table Row (`tr`)**: `border-b-2 border-black hover:bg-[#FFF9C4] transition-colors duration-100`
- **Alternating Zebra (Optional)**: `even:bg-[#F9F9F9]`
- **Cell Padding**: `py-3.5 px-4`
- **Amount Styling**:
  - Purchases / Debits: `font-mono font-bold text-base text-[#121212]`
  - Payments / Credits: `font-mono font-bold text-base text-[#1040C0]`
- **Category Badge**: Bordered pill with solid background:
  - `bg-[#E0E0E0] text-black border-2 border-black px-2.5 py-0.5 text-xs font-bold uppercase`
  - Clicking category opens inline Popover menu with 2-click reclassification.

---

### 4.9 Accordion / FAQ / Explainer

```text
CLOSED STATE:
┌──────────────────────────────────────────────────────────────────────────┐
│  + HOW DOES CC TRACK GUARANTEE CLIENT-SIDE PRIVACY?                      │
└──────────────────────────────────────────────────────────────────────────┘

OPEN STATE:
┌──────────────────────────────────────────────────────────────────────────┐
│  - HOW DOES CC TRACK GUARANTEE CLIENT-SIDE PRIVACY?                      │
├──────────────────────────────────────────────────────────────────────────┤
│  Your password is never sent to any server. Unlocking occurs locally in   │
│  your browser via WebAssembly (pdf.js). Decrypted buffers are sent to an  │
│  ephemeral RAM worker that discards raw bytes immediately after parsing. │
└──────────────────────────────────────────────────────────────────────────┘
```

- **Closed State**: `bg-white text-black border-4 border-black shadow-[4px_4px_0px_0px_#121212] p-5 font-bold uppercase`
- **Open State (Header)**: `bg-[#D02020] text-white border-4 border-black p-5 font-black uppercase`
- **Open State (Content Panel)**: `bg-[#FFF9C4] text-black border-x-4 border-b-4 border-black p-5 font-medium leading-relaxed`
- **Icon**: Chevron or Plus/Minus with $180^\circ$ mechanical rotation.

---

## 5. Complete Layout & Grid Architecture

### 5.1 Page Layout Grid System

The interface is organized on a strict **12-column constructivist layout** with maximum width `max-w-7xl` ($1280\text{px}$) and solid horizontal section divisions.

```text
┌────────────────────────────────────────────────────────────────────────┐
│ NAVIGATION BAR: 3-Shape Logo │ Upload │ Dashboard │ Docs │ [GITHUB]    │
├────────────────────────────────────────────────────────────────────────┤
│ HERO SECTION:                                                          │
│ ┌──────────────────────────────────────┐┌────────────────────────────┐ │
│ │ 8-COL CONSTRUCTIVIST POSTER HEADLINE ││ 4-COL SOLID BLUE PANEL     │ │
│ │ "DISSECT YOUR SPENDING WITH         ││ ABSTRACT GEOMETRIC ART      │ │
│ │  MATHEMATICAL RIGOR."                ││ ● ■ ▲ COMPOSITION           │ │
│ │ [DROP STATEMENT] [VIEW DEMO REPORT]  ││ 100% CLIENT DECRYPTED       │ │
│ └──────────────────────────────────────┘└────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────┤
│ STATS BAR (SOLID BAUHAUS YELLOW BACKGROUND #F0C020):                   │
│ 4-COLUMN DIVIDED METRICS (₹12M+ AUDITED │ 0 PASSWORDS STORED │ 5 BANKS)│
├────────────────────────────────────────────────────────────────────────┤
│ DASHBOARD MAIN VIEW:                                                   │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ RECONCILIATION STAMP BANNER                                        │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│ ┌──────────────┐┌──────────────┐┌──────────────┐┌────────────────────┐ │
│ │ TOTAL SPEND  ││ NET CHARGES  ││ TOP CATEGORY ││ ANOMALIES FLAGGED  │ │
│ └──────────────┘└──────────────┘└──────────────┘└────────────────────┘ │
│ ┌──────────────────────────────────────┐┌────────────────────────────┐ │
│ │ 8-COL DAILY SPEND TIMELINE (RECHARTS)││ 4-COL CATEGORY DONUT       │ │
│ └──────────────────────────────────────┘└────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ 12-COL BEHAVIORAL RECOMMENDATIONS & SAVINGS SIMULATOR              │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ 12-COL INTERACTIVE TRANSACTION MANAGER & FILTER ENGINE             │ │
│ └────────────────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────┤
│ FOOTER (SOLID BLACK #121212 BACKGROUND, WHITE TEXT, YELLOW ACCENTS)   │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Section Color Blocking Blueprint

To eliminate generic SaaS monotony, major page sections transition between solid color backgrounds:
- **Hero Top Panel**: Canvas Off-White (`#F0F0F0`) with Right Accent in Bauhaus Blue (`#1040C0`)
- **Key Proof / Stats Bar**: Solid Bauhaus Yellow (`#F0C020`) with black dividers
- **Upload / Ingestion Workspace**: Pure White (`#FFFFFF`) with dashed $4\text{px}$ black borders
- **Anomalies / Spikes Section**: Solid Bauhaus Red (`#D02020`) card headers
- **Recommendations Section**: Sunlight Yellow (`#FFF9C4`) tinted background with black borders
- **Footer**: Near-black (`#121212`) with white typography and yellow hover links

---

## 6. Implementation Code Templates

### 6.1 `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#F0F0F0',
        ink: '#121212',
        paper: '#FFFFFF',
        muted: '#E0E0E0',
        bauhaus: {
          red: '#D02020',
          'red-hover': '#B81B1B',
          blue: '#1040C0',
          'blue-hover': '#0C3299',
          yellow: '#F0C020',
          'yellow-hover': '#D9AC1A',
          'yellow-light': '#FFF9C4',
          green: '#008844',
        },
      },
      fontFamily: {
        sans: ['Outfit', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderWidth: {
        '2': '2px',
        '3': '3px',
        '4': '4px',
        '6': '6px',
        '8': '8px',
      },
      boxShadow: {
        'bauhaus-xs': '2px 2px 0px 0px #121212',
        'bauhaus-sm': '4px 4px 0px 0px #121212',
        'bauhaus-md': '6px 6px 0px 0px #121212',
        'bauhaus-lg': '8px 8px 0px 0px #121212',
        'bauhaus-xl': '12px 12px 0px 0px #121212',
        'bauhaus-red': '4px 4px 0px 0px #D02020',
        'bauhaus-yellow': '4px 4px 0px 0px #F0C020',
      },
      borderRadius: {
        none: '0px',
        full: '9999px',
      },
      keyframes: {
        'button-depress': {
          '0%': { transform: 'translate(0, 0)', boxShadow: '4px 4px 0px 0px #121212' },
          '100%': { transform: 'translate(4px, 4px)', boxShadow: '0px 0px 0px 0px #121212' },
        },
      },
      animation: {
        'button-depress': 'button-depress 100ms ease-out forwards',
      },
    },
  },
  plugins: [],
};

export default config;
```

---

### 6.2 Global CSS (`apps/web/src/app/globals.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: #F0F0F0;
    --foreground: #121212;
    --border: #121212;
  }

  body {
    background-color: var(--background);
    color: var(--foreground);
    font-family: 'Outfit', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* Universal Selection Style */
  ::selection {
    background-color: #F0C020;
    color: #121212;
  }

  /* Strict Scrollbar Styling */
  ::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }
  ::-webkit-scrollbar-track {
    background: #E0E0E0;
    border-left: 2px solid #121212;
  }
  ::-webkit-scrollbar-thumb {
    background: #121212;
    border: 2px solid #E0E0E0;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #D02020;
  }
}

@layer utilities {
  .bg-bauhaus-dots {
    background-image: radial-gradient(#121212 1.5px, transparent 1.5px);
    background-size: 24px 24px;
  }

  .bg-bauhaus-stripes {
    background: repeating-linear-gradient(
      45deg,
      #121212,
      #121212 4px,
      #F0C020 4px,
      #F0C020 16px
    );
  }

  .bauhaus-clip-triangle {
    clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
  }

  .bauhaus-card {
    @apply bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg transition-transform duration-150 hover:-translate-y-1;
  }

  .bauhaus-btn-primary {
    @apply bg-bauhaus-red text-white border-2 md:border-4 border-black shadow-bauhaus-sm font-bold uppercase tracking-wider px-6 py-3 transition-all duration-100 hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-bauhaus-yellow;
  }

  .bauhaus-btn-secondary {
    @apply bg-bauhaus-blue text-white border-2 md:border-4 border-black shadow-bauhaus-sm font-bold uppercase tracking-wider px-6 py-3 transition-all duration-100 hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-bauhaus-yellow;
  }

  .bauhaus-btn-yellow {
    @apply bg-bauhaus-yellow text-black border-2 md:border-4 border-black shadow-bauhaus-sm font-bold uppercase tracking-wider px-6 py-3 transition-all duration-100 hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-bauhaus-md active:translate-x-1 active:translate-y-1 active:shadow-none focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-bauhaus-red;
  }
}
```

---

### 6.3 Core React Component Implementations

#### 1. Bauhaus Brand Logo (`apps/web/src/components/ui/BauhausLogo.tsx`)

```tsx
import React from 'react';
import Link from 'next/link';

export interface BauhausLogoProps {
  size?: 'sm' | 'md' | 'lg';
}

export const BauhausLogo: React.FC<BauhausLogoProps> = ({ size = 'md' }) => {
  const shapeSizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl',
  };

  return (
    <Link href="/" className="inline-flex items-center gap-3 group">
      {/* 3 Primitives */}
      <div className="flex items-center gap-1.5">
        {/* Red Circle */}
        <div
          className={`${shapeSizes[size]} rounded-full bg-bauhaus-red border-2 border-black shadow-[2px_2px_0px_0px_#121212] group-hover:scale-110 transition-transform`}
          aria-hidden="true"
        />
        {/* Blue Square */}
        <div
          className={`${shapeSizes[size]} rounded-none bg-bauhaus-blue border-2 border-black shadow-[2px_2px_0px_0px_#121212] group-hover:rotate-12 transition-transform`}
          aria-hidden="true"
        />
        {/* Yellow Triangle */}
        <div
          className={`${shapeSizes[size]} bg-bauhaus-yellow bauhaus-clip-triangle border-black group-hover:-translate-y-1 transition-transform`}
          aria-hidden="true"
        />
      </div>

      {/* Wordmark */}
      <div className="flex flex-col">
        <span className={`font-black uppercase tracking-tighter text-ink ${textSizes[size]} leading-none`}>
          CC TRACK
        </span>
        <span className="font-bold text-[9px] uppercase tracking-[0.25em] text-ink/80 leading-tight mt-0.5">
          Spending Intelligence
        </span>
      </div>
    </Link>
  );
};
```

---

#### 2. Overview Metric Card (`apps/web/src/components/dashboard/OverviewCard.tsx`)

```tsx
import React from 'react';
import { LucideIcon } from 'lucide-react';

export interface OverviewCardProps {
  title: string;
  value: string;
  subtitle?: string;
  changePercent?: number;
  shape: 'circle' | 'square' | 'triangle';
  icon?: LucideIcon;
}

export const OverviewCard: React.FC<OverviewCardProps> = ({
  title,
  value,
  subtitle,
  changePercent,
  shape,
  icon: Icon,
}) => {
  return (
    <div className="bg-white border-2 md:border-4 border-black shadow-bauhaus-md md:shadow-bauhaus-lg p-5 md:p-6 relative transition-transform duration-150 hover:-translate-y-1">
      {/* Top Right Bauhaus Geometric Marker */}
      <div className="absolute top-4 right-4" aria-hidden="true">
        {shape === 'circle' && (
          <div className="w-4 h-4 rounded-full bg-bauhaus-red border-2 border-black" />
        )}
        {shape === 'square' && (
          <div className="w-4 h-4 rounded-none bg-bauhaus-blue border-2 border-black" />
        )}
        {shape === 'triangle' && (
          <div className="w-4 h-4 bg-bauhaus-yellow bauhaus-clip-triangle" />
        )}
      </div>

      {/* Header Label */}
      <div className="flex items-center gap-2 mb-2">
        {Icon && <Icon className="w-4 h-4 text-ink" />}
        <span className="text-xs font-bold uppercase tracking-widest text-ink/75">
          {title}
        </span>
      </div>

      {/* Main Metric Value */}
      <div className="text-3xl md:text-4xl font-black font-mono tracking-tight text-ink my-2">
        {value}
      </div>

      {/* Divider */}
      <div className="h-0.5 bg-black my-3 w-full" />

      {/* Comparison Delta / Subtitle */}
      <div className="flex items-center justify-between text-xs">
        {subtitle && <span className="text-ink/80 font-medium">{subtitle}</span>}
        {changePercent !== undefined && (
          <span
            className={`font-bold font-mono px-2 py-0.5 border-2 border-black ${
              changePercent > 0
                ? 'bg-bauhaus-red text-white'
                : 'bg-bauhaus-yellow text-black'
            }`}
          >
            {changePercent > 0 ? `+${changePercent}%` : `${changePercent}%`}
          </span>
        )}
      </div>
    </div>
  );
};
```

---

#### 3. Reconciliation Badge (`apps/web/src/components/dashboard/ReconciliationBadge.tsx`)

```tsx
import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

export interface ReconciliationBadgeProps {
  status: 'VALIDATED' | 'REVIEW_REQUIRED';
  extractedTotal: number;
  statementTotal: number;
  discrepancy: number;
}

export const ReconciliationBadge: React.FC<ReconciliationBadgeProps> = ({
  status,
  extractedTotal,
  statementTotal,
  discrepancy,
}) => {
  const isValidated = status === 'VALIDATED';

  return (
    <div
      className={`border-2 md:border-4 border-black p-4 md:p-6 shadow-bauhaus-md md:shadow-bauhaus-lg ${
        isValidated ? 'bg-bauhaus-yellow text-black' : 'bg-bauhaus-red text-white'
      }`}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left Status Stamp */}
        <div className="flex items-center gap-3">
          {isValidated ? (
            <div className="w-10 h-10 bg-white border-2 border-black flex items-center justify-center shadow-bauhaus-xs">
              <CheckCircle2 className="w-6 h-6 text-black" />
            </div>
          ) : (
            <div className="w-10 h-10 bg-black border-2 border-white flex items-center justify-center shadow-bauhaus-xs">
              <AlertTriangle className="w-6 h-6 text-bauhaus-yellow" />
            </div>
          )}

          <div>
            <div className="text-xs font-bold uppercase tracking-widest opacity-80">
              Deterministic Mathematical Audit
            </div>
            <div className="text-xl md:text-2xl font-black uppercase tracking-tight">
              {isValidated ? 'RECONCILIATION PASSED: 100% MATCH' : 'REVIEW REQUIRED: DISCREPANCY DETECTED'}
            </div>
          </div>
        </div>

        {/* Right Financial Figures */}
        <div className="flex items-center gap-4 bg-white text-black p-3 border-2 border-black shadow-bauhaus-xs font-mono text-xs md:text-sm">
          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">Extracted Sum</span>
            <span className="font-bold">₹ {extractedTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
          </div>
          <div className="w-px h-8 bg-black" />
          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">Statement Due</span>
            <span className="font-bold">₹ {statementTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
          </div>
          <div className="w-px h-8 bg-black" />
          <div>
            <span className="block text-[10px] uppercase font-bold text-ink/60">Delta</span>
            <span className={`font-black ${discrepancy === 0 ? 'text-black' : 'text-bauhaus-red'}`}>
              ₹ {discrepancy.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## 7. Responsive Strategy & Breakpoint Matrix

| Screen Size | Breakpoint | Border Width | Shadow Size | Typography Headline | Grid Columns |
|---|---|---|---|---|---|
| **Mobile** | `< 640px` (`sm`) | $2\text{px}$ (`border-2`) | $3\text{px} - 4\text{px}$ (`shadow-[4px_4px_0px_0px_#121212]`) | `text-4xl` ($36\text{px}$) | Single column ($1\text{ col}$) |
| **Tablet** | `640px - 1024px` (`md`) | $3\text{px} - 4\text{px}$ | $6\text{px}$ (`shadow-bauhaus-md`) | `text-6xl` ($60\text{px}$) | $2\text{ col}$ cards, $1\text{ col}$ chart |
| **Desktop** | `> 1024px` (`lg`/`xl`) | $4\text{px}$ (`border-4`) | $8\text{px} - 12\text{px}$ (`shadow-bauhaus-lg`) | `text-8xl` ($96\text{px}$) | $4\text{ col}$ overview, $8+4\text{ col}$ charts |

---

## 8. Accessibility (A11y) & Usability Standards

1. **High Contrast Ratios (WCAG AAA Compliance)**:
   - Stark Black (`#121212`) on Bauhaus Yellow (`#F0C020`): Contrast ratio **$11.8:1$** (Exceeds AAA).
   - Pure White (`#FFFFFF`) on Bauhaus Red (`#D02020`): Contrast ratio **$4.9:1$** (Exceeds AA for large text/buttons).
   - Pure White (`#FFFFFF`) on Bauhaus Blue (`#1040C0`): Contrast ratio **$7.5:1$** (Exceeds AAA).
   - Stark Black (`#121212`) on Off-White Canvas (`#F0F0F0`): Contrast ratio **$16.2:1$** (Exceeds AAA).

2. **Keyboard Focus States**:
   - Focus rings must never be hidden.
   - All interactive elements use `focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-bauhaus-yellow focus-visible:ring-offset-2 focus-visible:ring-offset-black`.

3. **Screen Readers & Semantic HTML**:
   - Form inputs include explicit `<label className="sr-only">` or visible bold uppercase labels.
   - Financial tables use `<caption className="sr-only">`, proper `scope="col"`, and `aria-sort` indicators.
   - Status indicators pair colors with explicit icons and descriptive text (never color alone).

---

## 9. Visual Anti-Patterns (What NOT to Do)

| Prohibited Anti-Pattern | Why It Breaks Bauhaus | Mandatory Alternative |
|---|---|---|
| ❌ Soft gradients / blur backdrops (`backdrop-blur-md`) | Dilutes geometric clarity and structural honesty | Solid color blocking (`bg-[#1040C0]`, `bg-[#F0C020]`) |
| ❌ Rounded cards (`rounded-xl`, `rounded-2xl`) | Dilutes the constructivist rectangular grid | Strictly `rounded-none` ($0\text{px}$) |
| ❌ Soft ambient shadows (`shadow-xl`) | Creates fuzzy, indistinct depth | Hard offset shadows (`shadow-[8px_8px_0px_0px_#121212]`) |
| ❌ Generic pastel badges (light blue, light pink) | Violates primary color theory | Primary solids with $2\text{px}$ black borders |
| ❌ Muted generic sans (Inter, Arial, Roboto) | Lacks bold constructivist character | Geometric sans **Outfit** (weights 700 & 900) |
| ❌ Floating organic curves or wavy dividers | Undermines structural architectural grid | Pure linear dividing borders (`border-b-4 border-black`) |

---

*This document serves as the immutable UI/UX blueprint for all frontend engineers, designers, and AI coding agents building CC Track.*
