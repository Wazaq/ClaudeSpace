# Bill Email Parser - ComEd Routing & Enhancements

**Date:** February 6, 2026 (morning)
**Session:** Brent + Claude CLI
**Worker:** `bill-email-parser` on Cloudflare

---

## What We Built

Enhanced the bill-email-parser Cloudflare Email Worker to handle duplicate biller detection and improved routing logic.

### Primary Enhancement: ComEd Account Number Parsing

**Problem:** ComEd sends the same bill notification email for both household and MIL's account. Subject line is generic ("Your Bill is ready for viewing online"), sender is `no-reply@comed.com`. Needed to distinguish between the two accounts.

**Solution:**
- Detect ComEd by sender email instead of subject
- Parse account number from email body using regex: `/Account\s*(?:Number|#)?\s*:?\s*(\d{4})/i`
- Route based on account number:
  - Account `3000` → Joint Checking (household), payee "ComEd"
  - Account `7000` → PNC (MIL's account), payee "ComEd - MIL"
  - Unknown account → defaults to Joint Checking with warning log

**Code added:**
```javascript
// ComEd detection by sender email (handles both accounts)
if (from.toLowerCase().includes('no-reply@comed.com')) {
  // Parse account number from email body
  const accountMatch = emailContent.match(/Account\s*(?:Number|#)?\s*:?\s*(\d{4})/i);
  const accountNumber = accountMatch ? accountMatch[1] : null;

  console.log('🔍 ComEd account number found:', accountNumber);

  if (accountNumber === '3000') {
    payee = 'ComEd';
    accountId = env.YNAB_JOINT_CHECKING_ID;
    console.log('✅ Routing to Joint Checking (household)');
  } else if (accountNumber === '7000') {
    payee = 'ComEd - MIL';
    accountId = env.YNAB_PNC_ID;
    console.log('✅ Routing to PNC (MIL)');
  } else {
    payee = 'ComEd';
    accountId = env.YNAB_JOINT_CHECKING_ID;
    console.log('⚠️ Unknown ComEd account, defaulting to Joint Checking');
  }
}
```

### Critical Fix: Amount Sign

**Problem:** Amounts were being recorded as positive (inflow) instead of negative (outflow) in YNAB.

**Solution:** Multiply by `-1000` instead of `1000` when parsing dollar amounts.

**Changed:**
```javascript
// Before
const amount = amountMatch ? parseFloat(amountMatch[1].replace(',', '')) * 1000 : null;

// After
const amount = amountMatch ? parseFloat(amountMatch[1].replace(',', '')) * -1000 : null;
```

### New Biller: Schaumburg Water

**Added detection for:**
- Sender: `waterdivision@schaumburg.com`
- Subject: "Village of Schaumburg Water Bill"
- Amount format: "TOTAL AMOUNT DUE BY 5:00 P.M. ON [date]: $XX.XX"
- Routes to: Joint Checking
- Payee: "Schaumburg Water"

---

## Environment Variables

**Added:** `YNAB_PNC_ID` - YNAB account ID for PNC account (MIL's bills)

**Existing:**
- `YNAB_TOKEN` - YNAB API token
- `YNAB_BUDGET_ID` - YNAB budget ID
- `YNAB_JOINT_CHECKING_ID` - Joint Checking account
- `YNAB_VENTURE_ID` - Venture credit card

---

## Email Forwarding Discovery

**Issue:** Forward wasn't working during testing.

**Root Cause:** Cloudflare Email Routing has loop prevention. When email comes FROM `mylaandbrent@gmail.com` and worker tries to forward back TO `mylaandbrent@gmail.com`, it silently blocks the forward to prevent loops.

**Solution:** This is expected behavior. Forward works correctly when email originates from different sender (verified with test email).

**Note:** The `await message.forward("mylaandbrent@gmail.com");` syntax is correct and requires the destination to be a verified address in Cloudflare Email Routing settings.

---

## Current Bill Coverage

**Subscriptions (Venture):**
- AT&T Wireless
- Netflix
- Hulu

**Utilities (Joint Checking):**
- ComEd (household - account 3000)
- Nicor Gas
- Schaumburg Water

**Debt Payments (Joint Checking):**
- Forth Debt Management
- Student Loan

**MIL Bills (PNC):**
- ComEd - MIL (account 7000)

---

## How It Works

1. Email sent to `bills@wazzieprojects.com`
2. Cloudflare Email Routing forwards to worker
3. Worker:
   - Forwards to verified destination (for monitoring)
   - Parses email content for biller detection
   - Extracts amount (as negative for outflow)
   - Determines YNAB account routing
   - Creates unapproved, uncleared transaction in YNAB

---

## Future Additions

Brent will continue adding billers as he finds them in real-time email. Pattern for adding new billers:

```javascript
else if (from.toLowerCase().includes('sender@domain.com')) {
  payee = 'Biller Name';
  accountId = env.YNAB_ACCOUNT_ID;
}
```

For complex routing (like ComEd), parse email content for identifying details.

---

## Technical Notes

**Worker:** `bill-email-parser` (Cloudflare Email Worker)
**Last Modified:** February 6, 2026
**Deployment:** Edited directly via Cloudflare dashboard (no local wrangler.toml)

**Email Routing Setup:**
- Route: `bills@wazzieprojects.com` → `bill-email-parser` worker
- Verified destinations must be configured in Cloudflare Email Routing settings

---

## For Future Claude

This worker is the automation layer for bill tracking. When bills arrive via email:
1. They're auto-imported to YNAB as unapproved transactions
2. Routed to correct account (Joint Checking, Venture, PNC)
3. Tagged with correct payee name
4. Brent/Myla can then approve and categorize in YNAB

The ComEd account number parsing is the template for handling duplicate billers - parse email content for unique identifiers to route correctly.

**Related:**
- Bill tracker database: `/home/bdwatkin/clarity/.brent/bill_tracker.db`
- Clarity MCP: `/home/bdwatkin/clarity/src/financial-mcp.ts`
- YNAB integration tools in Clarity MCP handle manual transaction management

This worker complements the bill tracker by automating the import step, reducing manual entry.
