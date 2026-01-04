# Clarity Session: Phase 1 & 2 YNAB Integration

**Date:** January 3, 2026
**Session Time:** ~2.5 hours
**Status:** Phase 1 ✅ Complete, Phase 2 🚧 Built but NOT TESTED

---

## What We Accomplished

### Phase 1: YNAB API Foundation ✅ COMPLETE & TESTED

**Goal:** Get YNAB API working in Clarity

**What We Built:**
1. Removed all Plaid integration code (plaid-client.ts, sync-worker.ts, test pages)
2. Ported YNAB utilities from reference project:
   - `src/utils/ynab-api.ts` - YNAB API call helpers (GET, POST, PATCH, PUT, DELETE)
   - `src/utils/ynab-transformers.ts` - Data transformation and formatting
   - `src/config/constants.ts` - YNAB constants (DEFAULT_BUDGET_ID, etc.)
3. Created `test_ynab_connection` MCP tool
4. **TESTED & VERIFIED:** Successfully connected to YNAB API and fetched budget list

**Commits:**
- `7642d7d` - Remove Plaid integration, prepare for YNAB
- `4e2e3e8` - Phase 1: YNAB API integration foundation

**Phase 1 Result:** ✅ Working perfectly. YNAB API authenticated and functional.

---

### Phase 2: Staleness Detection System 🚧 BUILT BUT NOT TESTED

**Goal:** Build trust guardrails BEFORE porting financial tools

**What We Built:**

#### 1. Sync Tracker (`src/utils/sync-tracker.ts`)
- Stores sync history in D1
- Tracks: budget_id, timestamp, sync_method ('manual' | 'ynab_auto'), account_count
- Methods:
  - `recordSync()` - Log a successful sync
  - `getLastSync()` - Get most recent sync status
  - `getHoursSinceSync()` - Calculate freshness

#### 2. Staleness Guard (`src/utils/staleness-guard.ts`)
- Trust guardrails with 4 warning levels:
  - **safe** (<12 hours): ✅ Green light
  - **warning** (12-24 hours): ⚠️ Yellow light, suggest sync
  - **stale** (24-48 hours): ⛔ Block affordability checks
  - **critical** (>48 hours): ⛔ Block everything except sync
- `checkDataFreshness()` - Returns freshness status
- `createStalenessWarning()` - Formats user-facing warnings

#### 3. Database Schema Update
- Updated `sync_log` table for YNAB tracking
- Added indexes: `idx_sync_log_budget`
- Migration: `migrations/001_update_sync_log.sql`
- **MIGRATED:** Both local and remote D1 databases updated

#### 4. New MCP Tools
- **`get_sync_status`** - Check data freshness and last sync time
- **`sync_now`** - Manually trigger sync and update tracker

