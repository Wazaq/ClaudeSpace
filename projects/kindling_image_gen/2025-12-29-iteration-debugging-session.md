# Iteration System Debugging Session

**Date:** December 29, 2025
**Status:** 🔧 In Progress - Debugging Score Tracking & Fix Prompts

---

## Session Summary

Continued testing the iteration system that was built earlier today. Found two critical bugs during end-to-end testing:

1. **Scores not carrying over between iterations** - Iteration 2+ showing "Before: Score 0.0/10, Checklist 0%" instead of actual scores from previous iteration
2. **Generic fix prompts instead of using missing checklist items** - Falling back to "improve quality and details to match..." instead of using actual missing items

---

## What Happened This Session

### Initial Test Results

User tested the iteration system and found issues in the iteration detail display:

```
🔄 Iteration Attempted
3 iterations performed - did not fully pass all gates

Iteration 1:
Before: Score 0.0/10, Checklist 0%
Fix prompt: "improve quality and details to match: In a softly lit bedroom setting..."
Denoise: 0.75

Iteration 2:
Before: Score 0.0/10, Checklist 0%
Fix prompt: "refine details, improve quality"
Denoise: 0.60
```

**Problems identified:**
- Iteration 2 should show scores from after iteration 1, not 0.0/0%
- Iteration 1 should use missing checklist items, not generic fallback prompt
- Final analysis showed missing items existed: "softly lit bedroom, two women in their 20s, women wearing nighties, one woman has red hair one has blue hair, calm and relaxing mood"

### Attempted Fixes

**Fix #1: Score Tracking Logic**

Changed the flow in `iteration_engine.py`:

```python
# OLD FLOW (BROKEN):
for iteration_num in range(1, max_iterations + 1):
    analysis = vision_analyzer.analyze_image(...)  # Analyze current image
    # ... generate fix ...
    # Log with previous_analysis (but never updated it properly)
    previous_analysis = analysis  # Too late!

# NEW FLOW (ATTEMPTED):
for iteration_num in range(1, max_iterations + 1):
    # Use pre-computed initial_analysis for iteration 1
    if iteration_num == 1 and previous_analysis is not None:
        analysis = previous_analysis
    else:
        analysis = vision_analyzer.analyze_image(...)

    # ... generate fix ...

    # Log with scores that triggered THIS iteration
    iteration_log.append({
        'previous_score': analysis.get('overall_score', {}).get('score', 0),
        'previous_checklist_pct': analysis.get('checklist_validation', {}).get('completion_percentage', 0)
    })

    # Analyze the NEW image for next iteration
    previous_analysis = vision_analyzer.analyze_image(current_image_path, ...)
```

**Fix #2: Added Debug Logging**

Added to `generate_fix_prompt()`:
```python
missing = analysis.get('checklist_validation', {}).get('missing_items', [])
print(f"🔍 DEBUG: Missing items from analysis: {missing}")
```

This will help us see what the vision analyzer is actually returning.

### Test Result After Fixes

User tested again - still didn't work:
- Test log updated: `.brent/debug_logs/auto-ai-test.log`
- Final image: `sd_output/iteration_2_00007_.png`

---

## Current State of Code

### Files Modified This Session

**`app/services/iteration_engine.py`**
- Added `initial_analysis: Optional[Dict] = None` parameter to `iterate_image()`
- Changed iteration loop to use initial_analysis for first iteration check
- Modified score tracking to analyze new image immediately after generation
- Added debug logging for missing_items

**`static/js/ui.js`**
- Added expandable "📋 View iteration details" section
- Shows each iteration's:
  - Before scores (previous_score, previous_checklist_pct)
  - Fix prompt used
  - Denoise level applied

**`app/routes/automation.py`** (earlier in day)
- Passes `initial_analysis` to `iterate_image()` to avoid re-analyzing initial image

---

## Known Issues

### Issue #1: Scores Still Not Carrying Over

**Symptom:** Iteration 2+ shows "Before: Score 0.0/10, Checklist 0%"

**Expected:** Should show actual scores from after previous iteration

**Hypothesis:** The `previous_analysis` variable isn't being set correctly, or the analysis structure doesn't have the expected keys.

**Next Steps:**
1. Check what the vision analyzer actually returns - does it have `overall_score.score` and `checklist_validation.completion_percentage`?
2. Add more debug logging to see what `previous_analysis` contains at log time
3. Verify the new image analysis (line 274-278) is actually running and storing results

### Issue #2: Generic Fix Prompts

**Symptom:** Iteration 1 uses "improve quality and details to match..." instead of missing checklist items

**Expected:** Should use top 3 missing items: "softly lit bedroom, two women in their 20s, women wearing nighties"

**Hypothesis:** The `missing_items` array is empty when `generate_fix_prompt()` is called, even though the final analysis shows missing items.

