# Neural Swarm — Project Reference

*Last updated: 2026-03-31*

---

## What It Is

Multi-agent AI swarm. Primary active use: **YNAB email processing agent** — monitors email, categorizes transactions, updates YNAB budget. Morning digest feature disabled 2026-03-27.

---

## Key Paths

| What | Path |
|------|------|
| Root | `/home/bdwatkin/neural-swarm/` |
| Main bot | `run_bot.py` |
| Config | `config.yaml` |
| Agents | `agents/` |
| Interfaces | `interfaces/` |
| Venv | `venv/` |

---

## Services

| Service | Description |
|---------|-------------|
| `neural-swarm-bot.service` | Main bot |
| `neural-swarm-scheduler.service` | Scheduled tasks |

---

## Current Config

- **YNAB agent:** Active, processing emails, working well
- **Morning digest:** Disabled (task commented out in `bot.py`, 2026-03-27)

---

## Known Issues / TODO

- [ ] YNAB: exclude public dividends from processing
- [ ] YNAB: correct account assignment (transactions going to wrong account)
- [ ] YNAB: stop double tracking (order placed/shipped/arrived = 3 transactions, should be 1)
- [ ] YNAB: Target cleanup (order placed → drive up ready → cancelled = chaos)
- [ ] NSA: add Etsy email handling
- [ ] NSA: Nicor Gas → route to Capital One Venture One (not current account)
- [ ] NSA: Torrid double tracking (same as Target issue)
- [ ] NSA: Warby Parker → skip/ignore (paid via HSA)
- [ ] NSA: Apple → route to Capital One Venture One
- [ ] Jewel-Osco $0.89 transaction investigation (wrong amount? fee? fuel points?)
