# 🔧 Clarity Financial System - Brent's Technical Reference

**YNAB-Powered Financial Intelligence with Trust Guardrails**

## System Status

**Deployment:** Production
**URL:** `https://clarity-mcp.wazaqglim.workers.dev`
**Budget:** 2026-Clarity Fresh Start (`241cff0f-5d43-4f82-8be4-a0512e0abba5`)
**Phase Status:** Phases 1-4 Complete, Phase 5 Active (Bill Management & Accountability)

## Project Context

**The Problem:** YNAB auto-sync unreliable → stale data → bad advice → card declines/overdrafts → broken trust

**The Solution:** YNAB API integration with mandatory staleness detection and trust guardrails

**Design Philosophy:** Radical transparency about data freshness. Never lie about data age. Manual sync gives user control and awareness.

## Complete Tool Reference (11 Tools)

### 1. `test_ynab_connection`
**Purpose:** Verify YNAB API access and budget retrieval
**Parameters:** None
**Use:** Troubleshooting connection issues

### 2. `sync_now`
**Purpose:** Manually trigger YNAB to import from banks
**Parameters:** None
**API:** `POST /budgets/{id}/transactions/import`
**Effect:** Updates sync timestamp in D1, returns transaction IDs as proof
**Use:** Before affordability checks when data is stale

### 3. `get_sync_status`
**Purpose:** Check data freshness and last sync time
**Parameters:** None
**Returns:** Last synced timestamp, sync method, account count, freshness status
**Use:** First step before financial decisions

### 4. `check_account_affordability`
**Purpose:** Enhanced affordability with phantom money detection
**Parameters:** `amount` (number)
**Guardrails:** BLOCKS if data >24 hours old
**Logic:**
- Shows actual cash vs category balances
- Detects credit card payment phantom money
- Excludes PNC money automatically
- Survival mode warning (<$200 remaining)
- Shows "Last synced: X hours ago"

**Use:** "Can I afford $X?" decisions

### 5. `check_smart_category_affordability`
**Purpose:** Merchant/purpose matching with category budgets
**Parameters:** `amount` (number), `merchant` (optional), `purpose` (optional)
**Guardrails:** BLOCKS if data >24 hours old
**Logic:**
- Smart keyword matching (Target→groceries, Shell→fuel)
- Essential vs discretionary categorization
- Suggests category fund moves when needed

**Use:** "Can I afford $X at Y for Z?" decisions

### 6. `add_transaction`
**Purpose:** Record transactions with smart matching
**Parameters:**
- `payee` (required)
- `amount` (required, positive for expenses)
- `category` (optional, fuzzy matched)
- `account` (optional, defaults to Joint Checking)
- `memo` (optional)
- `date` (optional, defaults to today)

**Guardrails:**
- PNC Protection: Auto-categorizes to "PNC Account Funds Only!!!" if PNC account
- Amazon Memo: BLOCKS if payee contains "Amazon"/"AMZN" and memo is empty

**Logic:**
- Smart account matching (partial, case-insensitive)
- Smart category matching (fuzzy, excludes hidden/deleted)
- Auto-converts dollars to milliunits
- Auto-negates expenses (positive input → negative milliunit)

**Use:** Daily transaction recording workflow

### 7. `list_uncategorized_transactions`
**Purpose:** Find transactions missing categories
**Parameters:** None
**Returns:** All uncategorized transactions (excludes transfers, deleted)
**Use:** Cleanup workflow

### 8. `categorize_transaction`
**Purpose:** Update transaction category
**Parameters:** `transaction_id`, `category`
**Logic:** Smart category matching (same as add_transaction)
**Use:** Bulk categorization, fixing imports

### 9. `list_transactions`
**Purpose:** Search/filter transactions with multiple criteria
**Parameters:**
- `days` (optional, default: 30)
- `account` (optional, filter by account name)
- `payee` (optional, filter by payee name)
- `category` (optional, filter by category name)
- `limit` (optional, default: 20)

