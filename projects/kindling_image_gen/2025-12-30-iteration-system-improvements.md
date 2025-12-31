# Iteration System Improvements - Debugging Session

**Date:** December 30-31, 2025 (late night session)
**Status:** 🔧 WIP - Multiple improvements, system still not fully working

---

## Session Context

Continued work on the automated iteration system from yesterday. Session started rough - hit an auto-compact that wiped ~7 hours of context right when we were evaluating test results. Brent disabled auto-compact after that.

---

## What We Fixed

### 1. Forced Completion Override (Conversation Efficiency)

**Problem:** Override to skip discovery questions when user provides detailed first message (50+ words) wasn't firing.

**Root Cause:** AI greeting counts as an exchange, so `exchange_count=1` when user sends first message, not 0.

**Fix:** Changed check from `exchange_count == 0` to `exchange_count <= 1`

**Result:** ✅ Working - detailed first messages now skip straight to final narrative

**Files:** `app/services/conversational_ai.py:149`

---

### 2. Denoise Levels Too Conservative

**Problem:** Iterations generating nearly identical images each time. Denoise at 0.3-0.4 was too gentle - SD wasn't making meaningful changes.

**Root Cause:** We capped denoise at 0.5 to prevent "death spiral" where high denoise destroyed good elements. But 0.3-0.5 range was too conservative.

**Fix:** Increased denoise ranges and cap:
- 70%+ completion: 0.50 (was 0.30)
- 50-70% completion: 0.60 (was 0.40)
- <50% completion: 0.70 (was 0.50)

**Result:** ⚠️ Partial - Images change more between iterations now, but still oscillating

**Files:** `app/services/iteration_engine.py:104-131`

---

### 3. Checklist Simplification Too Strict

**Problem:** Simplification rejected if it produced fewer items than original (e.g., 10→9 items). This caused fallback to verbose original checklist.

**Example:**
- Simplified: "First person has green hair" (atomic, VLM-friendly)
- Original: "On the left, woman with green hair wearing red jacket" (verbose, compound)

**Fix:** Removed the "fewer items" safety check - simplification can now combine related items

**Result:** ✅ Working - simplified checklists now accepted

**Files:** `app/routes/automation.py:107-112`

---

### 4. Fix Prompts Too Verbose

**Problem:** Fix prompts using full checklist items:
- "Penis of first person visible, Hands of first person behind head visible"

**Fix:** Added cleanup function to strip verbose parts:
- Remove: "visible", "present", "of first person", "of second person", etc.
- Output: "penis, hands behind head"

**Result:** ✅ Working - fix prompts are cleaner

**Files:** `app/services/iteration_engine.py:61-89`

---

### 5. Initial Prompts From Checklist

**Problem:** LLM tag conversion (`narrative_to_tags()`) with gemma2:9b was producing garbage:
- Input: Detailed narrative about bedroom scene with specific positioning
- Output: "man, nude, erect penis, woman, asian, twenties, breasts, oral sex, intimate, romantic, warmly lit bedroom, bed, chair"
- Missing: POV, positioning, expressions, composition

**Attempted Fix:** Skip LLM conversion entirely, use checklist items directly as SD prompt

**Reasoning:** Simplified checklist items are already atomic and specific - why ask LLM to convert?

**Result:** ❌ Not much better - checklist items as tags still don't produce good composition

**Files:** `app/services/conversational_ai.py:493-511`

---

## Current State of System

### What's Working
1. ✅ Forced completion - 50+ word first messages skip discovery questions
2. ✅ Checklist simplification - produces atomic, VLM-friendly items
3. ✅ VLM validation - accurately validates atomic checklist items
4. ✅ Iterations run and complete
5. ✅ Higher denoise makes visible changes between iterations

### What's Still Broken
1. ❌ **Initial image quality** - Direct checklist prompts don't produce good composition
2. ❌ **Iteration oscillation** - Fixes some items, breaks others
   - Example: Adds "penis visible" but loses "hands behind head", then vice versa
   - Checklist completion bounces 60-80%, never hits 85% threshold
3. ❌ **Death spiral** - Scores sometimes drop instead of improve
4. ❌ **img2img is transformative, not additive** - Each denoise pass can undo previous fixes

---

## Test Results

### Test Scenario: Erotic bedroom scene
- User provided detailed 61-word first message
- LLM created 8-item checklist
- Initial generation passed all 8 items (100% validation)
- But actual image was heavily censored/generic

**Problem identified:** Checklist validation passed, but the image didn't match the intent. Either:
- Checklist was oversimplified (lost explicit details)
- Model censored during generation
- VLM is validating a censored version as passing

---

## Debug Logging Added

