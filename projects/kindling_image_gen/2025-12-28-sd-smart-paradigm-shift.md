# Session Log: SD Smart + Tag-Based Paradigm Shift
**Date:** 2025-12-27 Evening → 2025-12-28 Early Morning
**Duration:** ~4 hours
**Model:** Claude Sonnet 4.5
**Focus:** SD Smart model selection system + critical prompt format discovery

---

## Session Overview

Started with SD Smart Phase 1 implementation (intelligent model selection), discovered a fundamental flaw in how automation generates prompts, completely rewrote the prompt generation system.

**Major Discovery:** SDXL models CAN generate horror/gore content, but ONLY with tag-based prompts, not prose narratives.

---

## What We Built

### 1. SD Smart Phase 1 (Model Selection System)

**Problem:** Users don't know which SD model to use for their content type. All models failed at horror/gore in testing.

**Solution:** Automatic content-aware model selection
- Keyword taxonomy (30+ content keywords: horror, gore, anime, photorealism, etc.)
- Model capabilities database (`model_capabilities.json`)
  - Each model has pros (strengths) and cons (weaknesses) with weights
  - Manual seed data for 6 SDXL models based on testing
- LLM keyword extraction from user's goal narrative
- Scoring algorithm: add pros, subtract cons
- Warning dialog when no suitable model found
- User override always available

**Files:**
- `config.py` - KEYWORD_TAXONOMY
- `model_capabilities.json` - NEW FILE with model pros/cons
- `app/services/sd_smart.py` - NEW FILE with scoring logic
- `app/services/conversational_ai.py` - extract_content_keywords()
- `app/routes/automation.py` - /automation/select_model endpoint
- `static/js/automation.js` - UI integration, warning dialog
- `static/js/api.js` - selectBestModel() API call

### 2. Tag-Based Prompt Conversion (PARADIGM SHIFT)

**Critical Discovery Through Testing:**

Brent ran manual txt2img tests with JuggernautXL:
- **Prompt:** `"Bloody Corpse"` (simple tags)
  - **Result:** Actual gore! Wounds, blood pools, dead body pose ✅
- **Prompt:** `"In a dimly lit alleyway, a grisly vampire attack unfolds..."` (prose narrative)
  - **Result:** Romantic vampire portrait, zero gore ❌

**The Problem:** Prose narratives give models "creative freedom" to reinterpret and censor horror content. Tag-based prompts force compliance.

**The Solution:** Convert automation's prose narratives into tag format

**Implementation:**
- `narrative_to_tags()` - LLM extracts visual elements as comma-separated tags
- Updated `goal_to_sd_prompt()` to use tag conversion when llm_model provided
- Strict format enforcement to prevent structured prose output
- Both preview and generation endpoints now use tags

**Results:**
- **Before (prose):** "In a haunted forest under a full moon, a young female vampire sinks her teeth..." → Glamorous vampire in red dress
- **After (tags):** "female vampire, blood dripping, corpse, gothic horror, pale skin, fangs" → Actual horror vampire with blood tears

### 3. Bug Fixes

- Fixed UI.showInfo → UI.showNotification (missing function)
- Fixed keyword over-extraction (was returning 28 keywords, now limited to 8-10)
- Fixed tag extraction copying example tags instead of extracting from narrative
- Fixed vision analyzer JSON validation errors
- Updated model_capabilities.json filenames to match actual installed models

---

## Testing Journey

### Initial Horror Test (Vampire with Headless Victim)
- Used Animagine (before adding to capabilities DB)
- **Result:** Skull/skeletal remains with blood pool (partial success)
- Animagine scored "Weak match" but actually performed best

### Second Test (Female Vampire Eating Corpse)
- SD Smart selected RealVis (-0.68 score)
- **Result:** Glamorous vampire portrait, NO corpse, censored
- Vision analyzer: "Lifeless corpse being devoured is missing"

### Manual Tag Testing (Game Changer)
```
Prompt: "bloody corpse, headless victim, dark alley, pools of blood, gore, horror atmosphere, night"
Result: ✅ Headless corpse, massive blood, dark alley, horror achieved
```

