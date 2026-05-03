# SPOT — Project Reference

*Last updated: 2026-04-17*

**SPOT = Self-Programming through Observation and Teaching**

---

## What It Is

A persistent AI entity running on local Ollama. Starts with foundational capabilities but builds a genuine "skills/experience" layer over time through human teaching, AI consultation, and web research. Inspired by Commander Data (ST:TNG). Not a chatbot — an entity with continuous identity, memory, and autonomous daily activity.

---

## Key Paths

| What | Path |
|------|------|
| Root | `/home/bdwatkin/spot/` |
| Main chat loop | `chat.py` |
| Core shared logic | `spot_core.py` |
| Discord bot | `spot_discord.py` |
| Heartbeat | `spot_heartbeat.py` |
| Maintenance/decay | `spot_maintenance.py` |
| DB tools | `spot_tools.py` |
| DB schema | `init_db.py` |
| Live DB | `/home/bdwatkin/spot_identity.db` |
| Session logs | `/home/bdwatkin/spot/logs/` |

---

## Model

- **LLM:** `qwen3.5:35b` (via SPOT_MODEL env var)
- **Backend:** Ollama (local)
- **Note:** qwen3.5 is a thinking model — heartbeat tool set must stay lean (≤6 tools) or inference times out

---

## Services

| Service | Description |
|---------|-------------|
| `spot-discord` | Discord bot — always running |
| `spot-heartbeat.timer` | Daily noon autonomous reasoning + Discord post |
| `spot-maintenance.timer` | Daily 3am memory decay |

All system-level. `sudo systemctl [start/stop/restart] spot-discord`

---

## Architecture (Phase 9 — Current)

### Memory System (SQLite)
- `memory_nodes` table: content, significance, source_type, is_core, access_count, last_accessed_at
- **Core memories** (`is_core=1`): never decayed, never evicted, injected as "Core Self" in system prompt
- **Memory cap:** 50 entries, evicts lowest-significance non-core on overflow
- **Decay:** -1 significance per 30 days idle, floor at 1, core exempt
- **Dedup:** Jaccard word-overlap similarity (threshold 0.6)

### Tools Available to SPOT
- `query_memory` — recall stored memories
- `store_memory` — only at goodbye wrap (not mid-session)
- `propose_growth` — posts to Discord #spot for Brent approval
- `ask_claude` — consults Claude (haiku via `claude -p`, no session persistence)
- `search_web` — web research via `claude -p --allowedTools WebSearch`
- `notify_discord` — send messages to Discord channel

### Session Handling
- Terminal: `python3 chat.py 2>&1 | tee logs/spot_test_$(date +%s).log`
- Discord: `!chat` or reply to any SPOT post → opens thread (1:1 with DB session)
- 60-minute inactivity timeout auto-wraps Discord sessions

---

## Useful Commands

```bash
# Check memories
sqlite3 /home/bdwatkin/spot_identity.db "SELECT id, is_core, significance, substr(content,1,80) FROM memory_nodes ORDER BY is_core DESC, significance DESC;"

# Set core memory
sqlite3 /home/bdwatkin/spot_identity.db "UPDATE memory_nodes SET is_core = 1 WHERE id = X;"

# Check memory count
sqlite3 /home/bdwatkin/spot_identity.db "SELECT COUNT(*) FROM memory_nodes;"
```

---

## Current Status (2026-05-03)

- Phase 9 complete — full Discord conversational interface
- 78/300 memories after cleanup (was 100/100 CRITICAL — all archived heartbeat logs purged)
- Heartbeat now autonomous: two-step inference, Spot chooses his own task, uses real tools
- Memory pipeline working: active → dormant (7d) → archived (30d) → deleted (3am)
- Cap raised 100→300, env-configurable via SPOT_MEMORY_CAP
- Conversation tool sets split: CHAT_TOOLS (8, default) / CONVERSATION_TOOLS (23, !work mode)
- store_memory available mid-conversation (no longer wrap-only)
- chat_sync synthesis timeout raised to 300s (was 120s, caused silent timeouts after multi-tool chains)

---

## Tool Sets

| Set | Tools | Used when |
|-----|-------|-----------|
| CHAT_TOOLS | 8 | Default conversation (query_memory, store_memory, recall_session_context, search_web, consult_claude, suggest_wrap, write_notes_file, propose_growth) |
| CONVERSATION_TOOLS | 23 | Work mode (!work) — all above + code/self-modification tools |
| HEARTBEAT_TOOLS | 7 | Heartbeat autonomous tasks |
| WRAP_TOOLS | 24 | Goodbye wrap — CONVERSATION_TOOLS + store_session_summary |

Discord mode commands: `!work` (enable full tool set), `!endwork` (return to chat mode)

---

## TODO

- [ ] **Heartbeat tool reliability** — (in progress, backend session) pre-inject query_database/query_memory/notes results as text into step 2, mirror `_run_greeting` pattern. Only keep search_web and store_memory as live tools.
- [ ] **Spot has a note waiting** — `notes/2026-05-02-manual-maintenance.md` explains archived memory discrepancy. He'll find it once heartbeat tool loop is fixed.
- [ ] **Conversation side monitoring** — test lean CHAT_TOOLS in practice; verify store_memory fires mid-conversation; check if synthesis timeout fix (300s) improves reliability
- [x] **Conversation improvements (2026-05-03)** — lean CHAT_TOOLS, mid-conversation store_memory, !work mode, synthesis timeout fix
- [x] **Heartbeat enhancement (2026-05-02)** — two-step inference, self-directed tasks, honest fallback, multi-chunk Discord, HEARTBEAT_TOOLS (7 tools incl. read_file)
- [x] **Memory system (2026-05-02)** — cap 100→300 (SPOT_MEMORY_CAP env var), maintenance deletes archived, pipeline: active→dormant(7d)→archived(30d)→deleted(3am)
- [x] **Honest epistemics (2026-05-02)** — added to system prompt: "Memory is a starting point, not a proof. When something matters, check it."
- [ ] OpenClaw — shelved. May revisit as separate project with new personality.
