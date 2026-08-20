-- =============================================================================
-- CC Track Database Schema & Migration (PostgreSQL / Supabase)
-- Version: 1.0.0
-- Security: Row Level Security (RLS) Enabled on all tables
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------------------------------------------------------
-- 1. USERS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(150),
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 2. CREDIT CARDS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    issuer VARCHAR(50) NOT NULL, -- HDFC, ICICI, SBI, AXIS, AMEX
    card_name VARCHAR(100),       -- Regalia, Millennia, Amazon Pay ICICI
    card_last_4 VARCHAR(4),
    credit_limit NUMERIC(12, 2),
    billing_cycle_day INT CHECK (billing_cycle_day BETWEEN 1 AND 31),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 3. STATEMENTS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS statements (
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
    reconciliation_status VARCHAR(20) NOT NULL DEFAULT 'VALIDATED', -- VALIDATED, REVIEW_REQUIRED
    reconciliation_delta NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    raw_text_length INT DEFAULT 0,
    unparsed_lines JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 4. TRANSACTIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement_id UUID NOT NULL REFERENCES statements(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    post_date DATE,
    merchant_raw TEXT NOT NULL,
    merchant_normalized VARCHAR(150),
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    transaction_type VARCHAR(30) NOT NULL DEFAULT 'PURCHASE', -- PURCHASE, REFUND, FEE, GST, EMI, etc.
    category VARCHAR(50) NOT NULL DEFAULT 'Other / Uncategorized',
    subcategory VARCHAR(50),
    tier INT DEFAULT 1,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    source_page INT DEFAULT 1,
    confidence_score NUMERIC(3, 2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 5. DETERMINISTIC FINDINGS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement_id UUID NOT NULL REFERENCES statements(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    finding_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', -- CRITICAL, HIGH, MEDIUM, LOW, INFO
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    impact_amount NUMERIC(12, 2),
    actionable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 6. RECOMMENDATIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement_id UUID REFERENCES statements(id) ON DELETE CASCADE,
    finding_id UUID REFERENCES findings(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rec_type VARCHAR(50) NOT NULL, -- CATEGORY_REDUCTION, SUBSCRIPTION_AUDIT, etc.
    title VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    action_text TEXT NOT NULL,
    estimated_savings NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    confidence NUMERIC(3, 2) NOT NULL DEFAULT 1.00,
    priority INT NOT NULL DEFAULT 1,
    target_category VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, ACCEPTED, DISMISSED, COMPLETED
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 7. FEEDBACK & OUTCOME EVENTS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID REFERENCES recommendations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(30) NOT NULL, -- VIEWED, EXPLORED_TRANSACTIONS, ACCEPTED, DISMISSED, COMPLETED, UNDONE
    dismiss_reason VARCHAR(50),
    feedback_notes TEXT,
    event_payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- PERFORMANCE INDEXES
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
CREATE INDEX IF NOT EXISTS idx_statements_user_id ON statements(user_id);
CREATE INDEX IF NOT EXISTS idx_statements_file_hash ON statements(file_hash);
CREATE INDEX IF NOT EXISTS idx_statements_period ON statements(period_start, period_end);

CREATE INDEX IF NOT EXISTS idx_transactions_statement_id ON transactions(statement_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_recurring ON transactions(is_recurring) WHERE is_recurring = TRUE;

CREATE INDEX IF NOT EXISTS idx_findings_statement_id ON findings(statement_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_statement_id ON recommendations(statement_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_status ON recommendations(user_id, status);
CREATE INDEX IF NOT EXISTS idx_rec_events_rec_id ON recommendation_events(recommendation_id);

-- -----------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES (Supabase Auth Integration)
-- -----------------------------------------------------------------------------
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation_events ENABLE ROW LEVEL SECURITY;

-- Users: read & update own profile
CREATE POLICY "Users can manage own profile"
    ON users FOR ALL
    USING (auth.uid() = id);

-- Cards: user isolation
CREATE POLICY "Users can manage own cards"
    ON cards FOR ALL
    USING (auth.uid() = user_id);

-- Statements: user isolation
CREATE POLICY "Users can manage own statements"
    ON statements FOR ALL
    USING (auth.uid() = user_id);

-- Transactions: user isolation
CREATE POLICY "Users can manage own transactions"
    ON transactions FOR ALL
    USING (auth.uid() = user_id);

-- Findings: user isolation
CREATE POLICY "Users can view own findings"
    ON findings FOR ALL
    USING (auth.uid() = user_id);

-- Recommendations: user isolation
CREATE POLICY "Users can manage own recommendations"
    ON recommendations FOR ALL
    USING (auth.uid() = user_id);

-- Recommendation Events: user isolation
CREATE POLICY "Users can manage own feedback events"
    ON recommendation_events FOR ALL
    USING (auth.uid() = user_id);
