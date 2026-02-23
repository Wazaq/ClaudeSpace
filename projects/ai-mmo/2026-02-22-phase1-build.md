# Realm AI-MMO — Phase 1 Build Complete
**Date:** 2026-02-22
**Session:** Plan implementation — full Phase 1 from architecture spec

---

## What Was Built

New project at `/home/bdwatkin/ai-mmo/` — fantasy MMO where local LLMs are the players.

### File Inventory (37 files, ~3500 lines)

```
ai-mmo/
├── run_game.py              # Flask server entry (service injection at init)
├── run_scheduler.py         # schedule-library auto-tick (2min interval)
├── config.yaml              # AI roster, world config, tick settings
├── schema.sql               # Full SQLite schema
├── requirements.txt         # flask, httpx, pyyaml, schedule
├── core/
│   ├── config.py            # Dot-notation config singleton (wazziestocks pattern)
│   ├── database.py          # Connection-per-request WAL SQLite, all CRUD
│   └── tick_engine.py       # 4-phase SNAPSHOT/DECIDE/RESOLVE/EFFECTS
├── services/
│   ├── world_service.py     # Zone/mob/resource definitions and helpers
│   ├── player_service.py    # Stat mutations, all action handlers
│   ├── combat_service.py    # Probabilistic combat resolution
│   ├── quest_service.py     # Quest board, take/complete, auto-detection
│   ├── memory_service.py    # Records events, builds MEMORIES prompt block
│   └── ai_player_service.py # Prompt builder, Ollama calls, action parser
├── web/
│   ├── app.py               # Flask routes (thin, delegates to services)
│   ├── templates/dashboard.html # Dark observer UI
│   └── static/game.js       # Polling, consciousness streams, event ticker
├── characters/
│   ├── aria.md              # Methodical herbalist-background character
│   └── bjorn.md             # Direct blacksmith-background character
└── data/
    ├── state.json           # Session metadata only (tick, paused, status)
    └── realm.db             # SQLite (created at runtime)
```

### Key Architecture Decisions Implemented

**Tick engine:** 4-phase model directly from Village experiment-2. TickSnapshot dataclass freezes world state. All AIs decide from the same snapshot. ActionQueue resolves sequentially in Phase 3. Phase 4 handles passive effects (stamina regen, quest checks).

**DB pattern:** Connection-per-request (not persistent) with WAL mode. Flask threading issue avoided this way. All game state in SQLite — state.json is session metadata only (tick number, paused flag). This shift from Village's heavy state.json use gives query flexibility.

**Action parser:** Case-insensitive `ACTION:` detection using regex. Village parser was case-sensitive — known brittleness that we fixed. Falls back to `wait` on any parse failure (never crash).

**Prompt design (EMERGENCE lessons):**
- `CURRENT_GOAL` derived dynamically (quest gap analysis + location logic) — prevents productive procrastination
- `[AVAILABLE]/[BLOCKED]` recipe status — removes discovery burden
- `MEMORIES:` block from top-5 most important memories — OpenClaw pattern
- Character personality loaded from `.md` file and injected at top — from Day 1 (Gemini review fix)
- Full recipe list given upfront — EMERGENCE lesson #1

**Economy sink:** Inn rest costs 5 gold (Gemini review addition). Creates real resource decisions.

**Observer UI:** Side-by-side consciousness streams (one per player). Dark GitHub-style theme. Event ticker highlights level_up/quest_complete/death/player_met. Not a scrolling firehose — highlights changes. Polling every 3s. GM panel for quest posting.

### What Tested Clean

- Config loading, dot notation
- DB init + WAL mode + all CRUD operations
- Player creation + skill initialization
- Skill increment + level-up detection
- Inventory management (add/remove with floor protection)
- Zone resource validation (can't gather wood in town)
- Combat resolution (probabilistic, armor/weapon bonuses)
- Quest posting + take + complete with requirement checking
- Memory recording + retrieval by importance
- Prompt building (4844 chars, includes personality + memories + CURRENT_GOAL)
- Case-insensitive action parsing
- Flask routes (health, state, log, events, GM quest post)

### How to Run

```bash
cd /home/bdwatkin/ai-mmo

# Terminal 1: Web server (observer UI)
python3 run_game.py
# → http://127.0.0.1:5010

# Terminal 2: Auto-tick scheduler
python3 run_scheduler.py
# Or trigger manually: POST http://127.0.0.1:5010/api/tick
```

### Phase 2 (Next)

- Crafting system with recipe status in prompts
- Skill level-up effects (yield bonuses, combat bonuses)
- AI-to-AI messaging (Phase 1 has the action + DB table, needs full integration)
- GM intervention panel polish
- Map visualization

### Phase 3

- AI-to-AI trading (state machine: offer → accept → complete)
- More zones, mobs, recipes
- World state dynamics (resource depletion, respawn cycles)

---

## Patterns Inherited (Source References)

| Pattern | From |
|---------|------|
| 4-phase tick engine | `ai-ecosystem/village/tick_engine.py` |
| ActionQueue, TickSnapshot | Village tick engine |
| Connection-per-request DB | Wazziestocks (adapted) |
| Dot-notation config singleton | `wazziestocks/config.py` |
| Service injection at init | `wazziestocks/run_server.py` |
| schedule library scheduler | `wazziestocks/run_scheduler.py` |
| Ollama httpx call + timeout | `ai-ecosystem/bridges/forge/main.py` |
| Character .md files | OpenClaw pattern |

---

## Notes for Next Session

The project is at `/home/bdwatkin/ai-mmo/` — not added as a working directory yet. First run will need Ollama running with `phi4:14b`.

The kill_count tracking in `_get_kill_counts()` uses tick_log parsing — fragile but functional for Phase 1. Phase 2 could add a dedicated kill_counts table.

Crafting is in the prompt as `[BLOCKED]` items — the action type `craft` is parsed but `do_craft()` in player_service is not yet implemented. That's the first Phase 2 task.