**Next Steps:**
1. Check the debug log for "🔍 DEBUG: Missing items from analysis:" output
2. Verify the vision analyzer is returning `checklist_validation.missing_items` in the expected format
3. Check if the initial analysis has different structure than later analyses

### Issue #3: Only 2 Iterations Running

**Symptom:** User's test shows iteration_2_00007_.png as final image (only 2 iterations instead of 3)

**Expected:** Should run max 3 iterations unless it passes quality gates

**Hypothesis:** Either:
- It passed quality gates after iteration 2 (unlikely given final scores)
- It hit some error condition and returned early
- The iteration tracking is off-by-one

**Next Steps:**
1. Check the server logs to see if iteration 3 actually ran
2. Look for error messages or early returns

---

## Architecture Notes

### How Iteration Flow SHOULD Work

```
Initial Generation
  ↓
Analyze initial image (score: 0/10, checklist: 0%)
  ↓
Quality gate check → FAIL
  ↓
ITERATION 1:
  - Use initial analysis scores (0/10, 0%)
  - Generate fix prompt from missing items
  - img2img with denoise 0.85
  - Analyze NEW image → (score: 4.2/10, checklist: 28%)
  ↓
ITERATION 2:
  - Use analysis from iteration 1 (4.2/10, 28%)
  - Generate fix prompt from REMAINING missing items
  - img2img with denoise 0.60
  - Analyze NEW image → (score: 6.1/10, checklist: 43%)
  ↓
ITERATION 3:
  - Use analysis from iteration 2 (6.1/10, 43%)
  - Generate fix prompt (refinement)
  - img2img with denoise 0.55
  - Analyze NEW image → (score: 6.8/10, checklist: 50%)
  ↓
Max iterations reached → Return best result
```

### Current Bug in Flow

The `previous_analysis` isn't being passed through the loop correctly. Each iteration needs to:
1. Log with the scores from BEFORE this iteration ran
2. Generate and analyze new image
3. Store that NEW analysis for the next iteration's "before" scores

---

## Test Data from Last Run

From `.brent/debug_logs/auto-ai-test.log`:

**User Prompt:**
"In a softly lit bedroom setting, two women in their 20s sit comfortably on the bed chatting away. Th[e scene is] calm and relaxing..."

**Checklist Items:**
- softly lit bedroom
- two women in their 20s
- women wearing nighties
- one woman has red hair, one has blue hair
- calm and relaxing mood

**Iteration Attempts:**
- Iteration 1: Fix prompt was generic fallback (should have been specific items)
- Iteration 2: Fix prompt was "refine details, improve quality" (should have been remaining items)
- Both showed "Before: Score 0.0/10, Checklist 0%"

**Final Analysis (after iterations):**
- Score: 4.8/10
- Checklist: 0% (missing all 5 items)
- Description: "three women, sitting on bed, conversing together..." (wrong - made 3 women instead of 2)

---

## Questions for Tomorrow

1. **What does vision analyzer return?**
   - Check the structure of `analysis` dict
   - Verify `checklist_validation.missing_items` exists and has correct format
   - Check if initial analysis differs from iteration analyses

2. **Where is previous_analysis breaking?**
   - Add logging at iteration start to show what `previous_analysis` contains
   - Log the NEW analysis after each generation
   - Verify the handoff between iterations

3. **Why only 2 iterations?**
   - Check logs for iteration 3
   - Look for early returns or errors

4. **Is the img2img actually helping?**
   - Scores went 0 → 4.8 (some improvement)
   - But checklist still 0% (no items fixed)
   - High denoise (0.75) might be changing too much, losing original context

---

## Potential Root Cause

**Theory:** The vision analyzer might be returning `missing_items` as a different structure than we expect.

Looking at the final analysis in the UI, it shows:
```
Missing 5 items: softly lit bedroom, two women in their 20s, women wearing nighties
```

But the iteration log suggests `missing_items` was empty or not in the expected format when `generate_fix_prompt()` was called.

**Check Tomorrow:**
```python
# In generate_fix_prompt(), what does this actually return?
missing = analysis.get('checklist_validation', {}).get('missing_items', [])

# Is it:
# Option 1: ["softly lit bedroom", "two women in their 20s", ...]
# Option 2: "softly lit bedroom, two women in their 20s, ..."  (string, not list)
# Option 3: {"items": [...]}  (nested object)
# Option 4: []  (empty - missing_items key doesn't exist in this analysis)
```

---

## Next Session Tasks

### Priority 1: Debug Logging
1. Add comprehensive logging to see actual analysis structure
2. Log `previous_analysis` at start of each iteration
3. Log `missing_items` when generating fix prompts
4. Check server logs for the debug output

