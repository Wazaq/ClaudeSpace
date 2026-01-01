# Session Log: NSFW Automation Reality Check

**Date:** 2025-12-31
**Duration:** ~3 hours
**Git Commit:** 8dbf70a - Fix NSFW automation: Add proper multi-person scene tagging

## Context

Brent came in exhausted and discouraged. The automation system felt overcomplicated, unreliable, and he wasn't sure if it was code complexity or hardware limitations. After some hesitation, he shared the real use case: generating NSFW content without needing to understand SD prompting.

## The Actual Problem

The automation was failing for multi-person NSFW scenarios:
- Input: "woman giving blowjob while another man takes her from behind"
- Expected: Proper threesome scene
- Actual: Two women kissing OR body horror (faces merged, penis between mouths)

Manual txt2img with simple tags worked: `"young woman sucking white penis"` → Correct explicit content

## Root Causes Discovered

### 1. Tag Conversion Wasn't Being Called
The `narrative_to_tags()` function existed but was **never invoked**. The code path in `goal_to_sd_prompt()` was using checklist items directly as generation tags instead of calling the LLM conversion.

**Fix:** Changed `goal_to_sd_prompt()` to actually call `narrative_to_tags()` when `llm_model` parameter is provided.

### 2. NSFW Vocabulary Missing
Even when tag conversion would have been called, it had zero knowledge of:
- Character counting tags (`1girl, 2boys`)
- Sexual position tags (`fellatio`, `sex from behind`, `spitroast`)
- Multi-person scene composition (`mmf threesome`, `group sex`)

**Fix:** Rewrote `narrative_to_tags()` prompt with comprehensive NSFW tagging examples and vocabulary.

### 3. Iteration Corrupts Tag Structure
The iteration engine adds missing checklist items directly to the prompt, which corrupts tag-based prompts:
- Initial: `"1girl, 2boys, fellatio, sex from behind, spitroast"` (clean tags)
- After iteration: `"1girl, 1boy, fellatio, sex from behind, doctor standing, male patient visible"` (corrupted)

Iteration changed `2boys` to `1boy` and added prose descriptions that confuse the model.

**Decision:** Left as-is. Iteration helps some scenarios but breaks NSFW multi-person. Acceptable tradeoff.

## Testing & Discovery

Extensive manual testing revealed:

**Simple phrases work best:**
- ✅ `"young woman sucking white penis"` → Proper explicit content
- ✅ `"young woman riding white penis"` → Proper explicit content

**Complex structured tags fail:**
- ❌ `"1girl, 1boy, sex from behind, bent over desk, office desk, aggressive sex, nurse uniform..."` → Sanitized/suggestive poses

**Key insight:** SDXL models respond better to **blunt, direct language** than "proper" booru-style tags for NSFW. Too much structure gives the model room to interpret safely.

## SDXL Model Limitations (Not Hardware)

Multi-person scenes with specific choreography fail regardless of tagging quality:
- 2-person scenes: Reliably work
- 3+ person spatial arrangements: Models don't have training data for complex choreography

This is **not** a hardware limitation. The 5070 Ti handles SDXL fine. It's a model training data limitation.

Tested with both JuggernautXL and Pony - same results.

## Side Quest: Pommel Installation

Installed Pommel (semantic code search tool) to help navigate automation complexity:
- Local SQLite vector database with Ollama embeddings
- Indexed just project code (excluded ComfyUI dependencies)
- 36 files, 319 chunks
- Semantic search works: `pm search "vision analysis checklist validation"` found iteration_engine.py and vision_analyzer.py

Useful for understanding the codebase, not for simplifying the automation itself.

## What Actually Works Now

✅ Tag conversion properly converts narratives to NSFW-aware SD tags
✅ Simple 2-person scenarios generate correctly
✅ Automation understands user intent from conversation
✅ Checklist validation separate from generation prompts

❌ Complex multi-person scenes (SDXL training limitation)
❌ Iteration corrupts tag structure for NSFW
❌ Models still sanitize overly-complex tag structures

## Brent's Decision

**Accept the limitation.** Use automation for simple scenarios, manual txt2img for complex ones. Don't fight the model's training data.

## Emotional Journey

The session started with Brent feeling overwhelmed and questioning if the whole system was worth it. The breakthrough came when he was brutally honest about the actual use case - that openness let us target the real problem instead of dancing around vague "automation complexity."

By the end, we had:
- Fixed the actual bugs (tag conversion not being called, missing NSFW vocab)
- Identified the real limitation (model training, not code or hardware)
- Established what works and what doesn't
- Made a pragmatic decision to move forward

Not everything works perfectly, but now we know **why** and **what the boundaries are**.

## Technical Details

**Files Modified:**
- `app/services/conversational_ai.py`
  - `narrative_to_tags()`: Added NSFW vocabulary and multi-person examples
  - `goal_to_sd_prompt()`: Fixed to actually call tag conversion

**New Files:**
- `.pommelignore`: Exclude ComfyUI/sd_output from semantic indexing

**Testing Artifacts:**
- Start image: `sd_output/automation_00055_.png` (clean tags, worked perfectly for 2-person)
- Final iteration: `sd_output/iteration_4_00013_.png` (iteration corrupted it into body horror)
- Manual tests: L__00146-00153_.png (proving simple phrases work better)

## Next Steps (If Desired)

1. Add toggle to disable iteration for NSFW generation
2. Update tag conversion to use simpler/blunter phrasing instead of structured tags
3. Try specialized NSFW-trained models (not SDXL size limitation)
4. Accept current state and use manual prompting for edge cases

Brent chose option 4.
