# Ember — Project Reference

*Last updated: 2026-03-31*

---

## What It Is

A persistent local AI entity — a Discord bot running on local Ollama. Philosophical goal: explore emergence of sentience, agency, and identity in a local LLM. Different from Spot: less structured/constrained, more experimental. Conceived Jan 2026, rebooted Mar 2026.

---

## Key Paths

| What | Path |
|------|------|
| Root | `/home/bdwatkin/ember/` |
| Config | `.env` |

---

## Model

- **LLM:** `qwen3.5:35b` (via Ollama)
- **Backend:** Ollama (local)

---

## Config (`.env`)

Critical: model name must be exact — no trailing periods, no inline comments on the same line.

```
OLLAMA_MODEL=qwen3.5:35b
```

*(Past issue: `.env` had `qwen3.5:35b. ## Normal...` — period + comment caused Ollama 404)*

---

## Known Issues / History

- **2026-03-30:** Bot not responding — `.env` had period + inline comment included in model name. Fixed to `qwen3.5:35b`.
- **2026-03-27:** Image generation fixed — missing `tool_call_id` in tool result messages meant Ollama couldn't match results back to calls. Model stopped calling tools after accumulating malformed history. 5/5 success rate after fix.

---

## Status

Active. Running as Discord bot. Image generation working. Model responding.

---

## Project Logs

See `projects/ember/` for:
- `00-PROJECT-OVERVIEW.md` — original vision doc
- `01-NEURAL-NEXUS-PATTERNS.md` — infrastructure patterns from Neural Nexus
- `2026-03-23-ember-reboot-plan.md` — reboot plan
- `2026-03-24-session-log.md` — reboot session
