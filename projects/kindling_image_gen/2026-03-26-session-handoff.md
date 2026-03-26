# Session Handoff — 2026-03-26 (afternoon)
*Context limit hit mid-session. Pick up here.*

---

## What Was Built Today

### Production Editing Pipeline — Hardening Pass
All in `kindling-image-gen`. Committed to master.

**Bug fixes:**
- Splice bug: `after = segs with id > replaces_seg_id` (was `>=`, caused duplicate IDs after bridge)
- Bridge retry prompt now uses descriptive text, not raw attribute numbers
- Transition validation threshold: 2/5 (was 3/5, too strict for noisy scenes)
- Drift check: adds first-to-last cumulative comparison alongside pair-by-pair

**Organization:**
- New segments go in `productions/segments/{slug}/` per-production subdirs
- Backward compat: `_discover_segments` checks subdir first, falls back to flat
- forclaude export fires on restitches; named from video stem (human-readable)
- Delete button on library cards: removes plan, segments, completed videos, forclaude exports
- Library card videos capped at `max-height: 300px`

**Character lock for seg 1 regen:**
- `sample_last_frame` path saved into plan JSON at production start
- `_run_segment_regen`: seg 1 auto-uses `sample_last_frame` as I2V init; fallback to `seg1_anchor.png`

**Regen UX:**
- Plain English → Translate → SD prompt preview flow (uses `dolphin-llama3:8b`, ~5s)
- Prompt + num_frames written back to plan JSON after regen
- Elapsed timer shows on regen status (updates every 3s)
- **Character lock checkbox** — checked by default for seg 2+, unchecked for seg 1. Uncheck when intentionally changing appearance.
- **Duration dropdown** — 2s through 8s (33-129 frames). Saved back to plan after regen.

---

## Test Scene: Miss Smith Classroom

Production: `i-want-to-do-a_423ffeb9`

Original 2 segments:
1. Teacher sitting at desk writing, facing camera
2. Teacher gets up, walks to whiteboard, writes "Miss Smith"

Tests run:
- Original production: PASSED — character held through 180° turn, whiteboard correct, spatial coherence (blackboard behind desk, rolling whiteboard she walked to)
- Regen seg 1 (no changes): Used anchor fallback → PASSED, same character
- Regen seg 1 (red hair, 8s, no char lock): Started but context ran out before seeing result

---

## Current State / What's In Flight

The regen UI changes (character lock checkbox + duration dropdown) were just deployed. Service is running. These have NOT been tested yet — do this first.

The teacher scene is the test vehicle. Recommend:
1. Hard refresh browser
2. Open edit view for `i-want-to-do-a_423ffeb9`
3. Regen seg 1 with: intent "give her red hair in a ponytail, looking down at papers", uncheck character lock, set duration to 7-8s
4. Verify: translated prompt has red hair, no anchor used, correct frame count sent to regen
5. Check forclaude export after completion

---

## WAN Research — KEY FINDINGS

Full doc at `projects/kindling_image_gen/WAN-best-practices.md`

**Most important for immediate use:**

1. **One action per clip** — hardest rule, most violated. "Look down → look up → smile" is 3 segments minimum, not 1. ScriptMaster needs to know this.

2. **Frame counts: `4n + 1` formula** (25, 49, 81, 97...). 81 = sweet spot. Fast actions need FEWER frames (49), not more. Quality degrades above 97.

3. **CFG should be 5-7** — check current ComfyUI workflow setting. Above 7 = flickering between frames.

4. **LoRAs required for character consistency** in longer productions. Prompt + anchor alone will drift across many segments. This is the real fix for the assassin production drift issue.

5. **FLF2V = what our bridge system does** — spatially coherent anchors required, no impossible motion paths.

6. **Community negative prompt baseline:**
   ```
   blurry, distorted face, deformed eyes, extra limbs, bad anatomy, artifacts, glitch, motion blur, watermark, text, flickering, duplicate body parts, low resolution, grainy, inconsistent character, identity drift
   ```

---

## Pending Work (prioritized)

1. **Test character lock checkbox + duration dropdown** — just deployed, untested
2. **Update ScriptMaster system prompt** with "one action per beat" rule and frame count guidance
3. **Update default negative prompt** in plan generation to use community baseline
4. **Check CFG setting** in ComfyUI WAN workflows
5. **Bridge UI**: surface terminal state when all retries exhausted (currently just stops)
6. **RIFE interpolation**: post-production 16fps → 24fps step (medium priority)
7. **LoRA training pipeline**: long-term fix for character drift
8. **Spot visibility cleanup**: `_post_visibility_status` in `spot_discord.py` lines 118-145 — raw tool results need delimiters/truncation

---

## Files Changed This Session

```
kindling-image-gen/
  app/routes/editing.py        — delete endpoint, translate_prompt endpoint, serve subdir logic
  app/routes/production.py     — sample_init.png saved to seg subdir
  app/services/video_editor.py — _seg_dir(), _discover_segments subdir, all path updates,
                                  restitch forclaude export, splice fix, retry prompt fix,
                                  validation threshold, cumulative drift, sample_last_frame
                                  for seg1 regen, prompt/num_frames writeback, char lock logic
  app/services/video_producer.py — slug/seg_dir in run_production, _stitch_and_finalize,
                                    forclaude naming from video stem, sample_last_frame into plan
  static/js/production.js      — library video height cap, delete button + deleteProduction()
  static/js/production_editor.js — char lock checkbox, duration dropdown, elapsed timer,
                                    translateRegenPrompt(), editRegenStartTime state
```

---

## Plan File

The implementation plan at `wobbly-sprouting-nest.md` is complete for stages 1-4. Active work is now hardening/UX iteration on top of that base.

---

*Handoff written at 5% context. All changes committed and pushed to master.*
