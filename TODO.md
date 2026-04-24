# Master TODO
*One list. Everything goes here. Add it before you forget it.*

---

## Kindling Image Gen

### Code Health (stabilize before adding more features)
- [x] **Consistent logging system** — done 2026-04-20. `app/services/logger.py` writes to `productions/kindling.log`, rotates to `.log.1` on startup, also writes to stderr (journald). 151 print() calls → log.info/warning/error/debug across 21 files. `/api/logs?lines=N` endpoint in status.py returns last N lines.
- [x] **Split `workflow_builder.py`** — done 2026-04-20. 1437 lines → 75-line turnstile + `app/services/workflows/sdxl.py`, `wan.py`, `flux.py`, `post_processing.py`. All 9 importers unchanged. Bonus: fixed `create_wan_i2v_22_svi_workflow` missing `return workflow` (was returning None in production).
- [x] **Audit `video_editor.py`** — done 2026-04-21. Already split (turnstile + 5 modules in `editor/`). No action needed.
- [x] **Extract `video_stitcher.py` from `video_producer.py`** — done 2026-04-21. `stitch_segments`, `_stitch_with_xfade`, `_get_video_duration` extracted to `app/services/video_stitcher.py`. `video_producer.py` and `production.py` updated to import from new module.
- [x] **Move `simplify_checklist_for_validation` out of `automation.py`** — done 2026-04-21. Moved to `conversational_ai.py`. `automation.py` updated to import from there.
- [ ] **Organize sd_output directory** — all intermediate/raw ComfyUI output dumps into `sd_output/`, final videos go to completed folder. Intermediate files should be cleaned up or organized into a temp/working subdirectory so `sd_output/` doesn't accumulate indefinitely.
- [ ] **Extract `translate_prompt` and `cascade_appearance` LLM logic from `editing.py`** — both routes inline raw Ollama API calls (~80 lines each). Same pattern as the checklist fix. Move to a service (likely a new `app/services/prompt_translator.py`).
- [x] **Split `main.js`** — done 2026-04-20. 1245 → 1005 lines. Extracted `settings.js` (system status, settings load/save) and `ui-setup.js` (prompt improvement, image analysis, sliders). `public.js` skipped — public interface not actively in use.