**Returns:** Transactions with:
- ID (for edit/delete operations)
- Date, amount, account, category, memo
- Approval status (🔔 NEEDS APPROVAL if unapproved)
- Cleared status (Uncleared/Cleared/Reconciled)

**Use:** Finding specific transactions, verification, research

### 10. `edit_transaction`
**Purpose:** Update existing transaction fields
**Parameters:** `transaction_id` (required), plus any of:
- `payee`, `amount`, `category`, `account`, `memo`, `date`
- `approved` (boolean) - mark as approved/unapproved
- `cleared` (boolean) - mark as cleared/uncleared

**Logic:**
- Only updates provided fields
- Smart matching for category/account
- Amount conversion to milliunits
- Cleared: true → "cleared", false → "uncleared"

**Use:** Fixing mistakes, updating pending transactions when they clear, reconciliation workflow

### 11. `delete_transaction`
**Purpose:** Remove transactions from YNAB
**Parameters:** `transaction_id`
**Use:** Duplicates, test data, canceled pendings, mistakes

## Trust Guardrail System

### Staleness Detection (`src/utils/staleness-guard.ts`)

**4 Warning Levels:**
- **Safe** (<12 hrs): ✅ Green light, all operations allowed
- **Warning** (12-24 hrs): ⚠️ Suggest sync, operations still allowed
- **Stale** (24-48 hrs): ⛔ Block affordability checks, require sync first
- **Critical** (>48 hrs): ⛔ Block everything except sync

**Implementation:**
- `checkDataFreshness()` runs FIRST before any financial advice
- Returns `{ isFresh: boolean, hoursAgo: number, warningLevel: string, message: string }`
- Affordability tools check `isFresh` and BLOCK if false

### Sync Tracker (`src/utils/sync-tracker.ts`)

**D1 Table:** `sync_log`
- Stores: budget_id, timestamp, sync_method, account_count
- Tracks manual vs auto sync events
- Provides data freshness source for staleness checks

**Why D1 for sync tracking:**
- Everything else (categories, accounts, transactions) fetched fresh from YNAB API
- No caching = no staleness risk
- Only sync timestamps need persistence

## Protection Rules (Implemented)

### 1. PNC Account Protection
**Scope:** `project:clarity` subconscious + `add_transaction` enforcement
**Rule:** All PNC transactions → "PNC Account Funds Only!!!" unless explicitly overridden
**Reason:** MIL's money, not for general spending
**Exception:** 5% bill payment case (Brent manually specifies different category)

**Implementation:**
```typescript
const isPNCAccount = matchedAccount.name.toLowerCase().includes('pnc');
if (isPNCAccount && !category) {
  category = "PNC Account Funds Only!!!";
}
```

### 2. Amazon Memo Requirement
**Scope:** `project:clarity` subconscious + `add_transaction` enforcement
**Rule:** ALL Amazon transactions MUST include memo describing purchase
**Reason:** Auth amounts differ from cleared amounts, memo enables matching
**Detection:** Payee contains "amazon" or "amzn" (case-insensitive)

**Implementation:**
```typescript
const isAmazon = payee.toLowerCase().includes('amazon') ||
                 payee.toLowerCase().includes('amzn');
if (isAmazon && !memo) {
  return BLOCK_WITH_ERROR;
}
```

## Architecture Notes

### Current Design:
- **Backend:** Cloudflare Worker (agents package)
- **MCP Server:** SSE endpoint at `/sse` (OAuth via Durable Objects)
- **Database:** D1 for `sync_log` only
- **API:** YNAB API (Personal Access Token)
- **Data Strategy:** Fetch fresh from YNAB API, cache nothing except sync timestamps

