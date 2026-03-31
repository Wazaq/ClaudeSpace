# Kindling Image Generation — Project Reference

*Last updated: 2026-03-31*

---

## What It Is

AI image/video generation system built on ComfyUI. Brent interacts via a Flask API wrapper — he never touches ComfyUI directly. Discord bot interface via Waifu (separate project).

---

## Key Paths

| What | Path |
|------|------|
| Root | `/home/bdwatkin/kindling-image-gen/` |
| API wrapper | `api_wrapper.py` |
| Workflow builder | `app/services/workflow_builder.py` |
| Generation logic | `app/services/generation.py` |
| Settings | `settings.json` |
| Model capabilities | `model_capabilities.json` |
| ComfyUI root | `ComfyUI/` |
| Models | `ComfyUI/models/` |
| Custom nodes | `ComfyUI/custom_nodes/` |
| Venv | `ComfyUI/venv/` |
| MCP server | `mcp_server.py` |

---

## Service

- **Name:** `kindling` (systemd, system-level)
- **Port:** 5000
- **Restart:** `sudo systemctl restart kindling`
- **Logs:** `sudo journalctl -u kindling -f`

---

## Models Installed

### SDXL Checkpoints (`ComfyUI/models/checkpoints/`)
| File | Notes |
|------|-------|
| `juggernautXL_ragnarokBy.safetensors` | Primary realism model |
| `reapony_v90.safetensors` | Good realism results |
| `noobaiXLNAIXL_epsilonPred11Version.safetensors` | Anime/illustrated |
| `animagineXLV31_v31.safetensors` | Anime |
| `ponyDiffusionV6XL_v6StartWithThisOne.safetensors` | Pony style |
| `waiIllustriousSDXL_v160.safetensors` | Illustrated |
| `fluxedUpFluxNSFW_70FP16.safetensors` | High realism, can go off-rails |

### Flux (`ComfyUI/models/unet/`)
| File | Notes |
|------|-------|
| `fluxedUpFluxNSFW_70FP16.safetensors` | Flux NSFW model |

### WAN Video (`ComfyUI/models/diffusion_models/`)
| File | Notes |
|------|-------|
| `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` | I2V high noise |
| `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` | I2V low noise |
| `wan2.2_t2v_14B_fp8_scaled.safetensors` | T2V standard |
| `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` | T2V high noise |
| `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` | T2V low noise |
| `wan2.2_animate_14B_fp8_scaled.safetensors` | Animate variant |
| `wan2.1_i2v_480p_14B_fp16.safetensors` | Legacy 2.1 |
| `wan2.1_t2v_14B_fp16.safetensors` | Legacy 2.1 |

### LoRAs (`ComfyUI/models/loras/`)
| File | Notes |
|------|-------|
| `SVI_v2_PRO_Wan2.2-I2V-A14B_LOW_lora_rank_128_fp16.safetensors` | WAN SVI v2 Pro |
| `SVI_v2_PRO_Wan2.2-I2V-A14B_HIGH_lora_rank_128_fp16.safetensors` | WAN SVI v2 Pro |
| `NSFW_master.safetensors` | NSFW quality |
| `NsfwPovAllInOneLoraSdxl-000009.safetensors` | NSFW POV |
| `nudify_xl_lite.safetensors` | Nudify |
| `wan_i2v_pov_blowjob_v1.2.safetensors` | WAN POV |
| `Asian_Bimbo.safetensors` | Style LoRA |

---

## Custom Nodes

| Node | Purpose |
|------|---------|
| `ComfyUI-Impact-Pack` | FaceDetailer, segmentation, SAM2 *(added 2026-03-31)* |
| `ComfyUI-WanVideoWrapper` | WAN video generation |

---

## Workflow Architecture

Workflows are built programmatically in `workflow_builder.py` — ComfyUI never opened manually.

### Current Workflows
| Function | Type | Notes |
|----------|------|-------|
| `create_sdxl_workflow()` | T2I | SDXL checkpoint, optional LoRA, **FaceDetailer always-on** *(2026-03-31)* |
| `create_img2img_workflow()` | I2I | SDXL, optional LoRA, **FaceDetailer always-on** *(2026-03-31)* |
| `create_flux_workflow()` | T2I | Flux via UNETLoader + separate CLIP/VAE |
| `create_wan_i2v_workflow()` | I2V | WAN 2.1, 14B, 480p |
| *(WAN 2.2 variants)* | I2V/T2V | High/low noise variants in generation.py |

### FaceDetailer Config (added 2026-03-31)
- Detector: `face_yolov8m.pt` (YOLO, in `models/ultralytics/bbox/`)
- Runs automatically — detects face then rerenders at 0.5 denoise if found
- No face = image passes through unchanged
- Applied to: SDXL and img2img workflows only (not Flux, not WAN)

---

## Known Issues / History

- **2026-03-30:** Ember fix — `.env` had period + inline comment in model name value
- **2026-03-27:** Inpaint + Video tabs removed from frontend (backend already done, frontend partially cleaned)
- **2026-03-27:** Sticky frames fixed (HTML structure — sub-panels were outside image-panel in DOM)
- **2026-02-28:** WAN 2.2 upgrade (from 2.1)
- **2026-03-04:** SVI LoRA integration

---

## TODO (from master TODO)

- [ ] Smart cascade regen (upstream segment change → auto-regen downstream)
- [ ] WAN aspect ratio investigation ("I want to do a" came out boxed)
- [ ] Add sounds to video productions
- [ ] Add voices to video productions
- [ ] LoRA training pipeline (musubi-tuner when a character earns it)
- [ ] Frontend JS/HTML cleanup (inpaint + video tabs still in frontend — see 2026-03-27 handoff for exact line numbers)
