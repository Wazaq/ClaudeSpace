# SPOT Phase 9: Discord Conversational Interface

## Context

SPOT currently requires SSH + `python3 chat.py` for conversation. The Discord bot already exists for proposals and heartbeats. Phase 9 makes Discord the primary conversation interface — SPOT lives where its heartbeats already land.

## Design Decisions

### Threads = Sessions (1:1)
Each conversation thread maps to exactly one SPOT session. Thread opens → session starts. Thread ends (goodbye or timeout) → goodbye wrap fires, session closes. This keeps main channel clean (heartbeats, proposals only) and context unambiguous.

### Context source: DB, not thread history
SPOT's context comes from the DB (memories, principles, proposals, recent sessions) — same as chat.py. The thread history is the visible conversation, not SPOT's memory. No mismatch: what you see IS the conversation, what SPOT knows comes from its persistent identity layer.

### Non-streaming with typing indicator
Discord doesn't support streaming. Bot posts "SPOT is thinking..." while Ollama runs, then edits the message with the response. Clean UX, no awkward partial text.

### Tool calls are silent
When SPOT calls query_memory, consult_claude, etc. mid-response, those round-trips happen invisibly. Only the final response posts to Discord. Same as how chat.py handles it — tool calls don't clutter the output.

### Session timeout: 30 minutes
If a thread goes quiet for 30 minutes, auto-wrap fires (stores memories, closes session). Thread gets a final message: "Session ended due to inactivity. Goodbye, Brent." Brent can always start a new thread.

---

## Triggers

**`!chat` in main channel** → bot creates a new thread ("SPOT — [date/time]"), starts session, SPOT greets.

**Reply to any SPOT heartbeat message** → bot creates a thread from that message, starts session. Natural entry point: SPOT says something interesting, Brent replies, conversation begins.

**"goodbye" in an active thread** → triggers wrap immediately, closes session.

---

## Architecture

### Extend `spot_discord.py`, don't replace it
All existing approval gate logic stays. Add:
- `active_threads` dict: `{thread_id: session_id}` — tracks open conversations
- `on_message` handler extended to route thread messages to Ollama
- `!chat` command creates thread + starts session
- Reply-to-heartbeat detection creates thread + starts session

### Ollama calls from async bot
discord.py is async; Ollama calls are blocking. Use `asyncio.get_event_loop().run_in_executor(None, blocking_fn)` to avoid freezing the bot. Same pattern for all tool calls.

### Reuse existing logic
- `start_session()`, `close_session()`, `save_message()` from spot_tools — unchanged
- `get_principles()`, `get_memories()`, `get_core_memories()`, `get_proposals()` — unchanged
- `run_tool_loop()` from chat.py — extract into shared module or inline simplified version
- System prompt construction — copy from chat.py, same identity framing

### Tool loop in Discord context
chat.py's `run_tool_loop` streams output, which doesn't work here. Need a non-streaming version:
- Single `ollama.chat()` call (non-streaming, `stream=False`)
- Check for tool calls in response
- Execute tools, append results, call again
- Repeat up to max_rounds=8
- Post final text response to thread

---

## Files to Change

**`spot_discord.py`** — extend with conversation handling (primary change)

**`spot_tools.py`** — possibly extract tool definitions to avoid importing chat.py

**`chat.py`** — consider extracting tool definitions + system prompt builder into `spot_tools.py` or a new `spot_core.py` so both chat.py and spot_discord.py share them without duplication

---

## New File: `spot_core.py` (optional but clean)

If the shared logic between chat.py and spot_discord.py gets unwieldy, extract:
- `build_system_prompt()` — assembles full system prompt from DB
- `CONVERSATION_TOOLS` — tool definitions list
- `run_tool_loop_sync()` — non-streaming tool loop for cron/discord use

This keeps chat.py and spot_discord.py thin I/O wrappers around shared core logic.

---

## Systemd Service for the Bot

Bot needs to run 24/7 to catch heartbeat replies, proposals, and `!chat` triggers.

**`/etc/systemd/system/spot-discord.service`:**
```ini
[Unit]
Description=SPOT Discord Bot
After=network.target

[Service]
Type=simple
User=bdwatkin
WorkingDirectory=/home/bdwatkin/spot
ExecStart=/usr/bin/python3 /home/bdwatkin/spot/spot_discord.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Note: `Type=simple` + `Restart=on-failure` because the bot is long-running (unlike the oneshot maintenance/heartbeat scripts).

---

## Verification

1. `!chat` in #spot → thread created, SPOT greets
2. Reply to a heartbeat → thread created, conversation starts
3. Ask SPOT something that triggers `query_memory` → tool fires silently, SPOT incorporates result
4. Say "goodbye" → wrap fires, memories stored, thread gets farewell message
5. Leave thread idle 30 min → auto-wrap fires
6. Check DB: `SELECT * FROM sessions ORDER BY id DESC LIMIT 3;` — sessions created correctly
7. Restart bot service, verify `!chat` still works

---

## Step Ordering

1. Extract shared logic into `spot_core.py` (build_system_prompt, tool definitions, sync tool loop)
2. Extend `spot_discord.py` with thread conversation handling
3. Test manually (run bot in terminal, verify threads work)
4. Write systemd service file to /tmp, install
5. Enable service, verify with `systemctl status spot-discord`
6. Update concept.md

---

## Open Question

**Goodbye wrap in Discord context:** chat.py's wrap is a separate tool loop that generates a farewell message AND stores memories. In Discord, do we want SPOT to post its farewell to the thread before wrapping? Probably yes — "Goodbye, Brent. I'll remember [x]." Feels right. Confirm during implementation.