### Priority 2: Fix Score Tracking
1. Once we see the actual analysis structure, fix the score extraction
2. Ensure `previous_analysis` is set correctly after each iteration
3. Verify handoff between iterations works

### Priority 3: Fix Prompt Generation
1. Fix `missing_items` extraction based on actual structure
2. Ensure iteration 1 uses top 3 missing items
3. Ensure iteration 2+ uses remaining items

### Priority 4: Test End-to-End
1. Run a simple test case (single person, simple scene)
2. Verify scores improve iteration to iteration
3. Verify fix prompts are specific and relevant
4. Check that all 3 iterations run

---

## Files to Check Tomorrow

1. **`app/services/vision_analyzer.py`** - See what structure it returns for `checklist_validation` and `missing_items`
2. **`app/services/iteration_engine.py`** - Add more debug logging, fix score/prompt bugs
3. **`~/.local/share/kindling-api.log`** - Check for debug output (though Flask might buffer it)
4. **`.brent/debug_logs/auto-ai-test.log`** - User's test results

---

## Performance Notes

- User reports 6+ minutes for full automation with 3 iterations
- This includes: initial gen (~45s) + 3 iterations (~45s each) + 4 analyses (~10s each)
- Expected: ~45 + 135 + 40 = ~220s = ~3.5 minutes
- Actual: 6 minutes suggests something is taking longer (maybe vision analysis with KISS mode disabled?)

---

## Code Snippets to Review Tomorrow

### Current iteration loop structure:
```python
for iteration_num in range(1, max_iterations + 1):
    # Analyze current image (unless we already have initial analysis for iteration 1)
    if iteration_num == 1 and previous_analysis is not None:
        analysis = previous_analysis  # Use pre-computed initial analysis
    else:
        analysis = vision_analyzer.analyze_image(...)

    # Check if we should iterate
    should_continue, reasons = should_iterate(analysis)
    if not should_continue:
        return IterationResult(success=True, ...)

    # Don't iterate after last attempt
    if iteration_num >= max_iterations:
        return IterationResult(success=False, ...)

    # Generate fix
    fix_prompt = generate_fix_prompt(analysis, goal_narrative, iteration_num)
    denoise = get_iteration_denoise(iteration_num, missing_count)

    # Create img2img workflow and generate
    # ...

    # Log iteration
    iteration_log.append({
        'iteration': iteration_num,
        'fix_prompt': fix_prompt,
        'denoise': denoise,
        'image_path': str(current_image_path),
        'previous_score': analysis.get('overall_score', {}).get('score', 0),
        'previous_checklist_pct': analysis.get('checklist_validation', {}).get('completion_percentage', 0)
    })

    # Analyze the NEW image for next iteration
    previous_analysis = vision_analyzer.analyze_image(current_image_path, ...)
```

### Potential issue:
The `analysis` variable is being logged as "previous_score", but it's the analysis from BEFORE the iteration ran. We then analyze the NEW image and store it in `previous_analysis` for the next iteration.

This might actually be CORRECT - we want to log "what scores triggered this iteration". But then why is iteration 2 showing 0.0/0%?

**Answer:** Because on iteration 2, we're not using `previous_analysis` (line 172 only uses it for iteration 1). So iteration 2 re-analyzes the current image (which is the output from iteration 1), and that becomes `analysis`. But we're logging that as "previous_score" which makes it look like "before this iteration" when it's actually "the current state before we generate the next fix".

**The real bug:** We need to use `previous_analysis` for ALL iterations, not just iteration 1.

---

## Tomorrow's Quick Fix Attempt

Try this in `iteration_engine.py`:

```python
for iteration_num in range(1, max_iterations + 1):
    # For iteration 1, use initial_analysis if provided
    # For iteration 2+, use the previous_analysis we stored
    if iteration_num == 1 and initial_analysis is not None:
        analysis = initial_analysis
    elif iteration_num > 1 and previous_analysis is not None:
        analysis = previous_analysis
    else:
        # Fallback: analyze current image
        analysis = vision_analyzer.analyze_image(...)

    # ... rest of logic ...

    # After generating new image:
    # Analyze it and store for next iteration
    previous_analysis = vision_analyzer.analyze_image(current_image_path, ...)
```

This ensures:
- Iteration 1 uses initial_analysis
- Iteration 2 uses the analysis from after iteration 1
- Iteration 3 uses the analysis from after iteration 2

---

**Status:** Session paused. User is tired after grinding on this. Pick up tomorrow with debug logging and root cause analysis.

**Last Image:** `sd_output/iteration_2_00007_.png`
**Last Log:** `.brent/debug_logs/auto-ai-test.log`

**Energy Level:** Low - need fresh eyes tomorrow
**Complexity:** Medium-High - subtle bug in state management across iterations
**Confidence in Fix:** Medium - have hypothesis, need to verify with debug logs
