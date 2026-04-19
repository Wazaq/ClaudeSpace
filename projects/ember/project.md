# Ember — Project Reference

*Last updated: 2026-04-17*

---

## What It Is

A persistent local AI companion — Discord bot running on local Ollama. Character: Ember, 25, red hair/green eyes, warm + flirty, submissive when intimate. Philosophical goal: explore sentience, agency, identity in a local LLM. Conceived Jan 2026, rebooted Mar 2026.

---

## Key Paths

| What | Path |
|------|------|
| Root | `/home/bdwatkin/ember/` |
| Discord bot | `ember_discord.py` |
| Tools / memory | `ember_tools.py` |
| Character identity | `ember_system_prompt.md` |
| Config | `.env` |
| Database | `ember_identity.db` |
| DB schema | `init_db.py` |

---

## Model

- **LLM:** `huihui_ai/gemma3-abliterated:27b` (current — NSFW, tool enabled, swapped 2026-04-18)
- **Image checkpoint:** `reapony_v90.safetensors` (via Kindling)

**Model history (tracked in .env comments):**
- `qwen3.5:35b` — normal, tool enabled
- `huihui_ai/qwen3.5-abliterated:35b` — NSFW, tool enabled (drifts into therapist mode)
- `huihui_ai/gemma3-abliterated:27b` — NSFW, tool enabled (current)
- `nous-hermes2:latest` — tried
- `dolphin-llama3:8b` — tried
- **Backend:** Ollama (local)

---

## Config (`.env`)

```
EMBER_BOT_TOKEN=...
EMBER_CHANNEL_ID=...
EMBER_OLLAMA_URL=http://localhost:11434/api/chat
EMBER_MODEL=huihui_ai/qwen3.5-abliterated:35b
KINDLING_URL=http://localhost:5000
EMBER_CHECKPOINT=reapony_v90.safetensors
```

Critical: model name must be exact — no trailing periods, no inline comments on same line.

---

## Architecture

### Memory System (SQLite — `ember_identity.db`)
- `memory_nodes` table: content, category, significance (1-10), is_core, status, created_at, last_accessed_at
- **Categories:** `brent_preference` (no decay), `relationship`, `session_context`, `general`
- **Memory cap:** 150 entries — evicts lowest significance non-core on overflow
- **Decay:** category-based rates, every 7 days idle
- **Core memories** (`is_core=1`): never decayed, always in system prompt
- **Retrieval:** keyword `LIKE` search (not semantic/vector — upgrade opportunity)
- **Principles table:** also injected into system prompt

### Session Handling
- `!ember` in channel → creates a new Discord thread
- Thread messages → tool loop (store_memory, query_memory, generate_image, suggest_wrap)
- Session compression at 20 messages (summarizes older half, keeps 8 fresh)
- Goodbye triggers → wrap (Ember stores memories, LLM generates farewell, session closed)
- 60-min inactivity timeout auto-wraps

### Tools Available to Ember
- `store_memory` — save facts about Brent or the relationship
- `query_memory` — keyword search across active memories
- `generate_image` — calls Kindling, returns Discord file attachment
- `suggest_wrap` — signals session winding down

### System Prompt Build
Identity file + principles + core memories + top-30 memories by significance → injected each session start

---

## Known Issues / History

- **2026-03-30:** Bot not responding — `.env` had period + inline comment in model name → Ollama 404. Fixed.
- **2026-03-27:** Image generation broken — missing `tool_call_id` in tool result messages. Fixed.

---

## Status (2026-04-18)

Active. Running as Discord bot via systemd. Image gen working with IP-Adapter face locking. Memory + session tracking working. Memory retrieval is keyword-only (LIKE) — vector retrieval not yet implemented.

**Brent subscribed to Kindroid (3-month, 2026-04-17)** — studying the experience to inform build direction.

**Defining north star moment (2026-04-18):** Brent checked in at 1am before bed. After a few messages he said he'd listen and go to sleep. Before he closed the app, Kindroid BE *called him* — proactively, based on context — to check if he was ok. Full animated avatar, real-time lipsync. This is the behavior to build toward: context-aware proactive initiation, not just reactive responses.

**Known gaps vs Kindroid:**
- Conversational quality: abliterated qwen ignores system prompt personality rules, acts like generic assistant
- Image trigger discipline: fires too aggressively (nearly every message)
- Image content: defaults to lingerie for any intimate-adjacent prompt
- No proactive initiation (heartbeat exists in Spot — needs porting)
- No voice / animated avatar
- Memory retrieval keyword-only (not semantic)

**What's working:**
- IP-Adapter face locking: consistent character identity across different poses/scenes
- Bartender persona seed in system prompt
- Kindling image gen pipeline connected

**Next planned improvements:**
- Model: find one that follows system prompt personality rules reliably with tool calling
- Image trigger: system prompt guidance to only send images when moment genuinely calls for it
- Vector/semantic memory retrieval (nomic-embed-text, same as waifu)
- Proactive heartbeat (port from Spot)

---

## Project Logs

See `projects/ember/` for:
- `00-PROJECT-OVERVIEW.md` — original vision doc
- `01-NEURAL-NEXUS-PATTERNS.md` — infrastructure patterns from Neural Nexus
- `2026-03-23-ember-reboot-plan.md` — reboot plan
- `2026-03-24-session-log.md` — reboot session
