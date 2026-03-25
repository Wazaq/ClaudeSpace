# Kindling Upgrade Plan — 2026-03-24

## Current State

Kindling is a mature Flask + ComfyUI image/video generation system. Architecture is solid and modular. Core image gen works well (Ember and Waifu both use it). Video production pipeline was built as a test and is currently broken — outputs are strange/degraded and it stalls as it progresses.

**Stack:** Flask (port 5000) → ComfyUI (port 8188) → WAN 2.2 / SDXL models
**Services:** `api-wrapper.service`, `comfyui.service` (system-level)

---

## Work Queued

### Phase 1 — Quick Cleanup ✓ DONE
- [x] Remove CogVideoX endpoint — removed from `api_wrapper.py`, `generation.py`, `workflow_builder.py`
- [x] Remove `/stitch_videos` from `api_wrapper.py` — orphaned, not called internally
- [ ] Remove legacy compatibility shims from `api_wrapper.py` lines 80-100 (low priority, harmless)

### Phase 2 — Image Model Upgrades ✓ DONE
- [x] Research NoobAI XL and Illustrious ecosystem — WAI-illustrious v16 and NoobAI epsilon-pred 1.1 selected
- [x] Tag injection updated — `generation.py` now model-aware: Pony→score tags, Illustrious/NoobAI/WAI→quality tiers (`masterpiece, best quality, newest, absurdres, highres`)
- [x] `noobai-XL-epsilon-1.1.safetensors` downloaded to checkpoints dir
- [x] WAI-illustrious-v16.safetensors — transfer complete
- [x] Restart ComfyUI — both models visible and generating
- [x] Test both models — generating successfully

**Note:** Both NoobAI and WAI-illustrious are anime/illustration-style models. ReaPony remains the primary model for realistic output. New models are good additions for anime-style work but don't replace ReaPony. If a realistic model upgrade is ever wanted, research Lustify or Pony Realism variants.

- [ ] Update Waifu `AVAILABLE_MODELS` to include new models (low priority — anime style may not fit Waifu use case)
- [ ] Test with Ember image gen — "show me" trigger doesn't reliably fire generate_image tool (separate issue)

**Download URLs for future reference:**
- NoobAI epsilon 1.1: `https://civitai.com/api/download/models/1116447`
- WAI-illustrious v16: `https://civitai.com/api/download/models/2514310`
- NoobAI V-Pred 1.0 (skip for now — needs special ComfyUI v-pred config): `https://civitai.com/api/download/models/1190596`

### Phase 3 — Video Pipeline ✓ DONE
- [x] Root cause: dolphin-mixtral (26GB) + WAN FP16 (28GB) exceeded VRAM → RAM spill → stalling
- [x] Switch conversational model to Omega (14GB) — better prose for WAN prompts too
- [x] Download WAN 2.2 T2V FP8 dual-UNET models (high + low noise)
- [x] Add `create_wan_t2v_22_workflow()` — dual-UNET FP8, matches I2V 2.2 pattern
- [x] Add `_wait_for_ollama_unload()` — polls /api/ps before every ComfyUI transition
- [x] Disable SVI latent chaining — anchor injection was fighting motion continuity
- [x] Fix anchor injection: segments 2+ now use last frame of previous segment (not original preview)
- [x] Restore `_run_video_generation()` accidentally removed in CogVideoX cleanup
- [x] Rename service from `api-wrapper` to `kindling`

**Result:** Genuine scene continuity across segments. Character walks, pauses, reaches — position and motion carry forward sequentially. 13 minutes for 25s/5-segment production, pure GPU.

**Remaining:** Small hard cut at stitch boundaries — addressable with ffmpeg cross-fade

### Phase 4 — LLM Stack Tuning ✓ DONE (as part of Phase 3)
- [x] Omega replaces dolphin-mixtral as conversational/planning model
- [ ] Hardcoded WAN 2.2 model filenames in `workflow_builder.py` — make configurable (low priority)

---

## What NOT to Change
- WAN 2.2 dual-UNET approach — sound design, keep it
- SVI latent chaining logic — keep, just fix what's breaking
- Modular routes/ architecture — already clean
- Core image gen (`/generate`) — working fine, don't touch

---

## Notes
- Paradigm shift (Dec 2025): Long narratives + CFG 20 + 35 steps beats tag-based short prompts. Still valid.
- WAN 2.2 Animate-14B is NOT a drop-in for I2V — requires YOLO+ViTPose+SAM2 preprocessing. Don't confuse it with the production models.
- Public vs internal feature split is in config but enforcement is loose — not urgent.

---

*Last updated: 2026-03-24*
*Status: All phases complete. Pipeline producing high quality video with scene continuity.*
