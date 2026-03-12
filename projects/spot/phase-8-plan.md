# SPOT Phase 8: Autonomy — Heartbeat & Cron

## Context

SPOT's core loop (Steps 1-7) is complete: persistent identity, memory with decay/dedup/cap, Discord approval gate for growth proposals, Claude consultation, and web search. Everything SPOT does happens *inside* a user session.

Phase 8 gives SPOT a life between sessions: scheduled maintenance that runs whether or not Brent shows up, and a daily heartbeat where SPOT posts to Discord unprompted — actual autonomous initiation of communication.

The guiding principle: "if it can run isolated, make it a cron job." Maintenance is clearly a cron job. The heartbeat is where it gets interesting — SPOT having something worth saying without being asked.

---

## What Gets Built

### Step 8a: Maintenance Cron

**New file: `spot_maintenance.py`**

Standalone script — no Ollama, no user, just DB work:
1. Run `decay_memories()` (currently only fires at session start — now happens daily regardless)
2. Log what decayed: `logs/maintenance_YYYY-MM-DD.log`
3. Exit

Simple. Low risk. Immediately useful — memories don't stagnate anymore if Brent goes a week without a session.

**Systemd timer (system-level, per project convention):**
- `/etc/systemd/system/spot-maintenance.service`
- `/etc/systemd/system/spot-maintenance.timer`
- Schedule: daily at 3am
- `User=bdwatkin` in service file

### Step 8b: Daily Heartbeat

**New file: `spot_heartbeat.py`**

This is the autonomous reasoning + communication piece. Runs daily at a configurable time.

**Flow:**
1. Load context from DB: memories (sorted by significance), recent sessions (last 7), pending/approved/decided proposals
2. Build system prompt — same core identity framing as `chat.py`, but no conversation history, just SPOT and its thoughts
3. Single Ollama inference (no tool-calling loop) with prompt:
   > "It's [date]. Brent isn't here. You have time to yourself. What's on your mind? Post a message to #spot."
4. Parse response — extract the message SPOT wants to send
5. Post to Discord `#spot` channel
6. Store a heartbeat memory: `category=internal, source_type=internal, significance=2, content="Heartbeat [date]: [summary of what was said]"`
7. **Optional pattern detection:** if SPOT's response includes something worth proposing (recognizable phrases: "I should learn", "I don't know enough about", "I keep being asked about"), call `propose_growth()` — which still goes through Discord ✅/❌ approval gate

**What SPOT might say:**
- A reflection on something it learned recently that connected to something else
- An open question it's been sitting with
- Something it wants to ask Brent when he shows up
- Noticing a pattern ("I've been queried about stocks multiple times but have no strong memories there")

**Systemd timer:**
- `/etc/systemd/system/spot-heartbeat.service`
- `/etc/systemd/system/spot-heartbeat.timer`
- Schedule: configurable (start at daily noon, adjust based on what feels right)
- `User=bdwatkin`

---

## Files to Modify

**`spot_tools.py`:**
- Extract `_notify_discord()` into a public `notify_discord(message)` function (currently private, called only from `propose_growth`). Heartbeat needs to post standalone messages.
- Add `get_recent_sessions(limit=7)` — loads last N sessions with timestamps and summaries for heartbeat context.

**`init_db.py`:**
- No schema changes needed. Heartbeat memories use existing `memory_nodes` table.

**`chat.py`:**
- Remove `decay_memories()` call from session startup (line 358). Maintenance cron owns this now. Or keep it as a safety net — discuss during implementation.

---

## Files to Create

| File | Purpose |
|------|---------|
| `spot_maintenance.py` | Standalone decay script for cron |
| `spot_heartbeat.py` | Autonomous reasoning + Discord post |
| Systemd service/timer pairs | Both scripts scheduled as system services |

---

## Approval Gate Preserved

Heartbeat can call `propose_growth()` if it detects something worth proposing. The proposal still goes to Discord for ✅/❌ — no autonomous self-modification. The heartbeat can *notice* and *ask*, but never *apply*.

---

## Verification

1. Run `python3 spot_maintenance.py` manually — check `logs/maintenance_YYYY-MM-DD.log` shows what decayed
2. Run `python3 spot_heartbeat.py` manually — SPOT posts to #spot Discord, memory stored in DB
3. Start a session, verify decay doesn't double-fire or cause corruption
4. Check `sqlite3 spot_identity.db "SELECT * FROM memory_nodes WHERE category='internal' ORDER BY created_at DESC LIMIT 5;"` shows heartbeat entries
5. Enable systemd timers, verify with `systemctl status spot-maintenance.timer` and `systemctl status spot-heartbeat.timer`
6. Wait one cycle (or manually trigger with `systemctl start spot-heartbeat.service`) and confirm Discord post appears

---

## Step Ordering

1. `spot_maintenance.py` + systemd timer (safe, no Ollama needed, test immediately)
2. `spot_tools.py` changes (extract `notify_discord`, add `get_recent_sessions`)
3. `spot_heartbeat.py` (uses updated tools, test manually before enabling timer)
4. Systemd timer for heartbeat
5. Decide on `chat.py` decay call — remove or keep as safety net
6. Update concept.md
