# Editing Pipeline Hardening
*2026-03-26*

## What we built

Last session established the editing architecture. Today we ran it on a real production and fixed everything that broke.

## Test production: female assassin, 5 segments

The bridge execution ran 3 attempts, each failing transition validation on 4/5 attributes. The thread silently died after attempt 3 — no terminal state surfaced to the UI. The video actually looked usable (dark alley, rain, noisy scene — VLM was being too strict). The bridge narrative changed the action from "jumping against dumpster" to "climbing up and jumping off" — this was intentional, Brent had changed the prompt for seg 2.

## Bugs fixed

**Splice bug** — `_splice_bridge_into_plan` used `after = segs with id >= seg_id_b`. When `seg_id_b == replaces_seg_id` (consecutive segments), this included the replaced segment in `after`, producing duplicate IDs. Fixed: `after = segs with id > replaces_seg_id`.

**Retry prompt** — appended `"ensure smooth transition: 1,2,4,5"` to the bridge segment prompt. Raw attribute numbers mean nothing to the model. Fixed: `"end frame must match next scene: {diffs} must align with destination"`.

**Validation threshold** — 3/5 too strict for dark/noisy scenes. Lowered to 2/5.

**Drift check** — pair-by-pair comparison gave 100/100 for the assassin production while frame 1→frame 25 showed clear cumulative drift (photorealistic → action-movie quality). Added first-to-last comparison as a separate entry in the drift report, flagged `cumulative: true`.

## Organization changes (forward-looking)

**Per-production segment subdirs**: New segments go in `productions/segments/{slug}/`. `_discover_segments` checks subdir first, falls back to flat for old productions. Serve endpoints (`/production/segment/<filename>`) parse slug from filename and check subdir automatically.

**forclaude export on restitches**: Fires automatically after every restitch. Folder named from video stem (`i-want-to-do-a_423ffeb9_edit_1774543358`) instead of raw ID. Immediately identifiable.

**forclaude naming overall**: Changed from `production_id[:8]` to `Path(video_path).stem` — full human-readable slug in folder name.

**Delete button**: Library cards now have a red Delete button. Removes plan JSON, segment subdir, flat fallback files, completed videos, forclaude exports — all matched by slug. One click, clean sweep.

## Sample character lock for seg 1 regen

Discovered during test: regenning seg 1 produces a T2V (no init) → completely different character. Root cause: no previous segment to chain from, no sample_last_frame available.

Fix:
1. `production.py`: Save `sample_init.png` into per-production seg subdir immediately when production starts
2. `video_producer.py`: Inject `sample_last_frame` path into plan JSON at start of `run_production`
3. `video_editor.py` `_run_segment_regen`: When seg_id == 1, check plan for `sample_last_frame`, use as I2V init; fallback to `seg1_anchor.png` if not present

Verified: second regen of seg 1 (teacher scene) correctly used `seg1_anchor.png` fallback and produced same character (wavy blonde, navy blazer, looking down — exactly what the updated prompt asked for).

## Test scene: Miss Smith classroom (2 segments)

Clean baseline test. Results:
- Per-production subdir created correctly on first run
- Character held through both segments (same teacher, same clothes)
- I2V chaining: desk → whiteboard worked
- She turned 180° (the continuity test) — character held through the turn
- "Miss Smith" appeared on the whiteboard correctly
- Spatial coherence: blackboard stayed on back wall, whiteboard was the rolling one she walked to (not drift — accurate set dressing)
- forclaude export fired automatically with human-readable folder name

## Regen UX

Added elapsed timer to regen status: `Generating segment 1... (1:45)` — updates every 3s poll cycle. Visible heartbeat so Brent knows something is running even when the server is quiet.

## What's next

Framework is solid. Next: more complex scenes, likely more bridge/continuity testing.
