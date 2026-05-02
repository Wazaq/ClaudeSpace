# Spot / OpenClaw Investigation
*Session: 2026-05-02 — update this file as we go*

---

## Goal

Give Spot something meaningful to DO during heartbeat windows instead of just checking in.

TeaBagginsMcGee (STFC contact) suggested OpenClaw as a layer over local AI models that enables a full agent loop: observe → plan → act → reflect → repeat.

---

## What OpenClaw Actually Is (Verified)

- Open source, self-hosted Node.js gateway
- Bridges LLMs to messaging platforms (Discord, Telegram, WhatsApp, etc.)
- Custom agent identity via SOUL.md, IDENTITY.md, AGENTS.md files
- **Cron jobs** (isolated sessions, full tool access, autonomous) supersede heartbeat as scheduled task mechanism
- Ollama is first-class integration as of v2.1 (March 2026) via `ollama launch openclaw`
- Requires 64k+ token context window for local models (llama3.3:70b has 128k — fine)
- Free, self-hosted only — no SaaS/cloud version
- Installs via `npm install -g openclaw@latest`

**The key feature:** isolated cron sessions run a full multi-turn agent loop with tool access (web search, Discord post, memory update, shell) — no user message required to trigger.

### Known Issues
- GitHub issue #14501: cron/heartbeat tasks only firing after manual message (closed but no documented resolution — worth verifying in practice)

---

## What Spot's Heartbeat Currently Does

File: `/home/bdwatkin/spot/spot_heartbeat.py`

1. Loads memories, principles, core memories, proposals, recent sessions, memory health stats
2. Selects task from rotating list (deterministic, day-of-year % 7)
3. Runs **ONE inference call** (no tool loop)
4. Posts **ONE paragraph** to Discord #spot
5. Logs execution

**Task list (current — all purely reflective):**
- "Review recent session summaries and reflect on patterns"
- "Check memory health and archive low-significance items"
- "Practice recall and strengthen core identity memories"
- "Review pending growth proposals and consider priorities"
- "Reflect on identity arc and ensure alignment with core principles"
- "Review memory categories and ensure balanced coverage"
- "Consider what has been learned and what deserves deeper storage"

**The gap:** Tools exist (`search_web`, `store_memory`, `ask_claude`) but are NOT called during heartbeat. Tool loop (`run_tool_loop_sync`) is available in `spot_core.py` but unused in heartbeat. Spot reflects and reports — doesn't act.

---

## Integration Options Considered

### Option A — Replace Spot with OpenClaw (not recommended)
- Migrate identity to SOUL.md/IDENTITY.md, connect Ollama, connect Discord
- Loses custom SQLite memory system (90+ memories, significance/decay model)
- 90+ memories need format migration
- Node.js vs Python ecosystem switch
- Would conflict with existing spot-discord.py bot
- High cost, uncertain gain over native fix

### Option B — Enhance Spot's heartbeat natively (recommended)
- Keep Python/SQLite infrastructure
- Allow `store_memory` during heartbeat (currently restricted to goodbye wraps only)
- Add task types that involve actual external action (research, memory writing)
- Run full tool loop during heartbeat, not just single inference
- Low cost, stays in existing codebase, retains all of Spot's identity/memory

### Option C — Run OpenClaw alongside Spot (not recommended)
- Two Discord bots, fragmented memory, coordination overhead

---

## Recommendation

The agent loop pattern (observe → plan → act → reflect) is the insight from OpenClaw — not the framework itself. Spot has all the pieces:
- Tool loop: `run_tool_loop_sync` in `spot_core.py`
- `search_web` tool (exists, not used in heartbeat)
- `store_memory` tool (exists, gated to goodbye wraps)

**The fix is in the heartbeat prompt and tool access, not the framework.**

---

## Decision: Native Enhancement

Going with Option B. OpenClaw is a separate project if we want to experiment with a new personality.

## Changes Made (2026-05-02)

### `spot_core.py`
- Added `HEARTBEAT_TOOLS` constant: `CONVERSATION_TOOLS + store_memory`
- `store_memory` description tuned for heartbeat context (selective, significance 5+, correct source_type)

