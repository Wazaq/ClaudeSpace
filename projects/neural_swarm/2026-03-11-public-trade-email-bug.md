# Neural Swarm: Public Trade Email Bug
*2026-03-11 — noted for next session*

## Problem
YNAB agent is recording Public (stock app) trade confirmation emails as bank transactions. Three issues:

1. **Wrong amounts** — agent misreads trade value from email content
2. **Wrong transaction type** — in-app trades use buying power, not real bank money. Shouldn't be recorded in YNAB at all.
3. **Can't just block all Public emails** — real bank deposits to Public portfolio SHOULD be recorded

## What we know
- Transactions show up under "Purchases" label in YNAB
- Memo starts with `[NSA]` confirming it's agent-added, not bank feed
- 8 transactions added on 2026-03-10, all "Your trade executed" memo
- Only 1 Public email came through the agent (the others may be bank feed duplicates — unclear)

## Desired behavior
- **Skip:** "Your trade executed" emails from Public (in-app trades, no bank money moved)
- **Record:** Deposit confirmation emails from Public (real bank → portfolio transfers)

## Fix approach
Look at the actual Public email formats to understand subject/content differences between trade confirmations and deposit confirmations. Then either:
- Add to `skip_subject_patterns` if subject line is distinct enough
- Or add content-based filtering in the triage prompt for Public specifically

## Fix Applied (2026-03-11)
- Confirmed no deposit confirmation emails from Public — deposits are in-app only
- Known Public email types: "Your trade executed", "Earned interest", "Monthly statement"
- Added all three to `skip_subject_patterns` in `config.yaml`
- Added `public\.com` to `skip_payee_patterns` as belt-and-suspenders
- 8 bad transactions from 2026-03-10 cleaned up manually in YNAB
