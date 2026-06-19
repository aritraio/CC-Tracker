# Product Map: AI Financial Journal

## Vision

> Turn boring credit card statements into a personal financial story that helps users understand, improve, and optimize their spending.

---

# User Journey

```text
Sign Up
   ↓
Upload Statement PDF
   ↓
AI Extracts Transactions
   ↓
Categorization Engine
   ↓
Financial Journal Generation
   ↓
Insights & Recommendations
   ↓
Goal Planning
   ↓
Monthly Review
```

---

# MVP Architecture

```text
Frontend (Next.js)
        │
        ▼
PDF Upload Service
        │
        ▼
Statement Parser
        │
        ▼
Transaction Database
        │
        ├── Categories
        │
        ├── Journal Engine
        │
        ├── Analytics Engine
        │
        └── AI Insights Engine
        │
        ▼
Dashboard
```

---

# Core Modules

## 1. Authentication

### Features

* Email Login
* Google Login

### Data

```text
User
 ├─ Name
 ├─ Email
 ├─ Created At
 └─ Settings
```

---

## 2. Statement Upload

### Inputs

* PDF Statement
* CSV Statement (future)

### Outputs

```text
Transaction
 ├─ Date
 ├─ Merchant
 ├─ Amount
 ├─ Card
 ├─ Category
 └─ Metadata
```

---

## 3. Transaction Categorization

### Categories

```text
Food
Travel
Shopping
Bills
Education
Healthcare
Entertainment
Subscriptions
Investments
Others
```

### Example

```text
Swiggy
→ Food

Amazon
→ Shopping

Uber
→ Travel
```

---

## 4. Journal Engine ⭐

### Main Differentiator

Converts transactions into a story.

Example:

```text
June 5

Amazon
₹1999

AI Note:
Largest purchase this week.
```

---

### Weekly Summary

```text
Week 2

Spent ₹4,200

Top Category:
Food

Most Frequent Merchant:
Swiggy
```

---

### Monthly Story

```text
June 2026

Spent ₹28,400

+22% from May

Food:
₹8,200

Shopping:
₹5,600

Transport:
₹2,100
```

---

## 5. Analytics Dashboard

### Widgets

#### Spending Breakdown

```text
Food       30%
Shopping   25%
Travel     15%
Bills      10%
Others     20%
```

---

### Monthly Trends

```text
Jan ████

Feb ██████

Mar █████

Apr ███████
```

---

### Merchant Analysis

```text
Amazon
₹15,000

8 Purchases

Average:
₹1,875
```

---

## 6. AI Recommendation Engine

### Recommendation Types

#### Overspending

```text
Food delivery increased 43%.

Potential savings:
₹2,100/month
```

---

#### Subscription Detection

```text
Spotify
ChatGPT
Netflix

Total:
₹1,450/month
```

---

#### Anomaly Detection

```text
₹9,500 spent at Merchant X.

This is 6× your average transaction.
```

---

#### Cashback Optimization

```text
You use Card A for Amazon.

Card B would have earned
₹430 extra cashback.
```

(Massive feature for credit-card enthusiasts.)

---

## 7. Goal Planning

### User Creates Goal

```text
New Laptop

Target:
₹100,000

Deadline:
March 2027
```

---

### AI Projection

```text
Current savings rate:
₹4,500/month

Goal achieved in:
22 months

Reduce food spending by 15%
→ Goal achieved in 18 months
```

---

# Future Features

## V2

### Multi-Card Dashboard

```text
HDFC Millennia
Axis Ace
ICICI Amazon
Amex MRCC
```

Unified spending view.

---

### Spending Heatmap

GitHub-style spending calendar.

```text
🟩🟩⬜🟩
🟨🟩🟩🟥
⬜🟩🟨🟩
```

---

### Monthly Report PDF

```text
Financial Review
June 2026
```

Export and share.

---

## V3

### Account Aggregator Integration

Auto-fetch transactions.

No manual uploads.

---

### AI Chat

```text
Why was my spending higher this month?

↓

Shopping increased by 31%.
Amazon purchases contributed
₹3,200 of the increase.
```

---

# Database Design

```text
Users
│
├── Statements
│
├── Transactions
│
├── Categories
│
├── Goals
│
├── Recommendations
│
└── Reports
```

---

# Launch Roadmap

### Phase 1 (4 Weeks)

✅ Login

✅ PDF Upload

✅ Transaction Parsing

✅ Categorization

✅ Journal Timeline

✅ Monthly AI Summary

---

### Phase 2

✅ Goal Planning

✅ Subscription Detection

✅ Spending Heatmap

✅ Merchant Insights

---

### Phase 3

✅ Cashback Optimization

✅ Account Aggregator

✅ AI Chat Assistant

---

# One-Sentence Pitch

> **AI Financial Journal transforms credit card statements into a personalized financial story, helping users understand spending habits, optimize rewards, and make better money decisions.**
