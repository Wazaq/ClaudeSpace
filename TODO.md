# Master TODO
*One list. Everything goes here. Add it before you forget it.*

---

## Kindling Image Gen

### UI Cleanup
- [x] **Remove quick presets** from T2I — done 2026-03-27
- [x] **Remove Inpainting tab** — done 2026-03-27, frontend + backend fully removed
- [x] **Remove Video tab** — done 2026-03-27, frontend + backend fully removed
- [x] **Sticky frames bug** — fixed 2026-03-27 (root cause: broken HTML structure, sub-panels were outside image-panel in DOM)

### Pipeline Features
- [ ] **FaceDetailer (face quality improvement)** — Impact Pack installed, but `UltralyticsDetectorProvider` node doesn't exist in current version (V8.28.2). Fix: update Impact Pack to a newer version that includes it, then add FaceDetailer nodes back to `create_sdxl_workflow` and `create_img2img_workflow` in `workflow_builder.py`. The YOLO model to use: `face_yolov8m.pt` in `models/ultralytics/bbox/`. ultralytics + onnxruntime pip packages already installed.
- [ ] **Smart cascade regen** — when upstream segment changes, auto-regen downstream segments
- [ ] **Auto-checkpoint anchoring** — for long productions, every N segments (configurable, default 3-4) explicitly reset the drift baseline by using the rendered last frame as the new anchor instead of always chaining back to the original sample. Prevents cumulative drift on 10+ segment productions. Currently doable manually via per-segment inits in edit view but needs automation.
- [ ] **Segment init/final frame thumbnails** — show first and last frame of each segment as small thumbnails on the segment card during production. Lets you monitor character drift in real time without digging in sd_output. Keyframe extraction already exists (forclaude/), just needs an endpoint to serve per-segment first/last frames and UI to display them as cards complete.
- [ ] **Visual prompt translator layer** — polish_prompt() pass between plan generation and ComfyUI submission. Takes human-readable emotional/narrative language ("feels happy") and converts to WAN-legible visual descriptors ("wide smile, bright eyes, slight head tilt, relaxed shoulders"). Focused system-prompted LLM call, comma-separated output, single clear action enforced. Fits in video_producer.py before segment send.
- [ ] **VRAM monitoring / memory pressure indicator** — real-time VRAM usage display in the UI. Show current usage vs 32GB, warn when approaching limits (especially during dual-UNET WAN 2.2 workflows). pynvml or nvidia-smi polling. Good place: status bar or sidebar widget in the production UI.
- [ ] **SQLite state persistence** — production sessions and plan state currently in-memory only, lost on restart. SQLite would let you resume an interrupted production, recover plan state after a crash, and review past session context. Low overhead for a single-user local system vs Redis.
- [ ] **WAN aspect ratio investigation** — "I want to do a" came out boxed instead of widescreen. Understand why, prevent it.
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

---

## Ember

- [x] **Image generation reliability** — fixed 2026-03-27. Missing `tool_call_id` in tool result messages meant Ollama couldn't match results back to calls. Model stopped calling tools after accumulating malformed history. 5/5 after fix.
- [x] **Bot not responding** — fixed 2026-03-30. `.env` had a period and inline comment included in the model name value (`Qwen3.5:35b. ## Normal...`). Ollama returned 404. Fixed to `qwen3.5:35b`.

---

## Spot

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

- [ ] **followup.md log** — save full follow-up Q&A session to `reviews/<session>/followup.md` so conversations can be reviewed later or handed to Claude
- [ ] **Increase minimum file reads** — 10 is a floor, but a configurable `--min-files` CLI arg would let you push deeper on larger projects
- [ ] **Model roleplay bleed fix** — Omega outputs `<|im_end|><|im_start|>user` tokens when context gets long, injecting fake user turns. Strip these from streamed output.
- [ ] **Post-review summary commit** — after a review session, auto-commit the review + scratch + notebook to the target project's repo as a dated review artifact

---

## Someday / Maybe

- [ ] **RIFE on fast-action content** — test frame interpolation on sharp quick motion to see if 32fps is worth it

---

*Last updated: 2026-03-30*