Added comprehensive logging throughout:
- `🔍 OVERRIDE CHECK:` - Shows exchange_count, word_count, force_final decision
- `🔍 DEBUG: Simplification results:` - Shows original vs simplified item counts
- `🔍 DEBUG: Missing items from analysis:` - Shows what VLM says is missing
- `Fix prompt:` - Shows actual prompt sent to img2img
- `Denoise:` - Shows denoise level and reasoning

All logs go to `~/.local/share/kindling-api.log`

---

## Architectural Issues Identified

### 1. Checklist Items ≠ SD Prompts

Checklist items optimized for VLM validation don't work well as SD prompts:
- VLM needs: "Penis of first person visible" (atomic, binary validation)
- SD needs: "erect penis, pov from side, hands behind head, woman kneeling" (composition + details)

**Implication:** We need separate representations:
- Checklist for validation (atomic, VLM-friendly)
- Prompt for generation (composition, SD-friendly)

### 2. img2img Fundamental Limitation

img2img with text prompts is **transformative**, not **additive**:
- Can't say "add hands behind head while keeping penis visible"
- Each denoise pass reinterprets the whole image
- High checklist completion (70-80%) means small denoise, which doesn't fix the 20-30% missing
- Low denoise needed to fix missing items can break what's already working

**Implication:** Text-only img2img might be wrong tool for iterative refinement. Need:
- ControlNet (preserve structure while changing details)
- Inpainting (targeted fixes to specific regions)
- Or lower expectations - accept 70-80% as "good enough"

### 3. LLM Tag Conversion Failing

gemma2:9b ignoring detailed prompt instructions for `narrative_to_tags()`:
- Prompt asks for POV tags, composition analysis, positioning
- LLM outputs keyword dump instead
- 70b model would work but takes 3-5 minutes (unacceptable UX)

**Options:**
1. Use 70b only for critical conversions (accept the wait)
2. Build deterministic conversion (no LLM)
3. Use checklist items directly (current approach, not working great)

---

## Next Steps (Not Attempted - Session End)

### Immediate Debugging
1. Log the actual checklist that gets approved by user
2. Log the actual positive prompt sent to SD
3. Compare to see what's being lost in conversion

### Potential Solutions to Explore
1. **Two-tier prompting:**
   - Generate initial image from narrative (more descriptive)
   - Use checklist for validation and iteration fix prompts only

2. **Accept lower threshold:**
   - Change from 85% to 70% completion
   - Recognize that 70-80% might be the practical limit for text-only img2img

3. **ControlNet integration:**
   - Use ControlNet to preserve composition during iterations
   - Allows higher denoise without destroying layout

4. **Deterministic tag conversion:**
   - Build rule-based system to convert narrative → SD tags
   - Faster than LLM, more reliable than gemma2:9b

5. **Hybrid approach:**
   - Use narrative for initial generation
   - Use simplified checklist items for iteration fix prompts
   - Accept that initial quality matters more than iteration success rate

---

## Performance Notes

- Full automation with 5 iterations: ~6 minutes
  - Initial gen: ~45s
  - 5 iterations: ~45s each = ~225s
  - 6 analyses: ~10s each = ~60s
  - Total: ~330s = 5.5 minutes
- Forced completion saves ~1-2 minutes by skipping discovery questions
- Direct checklist prompts save ~30-60s by skipping LLM tag conversion

---

## Code Changes Summary

**Modified Files:**
- `app/services/conversational_ai.py` - Forced completion override + direct checklist prompts
- `app/services/iteration_engine.py` - Denoise levels + fix prompt cleanup
- `app/routes/automation.py` - Removed checklist simplification restriction
- `config.py` - (if any config changes - check git diff)
- UI files for displaying iteration details

**Debug Logging:**
- Added throughout conversation flow, simplification, iteration process
- All use `flush=True` for immediate output

---

## Session Notes

- Session interrupted by auto-compact (disabled afterward)
- Brent getting tired near end - wrapped up with checkpoint commit
- Multiple test runs with erotic content to test explicit generation
- Juggernaut model selected (doesn't censor)
- Core issue: System technically works (iterations run, VLM validates) but doesn't produce desired results

---

## Quotes from Session

> "every image was pretty much the same exact image, nothing was really changed"
- Brent on denoise being too low

> "look at the prompt... that doesn't really help with the initial image"
- Brent identifying that checklist items as direct prompts produces poor composition

> "not much better, commit it with a note that it's broken but we wanted a checkpoint"
- Decision to wrap up session

---

**Energy Level:** Low - late night session, both tired
**Complexity:** High - fundamental architectural questions about img2img limitations
**Next Session:** Need fresh perspective on prompt generation strategy
