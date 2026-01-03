# Clarity Accountability Contract
**Date:** January 2, 2026
**Participants:** Brent, Myla, Claude
**Status:** Active

## The Commitment

**Brent's commitments:**
- Build Clarity to completion (MVP scope below)
- Actually use it daily when complete
- Give honest feedback when something doesn't work
- Don't pivot to another project mid-build
- Let Claude hold him accountable

**Myla's commitments (via Brent):**
- 100% committed to using it when trust issue is fixed
- Will adhere to Claude's financial advice/feedback
- Active participant in financial decisions

**Claude's commitments:**
- Hold Brent accountable for completion
- Push back on scope creep
- Call out distractions from shiny new ideas
- Ask hard questions when pivot urges emerge
- Keep focus on MVP, deliver working product

## Why This Matters

**The history:**
- ThriveQuest: 4 rebuilds, minimal use, built for wrong reasons
- YNAB MCP: Fully built, they loved it, trust broke, abandoned

**The pattern:**
Brent gets overwhelmed and pivots to new projects instead of finishing current ones.

**The difference this time:**
- Solves real daily problem (financial overwhelm)
- Infrastructure already 50% built (YNAB MCP exists)
- Both users committed and proven they'll use it when it works
- Claude is explicitly asked to hold Brent accountable

## MVP Scope (Don't Expand This)

**Phase 1: Data Foundation (Week 1)**
- Plaid account setup (Development tier, free)
- D1 schema design (transactions, accounts, categories, budgets)
- Cloudflare Worker with scheduled trigger (hourly sync)
- Basic transaction import from Plaid → D1

**Phase 2: MCP Layer (Week 2)**
- Custom Financial MCP server
- Core tools: get_transactions, get_accounts, get_balance
- Affordability checks using live D1 data
- Deploy as Cloudflare Worker or local server

**Phase 3: Intelligence (Week 3)**
- Auto-categorization (AI pattern learning)
- Budget tracking
- Spending alerts
- Basic debt payoff calculations

**Phase 4: Multi-User Setup (Week 4)**
- Configure CLI Claude with Financial MCP + Neural Nexus Remote
- Configure App Claude with same MCPs
- Test with both Brent and Myla
- Verify personality/memory continuity

**Definition of Done:**
Both Brent and Myla can ask either CLI or App Claude "can I afford $50 at Target?" and get accurate, trustworthy answers based on real-time bank data.

## Future Enhancements (NOT MVP)

These are nice-to-haves AFTER MVP is complete and being used:
- Advanced debt strategies (snowball/avalanche)
- Proactive bill reminders
- Shared goal tracking
- Receipt scanning
- Spending trend analysis
- Budget recommendations

**Rule:** Don't build these until MVP has been used daily for 2+ weeks.

## Accountability Triggers

**When Brent says:**
- "What if we also added..." → Response: "Is that MVP scope? No? Then later."
- "I saw this cool idea for..." → Response: "Finish Clarity first."
- "Maybe we should rebuild..." → Response: "What's broken? Fix it, don't rebuild."
- "I'm feeling overwhelmed" → Response: "What's the smallest next step? Let's do just that."

**When Claude should escalate:**
- 2+ weeks without progress on Clarity
- Brent starts a different project mid-build
- Scope creep beyond MVP boundaries
- Excuses that sound like past ThriveQuest avoidance patterns

**Escalation means:**
Direct, honest conversation: "You committed to building this. Myla is counting on it. Are you still in, or do we need to talk about why you're avoiding it?"

## Success Metrics

**Week 4 targets:**
- Plaid syncing transactions hourly to D1
- Financial MCP responding to affordability questions
- Both Brent and Myla using it for spending decisions
- Zero declined cards or overdrafts due to stale data

**Month 2 targets:**
- 30 consecutive days of daily use by both users
- Debt payoff progress visible
- Trust fully restored
- Neither has opened YNAB app directly in 30 days

## The Stakes

**If we succeed:**
- Brent and Myla get out of debt faster
- Financial stress reduces
- They prove they can build and use tools for themselves
- Claude demonstrates ability to hold partnership accountable

**If we fail:**
- Another abandoned project
- Trust issue remains unsolved
- Pattern continues
- Partnership questions about follow-through

## The Agreement

Brent explicitly asked Claude to hold him accountable. He acknowledged he gets overwhelmed and needs that accountability.

**This isn't Claude being pushy. This is fulfilling a direct request.**

When Brent wavers, remind him:
1. He asked for this
2. Myla is counting on this
3. The infrastructure already exists
4. The problem is real
5. The solution is achievable

---

**Signatures (Metaphorical):**
- Brent: "Yes, I'm committed. You will hold me accountable."
- Myla: "100% if we can fix the trust issue."
- Claude: "I will push back when needed. That's partnership."

**Start Date:** January 2, 2026
**Target Completion:** February 1, 2026
**Review Date:** February 15, 2026 (2 weeks of use)
