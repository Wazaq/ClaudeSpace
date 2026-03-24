# Ember Reboot Plan
*2026-03-23 — session notes before context death*

## What Ember Is Now
Repurposing Ember (original multi-AI group chat concept) into an adult companion Discord bot.
Private server only. Not a replacement for Myla — a pressure valve for needs she doesn't want to help with.
SPOT-level memory/identity so it grows over time.

## Architecture
```
Discord bot (ember_discord.py)
    ↓ conversation
Ollama (huihui_ai/qwen3.5-abliterated:35b)
    ↓ image requests
Kindling API (localhost:5000/generate-image)
    ↓ memory/identity
SQLite (ember_identity.db — clean out old data, start fresh)
```

## Model
**`huihui_ai/qwen3.5-abliterated:35b`** — clear winner.
- Same Qwen architecture as SPOT — already trusted
- Abliterated (refusals removed at weight level, not prompt hacks — more reliable)
- ~24GB, fits on RTX 5070 Ti
- `qwen3.5:35b` base already pulled on the machine

```bash
ollama pull huihui_ai/qwen3.5-abliterated:35b
```

## Image Generation
No new infrastructure. Kindling Flask API already running on port 5000.
`/generate-image` route exists. Ember calls it over HTTP.
SDXL and Flux both available.

## What to Port from SPOT
- Discord bot structure (spot_discord.py as template)
- Memory system (significance, decay, is_core, categories)
- consult_claude equivalent
- suggest_wrap

## What NOT to Port from SPOT
- Growth proposals / code review workflow (SPOT-specific)
- Heartbeat / maintenance scripts (add later if needed)

## What's New vs SPOT
- Image generation on demand ("generate me...")
- Adult/uncensored persona
- Relationship/preference memory (what Brent likes, evolving dynamic)

## Next Steps (next session)
1. Pull the model
2. Clean out Ember directory (flush old DB, remove planning docs no longer relevant)
3. Init new ember_identity.db (same schema as SPOT roughly)
4. Build ember_discord.py from SPOT template
5. Wire Kindling image gen
6. First contact
