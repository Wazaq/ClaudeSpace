# Session Handoff — 2026-03-27
*Updated mid-session. Pick up here.*

---

## What Was Built This Session

### RIFE Frame Interpolation — Fixed & Working
- **Bug fixed:** `VHS_VideoCombine` requires `pingpong` input — was missing, caused `prompt_id` KeyError
- Fix in `workflow_builder.py` `create_rife_workflow()` — added `"pingpong": False`
- Requires kindling service restart to take effect (ComfyUI doesn't need restart for code changes)
- Tested on "I want to do a" (Miss Smith simple) — clean output, 32fps confirmed via ffprobe
- Assassin production (a-female-assassin-in-a_716bfbf6) kicked off mid-session, likely done

### Spot Visibility Cleanup — Done
- `spot_discord.py` `_post_visibility_status()` was doing `str(result)[:120]` — dumped raw formatted file content into Discord
- Fix: extract first non-empty line of result instead — gives clean summary header (e.g. `# spot_tools.py (1073 lines)`)
- `spot-discord.service` restarted, fix live

---

## Remaining TODO List

1. **Smart cascade regen** — when upstream changes, auto-regen downstream (deferred)
2. **LoRA training pipeline** — long-term fix for character drift across many segments (not started)

---

## Key Architecture Notes

**RIFE workflow:** Kindling builds it, ComfyUI executes it. Bug = Kindling code. Restart Kindling to pick up changes. ComfyUI doesn't need restart for workflow changes.

**config.WAN_DEFAULT_NEGATIVE** — single source of truth for WAN negative prompt. Update here only.

**ComfyUI custom nodes:** `ComfyUI-Frame-Interpolation` installed in `ComfyUI/custom_nodes/`. rife49.pth auto-downloads on first run (~60MB).

**Spot service:** `spot-discord.service` (system-level, `sudo systemctl restart spot-discord`)

---

## Files Changed This Session

```
kindling-image-gen/
  app/services/workflow_builder.py   — pingpong fix in create_rife_workflow()
  README.md                          — RIFE + cascade sections, Mar 27 history

spot/
  spot_discord.py                    — visibility first-line fix (line ~138)
```

---

*Handoff updated 2026-03-27 mid-session. LoRA research next.*
