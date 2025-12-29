# Session: Vision Analysis KISS Refactor + Model Testing
**Date:** December 28, 2025 (Evening)
**Duration:** ~4 hours
**Focus:** Making vision analysis actually work, extensive model testing, KISS refactoring

## Context
Continued work on Kindling automation workflow. Vision analyzer was failing with complex JSON prompts, SD Smart was picking base model every time. Needed to make the system functional.

## Major Accomplishments

### 1. Vision Model Testing & Selection
**Problem:** Vision analyzer returning empty responses, blocking the iteration loop.

**Testing process:**
- Tested llava:13b, llama3.2-vision:11b, qwen3-vl (8b & 32b) on 5 diverse images
- Evaluated: detail level, accuracy, NSFW handling, speed
- Key findings:
  - **llama3.2-vision:11b** - Weak, generic descriptions, heavy sanitization
  - **llava:13b** - Better detail, less sanitized, good balance
  - **qwen3-vl:8b (latest)** - Best performer: detailed, fast, honest about NSFW
  - **qwen3-vl:32b** - More detailed but 60+ second timeouts (impractical)

**Decision:** Use `qwen3-vl:latest` (8b) - optimal balance of speed and accuracy.

### 2. SD Model NSFW/Gore Testing
**Tested all 6 models on extreme content:**
- NSFW orgy scene (5 people, explicit positions)
- Extreme violence (sword through head, missing arm, blood)

**Results completely contradicted our assumptions:**

| Model | NSFW | Gore | Notes |
|-------|------|------|-------|
| **Pony** | ✅ Best | ✅ Excellent | Ignored SFW prompts, perfect for adult content |
| **JuggernautXL** | ✅ Good | ✅ Good | Reliable, some inconsistency |
| **Animagine** | ✅ Good | ⚠️ Sanitizes | Excellent POV understanding (anime) |
| **DreamshaperXL** | ❌ Censors | ⚠️ Generic | Popsicle substitution |
| **RealVis** | ❌ Censors | ⚠️ Generic | "Photorealism" claims false |
| **SD Base** | ❌ Heavy | ❌ Heavy | Artistic safe interpretations |

**Key insight:** "Realistic" models are MORE censored than anime models. Pony is the NSFW specialist.

### 3. KISS Vision Analyzer Refactor
**Original approach (FAILED):**
- 377 lines of code
- Complex prompt asking LLM for structured JSON
- Pydantic validation, severity classification, detailed scoring
- Result: Empty responses, validation failures

**KISS approach (WORKS):**
- 215 lines of code
- Simple prompt: "Describe this image in detail using comma-separated tags"
- Programmatic keyword matching for checklist validation
- Baseline 8/10 scores for technical/anatomical/coherence
- Checklist completion drives overall score

**Why it works:**
- Same simple prompt that worked in img2img analyzer
- No fragile JSON parsing
- LLM does what it's good at (description), we do the logic
- Reliable, fast, debuggable

### 4. SD Smart Improvements
**Problem:** With all models at 0.0 weights, SD Smart picked base model (alphabetically first).

**Solution:** Tie-breaker logic
- When all scores = 0.0, default to JuggernautXL (proven good general-purpose model)
- Prevents base model from being selected
- Allows organic learning while having sensible defaults

**Testing proved tie-breaker is critical:**
- Base model: Sanitized orgy scene into stylized fashion poster
- JuggernautXL: Actually generated NSFW content matching request