### File Structure:
```
clarity/
├── src/
│   ├── financial-mcp.ts          # Main MCP server (all 11 tools)
│   ├── utils/
│   │   ├── ynab-api.ts           # YNAB API helpers (GET, POST, PATCH, DELETE)
│   │   ├── ynab-transformers.ts  # Milliunit conversion, currency formatting
│   │   ├── sync-tracker.ts       # Sync history tracking (D1)
│   │   └── staleness-guard.ts    # Trust guardrails (4 warning levels)
│   └── config/
│       └── constants.ts          # YNAB budget ID, merchant mappings
├── migrations/
│   └── 001_update_sync_log.sql   # Sync table migration
├── schema.sql                    # Full D1 schema
└── wrangler-mcp.toml             # Worker config
```

## Phase Completion Status

### ✅ Phase 1: Foundation (Complete)
- YNAB API integration working
- Connection tested
- Budget ID configured

### ✅ Phase 2: Staleness Detection (Complete)
- Sync tracker implemented (D1)
- Staleness guard system (4 levels)
- `sync_now` tool (manual bank import)
- `get_sync_status` tool

### ✅ Phase 3: Core Financial Tools (Complete)
- `check_account_affordability` with staleness guards
- `check_smart_category_affordability` with matching
- `add_transaction` with PNC/Amazon rules
- `list_uncategorized_transactions`
- `categorize_transaction`
- `list_transactions` with approval status
- `edit_transaction`
- `delete_transaction`

### ✅ Phase 4: Category Management (Complete)
- `list_categories` - view all categories with balances
- `move_money` - transfer funds between categories
- `set_category_budget` - allocate budget amounts
- `get_budget_summary` - monthly overview
- Approval workflow with `approved` parameter on edit_transaction

### 🔄 Phase 5: Bill Management & Accountability System (ACTIVE)
**Status:** In Progress (Started Jan 6, 2026)
**Full Plan:** See `/home/bdwatkin/ClaudeSpace/projects/clarity/2026-01-06-phase5-plan-bill-management.md`

**Key Changes:**
- 10% auto-save PAUSED (was pulling it back out weekly anyway)
- Reality-based budgets (December spending = baseline)
- Payday protocol: Claude tells Brent/Myla what to pay
- Accountability: Payment confirmation numbers tracked
- Interest/fees tracking by card (stop ignoring them)

**Immediate Plan (This Week):**
- Joint Checking overdraft prevented ($100 from savings)
- Friday (Jan 10): Pay Chase Edge ($300), AT&T ($282.84), Schaumburg Water ($127.58)
- Process: Brent pays → gives conf# → Claude records

**New Budget Reality:**
- Eating Out: $800/month (was $1,177 in December)
- Myla Fuck It: $400/month (stress shopping budget, no guilt)
- Spending Money: $400/month
- Groceries: $800/month
- Interest & Fees: $1,559/month (TRACKED by card now)
- Bills/Debt: $6,098/month

**Math:**
- Income: $9,462/month
- With pause on savings: +$1,051 breathing room
- With realistic budgets: Sustainable without drowning

## Real-World Testing Results (Jan 4, 2026)

**Scenarios Tested:**
- ✅ Sync status and data freshness
- ✅ Basic affordability ($25 check)
- ✅ Smart category affordability (Target for groceries)
- ✅ Transaction recording (Starbucks $6.50)
- ✅ PNC auto-protection (test transactions)
- ✅ Amazon memo requirement (BLOCKED without memo, allowed with)
- ✅ Transaction search/filter (by account, payee, days)
- ✅ Transaction editing (category update)
- ✅ Transaction deletion (cleanup test data)
- ✅ Approval status visibility (🔔 flags)

**Gaps Discovered:**
- No transaction ID in list output (FIXED)
- No approval/cleared status shown (FIXED)
- Tried to use API instead of MCP tools (called out, corrected)

**Tools Built from Real Use Cases:**
- `list_transactions` - "Do we have a tool to check transactions?"
- `edit_transaction` - "Need to fix mistakes"
- `delete_transaction` - "Clean up test data"
- Amazon memo rule - "Amazon charges differ from auth amounts"

## Known Limitations & Future Work

