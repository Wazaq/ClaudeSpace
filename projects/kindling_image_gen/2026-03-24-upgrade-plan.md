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

### Phase 2 — Image Model Upgrades
- [ ] Research and pull NoobAI XL and/or Illustrious XL checkpoints
  - These are the current generation SDXL-compatible models
  - Better character consistency, better quality than Juggernaut/Pony/Animagine
  - Important for Ember's image gen quality
- [ ] Test new models with Ember's system prompt image descriptions
- [ ] Update Waifu `AVAILABLE_MODELS` if needed

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
*Next session: Start with Phase 1 cleanup*
