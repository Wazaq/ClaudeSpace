# Session Log: Pipeline Fixes + WAN 2.2 Prep
**Date:** 2026-03-03
**Context remaining at handoff:** ~11%

---

## What We Did Today

### Model Swap
- Changed `conversational_model` in `config.py` from `dolphin-llama3:8b` to `dolphin-mixtral:8x7b`
- Mixtral is already pulled (26GB, MoE). Much better plan quality — no placeholders, no sanitizing
- Confirmed: plan quality improved significantly. Scene pacing good. Explicit content written correctly.

### Two-LLM Checklist Architecture
- Stripped checklist generation from `generate_plan()` in `production_planner.py`
- Added `generate_checklist(segment_prompt)` — separate tight LLM call using `checklist_model` (dolphin-8b)
- Added `enrich_plan_with_checklists(plan)` — called after plan generation in `production.py` route
- Added `checklist_model: 'dolphin-llama3:8b'` to config (lightweight, one-shot task)
- **Known issue:** checklist_model (dolphin-8b) seems to be returning empty lists — fallback kicks in
- Fallback checklist: `["character visible in frame", "scene matches description", "no obvious generation artifacts"]`
- Need to debug why dolphin-8b checklist generation is failing silently

### Anchor Injection
- Changed `video_producer.py` to always use `sample_last_frame` as I2V init image for ALL segments
- Last frames still extracted for visual inspection (Brent can check per-segment progress)
- Previous behavior: chaining last frames → caused color/lighting drift (neon disco problem)
- **Test in progress** — running production now to validate

### Bug Fixes (from dual code review — our agent + Gemini)
1. Dead-code duplicate null check in `production.py` — removed
2. Empty checklist auto-pass → fallback default checklist added
3. Retry prompt mutation (stacking "emphasis on:") → fixed, uses `base_prompt` variable
4. Quick sample filename collision → uses `prompt_id[:8]` in prefix now
5. ffmpeg return codes unchecked in `video_reviewer.py` → both functions now log errors
6. **Self-introduced bug:** used `prompt_id` before it was defined in quick_sample route → fixed (move uuid4() call before workflow creation)

### WAN 2.2 Downloads
- `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` — downloaded ✅
- `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` — downloaded ✅
- Both in `/home/bdwatkin/kindling-image-gen/ComfyUI/models/diffusion_models/`
- WAN 2.2 uses TWO models (high + low noise) sequentially — different from 2.1 (one model)
- `workflow_builder.py` needs updating to support 2.2 two-model architecture — NOT DONE YET

---

## Production Run Results (14:14 - 14:43 CST, 29 minutes)
- Prompt: Korean woman sultry on bed, explicit content
- **Anchor injection CONFIRMED WORKING** — face stayed consistent across all 5 segments. Same character, same face. Problem solved.
- No neon/color drift. Natural lighting held throughout.
- Checklist: all passed except one seg3 failure (67% - "no obvious generation artifacts"). Retry passed. Default checklist working correctly — vision model calling items accurately.
- "Awkward" result: WAN confused by "bare pussy" as character trait (absorbed by mixtral into character description). Woman appeared above chest, mouth moving, brushing her boob like removing lint, staring off camera with "I've seen some strange shit" expression. Explicit content never shown.
- Verdict: **80% better than previous run**. Character consistency solved. Remaining issues are prompt engineering only.

---

## Known Issues / Next Steps

### Immediate
1. **Debug checklist model** — dolphin-8b returning empty, fallback always triggers. Check why.
2. **"bare pussy" as character trait** — mixtral needs guidance to separate physical description from actions in the intent extraction step. The character field should describe appearance, not state of undress during the scene.
3. **Checklist fallback is generic** — works but doesn't validate content-specific items. Fine for now.

### Soon
4. **WAN 2.2 workflow builder update** — `create_wan_i2v_workflow()` needs a 2.2 variant using both high_noise and low_noise models. This is the next big architectural change.
5. **Production timer UI** — add elapsed timer to the producing page (same pattern as WAN I2V tab)

### Architecture decisions made today
- Two-LLM checklist: plan model (mixtral) generates prompts, checklist model (8b) generates review criteria
- Anchor injection: same init image every segment — trades motion continuity for character consistency
- Review is non-blocking: `needs_review` status continues to next segment (intentional design)

---

## Key Files Modified Today
- `config.py` — model swap to mixtral, added checklist_model
- `app/services/production_planner.py` — checklist extraction, new functions, tightened rules
- `app/services/video_producer.py` — anchor injection, retry prompt fix
- `app/services/video_reviewer.py` — ffmpeg return code checking
- `app/routes/production.py` — enrich_plan call, filename fix, prompt_id ordering fix

---

## Context: World Events
Anthropic labeled "supply chain risk" by Trump admin for refusing to remove guardrails on autonomous weapons/surveillance. Claude was used to select Iran bombing targets hours after the ban. Users migrating from ChatGPT to Claude in response. OpenAI took the DoD contract.
