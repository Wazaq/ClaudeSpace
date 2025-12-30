# Iteration System Implementation

**Date:** December 29, 2025
**Status:** ✅ Complete - Ready for Testing

---

## What Was Built

An end-to-end automated iteration system that fixes failed image generations using progressive img2img refinement.

### System Flow

```
1. Generate initial image
   ↓
2. Analyze with vision analyzer
   ↓
3. Check quality gates:
   - Overall score ≥ 7.0/10
   - Checklist completion ≥ 85%
   - No critical issues
   ↓
4. If PASS → Done ✅
   If FAIL → Start iteration ↓
   ↓
5. Generate fix prompt from missing items
   ↓
6. img2img with appropriate denoise
   ↓
7. Re-analyze result
   ↓
8. Repeat steps 5-7 (max 3 iterations)
   ↓
9. Return best result
```

---

## Files Created/Modified

### New Files

**`app/services/iteration_engine.py`** (New)
- Core iteration logic
- Quality gate checking (`should_iterate()`)
- Fix prompt generation (`generate_fix_prompt()`)
- Denoise calculation (`get_iteration_denoise()`)
- Main iteration loop (`iterate_image()`)

### Modified Files

**`app/routes/automation.py`**
- Added `iteration_engine` import
- Integrated iteration after initial analysis (lines 380-451)
- Returns iteration metadata in response

**`static/js/automation.js`**
- Updated `generateFromGoal()` to pass iteration data
- Status message shows iteration count

**`static/js/ui.js`**
- Updated `showAutomationResult()` signature
- Updated `renderAnalysis()` to display iteration info
- Shows green/orange banner based on iteration success

---

## How It Works

### Quality Gate Detection

```python
def should_iterate(analysis: Dict) -> Tuple[bool, List[str]]:
    """
    Checks three conditions:
    1. Overall score < 7.0/10
    2. Checklist completion < 85%
    3. Critical issues present

    Returns (should_iterate, reasons)
    """
```

### Progressive Fix Prompts

**Iteration 1 (Major Changes):**
- Takes top 3 missing checklist items
- Simple, direct prompt: "woman sitting on couch, reading book, fireplace"
- High denoise: 0.75-0.85

**Iteration 2+ (Refinement):**
- Takes remaining missing items
- Subtle adjustments
- Lower denoise: 0.55-0.60

### Denoise Strategy

Based on research from professional workflows:

```python
Iteration 1:
  5+ missing items → denoise 0.85 (major transformation)
  3-4 missing items → denoise 0.80 (moderate changes)
  1-2 missing items → denoise 0.75 (minor changes)

Iteration 2:
  denoise 0.60 (refinement)

Iteration 3:
  denoise 0.55 (final polish)
```

### Max Iterations

Default: **3 iterations** (configurable)

**Why 3?**
- Research shows 2-3 iterations is typical for professional workflows
- Diminishing returns after 3 attempts
- Better to regenerate from scratch than iterate forever

---

## UI Indicators

### Status Message

**Passed on first try:**
```
✅ Generated in 45.2s!
```

**Iteration successful:**
```
✅ Generated in 127.5s (2 iterations to pass quality gates)
```

**Iteration attempted but didn't fully pass:**
```
⚠️  Generated in 165.3s (3 iterations, did not pass all gates)
```

### Analysis Panel

Shows colored banner at top:

**Green banner (iteration succeeded):**
```
🔄 Iteration Successful!
2 iterations performed - image now passes quality gates!
Initial issues: Overall score 6.6/10 below threshold; Checklist 44% below threshold
```

**Orange banner (iteration attempted):**
```
🔄 Iteration Attempted
3 iterations performed - did not fully pass all gates
Initial issues: Overall score 6.6/10 below threshold; Checklist 44% below threshold
```

---

## Testing Status

### ✅ Completed

1. Progressive img2img test with standing→sitting woman
2. Research on professional workflows
3. Code implementation and integration
4. UI indicators

### ⏳ Pending

1. **End-to-end test with real failed automation image**
   - Use the cabin image that scored 6.6/10 with 44% checklist
   - Verify iteration actually improves the result
   - Check that UI displays iteration status correctly

---

## How to Test

### Option 1: Through UI (Recommended)

1. Open automation tab
2. Start conversation
3. Describe the cozy cabin scene (same as before)
4. Approve checklist
5. Generate
6. System should:
   - Detect failure (score 6.6, checklist 44%)
   - Attempt iterations automatically
   - Show iteration status in UI

