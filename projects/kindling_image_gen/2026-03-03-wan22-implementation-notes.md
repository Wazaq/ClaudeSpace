# WAN 2.2 Implementation Notes
*2026-03-03, Session 3*

---

## Community Research Findings

### The Big Context: Two Different User Populations
The WAN 2.2 community is split between native 14B users and Lightning/LightX2V LoRA acceleration users. This causes massive confusion in guides because optimal settings differ wildly. **We are using native 14B.**

| Setting | Native 14B (us) | Lightning LoRA |
|---|---|---|
| Steps | 20-40 | 4-8 |
| CFG | 3.5 | 1.0 |
| Shift | 8.0 | 5.0 |

### Validated Settings (Plan Confirmed Correct)
- **Shift 8.0**: Official template value. Community explanation: shift=8 produces a true 50/50 sigma split between high/low noise. Right default for native.
- **50/50 step split** (`half_steps = steps // 2`): Confirmed for native.
- **CFG 3.5**: Confirmed for native non-LoRA use.
- **euler + simple scheduler**: Works fine.

### Things to Look Into Later

**beta57 scheduler (RES4LYF package)**
- Community raves about it for WAN 2.2
- Described as "absolute must" by one author
- Requires installing `RES4LYF` custom node package
- Not needed for v1 but worth experimenting with after baseline works
- Link: search "ComfyUI RES4LYF beta57 WAN 2.2"

**ComfyUI-WanMoEScheduler**
- Custom node that automatically calculates the correct sigma boundary for the high/low split
- Removes the guesswork from `half_steps` — let the scheduler find the optimal transition point
- Could be a better approach than static 50/50 split
- Link: https://github.com/cmeka/ComfyUI-WanMoEScheduler

**Shift value tuning**
- shift=8 is safe default (50/50 sigma split)
- shift=5 = more motion, less detail refinement
- shift=3 = max motion
- Could tune down to 5-6 if videos feel stiff

**3-Sampler approach (High → High → Low)**
- First High: no LoRA, establishes motion
- Second High + Low: with LoRA for speed
- Apparently produces better motion than pure 2-sampler
- Not relevant now (we're not using LoRA) but worth knowing exists

### Sources
- [Darksidewalker's Definitive I2V Guide](https://civitai.com/articles/20293/darksidewalkers-wan-22-14b-i2v-usage-guide-definitive-edition)
- [Simple and Effective WAN 2.2 I2V Workflow](https://civitai.com/articles/25397/simple-and-effective-wan22-i2v-workflow)
- [WAN 2.2 I2V Basics: First Video](https://civitai.com/articles/21738/wan-22-i2v-with-or-without-acceleration-basics-first-video)
- [ComfyUI-WanMoEScheduler](https://github.com/cmeka/ComfyUI-WanMoEScheduler)
- [ComfyUI-WanMoeKSampler](https://github.com/stduhpf/ComfyUI-WanMoeKSampler)

---

## Implementation Plan Summary

Three files to change (from `plans/wan22-workflow-builder.md`):
1. `workflow_builder.py` — add `create_wan_i2v_22_workflow()`
2. `config.py` — add `wan_i2v_version: '2.2'` + `wan_i2v_22_cfg: 3.5`
3. `video_producer.py` — version branch in `_submit_segment()` ~line 192

Seed node stays at `"12"` — no change to `_submit_segment` seed logic needed.

---

## Session Progress

- [x] Read current workflow_builder.py
- [x] Write create_wan_i2v_22_workflow()
- [x] Update config.py
- [x] Update video_producer.py — version branch + forclaude keyframe extraction
- [x] Fix KeyError: KSamplerAdvanced uses noise_seed not seed (generation.py line 777)
- [x] Restart service, run test productions — confirmed working
- [ ] (Optional) Update WAN I2V manual tab in UI

## Bug Fixed During Testing

`_run_video_generation()` in generation.py tried to read `workflow[seed_node]["inputs"]["seed"]`
after generation completed. KSamplerAdvanced uses `noise_seed` not `seed` — KeyError was
swallowing silently, leaving videos in sd_output/ uncollected. Fixed with `.get()` fallback.

## Confirmed Working

Two full productions ran clean:
1. Hermione (redhead, WAN 2.2 animated the "showing cleavage" prompt with balloon physics — hilarious)
2. Knight in burning castle — cinematic, character consistent across all 10 frames, production-ready quality

forclaude keyframe extraction working automatically after every production.