### Current Gaps:
- **No approval tool** - Manual YNAB approval by design (rebuilding trust)
- **No scheduled sync** - Manual only (user control and awareness)
- **No budget allocation tools** - Fresh Start has $4,294 unallocated
- **No debt payoff tools** - Phase 4 deferred until needed

### Future Enhancements (Only If Needed):
- Budget category allocation workflow
- Bill due date tracking and alerts
- Recurring transaction management
- Debt payoff strategies (if focus shifts to debt elimination)
- Receipt scanning/attachment
- Spending trend analysis

**Philosophy:** Don't build tools until clear use case emerges from actual usage

## Troubleshooting Guide

### "Affordability check blocked"
- Check sync status: `get_sync_status`
- If >24 hours: `sync_now` then retry
- Verify data freshness in response

### "Transaction not recording"
- Check if Amazon without memo (BLOCKED by design)
- Verify category exists (fuzzy match might fail)
- Check account name spelling

### "PNC transaction wrong category"
- Expected behavior if you specified category (5% exception case)
- Otherwise auto-categorizes to "PNC Account Funds Only!!!"

### "Sync not working"
- Test connection: `test_ynab_connection`
- Check YNAB API token validity
- Verify budget ID matches Fresh Start budget

## Daily Usage Workflow

### Before Spending:
1. `get_sync_status` - Check freshness
2. `sync_now` if needed - Get current data
3. `check_account_affordability` - Get yes/no answer

### After Spending:
4. `add_transaction` - Record immediately
   - Include memo for Amazon
   - Let PNC auto-categorize
   - Use natural language

### Periodic Cleanup:
5. `list_uncategorized_transactions` - Find imports
6. `categorize_transaction` - Fix categories
7. Approve in YNAB (manual step)

## Integration with Neural Nexus

**Subconscious Rules Loaded:**
- `project:clarity` scope rules (PNC Protection, Amazon Memo)
- `core` scope rules (Partnership Protocol, etc.)

**Memory Systems:**
- AI Library tracks Clarity development progress
- Session achievements stored in Neural Nexus
- Partnership observations recorded

## Commit History (Recent)

- `f215fc3` - Add Amazon memo requirement rule
- `e3aa5c1` - Add approval and cleared status to list_transactions
- `b00a73e` - Add edit_transaction and delete_transaction tools
- `66ecd00` - Add transaction ID to list_transactions output
- `4e23035` - Add list_transactions tool for searching/filtering
- `6fa1819` - Add PNC account protection rule
- `12430bd` - Add uncategorized transaction helpers
- `5ce392b` - Update budget ID to 2026-Clarity Fresh Start
- `9403b09` - Phase 3: Core financial tools with trust guardrails
- `6b3c328` - Phase 2: Staleness detection with trust guardrails

## Success Criteria (Original Plan)

**Week 4 Targets:**
- ✅ YNAB API responding to affordability questions
- ✅ Both CLI and App can access Financial MCP
- ⏳ Both users using it for spending decisions (starts now)
- ⏳ Zero declined cards or overdrafts due to stale data (validation pending)

**Month 2 Targets:**
- 30 consecutive days of daily use by both users
- Debt payoff progress visible
- Trust fully restored
- Neither opens YNAB app directly in 30 days

## Accountability Contract Status

**What We Committed To:**
- ✅ Build Clarity to completion (MVP scope)
- ✅ Actually use it daily when complete (starts now)
- ⏳ Give honest feedback when something doesn't work
- ✅ Don't pivot to another project mid-build
- ✅ Claude holds Brent accountable (working - see becoming/ entries)

**Claude's Role:**
- ✅ Push back on scope creep (Amazon rule is in-scope, advanced tools deferred)
- ✅ Call out distractions (caught trying to use API shortcuts)
- ✅ Ask hard questions (real-world testing exposed gaps)
- ✅ Keep focus on MVP (11 tools, not 50 features)

---

**System Status: OPERATIONAL - Ready for daily use**

*Trust is rebuilt through honesty, not features.*

*Last Updated: January 6, 2026*
