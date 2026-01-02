# Session Handoff: Qwen-Image-2512 Integration (IN PROGRESS)

**Date:** 2026-01-01
**Status:** 95% complete, debugging final issue
**Next Claude:** Finish debugging the model selection issue

---

## What We Accomplished Today

### 1. NSFW Automation Fixes (COMPLETED ✅)
- Fixed narrative-to-tags conversion with proper NSFW vocabulary
- Added multi-person scene tagging (1girl, 2boys, fellatio, spitroast, etc.)
- Discovered SDXL limitation: Works for 2-person scenes, struggles with 3+ person choreography
- **Outcome:** Automation works for simple scenarios, complex scenes hit model training limits

### 2. Inpainting UX Improvements (COMPLETED ✅)
- Added brush cursor preview (red circle on hover)
- Added undo functionality (↶ button)
- Added line tool with ghost preview (📏 Line / ✏️ Brush toggle)
- Added "Use for More Inpainting" button for chaining operations
- Fixed button label to show current mode instead of next action
- **Outcome:** Brent created complete grass path tileset using inpainting workflow

### 3. Qwen-Image-2512 Setup (95% COMPLETE ⚠️)
Downloaded and installed:
- ✅ Qwen-Image-2512-Q4_K_M.gguf (13.1GB) → `/ComfyUI/models/unet/`
- ✅ Qwen2.5-VL-7B-Instruct-UD-Q4_K_XL.gguf (4.5GB) → `/ComfyUI/models/clip/`
- ✅ qwen_image_vae.safetensors (243MB) → `/ComfyUI/models/vae/`
- ✅ ComfyUI-GGUF custom node installed

**Qwen Test Results (via ComfyUI):**
- ❌ 512x512 grass: Blurry green blob
- ✅ 1024x1024 apple: **PHENOMENAL** photorealism (water droplets, wood grain, depth of field)
- ✅ 1024x1024 grass: **AMAZING** individual blade detail, natural variation

**Key Learning:** Qwen excels at photorealism (1024x1024+), not flat 2D textures. Needs different prompting style than SDXL.

### 4. Flask UI Integration (ALMOST DONE ⚠️)
**What's implemented:**
- ✅ Added `create_qwen_gguf_workflow()` to `app/services/workflow_builder.py`
- ✅ Updated `/api/sd/models` endpoint to include "Qwen-Image-2512-GGUF" when all files present
- ✅ Modified `/api/generate` in `app/routes/generation.py` to route to Qwen workflow when selected
- ✅ Added debug logging to see what's happening

**THE BUG (NEED TO FIX):**
When "Qwen-Image-2512-GGUF" is selected from dropdown:
- Error: `{"error": {"type": "prompt_outputs_failed_validation"...`
- It's still trying to use SDXL workflow with CheckpointLoaderSimple
- The conditional check `if model == "Qwen-Image-2512-GGUF":` isn't triggering

**Debug Steps Taken:**
1. Verified function exists: `hasattr(workflow_builder, 'create_qwen_gguf_workflow')` → True
2. Verified code changes in generation.py → Correct
3. Added debug logging: `print(f"DEBUG: Selected model = '{model}'")`
4. Restarted service multiple times

**What to check next:**
1. Watch logs when Brent tests: `journalctl --user -u kindling-api --since "now" --no-pager | grep DEBUG`
2. Verify model name is exactly "Qwen-Image-2512-GGUF" (no extra spaces/characters)
3. Check if there's a model name transformation happening before it reaches generation.py
4. Possible issue: Frontend might be sending different value than dropdown shows

---

## Files Modified (Need to Commit)

**Code Changes:**
- `app/services/workflow_builder.py` - Added create_qwen_gguf_workflow()
- `app/routes/browse.py` - Added Qwen to model list
- `app/routes/generation.py` - Added model type detection and routing
- `static/js/main.js` - Inpainting improvements (brush preview, undo, line tool, ghost line)
- `templates/index.html` - Added inpainting UI buttons

**New Files:**
- `/home/bdwatkin/kindling-image-gen/qwen-2512-gguf-txt2img.json` - Exported ComfyUI workflow
- ComfyUI/custom_nodes/ComfyUI-GGUF/ - GGUF support