### Story Pipeline
- [x] **Register editor routes** — already done. `editing_bp` imported and registered in `api_wrapper.py` lines 36+75. `editing.py` is fully implemented.
- [x] **Script editing route** — already done. `generate_plan` accepts optional `script` override in body (line 318). Frontend shows script in editable textarea; `approveScript()` passes it to plan generation. Full round-trip works.
- [ ] **Story Mode: narrative editing** — Story Mode only has 4 routes (start, chat, generate_preview, build_plan). No way to refine ScriptMaster output after the fact. Add `/story/edit_script` or allow re-chat before build_plan.
- [x] **Writer always generates 2 beats** — fixed 2026-04-22. `total_duration_seconds` was hardcoded to 10 in intent JSON template (always 2 beats). Added `num_segments` field to intent extraction — model infers from conversation ("6 segments" → 6). Writer and planner both prefer `num_segments` over duration division. Validated: 6-beat script, 6-segment production, 28s clean run.
- [x] **Configurable script writer model** — done 2026-04-22. Added `script_writer_model` key to `AUTONOMOUS_WORKFLOW` in config.py (defaults to None = use conversational_model). Set to e.g. `'qwen3.5:35b'` for non-kink productions. Writer logs which model it's using.
- [ ] **Sample as visual contract** — approved sample prompt should be passed to the script writer as a style reference. Currently sample and production are unrelated; production ignores the sample's atmosphere/lighting/composition entirely. On sample approval, retrieve the prompt text from the job dict (via `session.sample_prompt_id`) and pass it to `generate_narrative_script()` and `generate_plan()` as a locked style anchor. If sample is skipped, use intent only as today.
- [x] **Character consistency validation** — done 2026-04-21. `review_segment()` accepts optional `reference_frame`; when provided, prepends it to the vision model images and adds a consistency checklist item. `video_producer.py` locks S1's first frame after approval and passes it to all subsequent segment reviews.
- [x] **Persist production conversations** — already done. `session_cache.py` uses diskcache with 24h TTL, persisted to `.cache/sessions/`. Sessions survive restarts.
- [ ] **SVI auto-enable** — Blocked: T5 encoder OOMs with dual-UNET fp8 scaled setup (~25GB UNETs + 6GB T5 > 32GB). Revisit if SVI workflow rewritten to use CLIPLoader instead of LoadWanVideoT5TextEncoder (which doesn't support fp8 scaled). `svi_mode` reverted to False 2026-04-21.
- [x] **ComfyUI OOM kills** — fixed 2026-04-22. Root cause: qwen3-vl (vision reviewer) stayed loaded in Ollama VRAM during next segment generation. Added `_unload_vision_model()` call after every `review_segment()` in `video_producer.py`. Validated: 6-segment run, no interruptions.
- [x] **Prompt polish failure logging** — done 2026-04-21. Changed silent fallback to `log.warning` for both empty-response and exception cases in `_polish_prompt()`.

### UI Cleanup
- [x] **Remove quick presets** from T2I — done 2026-03-27
- [x] **Remove Inpainting tab** — done 2026-03-27, frontend + backend fully removed
- [x] **Remove Video tab** — done 2026-03-27, frontend + backend fully removed
- [x] **Sticky frames bug** — fixed 2026-03-27 (root cause: broken HTML structure, sub-panels were outside image-panel in DOM)

### Pipeline Features
- [ ] **FaceDetailer (face quality improvement)** — Impact Pack installed, but `UltralyticsDetectorProvider` node doesn't exist in current version (V8.28.2). Fix: update Impact Pack to a newer version that includes it, then add FaceDetailer nodes back to `create_sdxl_workflow` and `create_img2img_workflow` in `workflow_builder.py`. The YOLO model to use: `face_yolov8m.pt` in `models/ultralytics/bbox/`. ultralytics + onnxruntime pip packages already installed.
- [ ] **Smart cascade regen** — when upstream segment changes, auto-regen downstream segments
- [x] **Auto-checkpoint anchoring** — done 2026-04-15. Every N segs (default 4, `auto_checkpoint_interval` in config), saves last frame as checkpoint. Forces I2V from checkpoint at group boundaries (segs 5, 9, 13...). Logs 🎯 in production output. Set to 0 to disable.
- [x] **Segment init/final frame thumbnails** — done 2026-04-15. First+last frame extracted after each segment completes, stored in job state, shown as small thumbnails on segment cards in production view. Uses existing segment_frame endpoint.
- [x] **Visual prompt translator layer** — done 2026-04-15. `_polish_prompt()` in video_producer.py, runs before retry loop per segment. Uses translate_model. `polish_prompts: True` in config to disable. Falls back silently on failure.
- [x] **VRAM monitoring / memory pressure indicator** — done 2026-04-15. pynvml (nvidia-ml-py) in status.py, progress bar in settings tab. Green/yellow/red at 60%/85%. Polls every 10s. Shows OS-level usage (includes ComfyUI process).
- [x] **SQLite state persistence + resume** — done 2026-04-18. `productions/kindling_jobs.db` persists job + segment state on every change. Interrupted jobs detected at startup, banner shown with Resume button. Resume picks up from last approved segment (session survives via diskcache 24h TTL). New endpoints: `/production/interrupted`, `/production/resume/<id>`.
- [x] **WAN aspect ratio investigation** — done 2026-04-15. Root cause: I2V workflow calls in _submit_segment never passed width/height, falling back to 512×512 defaults. Added `wan_video_width: 832` and `wan_video_height: 480` to config. All I2V and T2V calls now use config values.
- [x] **Writer layer** — done 2026-04-16. Narrative script stage fires after sample approval. Uses `Beat N:` format; beat count determines segment count. Planner treats script as primary source.
- [x] **Plan generation fix for large segment counts** — done 2026-04-16. format_json=False, brace-depth JSON extraction, timeout = max(180, segments × 25). Fixes failures on 7+ segment plans.
- [x] **Crossfade stitching** — done 2026-04-16. stitch_segments() defaults to 0.4s xfade via ffmpeg, falls back to plain concat on failure. Softens hard cuts between segments.
- [x] **Lightbox for thumbnails** — done 2026-04-16. Click any first/last frame thumbnail → full-size overlay. Escape or click to close.
- [x] **Checklist banned phrases update** — done 2026-04-18. Added transitional motion phrases (pulls open, standing up, sitting down, etc.) to `_CHECKLIST_BANNED_PHRASES` in `production_planner.py`.
- [x] **Scene chaining** — done 2026-04-18, improved 2026-04-20. Chain context inheritance (parent intent locked into writer/planner), `chained_from` DB field, "Merge with Parent" button, library Chain button, fuzzy slug matching, resume `prev_video_path` fix.
- [ ] **WAN 2.7 weights** — watch Wan-AI HuggingFace org; when weights drop, wire in subject referencing (first+last frame API already exists). Currently API-only.
- [ ] **WAN 2.2 NSFW LoRAs** — Brent was browsing on HuggingFace, download to ComfyUI/models/loras/ when ready.
- [x] **LoRA scanner utility** — done 2026-04-20. `scan_loras.py` reads safetensors metadata + tensor keys to categorize by base model, detects HIGH/LOW pairs, flags missing partners. Run anytime to audit the collection.
- [ ] **Multi-LoRA support** — workflow_builder.py currently wires in only a single LoRA node. Support a `loras: list[{name, strength}]` chain (nodes output feeds into next). Required for combining HIGH+LOW variant pairs and stacking effect LoRAs. API, production pipeline, and UI all need updates.
- [ ] **Add sounds** to video productions
- [ ] **Add voices** to video productions
- [ ] **AnimateDiff pipeline** — anime-style video generation. Separate pipeline from WAN, uses AnimateDiff motion modules + anime checkpoint (animagineXLV31 already installed). Full checklist below.
  - [ ] Install **ComfyUI-AnimateDiff-Evolved** custom node (`cd ComfyUI/custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git`)
  - [ ] Download a **motion module** — must be SDXL-compatible. Good candidates: `animatediff_lightning_4step_sdxl`, anything by ByteDance for SDXL. Search CivitAI > Motion filter. Goes in `ComfyUI/models/animatediff_models/`
  - [ ] Verify **animagineXLV31** works as base (already installed in checkpoints/)
  - [ ] May need **SDXL VAE** — check if current ae.safetensors works or if a dedicated SDXL VAE is needed
  - [ ] Build `create_animatediff_workflow()` in `workflow_builder.py` once models are confirmed
  - [ ] Wire into Kindling API (new route or extend existing)
- [ ] **LoRA training pipeline** — when a recurring character earns it. musubi-tuner, 32GB handles local I2V. IAMCCS-nodes for ComfyUI loading.

### Curiosity / Research
- [x] **How do deepfakes work?** — done 2026-03-31, covered face swap vs diffusion-based approaches, pipeline, and nudify accuracy limits
- [ ] **Narrative prompting experiment** — Kindroid uses pure prose prompts (mood, atmosphere, sensory detail, no SD keywords) and gets strong results. Test: strip the keyword boilerplate from Kindling's prompt polisher and let the LLM write narrative-style instead. Compare output quality. Hypothesis: narrative density may translate better to WAN's video generation than technical keyword lists.

---

## Ember

- [x] **Image generation reliability** — fixed 2026-03-27. Missing `tool_call_id` in tool result messages meant Ollama couldn't match results back to calls. Model stopped calling tools after accumulating malformed history. 5/5 after fix.
- [x] **Bot not responding** — fixed 2026-03-30. `.env` had a period and inline comment included in the model name value (`Qwen3.5:35b. ## Normal...`). Ollama returned 404. Fixed to `qwen3.5:35b`.

---

## Spot

- [ ] **Research using Spot with OpenClaw** — investigate integration/usage
- [ ] **Get back to working sessions with Spot** — he's been heartbeating, needs actual use
- [x] **Spot visibility fix** — done 2026-03-27, now shows first line of result only instead of raw content dump
- [x] **VISIBILITY_TOOLS review** — confirm the set is right after the first-line display fix. Observe in Discord.

---

## STFC Assistant

- [ ] **Finish fleshing out the web app**
- [x] **Clean up My State** — card layout done, two-section buildings (Current/Maxed) done 2026-04-09
- [ ] **Auto-refresh on save** — reload building sections after saving without full page refresh
- [ ] **Event help** (Myla's idea) — pull daily event from site, tell you what to focus on (who/what ship/crew). Needs deep dive research.
- [ ] **AI state updater** — AI helps update your state (e.g. "Max research up to X" marks everything prior complete). Good onboarding tool.
- [ ] **Building prereq traversal** — "what do I need to reach Ops 64?" walks the dependency tree, surfaces everything not yet at required level in order.

### Data Quality (audit needed)
- [ ] **building_id_map.json audit** — extended loader pulls levels 61-80 from data.stfc.space using ID map. HOLODECK shows max level 80 in DB but real cap is 30 — suggests ID mapping errors attaching wrong data to wrong buildings. Need to verify a sample of buildings against actual game/site data. Widespread errors suspected.
- [ ] **"Mark as maxed" override** — UI toggle to manually flag a building as maxed regardless of DB data, for cases where dataset is wrong or game-imposed caps differ.

### Missing Buildings (data gaps to revisit)
- [ ] **Dive Bar** — not in community dataset, newer building. Add manually or wait for data update.
- [ ] **Court of Q** — older building, never in community dataset. Needs manual add or better data source.
- [ ] **District 56** — not in community dataset. Needs manual add or better data source.
- [ ] **The War Room** (and associated buildings) — entire section missing from community dataset. Investigate better data source.
- [ ] **Signal Observatory** — newer building, missing from dataset.
- [ ] **Outpost Control Center** — missing from dataset.
- [ ] **Transogen Forge** — missing from dataset.
- [ ] **Recon Locus** — missing from dataset.
- [ ] **DTI Headquarters** — missing from dataset. (Don't tell Trump)
- [ ] **The Nova Squadron** — missing from dataset.
- [ ] **Independent Archives** — missing from dataset.

---

## WazzieStocks

- [x] **Shut it down** — done 2026-03-27, both services stopped and disabled

---

## Neural Swarm

- [x] **Disable morning digest** — done 2026-03-27, task commented out in bot.py. YNAB email processing unaffected.
- [ ] **YNAB agent tweaks** — working well, no specific ideas yet. Revisit when something surfaces.
- [ ] **NSA: Etsy emails** — add Etsy email handling
- [ ] **NSA: Jewel-Osco** — investigate $0.89 transaction (wrong amount? fee? fuel points?)
- [x] **NSA: Nicor Gas** — done 2026-04-10, dedicated rule routes to Venture One with Nicor/Gas category
- [x] **NSA: Torrid** — done 2026-04-10, covered by order lifecycle skip patterns
- [ ] **NSA: Warby Parker** — add to skip/ignore list, paid via HSA
- [ ] **NSA: VCA Careclub** — route to Venture One
- [ ] **NSA: Anthropic** — route to Venture One
- [x] **Brent: update PS Store payment card** — done 2026-04-10
- [ ] **NSA: Apple** — route to Capital One Venture One
- [ ] **YNAB agent: exclude public dividends** — filter these out from processing
- [ ] **YNAB agent: correct account assignment** — figure out how to put transactions on the right account
- [x] **YNAB agent: stop double tracking** — done 2026-04-10. Added skip_subject_patterns for arriving/ready for pickup/drive-up/order update/preparing. Only order confirmation + refund emails create transactions.
- [x] **YNAB agent: Target cleanup** — done 2026-04-10. Covered by drive-up ready + order status update patterns above.
- [ ] **New swarm idea** — no direction yet, explore when inspiration hits

---

## Claude Session History (Vector Search)

- [x] **Index JSONL session logs into vector DB** — done 2026-03-30. 8800+ chunks, nomic-embed-text, SQLite at `~/ClaudeSpace/tools/session-search/index.db`
- [x] **Build `/search-history` skill** — done 2026-03-30. Semantic search, top-5 results, clean text output.
- [ ] **Decay on the vector index** — significance score per chunk, decay over time, evict low-significance entries from search index (source JSONL files stay on disk).

---

## Lens (Agentic Code Reviewer)

- [x] **followup.md log** — done 2026-04-15, full Q&A written to `reviews/<session>/followup.md` during loop
- [x] **Increase minimum file reads** — done 2026-04-15, `--min-files` CLI arg (default 10)
- [x] **Model roleplay bleed fix** — done 2026-04-15, truncate at `<|im_end|>`, strip remaining `<|im_...|>` tokens in stream_ollama()
- [ ] **Post-review summary commit** — after a review session, auto-commit the review + scratch + notebook to the target project's repo as a dated review artifact

---

## Someday / Maybe

- [ ] **RIFE on fast-action content** — test frame interpolation on sharp quick motion to see if 32fps is worth it
- [ ] **Research Kindroid: Personal AI** — investigate what it is, how it works, relevance to our projects

---

*Last updated: 2026-04-23*
