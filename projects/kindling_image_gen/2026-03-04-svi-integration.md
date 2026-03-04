# SVI 2.0 Pro Integration — Confirmed Working

**Date:** 2026-03-04
**Status:** Shipped and confirmed in production

---

## What We Built

Integrated SVI 2.0 Pro (Stable Video Infinity) into the WAN 2.2 I2V multi-segment pipeline to solve the snap-back problem. Previously, every segment's motion anchored to the first frame's pose because the model only sees an image — it has no idea what direction things were moving. SVI fixes this by passing raw latent tensors (`prev_samples`) between segments, carrying motion vectors forward in latent space.

## Files Changed

- `config.py` — added `svi_mode` flag (currently `True`)
- `app/services/workflow_builder.py` — added `create_wan_i2v_22_svi_workflow()`
- `app/services/comfyui_client.py` — added `get_output_latent_filename()`
- `app/services/video_producer.py` — latent chaining in `run_production()` + `_submit_segment()`
- `ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/__init__.py` — importlib.util registration of SVI2Pro-FLF nodes

## Key Technical Details

**Node architecture (SVI workflow):**
- `WanVideoModelLoader` replaces `UNETLoader` — loads HIGH/LOW UNETs with LoRA
- `WanVideoSampler` ×2 replaces `KSamplerAdvanced` ×2 — dual-UNET step split
- `WanVideoSVIProEmbeds` builds image embeds from anchor image + optional `prev_samples`
- `WanCutLastSlot` trims 1 temporal slot before saving (required by SVI Pro protocol)
- `SaveLatent` saves trimmed latent to ComfyUI output dir after each segment
- `LoadLatent` with `[output]` annotation loads prior segment's latent for chaining

**SVI2Pro-FLF discovery:** The `ComfyUI-Wan-SVI2Pro-FLF` directory lives inside WanVideoWrapper, not as a standalone custom node. Hyphenated directory name prevents normal Python package import. Solution: `importlib.util.spec_from_file_location()` to load `nodes.py` directly by path, added to WanVideoWrapper's `__init__.py`.

**Latent routing:** ComfyUI's annotated filepath format (`"filename.latent [output]"`) routes `LoadLatent` to the output directory instead of input directory, enabling segment-to-segment chaining without manual file copies.

**LoRA files:** Both SVI LoRAs were already present when work began:
- `SVI_v2_PRO_Wan2.2-I2V-A14B_HIGH_lora_rank_128_fp16.safetensors`
- `SVI_v2_PRO_Wan2.2-I2V-A14B_LOW_lora_rank_128_fp16.safetensors`

## Test Result

5-segment story mode production (busty Korean woman beach approach). Frame analysis at all 4 segment boundaries showed clean motion continuity — no snap-back to initial pose. Most dramatic boundary (seg 4→5): character in deep forward lean in final frame of seg 4; seg 5 picks up from same forward lean position rather than resetting to initial upright running pose.

Brent's verdict: "very little snap back, nothing jarring"

## Commit

`b85e9a8` — kindling-image-gen master
