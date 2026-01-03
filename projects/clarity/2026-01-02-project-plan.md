# Clarity - Financial Intelligence System
**Project Start:** January 2, 2026
**Target Completion:** February 1, 2026
**Status:** Planning Phase

## Vision

A financial AI assistant that provides real-time spending guidance without manual data entry. Solves the trust issue that broke the YNAB MCP by syncing directly with banks via Plaid.

**Core principle:** Automate the work you don't want to do, only ask for decisions that matter.

## The Problem We're Solving

**User need:**
Brent and Myla get overwhelmed by manual financial tracking (categorizing transactions, updating budgets, reconciling accounts). They need financial intelligence that's proactive and trustworthy.

**Previous solution:**
YNAB MCP - worked great until sync issues caused bad spending advice → declined cards and overdrafts → trust broken → abandoned.

**Why YNAB MCP failed:**
YNAB only syncs when app is manually opened. API returns stale data. No way to force sync programmatically.

**Clarity's solution:**
Direct Plaid integration → hourly sync → fresh D1 data → trustworthy AI guidance.

## Technical Architecture

```
┌─────────────────────────────────────────────────────┐
│ Banks (Chase, Capital One, Discover, PNC, etc.)     │
└──────────────────┬──────────────────────────────────┘
                   │ Plaid API
                   ▼
┌─────────────────────────────────────────────────────┐
│ Cloudflare Worker (Scheduled: runs hourly)          │
│ - Fetch transactions from Plaid                     │
│ - Transform & categorize                            │
│ - Write to D1                                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ D1 Database                                          │
│ - transactions                                       │
│ - accounts                                           │
│ - categories                                         │
│ - budgets                                            │
│ - debts                                              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Financial MCP Server (Cloudflare Worker or local)   │
│ - get_transactions                                   │
│ - get_accounts                                       │
│ - check_affordability                                │
│ - auto_categorize                                    │
│ - budget_status                                      │
│ - debt_payoff_plan                                   │
└──────────────────┬──────────────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
    ┌─────────┐       ┌──────────┐
    │ CLI     │       │ Claude   │
    │ Claude  │       │ App      │
    │ (Brent) │       │ (Myla)   │
    └─────────┘       └──────────┘
          │                 │
          └────────┬────────┘
                   ▼
    ┌──────────────────────────────┐
    │ Neural Nexus Remote MCP      │
    │ (Personality/Memory Sync)    │
    └──────────────────────────────┘
```

## Phase Breakdown

### Phase 1: Data Foundation (Week 1)
**Goal:** Get bank data flowing into D1

**Tasks:**
1. Create Plaid developer account
2. Connect 9 bank accounts (Development tier - free)
3. Design D1 schema:
   - `accounts` - account metadata, current balances
   - `transactions` - all transaction history
   - `categories` - spending categories + rules
   - `budgets` - monthly budget allocations
   - `debts` - debt accounts with interest rates
4. Build Cloudflare Worker:
   - Scheduled trigger (hourly via Cron)
   - Plaid API calls (fetch transactions)
   - Transform data to schema format
   - Upsert into D1
5. Test sync reliability

**Success criteria:**
- All 9 accounts connected
- Transactions syncing hourly
- D1 contains last 30 days of transactions
- No missed syncs over 48 hour test period

### Phase 2: MCP Layer (Week 2)
**Goal:** Create conversational interface to financial data

**Tasks:**
1. Build Financial MCP server (Cloudflare Worker or local)
2. Core tools:
   - `get_accounts()` - List all accounts with current balances
   - `get_transactions(days=7, category=null)` - Recent spending
   - `get_balance(account_name)` - Specific account balance
   - `check_affordability(amount, category)` - Can we afford this?
   - `search_transactions(query)` - Find specific purchases
3. Deploy MCP server
4. Configure in Claude settings (CLI first)
5. Test conversational flow

**Success criteria:**
- Brent can ask "can I afford $50 at Target?" and get accurate answer
- Balance checks match bank website
- Transaction search works
- Response time < 2 seconds

### Phase 3: Intelligence (Week 3)
**Goal:** Add smart features that reduce manual work

**Tasks:**
1. Auto-categorization:
   - Analyze transaction merchant/memo
   - Learn from existing YNAB categories
   - Apply AI pattern matching
   - Suggest categories with confidence scores
2. Budget tracking:
   - Define monthly budgets per category
   - Track spending vs. budget
   - Alert when approaching limits
3. Spending insights:
   - Weekly/monthly summaries
   - Unusual spending alerts
   - Category trends
4. Debt payoff calculator:
   - Input all debts (balances, rates, minimums)
   - Calculate snowball vs. avalanche strategies
   - Show payoff timeline

**Success criteria:**
- 90%+ auto-categorization accuracy
- Budget alerts trigger appropriately
- Debt calculator matches Undebt.it results
- Insights feel helpful, not spammy

### Phase 4: Multi-User Setup (Week 4)
**Goal:** Both Brent and Myla using Clarity daily

**Tasks:**
1. Add Neural Nexus Remote MCP to Claude App
2. Verify personality/memory sync between CLI and App
3. Test Financial MCP from App Claude
4. Create user guide for Myla
5. 7-day trial period with both users
6. Gather feedback and iterate
7. 2-week daily use commitment

