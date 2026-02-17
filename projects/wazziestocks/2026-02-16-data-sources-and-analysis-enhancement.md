# WazzieStocks Session: Data Sources + Analysis Enhancement
**Date:** 2026-02-16
**Duration:** ~2.5 hours

---

## What We Accomplished

### 1. Stripped Unreliable Data Sources
- **Removed AlphaVantage** - 2.6 Trustpilot, cancellation hell, data accuracy issues
- **Removed FMP** - No refunds policy, 403 on free tier for fundamentals
- **Removed YFinance** - IP ban risks, wrong historical prices (showing $600 AAPL)
- **Kept: Finnhub free tier** - 60 calls/min, reliable, includes fundamentals

### 2. Finnhub Free Tier Capabilities
What the free tier actually includes:
- Quotes (real-time)
- Basic fundamentals (`/stock/metric?metric=all`)
- Company news (3 years)
- **NOT included:** News sentiment (premium, $50/month via Fundamental-1 tier)

Key fields from `/stock/metric`:
- `pe_ratio`, `price_to_book`, `price_to_sales`
- `market_cap`, `roe`, `roa`, `profit_margin`, `operating_margin`
- `debt_to_equity`, `current_ratio`, `quick_ratio`
- `eps`, `beta`, `dividend_yield`
- `52_week_high`, `52_week_low`

**Percentage formatting gotcha:** Finnhub returns percentages already ×100
- ROE = 159.94 means 159.94% (not 0.15994)
- Use `:.2f%` not `:.2%` to avoid showing 15994%

### 3. Enhanced Claude Analysis Prompt
**Before:** 5 fields (P/E, profit margin, debt/equity, + 2 we didn't have)
**After:** 14 fields (all available Finnhub fundamentals + technicals)

**A/B Test Results:**
- Old avg confidence: 44.9%
- New avg confidence: 62.7% (+17.8%)
- Recommendations changed: 12/29 (all HOLD → BUY)
- Changed stocks: APLE, BMY, CSCO, DUK, GILD, MDT, MRK, PEP, SO, VZ, WFC, XOM
- Reasoning detail: +208 chars average (more context, better analysis)

### 4. Added Plain English Summaries
Brent is new to investing - jargon-heavy reasoning wasn't useful.
Added `plain_english` field to Claude's JSON output:
- 2-3 sentences, no jargon, explains what matters
- Shown prominently on dashboard (green highlight)
- Technical details collapsed under "Full Analysis" toggle
- DB column added with migration for existing installs

### 5. Fixed Sentiment 403 Errors
- News sentiment = premium feature on Finnhub
- Commented out calls to avoid spamming their API
- Finnhub Fundamental-1 plan ($50/month) includes it if needed later
- Also includes: SEC Filings Sentiment, Social Sentiment (Reddit/Twitter)

---

## Current Architecture

```
Data: Finnhub free tier (quotes + fundamentals + news)
Analysis: Claude Sonnet 3.5 (14 fundamental fields + technicals)
Recommendations: BUY/SELL/HOLD with plain English + technical details
Storage: SQLite (wazziestocks.db)
Dashboard: Flask on port 5002 (systemd auto-start)
Cost: ~$0.20/week for 29 stocks = ~$0.86/month
```

---

## Next Session Priorities (from Brent)

1. **Market sweep for new stocks** - currently disabled, needs stock screener
   - Current code has `_find_buy_opportunities()` method ready but screener disabled
   - Need alternative to FMP screener (was $22/month)
   - Options: Finnhub screener? Manual list expansion? Wikipedia S&P500?

2. **Budget-aware BUY recommendations** - partial shares, proportional allocation
   - Currently recommends "add 1 share" for all BUYs
   - Need: sync buying power from Public.com, split across BUY candidates
   - Public.com supports fractional shares
   - Example: "$200 buying power, 5 BUY recs → allocate proportionally"

3. **Claude virtual portfolio** - sandbox automation
   - Virtual portfolio continues Phase 1 behavior
   - Need to wire up scheduler for virtual auto-trading

4. **Scheduler automation** - tie everything together
   - Daily sync (9 AM)
   - Weekly recommendations (Sunday)
   - Cost tracking + alerts

---

## Files Changed This Session
- `app/utils/api_clients.py` - prompt enhancement (14 fields), sentiment disabled
- `app/services/recommendation_engine.py` - plain_english threading, sentiment disabled
- `core/database.py` - plain_english column + migration
- `templates/recommendations.html` - plain English UI, collapsible technical details
- `test_prompt_comparison.py` - NEW: A/B test script for prompt changes

---

## Lessons Learned

**Data source research matters more than speed** - We almost paid for FMP/AV before
discovering Finnhub free tier covered everything we needed.

**Slowing down pays off** - Brent wanted to explore Finnhub pricing together rather
than rush to "rip it out." Led to better understanding of what $50/month gets you
and when it might be worth it.

**Give Claude the data it needs** - Old prompt had 5 fields, Claude was effectively
guessing. 14 fields → dramatically better analysis. Quality in = quality out.

**Plain English matters for the actual user** - Technical reasoning is correct but
useless if the human can't understand it. Always think about who reads the output.
