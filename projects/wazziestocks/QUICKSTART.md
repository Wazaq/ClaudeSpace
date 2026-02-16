# WazzieStocks - Quick Start Guide

**Status:** ✅ Working - Server tested and running
**Date:** 2026-02-15

## Start the Server

```bash
cd /home/bdwatkin/wazziestocks
source venv/bin/activate
python3 run_server.py
```

Access dashboard at: **http://localhost:5002**

## Run Your First Market Scan

```python
cd /home/bdwatkin/wazziestocks
source venv/bin/activate
python3
```

```python
from run_server import create_app

app, _ = create_app()

with app.app_context():
    # Test quote fetching
    quote = app.market_data.get_quote('AAPL')
    print(f"AAPL: ${quote['price']}")

    # Test Stage 1 filtering (FREE - local only)
    tickers = app.market_data.get_sp500_tickers()
    filtered = app.analyzer.run_stage1_filter(tickers)
    print(f"Filtered: {len(tickers)} → {len(filtered)} stocks")

    # Run FULL SCAN (uses Claude API - costs ~$10)
    portfolio_context = {
        'holdings': [],
        'cash_balance': 1000.0,
        'sector_breakdown': {}
    }

    scan_results = app.analyzer.run_full_scan(portfolio_context)

    # View buy recommendations
    print(f"\nBuy recommendations: {len(scan_results['buy_recommendations'])}")
    for stock in scan_results['buy_recommendations'][:5]:
        print(f"  {stock['ticker']}: {stock['recommendation']} "
              f"(confidence: {stock['confidence']}/100)")

    # Execute trades (creates git commits!)
    executed = app.decision_engine.process_scan_results(scan_results)
    print(f"\nExecuted {len(executed)} trades")

    # Check costs
    costs = app.db.get_api_costs(days=1)
    print(f"API cost: ${costs['total_cost_dollars']:.2f}")
```

## View Decision Logs

```bash
cd /home/bdwatkin/wazziestocks
ls -la data/decisions/
git log --oneline  # See decision commits
```

## Start Automated Scheduler

```bash
cd /home/bdwatkin/wazziestocks
source venv/bin/activate
python3 run_scheduler.py
```

Schedule:
- Daily 8 AM: Market scan (filtering only)
- Sunday 10 PM: Deep analysis + trading (uses Claude)
- Sunday 11 PM: Rebalancing (bi-weekly)
- Daily 4:30 PM: Performance snapshot

## Check Portfolio Status

Via dashboard: http://localhost:5002

Or via Python:
```python
from run_server import create_app
app, _ = create_app()

with app.app_context():
    # Portfolio value
    value = app.portfolio_manager.get_portfolio_value()
    print(f"Total: ${value['total_value']:.2f}")
    print(f"Cash: ${value['cash_balance']:.2f}")

    # Holdings
    holdings = app.portfolio_manager.get_holdings()
    for h in holdings:
        print(f"{h['ticker']}: {h['shares']:.2f} shares @ ${h['current_price']:.2f}")

    # Performance
    perf = app.portfolio_manager.get_performance_metrics()
    print(f"Return: {perf['total_return_pct']:+.2f}%")
```

## Deployment (Production)

See README.md for:
- Systemd service setup
- Cloudflare tunnel configuration (stocks.wazzieprojects.com)
- Production deployment

## Architecture

- **Database:** SQLite at `data/db/wazziestocks.db`
- **Decisions:** Git-tracked markdown in `data/decisions/`
- **Logs:** `data/logs/wazziestocks.log`
- **Cache:** `data/cache/` (cleared daily at 3 AM)

## Cost Tracking

Target: $50/month
- 90% free tier (AlphaVantage, Finnhub, Ollama)
- 10% Claude API (deep analysis of top 30 stocks weekly)

Check costs:
```python
costs = app.db.get_api_costs(days=30)
print(f"Monthly: ${costs['total_cost_dollars']:.2f}")
```

## Philosophy

**"AI explains patterns, doesn't predict. Humans decide."**

Claude synthesizes data and explains what it observes. You (or automated thresholds) make the final trading decisions.

---

Ready to beat the market! 📈