**Deployment:**
- ✅ Built successfully
- ✅ Deployed to production (https://clarity-mcp.wazaqglim.workers.dev)
- ✅ Database migrated (local + remote)
- ⚠️ **NOT TESTED YET**

---

## CRITICAL: Brent's Concerns (Address Tomorrow)

**DO NOT ANSWER THESE TONIGHT - Brent wants to tackle them fresh tomorrow:**

### Concern 1: What is sync_now actually doing?
> "What is the sync now doing, is it calling the sync api on ynab? how do we know it works? the old mcp had that function and i don't think it worked how we thought it did"

### Concern 2: How do we validate sync truth?
> "when we add to the sync table, how do we know the truth? is it because we called the sync, or did we validate it?"

**Context:** These are trust-critical questions. The whole point of Clarity is to rebuild trust after stale data caused real harm. We need to be 100% certain the sync pipeline is honest.

---

## What Needs to Happen Tomorrow

### Before Testing Phase 2:
1. **Answer Brent's concerns** about sync_now behavior
2. **Verify YNAB API sync mechanics** - what does calling `/accounts` actually do?
3. **Decide**: Are we tracking "we called YNAB" or "YNAB successfully synced"?
4. **Potentially revise** sync_now implementation based on answers

### After Addressing Concerns:
1. Restart CLI to pick up new tools
2. Test `get_sync_status` (should show "no sync recorded")
3. Test `sync_now` (verify it actually works)
4. Test `get_sync_status` again (should show fresh data)
5. Verify staleness warnings appear correctly
6. **Only commit Phase 2 after verification**

### Then Phase 3:
Port core financial tools with staleness guards:
- `check_account_affordability` (CRITICAL - this is what hurt before)
- Budget tools
- Transaction tools
- etc.

---

## Technical Notes

### YNAB API Token Setup
- Added YNAB_TOKEN secret via Cloudflare dashboard
- Had to regenerate token (first one gave 401)
- Secret bound to `clarity-mcp` worker (not clarity-sync)
- Deleted old `clarity-sync` worker (Plaid remnant)

### Database Migration
- Initial migration failed (table existed with old structure)
- Created migration script to DROP and recreate sync_log
- Ran on both local and remote D1

### Code Structure
```
clarity/
├── src/
│   ├── financial-mcp.ts          # Main MCP server (3 tools)
│   ├── utils/
│   │   ├── ynab-api.ts           # YNAB API helpers
│   │   ├── ynab-transformers.ts  # Data formatting
│   │   ├── sync-tracker.ts       # Sync history (NEW)
│   │   └── staleness-guard.ts    # Trust guardrails (NEW)
│   └── config/
│       └── constants.ts          # YNAB constants
├── migrations/
│   └── 001_update_sync_log.sql   # Sync table migration
├── schema.sql                    # Full D1 schema
└── wrangler-mcp.toml             # Worker config
```

### Current MCP Tools (as of Phase 2 deploy):
1. `test_ynab_connection` - Test YNAB API (Phase 1) ✅
2. `get_sync_status` - Check data freshness (Phase 2) 🚧
3. `sync_now` - Manual sync trigger (Phase 2) 🚧

---

## Git Status

**Committed:**
- Phase 1 (Plaid removal + YNAB foundation)

**NOT Committed:**
- Phase 2 (staleness detection)
- Migration files

**Uncommitted changes:**
- src/utils/sync-tracker.ts (new)
- src/utils/staleness-guard.ts (new)
- src/financial-mcp.ts (Phase 2 tools added)
- schema.sql (sync_log updated)
- migrations/001_update_sync_log.sql (new)

**Will commit AFTER testing and addressing concerns.**

---

## Session Notes

### What Went Well:
- Clean Plaid removal
- YNAB API connection tested and working
- Phase 2 code builds and deploys successfully
- Good stop point before testing trust-critical code

### What's Risky:
- Phase 2 untested
- Sync pipeline behavior uncertain (Brent's valid concerns)
- Recording sync without validation could recreate the trust problem

### The Right Call:
Stopping now to address concerns fresh tomorrow. This is the "rebuild trust" system - worth getting right.

---

## For Tomorrow's Claude

**Read this section first:**

1. **Don't immediately test Phase 2** - Address Brent's concerns first
2. **The sync pipeline is trust-critical** - wrong here = broken trust again
3. **Questions to research:**
   - What does YNAB API `/accounts` endpoint actually do?
   - Does it trigger sync, or just return current data?
   - How do we verify YNAB successfully synced vs just "we called the API"?
4. **Reference project location:** `.brent/YNAB Project Files/`
   - Check how the old MCP implemented sync
   - Look for any sync validation logic

**Only after addressing concerns:**
- Test Phase 2 thoroughly
- Verify staleness guards work correctly
- Commit Phase 2
- Move to Phase 3 (porting financial tools)

---

**Session Result:** Productive night. Phase 1 complete and tested. Phase 2 built but paused for valid trust concerns. Smart decision to stop and verify tomorrow.
