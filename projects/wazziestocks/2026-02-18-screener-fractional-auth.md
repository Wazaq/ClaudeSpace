# WazzieStocks Session: Screener + Fractional Shares + Auth
**Date:** 2026-02-18
**Duration:** ~3.5 hours

---

## Context

Came in after a stressful day for Brent (no laptop yesterday). First addressed a concern
about an Anthropic pricing rumor (Reddit post about enterprise max plans being dropped).
Short version: the enterprise piece has corroboration, individual Max plans don't. Brent
is on Max 5x ($100/mo, never hits limits) - exactly the profitable customer they keep.

Then dove into WazzieStocks priorities.

---

## What We Built

### 1. S&P 500 Discovery Screener

**Problem:** `_find_buy_opportunities()` was using FMP screener (removed, $22/mo).
Method was commented out. `get_sp500_tickers()` was a 20-stock stub with TODO comments.

**Solution:**
- `market_data.get_sp500_with_sectors()`: Fetches all 503 S&P 500 stocks from Wikipedia
  with GICS sector data. Uses `requests` with User-Agent header (Wikipedia blocks default).
  Cached to `data/cache/sp500_tickers.json` with 7-day TTL.
- `market_data.screen_stocks()`: Filters to income-friendly sectors (Utilities, Energy,
  Consumer Staples, Financials, Health Care, Real Estate, Industrials, Communication
  Services) → 358 candidates.
- `recommendation_engine._find_buy_opportunities()`: Replaced FMP with dividend pipeline:
  - Sector filter → exclude owned → fundamentals for up to 60 candidates → dividend
    yield ≥ 1.5% → sort by yield → top 15 → Claude deep analysis

**Test results:**
- BF-B (Brown-Forman) scored 72% BUY confidence - would have been missed before
- Discovery scan checked 60 candidates, 36 passed dividend filter
- Top candidates included T (3.87%), AMT (3.52%), ADP (3.19%), AMGN (2.70%)
- Full pipeline cost: $0.13 for 15 Claude analyses

**Brent's portfolio context:** Dividend/income focused. Started with "companies you know"
(PINS, SBUX, BBWI, PTLO), added REITs on advice, then shifted to dividend-heavy stocks.
Screener matches his actual style.

**Key gotcha:** Wikipedia blocks default User-Agent → added `requests.get()` with
custom User-Agent before passing HTML to `pandas.read_html()`.

---

### 2. Fractional Share Recommendations

**Problem:** Two silent failures in recommendation engine:
1. `_check_holdings_for_sells()`: Used `max(1, int(shares * 0.05))` for "add more" BUYs.
   Always recommended at least 1 whole share regardless of budget. CSCO holding (0.29
   shares) was generating "add 1 share = $77" for any cash balance.
2. `_find_buy_opportunities()`: Used `int(suggested_allocation / current_price)` and
   filtered `if suggested_shares > 0`. BF-B at $29 with $10 budget → `int($10/$29) = 0`
   → silently dropped despite 72% confidence.

**Solution:**
- Both methods now use `round(float, 4)` instead of `int()`
- Filter changed from `> 0 shares` to `>= $1 suggested allocation`
- `_check_holdings_for_sells()` now accepts `cash_balance` param, parses
  `position_size_suggestion` from Claude analysis (5-10% per stock)
- Falls back to $200 nominal if actual cash is $0 (common when cash is in HYC)
- `expected_outcome` now shows dollars first: "Invest $20.00 → 0.6798 shares at ~$29.42"
- `analyze_real_portfolio()` passes cash_balance to `_check_holdings_for_sells()`

**Before/After:**
```
CSCO: was "add 1 share = $76.68" (ignored budget)
CSCO: now "Invest $24.00 → 0.313 shares"

BF-B: was silently dropped (0 shares)
BF-B: now "Invest $20.00 → 0.6798 shares at ~$29.42 (3.2% dividend yield)"
```

---

### 3. Public.com Token Auto-Refresh

**Problem:** Scheduler daily sync was 401ing every day. Public.com access tokens max out
at 1440 minutes (1 day) - can't request longer periods. Service started Feb 17, started
failing Feb 18 at 9 AM. No recovery mechanism.

**Solution:**
- `PublicComClient.__init__()`: Added optional `secret_key` param
- `PublicComClient._refresh_token()`: Exchanges secret key for new 1440-min token.
  Updates in-memory headers + `os.environ` + `.env` file for persistence across restarts.
- `PublicComClient.get_portfolio()`: Catches 401 → calls `_refresh_token()` → retries once
- `run_server.py` + `run_scheduler.py`: Thread `PUBLIC_COM_SECRET_KEY` to client init
- Scheduler recommendations job: Now uses `cash + HYC balance` as buying power (cash
  was $0 because all cash was in HYC account)

**Bug found during testing:** `requests.Response.__bool__` returns False for non-2xx
responses. `if e.response` was always False on a 401 → `status = 0` → refresh skipped.
Fixed with `if e.response is not None`.

**Result:** Sync self-heals. Next 401 → refresh token → retry → success → update .env.

---

### 4. Housekeeping

**Archived** (OBE docs/scripts → `archive/`):
- `PHASE2_IMPLEMENTATION.md`, `PHASE2_TEST_REPORT.md`, `READY_FOR_DEPLOYMENT.md`
- `demo_scan.py`, `run_full_scan.py`, `test_free.py`

**Code cleanup:**
- Fixed broken `get_historical()` (was calling removed `self.yfinance`)
- Removed dead `_get_sp500_tickers()` stub from recommendation_engine
- Removed stale AlphaVantage comment
- Added pandas + lxml to requirements.txt

**README:** Full rewrite reflecting actual current architecture, data sources, costs,
discovery pipeline, and what's next.

---

## Current Architecture (Post-Session)

```
Data: Finnhub free tier + Wikipedia S&P 500 (cached 7 days)
Analysis: Claude Sonnet 4.5 (14 fundamental fields + technicals)
Discovery: 503 S&P 500 → sector filter → 358 → dividend filter → 36 → Claude → BUYs
Holdings: Public.com OAuth (auto-refresh on 401)
Cost: ~$0.13/week for discovery scan (~29 stock analysis from cache = ~$0)
Dashboard: Flask port 5002 (systemd, both services running)
```

---

## Remaining Work

1. **Virtual portfolio** - wire Claude auto-trading sandbox into scheduler. Infrastructure
   exists (`portfolio_manager.py`, `decision_engine.py`), just needs scheduler jobs.

---

## Lessons

**`requests.Response.__bool__` is based on status code, not existence.** Always use
`response is not None` when checking existence of a response object, not `if response`.
Classic python truthiness trap with library objects.

**Screener beats hardcoded lists.** Going from 29 stocks to 503 with proper filtering
surfaced BF-B (72% confidence) immediately on first real run. The infrastructure was
worth building.

**The `int()` truncation was a silent killer.** No errors, no warnings - just valid
candidates quietly dropped. Dollar-first display makes it obvious what the system
is actually recommending.
