# Session Handoff — 2026-03-27 (morning session)
*Updated at session close. Pick up here.*

---

## What Was Built Today (2026-03-27 morning)

### Completed TODOs

**#4 CFG check** — verified, no changes needed.
- WAN 2.1 I2V/T2V: cfg=6 ✅ (within 5-7 range)
- WAN 2.2 I2V/T2V: cfg=3.5 ✅ (intentionally lower per community guidance)

**#3 Default negative prompt** — centralized + improved
- New constant `config.WAN_DEFAULT_NEGATIVE` (one place to update going forward)
- Merged WAN official Chinese defaults (static frame, frozen motion, backwards walking, three legs, crowded background)
- Updated: `production_planner.py` (x2), `video_producer.py` fallback, `story_production.py` WAN segments

**#2 ScriptMaster system prompt**
- Added "ONE ACTION PER SEGMENT" rule to `generate_plan()` prompt
- Added 4n+1 frame count formula with fast/slow action guidance

**#1 Cascade appearance update**
- New route: `POST /production/cascade_appearance/<plan_id>/from/<seg_id>`
- Rewrites all downstream segment prompts with new character appearance using LLM
- Batches of 4 to prevent LLM truncation on large productions
- Frontend: purple "Cascade appearance to downstream segs →" button appears after translate
- Updates segment cards in-place — no page reload needed
- Shows warning if partial update detected

**Bridge UI terminal state**
- When all retries exhausted + validation still fails: `validation_exhausted` flag set
- Frontend shows orange warning with remaining differences instead of green "complete"
- Live validation display during polling no longer overwrites final result

**UX fixes**
- Tab persistence across refresh (localStorage)
- "Back to Library" now shows chat/story mode start screen (was showing nothing)
- Segment cards scroll to relevant position after split-regen and bridge reloads
- Fixed `switchTab()` to use `querySelector` instead of `event.target` (safe for programmatic calls)

**RIFE 32fps interpolation**
- Installed `ComfyUI-Frame-Interpolation` custom node + `cupy` dependency
- `create_rife_workflow()` in workflow_builder.py: VHS_LoadVideoPath → RIFE VFI → VHS_VideoCombine
- Background job: `start_interpolation()` / `get_interpolation_status()`
- Routes: `POST /production/interpolate/<plan_id>`, `GET /production/interpolate_status/<id>`
- Frontend: purple "RIFE 32fps" button in edit view toolbar
- **First run will auto-download rife49.pth (~60MB)** — may take a moment
- Output: `{slug}_interp_{ts}.mp4` in PRODUCTIONS_COMPLETED

---

## Remaining TODO List

1. **Smart cascade regen** — when upstream changes, auto-regen downstream (Brent deferred)
2. **Spot visibility cleanup** — `spot_discord.py:118-145`, raw tool results need delimiters/truncation
3. **RIFE testing** — test the new button on a completed production; first run downloads model
4. **LoRA training pipeline** — long-term fix for character drift across many segments

---

## Key Architecture Notes

**config.WAN_DEFAULT_NEGATIVE** — single source of truth for WAN negative prompt.
Merges English community baseline + WAN Chinese official defaults.
Update here only.

**ComfyUI service:** `comfyui.service` (separate from `kindling` service)
- Restart with: `sudo systemctl restart comfyui`
- Custom nodes in: `ComfyUI/custom_nodes/`
- Newly installed: `ComfyUI-Frame-Interpolation` (RIFE + 12 other VFI methods)

**Cascade appearance flow:**
1. User translates segment intent → purple cascade button appears
2. Click → LLM rewrites downstream prompts in batches of 4
3. Segment card text updates in-place, no reload
4. Warning shown if fewer segments returned than expected (click again to retry)

**RIFE workflow:**
- `VHS_LoadVideoPath` (full path) → `RIFE VFI` (multiplier=2, rife49.pth, float16) → `VHS_VideoCombine` (32fps, h264-mp4)
- Output lands in `sd_output/`, moved to `productions/completed/`
- Does NOT delete the original 16fps version

---

## Files Changed This Session

```
kindling-image-gen/
  config.py                          — WAN_DEFAULT_NEGATIVE constant
  app/routes/editing.py              — cascade_appearance route, interpolate routes, bridge terminal state
  app/routes/story_production.py     — use config.WAN_DEFAULT_NEGATIVE
  app/services/production_planner.py — WAN_DEFAULT_NEGATIVE, one-action rule, 4n+1 guidance
  app/services/video_producer.py     — use config.WAN_DEFAULT_NEGATIVE
  app/services/video_editor.py       — bridge terminal state, start_interpolation, _run_interpolation
  app/services/workflow_builder.py   — create_rife_workflow()
  static/js/production_editor.js     — cascade UI, scroll restore, bridge terminal state, RIFE UI
  static/js/ui.js                    — tab persistence (localStorage), switchTab fix
  static/js/main.js                  — restore active tab on load
  templates/index.html               — RIFE button
ComfyUI/custom_nodes/
  ComfyUI-Frame-Interpolation/       — newly installed RIFE node
```

---

*Handoff written end of morning session 2026-03-27. All changes committed to master. Service running.*
