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

### Phase 3 — Video Pipeline (Rethink/Fix)
- [ ] Diagnose what's actually failing in the current pipeline
  - Is it the SVI latent chaining? The vision review loop? The stitching?
  - Pull logs from a failed run and trace where it breaks down
- [ ] Decide: fix the current pipeline or rebuild it cleaner
  - The dual-UNET WAN 2.2 approach is still sound
  - The complexity (planner → sampler → reviewer → retry → stitch) may be over-engineered for current use
- [ ] Consider a simpler "just generate a video" path without the full autonomous pipeline for quick tests

### Phase 4 — LLM Stack Tuning
- [ ] Evaluate if dolphin-mixtral is still the right choice for Kindling's planning/optimization
  - Given what we learned today about model quality, may be worth testing Omega or Qwen3 for the planner role
- [ ] Hardcoded WAN 2.2 model filenames in `workflow_builder.py` — make configurable

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
*Next session: Phase 3 — diagnose video pipeline failures*
