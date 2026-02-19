# WazzieStocks Session: Performance Tracking + Playground
**Date:** 2026-02-19
**Duration:** ~2 hours

---

## Context

Picked up after the Feb 18 session. Implemented a pre-planned spec for recommendation
performance tracking, then caught a few UX issues and finally unblocked the virtual
portfolio ("playground") that had been silently dead since launch.

Brent context this session: discussed his actual investing background (beginner, started
on Public.com with recommended stocks + REITs, $20/wk to brokerage + $25/wk to HYC,
stopped mid-last-year due to budget). This shaped the HYC decision below.

---

## What We Built

### 1. Recommendation Performance Tracking

**Goal:** Snap prices at key moments so we can measure how recs actually perform.

**DB changes:**
- Added `recommendation_price REAL` and `execution_price REAL` columns to
  `real_portfolio_recommendations` (ALTER TABLE migrations, idempotent)
- New `get_recommendation_by_id(id)` method
- New `get_executed_recommendations(limit)` method
- `save_recommendation()` now accepts `recommendation_price`
- `update_recommendation_status()` now accepts `execution_price`

**Engine changes:**
- Save loop in `analyze_real_portfolio()` calls `get_quote()` per rec and stores
  `recommendation_price` at generation time (quote already cached from analysis run)
- `mark_recommendation_executed()` now fetches live quote and snaps `execution_price`
  before updating DB

**New `get_performance_summary()`:**
- Fetches all executed recs
- For each with `execution_price`: computes `pct_gain`, `dollar_gain`, `days_held`
- Returns accuracy stats (`"6 of 8 profitable"` style)
- Calls `_compute_virtual_comparison()` to benchmark against virtual portfolio

**New `_compute_virtual_comparison()`:**
- Finds earliest execution date across recs with P&L data
- Fetches virtual portfolio snapshots from that date forward
- Computes `virtual_return_pct` as delta from baseline snapshot to latest
- Returns avg rec return vs virtual, and how many recs beat virtual

**Verified:** Next Sunday's run will show `recommendation_price` for all new recs.
Existing recs (ids 1-41, pre-this-change) show NULL — graceful N/A in UI.

---

### 2. Recommendations Page Overhaul

**4-tab nav:** Pending (N) | Executed (N) | Rejected (N) | Performance

Each section gated with `{% if active_tab == '...' %}` — one visible at a time.
Lazy-loads performance data only when Performance tab is requested (avoids N quote
fetches on every page load).

**Summary bar (pending tab):**
- Shows rec count, total suggested cost, avg per position
- Computed from `suggested_shares * recommendation_price` in Jinja
- First run showed $459 (pre-cap fix) — expected, correct

**Performance tab:**
- Accuracy scorecard: "X of Y profitable"
- 2-column grid: Avg Rec Return vs Virtual Portfolio return (same period)
- Per-rec cards with colored P&L, entry/current price, days held, confidence
- Recs without `execution_price` show "N/A" cleanly

---

### 3. Real Portfolio Page Cleanup

Removed the full pending recommendations list from `/real-portfolio`. With 29 holdings
and growing, it was going to be a wall of scrolling. Replaced with a slim teaser card:
"13 pending recommendations waiting for your review → View Recommendations"

Also removed the now-unused JS functions (`markExecuted`, `markRejected`) and CSS.

---

### 4. HYC Buying Power Fix

**Discussion:** Brent's cash was $0, HYC was $328. Previous code treated HYC as
spendable buying power (`cash + hyc`). Recs were sizing against $328 — not right.
HYC is yield-earning savings, not trading cash.

**Decision:** Exclude HYC, set $100 hard cap as floor.
- Cap acts as floor: `max(actual_cash, cap)`
- When cash is $0: uses $100
- When Brent deposits cash > $100: actual wins automatically
- When he restarts auto-deposits later: same formula, no code change needed

**Config (`config.yaml`):**
```yaml
public_com:
  include_hyc: false
  buying_power_cap: 100
```

---

### 5. Virtual Portfolio Pipeline Fix ("The Playground")

**What the playground is:** Virtual $1K portfolio where Claude auto-trades with real
market data but fake money. Decision engine + portfolio manager were fully built
(Phase 1). Notes from Feb 16 and Feb 18 both said "just needs wiring."

**What we found:** The infrastructure WAS wired. The scheduler runs `deep_analysis()`
every Sunday at 10 PM which calls `process_scan_results()` which auto-executes trades.
The real problem: Stage 1 had been returning 0 stocks since day one.

**Root cause:** `get_multiple_quotes()` returns `price` but NOT `volume` or `market_cap`
from the bulk Finnhub API. The Stage 1 filter used `.get('key', 0)` which returns `None`
when the key exists but has a None value. `None >= 1,000,000,000` → silently False.
Every stock filtered out. 503 → 0 every single day since launch.

**Same issue in Stage 2:** `_calculate_fundamental_score()` used the same pattern —
`fundamentals.get('pe_ratio', 0)` returns `None` not `0` when key is present but null.
`10 <= None <= 25` → TypeError, crash.

**Fix:**
- Stage 1: Use `or 0` to coerce None. Skip market_cap/volume filters when data is
  unavailable (treat as "pass" — Stage 2 fundamentals does the real filtering)
- Stage 2: Same `or 0` pattern on all 5 scoring fields

**Verified:** 503 → 120 (Stage 1) → Stage 2 working (XOM: 60, JNJ: 55, etc.)
Next Sunday at 10 PM: first real virtual portfolio auto-trade.

---

## Architecture Post-Session

```
Virtual portfolio:  $1K fake money, auto-traded by Claude (Sunday 10 PM)
                    503 → Stage 1 (price filter) → 120 → Stage 2 (fundamentals) → 30
                    → Stage 3 (Claude) → confidence ≥ 80 → auto-execute

Real portfolio:     Public.com (read-only), human-in-the-loop
                    Buying power = max(cash, $100 cap) — HYC excluded
                    Recs: price snapped at generation + execution for P&L tracking
                    Performance tab shows per-rec P&L vs virtual benchmark

Weekly Sunday run:  Real recs at 10:30 PM, virtual trades at 10 PM
```

---

## Remaining Work

Nothing on the current roadmap. This iteration is complete.

Ideas for future iterations:
- Push notifications when new recs are generated
- Historical chart of virtual portfolio vs real portfolio vs S&P 500
- Rec quality score that improves as executed rec P&L data accumulates

---

## Lessons

**`dict.get('key', 0)` ≠ `dict.get('key') or 0`**
When the key exists but value is None, the default is ignored — you get None.
Use `or 0` (or `or default`) when the value itself might be None.

**"Just needs wiring" is worth verifying.** The virtual portfolio had been silently
dead since Feb 15. The pipeline was built and scheduled, but a None comparison bug
meant it had never once made it past Stage 1. Always run the pipeline end-to-end
before calling infrastructure "done."