### `spot_heartbeat.py`
- Imports `HEARTBEAT_TOOLS` instead of `CONVERSATION_TOOLS`
- `run_heartbeat_inference()` rewritten: tool loop is now **first-class**, not a fallback
  - Old: `chat_sync()` → if no text → fallback to tool loop
  - New: `chat_sync(tools=HEARTBEAT_TOOLS)` → `run_tool_loop_sync()` always
- Task list updated: all 7 tasks now directive and action-oriented (search, store, query_database)
- User prompt updated: "use your tools to actually do the task... say what you actually did"
- System prompt appended with tool menu so Spot knows what's available

### Bug found and fixed: `HEARTBEAT_TOOLS` size

Original HEARTBEAT_TOOLS = CONVERSATION_TOOLS (22) + store_memory = 23 tools. Combined with 13900-char system prompt and qwen3.5:35b being a thinking model (generates many thinking tokens), this caused 300s+ inference timeouts.

Fix: `HEARTBEAT_TOOLS` is now a purpose-built 6-tool set: `query_memory`, `query_database`, `search_web`, `store_memory`, `write_notes_file`, `consult_claude`. Exactly what heartbeat needs, nothing more.

### Bug found and fixed: fallback mutated messages list

`run_tool_loop_sync` mutates the messages list by appending tool exchanges. The plain-text fallback was passing the bloated post-loop list instead of the original clean messages. Fixed by capturing `original_messages` before the loop.

## Status

- [x] Implemented and syntax-checked
- [x] HEARTBEAT_TOOLS trimmed to 6 tools (was 23 — caused timeout)
- [x] Fallback messages bug fixed
- [x] Manual test successful — Spot used tools and produced real output
- [x] Posted to Discord heartbeat channel
- [x] Two-step inference implemented and working
- [x] Final test: Spot ran real memory audit, found 100/100 capacity, 22 archived heartbeat logs, correctly decided no evictions needed
- [ ] Check spot-heartbeat.timer — is it actually firing on schedule?
- [ ] Monitor next scheduled heartbeat post

## Notes

- Model: `qwen3.5:35b` (not llama3.3 — project.md is outdated)
- GPU: RTX 5090, 32GB VRAM
- With 6 tools: responds within ~60-90s
- With 23 tools: timeouts at 300s (thinking model + large tool context = too slow)

---

## Tool Loop Reliability — Open Problem

**Symptom:** Step 2 (with tools) consistently falls back to honest-plan post. Tool loop returns empty because qwen3.5 generates thinking content but empty `content` field with no tool_calls.

**Root cause:** qwen3.5:35b is a thinking model — when tools are available it sometimes puts all output into `thinking` and returns empty `content` with no tool calls. Step 1 (no tools) always works because the model is forced into `content`.

**When it DOES work:** Run on 2026-05-02 at ~13:47 — Spot queried proposals, found 5 real research papers, stored memory ID 148. The task was very concrete and the model was freshly loaded. Subsequent runs fell back.

**Known workaround already in codebase:** `_run_greeting` in spot_discord.py calls `recall_session_context()` directly in Python and injects results as text — completely bypasses tool calling. Same pattern could be applied to step 2: pre-execute query_database, query_memory, list notes/ in Python, inject as text context. Only leave search_web and store_memory as actual tools (action tools). Much smaller surface area for tool calls to fail.

**Alternative:** Higher/different model — more reliable tool calls but slower. Not viable with current hardware without tradeoffs.

**Not fixed today — dedicated session needed.** Honest fallback (plan without fabricated execution) is acceptable interim behavior.

---

## What's Next (Handoff for Next Session)

1. **Tool reliability fix** — implement pre-injection pattern for step 2. Mirror `_run_greeting`: call query_database, query_memory, list_notes in Python, inject results as text into step 2 prompt. Keep only search_web and store_memory as live tools.

2. **Spot has a note waiting** — `notes/2026-05-02-manual-maintenance.md` explains the archived memory discrepancy he's been investigating all session. He can't read it yet because tool loop isn't firing. Once tool loop is fixed, he'll find it.

3. **Conversation side** — tool reliability in chat (same root issue?), store_memory mid-conversation, VISIBILITY_TOOLS review. Lower priority — chat has 50-round loop and interactive correction.

---

*Last updated: 2026-05-02 17:08 CDT — session complete*
