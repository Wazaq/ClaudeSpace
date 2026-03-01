# Session Handoff: WAN Video + Production Pipeline Planning
**Date:** 2026-02-28
**Next session:** Continue in Plan Mode for Production Pipeline

---

## What We Built Today

### WAN 2.1 I2V — Fully Working
- `create_wan_i2v_workflow()` in `workflow_builder.py`
- `/generate_wan_video` route in `generation.py`
- UI: WAN I2V sub-tab in Video tab, image upload/preview, LoRA dropdown, elapsed timer
- Fixed: `start_image` (not `image`), seed_node param, rate limiter exemption on `/video_status`

### WAN 2.1 T2V — Built, Pending Model
- `create_wan_t2v_workflow()` in `workflow_builder.py` (uses `EmptyHunyuanLatentVideo`)
- `/generate_wan_t2v` route in `generation.py`
- UI: WAN T2V sub-tab in Video tab
- Model downloading: `wan2.1_t2v_14B_fp16.safetensors` (~35GB, started ~22:16 CST, ETA 70m)

### UI Restructure
- Image tab now has sub-tabs: Text to Image / Image to Image / Inpainting
- Video tab now has sub-tabs: CogVideoX T2V / WAN I2V / WAN T2V
- Sub-tab pattern is extensible — easy to add more

### Service Fix
- All services are SYSTEM-level (`/etc/systemd/system/`), NOT `--user`
- Changed api-wrapper log path to `~/.local/log/api_wrapper.log` (user-owned)
- Never use `systemctl --user` for these services

---

## The Big Vision: Conversational Video Production Pipeline

Brent described his end-to-end dream:

```
You (conversational)
  → Intent Agent       — parses scene/style/length, decides T2V vs I2V
  → Quick Sample       — low steps, short clip ("is this the vibe?")
  → Brent approves/redirects
  → Plan Agent         — writes full production plan (segments, prompts, models, LoRAs)
  → Creation Agent     — executes plan segment by segment
    ↔ Review Agent     — checks each segment against plan, rejects/retries if off
  → Stitch Agent       — combines approved segments
  → Output             — /productions/ folder (separate from sd_output)
```

---

## Research Findings (Pre-done for plan mode)

### Vision Models Available in Ollama
- `qwen3-vl:latest` (8.8B, 6.1GB) — **best for Review Agent**, fast, capable
- `qwen3-vl:32b` (20.9GB) — premium option if quality needs it
- `llama3.2-vision:11b` (7.8GB) — solid fallback
- `llava:13b` (8.0GB) — established, proven

**Recommendation:** `qwen3-vl:latest` for the review loop (speed matters), `qwen3-vl:32b` for final quality check if desired.

### Existing Infrastructure to Reuse
The automation system (`app/routes/automation.py`) already has the exact pattern:
- `conversational_ai` — Ollama LLM chat
- `vision_analyzer` — VLM image validation via base64
- `session_cache` — conversation state
- `comfyui_client` — workflow execution

We're **extending** this system for video, not building from scratch.

### Stitch Endpoint — Ready
`/stitch_videos` POST — takes `video_files` array + `output_filename`, uses FFmpeg concat (lossless, fast). Requires files to be in `OUTPUT_DIR`. Works well.

### Productions Folder
Does NOT exist. Needs: `/home/bdwatkin/kindling-image-gen/productions/`
- Subdirs: `productions/completed/`, `productions/segments/`, `productions/plans/`

### LoRAs Available
- `wan_i2v_pov_blowjob_v1.2.safetensors` — WAN I2V specific
- `NSFW_master.safetensors`, `nudify_xl_lite.safetensors`, `NsfwPovAllInOneLoraSdxl-000009.safetensors`, `Asian_Bimbo.safetensors` — SDXL
- `Hand-Painted_2d_Seamless_Textures-000007.safetensors` — general

---

## Key Gaps to Address in Planning

1. **Intent parsing** — how does the AI decide T2V vs I2V from description?
2. **Plan document format** — what does the production plan look like? JSON? Markdown?
3. **Review Agent for video** — vision_analyzer works on images; need to extract key frames from video for review
4. **Segment-to-segment coherence** — how do we keep style/character consistent across segments?
5. **Productions folder** — structure, metadata, naming convention
6. **Where does this live** — new automation sub-tab? Separate "Productions" tab? Separate route module?

---

## Next Session Instructions

**Start in Plan Mode** for the Production Pipeline.

Key decisions to make in planning:
1. Where does the pipeline UI live (new tab vs extend automation)?
2. Plan document format
3. Frame extraction approach for video review (ffmpeg thumbnail?)
4. Segment coherence strategy (I2V chaining? consistent seed? LoRA?)
5. Productions folder structure

The automation system is the right base. Read `app/routes/automation.py` and `app/services/vision_analyzer.py` first to understand the existing pattern before designing the extension.

---

## Commits Today
- `8aa78b3` — WAN I2V initial implementation
- `3e45399` — WAN I2V UI improvements (elapsed timer, LoRA dropdown, rate limiter fix)
- `a1d7f7f` — UI restructure (image/video sub-tabs)
- `fc3b433` — WAN T2V support added
