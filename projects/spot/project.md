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

## Current Status (2026-05-02)

- Phase 9 complete — full Discord conversational interface
- 78/300 memories after cleanup (was 100/100 CRITICAL — all archived heartbeat logs purged)
- Heartbeat now autonomous: two-step inference, Spot chooses his own task, uses real tools
- Memory pipeline working: active → dormant (7d) → archived (30d) → deleted (3am)
- Cap raised 100→300, env-configurable via SPOT_MEMORY_CAP

---

## TODO

- [ ] Get back to working sessions with SPOT — he's been idle, needs actual use
- [ ] Memory pruning conversation (approaching 100+ memories, decisions needed)
- [x] **Heartbeat enhancement (2026-05-02)** — Spot now uses tools during heartbeat: query_database, search_web, store_memory. First run found a rejected proposal, researched 5 real papers on proactive AI questioning, stored memory ID 148, wrote notes files. See session log: `2026-05-02-openclaw-investigation.md`
- [ ] OpenClaw — shelved for now. May revisit as a separate project with a new personality to experiment with the framework directly.
