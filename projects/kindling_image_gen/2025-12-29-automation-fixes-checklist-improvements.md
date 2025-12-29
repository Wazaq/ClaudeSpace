# Automation Workflow Debugging & Checklist Improvements

**Date:** December 29, 2025
**Session Focus:** Fixing automation bugs, simplifying checklist extraction, adding UI controls

---

## What We Fixed

### 1. LLM Template Response Bug
**Problem:** dolphin-llama3 would sometimes output "Your conversational response to the user" (the JSON template) instead of actual content.

**Solution:** Added auto-retry detection (conversational_ai.py:173-191)
- Detects when message equals template text
- Automatically retries the same LLM call once
- Silent recovery - user never sees the glitch

### 2. Checklist Extraction Hallucinations
**Problem:** Original extraction prompt taught the LLM to hallucinate details:
- "auburn hair" instead of "brunette"
- "candlestick with burning candle" (never mentioned)
- "wooden chair" instead of "leather couch"

**Root cause:** Example-heavy prompt that showed the LLM how to elaborate:
```
Be SPECIFIC. Not "fairy" but "topless fairy with blue hair and tanned skin".
```

**Solution:** Simplified extraction prompt to be purely extractive (conversational_ai.py:322-332):
```python
extraction_prompt = f"""Read this narrative and extract the key visual requirements as a checklist.
Only include what is explicitly mentioned - do not add or infer details.

Narrative:
{goal_narrative}

Return JSON format:
{{
    "checklist": ["requirement 1", "requirement 2", ...]
}}
"""
```

**Result:** Checklist now accurately reflects what user described, no creative additions.

### 3. "Let me summarize" Detection Bandaid
**Problem:** LLM would say "Let me summarize..." but forget to set `is_final_narrative: true` flag.

**Solution:** Keyword detection with safeguards (conversational_ai.py:196-210)
- Detects summary phrases: "let me summarize", "based on your description, i imagine"
- Doesn't trigger on questions ("would you like me to summarize?")
- Automatically sets flag AND copies message to goal_narrative if missing

### 4. Analyzer Description Display
**Feature added:** Shows raw vision model output in UI (ui.js:372-377)
- Displays exactly what qwen3-vl detected
- Helps debug checklist matching issues
- Shows user what the AI "sees"

### 5. Editable Checklist with Add/Remove
**Feature added:** Full checklist editing capabilities (ui.js:306-348)
- **× button** next to each item to remove
- **+ Add Requirement** button to add new items
- Live re-rendering when items change
- Indices auto-update after removal

**Why this matters:** User can refine AI-generated checklist before generation
- Add missing details ("woman has large chest")
- Remove irrelevant items
- Change attributes ("brunette" → "long red hair")

---

## Testing Results

### Test 1: Simplified Extraction (Successful)
**Prompt:** Cozy cabin interior, brunette woman reading book, etc.

**Checklist extracted:**
- ✅ Cozy cabin interior
- ✅ Fireplace with dancing flames
- ✅ Woman in her early 30s, brunette, wearing red sweater and jeans
- ✅ Leather couch
- ✅ Book
- ✅ Warm ambient lighting
- ✅ Snow visible through window
- ✅ Rustic wooden walls
- ✅ Photorealistic art style

**No hallucinations!** Accurate extraction.

### Test 2: Edited Checklist (Successful)
**User added:**
- Item #8: "Woman has a large chest"
- Item #9: "Woman has long red hair" (changed from brunette)

**Result:** Generated image had red hair! Checklist edits were respected.

### Test 3: Failed Generation (Ready for Iteration)
**Image:** Woman standing and posing, not sitting/reading
**Score:** 6.6/10 (below 7.0 threshold)
**Checklist:** 44% (below 85% threshold)

**Missing:**
- She's standing instead of lounging on couch with book
- No visible book
- No snow visible through windows
- TV not showing National Lampoon's Christmas Vacation specifically

**This is PERFECT for testing img2img iteration** - real failures that need fixing.

---

## What's Next

### Iteration System (Not Started)
1. Detect failed generation (score < 7 OR checklist < 85%)
2. Analyze what's wrong from vision feedback
3. Generate img2img "fix" prompt based on missing items
4. Use denoise 0.7-0.8 for significant changes
5. Re-analyze and iterate until pass or max iterations

### From Earlier Testing (img2img experiments)
**Discovered:**
- **Prompt strategy:** Change-only prompts work best ("make the hair red")
- **Denoise sweet spot:** 0.7-0.8 for actual changes that preserve good elements
- **Hybrid/full prompts:** Don't work well - model ignores change request

---

## Files Modified

- `app/services/conversational_ai.py` - Template retry, simplified extraction, summary detection
- `static/js/ui.js` - Analyzer description display, add/remove checklist buttons
- `app/services/vision_analyzer.py` - Already had raw_description, just exposed it

---

## Key Lessons

**1. Simplicity > Complexity for LLM Prompts**
- Detailed examples teach the LLM to hallucinate
- Simple extractive prompts work better
- Trust the model, don't over-constrain

**2. LLMs Are Unreliable, Build Fallbacks**
- Template response bug required auto-retry
- Summary detection needed because LLMs forget flags
- Bandaids are practical when models misbehave

**3. User Control Matters**
- Editable checklist gives users final say
- Vision analyzer description helps debug
- Trust but verify approach

**4. Test With Real Use Cases**
- The "too perfect" cabin image taught us nothing
- The standing-instead-of-sitting failure is valuable
- Iteration needs real failures to debug

---

**Status:** Ready to implement iteration loop using img2img with change-only prompts at denoise 0.7-0.8.
