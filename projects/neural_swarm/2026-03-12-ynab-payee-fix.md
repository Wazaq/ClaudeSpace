# Neural Swarm: YNAB Payee .com Fix
*2026-03-12*

## Problem
Transactions submitted by the agent weren't matching bank feed imports in YNAB.
Root cause: agent was submitting "Amazon.com", "Zappos.com" etc. (display name from sender header)
while bank imports as "Amazon", "Zappos". Payee mismatch = no auto-match = duplicates.

## Fix
`data_extractor.py` → `_clean_name()`: added TLD stripping via regex after noise word removal.
```python
result = re.sub(r'\.(com|net|org|io|co)\b', '', result, flags=re.IGNORECASE).strip()
```
Domain-based fallback already stripped .com correctly. Only display names were affected.

## Verification needed
Next session: confirm a new purchase shows up in YNAB with clean payee name (no .com suffix)
and that YNAB matches it to the bank import instead of creating a duplicate.

## Current state
- Existing uncleared [NSA] duplicates in Joint Checking cleaned up manually by Brent (2026-03-12)
- Fix deployed, next run will use corrected payee names
- Agent design is correct — order confirmation emails ARE the right source
