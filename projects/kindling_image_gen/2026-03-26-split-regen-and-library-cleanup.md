# Session Log: Split-Regen + Library Cleanup
*2026-03-26 afternoon*

---

## What Was Built

### Split-Regen (core new feature)
**Problem:** Regen was 1-to-1 only. No way to split one segment into multiple when a description contains multiple actions. Bridge existed for connecting two segments, but couldn't touch seg 1 or add narrative content (wrong tool for the job).

**Solution:** New split-regen pipeline that replaces one segment with N segments, one per detected action.

**Components:**
- `translate_prompt` endpoint: switched from `/api/generate` to `/api/chat` with `think: false` (Qwen3.5 is a reasoning model — thinking mode was putting JSON output in `thinking` field instead of `response`). Returns `{segments: [{label, prompt}], translated_prompt}` — detects multiple actions, splits automatically.
- `translate_model` config key: `huihui_ai/qwen3.5-abliterated:35b` (Spot's model, JSON-capable). Separate from `checklist_model`.
- `start_split_regen` / `_run_split_regen` in `video_editor.py`: generates N segments sequentially with I2V chaining (same pattern as bridge execution). Uses `_splice_bridge_into_plan` to insert N segments replacing original.
- `start_split_regen_route` / `split_regen_status` routes in `editing.py`.
- Frontend: translate response shows segment breakdown ("3 actions detected"), confirm button updates label, split-regen progress shows "Generating segment X of N", auto-reloads edit view on completion (segment IDs change).

**Bugs found and fixed during testing:**
1. File naming: split-regen files were named `{slug}_splitregen..._s1_...mp4` — `_discover_segments` only finds `{slug}_seg\d+_.mp4`. Fixed to use standard naming.
2. Character lock ignored for seg 1: both single-regen and split-regen were always using `sample_last_frame` regardless of `use_init_from_prev` flag. Fixed — char lock unchecked → T2V from prompt only (enables appearance changes).

### Reasoning model + JSON mode fix
Qwen3.5 with `format: json` + `/api/generate` puts output in `thinking` field (empty `response`). Fix: use `/api/chat` with `think: false` as top-level parameter. This is the correct approach per Ollama docs — `think` in options is ignored for generate endpoint.

### Library deduplication
Every restitch created a new `{slug}_edit_{timestamp}.mp4` in completed/, accumulating indefinitely.

**Fixes:**
1. `list_productions`: deduplicates by slug, shows only latest version per production.
2. `restitch_production`: deletes all previous versions for the same slug after writing new file. One file per production on disk, always current.

### Orphan port fix
Pattern: service crashes mid-job → Python process lingers holding port 5000 → systemd restart loop (every attempt fails with "Address already in use").

**Fix:** Added `ExecStartPre` to kindling.service that kills whatever holds port 5000 before starting. Also updated log files from `api_wrapper.log` to `kindling.log`.

### Rate limiter
Global default bumped from 200/hour to 2000/hour — internal dev server was 429ing itself during normal use.

---

## Key Architectural Insight: Character Lock

- **Seg 1, char lock checked**: I2V from `sample_last_frame` (preserves appearance)
- **Seg 1, char lock unchecked**: T2V — model generates from prompt alone. This is how you change character appearance.
- **Seg N > 1, char lock checked**: I2V from previous segment's last frame (chains appearance)
- **Seg N > 1, char lock unchecked**: T2V — new character from prompt (breaks chain intentionally)

LoRA is the long-term solution for consistent appearance across many segments without drift.

---

## Pending / Known Issues

1. **Cascade prompt update**: when you change appearance in one segment, downstream segment prompts still have the old description. Manual edit required. "Smart handling on regen" feature deferred.
2. **Camera framing inconsistency**: WAN picks its own shot composition per segment. Explicit framing keywords in every prompt ("medium shot, waist-up") is the fix.
3. **Bridge between seg 2 and 3**: hard cut from seated/smiling to standing at whiteboard. Bridge would smooth it.
4. **ScriptMaster prompt update**: "one action per beat" rule + frame count guidance (from WAN research).
5. **Default negative prompt update**: community baseline from WAN research.
6. **CFG check** in ComfyUI WAN workflows (should be 5-7).
7. **Spot visibility cleanup**: `spot_discord.py` lines 118-145.
8. **RIFE interpolation**: post-production 16→24fps (medium priority).
9. **LoRA training pipeline**: long-term character consistency fix.
