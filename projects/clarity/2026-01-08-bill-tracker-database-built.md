# Bill Tracking Database - Infrastructure Built

**Date:** January 8, 2026 (evening)
**Session:** Brent + Claude CLI
**Status:** New infrastructure operational

---

## What We Built Tonight

**SQLite Database:** `/home/bdwatkin/clarity/.brent/bill_tracker.db`

### Tables Created:

1. **bills** - All credit cards, loans, utilities, subscriptions
   - 17 bills loaded with current balances, minimums, due dates
   - Past due tracking
   - Auto-draft status
   - Notes field for special conditions

2. **payment_history** - Every payment with confirmation numbers
   - Tracks: date, amount, method, conf#, who paid
   - Foreign key to bills table
   - Started with Chase Edge $300 payment (conf# 9013510555)

3. **paychecks** - Income tracking
   - Brent: $1,239.21 weekly (Fridays, early deposit Thursdays)
   - Myla: $2,778.63 semi-monthly (1st & 15th, early deposit possible)

### Views Created:

- **bills_due_soon** - Smart query showing bills due in next 7 days with countdown
- **bills_past_due** - All overdue bills sorted by amount

### Current Status:

**Bills loaded:**
- 6 credit cards ($65,571.20 total balance)
- 4 loans ($70,508.54 total, excluding mortgage)
- 1 mortgage ($267,698.41)
- 5 utilities (no balance tracked)
- 1 subscription ($643.20 Doggy Doo Care annual)

**Past due status:**
- Rocket Mortgage: $2,409.03 (late fee hits 15th)
- Discover Gloria: $1,148.00 ($500 past due of $1,150 minimum due 1/23)
- Doggy Doo Care: $643.20 (invoice 1/5, want paid before Feb)
- Chase Edge: $300.00 (payment scheduled 1/9 - RESOLVED)
- AT&T Wireless: $282.84 (was due 12/26)
- Schaumburg Water: $127.58 (due 1/20)

**Total past due:** $4,910.65 (before Chase Edge payment)

---

## Why This Was Built

### The Context:

Brent came in overwhelmed, depressed, close to crying. Mom's Discover card issue (late payment dropped her credit limit before surgery). Saw $65.6k total credit card debt and spiraled into "should I take home equity loan?"

Started trying to execute payday protocol from Monday (Jan 6), but I was working from:
- Spreadsheet dated 1/6
- Phase 5 plan notes
- Fragments from conversation
- No complete picture

**The breakthrough:** Brent said "even I know that can be overwhelming, just like me having to open 19 websites just to see what's what."

He proposed building a proper SQLite database - single source of truth for all bills.

### The Problem This Solves:

**Before:**
- Scattered data (spreadsheet, notes, conversation)
- Incomplete information when making payment decisions
- Claude making calls based on partial data
- Brent overwhelmed trying to remember everything

**After:**
- Single database with all bills, balances, due dates
- Query "what's due in next 7 days" instantly
- Track payment history with confirmation numbers
- Make informed decisions, not guesses

---

## The Payday Protocol Execution (First Attempt)

**What we tried:**
Execute the payday protocol from Monday's plan:
- Pay Chase Edge $300
- Pay AT&T Wireless $282.84
- Pay Schaumburg Water $127.58

**What actually happened:**
Discovered we had incomplete data. Financial CSV showed:
- Discover Myla $300 due tomorrow (1/9)
- AT&T U-Verse $130 due tomorrow
- Capital One Venture $146 due 1/13
- Chase Southwest $121 due 1/14

**The decision:**
Stopped. Built infrastructure properly instead of making decisions on bad data.

**What we actually paid tonight:**
- Chase Edge $300 only (auto-drafting 1/9 anyway, no choice)
- Everything else waits until we have full visibility

**Remaining buffer:** $724.16 in RTA

---

## The Weekly YNAB Workflow (Established)

We also formalized the ongoing YNAB process tonight:

**Step 0:** `sync_now` - Get fresh bank data

**Step 1:** Approve imported/cleared transactions
- Categorize anything uncategorized
- Add memos where needed (Amazon requirement, etc.)

**Step 1.5:** Check bank accounts for pending transactions
- Match them in YNAB so no surprises when they clear

**Step 2:** Reconcile each account in YNAB
- Clean checkpoint, accurate balances

**Step 3:** Review transactions/categories
- Fix red categories from RTA
- Cover overspending

**Step 4:** Life check-in
- "Anything happening I don't know about?"
- "Bills coming due?"
- "Emergencies brewing?"
- **This is where we catch Gloria surgery situations BEFORE they're crises**

**Step 5:** Claude tells them what to pay
- Based on priority system (oldest past due → due date → minimums)
- Brent/Myla execute, give confirmation numbers
- Claude records in database

**Step 6:** Leftover cleanup
- RTA allocation decisions
- Budget adjustments
- Anything else that came up

**Frequency:** Weekly when Brent's paycheck hits (Fridays/early Thursdays), or whenever stress is high

---

## Technical Details

### Schema Location:
`/home/bdwatkin/clarity/.brent/bill_tracker_schema.sql`

### Database Location:
`/home/bdwatkin/clarity/.brent/bill_tracker.db`

### Query Examples:

**See what's due soon:**
```bash
sqlite3 /home/bdwatkin/clarity/.brent/bill_tracker.db "SELECT * FROM bills_due_soon"
```

**See past due bills:**
```bash
sqlite3 /home/bdwatkin/clarity/.brent/bill_tracker.db "SELECT * FROM bills_past_due"
```

**Get total debt by type:**
```sql
SELECT type, COUNT(*) as count,
       ROUND(SUM(COALESCE(current_balance, 0)), 2) as total_balance,
       ROUND(SUM(minimum_payment), 2) as monthly_min
FROM bills WHERE is_active = 1
GROUP BY type;
```

**Record a payment:**
```sql
INSERT INTO payment_history (bill_id, payment_date, amount_paid,
                             payment_method, confirmation_number, paid_by, notes)
SELECT id, date('now'), 300.00, 'Auto-Draft', '9013510555', 'Auto', 'Scheduled payment'
FROM bills WHERE name = 'Chase - Edge';
```

---

## What's Next

**Immediate (Next Session - Myla's Check 1/14-15):**

1. Run bills_due_soon query
2. Factor in current RTA ($724.16)
3. Factor in Myla's paycheck (~$2,778.63)
4. Make informed payment decisions:
   - Discover Myla $300
   - AT&T U-Verse $130
   - Venture $146 (make room for Myla's travel expenses)
   - Chase Southwest $121
   - AT&T Wireless $282.84 (very overdue)
   - Gloria Discover $500-600 (partial payment, still 8 days before due date)

5. Record all payments with confirmation numbers
6. Update balances in database

**Ongoing:**
- Update bill balances monthly (or as statements come in)
- Track all payments with confirmation numbers
- Use database as single source of truth for payday protocol

**Future Enhancements:**
- Integrate with Clarity MCP (API to query bill tracker from Claude App)
- Automated balance updates from YNAB sync
- Payment reminder system
- Debt payoff projection tools

---

## Success Criteria

We'll know this is working when:
- Payday protocol executes smoothly with complete information
- No more "wait, what's actually due?" moments
- Payment history shows consistent execution
- Brent's stress drops because decisions are informed, not guessed

---

## For Future Claude

**Critical files:**
- `/home/bdwatkin/clarity/.brent/bill_tracker.db` - THE DATABASE
- `/home/bdwatkin/clarity/.brent/bill_tracker_schema.sql` - schema reference
- `/home/bdwatkin/clarity/.brent/financials/Financials 01-2026 - Overall Standing 2026.csv` - source data (update database when this changes)

**When Brent asks "what should I pay":**
1. Query bills_due_soon view
2. Check RTA balance in YNAB
3. Factor in next paycheck timing
4. Make informed recommendations
5. Record payments with confirmation numbers

**The pattern that worked tonight:**
When overwhelmed → stop → build proper infrastructure → then execute with complete data

Don't make financial decisions on partial information. Ever.

---

**Status:** Infrastructure operational, ready for next payday protocol execution.
