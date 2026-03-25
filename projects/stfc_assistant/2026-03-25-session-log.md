# STFC Assistant — Build Session Log
*2026-03-25*

## What was built

Full web-based game assistant for Star Trek Fleet Command. Flask + Python + SQLite + vanilla JS, matching Kindling's stack.

## Architecture

- **Port:** 5001 (`stfc-assistant.service` system-level, User=bdwatkin)
- **Data:** Two sources ingested into SQLite
  - GitHub `STFCcommunity/data` — levels 1-60, 1054 research + 95 buildings
  - `data.stfc.space` API — levels 61-80, 1342 additional building levels (sigma costs)
- **Resolver:** DAG traversal (`app/services/resolver.py`), topological order, player state diff, level expansion
- **LLM:** Qwen via Ollama for both players (agent-style, not conversational partner)
- **UI:** 4-tab web app — Assistant, Checklist, My State, Data Browser

## Key files

```
app.py                              Flask entry point
config.py                           LLM profiles, paths, settings
app/services/resolver.py            CORE: DAG prerequisite resolver
app/services/data_loader.py         GitHub JSON ingester
app/services/data_loader_extended.py  data.stfc.space ingester (levels 61-80)
app/services/llm_client.py          Ollama client
app/routes/chat.py                  LLM orchestration (multi-turn clarification → resolver)
app/routes/checklist.py             Check/uncheck with player state write-back
data/building_id_map.json           GitHub building name → stfc.space numeric ID map
stfc-assistant.service              systemd service file
```

## Data notes

- `data/stfc-community/` — cloned GitHub repo (gitignored, re-clone on new machine)
- `instance/stfc.db` — SQLite DB (gitignored, rebuilt on first startup)
- `data/building_id_map.json` — **keep in repo** — 95-entry map built by matching build_time fingerprints

### Resource types in DB
- Standard: `parsteel`, `tritanium`, `dilithium`
- Sigma (Ops 61+): `sigma-parsteel`, `sigma-tritanium`, `sigma-dilithium`
- Materials: `ore`, `gas`, `crystal` with `grade` (1-6) and `rarity` (common/uncommon/rare/epic)

### Data gaps
- Research data: GitHub repo tops out around level 30 for most research. `data.stfc.space` research summary has 2311 entries but none go above level 30 either — this is a game data limitation, not a scraping gap.
- Buildings: fully covered 1-80 with both sources combined.

## Resolver behavior

- **Fresh player** (no state): plan can be 2000+ steps — correct, that's the whole tree
- **Player with state entered**: resolver diffs and shows only remaining work
- **State write-back**: checking a checklist item writes to `player_research` or `player_buildings` — future resolver calls reflect it automatically
- **Staleness warning**: if player state > 14 days old, LLM warns before generating plan

## Known issues / next session

- Research above level ~30 not in any data source — affects high-level research planning
- LLM needs Qwen model running locally (`huihui_ai/qwen3.5-abliterated:35b`) — if Ollama doesn't have it pulled, chat will fail with connection error
- Player state requires manual entry for first use (no import from game)
- Image gen not implemented (not scoped)

## Setup on new machine

```bash
cd /home/bdwatkin/stfc-assistant
python3 -m venv venv
venv/bin/pip install -r requirements.txt
git clone --depth=1 https://github.com/STFCcommunity/data data/stfc-community
venv/bin/python -c "from app.utils.db import init_db; from app.services.data_loader import ingest_all; from app.services.data_loader_extended import ingest_extended_buildings; init_db(); ingest_all(force=True); ingest_extended_buildings(force=True)"
# Then install service and start
```