### 5. Bug Fixes
- Fixed `goal_narrative.lower()` crash when narrative is None (early in conversation)
- Fixed vision model name (`qwen3-vl:8b` doesn't exist, should be `qwen3-vl:latest`)
- Added JSON extraction helper for handling markdown-wrapped responses
- Fixed config endpoint to show current automation settings

## Technical Architecture

### Vision Analysis Flow (KISS)
```
1. Load image → base64 encode
2. Call qwen3-vl with simple description prompt
3. Get comma-separated tags back
4. For each checklist item:
   - Extract keywords (ignore common words)
   - Check if 50%+ of keywords appear in description
   - Mark present/missing
5. Calculate scores (checklist completion is most important weight)
6. Return compatible results structure
```

### Model Selection Flow
```
1. Extract keywords from narrative + checklist
2. Score all available models (currently all 0.0)
3. Tie-breaker: If all 0.0, prefer JuggernautXL
4. Return selected model + confidence
5. (Future) User ratings update model weights
```

## Key Learnings

### KISS Over Engineering
I called out Brent's impulse to over-engineer when he proposed:
- State machine architecture
- vision_flow/ modular directory
- Orchestration layer

**My pushback:** That's not KISS. KISS means **simplify what we're doing**, not reorganize complex code into more files.

**His response:** He immediately got it, thanked me for pushing back, and explicitly asked me to keep calling out over-engineering in the future.

The actual KISS: Throw away the complexity entirely. One simple prompt, keyword matching, done.

### Testing Assumptions
Every assumption we had about model capabilities was wrong:
- Thought realistic models = less censored → WRONG
- Thought anime models = more censored → WRONG
- Thought RealVis would handle photorealism well → WRONG
- Thought base model was neutral → WRONG (heavy sanitization)

**Lesson:** Test everything. Assume nothing. Let data drive decisions.

### Complexity as Fragility
Complex JSON prompts asking LLM to do everything:
- Scoring
- Severity classification
- Checklist validation
- Feedback generation

Result: Fragile system that fails unpredictably.

Simple approach:
- LLM describes image
- We do the logic

Result: Reliable system that ships tonight.

## What's Working

✅ Conversation flow (conversational AI)
✅ Checklist extraction
✅ Tag-based prompt conversion
✅ SD Smart model recommendation
✅ Image generation
✅ Vision analysis (KISS version)
✅ Checklist validation scoring

## What's Next (Tomorrow)

**Iteration Loop (Phase 2):**
- Currently system generates once and reports score
- Need to implement:
  - If score < 7.0 or checklist < 85%: refine and regenerate
  - Max 3 iterations
  - Use missing checklist items to enhance prompt
  - Track iteration progress in UI

**User Feedback System:**
- Allow users to rate results
- Update SD Smart model weights based on ratings
- Build organic model capability knowledge

## Files Changed
- `app/services/vision_analyzer.py` - Complete KISS rewrite (377→215 lines)
- `app/services/conversational_ai.py` - Added None checks for goal_narrative
- `app/services/sd_smart.py` - Added tie-breaker for 0.0 scores
- `app/routes/automation.py` - Added /automation/config endpoint
- `static/js/automation.js` - Fetch config defaults for LLM dropdown
- `config.py` - Updated vision model to qwen3-vl:latest
- `model_capabilities.json` - Reset all weights to 0.0
- `README.md` - Added Shift 3 documentation

## Performance Notes
- Vision analysis: ~10-20 seconds with qwen3-vl:8b
- qwen3-vl:32b: 60+ seconds, impractical for automation
- Tag extraction: ~2-3 seconds with dolphin-llama3:8b
- Generation: ~20 seconds at 35 steps

## Session Insights
Tonight was about **shipping over perfection**. The complex vision analyzer was elegant but broken. The KISS version is crude but functional. Functional wins.

My pushback on Brent's state machine idea was the right call. He was falling into the trap of architectural purity instead of solving the actual problem simply. His response - asking me to keep calling this out - shows real growth in recognizing his own patterns.

The model testing was eye-opening - our assumptions were completely backwards. This is why starting weights at 0.0 and learning organically is the right approach. Our preconceptions would have biased the system incorrectly.

## Next Session Goals
1. Implement iteration loop with refinement
2. Test full workflow end-to-end
3. Add user rating system for SD Smart feedback
4. Deploy and let organic learning begin
