# Kindling: Writer Layer, Crossfade Stitching, Lightbox
*2026-04-16 — session ended ~21:42 CDT*

---

## What Got Built

### Writer Layer
New narrative script stage fires after sample approval, before plan generation.

- Uses `Beat N:` format — beat count drives segment count
- Planner prompt treats script as primary source, not chat history
- Gives the model a structured story arc to work from rather than inferring intent from conversation

### Plan Generation Fix (Large Segment Counts)
Previous approach broke on 7+ segments. Root cause: format_json=True was causing Ollama to refuse or corrupt large structured outputs, and timeout was fixed regardless of job size.

Fixes:
- `format_json=False` — let model generate JSON naturally
- Brace-depth JSON extraction — parse out the first complete JSON object from model output
- `timeout = max(180, segments × 25)` — scales with complexity

### Crossfade Stitching
`stitch_segments()` now defaults to 0.4s xfade between segments via ffmpeg `xfade` filter.
- Falls back to plain concat on failure
- Hard cuts remain visible but noticeably softened

### Lightbox for Thumbnails
Click any first/last frame thumbnail in the production view → full-size overlay appears.
- Escape key or click anywhere closes it
- No new infrastructure — just CSS + JS on existing thumbnail endpoints

---

## First 9-Segment Production
- 67 minutes end-to-end
- Character held across all segments, no visible drift
- Crossfade active — cuts visible but softer than plain concat
- Next run will have banned phrase fixes to smooth checklist further

---

## Pending From This Session

**Banned phrases** — two motion descriptions slipped through the checklist filter:
- "PJ top pulls open" (Seg 1)
- "standing up slowly" (Seg 2)
Add both to `_CHECKLIST_BANNED_PHRASES` in `production_planner.py`.

**Dragon/sorceress production** — 7-beat script was ready to paste when context wall hit. Production never started. Resume by pasting the script in a new session.

**WAN 2.7** — subject referencing (first+last frame) is API-only right now. Watch Wan-AI HuggingFace org for weight release. Wiring is straightforward once weights land.

**WAN 2.2 NSFW LoRAs** — Brent was browsing HuggingFace, download to `ComfyUI/models/loras/` when selected.

**Scene chaining** — use a completed production's final frame to seed the next scene. Not designed yet.

---

## Architecture State

```
Chat → Sample → Writer (NEW) → Planner → Production loop
                                ↑
                          Script: Beat N: format
                          Beat count = segment count
```

Plan generation: `format_json=False`, brace-depth extraction, scaled timeout
Crossfade: `stitch_segments()` → ffmpeg xfade 0.4s → fallback concat
Thumbnails: click → lightbox overlay (Escape/click to close)
