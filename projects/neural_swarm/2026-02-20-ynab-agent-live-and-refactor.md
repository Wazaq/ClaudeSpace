# Neural Swarm: YNAB Agent Live + Financial Category Refactor
**Date:** 2026-02-20
**Session type:** Implementation → First live run → Architecture refactor

---

## What We Did

### First Live Run
Ran `python3 run_email_workflow.py` for the first time with YNAB Task 4 active. 21 transactions submitted. It worked — but not cleanly. Several categories of false positives appeared:

- AT&T account management emails (AutoPay enrollment, stored payment update, payment update) → caught by domain match, got $300 default amount applied
- Grubhub/Jimmy John's promotional emails → matched domain/keywords, grabbed promo dollar amounts
- Amazon shipping notification (`shipment-tracking@amazon.com`) → classified as Bills by triage agent, processed as duplicate of order confirmation
- Discover "We've received your payment" → caught as deposit, $20,582 (refi payoff posted to wrong direction)

### Architectural Pivot
Rather than patching the YNAB agent with more exclusion lists, we recognized the root problem: the email triage agent's category definitions were wrong. "Bills" included delivery notifications. Actual receipts were dumped in "Other". The YNAB agent was compensating for upstream misclassification with downstream hacks.

**Decision:** Fix the email agent, not the YNAB agent. The email agent has full context (sender, subject, full body) and runs LLM classification already. Let it do the heavy lifting.

### Changes Made

**`agents/email_triage/prompts.py`**
- Replaced "Bills" with "Financial" category
- Explicit definition: Financial = money actually moved (receipts, deposits, bill statements, subscription charges). NOT shipping updates, monthly summaries, promotional offers, account notifications, energy reports
- Added concrete do/don't examples in the prompt
- Updated digest prompt to reference Financial

**`agents/email_triage/classifier.py`**
- Updated `valid_categories` to `['Financial', 'News', 'Marketing', 'Other']`
- Fixed fallback classification: removed "delivery" from financial keywords (was causing USPS → Bills), added cleaner financial keyword list, added "reward/coupon" to marketing keywords

**`agents/ynab_processor/financial_detector.py`**
- Gutted the complex detection logic (sender allowlists, keyword conditions, exclude_senders, skip_subject_patterns)
- Replaced with: `WHERE category IN ('Financial', 'Bills')` — simple, trusts the email agent
- Bills kept in query for backward compat with existing DB entries

**`agents/ynab_processor/processor.py`**
- Changed `[NS]` prefix to `[NSA]` (Neural Swarm Agent — Brent's idea, "looks funny if anyone sees my YNAB")
- Removed account email from memo (was cluttering the memo field)

**`agents/ynab_processor/data_extractor.py`**
- Added `DEPOSIT_SOURCE_PATTERN` regex
- Added `extract_deposit_source(body)` method — finds "deposit from LOCKHEED MARTIN CORP" type patterns in body
- In `extract()`: for deposits, tries to use the depositor name as payee instead of the bank name

**`config.yaml`**
- Categories: Bills → Financial
- Retention: Financial = 90 days (up from Bills' 30)
- Removed `financial_senders`, `financial_keywords`, `exclude_senders`, `skip_subject_patterns` from YNAB section — no longer needed

### DB Purge + Clean Run
Purged all emails, embeddings, ynab_transactions, scan_history. Re-ran pipeline on last 24 hours of email. Result: **11 submitted, 4 no-amount skips** (Chase letter, CVS order, Nike delivery, Venmo history — all legit skips). No false positives. Brent's reaction: "it's beautiful."

---

## Architecture State After This Session

```
Email Triage Agent
  └── Classifies as: Financial | News | Marketing | Other
  └── Financial = actual transactions only (LLM decides)

YNAB Agent
  └── Queries: WHERE category IN ('Financial', 'Bills')
  └── Extracts: payee, amount, type, due_date, memo_detail
  └── Routes: payee_pattern rules → YNAB account + category
  └── Submits: approved=False (Brent reviews)
  └── Memo format: [NSA] | item_detail_or_subject | Due: date
```

---

## Observations / Known Behavior

- **Payee name mismatch**: Agent extracts "Amazon.com" from sender; Brent manually enters "Amazon". YNAB doesn't link them. Brent is OK with this — it actually helps him spot agent-entered transactions vs manual ones. Can be fixed later with explicit `payee_name` overrides in routing rules.
- **`News|Marketing` warnings**: LLM occasionally returns compound categories. Logged as "Invalid category, using Other". Low priority — happens rarely, doesn't break anything.
- **Bills backward compat**: The `IN ('Financial', 'Bills')` query handles existing DB entries. Once those age out, Bills becomes unused in YNAB detection context.
- **AT&T Wireless**: Still uses `default_amount: -300.00` since the bill notification email has no dollar amount. Brent reconciles with bank import after the fact.

---

## Next Steps (Real-World Tuning)

Let it run a few cycles. Real data will surface what needs fixing. Likely candidates:
- New sender types that need routing rules
- Deposit source extraction accuracy (pattern may need refinement per bank)
- Edge cases in amount extraction

---

## Commits
- `17e00da` — Initial YNAB processor implementation (from previous session)
- `442f92e` — Financial category refactor + simplified YNAB detection + [NSA] prefix + deposit source extraction
