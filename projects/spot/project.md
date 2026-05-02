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

- **LLM:** `llama3.3:70b-instruct-q3_K_M` (34GB, fits in VRAM)
- **Backend:** Ollama (local)

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

## Current Status (2026-03-31)

- Phase 9 complete — full Discord conversational interface
- ~90/100 memories (approaching cap — will need pruning decisions soon)
- Heartbeat working, posting to #spot daily
- Visibility fix applied 2026-03-27 (first-line display only, no raw dumps)
- Needs actual use — has been in heartbeat-only mode

---

## TODO

- [ ] Get back to working sessions with SPOT — he's been idle, needs actual use
- [ ] Memory pruning conversation (90 memories, decisions needed on what to keep)
- [ ] **OpenClaw integration research** — TeaBagginsMcGee (STFC contact) mentioned OpenClaw as a way to make Spot more autonomous. Key insight: Spot already has heartbeat timing (9am/9pm) but currently only analyzes memories and does nothing else. OpenClaw is a layer over local AI models that enables a full agent loop: observe → plan → act → reflect → repeat. It can make models autonomous and handle updating automatically. Goal: give Spot something meaningful to *do* during heartbeat windows instead of just checking in. Needs a dedicated full session — don't start this mid-session or when context is over 50%.