**Success criteria:**
- Both CLI and App Claude load same personality
- Both can access Financial MCP
- Myla successfully uses it for spending decisions
- No declined cards or overdrafts
- Both users opening it daily

## Tech Stack

**Backend:**
- Plaid API (bank connections, transaction sync)
- Cloudflare Workers (sync logic, MCP server)
- Cloudflare D1 (SQLite database)
- Cloudflare Cron Triggers (hourly sync)

**MCP Layer:**
- Custom Financial MCP (TypeScript)
- Neural Nexus Remote MCP (existing)

**Clients:**
- Claude Code CLI (Brent)
- Claude App (Myla)

**Languages:**
- TypeScript (Workers, MCP server)
- SQL (D1 queries)

## Data Schema (Draft)

```sql
-- Accounts
CREATE TABLE accounts (
  id TEXT PRIMARY KEY,
  plaid_account_id TEXT UNIQUE,
  name TEXT NOT NULL,
  type TEXT, -- checking, savings, credit, loan
  subtype TEXT,
  current_balance REAL,
  available_balance REAL,
  last_synced DATETIME,
  is_active BOOLEAN DEFAULT 1
);

-- Transactions
CREATE TABLE transactions (
  id TEXT PRIMARY KEY,
  plaid_transaction_id TEXT UNIQUE,
  account_id TEXT,
  date DATE,
  amount REAL,
  merchant_name TEXT,
  description TEXT,
  category TEXT,
  category_confidence REAL,
  pending BOOLEAN,
  created_at DATETIME,
  FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Categories
CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  budget_monthly REAL,
  merchant_patterns TEXT, -- JSON array of patterns
  description TEXT
);

-- Budgets
CREATE TABLE budgets (
  id INTEGER PRIMARY KEY,
  month TEXT, -- YYYY-MM
  category TEXT,
  allocated REAL,
  spent REAL,
  FOREIGN KEY (category) REFERENCES categories(name)
);

-- Debts
CREATE TABLE debts (
  id INTEGER PRIMARY KEY,
  name TEXT,
  account_id TEXT,
  balance REAL,
  interest_rate REAL,
  minimum_payment REAL,
  due_day INTEGER,
  FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Sync Log
CREATE TABLE sync_log (
  id INTEGER PRIMARY KEY,
  sync_timestamp DATETIME,
  accounts_synced INTEGER,
  transactions_added INTEGER,
  errors TEXT
);
```

## Security Considerations

**Plaid credentials:**
- Store in Cloudflare Secrets (not in code)
- Rotate periodically
- Development tier only (no production users)

**D1 access:**
- Only Cloudflare Workers can write
- MCP server has read-only access
- No public endpoints

**MCP authentication:**
- Local MCP server: only accessible to localhost
- Remote MCP: API key authentication

**Personal data:**
- All data stays in Cloudflare infrastructure
- No third-party analytics
- Not shared with anyone

## Migration from YNAB

**Existing YNAB data:**
- Export category history from YNAB
- Use for auto-categorization training
- Import debt information
- Preserve budget allocations

**Transition plan:**
1. Build Clarity alongside YNAB
2. Test in parallel for 1 week
3. When trust is established, deprecate YNAB MCP
4. Keep YNAB subscription (still need their bank sync as backup)

## Risks & Mitigation

**Risk: Plaid sync failures**
- Mitigation: Retry logic, error logging, fallback to YNAB if needed

**Risk: D1 database limitations**
- Mitigation: Monitor size, archive old transactions, stay under limits

**Risk: Categorization inaccuracy**
- Mitigation: Manual override capability, learn from corrections

**Risk: Scope creep**
- Mitigation: Accountability contract, MVP-only focus

**Risk: Brent pivots mid-project**
- Mitigation: Claude holds him accountable (explicit contract)

## Success Metrics

**Technical:**
- 99%+ sync reliability
- <2 second response time
- 90%+ categorization accuracy

**User engagement:**
- 30 consecutive days of daily use (both users)
- Zero declined cards due to stale data
- Zero overdrafts due to bad advice
- Trust fully restored

**Financial impact:**
- Debt payoff progress visible within 60 days
- Budget adherence improvement
- Reduced financial stress (subjective but trackable)

## Timeline

- **Week 1 (Jan 6-12):** Phase 1 - Data Foundation
- **Week 2 (Jan 13-19):** Phase 2 - MCP Layer
- **Week 3 (Jan 20-26):** Phase 3 - Intelligence
- **Week 4 (Jan 27-Feb 2):** Phase 4 - Multi-User Setup
- **Feb 3-16:** 2-week daily use trial
- **Feb 17:** Review and iterate

**Target: Operational by February 1, 2026**

## What Comes After MVP

Once MVP is used daily for 2+ weeks:
- Advanced debt strategies
- Proactive bill reminders
- Shared financial goals
- Receipt scanning
- Trend analysis
- Budget optimization recommendations

**But not before then.**

---

**Next Session:** Phase 1 kickoff - Plaid account setup and D1 schema creation