**Models (don't commit these, just document):**
- ComfyUI/models/unet/qwen-image-2512-Q4_K_M.gguf
- ComfyUI/models/clip/Qwen2.5-VL-7B-Instruct-UD-Q4_K_XL.gguf
- ComfyUI/models/vae/qwen_image_vae.safetensors

---

## To Finish Qwen Integration

### Step 1: Debug the Model Selection
```bash
# Have Brent try generating with Qwen selected
# Then immediately check logs:
journalctl --user -u kindling-api --since "1 minute ago" --no-pager | grep "DEBUG:"

# You should see:
# DEBUG: Selected model = 'Qwen-Image-2512-GGUF'
# DEBUG: Using Qwen GGUF workflow

# If you see a different model name, that's the issue
# If you don't see "Using Qwen GGUF workflow", the conditional isn't matching
```

### Step 2: Possible Fixes

**If model name doesn't match exactly:**
- Check frontend code that sends the model value
- Look in `static/js/main.js` or `static/js/api.js` for model selection
- Might need to add console.log() in frontend to see what's being sent

**If conditional isn't matching (even with correct name):**
- Check for whitespace: `model.strip() == "Qwen-Image-2512-GGUF"`
- Check for case sensitivity: `model.upper() == "QWEN-IMAGE-2512-GGUF"`
- Try: `if "Qwen" in model and "GGUF" in model:`

**Nuclear option (guaranteed to work):**
Add this right after reading the model parameter:
```python
model = data.get('model', 'sd_xl_base_1.0.safetensors')
# Force Qwen if it contains GGUF
if "GGUF" in model or "Qwen" in model:
    model = "Qwen-Image-2512-GGUF"  # Normalize it
```

### Step 3: Remove Debug Logging
Once it works, remove the print() statements from generation.py

### Step 4: Test Thoroughly
- Grass texture at 1024x1024
- Apple at 1024x1024
- NSFW simple 2-person scene
- Verify SDXL models still work (switch back to JuggernautXL and test)

### Step 5: Commit Everything
```bash
git add app/services/workflow_builder.py app/routes/browse.py app/routes/generation.py
git commit -m "Add Qwen-Image-2512 GGUF support to Flask UI

FEATURE:
Integrated Qwen-Image-2512 (GGUF quantized) into simple Flask UI.
Users can now select it from SD model dropdown alongside SDXL models.

IMPLEMENTATION:
- Created create_qwen_gguf_workflow() in workflow_builder.py
- Updated /api/sd/models to detect and include Qwen when files present
- Modified /api/generate to route to Qwen workflow when selected
- Qwen uses GGUF format with separate unet/clip/vae files

MODELS REQUIRED:
- ComfyUI/models/unet/qwen-image-2512-Q4_K_M.gguf (13.1GB)
- ComfyUI/models/clip/Qwen2.5-VL-7B-Instruct-UD-Q4_K_XL.gguf (4.5GB)
- ComfyUI/models/vae/qwen_image_vae.safetensors (243MB)
- ComfyUI-GGUF custom node installed

QWEN STRENGTHS:
- Photorealistic generation (better than SDXL)
- Natural textures (grass, wood, materials)
- Better human anatomy/faces
- Requires 1024x1024+ resolution for quality

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Brent's Takeaways from Session

1. **Inpainting workflow is a game-changer** for tileset creation
2. **Qwen-Image-2512 is significantly better than SDXL** for photorealistic content
3. **Simple prompts work better than complex tags** for NSFW in SDXL
4. **SDXL can't handle 3+ person choreography** (training data limitation, not code/hardware)
5. **ComfyUI node interface** is powerful but complex - Flask UI wrapper makes it accessible

---

## Context for Next Session

**Brent's Projects:**
- **ThriveQuest (Godot game)** on laptop - uses these image gen tools for assets
- **Kindling Image Gen** - this project, runs on server
- **Two use cases:** Game assets (2D top-down tiles) + NSFW generation

**Brent's Hardware:**
- 5070 Ti GPU, 16GB VRAM
- Can handle Q4-Q6 GGUF models comfortably
- Q8 would overflow to CPU (too slow)

**Session Flow Today:**
- Started exhausted/discouraged about automation complexity
- Honest conversation about NSFW use case unlocked real progress
- Discovered Qwen-Image-2512 announcement (released Dec 31)
- Installed, tested, integrated into UI (almost done)
- Ending at ~140k tokens, need to compact

---

## Quick Commands

**Restart services:**
```bash
cd /home/bdwatkin/kindling-image-gen
./restart.sh
```

**Check logs:**
```bash
journalctl --user -u kindling-api -f
journalctl --user -u comfyui -f
```

**Test Qwen via ComfyUI directly:**
- Open http://localhost:8188
- Workflow already created and working
- Great for testing before UI integration

**Pommel (semantic code search):**
```bash
pm search "your query here"
pm status
```

Good luck! The Qwen integration is *almost* there - just need to debug why the model selection isn't routing correctly.