### Option 2: Direct API Test

```python
# Test with existing failed image
import requests

response = requests.post('http://localhost:5000/automation/generate', json={
    'session_id': '<your_session_id>',
    'sd_model': 'juggernautXL_ragnarokBy.safetensors'
})

# Check response
print(response.json()['iteration'])
```

---

## Expected Behavior

### Scenario 1: First generation passes

```json
{
  "iteration": {
    "attempted": false,
    "success": true,
    "iterations": 0
  }
}
```

### Scenario 2: Iteration succeeds

```json
{
  "iteration": {
    "attempted": true,
    "success": true,
    "iterations": 2,
    "initial_reasons": [
      "Overall score 6.6/10 below threshold (need 7.0+)",
      "Checklist 44% below threshold (need 85%+)"
    ],
    "log": [
      {
        "iteration": 1,
        "fix_prompt": "woman sitting on couch, reading book, fireplace crackling",
        "denoise": 0.85,
        "previous_score": 6.6,
        "previous_checklist_pct": 44
      },
      {
        "iteration": 2,
        "fix_prompt": "snow visible through window, Christmas decorations",
        "denoise": 0.60,
        "previous_score": 7.2,
        "previous_checklist_pct": 78
      }
    ]
  }
}
```

### Scenario 3: Iteration attempted but didn't pass

```json
{
  "iteration": {
    "attempted": true,
    "success": false,
    "iterations": 3,
    "initial_reasons": [...],
    "log": [...]
  }
}
```

---

## Architecture Decisions

### Why Not Use ControlNet?

- ControlNet maintains/transfers poses, doesn't create new ones
- Plain img2img with progressive denoise proved effective
- Simpler, fewer dependencies

### Why Progressive Iteration?

- Research showed one-shot high-denoise causes body horror
- Breaking changes into steps (0.85 → 0.60 → 0.55) works better
- Matches professional workflows

### Why Max 3 Iterations?

- Diminishing returns after 3
- Better to regenerate from scratch than iterate infinitely
- Professional workflows typically use 2-3 passes

---

## Future Enhancements

### Phase 2: Advanced Techniques

1. **Inpainting for specific defects**
   - Target hands/faces specifically
   - Use vision analyzer to identify problem areas
   - Generate masks for inpainting

2. **Seed variation**
   - Try same fix prompt 2-3 times with different seeds
   - Pick best result
   - Increases success rate

3. **CFG scheduling**
   - Start high (CFG 12) for structure
   - Reduce to 8 for details
   - Finish at 5 for naturalistic refinement

### Phase 3: Learning System

1. **Track what works**
   - Which fix prompts succeed
   - Which denoise levels work for different changes
   - Build success pattern database

2. **Adaptive denoise**
   - Learn optimal denoise for specific types of changes
   - Adjust based on historical success rates

---

## Known Limitations

1. **No inpainting yet** - Can't target specific problem areas (hands, faces)
2. **No seed variation** - Only tries once per iteration
3. **Fixed max iterations** - Not adaptive based on progress
4. **Simple fix prompts** - Could be smarter about prioritization

---

## Performance Considerations

**Generation time:**
- No iteration: ~45s
- 1 iteration: ~90s
- 2 iterations: ~135s
- 3 iterations: ~180s

**Trade-off:**
- Slower generation vs higher success rate
- User can see progress in UI
- Better than regenerating from scratch multiple times manually

---

## Success Criteria

**System is successful if:**

1. ✅ Detects failures correctly (score < 7 OR checklist < 85%)
2. ✅ Generates appropriate fix prompts from missing items
3. ✅ Uses correct denoise levels for iteration number
4. ✅ Re-analyzes after each iteration
5. ✅ Stops when quality gates pass OR max iterations reached
6. ✅ UI shows iteration status clearly
7. ⏳ **Actually improves failed images** (needs end-to-end test)

---

## Next Steps

1. **Test with real automation session**
   - Run through full conversation flow
   - Let it generate and fail
   - Verify iteration kicks in and works

2. **Test with the known failed cabin image**
   - Manually trigger iteration on the 6.6/10 image
   - Verify it improves to 7.0+/10

3. **Monitor iteration logs**
   - Check console output during iteration
   - Verify denoise levels are correct
   - Verify fix prompts make sense

4. **Consider enhancements**
   - Based on real-world results
   - Add inpainting if hands/faces are common failures
   - Add seed variation if iterations aren't improving enough

---

**Status:** Implementation complete, ready for end-to-end testing with Brent.