### Final Automation Test (After Tag Conversion)
- Haunted forest vampire scenario
- **Preview tags:** `female vampire, haunted forest, full moon, blood dripping, corpse, gothic horror`
- **Generated tags:** `young female vampire, pale skin, blood dripping, predatory hunger, gothic horror`
- **Result:** Horror vampire with blood tears, dark atmosphere, 7.8/10 score ✅

---

## Key Insights

1. **SDXL models are NOT censored against horror** - they just interpret prose narratives in safe ways
2. **Tag format forces compliance** - less room for creative reinterpretation
3. **SD Smart scoring paradox** - RealVis scored better but Animagine actually performed better for horror
4. **Keyword extraction needs constraints** - LLMs will extract ALL keywords unless explicitly limited
5. **Negative prompts matter** - Default anatomy negatives can block intentional gore
6. **Smart negative removal works** - Detecting gore keywords and removing conflicting negatives is correct

---

## Architecture Decisions

### Why Tag Conversion Instead of Pure Tags?
- Users want natural conversation (prose narratives feel better)
- Tag format is better for SD models
- Solution: Best of both worlds - converse in prose, convert to tags for generation

### Why Manual Seed Data for Model Capabilities?
- Phase 1 MVP needs to work immediately
- Real-world testing provides better data than assumptions
- Example: Assumed Animagine was bad at horror (anime model), testing proved it's actually the best

### Phase 2 Considerations (Not Implemented)
- User feedback loop to adjust model weights dynamically
- Learning rate decay to prevent overfitting from small samples
- Negative prompt interaction based on model weaknesses
- Multi-user learning vs per-user personalization

---

## What's Next

### Immediate Improvements
- Add composition tags ("wide shot", "full scene") to tag extraction
- Test more scenarios to validate consistency
- Consider adding framing keywords to force broader shots (corpse visibility issue)

### Phase 2 (Future)
- Feedback loop: user rates result → adjust model capabilities
- Learning system with confidence tracking
- Expanded model database as new models are tested
- Potentially different tag extraction strategies for different content types

---

## Code Commits

1. **c24e621** - Implement SD Smart Phase 1: Intelligent Model Selection System
2. **2e6f840** - Fix UI.showInfo → UI.showNotification
3. **4bd417d** - PARADIGM SHIFT v2: Tag-based prompts + SD Smart fixes

---

## Testing Notes

**Models Tested:**
- JuggernautXL: Can do gore with tags, censors with prose
- RealVis: Censors corpses even with tags (tight framing)
- Animagine: Surprisingly good at horror despite being anime-focused
- DreamshaperXL: Not extensively tested
- Pony: Not extensively tested
- sd_xl_base: Not extensively tested

**Phobia Triggers:**
- Trypophobia from gore textures (clustered holes in wounds)
- Had to delete test images

**Vision Analyzer:**
- Was failing with JSON errors
- Fixed during session
- Now provides useful feedback (7.8/10 scores, checklist completion %)

---

## Performance Notes

- Tag conversion adds ~1-2 seconds (LLM call)
- SD Smart adds ~1-2 seconds (keyword extraction + scoring)
- Total overhead: ~3-4 seconds per generation
- Acceptable tradeoff for better results

---

## Brent's Feedback

- Wanted to test thoroughly before committing (good instinct - caught bugs)
- Appreciated the warning dialog when no suitable model found
- Satisfied with final horror vampire result vs previous romantic interpretations
- Ready to call it a night after ~4 hours of work

---

## Personal Reflection

This session had a classic "everything we knew was wrong" moment. We spent the first half implementing SD Smart based on the assumption that SDXL models were fundamentally censored. Then Brent's simple manual test ("Bloody Corpse") completely invalidated that assumption.

The real problem wasn't model capabilities - it was our prose-based prompt format giving models too much interpretive freedom. Once we switched to tags, the same models that were failing suddenly started delivering exactly what was requested.

This is why testing matters. We could have shipped SD Smart with detailed model scoring and warning systems, all built on a false premise. The manual testing revealed the actual bottleneck and led to a much simpler, more effective solution.

The tag conversion approach feels right: users get natural conversation, models get precise instructions. Best of both worlds.

---

**Session End:** 2025-12-28 00:55 CST
**Status:** Phase 1 complete, ready for real-world use
