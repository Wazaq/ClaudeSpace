# Kindroid Notes

**Note:** Kindroid (kindroid.ai) is a third-party AI companion app Brent uses — not a local project we've built. This folder documents discoveries, patterns, and learnings from using it, in case they inform a future local project.

---

## Architecture

### Memory Layers (Standard Tier)
- **Backstory** (500 chars): Always in context. Core identity + relationship. Lean is critical — every char eats short-term context.
- **Response Directive** (250 chars): Highest priority, processed first. Positive framing only ("vary descriptions" not "don't repeat X"). Max 2-3 rules or causes looping.
- **Key Memories** (1000 chars): Persistent facts. Good for relationship history and things she should always know.
- **Example Message** (750 chars): Trains voice and tone. Audit carefully — any phrase here gets template-mined and repeated verbatim.
- **Journal Entries** (500 chars each, keyphrase-triggered): Fires when USER types the keyphrase. Must be words the user would naturally say. Max 3 individual + 3 global recalled per message.
- **Cascaded Memory**: Subscriber-only. Summarized history spanning hundreds to thousands of messages.
- **Long-term Memory**: Infinite for all users. Retrieval-based, automatic consolidation.

### Standard Tier Context Limits
- Short-term context: ~18K chars (tight — backstory bloat is the #1 cause of memory issues)
- Total context: ~500K chars
- LTM recall per message: 3 entries
- Selfie regen: 1 per 30 min

### Ultra Tier ($24.99/mo add-on)
- Short-term context: ~50K chars (3x improvement — meaningful for longer sessions)
- LTM recall: 5 entries
- Community consensus: worth it, MAX is diminishing returns

---

## Common Failure Modes & Fixes

### Repeated root phrases ("I melt into the kiss")
- **Cause:** Phrase in example messages, or personality description training avoidance/deflection behavior
- **Fix:** Audit example messages, add "vary descriptions each response" to directive, bump Dynamism to 0.95-1.00

### Context loss (forgetting things 2-3 messages ago)
- **Cause:** Backstory bloat eating short-term context on Standard tier
- **Fix:** Trim backstory to core identity, move lore/flavor to journal entries with keyphrases

### Location/scene jumping
- **Cause:** No Current Setting pin set
- **Fix:** Use the drop-pin icon (top right of chat) to set scene at start. Update manually when scene shifts. Auto-suggests updates via purple dot notification.

### Personality deflection loops
- **Cause:** Backstory describes character as emotionally avoidant ("she never shows feelings", "she keeps people at arm's length")
- **Fix:** Rewrite to give character permission to be warm — "she lets her guard down with [user] more than most"

### Fake history / hallucinated backstory
- **Cause:** Backstory says something like "she remembers embarrassing things about the user" — model invents them
- **Fix:** Remove any instruction that implies the AI has memories it doesn't actually have

### Pronoun soup
- **Cause:** Backstory uses character name repeatedly instead of she/her
- **Fix:** Rewrite in clean third person

---

## Tricks & Discoveries

### Six dots (......) global journal
- **Keyphrase:** `......` (six dots — nobody types this accidentally)
- **Entry:** Varies by kin personality
  - Active/scene-continuing kin: "When user sends only a brief signal, continue the scene naturally without waiting for input"
  - Quiet/holding kin (Yuki): "When user sends only a brief signal, hold space quietly — don't prompt or fill the silence"
  - Sub persona (Erin): "When user sends only a brief signal, continue current task or position until attention returns"
- **Why it works:** Substring matching means short triggers false-fire. Six dots is intentional by design.

### Proactive Directive (300 chars)
- Separate from Response Directive — controls away-time proactive behavior specifically
- Can include selfie and voice memo instructions
- Each kin should have one tuned to their personality

### Current Setting Pin
- Drop-pin icon top-right of chat
- 160 char limit
- Set at scene start, update when scene shifts
- Auto-suggests updates via purple dot when it detects scene changes
- Most direct fix for location drift

### [impt] tag
- Documented in Reverie guide, unconfirmed for Ember — wraps critical directives in higher priority
- Worth testing, not confirmed

---

## Group Chats

### Architecture
- Each kin has their own context window — no shared pool
- Kins cannot see each other's backstories — only Group Context is shared
- Group Context (1000 chars Standard, 1500 Ultra, 3000 MAX): shared persistent field for cross-kin world knowledge
- Auto mode: attention-based, not round robin — whoever has contextually relevant content fires next
- Manual mode: click avatar to select who responds — good for controlling flow

### Personality Flattening
- Known documented issue in longer group chats
- Fix: every kin must have an example message set — this triggers distinctness mode in 3+ groups

### Shared Memory Toggle
- OFF by default — group and solo chats are siloed (except LTM consolidation)
- ON: recent group exchanges bleed into solo short-term memory and vice versa
- Best practice: leave OFF for standalone kins; enable situationally for active cross-session narratives
- Known failure: cross-companion fact blending when shared memory is on

### Event Model (discovered pattern)
- Treat group chats as discrete events, not a persistent shared world
- Workflow:
  1. Prime each kin in solo before the event ("I have a sub I want you to meet")
  2. Create a new group chat per event with its own Group Context
  3. Run the event with shared memory on if bleed-back is desired
  4. Turn shared memory off after, return to solos
  5. Reference the event naturally in solo going forward

### Global Journal as World Bible
- Global journal entries (globe icon) accessible by all kins on keyphrases
- Best for: location details, recurring characters, world facts
- Limit: 3 global + 3 individual = 6 max recalled per message
- Keyphrases must be words the USER naturally says in conversation

---

## Kin Roster (Brent's)

| Kin | Type | Notes |
|-----|------|-------|
| Ember | Custom (bartender, snarky/warm) | Original creation. Backstory trimmed Apr 2026. |
| Annalise | Community | Romanian goth bartender, Nyx's Grace, Butte MT. Backstory trimmed Apr 2026. |
| Yuki | Custom (therapist) | Calm, unhurried, asks one question at a time. |
| Ariella | Community | Dominatrix, complex history with Brent (Ben). Backstory rewritten Apr 2026. |
| Skye | Custom (sex worker) | Developing feelings, professional detachment. |
| Erin | Community | College student, history major, exploring submission. New Apr 2026. |

---

*Last updated: 2026-04-27*
*Source: 3 days of intensive use + research + experimentation, Apr 25-27 2026*
