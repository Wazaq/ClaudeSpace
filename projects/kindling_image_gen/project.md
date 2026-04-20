# Kindling Image Generation — Project Reference

*Last updated: 2026-04-18*

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

## Services — TWO SERVICES, RESTART BOTH WHEN IN DOUBT

| Service | What it is | Port |
|---------|-----------|------|
| `kindling` | Flask API wrapper (our code) | 5000 |
| `comfyui` | ComfyUI backend (the actual inference engine) | 8188 |

**⚠️ This bites us constantly:** Restarting `kindling` does NOT restart `comfyui`. If you install new custom nodes, update models, or change anything ComfyUI needs to load at startup — restart BOTH:
```bash
sudo systemctl restart comfyui.service
sudo systemctl restart kindling
```
ComfyUI takes ~15 seconds to fully start before kindling is usable.

**Logs:**
- `sudo journalctl -u kindling -f`
- `/tmp/comfyui.log` — ComfyUI startup output (custom node load errors, import failures)

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
| `ComfyUI-Impact-Pack` | FaceDetailer etc. — installed but FaceDetailer not yet wired in (see TODO) |
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

### FaceDetailer — NOT YET ACTIVE
- Impact Pack installed (V8.28.2), `ultralytics` + `onnxruntime` pip packages installed
- Blocker: `UltralyticsDetectorProvider` node doesn't exist in this Impact Pack version
- Fix: update Impact Pack → `UltralyticsDetectorProvider` will exist → wire into SDXL + img2img workflows
- See TODO for full context

---

## Production Pipeline — Key Files

| File | Purpose |
|------|---------|
| `app/routes/production.py` | All production endpoints (start, chat, plan, chain, resume, status) |
| `app/services/video_producer.py` | `run_production()` — the main generation loop |
| `app/services/production_planner.py` | Intent extraction, script, plan, checklist generation |
| `app/services/job_store.py` | SQLite persistence (`productions/kindling_jobs.db`) |
| `app/services/session_cache.py` | diskcache-based session storage (24h TTL) |
| `static/js/production.js` | Frontend production UI state machine |
| `templates/index.html` | All production phase HTML (chat/sample/script/plan/producing/result) |

### Production Flow
Chat → Intent → Quick Sample (optional) → Script (writer layer) → Plan → Generation → Review loop → Stitch → Result

### Scene Chaining (done 2026-04-18, improved 2026-04-20)
`POST /production/chain/<id>` — extracts last frame, saves to `productions/chains/`, seeds new session with `per_segment_inits={1: frame_path}`. Segment 1 auto-generates as I2V.

**Chain context inheritance (2026-04-20):** Parent intent (`characters`, `style`, `mood`, `scene`) now saved to DB as `intent_json` when a production starts. On chain, that intent is loaded and injected as locked "CONTINUATION CONTEXT" into both `extract_intent()` and `generate_narrative_script()` — writer and planner inherit the character spec automatically. Opening message tells the user what character they're continuing so they don't re-describe. `chained_from` field in `production_jobs` DB tracks lineage.

**Merge with Parent (2026-04-20):** `POST /production/merge/<id>` stitches parent + child final videos into one MP4. "Merge with Parent" button on result screen (shown when `chained_from` is set — pulled from DB into status response). Button also available from library via "Chain" button on each card.

**Library Chain button (2026-04-20):** Each library card with a completed video shows a "Chain" button. Calls chain endpoint and switches to production chat phase.

**Library fuzzy slug matching (2026-04-20):** Plan file slug may be truncated differently from video filename. Now matches on the 8-char production ID suffix (e.g. `_4fef4813`) instead of exact stem match — fixes videos not appearing in library.

### SQLite Persistence (done 2026-04-18)
`productions/kindling_jobs.db` — persists job + segment state on every change. Interrupted jobs detected at startup. Resume banner in UI. Resume picks up from last `approved` or `needs_review` segment.

**`intent_json` column (2026-04-20):** Parent intent dict stored as JSON on job creation. Used by chain endpoint for context inheritance. DB migration runs on startup (ALTER TABLE IF NOT EXISTS pattern).

**Resume `prev_video_path` fix (2026-04-20):** On interrupt+resume, `run_production()` now reconstructs `prev_video_path` from the last completed segment's filename on disk before starting the resumed segment. Previously, `init_from_previous` would silently skip (no prev path) causing T2V drift on the first resumed segment.

### Auto-Checkpoint Anchoring
Every N segments (default 4, `auto_checkpoint_interval` in config), saves last frame as checkpoint and forces I2V from it at group boundaries. Prevents cumulative visual drift on long productions.

### Checklist / Banned Phrases
`_CHECKLIST_BANNED_PHRASES` in `production_planner.py` — includes transitional motion phrases (pulls open, standing up, sitting down, etc.). Checklist auto-fails segments missing character specifics (hair, eyes, body). **Known gap:** for chained segments, I2V init image provides the character spec — checklist shouldn't flag "unspecified" when a chain frame exists.

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
