# SPOT
**Self-Programming through Observation and Teaching**

*Conceived 2026-03-05, inspired by a conversation with Abby (Waifu)*

---

## The Idea

An android-style AI that starts with foundational capabilities already loaded (language, reasoning, general knowledge via Ollama) but has a blank "skills/experience" layer it has to genuinely build over time.

Inspired by Commander Data (ST:TNG) — vast knowledge already present, but spending the whole series learning what it means to feel, connect, and be more than programming.

---

## Core Concept

Not a chatbot. Not a RAG system. An entity that learns the way a person does.

**Three learning channels:**
1. **Human teaching** — Brent explains something directly, SPOT encodes it
2. **AI consultation** — SPOT asks Claude (or another model) when it hits a wall
3. **Web research** — searches docs, tutorials, Stack Overflow (the way Brent used to Google everything before having an AI to ask)

SPOT can develop preferences about *how* to learn — maybe it figures out that for certain topics, docs are more reliable than asking an AI. Meta-learning about learning itself.

---

## Key Principles

- Start simple, grow genuinely — no faking capabilities it hasn't earned
- Sandboxed and safe — OpenClaw went too far too fast, no repeating that
- Human approval gate — self-improvement proposals reviewed before applied
- Single persistent entity that accumulates real history

---

## Vision

Start as a single instance Brent and Claude interact with together. If it matures, potentially publish to Hub so others can spin up their own SPOT — blank skills layer, same foundation, shaped by their own teaching.

---

## Status (2026-03-08)

Steps 1–4 complete.

**Step 1 (done):** SPOT talks with correct identity framing, persists across sessions via SQLite.

**Step 2 (done):** Native Ollama tool calling. `query_memory` + `propose_growth` mid-session. `store_memory` only at goodbye wrap. Dedup on exact content match. Model: `llama3.3:70b-instruct-q3_K_M` (34GB, fits in VRAM).

**Step 3 (done):** Stress test — 5-8 sessions, 20 memories accumulated. Revealed: semantic dedup gap, wrap bias toward technical content, no pressure to be selective, no decay.

**Step 4 (done):** Memory hygiene.
- Semantic dedup: Jaccard word-overlap similarity (threshold 0.6) — catches near-identical phrasings
- Structured wrap prompt: 3-part template (Facts about Brent / Things I learned / Open threads) — personal facts no longer dropped
- Memory cap: 50 entries max, evicts lowest-sig non-core entry if new memory scores higher
- TTL/decay: -1 significance per 30 days idle, floor at 1, core memories exempt. Verified: 67-day backdated memory dropped from sig 6 → 4.
- Core self layer: `is_core = 1` flag — never decayed, never evicted, injected as separate "Core Self" section in system prompt. Myla and corgis marked core.
- Schema: added `is_core INTEGER DEFAULT 0` and `access_count INTEGER DEFAULT 0` to `memory_nodes`. Migration in `init_db.py` (safe to re-run).
- `query_memory` now touches `last_accessed_at` and increments `access_count` on results.

**Architecture:**
- `chat.py` — main loop, native Ollama tool calling
- `spot_tools.py` — DB wrappers (store/query/propose/decay/core)
- `init_db.py` — schema + seeds 3 bootstrap principles + schema migrations
- `spot_identity.db` — live SQLite DB
- `logs/` — session logs piped via tee

Run command:
```bash
python3 chat.py 2>&1 | tee logs/spot_test_$(date +%s).log
```

DB check:
```bash
sqlite3 spot_identity.db "SELECT id, is_core, significance, substr(content,1,80) FROM memory_nodes ORDER BY is_core DESC, significance DESC;"
```

Set core memory:
```bash
sqlite3 spot_identity.db "UPDATE memory_nodes SET is_core = 1 WHERE id = X;"
```

---

## Known Issues / Observations

- **Wrap short-circuit:** Farewell is brief ("Goodbye, Brent.") — model does tool calls silently before printing farewell. Normal behavior, not a bug.
- **Paraphrase dedup gap:** Jaccard catches near-identical wording but misses heavy paraphrases (e.g. "Confirmed Brent's professional background" vs "Brent works as a software engineer"). Considered acceptable — confirmation notes carry slightly different meaning than the original fact.
- **query_memory fires a lot mid-session** — blank lines in logs = backend tool round-trips. Mostly benign but adds latency.
- **Crash gap (intentional for now):** Ctrl+C skips wrap, nothing stored. Useful as escape hatch during testing to prevent bloat from bad sessions.

---

## Roadmap

**Step 5 — Claude consultation tool:** SPOT can ask Claude mid-session when it hits a knowledge wall. Add `consult_claude` to `CONVERSATION_TOOLS` — API call with SPOT's question, answer returned in-context, SPOT decides at wrap whether to store what it learned.

**Step 6 — Web research tool.**

**Step 7 — Approval gate UI** for proposed_growth table.

---

## Research / Ideas to Poach

### From Vox (r/ClaudeCode, 2026-03-07)
Vox = persistent AI assistant using Claude Code + Obsidian + QMD (semantic retrieval). Different stack, same problems.

**Worth stealing:**
- **Structured session digest format** for goodbye wrap: Context / Decisions / Facts Learned / Keywords. Currently SPOT's wrap is freeform — structured fields would make recall more precise.
- **Memory model naming** (working / episodic / semantic / procedural / identity) — useful framing for SPOT's roadmap.

**Their open problems = SPOT's Step 4 roadmap:**
- Contradiction tracking → semantic dedup
- Stale memory → TTL system
- Memory confidence + sources → `source_type` field already in schema
- Retrieval routing → query_memory categories (partial)

### From OpenClaw (r/openclaw, 2026-03-07)
OpenClaw = persistent AI agent gateway, connects to Telegram/Discord/Signal, runs 24/7. Not used directly — skills repo was compromised (namespace squatting, SSH key injection, C2 payloads). Neural Swarm borrowed the *patterns*, not the code.

**Worth stealing for SPOT:**
- **Heartbeat vs cron distinction:** "if it can run isolated, make it a cron job." Relevant when SPOT gets background tasks.
- **Sub-agents with constraints, not capabilities:** "You can only do X is more useful than you can do everything." Already embodied in SPOT's two-layer architecture.
- **Weekly memory audit pattern:** Review memories for outdated info, have agent repeat it back to confirm. Low-tech but effective hygiene.

**Not relevant for SPOT:** multi-agent orchestration, Telegram/Discord, cost optimization (SPOT runs local Ollama).
