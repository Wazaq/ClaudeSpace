# Plan: WAN 2.2 I2V Workflow Builder
**Date:** 2026-03-03
**Status:** Ready to implement

---

## What We're Doing

Replacing WAN 2.1 I2V with WAN 2.2 in the production pipeline. Models are already downloaded. This is a workflow builder change — the pipeline plumbing stays the same.

---

## What's Different in WAN 2.2 vs 2.1

Confirmed from ComfyUI template `video_wan2_2_14B_i2v.json`:

| | WAN 2.1 | WAN 2.2 |
|---|---|---|
| Model files | 1 UNET (fp16) | 2 UNETs (high_noise + low_noise, fp8_scaled) |
| Sampler node | `KSampler` | `KSamplerAdvanced` × 2 |
| CLIPVision | Required (CLIPVisionLoader + Encode) | Optional — **unconnected in template** |
| VAE | wan_2.1_vae.safetensors | Same |
| CLIP | umt5_xxl_fp8_e4m3fn_scaled.safetensors | Same |
| ModelSamplingSD3 shift | 8.0 | 8.0 for high, 8.0 for low |
| Default CFG | 6.0 | 3.5 |

**The two-sampler pattern:**
- KSamplerAdvanced #1 (high_noise model): `add_noise=enable`, steps 0→N/2, `return_with_leftover_noise=enable`
- KSamplerAdvanced #2 (low_noise model): `add_noise=disable`, steps N/2→10000, `return_with_leftover_noise=disable`
- The second sampler takes the first sampler's LATENT as input

---

## Files to Change

### 1. `app/services/workflow_builder.py`

Add new function `create_wan_i2v_22_workflow()` with same signature as `create_wan_i2v_workflow()`.

**Node map (API format):**
```
"1": UNETLoader  ← wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors
"2": UNETLoader  ← wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors
"3": CLIPLoader  ← umt5_xxl_fp8_e4m3fn_scaled.safetensors, type="wan"
"4": VAELoader   ← wan_2.1_vae.safetensors
"5": LoadImage   ← init_image_path
"6": CLIPTextEncode  ← prompt, clip=["3",0]
"7": CLIPTextEncode  ← negative, clip=["3",0]
"8": ModelSamplingSD3  ← model=["1",0], shift=8.0
"9": ModelSamplingSD3  ← model=["2",0], shift=8.0
"10": WanImageToVideo  ← positive=["6",0], negative=["7",0], vae=["4",0],
                         clip_vision_output=(omit), start_image=["5",0],
                         width, height, length=num_frames, batch_size=1
"12": KSamplerAdvanced  ← model=["8",0], positive=["10",0], negative=["10",1],
                          latent_image=["10",2], add_noise="enable", seed=seed,
                          steps=steps, cfg=cfg, sampler_name="euler",
                          scheduler="simple", start_at_step=0,
                          end_at_step=half_steps, return_with_leftover_noise="enable"
"13": KSamplerAdvanced  ← model=["9",0], positive=["10",0], negative=["10",1],
                          latent_image=["12",0], add_noise="disable", seed=0,
                          steps=steps, cfg=cfg, sampler_name="euler",
                          scheduler="simple", start_at_step=half_steps,
                          end_at_step=10000, return_with_leftover_noise="disable"
"14": VAEDecode  ← samples=["13",0], vae=["4",0]
"15": VHS_VideoCombine  ← images=["14",0], fps, filename_prefix, ...
```

**Note:** Node 12 = first KSamplerAdvanced intentionally. `video_producer.py` uses `seed_node="12"` to randomize per-segment seeds. Keeping the seed node at 12 means no change needed in `_submit_segment`.

**half_steps** = `steps // 2`  (default 20 steps → 10/10 split)

**Default CFG** = 3.5 (WAN 2.2 recommendation, not 6.0)

**No CLIPVision nodes** — confirmed unconnected in official template, drop nodes 4+9 from 2.1.

### 2. `config.py`

In `AUTONOMOUS_WORKFLOW` dict, add:
```python
'wan_i2v_version': '2.2',   # '2.1' or '2.2'
```

Also add a top-level section or to AUTONOMOUS_WORKFLOW:
```python
'wan_i2v_22_cfg': 3.5,       # WAN 2.2 uses lower CFG
```

### 3. `app/services/video_producer.py`

In `_submit_segment()`, where it calls `workflow_builder.create_wan_i2v_workflow(...)`, check config and call the right builder:

```python
wan_version = config.AUTONOMOUS_WORKFLOW.get('wan_i2v_version', '2.1')
if seg_type == 'i2v' and init_image_path:
    if wan_version == '2.2':
        cfg_val = config.AUTONOMOUS_WORKFLOW.get('wan_i2v_22_cfg', 3.5)
        workflow = workflow_builder.create_wan_i2v_22_workflow(
            prompt=seg_def['prompt'],
            init_image_path=temp_filename,
            ...
            cfg=cfg_val,
            ...
        )
    else:
        workflow = workflow_builder.create_wan_i2v_workflow(...)
```

seed_node stays `"12"` — no change needed.

**Exact location in video_producer.py:** Around line 192, inside `_submit_segment()`:
```python
# Current code (replace the i2v branch):
if seg_type == 'i2v' and init_image_path:
    ...
    workflow = workflow_builder.create_wan_i2v_workflow(
        prompt=seg_def['prompt'],
        init_image_path=temp_filename,
        negative_prompt=seg_def.get('negative_prompt', ''),
        num_frames=seg_def.get('num_frames', 81),
        steps=seg_def.get('steps', 20),
        fps=seg_def.get('fps', 16),
        lora_name=seg_def.get('lora_name'),
        filename_prefix=f"prod_{prompt_id[:8]}"
    )
    seed_node = "12"
```

Replace with the version check shown above. All other args stay the same.

### 4. WAN I2V tab in UI (optional, check after pipeline works)

The WAN I2V tab in `main.js` presumably also calls a generate endpoint that builds a workflow. May need updating if it calls the I2V builder directly. Check after pipeline is confirmed working.

---

## What NOT to Change

- `create_wan_t2v_workflow()` — WAN 2.2 T2V models were not downloaded, keep using 2.1 T2V
- `video_producer.py` T2V path — unaffected
- Pipeline orchestration, review logic, checklist generation — all unchanged

---

## Implementation Order

1. Write `create_wan_i2v_22_workflow()` in workflow_builder.py
2. Add `wan_i2v_version: '2.2'` to config.py
3. Update `_submit_segment()` in video_producer.py to branch on version
4. Restart service, run a test production
5. If test passes, optionally update the WAN I2V manual tab in UI

---

## Open Questions

- Does `clip_vision_output` being unconnected cause an error or is it truly optional? The template omits it — should be fine, but first test run will confirm.
- Community posts may have production notes on the 2.2 two-model workflow. Worth checking before implementing if there are known gotchas (shift values, step split ratio, etc.).

---

## Files NOT Needing Changes

- `production_planner.py` — no change
- `video_reviewer.py` — no change
- `production.py` route — no change
- `templates/index.html` — no change (unless UI tab needs updating)
