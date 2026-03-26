# Session Handoff — 2026-03-26 (end of day)
*Updated at session close. Pick up here.*

---

## What Was Built Today

### Morning — Editing Pipeline Hardening
All committed to master.

**Bug fixes:**
- Splice bug: `after = segs with id > replaces_seg_id` (was `>=`)
- Bridge retry prompt: descriptive text instead of raw attribute numbers
- Transition validation threshold: 2/5 (was 3/5)
- Drift check: first-to-last cumulative comparison added

**Organization:**
- New segments go in `productions/segments/{slug}/` per-production subdirs
- `_discover_segments` checks subdir first, falls back to flat
- forclaude export fires on restitches, named from video stem
- Delete button on library cards
- Library card videos capped at `max-height: 300px`

**Character lock for seg 1 regen:**
- `sample_last_frame` saved into plan JSON at production start
- Seg 1 regen auto-uses it as I2V init; fallback to anchor; fallback to T2V

**Regen UX:**
- Plain English → Translate → SD prompt preview (dolphin-llama3:8b, ~5s)
- Prompt + num_frames written back to plan JSON after regen
- Elapsed timer on regen status
- Character lock checkbox (checked by default for seg 2+, unchecked for seg 1)
- Duration dropdown (2s–8s, 33–129 frames)

---

### Afternoon — Split-Regen + Library Cleanup
All committed to master.

**Split-regen (core new feature):**
- `translate_prompt` endpoint: switched to `huihui_ai/qwen3.5-abliterated:35b` via `/api/chat` with `think: false`. Returns `{segments: [{label, prompt}], translated_prompt}`. Detects multiple actions, splits automatically.
- `translate_model` config key added (separate from `checklist_model`)
- `start_split_regen` / `_run_split_regen` in `video_editor.py`: N segments generated sequentially with I2V chaining, uses `_splice_bridge_into_plan`, auto-restitches
- New routes: `/production/split_regen/<plan_id>/segment/<seg_id>` and `/production/split_regen_status/<job_id>`
- Frontend: shows breakdown, button label updates, progress "Generating segment X of N", auto-reloads edit view on complete

**Character lock fix (both regen paths):**
- Single-regen AND split-regen now both respect `use_init_from_prev` for seg 1
- Unchecked = T2V from prompt only (enables appearance changes)

**File naming fix:**
- Split-regen files now named `{slug}_seg{N:02d}_{hex}.mp4` so `_discover_segments` finds them

**Library dedup:**
- `list_productions`: one entry per slug (newest file only)
- `restitch_production`: deletes all previous versions for same slug after writing new file

**Service hardening:**
- `kindling.service`: added `ExecStartPre` to kill orphan on port 5000 before each start
- Logs: `StandardOutput/Error=append:/tmp/kindling.log` (was api_wrapper.log)
- Rate limiter: 2000/hr global default (was 200)

**WAN research doc:** `projects/kindling_image_gen/WAN-best-practices.md`

---

## Test Scene: Miss Smith Classroom

Production: `i-want-to-do-a_423ffeb9`

Current state (4 segments, red hair teacher):
1. Teacher looking down, writing on papers (T2V, red hair, char lock unchecked)
2. Teacher smiling at camera (I2V from seg 1)
3. Teacher sets papers down, stands up (I2V from seg 2) — split from original seg 3
4. Teacher walks to whiteboard, writes "hello" (I2V from seg 3)

Known issues with this production:
- Hard cut between seg 2 (seated smiling) and seg 3 (standing) — bridge candidate
- Camera framing inconsistency between segs (WAN picks its own composition) — fix with explicit framing keywords in prompts

---

## Pending Work (prioritized)

1. **Bridge seg 2→3** in Miss Smith production — hard cut from seated to standing
2. **Cascade prompt update** — when appearance changes, downstream prompts still have old description. Currently manual workaround (edit textarea before regen).
3. **ScriptMaster system prompt** — add "one action per beat" rule + frame count guidance (4n+1 formula, 81f sweet spot)
4. **Default negative prompt** — update plan generation to use community WAN baseline
5. **CFG check** in ComfyUI WAN workflows (should be 5-7, check current setting)
6. **Smart handling on regen** — downstream cascade regens when upstream changes (Brent's deferred feature)
7. **Bridge UI** — surface terminal state when all retries exhausted
8. **Spot visibility cleanup** — `spot_discord.py` lines 118-145, raw tool results need delimiters/truncation
9. **RIFE interpolation** — post-production 16fps→24fps (medium priority)
10. **LoRA training pipeline** — long-term fix for character drift across many segments

---

## Key Architecture Notes

**Character lock logic:**
- Seg 1 + char lock checked → I2V from `sample_last_frame` (appearance preserved)
- Seg 1 + char lock unchecked → T2V (new character from prompt — use for appearance changes)
- Seg N>1 + char lock checked → I2V from previous seg's last frame (chains appearance)
- Seg N>1 + char lock unchecked → T2V (breaks chain intentionally)

**Reasoning model note:** `huihui_ai/qwen3.5-abliterated:35b` puts JSON in `thinking` field when using `/api/generate`. Always use `/api/chat` with `"think": false` top-level parameter.

**One action per segment:** WAN's hard rule. The translate endpoint enforces this. "Looks down, then looks up, then smiles" = 3 segments minimum.

**Library:** One completed file per production. Deduped by slug. Old versions deleted on restitch.

**Orphan port:** `ExecStartPre` in kindling.service handles this automatically on restart. If manual kill needed: `ss -tlnp | grep 5000` → `kill -9 <pid>`.

---

## Files Changed This Session

```
kindling-image-gen/
  app/routes/editing.py          — translate endpoint rewrite, split_regen routes
  app/routes/production.py       — list_productions dedup
  app/services/video_editor.py   — start_split_regen, _run_split_regen,
                                   get_split_regen_status, restitch cleanup,
                                   character lock fix (both regen paths)
  app/utils/rate_limiter.py      — 2000/hr default
  config.py                      — translate_model key
  static/js/production_editor.js — split-regen UI, segment breakdown display,
                                   pollSplitRegenStatus, editTranslatedSegments state
  README.md                      — major update (service name, editing pipeline,
                                   split-regen, LLM stack, troubleshooting)
/etc/systemd/system/kindling.service — ExecStartPre, log rename
```

---

*Handoff written at session close. Everything committed and pushed to master. Kindling service running.*
